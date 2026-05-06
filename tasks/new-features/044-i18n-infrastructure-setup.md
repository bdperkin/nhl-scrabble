# I18n Infrastructure Setup

**GitHub Issue**: #494 - https://github.com/bdperkin/nhl-scrabble/issues/494

**Parent Task**: #218 - Internationalization and Localization (sub-task 1 of 6)

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

4-6 hours

## Description

Set up the foundational internationalization (i18n) infrastructure for the NHL Scrabble project. This includes installing Babel and gettext dependencies, creating the i18n utilities module, configuring translation extraction workflow, and establishing the directory structure for translation files. This is the first and foundational sub-task of the comprehensive i18n/l10n implementation (#218).

**Parent Task**: tasks/new-features/016-internationalization-localization.md

**Note**: This task has ID 044 but is logically sub-task 1 and must be completed before tasks 020-024.

## Current State

The project currently has no i18n infrastructure:

- No translation framework installed
- No i18n utilities module
- No translation extraction configuration
- No locales directory structure
- All strings are hardcoded in English throughout the codebase

**Current dependencies** (`pyproject.toml`):

```toml
[project]
dependencies = [
  "click>=8.1.7",
  "requests>=2.31.0",
  "rich>=13.7.0",
  # ... no i18n dependencies
]
```

**Current directory structure**:

```
src/nhl_scrabble/
├── api/
├── cli.py
├── models/
├── processors/
├── reports/
├── scoring/
└── web/
# No i18n.py module
# No locales/ directory
```

## Proposed Solution

### 1. Add Babel Dependencies

Add Babel and gettext to `pyproject.toml`:

```toml
[project.optional-dependencies]
i18n = [
  "babel>=2.14.0",
  "python-gettext>=5.0",
]

# For web interface
web = [
  "flask>=3.0.0",
  "flask-babel>=4.0.0",  # NEW for i18n
  # ... existing web dependencies
]
```

Update installation instructions to include i18n:

```bash
# Install with i18n support
uv pip install -e ".[i18n,web]"
```

### 2. Create I18n Utilities Module

Create `src/nhl_scrabble/i18n.py`:

```python
"""Internationalization utilities for NHL Scrabble."""

import gettext
import locale
import os
from pathlib import Path
from typing import Callable

# Supported locales (12 total covering major hockey markets)
SUPPORTED_LOCALES = [
    "en_US",  # English - United States (default)
    "en_CA",  # English - Canada
    "fr_CA",  # French - Canada
    "sv_SE",  # Swedish - Sweden
    "ru_RU",  # Russian - Russia
    "fi_FI",  # Finnish - Finland
    "cs_CZ",  # Czech - Czechia
    "de_DE",  # German - Germany
    "de_CH",  # German - Switzerland
    "it_CH",  # Italian - Switzerland
    "sk_SK",  # Slovak - Slovakia
    "lv_LV",  # Latvian - Latvia
]

# Default locale
DEFAULT_LOCALE = "en_US"

# Locales directory
LOCALES_DIR = Path(__file__).parent / "locales"


def get_system_locale() -> str:
    """Detect system locale.

    Returns:
        Locale code (e.g., "en_US") or DEFAULT_LOCALE if detection fails.

    Examples:
        >>> get_system_locale()
        'en_US'
        >>> # On French Canadian system: 'fr_CA'
    """
    try:
        system_locale, _ = locale.getdefaultlocale()
        if system_locale and system_locale in SUPPORTED_LOCALES:
            return system_locale
    except (ValueError, TypeError):
        pass
    return DEFAULT_LOCALE


def get_translator(locale_code: str | None = None) -> Callable[[str], str]:
    """Get translator function for a locale.

    Args:
        locale_code: Locale code (e.g., "fr_CA"). If None, uses system locale
            or NHL_SCRABBLE_LANG environment variable.

    Returns:
        Translation function (gettext). Returns identity function if
        translations not found (graceful fallback).

    Examples:
        >>> _ = get_translator("fr_CA")
        >>> _("Hello, World!")
        'Bonjour, le monde!'

        >>> _ = get_translator()  # Uses system locale
        >>> _("Analyzing NHL rosters...")
        'Analyse des effectifs de la LNH...'  # If system is fr_CA

        >>> # Environment variable override
        >>> os.environ["NHL_SCRABBLE_LANG"] = "sv_SE"
        >>> _ = get_translator()
        >>> _("Team")
        'Lag'  # Swedish translation
    """
    # Priority: explicit parameter > env var > system locale
    if locale_code is None:
        locale_code = os.getenv("NHL_SCRABBLE_LANG")
    if locale_code is None:
        locale_code = get_system_locale()

    # Validate locale
    if locale_code not in SUPPORTED_LOCALES:
        locale_code = DEFAULT_LOCALE

    try:
        translation = gettext.translation(
            "messages",
            localedir=str(LOCALES_DIR),
            languages=[locale_code],
        )
        return translation.gettext
    except FileNotFoundError:
        # Fallback to identity function (no translation)
        # This allows the app to work even without compiled translations
        return lambda s: s


def format_number(number: float, locale_code: str | None = None) -> str:
    """Format number according to locale conventions.

    Args:
        number: Number to format.
        locale_code: Locale code for formatting. If None, uses system locale.

    Returns:
        Formatted number string with locale-appropriate separators.

    Examples:
        >>> format_number(1234.56, "en_US")
        '1,234.56'
        >>> format_number(1234.56, "de_DE")
        '1.234,56'
        >>> format_number(1234.56, "fr_CA")
        '1 234,56'
    """
    if locale_code is None:
        locale_code = get_system_locale()

    try:
        locale.setlocale(locale.LC_NUMERIC, locale_code)
        return locale.format_string("%.2f", number, grouping=True)
    except locale.Error:
        # Fallback to standard formatting
        return f"{number:.2f}"
```

**Key Features**:

- **12 supported locales** covering major hockey markets
- **Graceful fallback**: Returns identity function if translations missing
- **Multiple locale sources**: Explicit parameter > env var > system locale
- **Locale-aware number formatting**: Uses regional conventions
- **Environment variable support**: `NHL_SCRABBLE_LANG` overrides

### 3. Create Babel Configuration

Create `babel.cfg` in project root:

```ini
# Babel extraction configuration for NHL Scrabble
# Extracts translatable strings from Python and Jinja2 templates

[python: **.py]
# Extract from all Python files
encoding = utf-8

[jinja2: **/templates/**.html]
# Extract from Jinja2 templates (web interface)
encoding = utf-8
```

**Purpose**:

- Tells `pybabel extract` which files to scan
- Python: All `.py` files (CLI, TUI, backend)
- Jinja2: All `.html` templates in `templates/` directories (web UI)

### 4. Create Locales Directory Structure

Create directory structure for translation files:

```bash
mkdir -p src/nhl_scrabble/locales
```

**Result**:

```
src/nhl_scrabble/
├── locales/           # NEW - translation files root
│   └── .gitkeep      # Ensure directory is tracked
├── i18n.py           # NEW - utilities module
└── ... (existing code)
```

**Note**: Individual locale directories (en_US, fr_CA, etc.) will be created later by `pybabel init` in sub-task 5 (task 023).

### 5. Create Translation Workflow Documentation

Create `.github/docs/translation-workflow.md`:

```markdown
# Translation Workflow

This document explains how to extract, manage, and compile translations for NHL Scrabble.

## Initial Setup

```bash
# Install i18n dependencies
uv pip install -e ".[i18n]"
```

## Extracting Strings

Extract all translatable strings from source code to POT template:

```bash
# Extract to messages.pot
pybabel extract -F babel.cfg -k _ -o messages.pot src/
```

This scans:

- All Python files for `_("string")` calls
- All Jinja2 templates for `{% trans %}` blocks

## Creating Locale Files

Initialize translation for a new locale:

```bash
# Example: French Canadian
pybabel init -i messages.pot -d src/nhl_scrabble/locales -l fr_CA
```

This creates: `src/nhl_scrabble/locales/fr_CA/LC_MESSAGES/messages.po`

## Updating Translations

When code changes and new strings are added:

```bash
# 1. Extract new strings
pybabel extract -F babel.cfg -k _ -o messages.pot src/

# 2. Update all locale .po files
pybabel update -i messages.pot -d src/nhl_scrabble/locales
```

## Compiling Translations

Compile `.po` files to binary `.mo` files for runtime use:

```bash
# Compile all locales
pybabel compile -d src/nhl_scrabble/locales
```

**Note**: `.mo` files are generated from `.po` files and should not be edited manually.

## Workflow Summary

```
Code with _("strings")
        ↓
  pybabel extract
        ↓
   messages.pot (template)
        ↓
   pybabel init (for new locales)
   pybabel update (for existing locales)
        ↓
   messages.po (edit translations here)
        ↓
  pybabel compile
        ↓
   messages.mo (runtime binary)
```

## Tools

- **pybabel**: Command-line tool from Babel package
- **Poedit**: GUI editor for .po files (optional)
- **Weblate**: Web-based translation platform (optional)

## CI/CD Integration

Translation compilation is automated in CI:

```yaml
- name: Compile translations
  run: |
    uv pip install -e ".[i18n]"
    pybabel compile -d src/nhl_scrabble/locales
```
```

### 6. Update Configuration

Add locale configuration to `src/nhl_scrabble/config.py`:

```python
from dataclasses import dataclass, field
import os


@dataclass
class Config:
    # ... existing config fields ...

    locale: str = field(
        default_factory=lambda: os.getenv("NHL_SCRABBLE_LANG", "en_US")
    )

    def __post_init__(self):
        """Validate configuration after initialization."""
        # ... existing validation ...

        # Validate locale
        from nhl_scrabble.i18n import SUPPORTED_LOCALES, DEFAULT_LOCALE

        if self.locale not in SUPPORTED_LOCALES:
            self.locale = DEFAULT_LOCALE
```

## Implementation Steps

1. **Add Dependencies** (30 min)

   - Update `pyproject.toml` with Babel dependencies
   - Add to `[project.optional-dependencies]` section
   - Add `flask-babel` to `web` optional dependencies
   - Document installation in README.md

2. **Create I18n Module** (2h)

   - Create `src/nhl_scrabble/i18n.py`
   - Implement `SUPPORTED_LOCALES` constant
   - Implement `get_system_locale()` function
   - Implement `get_translator()` function
   - Implement `format_number()` function
   - Add comprehensive docstrings with examples
   - Add type hints

3. **Create Babel Configuration** (15 min)

   - Create `babel.cfg` in project root
   - Configure Python file extraction
   - Configure Jinja2 template extraction
   - Test extraction with sample strings

4. **Create Directory Structure** (15 min)

   - Create `src/nhl_scrabble/locales/` directory
   - Add `.gitkeep` to ensure directory is tracked
   - Document structure in parent task

5. **Create Workflow Documentation** (1h)

   - Create `.github/docs/translation-workflow.md`
   - Document extraction process
   - Document initialization process
   - Document update workflow
   - Document compilation process
   - Include CI/CD integration examples

6. **Update Config Module** (30 min)

   - Add `locale` field to `Config` dataclass
   - Add validation in `__post_init__`
   - Support `NHL_SCRABBLE_LANG` env var
   - Add tests for locale validation

7. **Update Documentation** (1h)

   - Update README.md with i18n support info
   - Document supported locales
   - Document environment variables
   - Update installation instructions
   - Add i18n optional dependency group

## Testing Strategy

### Unit Tests

Create `tests/unit/test_i18n.py`:

```python
"""Tests for i18n utilities module."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from nhl_scrabble.i18n import (
    DEFAULT_LOCALE,
    SUPPORTED_LOCALES,
    format_number,
    get_system_locale,
    get_translator,
)


def test_supported_locales_count():
    """Test that all 12 expected locales are supported."""
    assert len(SUPPORTED_LOCALES) == 12


def test_supported_locales_includes_defaults():
    """Test that essential locales are included."""
    assert "en_US" in SUPPORTED_LOCALES
    assert "fr_CA" in SUPPORTED_LOCALES
    assert "sv_SE" in SUPPORTED_LOCALES


def test_default_locale():
    """Test default locale is en_US."""
    assert DEFAULT_LOCALE == "en_US"


def test_get_system_locale_fallback():
    """Test get_system_locale returns default when detection fails."""
    with patch("locale.getdefaultlocale", return_value=(None, None)):
        assert get_system_locale() == DEFAULT_LOCALE


def test_get_system_locale_supported():
    """Test get_system_locale returns supported locale."""
    with patch("locale.getdefaultlocale", return_value=("fr_CA", "UTF-8")):
        assert get_system_locale() == "fr_CA"


def test_get_system_locale_unsupported():
    """Test get_system_locale falls back for unsupported locale."""
    with patch("locale.getdefaultlocale", return_value=("ja_JP", "UTF-8")):
        assert get_system_locale() == DEFAULT_LOCALE


def test_get_translator_default():
    """Test get_translator returns function for default locale."""
    _ = get_translator("en_US")
    assert callable(_)
    # Without compiled translations, should return identity function
    assert _("Hello") == "Hello"


def test_get_translator_unsupported_locale():
    """Test get_translator falls back for unsupported locale."""
    _ = get_translator("invalid_LOCALE")
    assert callable(_)
    assert _("Test") == "Test"


def test_get_translator_env_var():
    """Test get_translator respects NHL_SCRABBLE_LANG env var."""
    with patch.dict(os.environ, {"NHL_SCRABBLE_LANG": "fr_CA"}):
        _ = get_translator()
        assert callable(_)


def test_get_translator_none_uses_system():
    """Test get_translator(None) uses system locale."""
    with patch("nhl_scrabble.i18n.get_system_locale", return_value="sv_SE"):
        _ = get_translator(None)
        assert callable(_)


def test_format_number_en_us():
    """Test number formatting for US locale."""
    result = format_number(1234.56, "en_US")
    # May vary by system, but should contain the number
    assert "1234" in result or "1,234" in result


def test_format_number_fallback():
    """Test number formatting fallback for invalid locale."""
    result = format_number(1234.56, "invalid_LOCALE")
    assert result == "1234.56"


def test_format_number_none_locale():
    """Test format_number with None uses system locale."""
    result = format_number(1234.56, None)
    assert "1234" in result
```

### Integration Tests

Create `tests/integration/test_i18n_integration.py`:

```python
"""Integration tests for i18n functionality."""

import os
from pathlib import Path

import pytest

from nhl_scrabble.config import Config
from nhl_scrabble.i18n import get_translator


def test_config_locale_default():
    """Test Config uses default locale."""
    config = Config()
    assert config.locale == "en_US"


def test_config_locale_from_env():
    """Test Config reads locale from environment."""
    with patch.dict(os.environ, {"NHL_SCRABBLE_LANG": "fr_CA"}):
        config = Config()
        assert config.locale == "fr_CA"


def test_config_locale_validation():
    """Test Config validates unsupported locale."""
    with patch.dict(os.environ, {"NHL_SCRABBLE_LANG": "invalid"}):
        config = Config()
        assert config.locale == "en_US"  # Falls back to default


def test_locales_directory_exists():
    """Test locales directory is created."""
    from nhl_scrabble.i18n import LOCALES_DIR

    # Directory may not exist until locales are initialized
    # Just verify path is defined correctly
    assert LOCALES_DIR.name == "locales"
    assert "nhl_scrabble" in str(LOCALES_DIR)
```

### Manual Testing

```bash
# 1. Install dependencies
uv pip install -e ".[i18n]"

# 2. Test extraction (should succeed even without marked strings yet)
pybabel extract -F babel.cfg -k _ -o messages.pot src/

# 3. Verify messages.pot is created
cat messages.pot

# 4. Test Python utilities
python3 << 'EOF'
from nhl_scrabble.i18n import get_translator, SUPPORTED_LOCALES
print(f"Supported locales: {len(SUPPORTED_LOCALES)}")
_ = get_translator("en_US")
print(_("Hello, World!"))
EOF

# 5. Test environment variable
export NHL_SCRABBLE_LANG=fr_CA
python3 << 'EOF'
from nhl_scrabble.i18n import get_translator
_ = get_translator()
print(_("Hello"))  # Should still be "Hello" until translations exist
EOF
```

## Acceptance Criteria

- [ ] Babel and python-gettext added to `pyproject.toml` `[project.optional-dependencies.i18n]`
- [ ] Flask-Babel added to `[project.optional-dependencies.web]`
- [ ] `src/nhl_scrabble/i18n.py` created with all utilities:
  - [ ] `SUPPORTED_LOCALES` constant (12 locales)
  - [ ] `DEFAULT_LOCALE` constant
  - [ ] `LOCALES_DIR` path
  - [ ] `get_system_locale()` function
  - [ ] `get_translator()` function
  - [ ] `format_number()` function
- [ ] `babel.cfg` created with Python and Jinja2 extraction rules
- [ ] `src/nhl_scrabble/locales/` directory created
- [ ] `.github/docs/translation-workflow.md` documentation created
- [ ] `Config` class updated with `locale` field
- [ ] README.md updated with i18n support information
- [ ] All functions have type hints
- [ ] All functions have comprehensive docstrings with examples
- [ ] Unit tests pass (20+ tests)
- [ ] Integration tests pass
- [ ] `pybabel extract` command works
- [ ] Documentation is clear and complete

## Related Files

- `pyproject.toml` - Add i18n dependencies
- `src/nhl_scrabble/i18n.py` - NEW utilities module
- `src/nhl_scrabble/locales/` - NEW directory for translations
- `babel.cfg` - NEW Babel configuration
- `src/nhl_scrabble/config.py` - Add locale field
- `README.md` - Document i18n support
- `.github/docs/translation-workflow.md` - NEW workflow documentation
- `tests/unit/test_i18n.py` - NEW unit tests
- `tests/integration/test_i18n_integration.py` - NEW integration tests

## Dependencies

- **Prerequisites**: None (this is the foundational task)
- **Blocks**:
  - Task 020: CLI Internationalization (needs i18n utilities)
  - Task 021: Web Internationalization (needs i18n utilities)
  - Task 022: TUI Internationalization (needs i18n utilities)
  - Task 023: Create Translation Files (needs babel.cfg and locales dir)
  - Task 024: Priority Language Translations (needs translation infrastructure)
- **Parent**: #218 - Internationalization and Localization

## Additional Notes

### Performance Implications

- Translation lookup is fast (gettext uses binary .mo files)
- First translation call loads .mo file into memory
- Subsequent calls are cached lookups
- Negligible performance impact (<1ms per translation)

### Security Considerations

- Translation files (.po/.mo) should be treated as trusted content
- No user input is passed to translation functions
- All locale codes are validated against `SUPPORTED_LOCALES`
- Environment variable `NHL_SCRABBLE_LANG` is validated

### Breaking Changes

None - this is purely additive infrastructure.

### Migration Required

None - no existing functionality is affected.

### Future Enhancements

- **Automated translation updates**: GitHub Actions workflow to auto-update .po files when code changes
- **Translation coverage reports**: Show % of strings translated per locale
- **Weblate integration**: Community translation platform
- **Pluralization support**: Handle plural forms correctly per locale
- **Date/time formatting**: Locale-aware date formatting (future sub-task)
- **Right-to-left (RTL) support**: If adding Arabic/Hebrew locales in future

### Why 12 Locales?

The 12 supported locales cover all countries with NHL teams plus major European hockey markets:

- **North America** (NHL teams): en_US, en_CA, fr_CA
- **European hockey powers**: sv_SE (Sweden), ru_RU (Russia), fi_FI (Finland), cs_CZ (Czechia), de_DE (Germany), sk_SK (Slovakia), lv_LV (Latvia)
- **Switzerland** (multilingual): de_CH, it_CH

Romansh (rm_CH) was considered but is very rare (~60,000 speakers) and can be added later if requested.

## Implementation Notes

*To be filled during implementation:*

- Actual implementation approach
- Challenges encountered
- Deviations from plan
- Actual effort vs estimated
- Related PRs
- Lessons learned
