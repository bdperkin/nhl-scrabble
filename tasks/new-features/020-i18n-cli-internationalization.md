# CLI Internationalization Implementation

**GitHub Issue**: #248 - https://github.com/bdperkin/nhl-scrabble/issues/248

**Parent Task**: #218 - Internationalization and Localization (sub-task 2 of 6)

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

4-6 hours

## Description

Internationalize the CLI interface (`src/nhl_scrabble/cli.py`) by wrapping all user-facing strings with gettext translation markers, adding locale option support, and enabling environment variable-based locale selection. This is the second sub-task of the comprehensive i18n/l10n implementation.

**Parent Task**: tasks/new-features/016-internationalization-localization.md

## Current State

The CLI is currently hardcoded in English:

```python
# src/nhl_scrabble/cli.py
@click.command()
@click.option("--format", type=click.Choice(["text", "json"]), default="text")
@click.option("--output", "-o", type=click.Path(), default=None,
              help="Output file path (default: stdout)")
def analyze(format: str, output: str | None) -> None:
    """Analyze NHL rosters and calculate Scrabble scores."""
    click.echo("Analyzing NHL rosters...")
    click.echo("Fetching team data...")
    # All strings are in English
```

**Issues:**

- All user-facing strings are hardcoded in English
- No locale detection or selection
- No translation support
- Help text not translatable

## Proposed Solution

### 1. Import Translation Utilities

```python
# src/nhl_scrabble/cli.py
import os
import click
from nhl_scrabble.i18n import get_translator, SUPPORTED_LOCALES

# Get translator (uses NHL_SCRABBLE_LANG env var or system locale)
_ = get_translator(os.getenv("NHL_SCRABBLE_LANG"))
```

### 2. Add Locale Option

```python
@click.command()
@click.option("--format", type=click.Choice(["text", "json"]), default="text",
              help=_("Output format (text or json)"))
@click.option("--output", "-o", type=click.Path(), default=None,
              help=_("Output file path (default: stdout)"))
@click.option("--locale", "-l", type=click.Choice(SUPPORTED_LOCALES), default=None,
              help=_("Display locale (e.g., fr_CA for Canadian French)"))
@click.option("--verbose", "-v", is_flag=True,
              help=_("Enable verbose logging"))
def analyze(format: str, output: str | None, locale: str | None, verbose: bool) -> None:
    """Analyze NHL rosters and calculate Scrabble scores."""
    # Override translator if locale specified
    if locale:
        global _
        _ = get_translator(locale)

    if verbose:
        click.echo(_("Verbose mode enabled"))

    click.echo(_("Analyzing NHL rosters..."))
    # ... rest of implementation
```

### 3. Wrap All User-Facing Strings

```python
# Before:
click.echo("Fetching team data...")
click.echo("Processing teams...")
click.echo(f"Found {count} players")

# After:
click.echo(_("Fetching team data..."))
click.echo(_("Processing teams..."))
click.echo(_("Found {count} players").format(count=count))
```

### 4. Translate Error Messages

```python
# Before:
raise click.ClickException("Invalid output format")

# After:
raise click.ClickException(_("Invalid output format"))
```

### 5. Extract CLI Strings

```bash
# Extract all CLI strings to messages.pot
pybabel extract -F babel.cfg -k _ -o messages.pot src/nhl_scrabble/

# Update locale files
pybabel update -i messages.pot -d src/nhl_scrabble/locales
```

## Implementation Steps

1. **Import I18n Utilities** (30 min)

   - Add import for get_translator and SUPPORTED_LOCALES
   - Initialize translator at module level
   - Test basic translation functionality

1. **Add Locale Option** (1h)

   - Add --locale/-l option to analyze command
   - Implement locale override logic
   - Support NHL_SCRABBLE_LANG environment variable
   - Test locale switching

1. **Wrap All Strings** (2-3h)

   - Identify all user-facing strings in cli.py
   - Wrap with \_() translation marker
   - Handle f-strings and string formatting
   - Test that all strings are captured

