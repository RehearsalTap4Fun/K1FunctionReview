"""Isolated filesystem helpers for lifecycle publication tests."""
from pathlib import Path
import shutil
import subprocess
import uuid

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def supplied_k1_project_root(monkeypatch, tmp_path):
    monkeypatch.setenv('K1_PROJECT_ROOT', str(tmp_path / 'user-supplied-k1-root'))


def run_git(repo, *args, check=True):
    return subprocess.run(['git', '-C', str(repo), *args], check=check,
                          capture_output=True, text=True, encoding='utf-8')


@pytest.fixture
def project_tmp():
    boundary = (PROJECT_ROOT / '.tmp').resolve()
    path = boundary / ('pytest-lifecycle-' + uuid.uuid4().hex)
    path.mkdir(parents=True)
    try:
        yield path
    finally:
        assert path.resolve().is_relative_to(boundary)
        # Windows Git objects can be read-only; preserve the failed-test fixture
        # if cleanup cannot remove it. Never change any repository outside .tmp.
        shutil.rmtree(path, ignore_errors=True)
