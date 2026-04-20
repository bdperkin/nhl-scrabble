# CLI Module Test Coverage (70% → 90%)

**GitHub Issue**: #253 - https://github.com/bdperkin/nhl-scrabble/issues/253

**Parent Task**: #221 - Comprehensive Test Coverage (sub-task 1 of 8)

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

2-3 hours

## Description

Improve test coverage for `src/nhl_scrabble/cli.py` from ~70% to 90%+ by adding comprehensive tests for command-line argument parsing, option combinations, error handling, and output formats.

**Parent Task**: tasks/testing/002-comprehensive-test-coverage-90-100.md (Phase 2)

## Current State

- **Current Coverage**: ~70%
- **Untested Areas**:
  - Option combination validation
  - Error handling edge cases
  - Environment variable integration
  - Output file handling errors
  - Invalid format handling

## Proposed Solution

Add comprehensive CLI tests using Click's CliRunner:

```python
# tests/unit/test_cli.py
from click.testing import CliRunner
from nhl_scrabble.cli import cli

class TestCLI:
    def test_analyze_default_options(self):
        """Test analyze with default options."""
        runner = CliRunner()
        result = runner.invoke(cli, ['analyze'])
        assert result.exit_code == 0

    def test_analyze_json_output(self, tmp_path):
        """Test JSON format output."""
        output_file = tmp_path / "output.json"
        runner = CliRunner()
        result = runner.invoke(cli, [
            'analyze',
            '--format', 'json',
            '--output', str(output_file)
        ])
        assert result.exit_code == 0
        assert output_file.exists()

        import json
        with open(output_file) as f:
            data = json.load(f)
        assert 'teams' in data

    def test_analyze_verbose_mode(self):
        """Test verbose logging."""
        runner = CliRunner()
        result = runner.invoke(cli, ['analyze', '--verbose'])
        assert result.exit_code == 0

    def test_analyze_custom_player_counts(self):
        """Test custom player count options."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            'analyze',
            '--top-players', '50',
            '--top-team-players', '10'
        ])
        assert result.exit_code == 0

    def test_analyze_invalid_format(self):
        """Test invalid format option."""
        runner = CliRunner()
        result = runner.invoke(cli, ['analyze', '--format', 'invalid'])
        assert result.exit_code != 0
        assert "Invalid value for '--format'" in result.output

    def test_version_command(self):
        """Test version command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert "2.0.0" in result.output

    def test_help_command(self):
        """Test help command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "analyze" in result.output

    def test_output_file_permission_error(self, tmp_path):
        """Test output file write permission error."""
        # Create read-only file
        output_file = tmp_path / "readonly.json"
        output_file.touch()
        output_file.chmod(0o444)

        runner = CliRunner()
        result = runner.invoke(cli, [
            'analyze',
            '--output', str(output_file)
        ])
        assert result.exit_code != 0
```

## Implementation Steps

1. **Add Core Command Tests** (1h)
1. **Add Option Combination Tests** (30 min)
1. **Add Error Handling Tests** (30 min)
1. **Add Edge Case Tests** (30 min)
1. **Verify Coverage Improvement** (30 min)

## Acceptance Criteria

- [ ] CLI coverage improved from 70% to 90%+
- [ ] All command options tested
- [ ] Error handling tested
- [ ] Output formats tested
- [ ] Environment variables tested
- [ ] All tests passing
- [ ] Coverage report shows improvement

## Dependencies

- **Parent**: #221

## Implementation Notes

*To be filled during implementation*
