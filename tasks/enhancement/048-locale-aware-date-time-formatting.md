# Locale-Aware Date and Time Formatting

**GitHub Issue**: #511 - https://github.com/bdperkin/nhl-scrabble/issues/511

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

3-4 hours

## Description

Add comprehensive locale-aware date and time formatting throughout the application using babel.dates module. Currently uses default formatting which doesn't respect locale preferences for date order (MM/DD/YYYY vs DD/MM/YYYY), time format (12-hour vs 24-hour), and display conventions.

## Current State

Default date/time formatting:
```python
# Currently uses Python's default formatting
datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Always YYYY-MM-DD HH:MM:SS
```

**Issues**:
- No locale-specific formatting
- Always uses ISO 8601 format
- Doesn't respect cultural preferences
- No timezone handling

## Proposed Solution

Implement locale-aware formatting using babel.dates:

```python
from babel.dates import format_datetime, format_date, format_time
from nhl_scrabble.i18n import get_system_locale

def format_localized_datetime(dt, locale=None, format='medium'):
    """Format datetime according to locale preferences.

    Args:
        dt: datetime object
        locale: Locale code (default: system locale)
        format: 'full', 'long', 'medium', 'short'

    Returns:
        Formatted date/time string
    """
    if locale is None:
        locale = get_system_locale()

    return format_datetime(dt, format=format, locale=locale)
```

### Format Examples by Locale

| Locale | Short Date | Long Date | Short Time | Long Time |
|--------|-----------|-----------|------------|-----------|
| en_US | 1/15/26 | January 15, 2026 | 2:30 PM | 2:30:45 PM EST |
| en_CA | 2026-01-15 | January 15, 2026 | 14:30 | 14:30:45 EST |
| fr_CA | 2026-01-15 | 15 janvier 2026 | 14 h 30 | 14 h 30 min 45 s |
| sv_SE | 2026-01-15 | 15 januari 2026 | 14:30 | 14:30:45 |
| de_DE | 15.01.26 | 15. Januar 2026 | 14:30 | 14:30:45 |

## Implementation Steps

1. **Add Formatting Functions** to `src/nhl_scrabble/i18n.py`:
   - `format_date(date, locale, format)`
   - `format_time(time, locale, format)`
   - `format_datetime(dt, locale, format)`

2. **Update CLI Module** (`src/nhl_scrabble/cli.py`):
   - Replace all `strftime()` calls
   - Use localized formatting

3. **Update Web Templates** (`src/nhl_scrabble/web/templates/`):
   - Add Jinja2 filters for date/time
   - Use babel's template integration

4. **Update Reports** (`src/nhl_scrabble/reports/`):
   - Format timestamps in reports
   - Use appropriate format level (short for tables, long for headers)

5. **Add Tests**:
   - Test each format level (full, long, medium, short)
   - Test all 12 locales
   - Verify timezone handling

## Testing Strategy

```python
# tests/unit/test_i18n_datetime.py
from nhl_scrabble.i18n import format_localized_datetime
from datetime import datetime

def test_format_datetime_en_us():
    dt = datetime(2026, 1, 15, 14, 30, 45)
    result = format_localized_datetime(dt, 'en_US', 'short')
    assert '1/15/26' in result or '1/15/2026' in result

def test_format_datetime_fr_ca():
    dt = datetime(2026, 1, 15, 14, 30, 45)
    result = format_localized_datetime(dt, 'fr_CA', 'long')
    assert 'janvier' in result.lower()
```

## Acceptance Criteria

- [ ] babel.dates module integrated
- [ ] Formatting functions added to i18n.py
- [ ] All CLI date/time displays use localized formatting
- [ ] All Web templates use localized formatting
- [ ] All Reports use localized formatting
- [ ] Tests for all 12 locales pass
- [ ] Timezone handling works correctly
- [ ] Documentation updated

## Related Files

- `src/nhl_scrabble/i18n.py` - Add formatting functions
- `src/nhl_scrabble/cli.py` - Update CLI output
- `src/nhl_scrabble/web/templates/` - Update templates
- `src/nhl_scrabble/reports/` - Update report formatting
- `tests/unit/test_i18n_datetime.py` - New test file

## Dependencies

- babel>=2.14.0 (already installed)
- Task 044: I18n infrastructure - COMPLETE

## Additional Notes

### Babel Date/Time Formats

- **full**: "Wednesday, January 15, 2026 at 2:30:45 PM Eastern Standard Time"
- **long**: "January 15, 2026 at 2:30:45 PM EST"
- **medium**: "Jan 15, 2026, 2:30:45 PM"
- **short**: "1/15/26, 2:30 PM"

### Cultural Considerations

- **US/CA**: AM/PM vs 24-hour preference varies
- **Europe**: Almost exclusively 24-hour format
- **Date separators**: / vs - vs . varies by locale
- **Month names**: Must be translated via locale

### Performance

- babel.dates caching: Results are automatically cached
- Minimal overhead: < 1ms per format call
