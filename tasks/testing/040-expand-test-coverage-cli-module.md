# Expand Test Coverage of CLI Module

**GitHub Issue**: #593 - https://github.com/bdperkin/nhl-scrabble/issues/593

## Priority

**HIGH** - Must Do (Next Sprint)

## Estimated Effort

24-32 hours

## Description

**CLI module (main entry point) has zero test coverage despite having extensive test files**, leaving the entire command-line interface untested. Current coverage is **0.00%**, with **~571 untested statements**:

- **cli.py**: 0.00% (571 statements untested - main CLI entry point)

**Total missing coverage**: ~571 statements in 1 critical file

**Similar to Tasks 036, 038 & 039**: Test files **already exist** (~2,621 lines of tests) but have **0% coverage**, indicating tests may be integration-only (using Click's CliRunner) without directly importing/executing the Python module, or coverage collection isn't configured properly for CLI testing.

**This is the MAIN ENTRY POINT** for the entire application - 0% coverage represents significant risk.

This represents critical gaps in quality assurance for:
- Click CLI application initialization
- Main command group configuration
- `analyze` command (main analysis workflow)
- `watch` command (monitoring mode with auto-refresh)
- `search` command (player search functionality)
- `interactive` command (REPL mode launcher)
- `test-analytics` command (test coverage analytics)
- CLI option parsing and validation
- Output path validation
- File format handling (text, JSON, Excel)
- Progress bar and UI integration
- Signal handling (SIGINT, SIGTERM)
- Error handling and user-friendly messages
- Verbose logging control
- Cache control options
- Filter options (conference, division, team)
- I18n integration in CLI
- Exit code handling

## Current State

### Existing Tests (But 0% Coverage):

**Total: ~2,621 lines of CLI tests across 10 files**

**tests/unit/test_cli_simple.py** - EXISTS (~200 lines) but 0% coverage
- Tests CLI commands via CliRunner
- May test CLI interface without importing cli.py directly

**tests/unit/test_cli_comprehensive.py** - EXISTS (~400 lines) but 0% coverage
- Comprehensive CLI command testing
- CliRunner-based integration tests

**tests/unit/test_cli_option_validation.py** - EXISTS (~350 lines) but 0% coverage
- Tests CLI option validation
- May not import cli.py module

**tests/unit/test_cli_edge_cases.py** - EXISTS (~300 lines) but 0% coverage
- Edge case testing for CLI
- Similar CliRunner pattern

**tests/unit/test_cli_short_options.py** - EXISTS (~250 lines) but 0% coverage
- Tests short option forms (-f, -o, -v, etc.)
- CliRunner pattern

**tests/unit/test_cli_i18n.py** - EXISTS (~200 lines) but 0% coverage
- Tests i18n in CLI context
- May need module-level import

**tests/integration/test_cli_analyze.py** - EXISTS (~400 lines) but 0% coverage
- Integration tests for analyze command
- End-to-end testing pattern

**tests/integration/test_cli_progress.py** - EXISTS (~250 lines) but 0% coverage
- Tests progress UI in CLI
- Integration-level testing

**tests/integration/test_cli_interactive.py** - EXISTS (~150 lines) but 0% coverage
- Tests interactive mode launcher
- Integration pattern

**tests/integration/test_cli_error_handling.py** - EXISTS (~121 lines) but 0% coverage
- Tests CLI error handling
- Integration pattern

### Coverage Breakdown:

**cli.py (571 statements, 0% coverage):**
```
Lines missing: 3-2001 (entire file except imports)
Features untested:
- CLI group initialization
- Version and help options
- validate_output_path() function
- analyze command:
  * All CLI options parsing
  * Progress bar creation
  * API client initialization
  * Team score processing
  * Playoff calculation
  * Report generation
  * Multiple output formats (text, JSON, Excel)
  * Filter application (conference, division, team)
  * Dashboard generation
  * File output handling
  * Error handling
- interactive command:
  * REPL mode launching
  * Data fetching control
  * Cache control
- search command:
  * Player search logic
  * Search results formatting
  * Output to file
  * Fuzzy matching control
- watch command:
  * Monitoring mode setup
  * Auto-refresh logic
  * Interval control
  * Signal handling (SIGINT, SIGTERM)
  * Terminal clearing
- test-analytics command:
  * Test coverage analytics
  * Codecov integration
  * Report generation
  * Output handling
- Helper functions:
  * Signal handlers
  * Output formatting
  * Error message display
```

## Proposed Solution

### Phase 0: Investigation (2-3 hours)
**Critical First Step** - Understand why existing tests have 0% coverage:
1. Review all 10 CLI test files (~2,621 lines total)
2. Identify test patterns (CliRunner vs direct imports)
3. Check coverage configuration for CLI module
4. Determine if Click's CliRunner affects coverage collection
5. Test coverage with isolated function imports
6. Document findings and root cause

### 1. Unit Tests for CLI Core

**cli.py** (571 statements):

```python
# tests/unit/test_cli_core.py (NEW)
"""Unit tests for CLI core functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner
from pathlib import Path

# CRITICAL: Import cli module directly to ensure coverage
from nhl_scrabble import cli as cli_module
from nhl_scrabble.cli import cli, validate_output_path


class TestCLIInitialization:
    """Test CLI application initialization."""

    def test_cli_group_exists(self):
        """Test CLI group is properly configured."""
        assert cli is not None
        assert hasattr(cli, 'commands')

    def test_cli_commands_registered(self):
        """Test all commands are registered."""
        assert 'analyze' in cli.commands
        assert 'watch' in cli.commands
        assert 'search' in cli.commands
        assert 'interactive' in cli.commands
        assert 'test-analytics' in cli.commands

    def test_version_option_configured(self):
        """Test version option is available."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        # Version string should be in output

    def test_help_option_configured(self):
        """Test help option is available."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Commands:' in result.output


class TestOutputPathValidation:
    """Test output path validation function."""

    def test_validate_output_path_none(self):
        """Test None output path (stdout) is valid."""
        # Should not raise
        validate_output_path(None)

    def test_validate_output_path_valid_new_file(self, tmp_path):
        """Test validation of new file in existing directory."""
        output_path = tmp_path / "output.txt"
        # Should not raise
        validate_output_path(str(output_path))

    def test_validate_output_path_valid_existing_file(self, tmp_path):
        """Test validation of existing writable file."""
        output_path = tmp_path / "output.txt"
        output_path.write_text("existing")
        # Should not raise
        validate_output_path(str(output_path))

    def test_validate_output_path_nonexistent_directory(self):
        """Test validation fails for nonexistent parent directory."""
        with pytest.raises(Exception):  # click.ClickException
            validate_output_path("/nonexistent/dir/output.txt")

    def test_validate_output_path_readonly_file(self, tmp_path):
        """Test validation fails for read-only file."""
        output_path = tmp_path / "readonly.txt"
        output_path.write_text("readonly")
        output_path.chmod(0o444)  # Read-only

        with pytest.raises(Exception):  # click.ClickException
            validate_output_path(str(output_path))


class TestAnalyzeCommand:
    """Test analyze command implementation."""

    @patch('nhl_scrabble.cli.DependencyContainer')
    @patch('nhl_scrabble.cli.ProgressManager')
    def test_analyze_command_basic(self, mock_progress, mock_container):
        """Test basic analyze command execution."""
        # Import ensures coverage
        from nhl_scrabble.cli import analyze

        # Mock dependencies
        mock_container.return_value.create_nhl_client.return_value.__enter__.return_value.fetch_standings.return_value = []

        runner = CliRunner()
        result = runner.invoke(cli, ['analyze'])

        # Should execute without error
        assert result.exit_code == 0

    @patch('nhl_scrabble.cli.DependencyContainer')
    def test_analyze_with_format_json(self, mock_container):
        """Test analyze with JSON output format."""
        mock_container.return_value.create_nhl_client.return_value.__enter__.return_value.fetch_standings.return_value = []

        runner = CliRunner()
        result = runner.invoke(cli, ['analyze', '--format', 'json'])

        assert result.exit_code == 0

    @patch('nhl_scrabble.cli.DependencyContainer')
    def test_analyze_with_format_excel(self, mock_container, tmp_path):
        """Test analyze with Excel output format."""
        output_path = tmp_path / "output.xlsx"

        runner = CliRunner()
        result = runner.invoke(cli, ['analyze', '--format', 'excel', '--output', str(output_path)])

        # Excel requires output file
        assert result.exit_code in [0, 2]  # 0=success, 2=usage error

    @patch('nhl_scrabble.cli.DependencyContainer')
    def test_analyze_with_output_file(self, mock_container, tmp_path):
        """Test analyze writing to file."""
        output_path = tmp_path / "output.txt"

        runner = CliRunner()
        result = runner.invoke(cli, ['analyze', '--output', str(output_path)])

        assert result.exit_code == 0

    @patch('nhl_scrabble.cli.DependencyContainer')
    def test_analyze_with_filters(self, mock_container):
        """Test analyze with conference/division/team filters."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            'analyze',
            '--conference', 'Eastern',
            '--division', 'Metropolitan',
            '--team', 'WSH'
        ])

        # Filters should be applied
        assert result.exit_code == 0

    @patch('nhl_scrabble.cli.DependencyContainer')
    def test_analyze_with_top_n(self, mock_container):
        """Test analyze with top N players option."""
        runner = CliRunner()
        result = runner.invoke(cli, ['analyze', '--top', '20'])

        assert result.exit_code == 0

    @patch('nhl_scrabble.cli.DependencyContainer')
    def test_analyze_verbose_mode(self, mock_container):
        """Test analyze with verbose logging."""
        runner = CliRunner()
        result = runner.invoke(cli, ['analyze', '--verbose'])

        # Verbose should enable debug logging
        assert result.exit_code == 0

    @patch('nhl_scrabble.cli.DependencyContainer')
    def test_analyze_no_cache(self, mock_container):
        """Test analyze with cache disabled."""
        runner = CliRunner()
        result = runner.invoke(cli, ['analyze', '--no-cache'])

        assert result.exit_code == 0

    @patch('nhl_scrabble.cli.DependencyContainer')
    def test_analyze_show_dashboard(self, mock_container):
        """Test analyze with dashboard option."""
        runner = CliRunner()
        result = runner.invoke(cli, ['analyze', '--show-dashboard'])

        assert result.exit_code == 0

    @patch('nhl_scrabble.cli.DependencyContainer')
    def test_analyze_api_error_handling(self, mock_container):
        """Test analyze handles API errors gracefully."""
        from nhl_scrabble.api.nhl_client import NHLApiError

        mock_container.return_value.create_nhl_client.return_value.__enter__.return_value.fetch_standings.side_effect = NHLApiError("API error")

        runner = CliRunner()
        result = runner.invoke(cli, ['analyze'])

        # Should handle error gracefully with non-zero exit
        assert result.exit_code != 0


class TestSearchCommand:
    """Test search command implementation."""

    @patch('nhl_scrabble.cli.DependencyContainer')
    @patch('nhl_scrabble.cli.PlayerSearch')
    def test_search_command_basic(self, mock_search, mock_container):
        """Test basic search command."""
        from nhl_scrabble.cli import search

        mock_search.return_value.search.return_value = []

        runner = CliRunner()
        result = runner.invoke(cli, ['search', 'Ovechkin'])

        assert result.exit_code == 0

    @patch('nhl_scrabble.cli.DependencyContainer')
    @patch('nhl_scrabble.cli.PlayerSearch')
    def test_search_with_output_file(self, mock_search, mock_container, tmp_path):
        """Test search writing to file."""
        output_path = tmp_path / "search.txt"
        mock_search.return_value.search.return_value = []

        runner = CliRunner()
        result = runner.invoke(cli, ['search', 'McDavid', '--output', str(output_path)])

        assert result.exit_code == 0

    @patch('nhl_scrabble.cli.DependencyContainer')
    @patch('nhl_scrabble.cli.PlayerSearch')
    def test_search_with_limit(self, mock_search, mock_container):
        """Test search with result limit."""
        mock_search.return_value.search.return_value = []

        runner = CliRunner()
        result = runner.invoke(cli, ['search', 'Smith', '--limit', '10'])

        assert result.exit_code == 0

    @patch('nhl_scrabble.cli.DependencyContainer')
    @patch('nhl_scrabble.cli.PlayerSearch')
    def test_search_fuzzy_matching(self, mock_search, mock_container):
        """Test search with fuzzy matching."""
        mock_search.return_value.search.return_value = []

        runner = CliRunner()
        result = runner.invoke(cli, ['search', 'Ovekin', '--fuzzy'])

        assert result.exit_code == 0


class TestWatchCommand:
    """Test watch command implementation."""

    @patch('nhl_scrabble.cli.DependencyContainer')
    @patch('nhl_scrabble.cli.time.sleep')
    def test_watch_command_basic(self, mock_sleep, mock_container):
        """Test basic watch command."""
        from nhl_scrabble.cli import watch

        # Mock to exit after first iteration
        mock_sleep.side_effect = KeyboardInterrupt()

        runner = CliRunner()
        result = runner.invoke(cli, ['watch'])

        # Should handle KeyboardInterrupt gracefully
        assert result.exit_code in [0, 130]

    @patch('nhl_scrabble.cli.DependencyContainer')
    @patch('nhl_scrabble.cli.time.sleep')
    def test_watch_with_interval(self, mock_sleep, mock_container):
        """Test watch with custom interval."""
        mock_sleep.side_effect = KeyboardInterrupt()

        runner = CliRunner()
        result = runner.invoke(cli, ['watch', '--interval', '10'])

        assert result.exit_code in [0, 130]

    @patch('nhl_scrabble.cli.DependencyContainer')
    @patch('nhl_scrabble.cli.time.sleep')
    def test_watch_signal_handling(self, mock_sleep, mock_container):
        """Test watch command handles SIGINT."""
        mock_sleep.side_effect = KeyboardInterrupt()

        runner = CliRunner()
        result = runner.invoke(cli, ['watch'])

        # Should exit cleanly on SIGINT
        assert result.exit_code in [0, 130]


class TestInteractiveCommand:
    """Test interactive command implementation."""

    @patch('nhl_scrabble.cli.InteractiveShell')
    def test_interactive_command_basic(self, mock_shell):
        """Test basic interactive command."""
        from nhl_scrabble.cli import interactive

        runner = CliRunner()
        result = runner.invoke(cli, ['interactive'])

        # Should launch interactive shell
        assert mock_shell.called

    @patch('nhl_scrabble.cli.InteractiveShell')
    def test_interactive_no_fetch(self, mock_shell):
        """Test interactive with --no-fetch."""
        runner = CliRunner()
        result = runner.invoke(cli, ['interactive', '--no-fetch'])

        assert mock_shell.called

    @patch('nhl_scrabble.cli.InteractiveShell')
    def test_interactive_no_cache(self, mock_shell):
        """Test interactive with --no-cache."""
        runner = CliRunner()
        result = runner.invoke(cli, ['interactive', '--no-cache'])

        assert mock_shell.called


class TestAnalyticsCommand:
    """Test test-analytics command implementation."""

    @patch('nhl_scrabble.cli.TestAnalyzer')
    def test_analytics_command_basic(self, mock_analyzer):
        """Test basic test-analytics command."""
        from nhl_scrabble.cli import test_analytics

        mock_analyzer.return_value.analyze.return_value = {}

        runner = CliRunner()
        result = runner.invoke(cli, ['test-analytics'])

        assert result.exit_code == 0

    @patch('nhl_scrabble.cli.TestAnalyzer')
    def test_analytics_with_output_file(self, mock_analyzer, tmp_path):
        """Test test-analytics writing to file."""
        output_path = tmp_path / "analytics.json"
        mock_analyzer.return_value.analyze.return_value = {}

        runner = CliRunner()
        result = runner.invoke(cli, ['test-analytics', '--output', str(output_path)])

        assert result.exit_code == 0


class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_invalid_command(self):
        """Test invalid command shows helpful error."""
        runner = CliRunner()
        result = runner.invoke(cli, ['invalid-command'])

        assert result.exit_code != 0

    def test_missing_required_argument(self):
        """Test missing required argument shows error."""
        runner = CliRunner()
        result = runner.invoke(cli, ['search'])  # Missing query

        assert result.exit_code != 0

    @patch('nhl_scrabble.cli.DependencyContainer')
    def test_invalid_format_option(self, mock_container):
        """Test invalid format option."""
        runner = CliRunner()
        result = runner.invoke(cli, ['analyze', '--format', 'invalid'])

        assert result.exit_code != 0


class TestCLII18n:
    """Test CLI internationalization."""

    @patch('nhl_scrabble.cli.DependencyContainer')
    def test_analyze_respects_locale(self, mock_container):
        """Test analyze uses locale settings."""
        # Test that CLI respects NHL_SCRABBLE_LANG
        # This is integration-level, may need env var setup
        pass
```

### 2. Integration Test Enhancement

Enhance existing integration tests to ensure coverage:

```python
# tests/integration/test_cli_analyze.py (ENHANCE)
# Already exists with ~400 lines
# Add imports to ensure modules are loaded for coverage

from nhl_scrabble.cli import cli, analyze  # Direct imports
import nhl_scrabble.cli as cli_module  # Module import

# Existing tests should then count toward coverage
```

### 3. Test Organization

```
tests/
├── unit/
│   ├── test_cli_core.py                   ✓ NEW (571 statements)
│   ├── test_cli_simple.py                 ✓ ENHANCE (add imports)
│   ├── test_cli_comprehensive.py          ✓ ENHANCE (add imports)
│   ├── test_cli_option_validation.py      ✓ ENHANCE (add imports)
│   ├── test_cli_edge_cases.py             ✓ ENHANCE (add imports)
│   ├── test_cli_short_options.py          ✓ ENHANCE (add imports)
│   └── test_cli_i18n.py                   ✓ ENHANCE (add imports)
└── integration/
    ├── test_cli_analyze.py                ✓ ENHANCE (add imports)
    ├── test_cli_progress.py               ✓ ENHANCE (add imports)
    ├── test_cli_interactive.py            ✓ ENHANCE (add imports)
    └── test_cli_error_handling.py         ✓ ENHANCE (add imports)
```

## Implementation Steps

1. **Phase 0: Investigation** (2-3 hours)
   - Review all 10 CLI test files (~2,621 lines total)
   - Understand why coverage is 0% despite extensive tests
   - Test Click CliRunner coverage behavior
   - Check pytest-cov configuration for CLI
   - Document findings and root cause

2. **Phase 1: CLI Core and Initialization** (4-6 hours)
   - Test CLI group and command registration
   - Test version and help options
   - Test output path validation
   - Test CLI entry point

3. **Phase 2: Analyze Command** (8-10 hours)
   - Test all analyze options and flags
   - Test output formats (text, JSON, Excel)
   - Test filters (conference, division, team)
   - Test dashboard generation
   - Test error handling
   - Test progress bar integration

4. **Phase 3: Other Commands** (4-6 hours)
   - Test search command
   - Test watch command and signal handling
   - Test interactive command launcher
   - Test test-analytics command

5. **Phase 4: Error Handling and Edge Cases** (3-4 hours)
   - Test invalid commands and options
   - Test API error handling
   - Test file I/O errors
   - Test signal handling

6. **Phase 5: Integration Test Enhancement** (2-3 hours)
   - Add module imports to existing tests
   - Verify coverage collection works
   - Run full test suite and check coverage

7. **Phase 6: Documentation** (1 hour)
   - Update test documentation
   - Document investigation findings
   - CI configuration updates

## Testing Strategy

### Unit Tests
- Test CLI components in isolation
- Mock dependencies (API client, file I/O)
- Test command logic without Click runner
- Test helper functions directly

### Integration Tests (Existing + Enhanced)
- Test full CLI execution with CliRunner
- Test command workflows end-to-end
- Verify proper integration with dependencies
- Add imports to ensure coverage

### Special Considerations
- **Click CliRunner**: May affect coverage - investigate in Phase 0
- **Signal handling**: Test SIGINT, SIGTERM gracefully
- **File I/O**: Use tmp_path fixture for file operations
- **Progress bars**: May need mocking for testing

## Acceptance Criteria

- [ ] Investigation complete - understand why tests had 0% coverage
- [ ] **cli.py** coverage: 0% → 95% (571 statements)
- [ ] All CLI commands tested (analyze, search, watch, interactive, test-analytics)
- [ ] All CLI options tested
- [ ] Output path validation tested
- [ ] Error handling tested (API errors, file errors, invalid options)
- [ ] Signal handling tested (SIGINT, SIGTERM)
- [ ] File output tested (text, JSON, Excel)
- [ ] Filter options tested
- [ ] Progress bar integration tested
- [ ] I18n integration tested
- [ ] All tests pass on all platforms
- [ ] All tests pass with Python 3.12-3.15-dev
- [ ] No test flakiness
- [ ] diff-cover shows 100% coverage
- [ ] Documentation updated with investigation findings

## Related Files

### Source Files:
- `src/nhl_scrabble/cli.py` - Main CLI entry point (571 statements)

### Test Files:
- `tests/unit/test_cli_core.py` - NEW comprehensive unit tests (571 statements)
- `tests/unit/test_cli_simple.py` - ENHANCE existing (~200 lines)
- `tests/unit/test_cli_comprehensive.py` - ENHANCE existing (~400 lines)
- `tests/unit/test_cli_option_validation.py` - ENHANCE existing (~350 lines)
- `tests/unit/test_cli_edge_cases.py` - ENHANCE existing (~300 lines)
- `tests/unit/test_cli_short_options.py` - ENHANCE existing (~250 lines)
- `tests/unit/test_cli_i18n.py` - ENHANCE existing (~200 lines)
- `tests/integration/test_cli_analyze.py` - ENHANCE existing (~400 lines)
- `tests/integration/test_cli_progress.py` - ENHANCE existing (~250 lines)
- `tests/integration/test_cli_interactive.py` - ENHANCE existing (~150 lines)
- `tests/integration/test_cli_error_handling.py` - ENHANCE existing (~121 lines)
- `tests/conftest.py` - Add CLI testing fixtures

## Dependencies

- **Independent**: Can be implemented immediately
- **Complements Tasks 033-039**: Part of comprehensive test coverage initiative
- **Investigation Required**: Similar to Tasks 036, 038 & 039 (tests exist but 0% coverage)
- **CRITICAL**: Main entry point - HIGH priority

## Additional Notes

### Why This Task is HIGH Priority

1. **Main Entry Point**: CLI is how users interact with the application
2. **User-Facing**: All user commands go through cli.py
3. **0% Coverage Risk**: Critical module with zero test coverage
4. **Large Surface Area**: 571 statements covering all commands
5. **Tests Exist**: ~2,621 lines of tests, but 0% coverage - investigation needed

### Investigation Hypotheses

**Why 0% coverage despite extensive tests?**

1. **CliRunner isolation**: Click's CliRunner may execute CLI without importing module
2. **Coverage scope**: pytest-cov may not track CLI execution through CliRunner
3. **Import patterns**: Tests may invoke CLI as subprocess, not Python import
4. **Entry point execution**: Coverage may not track Click decorators/entry points
5. **Test configuration**: CLI tests may be excluded from coverage

### Testing Patterns

```python
# Pattern 1: Unit test with direct import (ADDS COVERAGE)
from nhl_scrabble.cli import analyze, validate_output_path
def test_function():
    result = validate_output_path("/tmp/out.txt")
    # Tests function directly

# Pattern 2: CliRunner test (MAY NOT ADD COVERAGE)
from click.testing import CliRunner
def test_cli():
    runner = CliRunner()
    result = runner.invoke(cli, ['analyze'])
    # May not track module coverage
```

### Platform Compatibility

All tests must pass on:
- Linux (primary)
- macOS (signal handling differences)
- Windows (path handling, signal behavior)

### Coverage Target Rationale

**95% target** (not 100%) because:
- Signal handlers may be platform-specific
- Some error paths require specific system conditions
- Click framework internals may not be fully testable

## Implementation Notes

*To be filled during implementation:*
- Investigation findings (root cause of 0% coverage)
- Click CliRunner coverage behavior
- Coverage configuration changes needed
- Testing patterns that work for CLI
- Actual effort vs estimated
- Coverage improvements achieved

---

## Summary

This task addresses the **MAIN ENTRY POINT** of the NHL Scrabble application and is part of the **8-task comprehensive test coverage initiative**:

**Tasks 033-040 Combined**:
- ~4,317 untested statements
- 150-204 hours total effort
- Coverage target: 90.21% → 97%+
- Complete application coverage (all modules including main entry point)

**Task 040 specifically addresses**:
- CLI module (main entry point): ~571 statements at 0% coverage
- Investigation of unusual 0% coverage despite extensive tests (~2,621 lines)
- Unit and integration test coverage for all CLI commands
- **HIGH priority** due to being the main user interface
