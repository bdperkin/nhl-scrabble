# Web Interface Internationalization Implementation

**GitHub Issue**: #249 - https://github.com/bdperkin/nhl-scrabble/issues/249

**Parent Task**: #218 - Internationalization and Localization (sub-task 3 of 6)

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

6-8 hours

## Description

Internationalize the web interface by enabling Jinja2 i18n extension, adding Flask-Babel for locale detection, wrapping all template strings with `{% trans %}` tags, and implementing a language selector in the UI. This is the third sub-task of the comprehensive i18n/l10n implementation.

**Parent Task**: tasks/new-features/016-internationalization-localization.md

## Current State

Web templates are hardcoded in English:

```html
<!-- templates/index.html -->
<h1>
 NHL Scrabble Scores
</h1>
<p>
 Analyzing player names by Scrabble values
</p>
<table>
 <thead>
  <tr>
   <th>
    Team
   </th>
   <th>
    Score
   </th>
   <th>
    Players
   </th>
  </tr>
 </thead>
</table>
```

## Proposed Solution

### 1. Install Flask-Babel

```toml
[project.optional-dependencies]
web = [
  "fastapi>=0.104.0",
  "jinja2>=3.1.2",
  "flask-babel>=4.0.0", # Add this
]
```

### 2. Enable Jinja2 I18n Extension

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
    locale = request.args.get("lang")
    if locale in SUPPORTED_LOCALES:
        return locale

    # Try browser Accept-Language header
    return request.accept_languages.best_match(SUPPORTED_LOCALES)
```

### 3. Wrap Template Strings

```html
<!-- templates/index.html -->
<h1>
 {% trans %}NHL Scrabble Scores{% endtrans %}
</h1>
<p>
 {% trans %}Analyzing player names by Scrabble values{% endtrans %}
</p>
<table>
 <thead>
  <tr>
   <th>
    {% trans %}Team{% endtrans %}
   </th>
   <th>
    {% trans %}Score{% endtrans %}
   </th>
   <th>
    {% trans %}Players{% endtrans %}
   </th>
  </tr>
 </thead>
