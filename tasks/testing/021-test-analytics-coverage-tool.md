# Test Analytics and Coverage Analysis Tool

**GitHub Issue**: #359 - https://github.com/bdperkin/nhl-scrabble/issues/359

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

4-6 hours

## Description

Create a dedicated tool to analyze test analytics and coverage data from Codecov API. This tool will provide insights into test performance, coverage trends, failure patterns, and help identify areas needing more testing attention.

## Current State

We currently have:
- Codecov integration for coverage tracking and reporting
- Coverage badges in README showing overall coverage percentage
- PR-level coverage checks via codecov/patch and codecov/project
- Diff-cover for tracking coverage on changed lines

What we don't have:
- Easy way to query and analyze test analytics programmatically
- Historical trend analysis of coverage and test performance
- Detailed insights into which tests are slowest, flakiest, or most prone to failure
- Coverage gap analysis showing which modules need more testing

## Proposed Solution

Create a CLI tool `nhl-scrabble test-analytics` (or standalone script) that:

1. **Integrates with Codecov API** to fetch test analytics data
2. **Analyzes coverage trends** over time (improving/declining/stable)
3. **Identifies coverage gaps** (modules with low coverage)
4. **Highlights slow tests** that impact CI performance
5. **Detects flaky tests** with inconsistent pass/fail patterns
6. **Generates actionable reports** in text, JSON, or HTML format

### API Integration

```python
# src/nhl_scrabble/analytics/codecov_client.py
import os
from typing import Any
import httpx
from pydantic import BaseModel


class CodecovConfig(BaseModel):
    """Codecov API configuration."""

    base_url: str = "https://api.codecov.io/api/v2"
    org: str = "gh"
    owner: str = "bdperkin"
    repo: str = "nhl-scrabble"
    token: str = ""  # From environment: CODECOV_TOKEN

    @classmethod
    def from_env(cls) -> "CodecovConfig":
        """Load config from environment."""
        return cls(
            token=os.getenv("CODECOV_TOKEN", ""),
        )


class CodecovClient:
    """Client for Codecov API."""

    def __init__(self, config: CodecovConfig):
        self.config = config
        self.client = httpx.Client(
            base_url=config.base_url,
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {config.token}" if config.token else "",
            },
            timeout=30.0,
        )

    def get_test_analytics(self) -> dict[str, Any]:
        """Fetch test analytics data.

        Example endpoint:
        GET /api/v2/gh/bdperkin/repos/nhl-scrabble/test-analytics/
        """
        url = f"/{self.config.org}/{self.config.owner}/repos/{self.config.repo}/test-analytics/"
        response = self.client.get(url)
        response.raise_for_status()
        return response.json()

    def get_coverage_report(self, commit: str | None = None) -> dict[str, Any]:
        """Fetch coverage report for a specific commit or latest."""
        url = f"/{self.config.org}/{self.config.owner}/repos/{self.config.repo}/report/"
        if commit:
            url += f"{commit}/"
        response = self.client.get(url)
        response.raise_for_status()
        return response.json()

    def get_coverage_trends(self, branch: str = "main", days: int = 30) -> list[dict[str, Any]]:
        """Fetch coverage trends for a branch over time."""
        url = f"/{self.config.org}/{self.config.owner}/repos/{self.config.repo}/commits/"
        params = {"branch": branch}
        response = self.client.get(url, params=params)
        response.raise_for_status()
        commits = response.json().get("results", [])

        # Extract coverage from each commit
        trends = []
        for commit in commits[:days]:  # Limit to recent commits
            coverage = commit.get("totals", {}).get("coverage")
            if coverage is not None:
                trends.append({
                    "commit": commit["commitid"],
                    "timestamp": commit["timestamp"],
                    "coverage": coverage,
                    "author": commit.get("author", {}).get("username"),
                })

        return trends

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.client.close()
```

### Analytics Engine

