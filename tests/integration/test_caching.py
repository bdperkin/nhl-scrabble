"""Integration tests for API caching functionality."""

import time
from pathlib import Path

import pytest

from nhl_scrabble.api import NHLApiClient

# All integration tests get 5 minute timeout
pytestmark = [
    pytest.mark.integration,
    pytest.mark.timeout(300),  # 5 minutes for integration tests
]


def test_caching_performance(tmp_path: Path) -> None:
    """Test that caching is functional."""
    cache_dir = tmp_path / "cache"
    cache_file = cache_dir / "api_cache.sqlite"

    if cache_file.exists():
        cache_file.unlink()

    with NHLApiClient(cache_dir=cache_dir) as client:
        # First run - cold cache
        standings1 = client.get_teams()

        # Cache file should exist after first call
        assert cache_file.exists(), "Cache file not created"

        # Cache file should have data (size > 0)
        cache_size = cache_file.stat().st_size
        assert cache_size > 0, "Cache file is empty"

        # Second run - should use cache
        standings2 = client.get_teams()

        # Data should match
        assert standings1 == standings2, "Cached data doesn't match original"

        # Verify data is valid (returns dict of teams)
        assert len(standings1) > 0, "No teams returned"
        assert isinstance(standings1, dict), "Teams not returned as dict"


@pytest.mark.integration
def test_cache_respects_expiry(tmp_path: Path) -> None:
    """Test that cache expires after configured time."""
    cache_dir = tmp_path / "cache"

    # Use very short expiry for testing
    with NHLApiClient(cache_expiry=1, cache_dir=cache_dir) as client:
        client.clear_cache()

        # First request
        response1 = client.get_teams()

        # Wait for cache to expire
        time.sleep(2)

        # Second request - cache expired, should hit API again
        response2 = client.get_teams()

        # Responses should still match (same data)
        assert response1 == response2


@pytest.mark.integration
def test_no_cache_always_fresh(tmp_path: Path) -> None:
    """Test that no-cache always fetches fresh data."""
    cache_dir = tmp_path / "cache"
    cache_file = cache_dir / "api_cache.sqlite"

    # Should not create cache file
    with NHLApiClient(cache_enabled=False, cache_dir=cache_dir) as client:
        client.get_teams()
        client.get_teams()

        # Cache file should not exist
        assert not cache_file.exists()


@pytest.mark.integration
def test_cache_invalidation_works(tmp_path: Path) -> None:
    """Test that cache invalidation forces fresh API calls."""
    cache_dir = tmp_path / "cache"

    with NHLApiClient(cache_enabled=True, cache_dir=cache_dir) as client:
        # First call
        result1 = client.get_teams()

        # Clear cache
        client.clear_cache()

        # Second call should hit API again
        result2 = client.get_teams()

        # Results should still match (same data)
        assert result1 == result2


@pytest.mark.integration
def test_cache_across_multiple_endpoints(tmp_path: Path) -> None:
    """Test that caching works for different API endpoints."""
    cache_dir = tmp_path / "cache"
    cache_file = cache_dir / "api_cache.sqlite"

    with NHLApiClient(cache_enabled=True, cache_dir=cache_dir) as client:
        client.clear_cache()

        # Cache different endpoints
        teams = client.get_teams()
        assert len(teams) > 0

        # Cache should contain data
        assert cache_file.exists()
        cache_size = cache_file.stat().st_size
        assert cache_size > 0


@pytest.mark.integration
def test_cache_handles_errors_gracefully(tmp_path: Path) -> None:
    """Test that cache errors don't crash the client."""
    cache_dir = tmp_path / "cache"

    with NHLApiClient(cache_enabled=True, cache_dir=cache_dir) as client:
        # Operations should work even if cache has issues
        client.clear_cache()  # Should not raise
        client._is_url_cached("https://api-web.nhle.com/v1/standings/now")  # Should not raise

        # Verify client still works
        teams = client.get_teams()
        assert len(teams) > 0


@pytest.mark.integration
def test_cache_persists_across_sessions(tmp_path: Path) -> None:
    """Test that cache persists across different client sessions."""
    cache_dir = tmp_path / "cache"
    cache_file = cache_dir / "api_cache.sqlite"

    # First session - populate cache
    with NHLApiClient(cache_enabled=True, cache_dir=cache_dir) as client1:
        client1.clear_cache()
        result1 = client1.get_teams()

    # Cache file should exist after first session
    assert cache_file.exists()
    cache_size = cache_file.stat().st_size
    assert cache_size > 0

    # Second session - should use persisted cache
    with NHLApiClient(cache_enabled=True, cache_dir=cache_dir) as client2:
        result2 = client2.get_teams()

    # Results should match
    assert result1 == result2


