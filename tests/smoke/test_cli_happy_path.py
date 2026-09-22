#!/usr/bin/env python3
"""Smoke layer (PS-211): fast subprocess CLI happy-path tests (<60s).

Runs the installed `scitex-resource` console script (falling back to
`python -m scitex_resource`) in a subprocess with an isolated SCITEX_DIR
(see conftest.py) and asserts the happy path stays green.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys

import pytest

_CONSOLE = shutil.which("scitex-resource")
_BASE_CMD = [_CONSOLE] if _CONSOLE else [sys.executable, "-m", "scitex_resource"]


@pytest.mark.smoke
def test_cli_version_reports_package():
    """`--version` must exit 0 and name the distribution."""
    # Arrange
    cmd = [*_BASE_CMD, "--version"]
    # Act
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    # Assert
    assert result.returncode == 0 and "scitex-resource" in result.stdout


@pytest.mark.smoke
def test_metrics_show_json_shape():
    """`metrics show --no-gpu --json` must exit 0 with a metric payload."""
    # Arrange
    cmd = [*_BASE_CMD, "metrics", "show", "--no-gpu", "--json"]
    # Act
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    # Assert
    assert result.returncode == 0 and json.loads(result.stdout)["cpu_count"] > 0