```python
# src/nhl_scrabble/analytics/analyzer.py
from dataclasses import dataclass
from typing import Any


@dataclass
class CoverageGap:
    """Represents a module with insufficient coverage."""

    module: str
    current_coverage: float
    target_coverage: float
    lines_needed: int
    priority: str  # "high", "medium", "low"


@dataclass
class TestPerformance:
    """Test performance metrics."""

    test_name: str
    avg_duration: float
    max_duration: float
    min_duration: float
    failure_rate: float
    flakiness_score: float  # 0-1, higher = more flaky


class TestAnalyzer:
    """Analyzes test and coverage data."""

    def __init__(self, codecov_data: dict[str, Any]):
        self.data = codecov_data

    def find_coverage_gaps(
        self,
        target_coverage: float = 90.0,
    ) -> list[CoverageGap]:
        """Identify modules below target coverage."""
        gaps = []
        files = self.data.get("files", [])

        for file_data in files:
            coverage = file_data.get("totals", {}).get("coverage", 0)
            if coverage < target_coverage:
                total_lines = file_data.get("totals", {}).get("lines", 0)
                covered_lines = file_data.get("totals", {}).get("hits", 0)
                needed = int((total_lines * target_coverage / 100) - covered_lines)

                # Prioritize based on how far below target
                gap_size = target_coverage - coverage
                if gap_size > 30:
                    priority = "high"
                elif gap_size > 15:
                    priority = "medium"
                else:
                    priority = "low"

                gaps.append(CoverageGap(
                    module=file_data["name"],
                    current_coverage=coverage,
                    target_coverage=target_coverage,
                    lines_needed=needed,
                    priority=priority,
                ))

        return sorted(gaps, key=lambda g: g.current_coverage)

    def analyze_test_performance(self) -> list[TestPerformance]:
        """Analyze test execution performance."""
        test_data = self.data.get("test_analytics", {}).get("tests", [])

        performances = []
        for test in test_data:
            performances.append(TestPerformance(
                test_name=test["name"],
                avg_duration=test.get("avg_duration", 0),
                max_duration=test.get("max_duration", 0),
                min_duration=test.get("min_duration", 0),
                failure_rate=test.get("failure_rate", 0),
                flakiness_score=self._calculate_flakiness(test),
            ))

        return sorted(performances, key=lambda p: p.avg_duration, reverse=True)

    def _calculate_flakiness(self, test: dict[str, Any]) -> float:
        """Calculate flakiness score (0-1) based on pass/fail patterns."""
        # Higher variance in outcomes = more flaky
        pass_rate = 1 - test.get("failure_rate", 0)
        # If pass rate is near 50%, it's very flaky
        # If it's near 0% or 100%, it's consistent (not flaky)
        flakiness = 1 - abs(pass_rate - 0.5) * 2
        return round(flakiness, 3)

    def get_coverage_trend(
        self,
        trends: list[dict[str, Any]],
    ) -> str:
        """Determine if coverage is improving, declining, or stable."""
        if len(trends) < 2:
            return "insufficient_data"

        recent_avg = sum(t["coverage"] for t in trends[:7]) / min(7, len(trends[:7]))
        older_avg = sum(t["coverage"] for t in trends[7:14]) / min(7, len(trends[7:14]))

        diff = recent_avg - older_avg
        if diff > 1.0:
            return "improving"
        elif diff < -1.0:
            return "declining"
        else:
            return "stable"
```

### CLI Integration

