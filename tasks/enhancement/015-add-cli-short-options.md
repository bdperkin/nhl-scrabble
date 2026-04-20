# Add Standard Short Options to CLI Commands

**GitHub Issue**: #229 - https://github.com/bdperkin/nhl-scrabble/issues/229

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

30-60 minutes

## Description

Add standard short options (`-V`, `-h`) alongside existing long options (`--version`, `--help`) for all CLI commands. This improves user experience by following common CLI conventions and reducing typing required for frequently-used options.

## Current State

**Existing CLI (Click-based):**

The project uses Click for CLI implementation with only long options:

```python
# src/nhl_scrabble/cli.py
import click

@click.group()
@click.version_option(version=__version__)
def cli():
    """NHL Scrabble Score Analyzer."""
    pass

@cli.command()
@click.option("--format", type=click.Choice(["text", "json"]), default="text")
@click.option("--output", "-o", type=click.Path(), help="Output file")  # Has short option!
@click.option("--verbose", is_flag=True, help="Enable verbose logging")  # No short option
@click.option("--top-players", type=int, default=20)  # No short option
def analyze(format, output, verbose, top_players):
    """Analyze NHL teams and calculate Scrabble scores."""
    # Implementation
```

**Current Help Output:**

```bash
$ nhl-scrabble --help
Usage: nhl-scrabble [OPTIONS] COMMAND [ARGS]...

  NHL Scrabble Score Analyzer.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  analyze  Analyze NHL teams and calculate Scrabble scores.
```

**Analyze Command:**

```bash
$ nhl-scrabble analyze --help
Usage: nhl-scrabble analyze [OPTIONS]

Options:
  --format [text|json]  Output format  [default: text]
  -o, --output PATH     Output file
  --verbose             Enable verbose logging
  --top-players INTEGER Number of top players  [default: 20]
  --help                Show this message and exit.
```

**Issues:**

1. **Inconsistent**: `--version` has no `-V` short option
1. **Inconsistent**: `--help` has no `-h` short option (Click provides it by default, but not shown in some contexts)
1. **Inconsistent**: `--verbose` has no `-v` short option
1. **Partial Coverage**: Only `--output` has short option (`-o`)
1. **User Experience**: Users expect standard POSIX short options

## Proposed Solution

### Standard Short Options

Add short options following common CLI conventions:

**Universal Options:**

- `--version` → `-V` (capital V to match conventions like `gcc -V`, `python -V`)
- `--help` → `-h` (lowercase h is universal standard)

**Common Command Options:**

- `--verbose` → `-v` (standard for verbose mode)
- `--format` → `-f` (common for format selection)
- `--output` → `-o` (already implemented ✓)

**Updated CLI Code:**

```python
# src/nhl_scrabble/cli.py
import click
from nhl_scrabble import __version__

@click.group()
@click.version_option(version=__version__, prog_name="nhl-scrabble")
@click.help_option("-h", "--help")  # Add explicit -h
def cli():
    """NHL Scrabble Score Analyzer.

    Calculate Scrabble scores for NHL player names and generate
    comprehensive team standings reports.
    """
    pass

@cli.command()
@click.option(
    "-f", "--format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
@click.option(
    "-o", "--output",
    type=click.Path(),
    help="Output file path",
)
@click.option(
    "-v", "--verbose",
    is_flag=True,
    help="Enable verbose logging",
)
@click.option(
    "--top-players",
    type=int,
    default=20,
    help="Number of top players to display",
)
@click.option(
    "--top-team-players",
    type=int,
    default=5,
    help="Number of top players per team to display",
)
@click.help_option("-h", "--help")  # Add explicit -h for command
def analyze(format, output, verbose, top_players, top_team_players):
    """Analyze NHL teams and calculate Scrabble scores.

    Fetches current NHL roster data and calculates Scrabble scores
    for player names. Generates comprehensive reports including team
    standings, division standings, conference standings, and playoff
    brackets.

    Examples:

        # Basic usage (text output to stdout)
        nhl-scrabble analyze

        # JSON output to file
        nhl-scrabble analyze -f json -o report.json

        # Verbose mode
        nhl-scrabble analyze -v

        # Custom display limits
        nhl-scrabble analyze --top-players 50 --top-team-players 10
    """
    # Implementation remains the same
    pass
```

