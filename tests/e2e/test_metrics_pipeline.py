#!/usr/bin/env python3
"""E2E layer (PS-212): real-subsystem workflows, loopback only, no network.

Covers the metrics pipeline end to end: live psutil collection ->
heartbeat-shape dict -> JSON render. Gated by `RUN_E2E=1` (skipped by
default); the `e2e` marker is registered in `pyproject.toml`.
"""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_E2E") != "1",
    reason="e2e layer runs only with RUN_E2E=1",
)

from scitex_resource._specs._metrics import get_metrics


@pytest.mark.e2e
def test_metrics_pipeline_live_values():
    """Live-collected metrics must carry sane host values."""
    # Arrange
    # Act
    metrics = get_metrics(gpu=False)
    # Assert
    assert (
        metrics["cpu_count"] > 0
        and metrics["mem_total_mb"] > 0
        and metrics["load_avg_1m"] >= 0
    )