```python
# src/nhl_scrabble/cli.py (add new command)

@main.command()
@click.option("--format", type=click.Choice(["text", "json", "html"]), default="text")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--target-coverage", default=90.0, help="Target coverage percentage")
@click.option("--show-gaps", is_flag=True, help="Show coverage gaps")
@click.option("--show-slow-tests", is_flag=True, help="Show slowest tests")
@click.option("--show-flaky-tests", is_flag=True, help="Show flaky tests")
@click.option("--show-trends", is_flag=True, help="Show coverage trends")
@click.pass_context
def test_analytics(
    ctx: click.Context,
    format: str,
    output: str | None,
    target_coverage: float,
    show_gaps: bool,
    show_slow_tests: bool,
    show_flaky_tests: bool,
    show_trends: bool,
) -> None:
    """Analyze test analytics and coverage data from Codecov.

    Requires CODECOV_TOKEN environment variable for API access.

    Examples:
        # Show all analytics
        nhl-scrabble test-analytics

        # Show only coverage gaps
        nhl-scrabble test-analytics --show-gaps --target-coverage 95

        # Show slow tests
        nhl-scrabble test-analytics --show-slow-tests

        # Export to JSON
        nhl-scrabble test-analytics --format json -o analytics.json
    """
    from nhl_scrabble.analytics.codecov_client import CodecovClient, CodecovConfig
    from nhl_scrabble.analytics.analyzer import TestAnalyzer

    config = CodecovConfig.from_env()
    if not config.token:
        click.secho(
            "Error: CODECOV_TOKEN environment variable not set",
            fg="red",
            err=True,
        )
        ctx.exit(1)

    # Fetch data
    with CodecovClient(config) as client:
        analytics_data = client.get_test_analytics()
        coverage_data = client.get_coverage_report()
        trends_data = client.get_coverage_trends()

    # Analyze
    analyzer = TestAnalyzer({**analytics_data, **coverage_data})

    # Generate report
    report_data = {}

    if show_gaps or not any([show_slow_tests, show_flaky_tests, show_trends]):
        report_data["coverage_gaps"] = analyzer.find_coverage_gaps(target_coverage)

    if show_slow_tests or not any([show_gaps, show_flaky_tests, show_trends]):
        performances = analyzer.analyze_test_performance()
        report_data["slow_tests"] = performances[:10]  # Top 10 slowest

    if show_flaky_tests:
        performances = analyzer.analyze_test_performance()
        flaky = [p for p in performances if p.flakiness_score > 0.3]
        report_data["flaky_tests"] = flaky[:10]

    if show_trends or not any([show_gaps, show_slow_tests, show_flaky_tests]):
        report_data["coverage_trend"] = analyzer.get_coverage_trend(trends_data)
        report_data["coverage_history"] = trends_data[:30]

    # Format and output
    if format == "json":
        import json
        output_text = json.dumps(report_data, indent=2, default=str)
    elif format == "html":
        from nhl_scrabble.analytics.formatters import HTMLFormatter
        formatter = HTMLFormatter()
        output_text = formatter.format(report_data)
    else:
        from nhl_scrabble.analytics.formatters import TextFormatter
        formatter = TextFormatter()
        output_text = formatter.format(report_data)

    if output:
        Path(output).write_text(output_text)
        click.secho(f"Analytics report saved to {output}", fg="green")
    else:
        click.echo(output_text)
```

### Text Formatter