### Short Option Conventions

**Follow POSIX/GNU Standards:**

| Long Option      | Short Option | Justification                      |
| ---------------- | ------------ | ---------------------------------- |
| `--help`         | `-h`         | Universal standard                 |
| `--version`      | `-V`         | Common (capital to avoid conflict) |
| `--verbose`      | `-v`         | Standard verbose flag              |
| `--format`       | `-f`         | Common format selector             |
| `--output`       | `-o`         | Already implemented ✓              |
| `--top-players`  | (none)       | Too specific for short option      |
| `--top-team-...` | (none)       | Too specific for short option      |

**Guidelines:**

- ✅ Add short options for **common, frequently-used** options
- ✅ Use **lowercase** for regular options (`-v`, `-f`, `-o`)
- ✅ Use **capital** for special options (`-V` for version)
- ❌ Don't add short options for **infrequently-used** options
- ❌ Don't add short options for **domain-specific** options

### Updated Help Output

**After Implementation:**

```bash
$ nhl-scrabble --help
Usage: nhl-scrabble [OPTIONS] COMMAND [ARGS]...

  NHL Scrabble Score Analyzer.

Options:
  -V, --version  Show the version and exit.
  -h, --help     Show this message and exit.

Commands:
  analyze  Analyze NHL teams and calculate Scrabble scores.
```

```bash
$ nhl-scrabble analyze --help
Usage: nhl-scrabble analyze [OPTIONS]

  Analyze NHL teams and calculate Scrabble scores.

Options:
  -f, --format [text|json]      Output format  [default: text]
  -o, --output PATH             Output file path
  -v, --verbose                 Enable verbose logging
  --top-players INTEGER         Number of top players  [default: 20]
  --top-team-players INTEGER    Number of top players per team  [default: 5]
  -h, --help                    Show this message and exit.
```

### Usage Examples

**Before (long options only):**

```bash
nhl-scrabble --version
nhl-scrabble analyze --format json --output report.json --verbose
```

**After (short options available):**

```bash
nhl-scrabble -V
nhl-scrabble analyze -f json -o report.json -v
```

**Both work (backwards compatible):**

```bash
# Long options still work
nhl-scrabble --version
nhl-scrabble analyze --format json

# Short options now work
nhl-scrabble -V
nhl-scrabble analyze -f json

# Mix and match
nhl-scrabble analyze -f json --output report.json -v
```

## Implementation Steps

1. **Update CLI Main Group** (5 min)

   - Add `-h` to `@click.help_option()` decorator
   - Verify `@click.version_option()` includes version info
   - Test: `nhl-scrabble -h`, `nhl-scrabble -V`

1. **Update Analyze Command** (10 min)

   - Add `-f` to `--format` option
   - Add `-v` to `--verbose` option
   - Verify `-o` for `--output` (already exists)
   - Add `-h` to command-level `@click.help_option()`
   - Keep `--top-players` and `--top-team-players` without short options

1. **Test Short Options** (10 min)

   - Test `-V` / `--version`
   - Test `-h` / `--help`
   - Test `analyze -h`
   - Test `analyze -f json`
   - Test `analyze -v`
   - Test `analyze -o file.json`
   - Test combinations: `analyze -f json -o file.json -v`
   - Verify backwards compatibility with long options

1. **Update Documentation** (15 min)

   - Update `docs/reference/cli.md` with short options
   - Update README.md examples
   - Update help docstrings if needed
   - Update tutorials with short option examples

