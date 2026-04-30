"""Codecov API client for test analytics and coverage data."""

import os
from typing import Any

import httpx
from pydantic import BaseModel, Field


class CodecovConfig(BaseModel):  # type: ignore[explicit-any]
    """Codecov API configuration."""

    base_url: str = Field(
        default="https://api.codecov.io",
        description="Base URL for Codecov API",
    )
    org: str = Field(
        default="gh",
        description="Organization type (gh for GitHub)",
    )
    owner: str = Field(
        default="bdperkin",
        description="Repository owner username",
    )
    repo: str = Field(
        default="nhl-scrabble",
        description="Repository name",
    )
    token: str = Field(
        default="",
        description="Codecov API token",
    )

    @classmethod
    def from_env(cls) -> "CodecovConfig":
        """Load configuration from environment variables.

        Returns:
            CodecovConfig: Configuration instance with token from CODECOV_TOKEN env var.
        """
        return cls(
            token=os.getenv("CODECOV_TOKEN", ""),
        )


class CodecovClient:
    """Client for interacting with Codecov API.

    This client provides methods to fetch test analytics, coverage reports,
    and coverage trends from the Codecov API.

    Args:
        config: Codecov API configuration with authentication token.

    Example:
        >>> config = CodecovConfig.from_env()
        >>> with CodecovClient(config) as client:
        ...     data = client.get_coverage_report()
    """

    def __init__(self, config: CodecovConfig) -> None:
        """Initialize Codecov API client.

        Args:
            config: Codecov API configuration.
        """
        self.config = config
        self._client: httpx.Client | None = None

    @property
    def client(self) -> httpx.Client:
        """Get or create HTTP client.

        Returns:
            httpx.Client: Configured HTTP client.
        """
        if self._client is None:
            headers = {
                "accept": "application/json",
            }
            if self.config.token:
                headers["Authorization"] = f"Bearer {self.config.token}"

            self._client = httpx.Client(
                base_url=self.config.base_url,
                headers=headers,
                timeout=30.0,
            )
        return self._client

    def get_test_analytics(self) -> dict[str, Any]:  # type: ignore[explicit-any]
        """Fetch test analytics data from Codecov.

        Note: This endpoint may not be available for all repositories.
        Falls back to empty data if endpoint is not found.

        Returns:
            dict[str, Any]: Test analytics data including test execution metrics.

        Raises:
            httpx.HTTPStatusError: If API request fails with non-404 error.
        """
        url = f"/api/v2/{self.config.org}/{self.config.owner}/repos/{self.config.repo}/test-analytics/"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response.json()  # type: ignore[no-any-return]
        except httpx.HTTPStatusError as e:
            # Test analytics endpoint may not exist for all repos
            if e.response.status_code == 404:
                return {"test_analytics": {"tests": []}}
            raise

    def get_coverage_report(  # type: ignore[explicit-any]
        self,
        commit: str | None = None,
    ) -> dict[str, Any]:
        """Fetch coverage report for a specific commit or latest.

        Args:
            commit: Optional commit SHA to get coverage for. If None, gets latest.

        Returns:
            dict[str, Any]: Coverage report data including file-level coverage.

        Raises:
            httpx.HTTPStatusError: If API request fails.
        """
        url = f"/api/v2/{self.config.org}/{self.config.owner}/repos/{self.config.repo}/report/"
        if commit:
            url += f"{commit}/"

        response = self.client.get(url)
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    def get_coverage_trends(  # type: ignore[explicit-any]
        self,
        branch: str = "main",
        days: int = 30,
    ) -> list[dict[str, Any]]:
        """Fetch coverage trends for a branch over time.

        Args:
            branch: Branch name to get trends for. Defaults to "main".
            days: Number of days of history to fetch. Defaults to 30.

        Returns:
            list[dict[str, Any]]: List of commit coverage data ordered by recency.

        Raises:
            httpx.HTTPStatusError: If API request fails.
        """
        url = f"/api/v2/{self.config.org}/{self.config.owner}/repos/{self.config.repo}/commits/"
        params = {"branch": branch}

        response = self.client.get(url, params=params)
        response.raise_for_status()
        commits = response.json().get("results", [])

        # Extract coverage from each commit
        trends = []
        for commit in commits[:days]:  # Limit to recent commits
            totals = commit.get("totals", {})
            coverage = totals.get("coverage")
            if coverage is not None:
                trends.append(
                    {
                        "commit": commit["commitid"],
                        "timestamp": commit["timestamp"],
                        "coverage": coverage,
                        "author": commit.get("author", {}).get("username"),
                    }
                )

        return trends

    def __enter__(self) -> "CodecovClient":
        """Enter context manager.

        Returns:
            CodecovClient: This client instance.
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Exit context manager and close HTTP client.

        Args:
            *args: Exception information (unused).
        """
        if self._client is not None:
            self._client.close()
            self._client = None
