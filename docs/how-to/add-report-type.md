# How to Add a New Report Type

Create custom report generators for NHL Scrabble.

## Problem

You want to add a new type of report (e.g., player comparison report, historical trends, custom statistics) to the NHL Scrabble analyzer.

## Solution

Follow these steps to create and integrate a new report type.

### Step 1: Create report class

Create a new file in `src/nhl_scrabble/reports/`:

```python
# src/nhl_scrabble/reports/your_report.py
from nhl_scrabble.reports.base import BaseReport


class YourReport(BaseReport):
    """Your custom report generator.

    Detailed description of what this report shows.
    """

    def generate(self, data) -> str:
        """Generate the report.

        Args:
            data: Input data for the report.

        Returns:
            Formatted report string.
        """
        # Build your report
        sections = []
        sections.append(self._header("Your Report Title"))
        sections.append(self._format_data(data))
        sections.append(self._footer())

        return "\n".join(sections)

    def _format_data(self, data) -> str:
        """Format the main data section."""
        lines = []
        # Your formatting logic here
        return "\n".join(lines)
```

### Step 2: Add tests

Create test file `tests/unit/test_your_report.py`:

```python
import pytest
from nhl_scrabble.reports.your_report import YourReport


def test_your_report_generation():
    """Test report generates correctly."""
    reporter = YourReport()

    # Prepare test data
    test_data = {...}

    # Generate report
    result = reporter.generate(test_data)

    # Verify output
    assert "Your Report Title" in result
    assert len(result) > 0


def test_your_report_empty_data():
    """Test report handles empty data."""
    reporter = YourReport()
    result = reporter.generate([])

    assert "No data" in result or result == ""
```

### Step 3: Register report in CLI

Update `src/nhl_scrabble/cli.py` to include your report:

```python
from nhl_scrabble.reports.your_report import YourReport

def run_analysis(config: Config) -> str:
    # ... existing code ...

    # Initialize your reporter
    your_reporter = YourReport()

    # Generate reports
    reports = [
        conference_reporter.generate(conference_standings),
        division_reporter.generate(division_standings),
        your_reporter.generate(your_data),  # Add your report
        # ... other reports ...
    ]

    return "\n".join(reports)
```

### Step 4: Run tests

```bash
# Run your new tests
pytest tests/unit/test_your_report.py -v

# Run all tests
pytest

# Check coverage
pytest --cov=src/nhl_scrabble/reports/your_report.py
```

### Step 5: Update documentation

Add entry to docs:

- Document in [Python API Reference](../reference/code-api.md)
- Add example to tutorials if appropriate
- Update [Architecture Explanation](../explanation/architecture.md) if significant

## Example: Player Comparison Report

Here's a complete example for comparing two players:

```python
# src/nhl_scrabble/reports/player_comparison.py
from nhl_scrabble.models import PlayerScore
from nhl_scrabble.reports.base import BaseReport


class PlayerComparisonReport(BaseReport):
    """Compare Scrabble scores of multiple players."""

    def generate(self, players: list[PlayerScore]) -> str:
        """Generate player comparison report."""
        if not players:
            return "No players to compare."

        sections = []
        sections.append(self._header("Player Comparison"))
        sections.append(self._compare_players(players))

        return "\n".join(sections)

    def _compare_players(self, players: list[PlayerScore]) -> str:
        """Format player comparison table."""
        lines = []
        lines.append(f"{'Player':<30} {'First':<10} {'Last':<10} {'Total':<10}")
        lines.append("-" * 60)

        for player in sorted(players, key=lambda p: p.total, reverse=True):
            lines.append(
                f"{player.full_name:<30} "
                f"{player.first_name_score:<10} "
                f"{player.last_name_score:<10} "
                f"{player.total:<10}"
            )

        return "\n".join(lines)
```

## Troubleshooting

### Issue: Import errors

**Solution**: Ensure your file is in the correct location and __init__.py exists.

### Issue: Tests fail

**Solution**: Check test data structure matches your report's expectations.

### Issue: Report not showing

**Solution**: Verify you registered it in run_analysis() in cli.py.

## Related

- [Base Report API](../reference/code-api.md#reports) - BaseReport class documentation
- [Report Architecture](../explanation/report-system.md) - Understanding the report system
- [Testing Guide](run-tests.md) - How to test your report
