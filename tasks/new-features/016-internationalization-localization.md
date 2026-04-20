# Internationalization and Localization (i18n/l10n)

**GitHub Issue**: #218 - https://github.com/bdperkin/nhl-scrabble/issues/218

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

32-48 hours

## Description

Implement comprehensive internationalization (i18n) and localization (l10n) support across all user-facing components: Web interface, CLI, and TUI (Terminal User Interface). Support translations for 11 languages covering major hockey markets: English, French, Swedish, Russian, Finnish, Czech, German, Italian, Romansh, Slovak, and Latvian.

This enables the NHL Scrabble project to serve international hockey communities in their native languages, improving accessibility and user experience for non-English speakers.

## Current State

The project is currently English-only:

**CLI (src/nhl_scrabble/cli.py):**

```python
@click.command()
@click.option("--format", type=click.Choice(["text", "json"]), default="text")
@click.option("--output", "-o", type=click.Path(), default=None,
              help="Output file path (default: stdout)")
def analyze(format: str, output: str | None) -> None:
    """Analyze NHL rosters and calculate Scrabble scores."""
    # All strings hardcoded in English
```

**Web Interface (src/nhl_scrabble/web/):**

```html
<h1>NHL Scrabble Scores</h1>
<p>Analyzing player names by Scrabble values</p>
```

**TUI (src/nhl_scrabble/interactive/):**

```python
print("Welcome to NHL Scrabble Interactive Mode")
print("Commands: analyze, filter, export, quit")
```

**Issues:**

1. No i18n framework in place
1. All user-facing strings are hardcoded in English
1. No translation files or infrastructure
1. No locale detection or selection
1. Date/time formatting is not locale-aware
1. Number formatting is not locale-aware (e.g., 1,234.56 vs 1.234,56)

## Proposed Solution

### 1. I18n Framework Selection

Use **Babel** and **gettext** for Python internationalization:

```toml
# pyproject.toml
[project.optional-dependencies]
i18n = [
    "babel>=2.14.0",
    "python-gettext>=5.0",
]
```

For web templates, use **Jinja2 i18n extension** (already available).

### 2. Target Locales

Support the following locale codes:

| Locale | Language | Region        | Notes                    |
| ------ | -------- | ------------- | ------------------------ |
| en_US  | English  | United States | Default                  |
| en_CA  | English  | Canada        | Canadian English         |
| fr_CA  | French   | Canada        | Canadian French          |
| sv_SE  | Swedish  | Sweden        | Swedish                  |
| ru_RU  | Russian  | Russia        | Russian                  |
| fi_FI  | Finnish  | Finland       | Finnish                  |
| cs_CZ  | Czech    | Czechia       | Czech                    |
| de_DE  | German   | Germany       | German (Germany)         |
| de_CH  | German   | Switzerland   | German (Switzerland)     |
| it_CH  | Italian  | Switzerland   | Italian (Switzerland)    |
| rm_CH  | Romansh  | Switzerland   | Romansh (rare, optional) |
| sk_SK  | Slovak   | Slovakia      | Slovak                   |
| lv_LV  | Latvian  | Latvia        | Latvian                  |

**Note**: Romansh (rm_CH) is very rare - consider optional/future phase.

### 3. Directory Structure

```
src/nhl_scrabble/
├── locales/
│   ├── en_US/
│   │   └── LC_MESSAGES/
│   │       ├── messages.po    # Translation source
│   │       └── messages.mo    # Compiled translations
│   ├── fr_CA/
│   │   └── LC_MESSAGES/
│   │       ├── messages.po
│   │       └── messages.mo
│   ├── sv_SE/
│   │   └── LC_MESSAGES/
│   │       ├── messages.po
│   │       └── messages.mo
│   └── ... (other locales)
├── i18n.py                    # I18n utilities
└── ... (existing code)
```

### 4. I18n Utilities Module

Create `src/nhl_scrabble/i18n.py`:

