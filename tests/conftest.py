"""Local pytest fixtures used across the test suite."""

import sys
from pathlib import Path
from unittest import mock

import pytest

# Make src-layout package importable when running tests from a source checkout.
ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


class _PatchProxy:
    """Expose mock.patch and mock.patch.dict through a pytest-mock-like API."""

    def __init__(self, owner):
        self._owner = owner

    def __call__(self, target, *args, **kwargs):
        return self._owner._start_patch(mock.patch(target, *args, **kwargs))

    def dict(self, target, values=(), clear=False, **kwargs):
        return self._owner._start_patch(
            mock.patch.dict(target, values=values, clear=clear, **kwargs)
        )


class _SimpleMocker:
    """Small subset of pytest-mock's mocker fixture used by this repository."""

    Mock = mock.Mock
    MagicMock = mock.MagicMock
    call = mock.call
    ANY = mock.ANY

    def __init__(self):
        self._active_patchers = []
        self.patch = _PatchProxy(self)

    def _start_patch(self, patcher):
        self._active_patchers.append(patcher)
        return patcher.start()

    def stopall(self):
        while self._active_patchers:
            self._active_patchers.pop().stop()


@pytest.fixture
def mocker():
    """Provide a minimal fallback for environments without pytest-mock."""
    helper = _SimpleMocker()
    try:
        yield helper
    finally:
        helper.stopall()