1. **Extract Strings** (30 min)

   - Run pybabel extract for CLI module
   - Verify all strings in messages.pot
   - Initialize/update locale .po files

1. **Testing** (1-2h)

   - Unit tests for locale detection
   - Integration tests for each supported locale
   - Test environment variable support
   - Test --locale option
   - Verify translated strings appear correctly

1. **Documentation** (30 min)

   - Update CLI help text with locale option
   - Document NHL_SCRABBLE_LANG environment variable
   - Add examples to README.md
   - Update TRANSLATING.md with CLI-specific notes

## Testing Strategy

### Unit Tests

```python
# tests/unit/test_cli_i18n.py
from click.testing import CliRunner
from nhl_scrabble.cli import analyze

def test_cli_default_locale():
    """Test CLI with default (system) locale."""
    runner = CliRunner()
    result = runner.invoke(analyze)
    assert result.exit_code == 0

def test_cli_french_locale():
    """Test CLI with French locale."""
    runner = CliRunner()
    result = runner.invoke(analyze, ['--locale', 'fr_CA'])
    assert result.exit_code == 0
    # Verify French strings appear
    assert "Analyse" in result.output or result.exit_code == 0

def test_cli_locale_env_var():
    """Test CLI with NHL_SCRABBLE_LANG environment variable."""
    runner = CliRunner()
    result = runner.invoke(analyze, env={'NHL_SCRABBLE_LANG': 'sv_SE'})
    assert result.exit_code == 0

def test_cli_invalid_locale():
    """Test CLI with invalid locale."""
    runner = CliRunner()
    result = runner.invoke(analyze, ['--locale', 'xx_YY'])
    assert result.exit_code != 0  # Should fail validation
```

### Manual Testing

```bash
# Test each locale
nhl-scrabble analyze --locale en_US
nhl-scrabble analyze --locale fr_CA
nhl-scrabble analyze --locale sv_SE

# Test environment variable
export NHL_SCRABBLE_LANG=fr_CA
nhl-scrabble analyze

# Test help text translation
nhl-scrabble analyze --help --locale fr_CA
```

## Acceptance Criteria

- [ ] I18n utilities imported and translator initialized
- [ ] --locale/-l option added to CLI
- [ ] NHL_SCRABBLE_LANG environment variable supported
- [ ] All user-facing strings wrapped with \_()
- [ ] Error messages internationalized
- [ ] Help text translatable
- [ ] CLI strings extracted to messages.pot
- [ ] Tests pass for all supported locales
- [ ] Documentation updated

## Related Files

- `src/nhl_scrabble/cli.py` - CLI internationalization
- `src/nhl_scrabble/i18n.py` - I18n utilities (from sub-task 1)
- `src/nhl_scrabble/locales/` - Translation files
- `babel.cfg` - Extraction configuration
- `tests/unit/test_cli_i18n.py` - New tests

## Dependencies

- **Prerequisite**: Sub-task 1 (I18n Infrastructure) must be completed first
- **Parent Task**: #218 - Internationalization and Localization
- **Package**: Babel (from sub-task 1)

## Additional Notes

**Translation String Guidelines:**

- Use \_() for all user-visible strings
- Extract variable values from strings:
  - ❌ \_(f"Found {count} players") # Can't extract
  - ✅ \_("Found {count} players").format(count=count) # Extractable
- Use consistent terminology across CLI
- Avoid abbreviations that don't translate well
- Consider string length variations across languages

**Environment Variable:**

The `NHL_SCRABBLE_LANG` environment variable provides a way for users to set their preferred locale without using command-line flags on every invocation:

```bash
# Set in shell profile
export NHL_SCRABBLE_LANG=fr_CA

# Or per-command
NHL_SCRABBLE_LANG=sv_SE nhl-scrabble analyze
```

## Implementation Notes

*To be filled during implementation:*

- Number of strings internationalized
- Locale testing results
- Translation extraction challenges
- String length issues across languages
- Actual effort vs estimated