```python
# src/nhl_scrabble/analytics/formatters.py
from typing import Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel


class TextFormatter:
    """Format analytics data as text."""

    def __init__(self):
        self.console = Console()

    def format(self, data: dict[str, Any]) -> str:
        """Format analytics data as rich text."""
        output = []

        # Coverage gaps
        if "coverage_gaps" in data:
            output.append(self._format_coverage_gaps(data["coverage_gaps"]))

        # Slow tests
        if "slow_tests" in data:
            output.append(self._format_slow_tests(data["slow_tests"]))

        # Flaky tests
        if "flaky_tests" in data:
            output.append(self._format_flaky_tests(data["flaky_tests"]))

        # Trends
        if "coverage_trend" in data:
            output.append(self._format_trends(
                data["coverage_trend"],
                data.get("coverage_history", []),
            ))

        return "\n\n".join(output)

    def _format_coverage_gaps(self, gaps: list) -> str:
        """Format coverage gaps table."""
        table = Table(title="Coverage Gaps")
        table.add_column("Module", style="cyan")
        table.add_column("Current", justify="right")
        table.add_column("Target", justify="right")
        table.add_column("Lines Needed", justify="right")
        table.add_column("Priority", style="bold")

        for gap in gaps[:20]:  # Show top 20
            priority_color = {
                "high": "red",
                "medium": "yellow",
                "low": "green",
            }.get(gap.priority, "white")

            table.add_row(
                gap.module,
                f"{gap.current_coverage:.1f}%",
                f"{gap.target_coverage:.1f}%",
                str(gap.lines_needed),
                f"[{priority_color}]{gap.priority.upper()}[/{priority_color}]",
            )

        # Use console to render to string
        with self.console.capture() as capture:
            self.console.print(table)

        return capture.get()

    def _format_slow_tests(self, tests: list) -> str:
        """Format slow tests table."""
        table = Table(title="Slowest Tests")
        table.add_column("Test", style="cyan")
        table.add_column("Avg Duration", justify="right")
        table.add_column("Max Duration", justify="right")
        table.add_column("Failure Rate", justify="right")

        for test in tests:
            table.add_row(
                test.test_name,
                f"{test.avg_duration:.2f}s",
                f"{test.max_duration:.2f}s",
                f"{test.failure_rate * 100:.1f}%",
            )

        with self.console.capture() as capture:
            self.console.print(table)

        return capture.get()

    def _format_flaky_tests(self, tests: list) -> str:
        """Format flaky tests table."""
        table = Table(title="Flaky Tests")
        table.add_column("Test", style="cyan")
        table.add_column("Flakiness Score", justify="right")
        table.add_column("Failure Rate", justify="right")

        for test in tests:
            table.add_row(
                test.test_name,
                f"{test.flakiness_score:.3f}",
                f"{test.failure_rate * 100:.1f}%",
            )

        with self.console.capture() as capture:
            self.console.print(table)

        return capture.get()

    def _format_trends(self, trend: str, history: list) -> str:
        """Format coverage trend."""
        trend_emoji = {
            "improving": "📈",
            "declining": "📉",
            "stable": "➡️",
            "insufficient_data": "❓",
        }.get(trend, "")

        current = history[0]["coverage"] if history else 0
        oldest = history[-1]["coverage"] if len(history) > 1 else 0
        change = current - oldest

        text = f"{trend_emoji} Coverage Trend: {trend.upper()}\n"
        text += f"Current: {current:.1f}%\n"
        text += f"Change (30 days): {change:+.1f}%"

        panel = Panel(text, title="Coverage Trends", border_style="blue")

        with self.console.capture() as capture:
            self.console.print(panel)

        return capture.get()
```

## Implementation Steps

1. **Setup Analytics Module Structure**
   - Create `src/nhl_scrabble/analytics/` directory
   - Add `__init__.py`, `codecov_client.py`, `analyzer.py`, `formatters.py`

2. **Implement Codecov API Client**
   - Create `CodecovConfig` with environment-based configuration
   - Implement `CodecovClient` with API methods
   - Add proper error handling and authentication
   - Test API connectivity

3. **Implement Analytics Engine**
   - Create data models (`CoverageGap`, `TestPerformance`)
   - Implement `TestAnalyzer` with analysis methods
   - Add coverage gap detection
   - Add test performance analysis
   - Add flakiness detection

4. **Implement Formatters**
   - Create `TextFormatter` with Rich tables
   - Create `JSONFormatter` for programmatic access
   - Create `HTMLFormatter` for web display

5. **Add CLI Command**
   - Integrate `test-analytics` command into main CLI
   - Add all command options and flags
   - Add comprehensive help text and examples

6. **Add Dependencies**
   - Ensure `httpx` is in dependencies (already present)
   - Ensure `rich` is in dependencies (already present)
   - Add to pyproject.toml if needed

7. **Documentation**
   - Add CLI reference documentation
   - Add how-to guide for using test analytics
   - Document Codecov API integration
   - Add environment variable documentation

## Testing Strategy

### Unit Tests

