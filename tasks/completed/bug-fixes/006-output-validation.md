# Validate CLI Output Paths

**GitHub Issue**: #49 - https://github.com/bdperkin/nhl-scrabble/issues/49

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

1-2 hours

## Description

The CLI `--output` option does not validate that the output path is writable before fetching data from the API. This can result in wasted API calls if the output path is invalid or not writable.

## Current State

```python
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="Output file path (default: stdout)",
)
def analyze(
    format: str,
    output: str | None,
    verbose: bool,
    top_players: int,
    top_team_players: int,
) -> None:
    """Analyze NHL player names by Scrabble score."""
    # ... fetch all data ...

    # Only at the end do we try to write
    if output:
        try:
            with open(output, "w") as f:
                f.write(final_output)
        except IOError as e:
            logger.error(f"Failed to write to {output}: {e}")
            sys.exit(1)
```

**Issue**: If output path is invalid, we discover this AFTER fetching all NHL data (~30 seconds of API calls).

## Proposed Solution

Validate output path early, before any API calls:

```python
import os


def validate_output_path(output: str | None) -> None:
    """Validate that output path is writable.

    Args:
        output: Output file path, or None for stdout

    Raises:
        click.ClickException: If output path is not writable
    """
    if output is None:
        return  # stdout is always writable

    # Resolve to absolute path
    output_path = os.path.abspath(output)
    output_dir = os.path.dirname(output_path)

    # Check if directory exists
    if not os.path.exists(output_dir):
        raise click.ClickException(
            f"Output directory does not exist: {output_dir}\n"
            f"Create it first: mkdir -p {output_dir}"
        )

    # Check if directory is writable
    if not os.access(output_dir, os.W_OK):
        raise click.ClickException(
            f"Output directory is not writable: {output_dir}\n"
            f"Check permissions with: ls -ld {output_dir}"
        )

    # Check if file exists and is writable
    if os.path.exists(output_path):
        if not os.access(output_path, os.W_OK):
            raise click.ClickException(
                f"Output file exists but is not writable: {output_path}\n"
                f"Check permissions with: ls -l {output_path}"
            )

        # Warn if file will be overwritten
        logger.warning(f"Output file exists and will be overwritten: {output_path}")


@click.command()
@click.option(
    "-o", "--output", type=click.Path(), help="Output file path (default: stdout)"
)
def analyze(
    format: str,
    output: str | None,
    verbose: bool,
    top_players: int,
    top_team_players: int,
) -> None:
    """Analyze NHL player names by Scrabble score."""
    # Validate output path BEFORE fetching data
    validate_output_path(output)

    # ... fetch all data ...

    # Write output (now guaranteed to work)
    if output:
        with open(output, "w") as f:
            f.write(final_output)
    else:
        click.echo(final_output)
```

Alternative: Use Click's built-in path validation:

```python
@click.option(
    "-o",
    "--output",
    type=click.Path(writable=True, dir_okay=False, resolve_path=True),
    help="Output file path (default: stdout)",
)
def analyze(output: str | None, ...):
    """Analyze NHL player names by Scrabble score."""
    # Click already validated that output is writable
    # ...
```

**However**, Click's validation only works for existing files. For new files, it validates the parent directory.

## Testing Strategy

Add tests in `tests/integration/test_cli.py`:

