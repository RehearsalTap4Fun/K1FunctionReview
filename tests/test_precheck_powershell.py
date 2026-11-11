"""Regression tests for the static-precheck PowerShell scripts.

Contract: review-k1-function/references/quick-precheck.md (sections 3-6, 9).
The scripts are executed for real against throw-away repositories that live
inside this project's ``.tmp`` / ``.cache``; no formal K1 repository and no
network remote is ever contacted.

Every PowerShell start costs 1-2 s, so the checks are written as ``@scenario``
functions that a module fixture runs concurrently, each in its own sandbox
(``ctx``: see ``precheck_powershell_support.Scratch``).  ``test_precheck``
then reports one result per scenario; ``-k <scenario name>`` runs only the
selected ones.
"""
import json
import os
from pathlib import Path
import subprocess
import uuid

import pytest

from conftest import run_git
from precheck_powershell_support import (
    LFS_POINTER, POWERSHELL, PROJECT_ROOT, REMOTE_CACHE_BOUNDARY, TMP_ROOT,
    commit_all, init_repo, make_two_commit_repo, read_json, repo_fingerprint,
    run_scenarios, write_json,
)

pytestmark = pytest.mark.skipif(
    POWERSHELL is None, reason='PowerShell (pwsh/powershell) is not on PATH')

SNAPSHOT = 'snapshot-repository-state.ps1'
PREPARE = 'prepare-remote-snapshots.ps1'
COLLECT = 'collect-git-evidence.ps1'
EXPORT = 'export-git-file.ps1'
CLEANUP = 'cleanup-run-evidence.ps1'
MISSING_SHA = 'f' * 40

SCENARIOS = {}
XFAIL = {}


def scenario(function=None, *, cases=None, xfail=None):
    """Register ``function(ctx)`` or, with cases, ``function(ctx, case)``.

    ``cases`` maps a readable id to the case value.  ``xfail`` is a reason
    (applies to every case) or a {case id: reason} mapping; it is always
    strict so that a fixed script turns the suite red until the mark is
    removed.
    """
    def register(target):
        base = target.__name__
        if cases is None:
            SCENARIOS[base] = target
            if xfail:
                XFAIL[base] = xfail
            return target
        for case_id, value in cases.items():
            name = f'{base}[{case_id}]'
            SCENARIOS[name] = (lambda ctx, _value=value: target(ctx, _value))
            reason = xfail.get(case_id) if isinstance(xfail, dict) else xfail
            if reason:
                XFAIL[name] = reason
        return target
    return register(function) if function is not None else register