```python
"""Internationalization utilities for NHL Scrabble."""

import gettext
import locale
from pathlib import Path
from typing import Callable

# Supported locales
SUPPORTED_LOCALES = [
    "en_US",
    "en_CA",
    "fr_CA",
    "sv_SE",
    "ru_RU",
    "fi_FI",
    "cs_CZ",
    "de_DE",
    "de_CH",
    "it_CH",
    "sk_SK",
    "lv_LV",
]

# Default locale
DEFAULT_LOCALE = "en_US"

# Locales directory
LOCALES_DIR = Path(__file__).parent / "locales"


def get_system_locale() -> str:
    """Detect system locale.

    Returns:
        Locale code (e.g., "en_US") or DEFAULT_LOCALE if detection fails.
    """
    try:
        system_locale, _ = locale.getdefaultlocale()
        if system_locale and system_locale in SUPPORTED_LOCALES:
            return system_locale
    except (ValueError, TypeError):
        pass
    return DEFAULT_LOCALE


def get_translator(locale_code: str = None) -> Callable[[str], str]:
    """Get translator function for a locale.

    Args:
        locale_code: Locale code (e.g., "fr_CA"). If None, uses system locale.

    Returns:
        Translation function (gettext).

    Example:
        _ = get_translator("fr_CA")
        print(_("Hello, World!"))  # Prints: Bonjour, le monde!
    """
    if locale_code is None:
        locale_code = get_system_locale()

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
        # Fallback to default (no translation)
        return lambda s: s


def format_number(number: float, locale_code: str = None) -> str:
    """Format number according to locale.

    Args:
        number: Number to format.
        locale_code: Locale code for formatting.

    Returns:
        Formatted number string.

    Example:
        format_number(1234.56, "en_US")  # "1,234.56"
        format_number(1234.56, "de_DE")  # "1.234,56"
    """
    if locale_code is None:
        locale_code = get_system_locale()

    try:
        locale.setlocale(locale.LC_NUMERIC, locale_code)
        return locale.format_string("%.2f", number, grouping=True)
    except locale.Error:
        return f"{number:.2f}"
```

### 5. CLI Internationalization

Update CLI to use translations:

```python
# src/nhl_scrabble/cli.py
import click
from nhl_scrabble.i18n import get_translator

# Get translator (uses system locale or NHL_SCRABBLE_LANG env var)
_ = get_translator(os.getenv("NHL_SCRABBLE_LANG"))

@click.command()
@click.option("--format", type=click.Choice(["text", "json"]), default="text",
              help=_("Output format (text or json)"))
@click.option("--output", "-o", type=click.Path(), default=None,
              help=_("Output file path (default: stdout)"))
@click.option("--locale", "-l", type=click.Choice(SUPPORTED_LOCALES), default=None,
              help=_("Display locale (e.g., fr_CA for Canadian French)"))
def analyze(format: str, output: str | None, locale: str | None) -> None:
    """Analyze NHL rosters and calculate Scrabble scores."""
    if locale:
        # Override translator with specified locale
        _ = get_translator(locale)

    click.echo(_("Analyzing NHL rosters..."))
    # ... rest of implementation
```

### 6. Web Internationalization

Enable Jinja2 i18n extension:

```python
# src/nhl_scrabble/web/app.py
from flask import Flask, request
from flask_babel import Babel

app = Flask(__name__)
babel = Babel(app)

@babel.localeselector
def get_locale():
    """Select locale from request."""
    # Try URL parameter first
    locale = request.args.get('lang')
    if locale in SUPPORTED_LOCALES:
        return locale

    # Try browser Accept-Language header
    return request.accept_languages.best_match(SUPPORTED_LOCALES)
```

Templates use `{% trans %}` tags:

```html
<!-- templates/index.html -->
<h1>{% trans %}NHL Scrabble Scores{% endtrans %}</h1>
<p>{% trans %}Analyzing player names by Scrabble values{% endtrans %}</p>

<!-- Language selector -->
<select id="language">
  <option value="en_US">English (US)</option>
  <option value="fr_CA">Français (Canada)</option>
  <option value="sv_SE">Svenska</option>
  <!-- ... other locales -->
</select>
```

### 7. TUI Internationalization

Update interactive shell:

```python
# src/nhl_scrabble/interactive/shell.py
from nhl_scrabble.i18n import get_translator

_ = get_translator()

def welcome():
    """Display welcome message."""
    print(_("Welcome to NHL Scrabble Interactive Mode"))
    print(_("Commands: analyze, filter, export, quit"))
    print(_("Type 'help' for more information"))

def help_text():
    """Display help text."""
    return _("""
Available commands:
  analyze - Analyze all NHL teams
  filter  - Filter results by team/division/conference
  export  - Export results to file
  quit    - Exit the program
""")
```

### 8. Translation Workflow

**Step 1: Extract Translatable Strings**

Create `babel.cfg`:

```ini
[python: **.py]
[jinja2: templates/**.html]
encoding = utf-8
```

Extract strings:

```bash
# Extract all translatable strings to messages.pot
pybabel extract -F babel.cfg -o messages.pot src/
```

**Step 2: Create Translation Files**

For each locale:

```bash
# Initialize French Canadian translations
pybabel init -i messages.pot -d src/nhl_scrabble/locales -l fr_CA

# This creates: src/nhl_scrabble/locales/fr_CA/LC_MESSAGES/messages.po
```

**Step 3: Translate**

Edit `.po` files manually or use translation tool (Poedit, Weblate):

```po
# src/nhl_scrabble/locales/fr_CA/LC_MESSAGES/messages.po
msgid "Analyzing NHL rosters..."
msgstr "Analyse des effectifs de la LNH..."

msgid "Team"
msgstr "Équipe"

msgid "Score"
msgstr "Score"
```

**Step 4: Compile Translations**

```bash
# Compile all translations to .mo files
pybabel compile -d src/nhl_scrabble/locales
```

**Step 5: Update Translations** (when code changes)

```bash
# Extract new strings
pybabel extract -F babel.cfg -o messages.pot src/

# Update all locale .po files
pybabel update -i messages.pot -d src/nhl_scrabble/locales
```

### 9. Configuration

Add locale configuration:

```python
# src/nhl_scrabble/config.py

@dataclass
class Config:
    # ... existing config ...

    locale: str = field(
        default_factory=lambda: os.getenv("NHL_SCRABBLE_LANG", "en_US")
    )

    @validator("locale")
    def validate_locale(cls, v: str) -> str:
        """Validate locale is supported."""
        from nhl_scrabble.i18n import SUPPORTED_LOCALES, DEFAULT_LOCALE
        if v not in SUPPORTED_LOCALES:
            return DEFAULT_LOCALE
        return v
```

## Implementation Steps

1. **Setup I18n Infrastructure** (4-6h)

   - Add babel and gettext dependencies
   - Create `src/nhl_scrabble/i18n.py` utilities module
   - Create `locales/` directory structure
   - Create `babel.cfg` configuration
   - Set up translation extraction workflow
   - Document translation process

1. **CLI Internationalization** (4-6h)

   - Wrap all user-facing strings with `_()`
   - Add `--locale` option to CLI
   - Support `NHL_SCRABBLE_LANG` environment variable
   - Test locale detection
   - Extract CLI strings to messages.pot

1. **Web Internationalization** (6-8h)

   - Install Flask-Babel
   - Enable Jinja2 i18n extension
   - Wrap template strings with `{% trans %}`
   - Add language selector to web UI
   - Implement locale detection from Accept-Language header
   - Add `?lang=` URL parameter support
   - Extract web strings to messages.pot

1. **TUI Internationalization** (3-4h)

   - Wrap all interactive shell strings with `_()`
   - Test in different locales
   - Extract TUI strings to messages.pot

