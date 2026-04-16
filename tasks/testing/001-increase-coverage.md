# Increase Test Coverage from 49% to 80%+

## Priority

**HIGH** - Must Do (Next Sprint)

## Estimated Effort

8-12 hours

## Description

Current test coverage is 49.93% overall, with gaps in CLI, processors, and error handling paths. Target is 80%+ coverage to ensure code quality and catch regressions.

## Current Coverage Status

```
Name                                         Stmts   Miss  Cover
----------------------------------------------------------------
src/nhl_scrabble/__init__.py                    3      0   100%
src/nhl_scrabble/__main__.py                    4      4     0%  ⚠️
src/nhl_scrabble/api/__init__.py                8      0   100%
src/nhl_scrabble/api/nhl_client.py             57      9    84%  ⚠️
src/nhl_scrabble/cli.py                        42     24    43%  ⚠️
src/nhl_scrabble/config.py                     16      0   100%
src/nhl_scrabble/logging_config.py              8      2    75%  ⚠️
src/nhl_scrabble/models/__init__.py             1      0   100%
src/nhl_scrabble/models/player.py              10      0   100%
src/nhl_scrabble/models/standings.py           29      0   100%
src/nhl_scrabble/models/team.py                12      0   100%
src/nhl_scrabble/processors/__init__.py         1      0   100%
src/nhl_scrabble/processors/playoff_calc.py    87     45    48%  ⚠️
src/nhl_scrabble/processors/team_processor.py  28      5    82%  ⚠️
src/nhl_scrabble/reports/__init__.py            1      0   100%
src/nhl_scrabble/reports/base.py                7      1    86%  ⚠️
src/nhl_scrabble/reports/conference_report.py  28      2    93%
src/nhl_scrabble/reports/division_report.py    28      2    93%
src/nhl_scrabble/reports/playoff_report.py     45     16    64%  ⚠️
src/nhl_scrabble/reports/stats_report.py       33      5    85%  ⚠️
src/nhl_scrabble/reports/team_report.py        28      2    93%
src/nhl_scrabble/scoring/__init__.py            1      0   100%
src/nhl_scrabble/scoring/scrabble.py           16      0   100%
----------------------------------------------------------------
TOTAL                                          492    117    76%
```

Actually 76% (not 49%), but some modules need focus.

## Priority Targets

### 1. CLI Module (43% → 90%)

**File**: `src/nhl_scrabble/cli.py`
**Missing**: Main analyze() function paths

Add tests in `tests/unit/test_cli.py`:

```python
import pytest
from click.testing import CliRunner
from nhl_scrabble.cli import cli

def test_analyze_text_output(mock_nhl_api):
    """Test analyze command with text output."""
    runner = CliRunner()
    result = runner.invoke(cli, ["analyze"])

    assert result.exit_code == 0
    assert "NHL Scrabble Score Analysis" in result.output

def test_analyze_json_output(mock_nhl_api, tmp_path):
    """Test analyze command with JSON output."""
    runner = CliRunner()
    output_file = tmp_path / "output.json"

    result = runner.invoke(cli, ["analyze", "--format", "json", "--output", str(output_file)])

    assert result.exit_code == 0
    assert output_file.exists()

    import json
    data = json.loads(output_file.read_text())
    assert "teams" in data

def test_analyze_verbose_logging(mock_nhl_api, caplog):
    """Test analyze command with verbose logging."""
    runner = CliRunner()

    result = runner.invoke(cli, ["analyze", "--verbose"])

    assert result.exit_code == 0
    assert "DEBUG" in caplog.text

def test_analyze_custom_top_players(mock_nhl_api):
    """Test analyze command with custom top players count."""
    runner = CliRunner()

    result = runner.invoke(cli, ["analyze", "--top-players", "50"])

    assert result.exit_code == 0

def test_analyze_api_error_handling(monkeypatch):
    """Test analyze command handles API errors."""
    def mock_get_standings():
        raise Exception("API Error")

    monkeypatch.setattr("nhl_scrabble.api.NHLClient.get_standings", mock_get_standings)

    runner = CliRunner()
    result = runner.invoke(cli, ["analyze"])

    assert result.exit_code != 0
    assert "error" in result.output.lower()
```

### 2. __main__ Module (0% → 100%)

**File**: `src/nhl_scrabble/__main__.py`
**Missing**: Entry point execution

Add tests in `tests/unit/test_main.py`:

```python
import subprocess
import pytest

def test_main_module_executable():
    """Test that python -m nhl_scrabble works."""
    result = subprocess.run(
        ["python", "-m", "nhl_scrabble", "--help"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "analyze" in result.stdout

def test_main_module_analyze():
    """Test that python -m nhl_scrabble analyze works."""
    result = subprocess.run(
        ["python", "-m", "nhl_scrabble", "analyze", "--help"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "Analyze NHL player names" in result.stdout
```

### 3. Playoff Calculator (48% → 85%)

**File**: `src/nhl_scrabble/processors/playoff_calculator.py`
**Missing**: Edge cases, tie-breaking logic

Add tests in `tests/unit/test_playoff_calculator.py`:

