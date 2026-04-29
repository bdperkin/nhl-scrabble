"""Pytest configuration for performance tests.

Provides fixtures and utilities specific to performance and load testing.
"""

import shutil
from collections.abc import Generator
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def performance_report_dir() -> Generator[Path, None, None]:
    """Create directory for performance test reports.

    Yields:
        Path to performance reports directory

    The directory is cleaned up after the test session.
    """
    report_dir = Path("qa/web/tests/performance/reports")
    report_dir.mkdir(parents=True, exist_ok=True)

    yield report_dir

    # Cleanup is optional - keep reports for analysis


@pytest.fixture(scope="session")
def load_test_results_dir() -> Generator[Path, None, None]:
    """Create directory for load test results.

    Yields:
        Path to load test results directory

    The directory is cleaned up after the test session.
    """
    results_dir = Path("qa/web/tests/performance/results")
    results_dir.mkdir(parents=True, exist_ok=True)

    yield results_dir

    # Cleanup is optional - keep results for analysis


@pytest.fixture
def performance_thresholds() -> dict[str, float]:
    """Return performance thresholds for various metrics.

    Returns:
        Dictionary of threshold names to values (in seconds)
    """
    return {
        "page_load": 2.0,
        "api_response": 1.0,
        "fast_page": 1.0,
        "render_time": 0.5,
    }


@pytest.fixture(scope="session")
def skip_if_locust_unavailable() -> None:
    """Skip tests if Locust is not installed.

    Raises:
        pytest.skip: If Locust is not available
    """
    if shutil.which("locust") is None:
        pytest.skip("Locust not found (install with: pip install locust)")
