"""Pytest configuration and shared fixtures for web automation tests."""

from typing import Any

import pytest


@pytest.fixture(scope="session")  # type: ignore[untyped-decorator]
def browser_type_launch_args() -> dict[str, Any]:
    """Return browser launch arguments."""
    return {
        "headless": True,
        "slow_mo": 0,
    }


@pytest.fixture(scope="session")  # type: ignore[untyped-decorator]
def browser_context_args() -> dict[str, Any]:
    """Return browser context arguments."""
    return {
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
    }


@pytest.fixture  # type: ignore[untyped-decorator]
def base_url() -> str:
    """Return the base URL for the application under test."""
    return "http://localhost:5000"