1. **Create Translation Files** (2-3h)

   - Initialize .po files for all 12 locales
   - Set up directory structure
   - Create template .po files
   - Document translation contribution process

1. **Translate to Priority Languages** (8-12h)

   - **Phase 1** (high priority): en_US, fr_CA, sv_SE
     - EN: Template (already in English)
     - FR: ~200-300 strings to translate
     - SV: ~200-300 strings to translate
   - **Phase 2** (medium priority): de_DE, fi_FI, ru_RU
   - **Phase 3** (lower priority): remaining locales

   **Note**: Consider hiring professional translators or using community contributions for non-English translations. Machine translation (DeepL, Google Translate) can provide initial drafts but needs native speaker review.

1. **Number/Date Formatting** (2-3h)

   - Implement locale-aware number formatting
   - Implement locale-aware date/time formatting
   - Test with various locales
   - Document formatting behavior

1. **Testing** (3-5h)

   - Unit tests for i18n utilities
   - Integration tests for each locale
   - Manual testing in all interfaces (CLI, Web, TUI)
   - Test locale switching
   - Test fallback behavior
   - Verify .mo file generation

1. **Documentation** (2-3h)

   - Update README with i18n support info
   - Create TRANSLATING.md guide for contributors
   - Document supported locales
   - Document how to add new languages
   - Update CONTRIBUTING.md with translation workflow

1. **CI/CD Integration** (1-2h)

   - Add babel compile step to build process
   - Verify .mo files are included in distribution
   - Add locale smoke tests to CI
   - Test that fallback works when translations missing

## Testing Strategy

### Unit Tests

```python
# tests/unit/test_i18n.py
from nhl_scrabble.i18n import get_translator, format_number

def test_get_translator_default():
    """Test default translator (English)."""
    _ = get_translator("en_US")
    assert _("Hello") == "Hello"

def test_get_translator_french():
    """Test French translator."""
    _ = get_translator("fr_CA")
    assert _("Team") == "Équipe"
    assert _("Score") == "Score"

def test_format_number_us():
    """Test US number formatting."""
    assert format_number(1234.56, "en_US") == "1,234.56"

def test_format_number_german():
    """Test German number formatting."""
    assert format_number(1234.56, "de_DE") == "1.234,56"

def test_unsupported_locale_fallback():
    """Test fallback to English for unsupported locale."""
    _ = get_translator("xx_YY")
    assert _("Hello") == "Hello"
```

### Integration Tests

```python
# tests/integration/test_cli_i18n.py
from click.testing import CliRunner
from nhl_scrabble.cli import analyze

def test_cli_english():
    """Test CLI in English."""
    runner = CliRunner()
    result = runner.invoke(analyze, ["--locale", "en_US"])
    assert "Analyzing NHL rosters" in result.output

def test_cli_french():
    """Test CLI in French."""
    runner = CliRunner()
    result = runner.invoke(analyze, ["--locale", "fr_CA"])
    assert "Analyse des effectifs" in result.output
```

### Manual Testing

1. **CLI Testing**

   ```bash
   # Test each locale
   NHL_SCRABBLE_LANG=fr_CA nhl-scrabble analyze
   nhl-scrabble analyze --locale sv_SE
   ```

1. **Web Testing**

   - Visit `http://localhost:5000?lang=fr_CA`
   - Use browser language preferences
   - Test language selector widget

1. **TUI Testing**

   ```bash
   NHL_SCRABBLE_LANG=fi_FI nhl-scrabble interactive
   ```

## Acceptance Criteria

