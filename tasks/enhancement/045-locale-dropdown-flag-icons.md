# Add Country Flag Icons to Locale Dropdown

**GitHub Issue**: #507 - https://github.com/bdperkin/nhl-scrabble/issues/507

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

2-3 hours

## Description

Enhance the WebUI locale dropdown by adding appropriate country flag icons next to each language option. This improves the visual UX and makes language selection more intuitive for international users.

## Current State

The web interface locale selector displays a dropdown with text-only language options:

```html
<select name="locale" id="locale">
    <option value="en_US">English (US)</option>
    <option value="en_CA">English (Canada)</option>
    <option value="fr_CA">Français (Canada)</option>
    <option value="sv_SE">Svenska (Sweden)</option>
    <!-- ... other locales ... -->
</select>
```

Users can select their preferred locale, but there are no visual indicators (flags) to help quickly identify languages by country.

## Proposed Solution

Add Unicode flag emoji or SVG flag icons next to each locale option in the dropdown. Use the appropriate country flag for each locale:

### Flag Mapping

| Locale | Flag | Display Text                   |
| ------ | ---- | ------------------------------ |
| en_US  | 🇺🇸   | 🇺🇸 English (US)               |
| en_CA  | 🇨🇦   | 🇨🇦 English (Canada)           |
| fr_CA  | 🇨🇦   | 🇨🇦 Français (Canada)          |
| sv_SE  | 🇸🇪   | 🇸🇪 Svenska (Sweden)           |
| ru_RU  | 🇷🇺   | 🇷🇺 Русский (Russia)           |
| fi_FI  | 🇫🇮   | 🇫🇮 Suomi (Finland)            |
| cs_CZ  | 🇨🇿   | 🇨🇿 Čeština (Czech Republic)  |
| de_DE  | 🇩🇪   | 🇩🇪 Deutsch (Germany)          |
| de_CH  | 🇨🇭   | 🇨🇭 Deutsch (Switzerland)      |
| it_CH  | 🇨🇭   | 🇨🇭 Italiano (Switzerland)     |
| sk_SK  | 🇸🇰   | 🇸🇰 Slovenčina (Slovakia)     |
| lv_LV  | 🇱🇻   | 🇱🇻 Latviešu (Latvia)          |

### Implementation Approach

**Option 1: Unicode Flag Emoji (Recommended)**

Simplest approach using Unicode regional indicator symbols:

```python
# src/nhl_scrabble/i18n.py or web/app.py

LOCALE_FLAGS = {
    "en_US": "🇺🇸",
    "en_CA": "🇨🇦",
    "fr_CA": "🇨🇦",
    "sv_SE": "🇸🇪",
    "ru_RU": "🇷🇺",
    "fi_FI": "🇫🇮",
    "cs_CZ": "🇨🇿",
    "de_DE": "🇩🇪",
    "de_CH": "🇨🇭",
    "it_CH": "🇨🇭",
    "sk_SK": "🇸🇰",
    "lv_LV": "🇱🇻",
}

LOCALE_NAMES = {
    "en_US": "English (US)",
    "en_CA": "English (Canada)",
    "fr_CA": "Français (Canada)",
    "sv_SE": "Svenska (Sweden)",
    "ru_RU": "Русский (Russia)",
    "fi_FI": "Suomi (Finland)",
    "cs_CZ": "Čeština (Czech Republic)",
    "de_DE": "Deutsch (Germany)",
    "de_CH": "Deutsch (Switzerland)",
    "it_CH": "Italiano (Switzerland)",
    "sk_SK": "Slovenčina (Slovakia)",
    "lv_LV": "Latviešu (Latvia)",
}

def get_locale_display_name(locale_code: str) -> str:
    """Get display name with flag for a locale.

    Args:
        locale_code: Locale code (e.g., 'en_US', 'fr_CA')

    Returns:
        Display name with flag emoji (e.g., '🇺🇸 English (US)')
    """
    flag = LOCALE_FLAGS.get(locale_code, "")
    name = LOCALE_NAMES.get(locale_code, locale_code)
    return f"{flag} {name}" if flag else name
```

Update Jinja2 template:

```html
<!-- src/nhl_scrabble/web/templates/base.html -->
<select name="locale" id="locale" class="form-control">
    {% for locale in supported_locales %}
    <option value="{{ locale }}" {% if locale == current_locale %}selected{% endif %}>
        {{ get_locale_display_name(locale) }}
    </option>
    {% endfor %}
</select>
```

**Option 2: SVG Flag Icons**

Use a flag icon library (e.g., flag-icons, twemoji) for more consistent rendering:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/lipis/flag-icons@7.2.3/css/flag-icons.min.css" />

<select name="locale" id="locale">
    <option value="en_US">
        <span class="fi fi-us"></span> English (US)
    </option>
    <!-- ... -->