1. **Update Tests** (10 min)

   - Add tests for short options in test suite
   - Test `-V` returns version
   - Test `-h` shows help
   - Test `analyze -f`, `-v`, `-o` work correctly
   - Ensure existing long option tests still pass

## Testing Strategy

### Manual Testing

```bash
# Test version short option
nhl-scrabble -V
# Expected: nhl-scrabble, version 2.0.0

# Test version long option (backwards compatibility)
nhl-scrabble --version
# Expected: nhl-scrabble, version 2.0.0

# Test help short option (main)
nhl-scrabble -h
# Expected: Full help text

# Test help short option (command)
nhl-scrabble analyze -h
# Expected: Analyze command help

# Test format short option
nhl-scrabble analyze -f json
# Expected: JSON output

# Test verbose short option
nhl-scrabble analyze -v
# Expected: Verbose logging enabled

# Test output short option (already exists)
nhl-scrabble analyze -o test.txt
# Expected: Output written to test.txt

# Test combination
nhl-scrabble analyze -f json -o report.json -v
# Expected: Verbose JSON output to file

# Test backwards compatibility
nhl-scrabble analyze --format json --output report.json --verbose
# Expected: Same as above

# Test mixed options
nhl-scrabble analyze -f json --output report.json -v
# Expected: Works correctly
```

### Automated Testing

```python
# tests/unit/test_cli.py
import pytest
from click.testing import CliRunner
from nhl_scrabble.cli import cli

def test_version_short_option():
    """Test -V shows version."""
    runner = CliRunner()
    result = runner.invoke(cli, ["-V"])
    assert result.exit_code == 0
    assert "2.0.0" in result.output

def test_version_long_option():
    """Test --version shows version (backwards compatibility)."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "2.0.0" in result.output

def test_help_short_option():
    """Test -h shows help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["-h"])
    assert result.exit_code == 0
    assert "NHL Scrabble Score Analyzer" in result.output

def test_analyze_format_short_option():
    """Test analyze -f works."""
    runner = CliRunner()
    result = runner.invoke(cli, ["analyze", "-f", "json"])
    # Verify JSON output format

def test_analyze_verbose_short_option():
    """Test analyze -v works."""
    runner = CliRunner()
    result = runner.invoke(cli, ["analyze", "-v"])
    # Verify verbose logging enabled

def test_analyze_output_short_option():
    """Test analyze -o works."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["analyze", "-o", "test.txt"])
        assert Path("test.txt").exists()

def test_analyze_combined_short_options():
    """Test multiple short options together."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            ["analyze", "-f", "json", "-o", "report.json", "-v"]
        )
        assert result.exit_code == 0
        assert Path("report.json").exists()

def test_backwards_compatibility():
    """Test long options still work."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            ["analyze", "--format", "json", "--output", "report.json", "--verbose"]
        )
        assert result.exit_code == 0
        assert Path("report.json").exists()
```

## Acceptance Criteria

- [ ] `-V` shows version (same as `--version`)
- [ ] `-h` shows help at main level (same as `--help`)
- [ ] `analyze -h` shows analyze command help
- [ ] `analyze -f [text|json]` works (same as `--format`)
- [ ] `analyze -v` enables verbose mode (same as `--verbose`)
- [ ] `analyze -o PATH` works (already implemented, verify unchanged)
- [ ] All short options work in combination
- [ ] Long options still work (backwards compatibility)
- [ ] Mixed short and long options work
- [ ] Help text shows both short and long options
- [ ] Tests pass for all short options
- [ ] Documentation updated with short option examples
- [ ] CLI reference documentation updated
- [ ] README examples updated to use short options

## Related Files

**Modified Files:**

- `src/nhl_scrabble/cli.py` - Add short option decorators
- `tests/unit/test_cli.py` - Add short option tests
- `docs/reference/cli.md` - Update CLI reference documentation
- `README.md` - Update examples with short options
- `docs/tutorials/01-getting-started.md` - Add short option examples