- [ ] Babel and gettext configured and working
- [ ] I18n utilities module (`i18n.py`) implemented
- [ ] All CLI strings wrapped with `_()`
- [ ] All web template strings wrapped with `{% trans %}`
- [ ] All TUI strings wrapped with `_()`
- [ ] Translation files created for all 12 locales
- [ ] At least 3 locales fully translated (en_US, fr_CA, sv_SE)
- [ ] Locale detection works (system locale, env var, CLI option)
- [ ] Number formatting is locale-aware
- [ ] Date formatting is locale-aware
- [ ] Language selector works in web UI
- [ ] Fallback to English works for missing translations
- [ ] Documentation updated (README, TRANSLATING.md)
- [ ] Tests pass for all i18n functionality
- [ ] CI compiles translations successfully
- [ ] Distribution includes .mo files

## Related Files

- `src/nhl_scrabble/i18n.py` - New i18n utilities module
- `src/nhl_scrabble/locales/` - New translations directory
- `src/nhl_scrabble/cli.py` - Update with translations
- `src/nhl_scrabble/web/app.py` - Add Flask-Babel
- `src/nhl_scrabble/web/templates/` - Add trans tags
- `src/nhl_scrabble/interactive/shell.py` - Update with translations
- `src/nhl_scrabble/config.py` - Add locale configuration
- `pyproject.toml` - Add babel dependency
- `babel.cfg` - New extraction configuration
- `TRANSLATING.md` - New contributor guide
- `README.md` - Update with i18n information

## Dependencies

- **Python packages**:

  - `babel>=2.14.0` - I18n framework
  - `python-gettext>=5.0` - Gettext wrapper
  - `Flask-Babel>=4.0.0` - Flask i18n extension (if web interface exists)

- **System tools**:

  - `pybabel` command-line tool (installed with babel)
  - Optional: Poedit or similar for translation editing

- **Optional for professional translation**:

  - Budget for professional translators
  - Or community contribution platform (Weblate, Crowdin)

## Additional Notes

### Language Coverage Rationale

The selected languages cover major hockey markets:

- **North America**: EN (US/Canada), FR (Canada) - NHL's primary market
- **Europe**: SV (Sweden), FI (Finland), RU (Russia), CS (Czechia), SK (Slovakia), DE (Germany/Switzerland) - Strong hockey tradition
- **Switzerland**: DE, IT, RM - Multilingual country, minor hockey market
- **Latvia**: LV - Growing hockey market, NHL presence

### Translation Quality

**Option 1: Community Contributions** (Recommended)

- Use platforms like Weblate or Crowdin
- Allow community members to contribute translations
- Native speakers review and approve
- Cost: Free (time only)

**Option 2: Machine Translation + Review**

- Use DeepL or Google Translate for initial translation
- Have native speakers review and correct
- Cost: Moderate (reviewer time)

**Option 3: Professional Translation**

- Hire professional translators
- Highest quality, especially for marketing/public-facing text
- Cost: High ($0.10-0.20 per word × 300 words × 11 languages = $330-660)

### Romansh (rm_CH) Consideration

Romansh is spoken by ~40,000 people in Switzerland. Consider:

- Include in infrastructure but mark as "community contributed"
- Don't prioritize for initial release
- Accept community translations if offered

### Performance Implications

- **Runtime**: Gettext .mo file lookups are fast (cached)
- **Memory**: Each locale adds ~50-100KB of translation data
- **Startup**: Minimal impact (locale detection is fast)
- **Build**: Translation compilation adds ~5-10 seconds to build

### Security Considerations

- **Translation Safety**: User-provided translations could contain XSS vectors in web templates
- **Mitigation**: Always escape translated strings in templates (Jinja2 auto-escapes by default)
- **Validation**: Review all community-contributed translations before merging

### Breaking Changes

None - this is additive functionality. Default remains English.

### Migration Requirements

None - existing English users see no change.

### Future Enhancements

After initial implementation:

- Add more languages (Norwegian, Polish, Austrian German, etc.)
- Implement locale-specific Scrabble scoring (some languages use different letter values)
- Add locale-specific date/time preferences
- Support right-to-left languages (if expanding beyond European markets)
- Implement translation memory to reuse common strings
