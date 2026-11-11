"""Shared helpers for the static-precheck PowerShell script regression tests.

Every fixture repository is created inside this project's own ``.tmp`` (or the
script-mandated ``.cache/fast-precheck/remote-git`` object cache).  Nothing in
here contacts a network remote or touches a formal K1 repository.
"""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import shutil
import subprocess
import uuid

from conftest import run_git

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PROJECT_ROOT / 'review-k1-function' / 'scripts'
TMP_ROOT = PROJECT_ROOT / '.tmp'
REMOTE_CACHE_BOUNDARY = PROJECT_ROOT / '.cache' / 'fast-precheck' / 'remote-git'

POWERSHELL = shutil.which('pwsh') or (
    shutil.which('powershell') if os.name == 'nt' else None
)

LFS_POINTER = (
    b'version https://git-lfs.github.com/spec/v1\n'
    b'oid sha256:' + b'a' * 64 + b'\n'
    b'size 123456\n'
)


def run_script(name, *args, env=None, timeout=120):
    """Run one precheck script exactly the way the skill invokes it."""
    command = [POWERSHELL, '-NoProfile', '-File', str(SCRIPTS / name)]
    command += [str(value) for value in args]
    return subprocess.run(
        command, capture_output=True, text=True, encoding='utf-8',
        env=env, timeout=timeout, stdin=subprocess.DEVNULL,
    )


def write_json(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
    return path


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def init_repo(path, *, bare=False, branch='dev'):
    path.mkdir(parents=True)
    arguments = ['init', '--quiet', '--initial-branch', branch]
    if bare:
        arguments.append('--bare')
    subprocess.run(['git', *arguments, str(path)], check=True,
                   capture_output=True, text=True, encoding='utf-8')
    if not bare:
        for key, value in (
            ('user.name', 'Precheck Fixture'),
            ('user.email', 'precheck-fixture@example.invalid'),
            ('commit.gpgsign', 'false'),
            ('core.autocrlf', 'false'),
            ('core.hooksPath', str(path / '.git' / 'no-hooks')),
        ):
            run_git(path, 'config', key, value)
    return path


def commit_all(repo, message):
    run_git(repo, 'add', '--all')
    run_git(repo, 'commit', '--quiet', '--no-verify', '-m', message)
    return run_git(repo, 'rev-parse', 'HEAD').stdout.strip()


def make_two_commit_repo(path):
    """Repository with a base commit and one target commit on branch ``dev``.

    base   : keep.txt, modify.txt, delete.txt, config/Activity.xlsx (LFS pointer)
    target : modify.txt changed, delete.txt removed, added/new.txt added
    """
    repo = init_repo(path)
    (repo / 'keep.txt').write_text('keep\n', encoding='utf-8')
    (repo / 'modify.txt').write_bytes(b'base line\r\n\xff\xfe binary tail')
    (repo / 'delete.txt').write_text('to be deleted\n', encoding='utf-8')
    (repo / 'config').mkdir()
    (repo / 'config' / 'Activity.xlsx').write_bytes(LFS_POINTER)
    base = commit_all(repo, 'base commit')
    (repo / 'modify.txt').write_bytes(b'target line\r\n\x00\x01 other tail')
    (repo / 'delete.txt').unlink()
    (repo / 'added').mkdir()
    (repo / 'added' / 'new.txt').write_text('new file\n', encoding='utf-8')
    target = commit_all(repo, 'target commit')
    return repo, base, target


def repo_fingerprint(repo):
    """Everything a read-only command must leave untouched."""
    git_dir = Path(run_git(repo, 'rev-parse', '--absolute-git-dir').stdout.strip())
    index = git_dir / 'index'
    return {
        'head': run_git(repo, 'rev-parse', 'HEAD').stdout,
        'symbolic': run_git(repo, 'symbolic-ref', '-q', 'HEAD', check=False).stdout,
        'refs': run_git(repo, 'for-each-ref', '--format=%(refname) %(objectname)').stdout,
        'status': run_git(
            repo, '--no-optional-locks', 'status', '--porcelain=v1',
            '--untracked-files=all', check=False).stdout,
        'index': index.read_bytes() if index.is_file() else None,
        'fetch_head': (git_dir / 'FETCH_HEAD').exists(),
        'stash': run_git(repo, 'stash', 'list', check=False).stdout,
        'objects': run_git(repo, 'count-objects', '-v').stdout,
    }


class Scratch:
    """Per-scenario sandbox: a directory in .tmp, one outside the project,
    an optional remote-git cache root and optional run ids below .tmp."""

    def __init__(self, outside_root):
        token = uuid.uuid4().hex
        self.tmp = TMP_ROOT / ('pytest-precheck-' + token)
        self.tmp.mkdir(parents=True)
        self.outside = Path(outside_root) / token
        self.outside.mkdir(parents=True)
        self.env = dict(os.environ)
        self.env['K1_PROJECT_ROOT'] = str(self.outside / 'user-supplied-k1-root')
        self.env['POWERSHELL_TELEMETRY_OPTOUT'] = '1'
        self.env['POWERSHELL_UPDATECHECK'] = 'Off'
        self._cache = None
        self._run_ids = []

    def run(self, name, *args, env=None):
        return run_script(name, *args, env=self.env if env is None else env)

    def repo(self):
        return make_two_commit_repo(self.tmp / 'repo')

    @property
    def cache(self):
        if self._cache is None:
            self._cache = REMOTE_CACHE_BOUNDARY / ('pytest-precheck-' + uuid.uuid4().hex)
            self._cache.mkdir(parents=True)
        return self._cache

    def new_run_id(self):
        value = 'pytest-precheck-run-' + uuid.uuid4().hex
        self._run_ids.append(value)
        return value

    def close(self):
        boundary = TMP_ROOT.resolve()
        targets = [self.tmp] + [TMP_ROOT / value for value in self._run_ids]
        for target in targets:
            assert target.parent.resolve() == boundary
            if target.is_symlink():
                target.unlink()
            else:
                shutil.rmtree(target, ignore_errors=True)
        if self._cache is not None:
            assert self._cache.parent.resolve() == REMOTE_CACHE_BOUNDARY.resolve()
            shutil.rmtree(self._cache, ignore_errors=True)
        shutil.rmtree(self.outside, ignore_errors=True)


def run_scenarios(scenarios, outside_root, workers=None):
    """Run scenario callables concurrently (PowerShell start-up dominates the
    cost) and return {name: None | raised exception}."""
    workers = workers or max(2, min(8, os.cpu_count() or 2))
    cache_parents = [
        parent for parent in (
            REMOTE_CACHE_BOUNDARY.parent.parent, REMOTE_CACHE_BOUNDARY.parent,
            REMOTE_CACHE_BOUNDARY,
        ) if not parent.exists()
    ]
    TMP_ROOT.mkdir(exist_ok=True)

    def execute(item):
        name, function = item
        scratch = Scratch(outside_root)
        try:
            function(scratch)
            return name, None
        except BaseException as error:  # includes pytest skip/fail outcomes
            if isinstance(error, (KeyboardInterrupt, SystemExit)):
                raise
            return name, error
        finally:
            scratch.close()

    try:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            return dict(pool.map(execute, list(scenarios.items())))
    finally:
        for parent in reversed(cache_parents):
            try:
                parent.rmdir()
            except OSError:
                pass