```python
import os
import pytest
import tempfile
from click.testing import CliRunner
from nhl_scrabble.cli import cli


def test_output_to_nonexistent_directory():
    """Test that output to nonexistent directory fails early."""
    runner = CliRunner()

    result = runner.invoke(cli, ["analyze", "--output", "/nonexistent/dir/output.txt"])

    assert result.exit_code != 0
    assert "directory does not exist" in result.output.lower()


def test_output_to_readonly_directory(tmp_path):
    """Test that output to read-only directory fails early."""
    runner = CliRunner()

    # Create read-only directory
    readonly_dir = tmp_path / "readonly"
    readonly_dir.mkdir()
    readonly_dir.chmod(0o444)

    output_path = readonly_dir / "output.txt"

    result = runner.invoke(cli, ["analyze", "--output", str(output_path)])

    assert result.exit_code != 0
    assert "not writable" in result.output.lower()

    # Cleanup
    readonly_dir.chmod(0o755)


def test_output_to_readonly_file(tmp_path):
    """Test that output to read-only file fails early."""
    runner = CliRunner()

    # Create read-only file
    readonly_file = tmp_path / "readonly.txt"
    readonly_file.write_text("existing content")
    readonly_file.chmod(0o444)

    result = runner.invoke(cli, ["analyze", "--output", str(readonly_file)])

    assert result.exit_code != 0
    assert "not writable" in result.output.lower()

    # Cleanup
    readonly_file.chmod(0o644)


def test_output_overwrites_existing_file(tmp_path, caplog):
    """Test that output to existing file shows warning."""
    runner = CliRunner()

    # Create existing file
    existing_file = tmp_path / "existing.txt"
    existing_file.write_text("old content")

    result = runner.invoke(cli, ["analyze", "--output", str(existing_file)])

    # Should succeed but with warning
    assert result.exit_code == 0
    assert "will be overwritten" in caplog.text.lower()

    # File should be overwritten
    new_content = existing_file.read_text()
    assert "old content" not in new_content


def test_output_to_valid_path(tmp_path):
    """Test that output to valid path works."""
    runner = CliRunner()

    output_file = tmp_path / "output.txt"

    result = runner.invoke(cli, ["analyze", "--output", str(output_file)])

    assert result.exit_code == 0
    assert output_file.exists()
    assert output_file.stat().st_size > 0


def test_validation_happens_before_api_calls(monkeypatch):
    """Test that validation happens before making API calls."""
    runner = CliRunner()

    api_called = False

    def mock_get_standings():
        nonlocal api_called
        api_called = True
        return {"standings": []}

    monkeypatch.setattr("nhl_scrabble.api.NHLClient.get_standings", mock_get_standings)

    # Invalid output path
    result = runner.invoke(cli, ["analyze", "--output", "/nonexistent/dir/output.txt"])

    # Should fail without calling API
    assert result.exit_code != 0
    assert not api_called
```

## Acceptance Criteria

- [x] Output path validated before API calls
- [x] Nonexistent directories are detected and reported
- [x] Read-only directories are detected and reported
- [x] Read-only files are detected and reported
- [x] Existing files show warning before overwrite
- [x] Error messages include helpful hints for fixing the issue
- [x] Unit tests verify all validation cases
- [x] Integration tests verify API is not called for invalid paths

## Related Files

- `src/nhl_scrabble/cli.py`
- `tests/integration/test_cli.py`

## Dependencies

None - uses Python stdlib `os` module

## User Experience Impact

**Before**:

```bash
$ nhl-scrabble analyze --output /readonly/output.txt
Fetching NHL standings...
Fetching team rosters... (30+ API calls, ~30 seconds)
Error: Cannot write to /readonly/output.txt
```

**After**:

```bash
$ nhl-scrabble analyze --output /readonly/output.txt
Error: Output directory is not writable: /readonly
Check permissions with: ls -ld /readonly
```

Immediate feedback saves time and frustration.

## Additional Notes

Consider adding a `--force` flag to skip the overwrite warning for automation:

```python
@click.option("--force", is_flag=True, help="Overwrite output file without warning")
def analyze(output: str | None, force: bool, ...):
    if output and os.path.exists(output) and not force:
        if not click.confirm(f"Overwrite {output}?"):
            raise click.Abort()
```

## Implementation Notes

**Implemented**: 2026-04-16
**Branch**: bug-fixes/006-output-validation
**PR**: #79 - https://github.com/bdperkin/nhl-scrabble/pull/79
**Commits**: 1 commit (1d7c718)

### Actual Implementation

Followed the proposed solution closely with some refinements for modern Python practices:

- Used `Path` API instead of `os.path` methods (Path.resolve(), Path.parent, Path.exists())
- Kept `os.access()` for permission checks (no Path equivalent)
- Created `validate_output_path()` function exactly as specified
- Called validation after logging setup but before API calls
- All error messages include helpful hints with exact commands

**Validation flow:**