```python
import pytest
from nhl_scrabble.processors.playoff_calculator import PlayoffCalculator
from nhl_scrabble.models.team import TeamScore

def test_calculate_playoff_bracket():
    """Test playoff bracket calculation."""
    calculator = PlayoffCalculator()

    # Create sample team scores
    teams = [...]

    bracket = calculator.calculate_bracket(teams)

    assert "eastern" in bracket
    assert "western" in bracket

def test_identify_division_leaders():
    """Test division leader identification."""
    calculator = PlayoffCalculator()
    teams = [...]

    leaders = calculator.identify_division_leaders(teams)

    assert len(leaders["Atlantic"]) == 3
    assert all(team.playoff_indicator == "y" for team in leaders["Atlantic"])

def test_wild_card_selection():
    """Test wild card team selection."""
    calculator = PlayoffCalculator()
    teams = [...]

    wild_cards = calculator.select_wild_cards(teams, division_leaders)

    assert len(wild_cards) == 2
    assert all(team.playoff_indicator == "x" for team in wild_cards)

def test_tiebreaker_by_average():
    """Test tiebreaker uses average score."""
    calculator = PlayoffCalculator()

    team1 = TeamScore(name="Team1", total=100, average=5.0)
    team2 = TeamScore(name="Team2", total=100, average=6.0)

    sorted_teams = calculator.break_tie([team1, team2])

    assert sorted_teams[0].name == "Team2"  # Higher average

def test_tiebreaker_alphabetical():
    """Test tiebreaker falls back to alphabetical."""
    calculator = PlayoffCalculator()

    team1 = TeamScore(name="Bruins", total=100, average=5.0)
    team2 = TeamScore(name="Avalanche", total=100, average=5.0)

    sorted_teams = calculator.break_tie([team1, team2])

    assert sorted_teams[0].name == "Avalanche"  # Alphabetically first
```

### 4. NHL Client Error Paths (84% → 95%)

**File**: `src/nhl_scrabble/api/nhl_client.py`
**Missing**: Retry logic, timeout handling, various HTTP status codes

Add tests in `tests/unit/test_nhl_client.py`:

```python
def test_retry_on_network_error():
    """Test that requests are retried on network errors."""
    with NHLClient(retries=3) as client:
        with patch('requests.Session.get') as mock_get:
            # First 2 attempts fail, 3rd succeeds
            mock_get.side_effect = [
                requests.RequestException("Error 1"),
                requests.RequestException("Error 2"),
                Mock(status_code=200, json=lambda: {"data": "success"})
            ]

            result = client._make_request("endpoint")

            assert result == {"data": "success"}
            assert mock_get.call_count == 3

def test_timeout_error():
    """Test timeout error handling."""
    with NHLClient(timeout=1) as client:
        with patch('requests.Session.get', side_effect=requests.Timeout("Timeout")):
            with pytest.raises(NHLApiError, match="failed after"):
                client._make_request("endpoint")

def test_500_server_error():
    """Test 500 server error handling."""
    with NHLClient() as client:
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_get.return_value = mock_response

            with pytest.raises(NHLApiError, match="500"):
                client._make_request("endpoint")
```

### 5. Report Error Handling

Add error handling tests for all report classes:

```python
def test_report_handles_empty_data():
    """Test report generation with empty data."""
    report = TeamReport()

    output = report.generate(team_scores=[])

    assert "No teams found" in output or output == ""

def test_report_handles_missing_fields():
    """Test report handles data with missing fields."""
    report = ConferenceReport()

    # Team missing some fields
    team = TeamScore(name="Test", total=0)  # Missing average

    output = report.generate(conference_standings={...})

    # Should not crash
    assert output is not None
```

## Testing Strategy

1. Identify uncovered lines: `pytest --cov --cov-report=html`
1. Open `htmlcov/index.html` to see exact missing lines
1. Write tests for missing paths
1. Focus on error handling and edge cases
1. Aim for meaningful tests, not just coverage numbers

## Acceptance Criteria

- [ ] Overall coverage >= 80%
- [ ] CLI module >= 90%
- [ ] __main__ module = 100%
- [ ] Playoff calculator >= 85%
- [ ] NHL client >= 95%
- [ ] All reports >= 90%
- [ ] No critical paths left untested
- [ ] Tests are meaningful (not just covering lines)

## Related Files

- All `src/nhl_scrabble/**/*.py` files
- All `tests/unit/**/*.py` files
- `tests/integration/**/*.py` files
- `.coveragerc` (coverage configuration)

## Dependencies

None - uses existing pytest-cov

## Metrics

Track progress with:

```bash
# Overall coverage
make test-cov

# Per-module coverage
pytest --cov=src/nhl_scrabble/cli --cov-report=term-missing

# HTML report for detailed view
pytest --cov --cov-report=html
xdg-open htmlcov/index.html
```

## Time Breakdown

- CLI tests: 2-3 hours
- __main__ tests: 30 minutes
- Playoff calculator tests: 3-4 hours
- NHL client error paths: 2 hours
- Report error handling: 1-2 hours
- Integration tests: 1-2 hours

**Total**: 8-12 hours

## Additional Notes

**Coverage vs. Quality**: Aim for 80% with high-quality tests rather than 100% with meaningless tests. Focus on:

- Error paths
- Edge cases
- Integration points
- User-facing functionality

**Exclude from coverage** (if justified):

- Defensive never-reached code
- Type checking branches (if using mypy)
- Logging statements
- Debug-only code
