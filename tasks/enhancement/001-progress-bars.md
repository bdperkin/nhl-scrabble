# Add Progress Bars for Long Operations

**GitHub Issue**: #132 - https://github.com/bdperkin/nhl-scrabble/issues/132

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

2-3 hours

## Description

Add visual progress bars using the rich library to provide real-time feedback during long operations like API fetching, score calculation, and report generation.

Currently the application provides no progress indication during operations that can take 10+ seconds, leaving users unsure if the application is working or frozen. This creates a poor user experience and increases perceived wait time.

**Impact**: Improved user experience, reduced perceived wait time, better visibility into application state, professional appearance

**Operations to visualize**:

- API fetching (30 teams × 0.3s minimum = 9+ seconds)
- Score calculation (100+ players per team = 3000+ calculations)
- Report generation (multiple report types)

## Current State

**No progress indication**:

```python
# src/nhl_scrabble/cli.py
def analyze(...):
    """Analyze NHL Scrabble scores - no progress shown."""

    # Fetch standings (instant)
    standings = client.get_standings()

    # Fetch rosters - takes 9+ seconds, no progress
    for team in standings:
        roster = client.get_team_roster(team.abbrev)
        # User sees nothing while this runs

    # Calculate scores - takes time, no progress
    for team in teams:
        for player in team.players:
            score = calculate_score(player.name)
            # User sees nothing

    # Generate reports - no progress
    report = generate_reports(teams)
    # User sees nothing

    print(report)  # Only output after everything completes
```

**Problems**:

1. **Long waits with no feedback**:

   - API fetching: 9-15 seconds (depending on network)
   - Score calculation: 1-3 seconds
   - Total wait: 10-18 seconds with no indication

1. **Appears frozen**:

   - Terminal shows no activity
   - Users may think app crashed
   - May kill process thinking it's stuck

1. **No time estimates**:

   - Users don't know how long to wait
   - Can't plan whether to wait or do something else

1. **No operation visibility**:

   - Users don't know what operation is running
   - Can't identify slow operations
   - No debugging info for performance issues

## Proposed Solution

Implement rich progress bars with multi-level tracking:

**Step 1: Add rich dependency** (already present):

```toml
# pyproject.toml - already has rich for HTML report
dependencies = [
    "rich>=13.7.0",
    # ... other dependencies
]
```

**Step 2: Create progress manager module**:

```python
# src/nhl_scrabble/ui/progress.py
"""Progress bar management for NHL Scrabble."""

from contextlib import contextmanager
from typing import Optional
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
    MofNCompleteColumn,
    TextColumn,
)

class ProgressManager:
    """
    Manage progress bars for NHL Scrabble operations.

    Provides context managers for different operation types.
    """

    def __init__(self, enabled: bool = True):
        """
        Initialize progress manager.

        Args:
            enabled: Whether to show progress bars (disable for --quiet)
        """
        self.enabled = enabled
        self._progress: Optional[Progress] = None

    @contextmanager
    def create_progress(self):
        """Create rich Progress instance with custom columns."""
        if not self.enabled:
            yield None
            return

        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            TimeRemainingColumn(),
            TextColumn("[cyan]{task.fields[status]}"),
        )

        try:
            progress.start()
            self._progress = progress
            yield progress
        finally:
            progress.stop()
            self._progress = None

    @contextmanager
    def track_api_fetching(self, total_teams: int):
        """
        Track API fetching progress.

        Args:
            total_teams: Total number of teams to fetch

        Yields:
            Function to update progress after each team
        """
        with self.create_progress() as progress:
            if progress is None:
                yield lambda team: None
                return

            task = progress.add_task(
                "Fetching team rosters",
                total=total_teams,
                status=""
            )

            def update(team_abbrev: str):
                """Update progress after fetching a team."""
                progress.update(task, advance=1, status=f"[green]{team_abbrev}")

            yield update

    @contextmanager
    def track_score_calculation(self, total_players: int):
        """
        Track score calculation progress.

        Args:
            total_players: Total number of players to score

        Yields:
            Function to update progress after each player
        """
        with self.create_progress() as progress:
            if progress is None:
                yield lambda: None
                return

            task = progress.add_task(
                "Calculating Scrabble scores",
                total=total_players,
                status=""
            )

            def update():
                """Update progress after scoring a player."""
                progress.update(task, advance=1)

            yield update

    @contextmanager
    def track_report_generation(self, total_reports: int):
        """
        Track report generation progress.

        Args:
            total_reports: Total number of reports to generate

        Yields:
            Function to update progress after each report
        """
        with self.create_progress() as progress:
            if progress is None:
                yield lambda name: None
                return

            task = progress.add_task(
                "Generating reports",
                total=total_reports,
                status=""
            )

            def update(report_name: str):
                """Update progress after generating a report."""
                progress.update(
                    task, advance=1, status=f"[yellow]{report_name}"
                )

            yield update
```

**Step 3: Integrate into CLI**:

```python
# src/nhl_scrabble/cli.py
from nhl_scrabble.ui.progress import ProgressManager

@click.option("--quiet", "-q", is_flag=True, help="Suppress progress bars")
def analyze(
    quiet: bool = False,
    # ... other options
):
    """Analyze NHL Scrabble scores with progress tracking."""

    # Create progress manager
    progress_mgr = ProgressManager(enabled=not quiet)

    # Fetch standings (instant, no progress needed)
    standings = client.get_standings()
    teams = list(standings.teams)

    # Fetch rosters with progress
    with progress_mgr.track_api_fetching(len(teams)) as update_progress:
        team_scores = []
        for team in teams:
            roster = client.get_team_roster(team.abbrev)
            team_scores.append(process_roster(roster))
            update_progress(team.abbrev)  # Update progress bar

    # Calculate scores with progress
    total_players = sum(len(team.players) for team in team_scores)
    with progress_mgr.track_score_calculation(total_players) as update_progress:
        for team in team_scores:
            for player in team.players:
                player.score = calculate_score(player.name)
                update_progress()  # Update progress bar

    # Generate reports with progress
    report_types = ["team", "division", "conference", "playoff", "stats"]
    with progress_mgr.track_report_generation(len(report_types)) as update_progress:
        reports = []
        for report_type in report_types:
            report = generate_report(report_type, team_scores)
            reports.append(report)
            update_progress(report_type)  # Update progress bar

    # Output results
    for report in reports:
        click.echo(report)
```

**Step 4: Add overall progress wrapper** (optional):

```python
# src/nhl_scrabble/ui/progress.py
@contextmanager
def track_overall_analysis(self, num_teams: int):
    """
    Track overall analysis progress with sub-tasks.

    Shows main progress bar with current operation.

    Args:
        num_teams: Number of teams being analyzed

    Yields:
        Dict of progress update functions
    """
    with self.create_progress() as progress:
        if progress is None:
            yield {
                "api": lambda t: None,
                "score": lambda: None,
                "report": lambda r: None,
            }
            return

        # Main task (overall progress)
        main_task = progress.add_task(
            "NHL Scrabble Analysis",
            total=3,  # 3 main phases
            status="Starting..."
        )

        # Sub-task for current operation
        sub_task = progress.add_task(
            "",
            total=100,
            status="",
            visible=False
        )

        def start_api_phase():
            progress.update(main_task, status="Fetching team rosters...")
            progress.update(sub_task, total=num_teams, completed=0, visible=True)

        def update_api(team: str):
            progress.update(sub_task, advance=1, status=f"[green]{team}")

        def complete_api_phase():
            progress.update(main_task, advance=1)
            progress.update(sub_task, visible=False)

        # Similar for other phases...

        yield {
            "start_api": start_api_phase,
            "update_api": update_api,
            "complete_api": complete_api_phase,
            # ... other phase methods
        }
```

## Implementation Steps

1. **Create UI module**:

   - Create `src/nhl_scrabble/ui/` directory
   - Create `src/nhl_scrabble/ui/__init__.py`
   - Create `src/nhl_scrabble/ui/progress.py`

1. **Implement ProgressManager**:

   - Implement `create_progress()` context manager
   - Implement `track_api_fetching()` context manager
   - Implement `track_score_calculation()` context manager
   - Implement `track_report_generation()` context manager

1. **Integrate into CLI**:

   - Add `--quiet` flag to disable progress
   - Create ProgressManager instance
   - Wrap API fetching with progress tracking
   - Wrap score calculation with progress tracking
   - Wrap report generation with progress tracking

1. **Add tests**:

   - Unit tests for ProgressManager
   - Test with progress enabled and disabled
   - Integration tests for CLI with progress
   - Test --quiet flag

1. **Update documentation**:

   - Document --quiet flag in CLI help
   - Add screenshots to README
   - Document progress bar feature

## Testing Strategy

**Unit tests** (`tests/unit/test_progress.py`):

```python
import pytest
from unittest.mock import Mock, patch
from nhl_scrabble.ui.progress import ProgressManager

def test_progress_manager_disabled():
    """Test progress manager when disabled."""
    mgr = ProgressManager(enabled=False)

    with mgr.track_api_fetching(30) as update:
        # Should work but do nothing
        update("TOR")
        update("MTL")

    # No errors, progress not shown

def test_progress_manager_enabled():
    """Test progress manager when enabled."""
    mgr = ProgressManager(enabled=True)

    with patch('nhl_scrabble.ui.progress.Progress') as MockProgress:
        mock_progress = MockProgress.return_value
        mock_task = Mock()
        mock_progress.add_task.return_value = mock_task

        with mgr.track_api_fetching(30) as update:
            update("TOR")
            update("MTL")

        # Verify progress updated
        assert mock_progress.update.call_count == 2

def test_api_fetching_progress():
    """Test API fetching progress tracking."""
    mgr = ProgressManager(enabled=True)

    teams_fetched = []

    with mgr.track_api_fetching(3) as update:
        for team in ["TOR", "MTL", "BOS"]:
            teams_fetched.append(team)
            update(team)

    assert len(teams_fetched) == 3
```