**No New Files** - Pure enhancement to existing CLI

## Dependencies

**No External Dependencies** - Click already supports short options

**No Task Dependencies** - Standalone enhancement

## Additional Notes

### Click Short Option Support

Click natively supports short options via tuple syntax:

```python
# Method 1: Tuple (recommended)
@click.option("-v", "--verbose", is_flag=True)

# Method 2: Multiple decorators (also works)
@click.option("-v", is_flag=True)
@click.option("--verbose", is_flag=True)
```

**Best Practice**: Use tuple method for consistency.

### Standard Short Option Conventions

**Common Patterns:**

| Short | Long          | Usage                    |
| ----- | ------------- | ------------------------ |
| `-h`  | `--help`      | Show help (universal)    |
| `-V`  | `--version`   | Show version (capital V) |
| `-v`  | `--verbose`   | Verbose output           |
| `-q`  | `--quiet`     | Quiet output             |
| `-f`  | `--format`    | Output format            |
| `-o`  | `--output`    | Output file              |
| `-i`  | `--input`     | Input file               |
| `-c`  | `--config`    | Configuration file       |
| `-d`  | `--debug`     | Debug mode               |
| `-n`  | `--dry-run`   | Dry run (no changes)     |
| `-y`  | `--yes`       | Auto-confirm             |
| `-a`  | `--all`       | All items                |
| `-r`  | `--recursive` | Recursive operation      |
| `-l`  | `--list`      | List items               |
| `-t`  | `--test`      | Test mode                |
| `-p`  | `--port`      | Port number              |
| `-u`  | `--user`      | Username                 |
| `-w`  | `--watch`     | Watch mode               |
| `-s`  | `--silent`    | Silent mode              |
| `-e`  | `--exclude`   | Exclude pattern          |

**NHL Scrabble Usage:**

- `-V` / `--version` ✓
- `-h` / `--help` ✓
- `-v` / `--verbose` ✓
- `-f` / `--format` ✓
- `-o` / `--output` ✓ (already exists)

### Short Option Conflicts

**Avoid Conflicts:**

```python
# BAD: Conflicting -v
@click.option("-v", "--verbose", is_flag=True)
@click.option("-v", "--validate", is_flag=True)  # ❌ Conflict!

# GOOD: Use different short options
@click.option("-v", "--verbose", is_flag=True)
@click.option("--validate", is_flag=True)  # ✓ No short option
```

**Current NHL Scrabble:**

- `-V`: `--version` (capital V)
- `-v`: `--verbose` (lowercase v)
- `-f`: `--format`
- `-o`: `--output`
- `-h`: `--help`

No conflicts! ✓

### Backwards Compatibility

**Guaranteed:**

- All existing long options continue to work
- Existing scripts using long options unaffected
- New short options are **additions**, not replacements

**Migration Path:**

```python
# Old scripts (still work)
nhl-scrabble analyze --format json --output report.json --verbose

# New scripts (can use)
nhl-scrabble analyze -f json -o report.json -v

# Mixed (also works)
nhl-scrabble analyze -f json --output report.json -v
```

### User Experience Benefits

**Reduced Typing:**

```bash
# Before: 64 characters
nhl-scrabble analyze --format json --output report.json --verbose

# After: 46 characters (28% less typing)
nhl-scrabble analyze -f json -o report.json -v

# For version check: 50% less typing
nhl-scrabble --version  # 24 chars
nhl-scrabble -V         # 15 chars
```

**Faster Workflow:**

```bash
# Quick version check
nhl-scrabble -V

# Quick help
nhl-scrabble -h
nhl-scrabble analyze -h

# Rapid development iterations
nhl-scrabble analyze -f json -o test.json -v
```

**Muscle Memory:**

Users familiar with standard UNIX tools expect:

- `-h` for help (git, docker, npm, etc.)
- `-V` or `-v` for version
- `-v` for verbose
- `-f` for format
- `-o` for output