1. Early return if output is None (stdout)
1. Resolve path to absolute Path object
1. Check parent directory exists → error with `mkdir -p` hint
1. Check parent directory writable → error with `ls -ld` hint
1. If file exists, check writable → error with `ls -l` hint
1. If file exists, log overwrite warning

### Challenges Encountered

**Pre-commit Hooks:**

- Initial implementation used `os.path` methods
- Ruff PTH100/PTH110/PTH120 rules flagged to use Path API instead
- Refactored to use modern Path methods for better code quality
- Had to keep `os.access()` as Path has no equivalent

**Test Mocking:**

- Initial test for overwrite warning used `caplog` fixture
- Click runner doesn't propagate logs to caplog
- Fixed by mocking `logger.warning` directly and asserting on call

**Path Usage:**

- Needed to use `Path.cwd()` instead of `os.getcwd()` per ruff PTH109
- Balanced between Path API and os module appropriately

### Deviations from Plan

**Enhancements:**

- Used modern Path API instead of os.path (better practices)
- Created dedicated test file `test_cli_output_validation.py` instead of adding to `test_cli.py`
- Added extra test for relative path handling
- Added test for nested nonexistent directories
- Added test for attempting to write to directory instead of file

**No deviations from core functionality** - all specified features implemented exactly as designed.

### Actual vs Estimated Effort

- **Estimated**: 1-2 hours
- **Actual**: ~1.5 hours (middle of range)
- **Breakdown**:
  - Implementation: 20 minutes
  - Testing: 40 minutes (11 comprehensive tests)
  - Pre-commit fixes (Path refactoring): 15 minutes
  - PR and CI: 15 minutes

**On target!** - Implementation was straightforward as the task spec was very detailed.

### Test Coverage

**New Tests**: 11 integration tests in `test_cli_output_validation.py`

- `test_output_to_stdout` - Verify no validation for stdout
- `test_output_to_nonexistent_directory` - Directory doesn't exist
- `test_output_to_readonly_directory` - Directory not writable
- `test_output_to_readonly_file` - File not writable
- `test_output_overwrites_existing_file` - Warning logged
- `test_output_to_valid_path` - Success case
- `test_validation_happens_before_api_calls` - Key requirement verified
- `test_output_to_new_file_in_existing_directory` - Common case
- `test_output_with_relative_path` - Path resolution
- `test_output_with_nested_new_directories_fails` - Deep paths fail early
- `test_output_to_directory_instead_of_file` - Edge case handled

**Coverage**: 92.64% overall (+2.51pp from 90.13%)

- cli.py: 92.54% coverage (validation paths fully tested)
- All 131 tests passing (120 existing + 11 new)

### Lessons Learned

**Path API:**

- Modern Python prefers Path API over os.path methods
- Path.resolve() replaces os.path.abspath()
- Path.parent replaces os.path.dirname()
- Path.exists() replaces os.path.exists()
- Still need os.access() for permission checks (no Path equivalent)

**Early Validation:**

- Validating paths before expensive operations is good UX
- Users appreciate immediate feedback with actionable errors
- Error messages should always include fix commands
- Warning users about overwrite is polite but not blocking

**Testing:**

- Click runner testing requires careful fixture mocking
- Permission tests need cleanup (chmod back to writable)
- Test isolation important for file permission tests
- Mock validation keeps tests fast (no actual API calls)

**Code Quality:**

- 55 pre-commit hooks catch issues early
- Ruff's path rules enforce modern Python practices
- Automated formatting saves time (black, ruff-format)
- Type checking with mypy prevents bugs

### Related PRs

- PR #79: Output path validation (merged)

### User Impact

**Before**: Users would wait 30+ seconds for API calls only to discover output path was invalid.

**After**: Immediate feedback (\<1ms) with clear error messages and fix commands.

Example error messages:

```
Error: Output directory does not exist: /nonexistent/dir
Create it first: mkdir -p /nonexistent/dir

Error: Output directory is not writable: /readonly
Check permissions with: ls -ld /readonly

Error: Output file exists but is not writable: /readonly/file.txt
Check permissions with: ls -l /readonly/file.txt
```

**Result**: Better UX, time saved, clearer error messages.