**Integration tests** (`tests/integration/test_cli_progress.py`):

```python
from click.testing import CliRunner
from nhl_scrabble.cli import cli

def test_cli_shows_progress():
    """Test CLI shows progress bars."""
    runner = CliRunner()
    result = runner.invoke(cli, ["analyze"])

    # Should show progress-related output
    assert "Fetching team rosters" in result.output or result.exit_code == 0

def test_cli_quiet_mode():
    """Test CLI --quiet suppresses progress."""
    runner = CliRunner()
    result = runner.invoke(cli, ["analyze", "--quiet"])

    # Should not show progress bars
    assert "Fetching team rosters" not in result.output or result.exit_code == 0
```

**Manual testing**:

```bash
# Test with progress (default)
nhl-scrabble analyze
# Should show progress bars for each phase

# Test quiet mode
nhl-scrabble analyze --quiet
# Should show no progress bars

# Test with verbose (progress + extra info)
nhl-scrabble analyze --verbose
# Should show progress AND verbose logging
```

## Acceptance Criteria

- [ ] `ui/progress.py` module created
- [ ] `ProgressManager` class implemented
- [ ] `create_progress()` context manager works
- [ ] `track_api_fetching()` tracks team fetching
- [ ] `track_score_calculation()` tracks scoring
- [ ] `track_report_generation()` tracks reports
- [ ] Progress bars show percentage complete
- [ ] Progress bars show items completed (M of N)
- [ ] Progress bars show time remaining (ETA)
- [ ] Progress bars show current item being processed
- [ ] Spinner animation works while processing
- [ ] --quiet flag added to CLI
- [ ] --quiet flag disables progress bars
- [ ] Progress still works with --verbose
- [ ] Progress bars don't interfere with output
- [ ] Unit tests achieve 100% coverage of progress module
- [ ] Integration tests verify CLI progress
- [ ] All tests pass
- [ ] Documentation updated with --quiet flag
- [ ] README includes progress bar screenshot/example
- [ ] No regressions in existing functionality

## Related Files

- `src/nhl_scrabble/ui/__init__.py` - New UI module
- `src/nhl_scrabble/ui/progress.py` - New progress manager
- `src/nhl_scrabble/cli.py` - Integrate progress tracking
- `tests/unit/test_progress.py` - Progress unit tests
- `tests/integration/test_cli_progress.py` - CLI integration tests
- `README.md` - Document progress feature
- `docs/tutorials/01-getting-started.md` - Show progress in examples

## Dependencies

**Python packages**:

- `rich>=13.7.0` - Already in dependencies for HTML report

**Related tasks**:

- Could enhance: `enhancement/002-interactive-mode.md` (progress in REPL)
- Works with: Existing API client and scoring logic

**No blocking dependencies** - Can be implemented immediately

## Additional Notes

**Rich Progress Features Used**:

- `SpinnerColumn` - Animated spinner while processing
- `BarColumn` - Visual progress bar
- `TaskProgressColumn` - Percentage complete
- `MofNCompleteColumn` - "15/30" format
- `TimeRemainingColumn` - Estimated time remaining
- `TextColumn` - Custom status text (current item)

**Example Output**:

```
⠋ Fetching team rosters ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 50% 15/30 0:00:05 TOR
⠹ Calculating Scrabble scores ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 75% 2250/3000 0:00:02
⠼ Generating reports ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 60% 3/5 0:00:01 playoff
```

**Performance Considerations**:

- Progress updates are fast (\<1ms each)
- Rich uses efficient terminal control codes
- No noticeable performance impact
- Actually improves perceived performance

**Quiet Mode Use Cases**:

- Scripting/automation (don't want progress in logs)
- CI/CD pipelines (prefer plain text output)
- Piping output to files
- Screen readers (progress bars not accessible)

**Accessibility**:

Progress bars are visual-only. For accessibility:

- --quiet mode provides clean text output
- Verbose mode provides text-based progress logs
- Consider adding --accessible flag for text-only progress

**Future Enhancements**:

Could add:

- Overall progress bar with sub-tasks
- Speed metrics (teams/sec, players/sec)
- Progress bar customization (style, colors)
- Progress logging to file for debugging
- Nested progress bars for complex operations

**Trade-offs**:

- **Pro**: Much better UX, professional appearance
- **Pro**: Helps identify slow operations
- **Con**: Slightly more complex code
- **Con**: Not accessible for screen readers (mitigated by --quiet)

**Breaking Changes**: None - only adds --quiet flag, doesn't change defaults

## Implementation Notes

*To be filled during implementation:*

- Rich library features used
- Performance impact measured
- User feedback on progress bars
- Any issues with terminal compatibility
- Deviations from proposed solution
- Actual effort vs estimated
