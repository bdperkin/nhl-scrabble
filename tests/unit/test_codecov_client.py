"""Unit tests for Codecov API client."""

from unittest.mock import Mock, patch

import httpx
import pytest

from nhl_scrabble.analytics.codecov_client import CodecovClient, CodecovConfig


class TestCodecovConfig:
    """Tests for CodecovConfig."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = CodecovConfig()

        assert config.base_url == "https://api.codecov.io"
        assert config.org == "gh"
        assert config.owner == "bdperkin"
        assert config.repo == "nhl-scrabble"
        assert config.token == ""

    def test_custom_config(self) -> None:
        """Test custom configuration values."""
        config = CodecovConfig(
            base_url="https://custom.codecov.io",
            org="custom-org",
            owner="custom-owner",
            repo="custom-repo",
            token="custom-token",  # noqa: S106
        )

        assert config.base_url == "https://custom.codecov.io"
        assert config.org == "custom-org"
        assert config.owner == "custom-owner"
        assert config.repo == "custom-repo"
        assert config.token == "custom-token"  # noqa: S105

    def test_from_env_with_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test loading config from environment with token set."""
        monkeypatch.setenv("CODECOV_TOKEN", "test-token-123")
        config = CodecovConfig.from_env()

        assert config.token == "test-token-123"  # noqa: S105
        assert config.base_url == "https://api.codecov.io"  # Still uses defaults

    def test_from_env_without_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test loading config from environment without token."""
        monkeypatch.delenv("CODECOV_TOKEN", raising=False)
        config = CodecovConfig.from_env()

        assert config.token == ""


class TestCodecovClient:
    """Tests for CodecovClient."""

    @pytest.fixture
    def config(self) -> CodecovConfig:
        """Create test configuration."""
        return CodecovConfig(token="test-token")  # noqa: S106

    @pytest.fixture
    def mock_response(self) -> Mock:
        """Create mock HTTP response."""
        response = Mock(spec=httpx.Response)
        response.status_code = 200
        response.json.return_value = {"success": True}
        return response

    def test_client_initialization(self, config: CodecovConfig) -> None:
        """Test client initialization."""
        client = CodecovClient(config)

        assert client.config == config
        assert client._client is None  # Client not created yet

    def test_client_property_creates_client(self, config: CodecovConfig) -> None:
        """Test that client property creates HTTP client on first access."""
        client = CodecovClient(config)

        # Access client property
        http_client = client.client

        assert isinstance(http_client, httpx.Client)
        assert client._client is not None

    def test_client_property_with_token(self, config: CodecovConfig) -> None:
        """Test that client includes auth header when token is set."""
        client = CodecovClient(config)
        http_client = client.client

        assert "Authorization" in http_client.headers
        assert http_client.headers["Authorization"] == "Bearer test-token"

    def test_client_property_without_token(self) -> None:
        """Test that client works without token."""
        config = CodecovConfig(token="")
        client = CodecovClient(config)
        http_client = client.client

        assert "Authorization" not in http_client.headers

    @patch("httpx.Client")
    def test_get_test_analytics_success(
        self,
        mock_client_class: Mock,
        config: CodecovConfig,
        mock_response: Mock,
    ) -> None:
        """Test successful test analytics fetch."""
        mock_response.json.return_value = {
            "test_analytics": {
                "tests": [
                    {
                        "name": "test_example",
                        "avg_duration": 1.5,
                        "failure_rate": 0.1,
                    },
                ],
            },
        }

        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        with CodecovClient(config) as client:
            # Override client property to use our mock
            client._client = mock_client
            data = client.get_test_analytics()

        assert "test_analytics" in data
        assert len(data["test_analytics"]["tests"]) == 1
        mock_client.get.assert_called_once()

    @patch("httpx.Client")
    def test_get_test_analytics_404_fallback(
        self,
        mock_client_class: Mock,
        config: CodecovConfig,
    ) -> None:
        """Test that 404 errors on test analytics return empty data."""
        mock_response = Mock()
        mock_response.status_code = 404
        error = httpx.HTTPStatusError(
            message="Not Found",
            request=Mock(),
            response=mock_response,
        )

        mock_client = Mock()
        mock_client.get.side_effect = error
        mock_client_class.return_value = mock_client

        with CodecovClient(config) as client:
            client._client = mock_client
            data = client.get_test_analytics()

        # Should return empty data structure instead of raising
        assert data == {"test_analytics": {"tests": []}}

    @patch("httpx.Client")
    def test_get_test_analytics_other_error_raises(
        self,
        mock_client_class: Mock,
        config: CodecovConfig,
    ) -> None:
        """Test that non-404 errors are raised."""
        mock_response = Mock()
        mock_response.status_code = 500
        error = httpx.HTTPStatusError(
            message="Server Error",
            request=Mock(),
            response=mock_response,
        )

        mock_client = Mock()
        mock_client.get.side_effect = error
        mock_client_class.return_value = mock_client

        with CodecovClient(config) as client:
            client._client = mock_client
            with pytest.raises(httpx.HTTPStatusError):
                client.get_test_analytics()

    @patch("httpx.Client")
    def test_get_coverage_report(
        self,
        mock_client_class: Mock,
        config: CodecovConfig,
        mock_response: Mock,
    ) -> None:
        """Test coverage report fetch."""
        mock_response.json.return_value = {
            "files": [
                {
                    "name": "src/example.py",
                    "totals": {"coverage": 75.0, "lines": 100, "hits": 75},
                },
            ],
        }

        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        with CodecovClient(config) as client:
            client._client = mock_client
            data = client.get_coverage_report()

        assert "files" in data
        assert len(data["files"]) == 1
        assert data["files"][0]["name"] == "src/example.py"

    @patch("httpx.Client")
    def test_get_coverage_report_with_commit(
        self,
        mock_client_class: Mock,
        config: CodecovConfig,
        mock_response: Mock,
    ) -> None:
        """Test coverage report fetch with specific commit."""
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        with CodecovClient(config) as client:
            client._client = mock_client
            client.get_coverage_report(commit="abc123")

        # Verify commit SHA was included in URL
        call_args = mock_client.get.call_args
        assert "abc123" in call_args[0][0]

    @patch("httpx.Client")
    def test_get_coverage_trends(
        self,
        mock_client_class: Mock,
        config: CodecovConfig,
        mock_response: Mock,
    ) -> None:
        """Test coverage trends fetch."""
        mock_response.json.return_value = {
            "results": [
                {
                    "commitid": "abc123",
                    "timestamp": "2024-01-01T00:00:00Z",
                    "totals": {"coverage": 85.5},
                    "author": {"username": "testuser"},
                },
                {
                    "commitid": "def456",
                    "timestamp": "2024-01-02T00:00:00Z",
                    "totals": {"coverage": 86.0},
                    "author": {"username": "testuser2"},
                },
            ],
        }

        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        with CodecovClient(config) as client:
            client._client = mock_client
            trends = client.get_coverage_trends(branch="main", days=30)

        assert len(trends) == 2
        assert trends[0]["commit"] == "abc123"
        assert trends[0]["coverage"] == 85.5
        assert trends[0]["author"] == "testuser"

    @patch("httpx.Client")
    def test_get_coverage_trends_filters_null_coverage(
        self,
        mock_client_class: Mock,
        config: CodecovConfig,
        mock_response: Mock,
    ) -> None:
        """Test that trends with null coverage are filtered out."""
        mock_response.json.return_value = {
            "results": [
                {
                    "commitid": "abc123",
                    "timestamp": "2024-01-01T00:00:00Z",
                    "totals": {"coverage": 85.5},
                    "author": {"username": "testuser"},
                },
                {
                    "commitid": "def456",
                    "timestamp": "2024-01-02T00:00:00Z",
                    "totals": {"coverage": None},  # Null coverage
                    "author": {"username": "testuser2"},
                },
            ],
        }

        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        with CodecovClient(config) as client:
            client._client = mock_client
            trends = client.get_coverage_trends()

        # Should only include commit with non-null coverage
        assert len(trends) == 1
        assert trends[0]["commit"] == "abc123"

    def test_context_manager_closes_client(self, config: CodecovConfig) -> None:
        """Test that context manager closes HTTP client."""
        with CodecovClient(config) as client:
            # Access client to create it
            _ = client.client
            assert client._client is not None

        # After exiting context, client should be closed
        assert client._client is None