```python
# tests/unit/test_codecov_client.py
import pytest
from unittest.mock import Mock, patch
from nhl_scrabble.analytics.codecov_client import CodecovClient, CodecovConfig


def test_codecov_config_from_env(monkeypatch):
    """Test loading config from environment."""
    monkeypatch.setenv("CODECOV_TOKEN", "test-token-123")
    config = CodecovConfig.from_env()
    assert config.token == "test-token-123"


@pytest.fixture
def mock_codecov_response():
    """Mock Codecov API response."""
    return {
        "test_analytics": {
            "tests": [
                {
                    "name": "test_example",
                    "avg_duration": 1.5,
                    "max_duration": 2.0,
                    "min_duration": 1.0,
                    "failure_rate": 0.1,
                }
            ]
        },
        "files": [
            {
                "name": "src/example.py",
                "totals": {
                    "coverage": 75.0,
                    "lines": 100,
                    "hits": 75,
                }
            }
        ],
    }


def test_get_test_analytics(mock_codecov_response):
    """Test fetching test analytics."""
    with patch("httpx.Client") as mock_client:
        mock_response = Mock()
        mock_response.json.return_value = mock_codecov_response
        mock_client.return_value.get.return_value = mock_response

        config = CodecovConfig(token="test-token")
        with CodecovClient(config) as client:
            data = client.get_test_analytics()

        assert "test_analytics" in data
        assert len(data["test_analytics"]["tests"]) == 1


# tests/unit/test_analyzer.py
def test_find_coverage_gaps():
    """Test finding coverage gaps."""
    data = {
        "files": [
            {
                "name": "low_coverage.py",
                "totals": {"coverage": 50.0, "lines": 100, "hits": 50},
            },
            {
                "name": "high_coverage.py",
                "totals": {"coverage": 95.0, "lines": 100, "hits": 95},
            },
        ]
    }

    analyzer = TestAnalyzer(data)
    gaps = analyzer.find_coverage_gaps(target_coverage=90.0)

    assert len(gaps) == 1
    assert gaps[0].module == "low_coverage.py"
    assert gaps[0].current_coverage == 50.0
    assert gaps[0].priority == "high"


def test_analyze_test_performance():
    """Test test performance analysis."""
    data = {
        "test_analytics": {
            "tests": [
                {
                    "name": "slow_test",
                    "avg_duration": 10.0,
                    "max_duration": 15.0,
                    "min_duration": 8.0,
                    "failure_rate": 0.05,
                }
            ]
        }
    }

    analyzer = TestAnalyzer(data)
    performances = analyzer.analyze_test_performance()

    assert len(performances) == 1
    assert performances[0].test_name == "slow_test"
    assert performances[0].avg_duration == 10.0
```

### Integration Tests

```python
# tests/integration/test_test_analytics_command.py
import pytest
from click.testing import CliRunner
from nhl_scrabble.cli import main


@pytest.mark.skipif(
    not os.getenv("CODECOV_TOKEN"),
    reason="Requires CODECOV_TOKEN environment variable",
)
def test_test_analytics_command():
    """Test test-analytics CLI command (integration)."""
    runner = CliRunner()
    result = runner.invoke(main, ["test-analytics", "--show-gaps"])

    assert result.exit_code == 0
    assert "Coverage Gaps" in result.output


def test_test_analytics_without_token():
    """Test error handling when CODECOV_TOKEN is missing."""
    runner = CliRunner()
    result = runner.invoke(main, ["test-analytics"], env={"CODECOV_TOKEN": ""})

    assert result.exit_code == 1
    assert "CODECOV_TOKEN environment variable not set" in result.output
```

### Manual Testing

1. **Setup**:
   ```bash
   export CODECOV_TOKEN="your-codecov-token"
   ```

2. **Test Commands**:
   ```bash
   # Show all analytics
   nhl-scrabble test-analytics

   # Show only coverage gaps
   nhl-scrabble test-analytics --show-gaps --target-coverage 95

   # Show slow tests
   nhl-scrabble test-analytics --show-slow-tests

   # Show flaky tests
   nhl-scrabble test-analytics --show-flaky-tests

   # Show trends
   nhl-scrabble test-analytics --show-trends

   # Export to JSON
   nhl-scrabble test-analytics --format json -o analytics.json

   # Export to HTML
   nhl-scrabble test-analytics --format html -o analytics.html
   ```

3. **Verify**:
   - ✅ API connection successful
   - ✅ Data fetched correctly
   - ✅ Analysis results accurate
   - ✅ Output formatted properly
   - ✅ Files written correctly
   - ✅ Error handling works

## Acceptance Criteria