</table>
```

### 4. Add Language Selector

```html
<!-- templates/base.html -->
<nav>
 <select id="language-selector" onchange="changeLanguage(this.value)">
  <option %}="" %}selected{%="" 'en_us'="" endif="" get_locale()="=" if="" value="en_US" {%="">
   English (US)
  </option>
  <option %}="" %}selected{%="" 'fr_ca'="" endif="" get_locale()="=" if="" value="fr_CA" {%="">
   Français (Canada)
  </option>
  <option %}="" %}selected{%="" 'sv_se'="" endif="" get_locale()="=" if="" value="sv_SE" {%="">
   Svenska
  </option>
  <!-- Other locales -->
 </select>
</nav>
<script>
 function changeLanguage(locale) {
    const url = new URL(window.location);
    url.searchParams.set('lang', locale);
    window.location = url;
}
</script>
```

## Implementation Steps

1. **Install Flask-Babel** (30 min)
1. **Enable Jinja2 I18n** (1h)
1. **Wrap All Template Strings** (3-4h)
1. **Add Language Selector** (1h)
1. **Extract Web Strings** (30 min)
1. **Testing** (1-2h)
1. **Documentation** (30 min)

## Acceptance Criteria

- [x] Flask-Babel installed and configured
- [x] Jinja2 i18n extension enabled
- [x] Core template strings wrapped with {% trans %} (base.html, index.html, results.html)
- [ ] Remaining templates wrapped (teams.html, divisions.html, conferences.html, playoffs.html, stats.html)
- [x] Language selector in UI
- [x] Locale detection from Accept-Language header
- [x] URL parameter ?lang= support
- [x] Web strings extracted to messages.pot
- [x] Tests pass for all locales (14/14 passing)
- [x] Documentation updated (docs/reference/i18n.md)

## Related Files

- `src/nhl_scrabble/web/app.py` - Flask-Babel configuration
- `src/nhl_scrabble/web/templates/` - All templates
- `src/nhl_scrabble/locales/` - Translation files
- `tests/integration/test_web_i18n.py` - New tests

## Dependencies

- **Prerequisite**: Sub-task 1 (I18n Infrastructure) must be completed
- **Parent Task**: #218 - Internationalization and Localization

## Implementation Notes

**Implementation Date**: 2026-05-06
**Branch**: new-features/021-i18n-web-internationalization
**Status**: Mostly Complete (Core functionality working, some templates pending)

### What Was Implemented

**1. Flask-Babel Integration** ✅
- Installed flask-babel>=4.0.0 in i18n optional dependencies
- Configured Jinja2 i18n extension in FastAPI app
- Implemented locale detection from:
  - URL query parameter (?lang=fr_CA)
  - HTTP Accept-Language header
  - Default fallback to en_US

**2. Template Internationalization** ⚠️ Partially Complete
- **Completed Templates**:
  - `base.html` - 24 trans tags (navigation, header, footer, language selector)
  - `index.html` - 29 trans tags (hero section, form labels, help text, info section)
  - `results.html` - 30 trans tags (table headers, buttons, stats labels)
- **Pending Templates**:
  - `teams.html` - 0 trans tags (78 lines)
  - `divisions.html` - 0 trans tags (44 lines)
  - `conferences.html` - 0 trans tags (44 lines)
  - `playoffs.html` - 0 trans tags (73 lines)
  - `stats.html` - 0 trans tags (124 lines)

**3. Language Selector** ✅
- Dropdown selector in base.html with all 12 supported locales
- JavaScript function to change language via URL parameter
- Selected locale marked in dropdown
- Preserves locale across navigation

**4. Translation Files** ✅
- French Canadian (fr_CA): 25+ translations added
- Swedish (sv_SE): Basic structure in place
- English US (en_US): Source locale
- Compiled .mo files properly ignored in git, built during package build

**5. Build System** ✅
- Created `scripts/hatch_build.py` custom build hook
- Compiles .po → .mo during package build
- Added babel>=2.14.0 to build-system requirements
- Updated .gitignore to exclude *.mo files

**6. Testing** ✅
- 14 integration tests in `tests/integration/test_web_i18n.py`
- All tests passing (100%)
- Tests cover:
  - Locale detection (query param, Accept-Language header)
  - Template rendering with locales
  - Language selector presence and functionality
  - API endpoints with locale support

**7. Bug Fixes During Implementation**
- Fixed mypy type errors for Jinja2 i18n extension (added type: ignore comments)
- Fixed language parameter not retained in navigation links
- Fixed header title link not preserving ?lang parameter
- Updated visual regression test baselines for i18n changes
- Fixed codespell errors for French words (added "mis" to ignore list)

### Technical Decisions

**1. FastAPI vs Flask-Babel**
- Project uses FastAPI, not Flask
- Adapted Flask-Babel pattern to FastAPI using:
  - Direct gettext.translation() calls
  - Jinja2 Environment.install_gettext_translations()
  - Custom locale detection in dependency injection

**2. Locale Detection Priority**
1. URL parameter (?lang=xx_YY) - Highest priority
2. Accept-Language header - Second priority
3. Default locale (en_US) - Fallback

**3. Translation File Management**
- .po files tracked in git (source files)
- .mo files ignored, compiled during build
- Follows Python packaging best practices

### Known Issues / Technical Debt

1. **Incomplete Template Coverage**
   - 5 templates still need {% trans %} tags
   - Estimated 2-3 hours to complete
   - Non-blocking: Core functionality works

2. **Translation Coverage**
   - Only French Canadian has full translations
   - Other locales have structure but English fallback
   - Need translation contributions for: sv_SE, fi_FI, cs_CZ, de_DE, de_CH, it_CH, sk_SK, ru_RU, lv_LV

### Performance Impact

- Minimal: Translation lookup is cached
- .mo files loaded once per locale
- No measurable performance degradation in tests

### Documentation

- Updated `docs/reference/i18n.md` with web interface examples
- Includes Jinja2 template usage
- Documents locale detection mechanism

### Next Steps

To fully complete this task:
1. Add {% trans %} tags to remaining 5 templates
2. Extract new strings with `pybabel extract`
3. Update .po files with `pybabel update`
4. Get translation contributions for other locales
5. Re-run visual regression tests if template changes significant

### Test Results

```
tests/integration/test_web_i18n.py::14 tests PASSED
- TestLocaleDetection: 5 tests ✓
- TestTemplateRendering: 5 tests ✓
- TestAPIEndpoints: 2 tests ✓
- TestGetRequestLocale: 2 tests ✓
```

Overall test suite: 1627 passed, 90.13% coverage
