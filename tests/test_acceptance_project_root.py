import pytest

from acceptance_support import module


def test_windows_repository_write_guard_uses_supplied_root(monkeypatch):
    core = module('core')
    monkeypatch.setenv('K1_PROJECT_ROOT', r'D:\K1 Work')
    with pytest.raises(core.WorkflowError, match='FORMAL_REPOSITORY_READ_ONLY'):
        core.reject_formal_write(r'D:\K1 Work\K1Client\k1_client\output.json')
    core.reject_formal_write(r'D:\Other Work\output.json')


def test_repository_write_guard_requires_project_root(monkeypatch, tmp_path):
    core = module('core')
    monkeypatch.delenv('K1_PROJECT_ROOT', raising=False)
    with pytest.raises(core.WorkflowError, match='K1_PROJECT_ROOT_REQUIRED'):
        core.reject_formal_write(tmp_path / 'output.json')


def test_repository_write_guard_uses_supplied_posix_root(monkeypatch, tmp_path):
    core = module('core')
    root = tmp_path / 'chosen-k1-root'
    monkeypatch.setenv('K1_PROJECT_ROOT', str(root))
    with pytest.raises(core.WorkflowError, match='FORMAL_REPOSITORY_READ_ONLY'):
        core.reject_formal_write(root / 'K1Game' / 'game' / 'output.json')