- [ ] Codecov API client implemented with authentication
- [ ] Test analytics endpoint integrated
- [ ] Coverage report endpoint integrated
- [ ] Coverage trends analysis implemented
- [ ] Coverage gap detection implemented
- [ ] Test performance analysis implemented
- [ ] Flakiness detection implemented
- [ ] Text formatter with Rich tables
- [ ] JSON formatter implemented
- [ ] HTML formatter implemented (optional)
- [ ] CLI command `test-analytics` added
- [ ] Command options working (--show-gaps, --show-slow-tests, etc.)
- [ ] Environment variable CODECOV_TOKEN supported
- [ ] Unit tests for client (>80% coverage)
- [ ] Unit tests for analyzer (>80% coverage)
- [ ] Integration tests for CLI command
- [ ] Documentation added (CLI reference, how-to guide)
- [ ] Error handling for missing token
- [ ] Error handling for API failures
- [ ] Tests pass
- [ ] Pre-commit hooks pass

## Related Files

- `src/nhl_scrabble/analytics/__init__.py` - Analytics module
- `src/nhl_scrabble/analytics/codecov_client.py` - Codecov API client
- `src/nhl_scrabble/analytics/analyzer.py` - Analytics engine
- `src/nhl_scrabble/analytics/formatters.py` - Output formatters
- `src/nhl_scrabble/cli.py` - Add test-analytics command
- `tests/unit/test_codecov_client.py` - Client tests
- `tests/unit/test_analyzer.py` - Analyzer tests
- `tests/integration/test_test_analytics_command.py` - Integration tests
- `docs/how-to/use-test-analytics.md` - Usage guide
- `docs/reference/cli.md` - CLI documentation update
- `docs/reference/environment-variables.md` - CODECOV_TOKEN documentation

## Dependencies

- **External**:
  - Codecov API access (free for public repos)
  - Codecov API token (from https://codecov.io)
  - `httpx` library (already in dependencies)
  - `rich` library (already in dependencies)

- **Internal**:
  - None (standalone feature)

- **Configuration**:
  - `CODECOV_TOKEN` environment variable

## Additional Notes

### Codecov API Endpoints

The tool will use these Codecov API v2 endpoints:

1. **Test Analytics**:
   ```
   GET /api/v2/gh/bdperkin/repos/nhl-scrabble/test-analytics/
   ```

2. **Coverage Report**:
   ```
   GET /api/v2/gh/bdperkin/repos/nhl-scrabble/report/
   GET /api/v2/gh/bdperkin/repos/nhl-scrabble/report/{commit_sha}/
   ```

3. **Commit History**:
   ```
   GET /api/v2/gh/bdperkin/repos/nhl-scrabble/commits/
   ```

### Authentication

The Codecov API requires a token for private repositories. For public repositories, some endpoints work without authentication but with rate limiting. Best practice is to always use a token.

Get a token from: https://app.codecov.io/account/gh/bdperkin/access

### Performance Considerations

- API calls should be cached (consider adding caching)
- Large datasets should be paginated
- Consider rate limiting (Codecov has API rate limits)
- Use async/await for concurrent requests (future enhancement)

### Future Enhancements

- **GitHub Actions Integration**: Add workflow to run analytics on schedule
- **Alerts**: Send notifications when coverage drops below threshold
- **Trends Visualization**: Add ASCII or image-based charts
- **Comparison**: Compare coverage between branches/PRs
- **Export Formats**: Add CSV, PDF export options
- **Interactive Mode**: Add interactive TUI for exploring data
- **Database**: Store historical data locally for faster analysis

### Security Considerations

- **Token Security**: Never commit CODECOV_TOKEN to git
- **Token Scope**: Use read-only tokens when possible
- **Token Storage**: Store in environment or secrets manager
- **API Validation**: Validate all API responses
- **Error Messages**: Don't leak token in error messages

### Alternative Approach

Instead of a CLI tool, this could also be implemented as:
1. **Web Dashboard**: FastAPI endpoint showing analytics
2. **GitHub Action**: Automated weekly analytics reports
3. **Jupyter Notebook**: Interactive analysis notebook
4. **Monitoring**: Integration with Grafana/Prometheus

The CLI tool is the simplest starting point and most aligned with the existing CLI-focused project structure.

## Implementation Notes

*To be filled during implementation:*
- Actual Codecov API response format
- Any API limitations encountered
- Performance optimizations applied
- Deviations from proposed solution
- Actual effort vs estimated
- Challenges encountered
