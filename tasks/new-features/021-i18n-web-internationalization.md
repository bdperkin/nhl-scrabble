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
<h1>NHL Scrabble Scores</h1>
<p>Analyzing player names by Scrabble values</p>
<table>
  <thead>
    <tr>
      <th>Team</th>
      <th>Score</th>
      <th>Players</th>
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
    "flask-babel>=4.0.0",  # Add this
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
    locale = request.args.get('lang')
    if locale in SUPPORTED_LOCALES:
        return locale

    # Try browser Accept-Language header
    return request.accept_languages.best_match(SUPPORTED_LOCALES)
```

### 3. Wrap Template Strings

```html
<!-- templates/index.html -->
<h1>{% trans %}NHL Scrabble Scores{% endtrans %}</h1>
<p>{% trans %}Analyzing player names by Scrabble values{% endtrans %}</p>

<table>
  <thead>
    <tr>
      <th>{% trans %}Team{% endtrans %}</th>
      <th>{% trans %}Score{% endtrans %}</th>
      <th>{% trans %}Players{% endtrans %}</th>
    </tr>
  </thead>
</table>
```

### 4. Add Language Selector

```html
<!-- templates/base.html -->
<nav>
  <select id="language-selector" onchange="changeLanguage(this.value)">
    <option value="en_US" {% if get_locale() == 'en_US' %}selected{% endif %}>
      English (US)
    </option>
    <option value="fr_CA" {% if get_locale() == 'fr_CA' %}selected{% endif %}>
      Français (Canada)
    </option>
    <option value="sv_SE" {% if get_locale() == 'sv_SE' %}selected{% endif %}>
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

- [ ] Flask-Babel installed and configured
- [ ] Jinja2 i18n extension enabled
- [ ] All template strings wrapped with {% trans %}
- [ ] Language selector in UI
- [ ] Locale detection from Accept-Language header
- [ ] URL parameter ?lang= support
- [ ] Web strings extracted to messages.pot
- [ ] Tests pass for all locales
- [ ] Documentation updated

## Related Files

- `src/nhl_scrabble/web/app.py` - Flask-Babel configuration
- `src/nhl_scrabble/web/templates/` - All templates
- `src/nhl_scrabble/locales/` - Translation files
- `tests/integration/test_web_i18n.py` - New tests

## Dependencies

- **Prerequisite**: Sub-task 1 (I18n Infrastructure) must be completed
- **Parent Task**: #218 - Internationalization and Localization

## Implementation Notes

*To be filled during implementation*