</select>
```

**Note**: Browser support for styling `<option>` elements is limited. May need custom dropdown using `<div>` + JavaScript.

## Implementation Steps

1. **Add Flag Mappings** (30 min)

   - Add `LOCALE_FLAGS` dictionary to `src/nhl_scrabble/i18n.py`
   - Add `LOCALE_NAMES` dictionary with proper language names
   - Add `get_locale_display_name()` helper function
   - Ensure proper UTF-8 encoding for emoji

2. **Update Web Templates** (1h)

   - Update `src/nhl_scrabble/web/templates/base.html` locale dropdown
   - Add flags to locale selector in all web templates
   - Test rendering in different browsers (Chrome, Firefox, Safari)
   - Consider fallback for browsers with poor emoji support

3. **Add CSS Styling** (Optional, 30 min)

   - Add CSS to ensure consistent flag size
   - Handle RTL languages if needed
   - Ensure good contrast and visibility
   - Test on mobile devices

4. **Update Documentation** (30 min)

   - Update `docs/reference/i18n.md` with flag information
   - Document flag emoji Unicode ranges
   - Add screenshots showing new dropdown UI
   - Note browser compatibility

## Testing Strategy

### Manual Testing

1. **Visual Testing**:

   - Open WebUI in different browsers (Chrome, Firefox, Safari, Edge)
   - Verify flag emoji render correctly
   - Check alignment and spacing
   - Test on different operating systems (Windows, macOS, Linux)

2. **Functional Testing**:

   - Select each locale from dropdown
   - Verify correct locale is applied
   - Ensure flag doesn't interfere with form submission
   - Test with keyboard navigation (accessibility)

3. **Mobile Testing**:

   - Test on mobile browsers (iOS Safari, Chrome Mobile)
   - Verify dropdown works on touch devices
   - Check flag rendering on small screens

### Automated Testing

```python
# tests/integration/test_web_i18n.py

def test_locale_dropdown_has_flags(client):
    """Test that locale dropdown includes flag emojis."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.data.decode("utf-8")

    # Check for flag emoji in dropdown
    assert "🇺🇸 English (US)" in html
    assert "🇨🇦 English (Canada)" in html
    assert "🇨🇦 Français (Canada)" in html
    assert "🇸🇪 Svenska (Sweden)" in html


def test_get_locale_display_name():
    """Test locale display name with flags."""
    from nhl_scrabble.i18n import get_locale_display_name

    assert get_locale_display_name("en_US") == "🇺🇸 English (US)"
    assert get_locale_display_name("fr_CA") == "🇨🇦 Français (Canada)"
    assert get_locale_display_name("sv_SE") == "🇸🇪 Svenska (Sweden)"

    # Test unknown locale
    assert get_locale_display_name("xx_XX") == "xx_XX"
```

### Browser Compatibility

Test flag emoji rendering on:

- ✅ Chrome 90+ (full emoji support)
- ✅ Firefox 88+ (full emoji support)
- ✅ Safari 14+ (full emoji support)
- ✅ Edge 90+ (full emoji support)
- ⚠️ Older browsers may show fallback characters

## Acceptance Criteria

- [x] Flag emoji added to locale dropdown in WebUI
- [x] All 12 supported locales have appropriate country flags
- [x] Flags render correctly in Chrome, Firefox, Safari, Edge
- [x] Locale selection functionality remains unchanged
- [x] Flag display is consistent across operating systems
- [x] Tests added for locale display names
- [x] Documentation updated with flag information
- [x] Mobile rendering tested and working
- [x] Keyboard accessibility maintained
- [x] All existing tests pass

## Related Files

- `src/nhl_scrabble/i18n.py` - Add `LOCALE_FLAGS`, `LOCALE_NAMES`, `get_locale_display_name()`
- `src/nhl_scrabble/web/app.py` - Pass locale display names to templates
- `src/nhl_scrabble/web/templates/base.html` - Update locale dropdown
- `tests/integration/test_web_i18n.py` - Add tests for flag display
- `docs/reference/i18n.md` - Document flag emoji usage

## Dependencies

- **Prerequisites**:
  - Task 044 (I18n Infrastructure Setup) - Completed
  - Task 021 (Web Interface Internationalization) - Completed
  - All 12 locales must be supported in the web interface

**No external dependencies** - Unicode flag emoji are part of standard UTF-8

## Additional Notes

### Unicode Flag Emoji

Flag emoji are represented using regional indicator symbols:

- 🇺🇸 = U+1F1FA (REGIONAL INDICATOR SYMBOL LETTER U) + U+1F1F8 (REGIONAL INDICATOR SYMBOL LETTER S)
- 🇨🇦 = U+1F1E8 + U+1F1E6
- etc.

These are widely supported in modern browsers and operating systems.

### Browser Compatibility

**Pros of Unicode Emoji**:

- ✅ No external dependencies
- ✅ Works offline
- ✅ Lightweight (no images to load)
- ✅ Consistent with system emoji style
- ✅ Accessible (screen readers can announce country)

**Cons**:

- ❌ Rendering varies by OS/browser
- ❌ May not display in older browsers
- ❌ Limited styling control

**If Unicode emoji prove problematic**, consider fallback to SVG icons using the `flag-icons` library.

### Accessibility Considerations

- Ensure flag emoji don't interfere with screen readers
- Keep locale code in `value` attribute for form submission
- Consider adding `aria-label` with full locale name
- Maintain keyboard navigation support

### Performance

- Flag emoji have negligible performance impact (a few bytes per character)
- No additional HTTP requests required
- No JavaScript needed for basic implementation

### Future Enhancements

- Add flag emoji to CLI `--locale` help text
- Add flags to interactive shell locale display
- Consider custom dropdown UI with better flag rendering
- Add language-specific sorting (e.g., by region)

## Implementation Notes

*To be filled during implementation*