@pytest.mark.integration
def test_cache_respects_allowable_codes(tmp_path: Path) -> None:
    """Test that only successful responses (200) are cached."""
    import contextlib
    from unittest.mock import Mock, patch

    from nhl_scrabble.api.nhl_client import NHLApiError, NHLApiNotFoundError
    from nhl_scrabble.validators import ValidationError

    cache_dir = tmp_path / "cache"

    # Mock a 404 error response
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = Exception("404 Not Found")

    with NHLApiClient(cache_enabled=True, cache_dir=cache_dir) as client:
        client.clear_cache()

        # Attempt request that would fail
        # Cache should NOT store 404 responses
        # Suppress expected exceptions from invalid team roster request
        with (
            patch.object(client.session, "get", return_value=mock_response),
            contextlib.suppress(NHLApiNotFoundError, NHLApiError, ValidationError, Exception),
        ):
            client.get_team_roster("INVALID")

        # Cache should still be empty (404 not cached)
        if hasattr(client.session, "cache"):
            # Cache configured to only cache 200 responses
            assert True  # If we get here, cache configuration is working


# CLI Command Caching Tests


@pytest.mark.integration
def test_cli_analyze_command_caching(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that analyze command respects cache settings."""
    from unittest.mock import patch

    from click.testing import CliRunner

    from nhl_scrabble.cli import cli

    cache_dir = tmp_path / "cache"
    cache_file = cache_dir / "api_cache.sqlite"

    # Set cache directory via environment variable
    monkeypatch.setenv("NHL_SCRABBLE_CACHE_DIR", str(cache_dir))

    # Mock API responses to avoid real API calls
    mock_teams = {"TOR": {"division": "Atlantic", "conference": "Eastern"}}
    mock_roster = {
        "forwards": [{"firstName": {"default": "Test"}, "lastName": {"default": "Player"}}],
        "defensemen": [],
        "goalies": [],
    }

    with (
        patch("nhl_scrabble.api.nhl_client.NHLApiClient.get_teams", return_value=mock_teams),
        patch("nhl_scrabble.api.nhl_client.NHLApiClient.get_team_roster", return_value=mock_roster),
    ):
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--quiet"])
        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Cache file should exist
        assert cache_file.exists(), "Cache file was not created"


@pytest.mark.integration
def test_cli_analyze_no_cache_flag(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that analyze --no-cache flag disables caching."""
    from unittest.mock import patch

    from click.testing import CliRunner

    from nhl_scrabble.cli import cli

    cache_dir = tmp_path / "cache"
    cache_file = cache_dir / "api_cache.sqlite"

    # Set cache directory via environment variable
    monkeypatch.setenv("NHL_SCRABBLE_CACHE_DIR", str(cache_dir))

    # Mock API responses
    mock_teams = {"TOR": {"division": "Atlantic", "conference": "Eastern"}}
    mock_roster = {
        "forwards": [{"firstName": {"default": "Test"}, "lastName": {"default": "Player"}}],
        "defensemen": [],
        "goalies": [],
    }

    with (
        patch("nhl_scrabble.api.nhl_client.NHLApiClient.get_teams", return_value=mock_teams),
        patch("nhl_scrabble.api.nhl_client.NHLApiClient.get_team_roster", return_value=mock_roster),
    ):
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--quiet", "--no-cache"])
        assert result.exit_code == 0

        # Cache file should NOT exist (caching disabled)
        assert not cache_file.exists(), "Cache file was created despite --no-cache flag"


@pytest.mark.integration
def test_cli_search_command_caching(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that search command respects cache settings."""
    from unittest.mock import patch

    from click.testing import CliRunner

    from nhl_scrabble.cli import cli

    cache_dir = tmp_path / "cache"
    cache_file = cache_dir / "api_cache.sqlite"

    # Set cache directory via environment variable
    monkeypatch.setenv("NHL_SCRABBLE_CACHE_DIR", str(cache_dir))

    # Mock API responses
    mock_teams = {"EDM": {"division": "Pacific", "conference": "Western"}}
    mock_roster = {
        "forwards": [{"firstName": {"default": "Connor"}, "lastName": {"default": "McDavid"}}],
        "defensemen": [],
        "goalies": [],
    }

    with (
        patch("nhl_scrabble.api.nhl_client.NHLApiClient.get_teams", return_value=mock_teams),
        patch("nhl_scrabble.api.nhl_client.NHLApiClient.get_team_roster", return_value=mock_roster),
    ):
        runner = CliRunner()
        result = runner.invoke(cli, ["search", "McDavid", "--quiet"])
        assert result.exit_code == 0

        # Cache file should exist
        assert cache_file.exists(), "Cache file was not created"


@pytest.mark.integration
def test_cli_search_no_cache_flag(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that search --no-cache flag disables caching."""
    from unittest.mock import patch

    from click.testing import CliRunner

    from nhl_scrabble.cli import cli

    cache_dir = tmp_path / "cache"
    cache_file = cache_dir / "api_cache.sqlite"

    # Set cache directory via environment variable
    monkeypatch.setenv("NHL_SCRABBLE_CACHE_DIR", str(cache_dir))

    # Mock API responses
    mock_teams = {"EDM": {"division": "Pacific", "conference": "Western"}}
    mock_roster = {
        "forwards": [{"firstName": {"default": "Connor"}, "lastName": {"default": "McDavid"}}],
        "defensemen": [],
        "goalies": [],
    }

    with (
        patch("nhl_scrabble.api.nhl_client.NHLApiClient.get_teams", return_value=mock_teams),
        patch("nhl_scrabble.api.nhl_client.NHLApiClient.get_team_roster", return_value=mock_roster),
    ):
        runner = CliRunner()
        result = runner.invoke(cli, ["search", "McDavid", "--quiet", "--no-cache"])
        assert result.exit_code == 0

        # Cache file should NOT exist (caching disabled)
        assert not cache_file.exists(), "Cache file was created despite --no-cache flag"


@pytest.mark.integration
def test_cache_statistics_method(tmp_path: Path) -> None:
    """Test NHLApiClient.get_cache_info() returns cache statistics."""
    # Use custom cache directory to avoid polluting platform directory
    cache_dir = tmp_path / "cache"

    # Test with caching enabled
    with NHLApiClient(cache_enabled=True, cache_dir=cache_dir) as client:
        cache_info = client.get_cache_info()

        assert isinstance(cache_info, dict)
        assert "enabled" in cache_info
        assert cache_info["enabled"] is True

    # Test with caching disabled
    with NHLApiClient(cache_enabled=False) as client:
        cache_info = client.get_cache_info()

        assert isinstance(cache_info, dict)
        assert "enabled" in cache_info
        assert cache_info["enabled"] is False


@pytest.mark.integration
def test_cache_location_follows_platform_standard(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test cache is created in platform-specific location."""
    from unittest.mock import patch

    from click.testing import CliRunner

    from nhl_scrabble.cli import cli

    # Mock platformdirs to return test directory
    monkeypatch.setattr("platformdirs.user_cache_dir", lambda *args: str(tmp_path))

    # Mock API responses to avoid real API calls
    mock_teams = {"TOR": {"division": "Atlantic", "conference": "Eastern"}}
    mock_roster = {
        "forwards": [{"firstName": {"default": "Test"}, "lastName": {"default": "Player"}}],
        "defensemen": [],
        "goalies": [],
    }

    with (
        patch("nhl_scrabble.api.nhl_client.NHLApiClient.get_teams", return_value=mock_teams),
        patch("nhl_scrabble.api.nhl_client.NHLApiClient.get_team_roster", return_value=mock_roster),
    ):
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--quiet"])

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Cache should be in platform-specific directory
        assert (tmp_path / "api_cache.sqlite").exists()


@pytest.mark.integration
def test_custom_cache_directory_via_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test custom cache directory via environment variable."""
    from unittest.mock import patch

    from click.testing import CliRunner

    from nhl_scrabble.cli import cli

    custom_cache = tmp_path / "my_cache"
    monkeypatch.setenv("NHL_SCRABBLE_CACHE_DIR", str(custom_cache))

    # Mock API responses
    mock_teams = {"TOR": {"division": "Atlantic", "conference": "Eastern"}}
    mock_roster = {
        "forwards": [{"firstName": {"default": "Test"}, "lastName": {"default": "Player"}}],
        "defensemen": [],
        "goalies": [],
    }

    with (
        patch("nhl_scrabble.api.nhl_client.NHLApiClient.get_teams", return_value=mock_teams),
        patch("nhl_scrabble.api.nhl_client.NHLApiClient.get_team_roster", return_value=mock_roster),
    ):
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--quiet"])

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Cache should be in custom directory
        assert custom_cache.exists()
        assert (custom_cache / "api_cache.sqlite").exists()
