"""Isolation for the e2e layer: redirect user state into a tmp dir.

Explicit save/restore (no monkeypatch — PA-306): a deleted var would be
repopulated from the real `.env` via dotenv, so SCITEX_DIR is pointed at
an empty tmp tree instead of being removed.
"""

from __future__ import annotations

import os

import pytest


@pytest.fixture(autouse=True)
def _isolated_scitex_dir(tmp_path):
    previous = os.environ.get("SCITEX_DIR")
    os.environ["SCITEX_DIR"] = str(tmp_path / ".scitex")
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("SCITEX_DIR", None)
        else:
            os.environ["SCITEX_DIR"] = previous