def _symlink(link, target):
    try:
        os.symlink(target, link, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip('symbolic links are unavailable on this host')


# --------------------------------------------------------------------------
# snapshot-repository-state.ps1 (contract section 4, steps 5.2 / 5.12)
# --------------------------------------------------------------------------

def _snapshot(ctx, repositories):
    name = uuid.uuid4().hex
    request = write_json(ctx.tmp / f'{name}-request.json', {
        'repositories': [
            {'role': role, 'path': str(path)} for role, path in repositories
        ],
    })
    output = ctx.tmp / f'{name}-state.json'
    completed = ctx.run(SNAPSHOT, '-RequestPath', request, '-OutputPath', output)
    return completed, output


def _snapshot_entry(ctx, path):
    completed, output = _snapshot(ctx, [('client', path)])
    assert completed.returncode == 0, completed.stderr
    payload = read_json(output)
    assert payload['status'] == 'ok' and payload['errors'] == []
    assert len(payload['repositories']) == 1
    return payload['repositories'][0]


def _worktree_files(path):
    return sorted(
        (str(item.relative_to(path)), item.read_bytes())
        for item in path.rglob('*')
        if item.is_file() and '.git' not in item.relative_to(path).parts)


@scenario
def snapshot_reports_clean_repository_state(ctx):
    path, _base, target = ctx.repo()
    entry = _snapshot_entry(ctx, path)
    assert entry['role'] == 'client'
    assert entry['branch'] == 'dev'
    assert entry['head'] == target
    assert entry['dirty'] is False
    assert entry['entryCount'] == 0
    assert entry['categories'] == {}
    assert len(entry['digest']) == 64


def _modify_tracked(path):
    (path / 'keep.txt').write_text('edited\n', encoding='utf-8')


def _add_untracked(path):
    (path / 'brand-new.txt').write_text('x\n', encoding='utf-8')


def _delete_tracked(path):
    (path / 'keep.txt').unlink()


def _stage(path):
    _modify_tracked(path)
    run_git(path, 'add', 'keep.txt')


def _commit(path):
    _modify_tracked(path)
    commit_all(path, 'third commit')


def _switch_branch(path):
    run_git(path, 'switch', '--quiet', '-c', 'other')


@scenario
def snapshot_digest_changes_with_workspace(ctx):
    changes = {
        'modify-tracked': _modify_tracked, 'add-untracked': _add_untracked,
        'delete-tracked': _delete_tracked, 'stage': _stage, 'commit': _commit,
        'switch-branch': _switch_branch,
    }
    repositories = [
        (role, make_two_commit_repo(ctx.tmp / role)[0]) for role in changes]

    def digests():
        completed, output = _snapshot(ctx, repositories)
        assert completed.returncode == 0, completed.stderr
        return {item['role']: item['digest']
                for item in read_json(output)['repositories']}

    before = digests()
    for role, path in repositories:
        changes[role](path)
    after = digests()
    assert set(before) == set(after) == set(changes)
    unchanged = [role for role in changes if after[role] == before[role]]
    assert unchanged == []


@scenario
def snapshot_counts_status_categories(ctx):
    path, _base, _target = ctx.repo()
    (path / 'keep.txt').write_text('edited\n', encoding='utf-8')
    (path / 'u1.txt').write_text('1\n', encoding='utf-8')
    (path / 'u2.txt').write_text('2\n', encoding='utf-8')
    run_git(path, 'mv', 'modify.txt', 'renamed.txt')
    entry = _snapshot_entry(ctx, path)
    assert entry['dirty'] is True
    assert entry['entryCount'] == 4
    assert entry['categories'] == {' M': 1, '??': 2, 'R ': 1}


@scenario(cases={'already-modified': 'keep.txt', 'untracked': 'user-notes.txt'})
def snapshot_digest_changes_when_dirty_file_is_edited_again(ctx, file_name):
    path, _base, _target = ctx.repo()
    (path / file_name).write_text('first user edit\n', encoding='utf-8')
    before = _snapshot_entry(ctx, path)
    (path / file_name).write_text('second, different and longer user edit\n',
                                  encoding='utf-8')
    after = _snapshot_entry(ctx, path)
    assert after['digest'] != before['digest']


@scenario
def snapshot_is_stable_and_does_not_modify_repository(ctx):
    path, _base, _target = ctx.repo()
    (path / 'keep.txt').write_text('unstaged edit\n', encoding='utf-8')
    (path / 'staged.txt').write_text('staged\n', encoding='utf-8')
    run_git(path, 'add', 'staged.txt')
    (path / 'untracked.txt').write_text('untracked\n', encoding='utf-8')
    worktree_before = _worktree_files(path)
    before = repo_fingerprint(path)
    first = _snapshot_entry(ctx, path)
    second = _snapshot_entry(ctx, path)
    assert first == second
    assert first['dirty'] is True and first['entryCount'] == 3
    assert repo_fingerprint(path) == before
    assert _worktree_files(path) == worktree_before


@scenario
def snapshot_output_keeps_no_unrelated_paths(ctx):
    path, _base, _target = ctx.repo()
    (path / 'SecretUnrelatedDraft.cs').write_text('x\n', encoding='utf-8')
    nested = path / 'PrivateFolderName'
    nested.mkdir()
    (nested / 'AnotherUserFile.lua').write_text('y\n', encoding='utf-8')
    (path / 'keep.txt').write_text('edited\n', encoding='utf-8')
    run_git(path, 'mv', 'modify.txt', 'RenamedByUser.txt')
    completed, output = _snapshot(ctx, [('client', path)])
    assert completed.returncode == 0, completed.stderr
    text = output.read_text(encoding='utf-8')
    for leaked in (
        'SecretUnrelatedDraft', 'PrivateFolderName', 'AnotherUserFile',
        'RenamedByUser', 'keep.txt', 'modify.txt', str(path), ctx.tmp.name,
    ):
        assert leaked not in text
    assert completed.stdout.strip() == ''
    entry = read_json(output)['repositories'][0]
    # Section 4 allows branch/head, dirty, entryCount, categories and digest.
    # role identifies the entry; the two *Sha256 values are opaque hashes.
    assert set(entry) <= {
        'role', 'branch', 'head', 'dirty', 'entryCount', 'categories', 'digest',
        'indexSha256', 'statusSha256',
    }
    assert {'branch', 'head', 'dirty', 'entryCount', 'categories', 'digest'} <= set(entry)
    assert all(len(key) == 2 for key in entry['categories'])


@scenario
def snapshot_rejects_output_outside_project_tmp(ctx):
    path, _base, _target = ctx.repo()
    request = write_json(ctx.tmp / 'request.json', {
        'repositories': [{'role': 'client', 'path': str(path)}]})
    outside = ctx.outside / 'state.json'
    completed = ctx.run(SNAPSHOT, '-RequestPath', request, '-OutputPath', outside)
    assert completed.returncode == 2
    assert 'OUTPUT_OUTSIDE_PROJECT_TMP' in completed.stderr
    assert not outside.exists()


@scenario
def snapshot_rejects_request_outside_project_tmp(ctx):
    path, _base, _target = ctx.repo()
    request = write_json(ctx.outside / 'request.json', {
        'repositories': [{'role': 'client', 'path': str(path)}]})
    output = ctx.tmp / 'state.json'
    completed = ctx.run(SNAPSHOT, '-RequestPath', request, '-OutputPath', output)
    assert completed.returncode == 2
    assert 'REQUEST_OUTSIDE_PROJECT_TMP' in completed.stderr
    assert not output.exists()


@scenario
def snapshot_rejects_output_through_symlink(ctx):
    path, _base, _target = ctx.repo()
    outside = ctx.outside / 'outside'
    outside.mkdir()
    _symlink(ctx.tmp / 'link', outside)
    request = write_json(ctx.tmp / 'request.json', {
        'repositories': [{'role': 'client', 'path': str(path)}]})
    completed = ctx.run(
        SNAPSHOT, '-RequestPath', request,
        '-OutputPath', ctx.tmp / 'link' / 'state.json')
    assert completed.returncode == 2
    assert 'OUTPUT_REPARSE_POINT' in completed.stderr
    assert list(outside.iterdir()) == []


@scenario
def snapshot_never_overwrites_existing_output(ctx):
    path, _base, _target = ctx.repo()
    request = write_json(ctx.tmp / 'request.json', {
        'repositories': [{'role': 'client', 'path': str(path)}]})
    output = ctx.tmp / 'state.json'
    output.write_text('previous evidence', encoding='utf-8')
    completed = ctx.run(SNAPSHOT, '-RequestPath', request, '-OutputPath', output)
    assert completed.returncode == 2
    assert 'OUTPUT_ALREADY_EXISTS' in completed.stderr
    assert output.read_text(encoding='utf-8') == 'previous evidence'


@scenario
def snapshot_degrades_only_the_missing_repository(ctx):
    path, _base, target = ctx.repo()
    completed, output = _snapshot(ctx, [
        ('client', path), ('server', ctx.tmp / 'does-not-exist')])
    assert completed.returncode == 1
    payload = read_json(output)
    assert payload['status'] == 'error'
    assert [item['role'] for item in payload['repositories']] == ['client']
    assert payload['repositories'][0]['head'] == target
    assert payload['errors'] == [{'role': 'server', 'code': 'REPOSITORY_NOT_FOUND'}]


# --------------------------------------------------------------------------
# collect-git-evidence.ps1 (contract steps 5.4 / 5.7, section 6, section 9)
# --------------------------------------------------------------------------

def _collect(ctx, repositories):
    name = uuid.uuid4().hex
    request = write_json(ctx.tmp / f'{name}-collect-request.json',
                         {'repositories': repositories})
    output = ctx.tmp / f'{name}-git-evidence.json'
    completed = ctx.run(COLLECT, '-RequestPath', request, '-OutputPath', output)
    return completed, output


def _change_set(record):
    return sorted((item['status'], item['path']) for item in record['changes'])


EXPECTED_CHANGES = [('A', 'added/new.txt'), ('D', 'delete.txt'), ('M', 'modify.txt')]


@scenario
def collect_reports_changed_paths_between_full_shas(ctx):
    path, base, target = ctx.repo()
    completed, output = _collect(ctx, [{
        'role': 'server', 'path': str(path), 'source': 'local',
        'base': base, 'target': target,
    }])
    assert completed.returncode == 0, completed.stderr
    payload = read_json(output)
    assert payload['status'] == 'ok'
    assert payload['errors'] == [] and payload['requiresInput'] == []
    record = payload['repositories'][0]
    assert record['role'] == 'server'
    assert record['base'] == {
        'requested': base, 'resolvedRef': f'object:{base}', 'sha': base}
    assert record['target'] == {
        'requested': target, 'resolvedRef': f'object:{target}', 'sha': target}
    assert record['mergeBase'] == base
    assert _change_set(record) == EXPECTED_CHANGES
    assert [item['sha'] for item in record['commits']] == [target]
    assert record['commits'][0]['subject'] == 'target commit'
    assert record['noIndependentChange'] is False


@scenario
def collect_reports_renames_and_non_ascii_paths(ctx):
    path = init_repo(ctx.tmp / 'rename-repo')
    body = ''.join(f'line {index}\n' for index in range(40))
    (path / 'old_name.txt').write_text(body, encoding='utf-8')
    base = commit_all(path, 'base')
    run_git(path, 'mv', 'old_name.txt', 'new_name.txt')
    (path / '活动 配置.txt').write_text('内容\n', encoding='utf-8')
    target = commit_all(path, '重命名与中文路径')
    completed, output = _collect(ctx, [{
        'role': 'config', 'path': str(path), 'base': base, 'target': target}])
    assert completed.returncode == 0, completed.stderr
    record = read_json(output)['repositories'][0]
    changes = {item['path']: item for item in record['changes']}
    assert set(changes) == {'new_name.txt', '活动 配置.txt'}
    assert changes['new_name.txt']['status'].startswith('R')
    assert changes['new_name.txt']['oldPath'] == 'old_name.txt'
    assert changes['活动 配置.txt']['status'] == 'A'
    assert record['commits'][0]['subject'] == '重命名与中文路径'


@scenario
def collect_full_shas_stay_frozen_when_branch_moves(ctx):
    path, base, target = ctx.repo()
    request = [{'role': 'client', 'path': str(path), 'base': base, 'target': target}]
    first, first_output = _collect(ctx, request)
    (path / 'later.txt').write_text('later work\n', encoding='utf-8')
    moved = commit_all(path, 'branch moved after freeze')
    second, second_output = _collect(ctx, request)
    assert first.returncode == 0 and second.returncode == 0
    before = read_json(first_output)['repositories'][0]
    after = read_json(second_output)['repositories'][0]
    assert after['target']['sha'] == target != moved
    assert _change_set(after) == _change_set(before) == EXPECTED_CHANGES
    assert after['commits'] == before['commits']


@scenario
def collect_uses_committed_objects_and_is_read_only(ctx):
    path, base, target = ctx.repo()
    (path / 'keep.txt').write_text('uncommitted edit\n', encoding='utf-8')
    (path / 'untracked-user-file.txt').write_text('x\n', encoding='utf-8')
    before = repo_fingerprint(path)
    completed, output = _collect(ctx, [{
        'role': 'client', 'path': str(path), 'base': base, 'target': target}])
    assert completed.returncode == 0, completed.stderr
    record = read_json(output)['repositories'][0]
    assert _change_set(record) == EXPECTED_CHANGES
    assert repo_fingerprint(path) == before


@scenario
def collect_reports_missing_sha(ctx):
    path, base, target = ctx.repo()
    completed, output = _collect(ctx, [
        {'role': 'client', 'path': str(path), 'base': base, 'target': MISSING_SHA},
        {'role': 'server', 'path': str(path), 'base': MISSING_SHA, 'target': target},
    ])
    assert completed.returncode == 1
    payload = read_json(output)
    assert payload['status'] == 'error'
    assert [(item['role'], item['code'], item['requested'])
            for item in payload['errors']] == [
        ('client', 'TARGET_OBJECT_MISSING', MISSING_SHA),
        ('server', 'BASE_OBJECT_MISSING', MISSING_SHA)]
    for record, field in zip(payload['repositories'], ('target', 'base')):
        assert record[field] == {
            'requested': MISSING_SHA, 'resolvedRef': None, 'sha': None}
        assert record['changes'] == [] and record['commits'] == []
        assert record['mergeBase'] is None


@scenario
def collect_missing_target_branch_is_not_replaced_by_current_branch(ctx):
    """Section 9: a missing target is never substituted by HEAD/tracking refs."""
    path, base, target = ctx.repo()
    completed, output = _collect(ctx, [{
        'role': 'client', 'path': str(path), 'source': 'local',
        'base': base, 'target': 'dev_NK-0000'}])
    assert completed.returncode == 2
    payload = read_json(output)
    assert payload['status'] == 'requires_input'
    assert payload['requiresInput'][0]['code'] == 'TARGET_REF_MISSING'
    record = payload['repositories'][0]
    assert record['target'] == {
        'requested': 'dev_NK-0000', 'resolvedRef': None, 'sha': None}
    assert record['changes'] == [] and record['commits'] == []
    assert target not in output.read_text(encoding='utf-8')


@scenario
def collect_remote_source_rejects_repository_outside_cache(ctx):
    path, base, target = ctx.repo()
    completed, output = _collect(ctx, [{
        'role': 'client', 'path': str(path), 'source': 'remote', 'remote': 'origin',
        'baseRef': 'refs/remotes/origin/dev', 'targetRef': 'refs/remotes/origin/dev',
        'baseSha': base, 'targetSha': target}])
    assert completed.returncode == 1
    payload = read_json(output)
    assert [item['code'] for item in payload['errors']] == [
        'REMOTE_REPOSITORY_NOT_ALLOWED']
    record = payload['repositories'][0]
    assert record['base']['sha'] is None and record['target']['sha'] is None
    assert record['changes'] == [] and record['commits'] == []


@scenario(cases={'request': 'request', 'output': 'output'})
def collect_rejects_paths_outside_project_tmp(ctx, location):
    path, base, target = ctx.repo()
    payload = {'repositories': [
        {'role': 'client', 'path': str(path), 'base': base, 'target': target}]}
    if location == 'request':
        request = write_json(ctx.outside / 'request.json', payload)
        output = ctx.tmp / 'evidence.json'
        code = 'REQUEST_OUTSIDE_TMP'
    else:
        request = write_json(ctx.tmp / 'request.json', payload)
        output = ctx.outside / 'evidence.json'
        code = 'OUTPUT_OUTSIDE_TMP'
    completed = ctx.run(COLLECT, '-RequestPath', request, '-OutputPath', output)
    assert completed.returncode == 1
    assert code in completed.stderr
    assert not output.exists()


@scenario
def collect_rejects_output_through_symlink(ctx):
    path, base, target = ctx.repo()
    outside = ctx.outside / 'outside'
    outside.mkdir()
    _symlink(ctx.tmp / 'link', outside)
    request = write_json(ctx.tmp / 'request.json', {'repositories': [
        {'role': 'client', 'path': str(path), 'base': base, 'target': target}]})
    completed = ctx.run(
        COLLECT, '-RequestPath', request,
        '-OutputPath', ctx.tmp / 'link' / 'evidence.json')
    assert completed.returncode == 1
    assert 'OUTPUT_REPARSE_POINT' in completed.stderr
    assert list(outside.iterdir()) == []


# --------------------------------------------------------------------------
# export-git-file.ps1 (contract section 4, step 5.8, section 6)
# --------------------------------------------------------------------------

def _export(ctx, repository, commit, git_path, output, *extra):
    return ctx.run(
        EXPORT, '-Repository', repository, '-Commit', commit,
        '-GitPath', git_path, '-OutputPath', output, *extra)


def _blob(repository, commit, git_path):
    return subprocess.run(
        ['git', '-C', str(repository), 'cat-file', 'blob', f'{commit}:{git_path}'],
        check=True, capture_output=True).stdout


@scenario
def export_writes_exact_blob_bytes_per_commit(ctx):
    path, base, target = ctx.repo()
    base_out = ctx.tmp / 'export' / 'base' / 'modify.txt'
    target_out = ctx.tmp / 'export' / 'target' / 'modify.txt'
    first = _export(ctx, path, base, 'modify.txt', base_out)
    second = _export(ctx, path, target, 'modify.txt', target_out)
    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    assert base_out.read_bytes() == b'base line\r\n\xff\xfe binary tail'
    assert target_out.read_bytes() == b'target line\r\n\x00\x01 other tail'
    assert base_out.read_bytes() == _blob(path, base, 'modify.txt')
    assert target_out.read_bytes() == _blob(path, target, 'modify.txt')
    assert [item.name for item in (ctx.tmp / 'export').rglob('*.tmp')] == []


@scenario
def export_reads_commit_not_working_tree_and_is_read_only(ctx):
    path, base, _target = ctx.repo()
    (path / 'modify.txt').write_bytes(b'uncommitted working tree content')
    before = repo_fingerprint(path)
    output = ctx.tmp / 'modify-at-base.bin'
    completed = _export(ctx, path, base, 'modify.txt', output)
    assert completed.returncode == 0, completed.stderr
    assert output.read_bytes() == b'base line\r\n\xff\xfe binary tail'
    assert repo_fingerprint(path) == before
    assert (path / 'modify.txt').read_bytes() == b'uncommitted working tree content'


@scenario
def export_refuses_output_outside_project_tmp(ctx):
    path, _base, target = ctx.repo()
    outside = ctx.outside / 'leak' / 'modify.txt'
    completed = _export(ctx, path, target, 'modify.txt', outside)
    assert completed.returncode == 1
    assert 'OUTPUT_OUTSIDE_TMP' in completed.stderr
    assert not outside.exists() and not outside.parent.exists()


@scenario
def export_refuses_traversal_out_of_project_tmp(ctx):
    path, _base, target = ctx.repo()
    escaped = PROJECT_ROOT / ('precheck-escape-' + uuid.uuid4().hex + '.bin')
    traversal = ctx.tmp / '..' / '..' / escaped.name
    try:
        completed = _export(ctx, path, target, 'modify.txt', traversal)
        assert completed.returncode == 1
        assert 'OUTPUT_OUTSIDE_TMP' in completed.stderr
        assert not escaped.exists()
    finally:
        escaped.unlink(missing_ok=True)


@scenario
def export_refuses_output_through_symlink(ctx):
    path, _base, target = ctx.repo()
    outside = ctx.outside / 'outside'
    outside.mkdir()
    _symlink(ctx.tmp / 'link', outside)
    completed = _export(ctx, path, target, 'modify.txt', ctx.tmp / 'link' / 'modify.txt')
    assert completed.returncode == 1
    assert 'OUTPUT_REPARSE_POINT' in completed.stderr
    assert list(outside.iterdir()) == []


@scenario
def export_never_overwrites_existing_output(ctx):
    path, _base, target = ctx.repo()
    output = ctx.tmp / 'existing.bin'
    output.write_bytes(b'earlier evidence')
    completed = _export(ctx, path, target, 'modify.txt', output)
    assert completed.returncode == 1
    assert 'OUTPUT_ALREADY_EXISTS' in completed.stderr
    assert output.read_bytes() == b'earlier evidence'


@scenario(cases={'branch': 'dev', 'HEAD': 'HEAD', 'abbreviated-sha': 'abc1234'})
def export_rejects_movable_or_abbreviated_commit(ctx, commit):
    path, _base, _target = ctx.repo()
    output = ctx.tmp / 'by-ref.bin'
    completed = _export(ctx, path, commit, 'modify.txt', output)
    assert completed.returncode == 1
    assert 'INVALID_COMMIT' in completed.stderr
    assert not output.exists()


@scenario(cases={
    'parent': '../outside.txt', 'absolute': '/etc/hosts',
    'backslash': 'added\\new.txt'})
def export_rejects_unsafe_git_path(ctx, git_path):
    path, _base, target = ctx.repo()
    output = ctx.tmp / 'unsafe.bin'
    completed = _export(ctx, path, target, git_path, output)
    assert completed.returncode == 1
    assert 'INVALID_GIT_PATH' in completed.stderr
    assert not output.exists()


@scenario(cases={
    'missing-commit': ('missing', 'modify.txt'),
    'deleted-at-target': ('target', 'delete.txt')})
def export_missing_object_leaves_no_output(ctx, case):
    commit_kind, git_path = case
    path, _base, target = ctx.repo()
    commit = MISSING_SHA if commit_kind == 'missing' else target
    output = ctx.tmp / 'missing' / 'file.bin'
    completed = _export(ctx, path, commit, git_path, output)
    assert completed.returncode == 1
    assert 'GIT_OBJECT_EXPORT_FAILED' in completed.stderr
    assert not output.exists()
    assert list((ctx.tmp / 'missing').iterdir()) == []


@scenario
def export_missing_repository(ctx):
    output = ctx.tmp / 'none.bin'
    completed = _export(ctx, ctx.tmp / 'no-such-repo', MISSING_SHA, 'a.txt', output)
    assert completed.returncode == 1
    assert 'REPOSITORY_NOT_FOUND' in completed.stderr
    assert not output.exists()


@scenario
def export_lfs_pointer_without_materialize_stays_a_pointer(ctx):
    """Section 6: a pointer only proves the object identity, never content."""
    path, _base, target = ctx.repo()
    output = ctx.tmp / 'Activity.xlsx'
    completed = _export(ctx, path, target, 'config/Activity.xlsx', output)
    assert completed.returncode == 0, completed.stderr
    exported = output.read_bytes()
    assert exported == LFS_POINTER
    assert exported.startswith(b'version https://git-lfs.github.com/spec/v1\n')
    assert not exported.startswith(b'PK')
    assert not (path / '.git' / 'lfs' / 'objects').exists()


@scenario
def export_materialize_refuses_repository_outside_remote_cache(ctx):
    """Section 4: LFS writes may only target the FunctionPreview cache."""
    path, _base, target = ctx.repo()
    before = repo_fingerprint(path)
    output = ctx.tmp / 'Activity.xlsx'
    completed = _export(
        ctx, path, target, 'config/Activity.xlsx', output,
        '-MaterializeLfs', '-Remote', 'origin',
        '-ExpectedLfsPath', 'config/Activity.xlsx', '-LfsTimeoutSeconds', '5')
    assert completed.returncode == 1
    assert 'LFS_REPOSITORY_NOT_ALLOWED' in completed.stderr
    assert not output.exists()
    assert repo_fingerprint(path) == before
    assert not (path / '.git' / 'lfs').exists()


@scenario(cases={
    'other-remote': (('-Remote', 'upstream', '-ExpectedLfsPath',
                      'config/Activity.xlsx'), 'INVALID_LFS_REMOTE'),
    'other-path': (('-Remote', 'origin', '-ExpectedLfsPath',
                    'config/Other.xlsx'), 'LFS_PATH_MISMATCH'),
})
def export_materialize_requires_origin_and_exact_path(ctx, case):
    extra, code = case
    path, _base, target = ctx.repo()
    output = ctx.tmp / 'Activity.xlsx'
    completed = _export(
        ctx, path, target, 'config/Activity.xlsx', output, '-MaterializeLfs', *extra)
    assert completed.returncode == 1
    assert code in completed.stderr
    assert not output.exists()


# --------------------------------------------------------------------------
# prepare-remote-snapshots.ps1 (contract section 3 / 9), local bare remotes.
# The script accepts a repository below .tmp only when its origin is a
# file:// URL that is also below .tmp, so no network is ever involved.
# --------------------------------------------------------------------------

def _make_remote_pair(ctx, name='client', allow_filter=True):
    """Bare ``origin`` plus a formal-style clone whose tracking refs are stale.

    Returns (local, remote, shas): shas holds the live remote SHAs and the
    stale target SHA still recorded in the local clone's tracking ref.
    """
    seed, base, target = make_two_commit_repo(ctx.tmp / f'{name}-seed')
    remote = init_repo(ctx.tmp / f'{name}-origin.git', bare=True)
    if allow_filter:
        run_git(remote, 'config', 'uploadpack.allowFilter', 'true')
    run_git(seed, 'remote', 'add', 'origin', remote.as_uri())
    run_git(seed, 'tag', 'v-fixture', target)
    run_git(
        seed, 'push', '--quiet', 'origin', f'{base}:refs/heads/dev',
        f'{target}:refs/heads/dev_NK-8604', f'{base}:refs/heads/unrelated',
        'refs/tags/v-fixture')

    local = ctx.tmp / f'{name}-formal'
    subprocess.run(
        ['git', 'clone', '--quiet', '--branch', 'dev', remote.as_uri(), str(local)],
        check=True, capture_output=True, text=True, encoding='utf-8')
    for key, value in (('user.name', 'Precheck Fixture'),
                       ('user.email', 'precheck-fixture@example.invalid'),
                       ('commit.gpgsign', 'false')):
        run_git(local, 'config', key, value)
    stale_target = run_git(
        local, 'rev-parse', 'refs/remotes/origin/dev_NK-8604').stdout.strip()

    # The live remote moves on after the formal clone was last fetched.
    run_git(seed, 'switch', '--quiet', '--detach', target)
    (seed / 'live.txt').write_text('pushed after the local clone\n', encoding='utf-8')
    live_target = commit_all(seed, 'live remote commit')
    run_git(seed, 'push', '--quiet', 'origin', f'{live_target}:refs/heads/dev_NK-8604')
    assert stale_target == target != live_target
    return local, remote, {
        'base': base, 'stale_target': stale_target, 'live_target': live_target}


def _prepare(ctx, repositories, env=None, cache=None):
    name = uuid.uuid4().hex
    request = write_json(ctx.tmp / f'{name}-remote-request.json',
                         {'repositories': repositories})
    output = ctx.tmp / f'{name}-remote-manifest.json'
    completed = ctx.run(
        PREPARE, '-RequestPath', request, '-OutputPath', output,
        '-CacheRoot', cache or ctx.cache, '-TimeoutSeconds', '30', env=env)
    return completed, output


def _entry(role, local, base='dev', target='dev_NK-8604', remote='origin'):
    return {'role': role, 'localRepository': str(local), 'remote': remote,
            'baseBranch': base, 'targetBranch': target}


@scenario
def prepare_requires_k1_project_root(ctx):
    local, _remote, _shas = _make_remote_pair(ctx)
    env = {key: value for key, value in ctx.env.items() if key != 'K1_PROJECT_ROOT'}
    completed, output = _prepare(ctx, [_entry('client', local)], env=env)
    assert completed.returncode == 1
    assert 'K1_PROJECT_ROOT_REQUIRED' in completed.stderr
    assert not output.exists()
    assert list(ctx.cache.iterdir()) == []


@scenario
def prepare_freezes_live_remote_shas_into_isolated_cache(ctx):
    local, remote, shas = _make_remote_pair(ctx)
    before = repo_fingerprint(local)
    completed, output = _prepare(ctx, [_entry('client', local)])
    assert completed.returncode == 0, completed.stderr
    payload = read_json(output)
    assert payload['status'] == 'ok' and payload['errors'] == []
    manifest = payload['repositories'][0]
    cache = Path(manifest['repository'])
    assert manifest == {
        'role': 'client', 'source': 'remote', 'repository': str(cache),
        'remote': 'origin',
        'baseRef': 'refs/remotes/origin/dev',
        'targetRef': 'refs/remotes/origin/dev_NK-8604',
        'baseSha': shas['base'],
        # Live remote SHA, not the stale tracking ref of the formal clone.
        'targetSha': shas['live_target'],
    }
    assert cache.resolve() == (ctx.cache / 'client').resolve()
    assert cache.resolve().is_relative_to(REMOTE_CACHE_BOUNDARY.resolve())

    # The formal clone is untouched: no fetch, no ref update, no FETCH_HEAD.
    assert repo_fingerprint(local) == before
    assert run_git(local, 'rev-parse', 'refs/remotes/origin/dev_NK-8604'
                   ).stdout.strip() == shas['stale_target']

    # Cache has no checkout, exactly the two requested refs and no tags.
    assert run_git(cache, 'rev-parse', '--is-bare-repository').stdout.strip() == 'true'
    refs = run_git(cache, 'for-each-ref', '--format=%(refname)').stdout.split()
    assert sorted(refs) == [
        'refs/remotes/origin/dev', 'refs/remotes/origin/dev_NK-8604']
    assert run_git(cache, 'tag', '--list').stdout.strip() == ''
    assert run_git(cache, 'config', 'remote.origin.partialclonefilter'
                   ).stdout.strip() == 'blob:none'
    assert run_git(cache, 'remote', 'get-url', 'origin').stdout.strip() == remote.as_uri()
    assert not (ctx.cache / '.client.lock').exists()


@scenario
def prepare_manifest_feeds_collector_with_frozen_shas(ctx):
    local, _remote, shas = _make_remote_pair(ctx)
    completed, output = _prepare(ctx, [_entry('client', local)])
    assert completed.returncode == 0, completed.stderr
    manifest = read_json(output)['repositories'][0]
    request = {
        'role': 'client', 'path': manifest['repository'], 'source': 'remote',
        'remote': manifest['remote'], 'baseRef': manifest['baseRef'],
        'targetRef': manifest['targetRef'], 'baseSha': manifest['baseSha'],
        'targetSha': manifest['targetSha'],
    }
    collected, evidence = _collect(ctx, [request])
    assert collected.returncode == 0, collected.stderr
    record = read_json(evidence)['repositories'][0]
    assert record['source'] == 'remote' and record['remote'] == 'origin'
    assert record['base'] == {
        'requested': shas['base'], 'resolvedRef': 'refs/remotes/origin/dev',
        'sha': shas['base']}
    assert record['target']['sha'] == shas['live_target']
    assert _change_set(record) == sorted(EXPECTED_CHANGES + [('A', 'live.txt')])
    assert record['workingTree'] is None


@scenario
def collect_remote_source_never_resolves_movable_refs(ctx):
    """Step 5.4: the collector must not re-resolve a movable branch."""
    local, _remote, _shas = _make_remote_pair(ctx)
    completed, output = _prepare(ctx, [_entry('client', local)])
    assert completed.returncode == 0, completed.stderr
    manifest = read_json(output)['repositories'][0]
    movable = {
        'branch-names': ('dev', 'dev_NK-8604'),
        'tracking-refs': (manifest['baseRef'], manifest['targetRef']),
        'abbreviated': (manifest['baseSha'][:12], manifest['targetSha'][:12]),
        'target-only': (manifest['baseSha'], 'dev_NK-8604'),
    }
    rejected, rejected_output = _collect(ctx, [{
        'role': role, 'path': manifest['repository'], 'source': 'remote',
        'remote': 'origin', 'baseRef': manifest['baseRef'],
        'targetRef': manifest['targetRef'], 'baseSha': base, 'targetSha': target,
    } for role, (base, target) in movable.items()])
    assert rejected.returncode == 1
    payload = read_json(rejected_output)
    assert payload['status'] == 'error'
    assert [(item['role'], item['code']) for item in payload['errors']] == [
        (role, 'REMOTE_SHA_REQUIRED') for role in movable]
    for record in payload['repositories']:
        assert record['base']['sha'] is None and record['target']['sha'] is None
        assert record['changes'] == [] and record['commits'] == []
        assert record['mergeBase'] is None
    assert manifest['targetSha'] not in rejected_output.read_text(encoding='utf-8')


@scenario
def prepare_missing_remote_branch_never_falls_back_to_local_refs(ctx):
    local, _remote, shas = _make_remote_pair(ctx)
    # The formal clone knows a branch that the live remote does not have, both
    # as its current HEAD and as a leftover refs/remotes/origin/* tracking ref.
    run_git(local, 'switch', '--quiet', '-c', 'dev_local_only')
    (local / 'local-only.txt').write_text('never pushed\n', encoding='utf-8')
    local_only = commit_all(local, 'local only commit')
    run_git(local, 'update-ref', 'refs/remotes/origin/dev_local_only', local_only)
    before = repo_fingerprint(local)

    completed, output = _prepare(ctx, [_entry('client', local, target='dev_local_only')])
    assert completed.returncode == 1
    payload = read_json(output)
    assert payload['status'] == 'error'
    assert payload['repositories'] == []
    assert payload['errors'] == [{'role': 'client', 'code': 'REMOTE_BRANCH_MISSING'}]
    text = output.read_text(encoding='utf-8')
    for sha in (local_only, shas['stale_target'], shas['base'], shas['live_target']):
        assert sha not in text
    assert repo_fingerprint(local) == before
    assert not (ctx.cache / '.client.lock').exists()


@scenario
def prepare_degrades_only_the_failing_role(ctx):
    client, _remote, client_shas = _make_remote_pair(ctx, 'client')
    server, _remote, _server_shas = _make_remote_pair(ctx, 'server')
    completed, output = _prepare(ctx, [
        _entry('client', client),
        _entry('server', server, target='dev_missing_on_remote'),
    ])
    assert completed.returncode == 2, completed.stderr
    payload = read_json(output)
    assert payload['status'] == 'partial'
    assert [item['role'] for item in payload['repositories']] == ['client']
    assert payload['repositories'][0]['targetSha'] == client_shas['live_target']
    assert payload['errors'] == [{'role': 'server', 'code': 'REMOTE_BRANCH_MISSING'}]
    assert [item.name for item in ctx.tmp.iterdir()
            if item.name.startswith('.remote-')] == []


@scenario
def prepare_reports_filter_unsupported_remote(ctx):
    local, _remote, _shas = _make_remote_pair(ctx, allow_filter=False)
    completed, output = _prepare(ctx, [_entry('client', local)])
    assert completed.returncode == 1
    payload = read_json(output)
    assert payload['repositories'] == []
    assert payload['errors'] == [{'role': 'client', 'code': 'REMOTE_FILTER_UNSUPPORTED'}]


@scenario(cases={
    'https-user-password': 'https://user:secret-token@example.invalid/k1/k1_client.git',
    'ssh-url': 'ssh://git@example.invalid/k1/k1_client.git',
    'scp-style': 'git@example.invalid:k1/k1_client.git',
    'plain-https': 'https://example.invalid/k1/k1_client.git',
})
def prepare_rejects_unsafe_remote_url_without_contacting_it(ctx, url):
    local, _remote, _shas = _make_remote_pair(ctx)
    run_git(local, 'remote', 'set-url', 'origin', url)
    before = repo_fingerprint(local)
    completed, output = _prepare(ctx, [_entry('client', local)])
    assert completed.returncode == 1
    payload = read_json(output)
    assert payload['repositories'] == []
    assert payload['errors'] == [{'role': 'client', 'code': 'REMOTE_URL_UNSAFE'}]
    assert 'secret-token' not in output.read_text(encoding='utf-8')
    assert 'secret-token' not in completed.stdout + completed.stderr
    # Rejected before any cache repository (and so any fetch) exists.
    assert not (ctx.cache / 'client').exists()
    assert repo_fingerprint(local) == before


@scenario
def prepare_rejects_fixture_remote_outside_project_tmp(ctx):
    local, _remote, _shas = _make_remote_pair(ctx)
    outside = init_repo(ctx.outside / 'outside-origin.git', bare=True)
    run_git(local, 'remote', 'set-url', 'origin', outside.as_uri())
    completed, output = _prepare(ctx, [_entry('client', local)])
    assert completed.returncode == 1
    assert read_json(output)['errors'] == [
        {'role': 'client', 'code': 'REMOTE_URL_UNSAFE'}]
    assert not (ctx.cache / 'client').exists()


@scenario
def prepare_rejects_repository_that_is_neither_formal_nor_fixture(ctx):
    stray, _base, _target = make_two_commit_repo(ctx.outside / 'stray')
    completed, output = _prepare(ctx, [_entry('client', stray)])
    assert completed.returncode == 1
    assert read_json(output)['errors'] == [
        {'role': 'client', 'code': 'REPOSITORY_NOT_ALLOWED'}]
    assert not (ctx.cache / 'client').exists()


@scenario
def prepare_only_accepts_origin_remote(ctx):
    local, remote, _shas = _make_remote_pair(ctx)
    run_git(local, 'remote', 'add', 'upstream', remote.as_uri())
    completed, output = _prepare(ctx, [_entry('client', local, remote='upstream')])
    assert completed.returncode == 1
    assert read_json(output)['errors'] == [{'role': 'client', 'code': 'INVALID_REMOTE'}]
    assert not (ctx.cache / 'client').exists()


@scenario(cases={
    'refspec': 'refs/heads/dev:refs/heads/evil',
    'wildcard-refspec': '+refs/heads/*:refs/remotes/origin/*',
    'option': '--upload-pack=touch x'})
def prepare_rejects_refspec_like_branch_names(ctx, branch):
    local, _remote, _shas = _make_remote_pair(ctx)
    completed, output = _prepare(ctx, [_entry('client', local, target=branch)])
    assert completed.returncode == 1
    assert read_json(output)['errors'] == [
        {'role': 'client', 'code': 'INVALID_REMOTE_BRANCH'}]
    assert not (ctx.cache / 'client').exists()


@scenario
def prepare_rejects_unknown_role(ctx):
    local, _remote, _shas = _make_remote_pair(ctx)
    completed, output = _prepare(ctx, [_entry('tools', local)])
    assert completed.returncode == 1
    assert read_json(output)['errors'] == [
        {'role': 'tools', 'code': 'INVALID_REPOSITORY_ROLE'}]


@scenario
def prepare_reports_cache_lock_and_keeps_foreign_lock(ctx):
    local, _remote, _shas = _make_remote_pair(ctx)
    lock = ctx.cache / '.client.lock'
    lock.write_text('held by another run', encoding='utf-8')
    completed, output = _prepare(ctx, [_entry('client', local)])
    assert completed.returncode == 1
    payload = read_json(output)
    assert payload['repositories'] == []
    assert payload['errors'] == [{'role': 'client', 'code': 'CACHE_LOCK_TIMEOUT'}]
    assert lock.read_text(encoding='utf-8') == 'held by another run'
    assert not (ctx.cache / 'client').exists()


@scenario
def prepare_rejects_cache_root_outside_project_cache(ctx):
    local, _remote, _shas = _make_remote_pair(ctx)
    foreign_cache = ctx.tmp / 'foreign-cache'
    completed, output = _prepare(ctx, [_entry('client', local)], cache=foreign_cache)
    assert completed.returncode == 1
    assert 'CACHE_OUTSIDE_PROJECT_CACHE' in completed.stderr
    assert not output.exists()
    assert not foreign_cache.exists()


@scenario
def prepare_rejects_output_outside_project_tmp(ctx):
    local, _remote, _shas = _make_remote_pair(ctx)
    request = write_json(ctx.tmp / 'request.json',
                         {'repositories': [_entry('client', local)]})
    outside = ctx.outside / 'manifest.json'
    completed = ctx.run(
        PREPARE, '-RequestPath', request, '-OutputPath', outside,
        '-CacheRoot', ctx.cache, '-TimeoutSeconds', '30')
    assert completed.returncode == 1
    assert 'OUTPUT_OUTSIDE_PROJECT_TMP' in completed.stderr
    assert not outside.exists()
    assert list(ctx.cache.iterdir()) == []


# --------------------------------------------------------------------------
# cleanup-run-evidence.ps1 (step 5.1 boundary: a marked direct child of .tmp)
# --------------------------------------------------------------------------

def _cleanup(ctx, action, run_directory, run_id, reason):
    completed = ctx.run(
        CLEANUP, '-Action', action, '-RunDirectory', run_directory,
        '-RunId', run_id, '-Reason', reason)
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    payload = json.loads(lines[-1]) if lines else None
    return completed, payload


def _initialize(ctx, run_id):
    completed, payload = _cleanup(
        ctx, 'Initialize', TMP_ROOT / run_id, run_id, 'initialization')
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert payload['code'] == 'RUN_INITIALIZED'
    return TMP_ROOT / run_id


def _marker(run_id, **overrides):
    marker = {'schemaVersion': 1, 'owner': 'review-k1-function', 'runId': run_id,
              'physicalProjectRoot': str(PROJECT_ROOT)}
    marker.update(overrides)
    return marker


@scenario
def cleanup_initialize_then_cleanup_removes_only_the_run(ctx):
    run_id = ctx.new_run_id()
    sibling_id = ctx.new_run_id()
    sibling = TMP_ROOT / sibling_id
    sibling.mkdir()
    write_json(sibling / '.review-k1-run.json', _marker(sibling_id))
    (sibling / 'keep.json').write_text('{}', encoding='utf-8')

    run_directory = _initialize(ctx, run_id)
    marker = read_json(run_directory / '.review-k1-run.json')
    assert marker['owner'] == 'review-k1-function'
    assert marker['runId'] == run_id
    assert Path(marker['physicalProjectRoot']).resolve() == PROJECT_ROOT.resolve()
    (run_directory / 'git-evidence.json').write_text('{}', encoding='utf-8')
    nested = run_directory / 'export' / 'config'
    nested.mkdir(parents=True)
    (nested / 'Activity.xlsx').write_bytes(b'PK\x03\x04')

    completed, payload = _cleanup(ctx, 'Cleanup', run_directory, run_id, 'success')
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert payload['status'] == 'ok' and payload['code'] == 'RUN_CLEANED'
    assert payload['runId'] == run_id and payload['reason'] == 'success'
    assert not run_directory.exists()
    assert (sibling / 'keep.json').read_text(encoding='utf-8') == '{}'
    assert (ctx.tmp).is_dir()

    completed, payload = _cleanup(ctx, 'Cleanup', run_directory, run_id, 'success')
    assert completed.returncode == 0
    assert payload['code'] == 'RUN_ALREADY_ABSENT'


@scenario
def cleanup_refuses_directory_outside_project_tmp(ctx):
    run_id = ctx.new_run_id()
    outside = ctx.outside / run_id
    outside.mkdir()
    (outside / 'user-data.txt').write_text('keep me', encoding='utf-8')
    write_json(outside / '.review-k1-run.json', _marker(run_id))
    completed, payload = _cleanup(ctx, 'Cleanup', outside, run_id, 'success')
    assert completed.returncode == 1
    assert payload['status'] == 'error'
    assert payload['code'] == 'RUN_DIRECTORY_OUTSIDE_TMP'
    assert (outside / 'user-data.txt').read_text(encoding='utf-8') == 'keep me'
    assert not (TMP_ROOT / run_id).exists()


@scenario
def cleanup_refuses_mismatched_run_directory(ctx):
    run_id = ctx.new_run_id()
    run_directory = _initialize(ctx, run_id)
    nested = run_directory / 'nested'
    nested.mkdir()
    (nested / 'file.txt').write_text('x', encoding='utf-8')
    candidates = {
        'nested': nested,
        'tmp-root': TMP_ROOT,
        'other-child': ctx.tmp,
        'traversal': run_directory / '..' / '..' / 'review-k1-function',
    }
    for label, candidate in candidates.items():
        completed, payload = _cleanup(ctx, 'Cleanup', candidate, run_id, 'error')
        assert completed.returncode == 1, label
        assert payload['code'] == 'RUN_DIRECTORY_OUTSIDE_TMP', label
    assert (nested / 'file.txt').exists()
    assert (run_directory / '.review-k1-run.json').exists()
    assert ctx.tmp.is_dir()
    assert (PROJECT_ROOT / 'review-k1-function' / 'SKILL.md').is_file()


@scenario(cases={'dot-dot': '..', 'parent-package': '../review-k1-function'})
def cleanup_rejects_unsafe_run_id(ctx, bad_id):
    completed, payload = _cleanup(ctx, 'Cleanup', TMP_ROOT / bad_id, bad_id, 'success')
    assert completed.returncode == 1
    assert payload['code'] == 'INVALID_RUN_ID'
    assert (PROJECT_ROOT / 'review-k1-function' / 'SKILL.md').is_file()
    assert TMP_ROOT.is_dir() and ctx.tmp.is_dir()


@scenario
def cleanup_refuses_directory_without_ownership_marker(ctx):
    run_id = ctx.new_run_id()
    foreign = TMP_ROOT / run_id
    foreign.mkdir()
    (foreign / 'someone-elses.json').write_text('{}', encoding='utf-8')
    completed, payload = _cleanup(ctx, 'Cleanup', foreign, run_id, 'success')
    assert completed.returncode == 1
    assert payload['code'] == 'OWNERSHIP_MARKER_MISSING'
    assert (foreign / 'someone-elses.json').exists()


@scenario(cases={
    'run-id': {'runId': 'another-run'},
    'project-root': {'physicalProjectRoot': '/some/other/project'}})
def cleanup_refuses_marker_of_another_run(ctx, overrides):
    run_id = ctx.new_run_id()
    foreign = TMP_ROOT / run_id
    foreign.mkdir()
    write_json(foreign / '.review-k1-run.json', _marker(run_id, **overrides))
    (foreign / 'evidence.json').write_text('{}', encoding='utf-8')
    completed, payload = _cleanup(ctx, 'Cleanup', foreign, run_id, 'success')
    assert completed.returncode == 1
    assert payload['code'] == 'OWNERSHIP_MARKER_INVALID'
    assert (foreign / 'evidence.json').exists()


@scenario
def cleanup_refuses_run_containing_symlink_and_keeps_target(ctx):
    run_id = ctx.new_run_id()
    run_directory = _initialize(ctx, run_id)
    outside = ctx.outside / 'outside'
    outside.mkdir()
    (outside / 'precious.txt').write_text('must survive', encoding='utf-8')
    _symlink(run_directory / 'link', outside)
    (run_directory / 'evidence.json').write_text('{}', encoding='utf-8')
    try:
        completed, payload = _cleanup(ctx, 'Cleanup', run_directory, run_id, 'exception')
        assert completed.returncode == 1
        assert payload['code'] == 'RUN_CONTENT_REPARSE_POINT'
        assert (outside / 'precious.txt').read_text(encoding='utf-8') == 'must survive'
        assert (run_directory / 'evidence.json').exists()
    finally:
        (run_directory / 'link').unlink(missing_ok=True)


@scenario
def cleanup_refuses_symlinked_run_directory(ctx):
    run_id = ctx.new_run_id()
    outside = ctx.outside / 'outside-run'
    outside.mkdir()
    write_json(outside / '.review-k1-run.json', _marker(run_id))
    (outside / 'precious.txt').write_text('must survive', encoding='utf-8')
    _symlink(TMP_ROOT / run_id, outside)
    try:
        completed, payload = _cleanup(
            ctx, 'Cleanup', TMP_ROOT / run_id, run_id, 'success')
        assert completed.returncode == 1
        assert payload['code'] == 'RUN_DIRECTORY_REPARSE_POINT'
        assert (outside / 'precious.txt').read_text(encoding='utf-8') == 'must survive'
    finally:
        (TMP_ROOT / run_id).unlink(missing_ok=True)


@scenario
def cleanup_initialize_refuses_existing_directory(ctx):
    run_id = ctx.new_run_id()
    existing = TMP_ROOT / run_id
    existing.mkdir()
    (existing / 'earlier.json').write_text('{}', encoding='utf-8')
    completed, payload = _cleanup(ctx, 'Initialize', existing, run_id, 'initialization')
    assert completed.returncode == 1
    assert payload['code'] == 'RUN_DIRECTORY_ALREADY_EXISTS'
    assert [item.name for item in existing.iterdir()] == ['earlier.json']


@scenario(cases={
    'initialize-with-exit-reason': ('Initialize', 'success'),
    'cleanup-with-initialization': ('Cleanup', 'initialization')})
def cleanup_requires_matching_action_and_reason(ctx, case):
    action, reason = case
    run_id = ctx.new_run_id()
    completed, payload = _cleanup(ctx, action, TMP_ROOT / run_id, run_id, reason)
    assert completed.returncode == 1
    assert payload['code'] == 'INVALID_REASON'
    assert not (TMP_ROOT / run_id).exists()


# --------------------------------------------------------------------------
# pytest wiring
# --------------------------------------------------------------------------

def _params():
    return [
        pytest.param(name, id=name, marks=(
            [pytest.mark.xfail(strict=True, reason=XFAIL[name])]
            if name in XFAIL else []))
        for name in SCENARIOS
    ]


@pytest.fixture(scope='module')
def outcomes(request, tmp_path_factory):
    selected = {}
    for item in request.session.items:
        if item.module is not request.module or not hasattr(item, 'callspec'):
            continue
        name = item.callspec.params.get('name')
        if name in SCENARIOS:
            selected[name] = SCENARIOS[name]
    return run_scenarios(selected, tmp_path_factory.mktemp('precheck-outside'))


@pytest.mark.parametrize('name', _params())
def test_precheck(name, outcomes):
    error = outcomes[name]
    if error is not None:
        raise error