**Matching these conventions = better UX!**

### Documentation Updates

**README.md Examples:**

````markdown
## Quick Start

```bash
# Run analyzer
nhl-scrabble analyze

# With short options
nhl-scrabble analyze -f json -o report.json -v

# Show version
nhl-scrabble -V

# Show help
nhl-scrabble -h
nhl-scrabble analyze -h
````

````

**CLI Reference:**

```markdown
## Global Options

- `-V`, `--version` - Show version and exit
- `-h`, `--help` - Show help message and exit

## Analyze Command Options

- `-f`, `--format [text|json]` - Output format (default: text)
- `-o`, `--output PATH` - Output file path
- `-v`, `--verbose` - Enable verbose logging
- `--top-players INTEGER` - Number of top players to display (default: 20)
- `--top-team-players INTEGER` - Number of players per team (default: 5)
- `-h`, `--help` - Show command help and exit
````

### Testing Coverage

**Test Matrix:**

| Option              | Short | Long        | Combined   | Mixed            |
| ------------------- | ----- | ----------- | ---------- | ---------------- |
| Version             | `-V`  | `--version` | N/A        | N/A              |
| Help (main)         | `-h`  | `--help`    | N/A        | N/A              |
| Help (analyze)      | `-h`  | `--help`    | N/A        | N/A              |
| Format              | `-f`  | `--format`  | `-f -o`    | `-f --output`    |
| Output              | `-o`  | `--output`  | `-o -v`    | `-o --verbose`   |
| Verbose             | `-v`  | `--verbose` | `-v -f`    | `-v --format`    |
| All analyze options | N/A   | N/A         | `-f -o -v` | `-f --output -v` |

**Coverage: 100%** - All combinations tested

### Breaking Changes

**None** - This is purely additive:

- No existing functionality removed
- All long options still work
- New short options are optional
- Backwards compatible with all scripts
- No configuration changes required

### Performance Impact

**None** - Short options have identical performance to long options. Click parses both the same way internally.

### Accessibility Considerations

**Benefits:**

- Easier for power users (less typing)
- Standard conventions (familiar to UNIX users)
- Better for scripts (shorter, more readable)
- Improved documentation (both forms shown)

**Maintained:**

- Long options remain for clarity
- Help text shows both forms
- Tutorials can use either
- User can choose preference

### Future Enhancements

After initial implementation, consider:

- **Shell Completion**: Add completion for short options
- **Aliases**: Consider additional common aliases
- **Grouped Options**: Short options that can be combined (`-vf` = `-v -f`)
- **Man Pages**: Generate man page with short options documented

### Comparison with Other Tools

**Git:**

```bash
git --version     # Long
git -v            # Short (lowercase)
```

**Docker:**

```bash
docker --version  # Long
docker -v         # Short (lowercase)
```

**NPM:**

```bash
npm --version     # Long
npm -v            # Short (lowercase)
```

**Python:**

```bash
python --version  # Long
python -V         # Short (capital V) ← We'll use this!
```

**NHL Scrabble (after this task):**

```bash
nhl-scrabble --version  # Long
nhl-scrabble -V         # Short (capital V, matches Python)
```

### Migration Notes

**For Users:**

- No action required - long options still work
- Start using short options when convenient
- Mix and match as preferred

**For Documentation:**

- Update all examples to show both forms
- Prefer short options in "quick start" examples
- Use long options in "detailed" examples for clarity

**For Scripts:**

- No changes needed to existing scripts
- New scripts can use short options
- Consider using short options for brevity

### Success Metrics

**Quantitative:**

- [ ] 100% backwards compatibility (all tests pass)
- [ ] 100% short option coverage for common options
- [ ] 0 breaking changes introduced

**Qualitative:**

- [ ] User feedback positive
- [ ] Documentation clear and complete
- [ ] Follows industry standards
- [ ] Improves developer experience
