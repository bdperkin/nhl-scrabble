# CLI Option Standards

This document establishes standards for command-line interface options across all NHL Scrabble commands. Following these standards ensures consistency, maintainability, and a better user experience.

## Naming Conventions

### Option Names

- **Use kebab-case** for all option names

  - ✅ `--top-players`, `--output-format`, `--no-cache`
  - ❌ `--topPlayers`, `--output_format`, `--nocache`

- **Use descriptive names** - avoid abbreviations unless very common

  - ✅ `--verbose`, `--output`, `--config` (common abbreviations)
  - ❌ `--num-results` (use `--limit` or `--max-results`)

- **Use plural for multi-value options**

  - ✅ `--teams TOR,MTL,BOS` (accepts multiple teams)
  - ✅ `--divisions Atlantic,Metropolitan` (accepts multiple divisions)

- **Use singular for single-value options**

  - ✅ `--team TOR` (accepts one team)
  - ✅ `--division Atlantic` (accepts one division)

**Note**: For consistency across commands, we prefer **plural** even for single-value options when the same concept appears in multiple commands with different cardinalities.

### Examples

```bash
# Good - Consistent plural usage
nhl-scrabble analyze --divisions Atlantic
nhl-scrabble search --divisions Atlantic
nhl-scrabble dashboard --divisions Atlantic

# Bad - Inconsistent singular/plural
nhl-scrabble analyze --divisions Atlantic
nhl-scrabble search --division Atlantic  # Different from analyze!
```

## Short Options

### Reserved Global Short Options

These short options are **reserved** and must be consistent across ALL commands:

- `-o` - `--output` (output file path)
- `-v` - `--verbose` (enable verbose logging)
- `-q` - `--quiet` (suppress progress/output)
- `-h` - `--help` (show help message)

### Command-Specific Short Options

For command-specific options:

- **Limit to 5 short options per command** (prevents clutter)
- **Only for frequently used options** (not every option needs a short form)
- **Avoid similar single letters** (don't use `-d` for both `--debug` and `--division`)

### Examples

```python
# Good - Clear, frequently used
@click.option("--fuzzy", "-f")       # Primary feature of search command
@click.option("--limit", "-n")       # Very common Unix convention
@click.option("--team", "-t")        # Common filter

# Bad - Too many short options
@click.option("--division", "-d")
@click.option("--debug", "-D")       # Too similar to -d
@click.option("--duration", "-u")    # Confusing mnemonic
```

## Help Text Format

### Standard Formats

**For flags (boolean options):**

```python
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--quiet", "-q", is_flag=True, help="Suppress progress bars and status messages")
```

**For options with defaults:**

```python
@click.option(
    "--top-players",
    type=int,
    default=20,
    help="Number of top players to show (default: 20)",
)
```

**For options with ranges:**

```python
@click.option(
    "--top-players",
    type=click.IntRange(min=1, max=100),
    default=20,
    help="Number of top players to show (default: 20, range: 1-100)",
)
```

**For required options:**

```python
@click.option(
    "--output",
    required=True,
    help="Output file path (required for CSV/Excel formats)",
)
```

**For choice options:**

```python
# Option 1: Let Click.Choice show choices automatically
@click.option(
    "--format",
    type=click.Choice(["text", "json", "csv"], case_sensitive=False),
    default="text",
    help="Output format (default: text)",
)

# Option 2: Document choices explicitly
@click.option(
    "--format",
    help="Output format: text, json, csv (default: text)",
)
```

**For complex options with examples:**

```python
@click.option(
    "--teams",
    help="""Filter by teams (comma-separated).

Examples: TOR,MTL,BOS""",
)
```

### Help Text Guidelines

1. **Be concise** - One clear sentence
1. **Document defaults** - Always show default values
1. **Document ranges** - Show valid ranges for numeric options
1. **Use active voice** - "Enable verbose logging" not "Verbose logging is enabled"
1. **Avoid redundancy** - Don't repeat the option name in the description

## Option Order

Options should appear in **logical groups** within each command function:

### Standard Order

1. **Output Options**

   - `--format` (output format choice)
   - `--output, -o` (output file path)
   - Format-specific options (e.g., `--sheets` for Excel)

1. **Behavior Flags**

   - `--verbose, -v` (verbose logging)
   - `--quiet, -q` (suppress output)

1. **Data Source Options**

   - `--no-cache` (disable caching)
   - `--clear-cache` (clear cache)
   - `--season` (season selection)

1. **Display Options**

   - `--top-players` (number of players to show)
   - `--top-team-players` (players per team)
   - `--limit` (result limit)

1. **Report Selection**

   - `--report` (specific report type)

1. **Scoring Options**

   - `--scoring` (scoring system)
   - `--scoring-config` (custom scoring config)

1. **Filtering Options**

   - `--divisions` (division filter)
   - `--conferences` (conference filter)
   - `--teams` (team filter)
   - `--exclude-teams` (excluded teams)
   - `--min-score` (minimum score)
   - `--max-score` (maximum score)

1. **Specialized Options**

   - Command-specific options (e.g., `--fuzzy` for search)

### Example

```python
@cli.command()
# === Output Options ===
@click.option("--format", ...)
@click.option("--output", "-o", ...)
@click.option("--sheets", ...)

# === Behavior Flags ===
@click.option("--verbose", "-v", ...)
@click.option("--quiet", "-q", ...)

# === Data Source Options ===
@click.option("--no-cache", ...)
@click.option("--clear-cache", ...)

# === Display Options ===
@click.option("--top-players", ...)

# === Filtering Options ===
@click.option("--divisions", ...)
@click.option("--conferences", ...)
@click.option("--teams", ...)

def analyze(...):
    """Command implementation."""
```

## Validation

Use **Click's built-in types** for validation whenever possible. This provides immediate feedback with clear error messages.

### Integer Ranges

```python
@click.option(
    "--top-players",
    type=click.IntRange(min=1, max=100),
    default=20,
    help="Number of top players to show (default: 20, range: 1-100)",
)
```

### Port Numbers

```python
@click.option(
    "--port",
    type=click.IntRange(min=1, max=65535),
    default=8000,
    help="Port to bind to (default: 8000, range: 1-65535)",
)
```

### File Paths

```python
# Existing file (input)
@click.option(
    "--config",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    help="Configuration file path",
)

# Output file
@click.option(
    "--output",
    type=click.Path(dir_okay=False, writable=True),
    help="Output file path",
)
```

### Choices (Enumerations)

```python
@click.option(
    "--format",
    type=click.Choice(["text", "json", "csv", "excel"], case_sensitive=False),
    default="text",
    help="Output format (default: text)",
)
```

### Custom Validation

For complex validation beyond Click's types:

```python
def validate_season(ctx, param, value):
    """Validate season format YYYYYYYY."""
    if value is None:
        return None

    if not re.match(r"^\d{8}$", value):
        raise click.BadParameter("Season must be 8 digits (e.g., 20222023)")

    return value


@click.option(
    "--season",
    callback=validate_season,
    help="Season to analyze (format: YYYYYYYY, e.g., 20222023)",
)
```

### Why Use Click's Validation

**Benefits:**

1. **Immediate feedback** - Errors before expensive operations
1. **Consistent error messages** - Click provides standardized error format
1. **Type safety** - Values are validated before reaching function
1. **Better UX** - Clear error messages guide users

**Example:**

```bash
# Without validation
$ nhl-scrabble analyze --top-players 10000
# Fetches data... (2 minutes)
# Processes data... (1 minute)
# MemoryError: Ran out of memory

# With validation (click.IntRange(min=1, max=100))
$ nhl-scrabble analyze --top-players 10000
Error: Invalid value for '--top-players': 10000 is not in the range 1<=x<=100.
# Immediate feedback (< 1 second)
```

## Migration Guide

### Adding New Options

When adding new options to existing commands:

1. **Follow naming conventions** (kebab-case, descriptive)
1. **Add to appropriate section** (output, behavior, filtering, etc.)
1. **Use Click validation** (IntRange, Choice, Path)
1. **Document default** in help text
1. **Add to CLI reference** documentation
1. **Add tests** for the new option

### Changing Existing Options

**Non-breaking changes** (safe in minor versions):

- ✅ Improving help text
- ✅ Adding validation (if stricter validation is reasonable)
- ✅ Reordering options
- ✅ Adding new options

**Breaking changes** (require major version):

- ❌ Renaming options (e.g., `--division` → `--divisions`)
- ❌ Changing option behavior
- ❌ Removing options
- ❌ Making validation significantly stricter

For breaking changes:

1. **Document in CHANGELOG** with migration guide
1. **Update all documentation** (README, tutorials, API reference)
1. **Provide clear examples** of old vs new syntax
1. **Consider deprecation period** for widely-used options

## Common Patterns

### Multi-Value Options (Comma-Separated)

```python
@click.option(
    "--teams",
    help="Filter by teams (comma-separated: TOR,MTL,BOS)",
)
def command(teams: str | None):
    """Parse comma-separated teams."""
    if teams:
        teams_list = [t.strip() for t in teams.split(",")]
```

### Mutually Exclusive Options

```python
def validate_mutually_exclusive(ctx, param, value):
    """Ensure --scoring and --scoring-config are not both used."""
    if value and ctx.params.get("scoring_config"):
        raise click.UsageError(
            "--scoring and --scoring-config are mutually exclusive"
        )
    return value


@click.option("--scoring", callback=validate_mutually_exclusive, ...)
@click.option("--scoring-config", ...)
```

### Format-Specific Requirements

```python
def validate_csv_requires_output(ctx, param, value):
    """Validate CSV format requires output file."""
    output_format = ctx.params.get("output_format")
    if output_format in ("csv", "excel") and not value:
        raise click.UsageError(
            f"{output_format.upper()} format requires --output option"
        )
    return value


@click.option("--format", ...)
@click.option("--output", callback=validate_csv_requires_output, ...)
```

## Examples

### Good Option Definition

```python
@click.option(
    "--top-players",
    type=click.IntRange(min=1, max=100),
    default=20,
    help="Number of top players to show (default: 20, range: 1-100)",
)
```

**Why it's good:**

- ✅ Descriptive kebab-case name
- ✅ Built-in validation (IntRange)
- ✅ Clear default documented
- ✅ Range documented
- ✅ Concise help text

### Bad Option Definition

```python
@click.option(
    "--num",
    type=int,
    default=20,
    help="Number of players",
)
```

**Why it's bad:**

- ❌ Unclear name (`--num` of what?)
- ❌ No validation (accepts negative numbers, huge values)
- ❌ Default not documented
- ❌ No range guidance
- ❌ Incomplete help text

## Testing CLI Options

### Unit Tests

Test that options:

1. **Parse correctly** - Click accepts the values
1. **Validate correctly** - Invalid values are rejected
1. **Default correctly** - Default values are used when not specified
1. **Pass correctly** - Values reach the function

```python
def test_top_players_option(cli_runner):
    """Test --top-players option."""
    # Valid value
    result = cli_runner.invoke(cli, ["analyze", "--top-players", "50"])
    assert result.exit_code == 0

    # Too low (should fail)
    result = cli_runner.invoke(cli, ["analyze", "--top-players", "0"])
    assert result.exit_code != 0
    assert "Invalid value" in result.output

    # Too high (should fail)
    result = cli_runner.invoke(cli, ["analyze", "--top-players", "200"])
    assert result.exit_code != 0
    assert "not in the range" in result.output
```

### Help Text Tests

```python
def test_help_text_consistency(cli_runner):
    """Test help text follows standards."""
    result = cli_runner.invoke(cli, ["analyze", "--help"])
    assert result.exit_code == 0

    # Check defaults are shown
    assert "(default:" in result.output

    # Check ranges are shown for validated options
    assert "range:" in result.output or "min" in result.output.lower()
```

## References

- [Click Documentation](https://click.palletsprojects.com/)
- [Click Types](https://click.palletsprojects.com/en/stable/parameters/#parameter-types)
- [Click Validation](https://click.palletsprojects.com/en/stable/options/#callbacks-and-eager-options)
- [Unix CLI Conventions](https://www.gnu.org/software/libc/manual/html_node/Argument-Syntax.html)

## Changelog

- **2026-04-23**: Initial CLI standards document created (task refactoring/012)
