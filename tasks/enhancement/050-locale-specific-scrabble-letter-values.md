# Implement Locale-Specific Scrabble Letter Values

**GitHub Issue**: #523 - https://github.com/bdperkin/nhl-scrabble/issues/523

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

8-12 hours

## Description

Implement locale-specific Scrabble letter values to more accurately reflect letter rarity and point values in different languages. Currently all locales use English Scrabble letter values, which disadvantages players with names containing letters rare in English but common in other languages (and vice versa).

## Current State

All locales use English Scrabble letter values:
```python
# src/nhl_scrabble/scoring/scrabble_scorer.py
LETTER_VALUES = {
    'A': 1, 'E': 1, 'I': 1, 'O': 1, 'U': 1, 'L': 1, 'N': 1, 'S': 1, 'T': 1, 'R': 1,
    'D': 2, 'G': 2,
    'B': 3, 'C': 3, 'M': 3, 'P': 3,
    'F': 4, 'H': 4, 'V': 4, 'W': 4, 'Y': 4,
    'K': 5,
    'J': 8, 'X': 8,
    'Q': 10, 'Z': 10
}
```

**Problems:**
- Czech 'Č', 'Š', 'Ž' not valued appropriately
- Swedish 'Å', 'Ä', 'Ö' not valued
- Russian Cyrillic letters not valued at all (default to 0)
- French 'É', 'È', 'Ê' treated as 'E' (1 point) incorrectly
- German 'Ä', 'Ö', 'Ü', 'ß' not valued
- Unfair comparison across locales

## Proposed Solution

Implement locale-aware Scrabble scoring using official Scrabble letter values for each supported locale.

### Architecture

```python
# src/nhl_scrabble/scoring/letter_values.py

from typing import Dict

# English (en_US, en_CA)
LETTER_VALUES_EN = {
    'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4, 'I': 1,
    'J': 8, 'K': 5, 'L': 1, 'M': 3, 'N': 1, 'O': 1, 'P': 3, 'Q': 10, 'R': 1,
    'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 4, 'X': 8, 'Y': 4, 'Z': 10,
}

# French (fr_CA)
LETTER_VALUES_FR = {
    'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4, 'I': 1,
    'J': 8, 'K': 10, 'L': 1, 'M': 2, 'N': 1, 'O': 1, 'P': 3, 'Q': 8, 'R': 1,
    'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 10, 'X': 10, 'Y': 10, 'Z': 10,
}

# Swedish (sv_SE)
LETTER_VALUES_SV = {
    'A': 1, 'B': 3, 'C': 8, 'D': 1, 'E': 1, 'F': 3, 'G': 2, 'H': 2, 'I': 1,
    'J': 7, 'K': 2, 'L': 1, 'M': 2, 'N': 1, 'O': 2, 'P': 4, 'Q': 10, 'R': 1,
    'S': 1, 'T': 1, 'U': 3, 'V': 3, 'W': 8, 'X': 8, 'Y': 7, 'Z': 10,
    'Å': 4, 'Ä': 3, 'Ö': 4,
}

# Russian (ru_RU)
LETTER_VALUES_RU = {
    'А': 1, 'Б': 3, 'В': 1, 'Г': 3, 'Д': 2, 'Е': 1, 'Ё': 5, 'Ж': 5, 'З': 5,
    'И': 1, 'Й': 4, 'К': 2, 'Л': 2, 'М': 2, 'Н': 1, 'О': 1, 'П': 2, 'Р': 1,
    'С': 1, 'Т': 1, 'У': 2, 'Ф': 10, 'Х': 5, 'Ц': 10, 'Ч': 5, 'Ш': 8, 'Щ': 10,
    'Ъ': 10, 'Ы': 4, 'Ь': 5, 'Э': 8, 'Ю': 8, 'Я': 3,
}

# Finnish (fi_FI)
LETTER_VALUES_FI = {
    'A': 1, 'D': 7, 'E': 1, 'F': 8, 'G': 8, 'H': 4, 'I': 1, 'J': 4, 'K': 2,
    'L': 2, 'M': 3, 'N': 1, 'O': 2, 'P': 4, 'R': 2, 'S': 1, 'T': 1, 'U': 3,
    'V': 4, 'Y': 4, 'Ä': 2, 'Ö': 7,
}

# Czech (cs_CZ)
LETTER_VALUES_CS = {
    'A': 1, 'B': 3, 'C': 2, 'Č': 4, 'D': 1, 'Ď': 8, 'E': 1, 'É': 3, 'Ě': 3,
    'F': 5, 'G': 3, 'H': 2, 'Ch': 2, 'I': 1, 'Í': 2, 'J': 2, 'K': 1, 'L': 1,
    'M': 3, 'N': 1, 'Ň': 6, 'O': 1, 'Ó': 7, 'P': 1, 'Q': 10, 'R': 1, 'Ř': 4,
    'S': 1, 'Š': 4, 'T': 1, 'Ť': 7, 'U': 2, 'Ú': 5, 'Ů': 4, 'V': 1, 'W': 10,
    'X': 10, 'Y': 2, 'Ý': 4, 'Z': 2, 'Ž': 4,
}

# German (de_DE, de_CH)
LETTER_VALUES_DE = {
    'A': 1, 'Ä': 6, 'B': 3, 'C': 4, 'D': 1, 'E': 1, 'F': 4, 'G': 2, 'H': 2,
    'I': 1, 'J': 6, 'K': 4, 'L': 2, 'M': 3, 'N': 1, 'O': 2, 'Ö': 8, 'P': 4,
    'Q': 10, 'R': 1, 'S': 1, 'T': 1, 'U': 1, 'Ü': 6, 'V': 6, 'W': 3, 'X': 8,
    'Y': 10, 'Z': 3,
}

# Italian (it_CH)
LETTER_VALUES_IT = {
    'A': 1, 'B': 5, 'C': 1, 'D': 5, 'E': 1, 'F': 5, 'G': 8, 'H': 8, 'I': 1,
    'L': 3, 'M': 3, 'N': 3, 'O': 1, 'P': 5, 'Q': 10, 'R': 1, 'S': 1, 'T': 1,
    'U': 3, 'V': 5, 'Z': 8,
}

# Slovak (sk_SK)
LETTER_VALUES_SK = {
    'A': 1, 'Á': 4, 'Ä': 7, 'B': 3, 'C': 3, 'Č': 7, 'D': 2, 'Ď': 8, 'DZ': 8,
    'DŽ': 8, 'E': 1, 'É': 4, 'F': 8, 'G': 4, 'H': 3, 'CH': 5, 'I': 1, 'Í': 2,
    'J': 2, 'K': 1, 'L': 1, 'Ĺ': 5, 'Ľ': 5, 'M': 3, 'N': 1, 'Ň': 6, 'O': 1,
    'Ó': 5, 'Ô': 7, 'P': 2, 'Q': 10, 'R': 1, 'Ŕ': 4, 'S': 1, 'Š': 4, 'T': 1,
    'Ť': 7, 'U': 3, 'Ú': 5, 'V': 3, 'W': 10, 'X': 10, 'Y': 3, 'Ý': 4, 'Z': 4,
    'Ž': 4,
}

# Latvian (lv_LV) - Based on letter frequency in Latvian
LETTER_VALUES_LV = {
    'A': 1, 'Ā': 4, 'B': 8, 'C': 6, 'Č': 8, 'D': 3, 'E': 1, 'Ē': 5, 'F': 10,
    'G': 5, 'Ģ': 10, 'H': 10, 'I': 1, 'Ī': 4, 'J': 2, 'K': 2, 'Ķ': 6, 'L': 2,
    'Ļ': 5, 'M': 3, 'N': 2, 'Ņ': 5, 'O': 4, 'P': 4, 'R': 1, 'S': 1, 'Š': 6,
    'T': 1, 'U': 2, 'Ū': 4, 'V': 3, 'Z': 2, 'Ž': 6,
}

LOCALE_LETTER_VALUES: Dict[str, Dict[str, int]] = {
    'en_US': LETTER_VALUES_EN,
    'en_CA': LETTER_VALUES_EN,
    'fr_CA': LETTER_VALUES_FR,
    'sv_SE': LETTER_VALUES_SV,
    'ru_RU': LETTER_VALUES_RU,
    'fi_FI': LETTER_VALUES_FI,
    'cs_CZ': LETTER_VALUES_CS,
    'de_DE': LETTER_VALUES_DE,
    'de_CH': LETTER_VALUES_DE,
    'it_CH': LETTER_VALUES_IT,
    'sk_SK': LETTER_VALUES_SK,
    'lv_LV': LETTER_VALUES_LV,
}
```

### Updated Scorer

```python
# src/nhl_scrabble/scoring/scrabble_scorer.py

from nhl_scrabble.scoring.letter_values import LOCALE_LETTER_VALUES, LETTER_VALUES_EN
from nhl_scrabble.i18n import get_system_locale

class ScrabbleScorer:
    """Calculate Scrabble scores for player names with locale support."""

    def __init__(self, locale: str | None = None):
        """Initialize scorer with locale-specific letter values.

        Args:
            locale: Locale code (e.g., 'fr_CA'). If None, uses system locale.
        """
        if locale is None:
            locale = get_system_locale()

        self.locale = locale
        self.letter_values = LOCALE_LETTER_VALUES.get(locale, LETTER_VALUES_EN)

    def calculate_score(self, name: str) -> int:
        """Calculate Scrabble score for a name using locale letter values."""
        return sum(
            self.letter_values.get(char.upper(), 0)
            for char in name if char.isalpha()
        )
```

## Implementation Steps

1. **Research Official Letter Values**:
   - Verify values from official Scrabble editions for each locale
   - Sources:
     - English: Hasbro/Mattel Scrabble
     - French: Scrabble Francophone
     - Swedish: Alfapet (Swedish Scrabble)
     - Russian: Эрудит (Russian Scrabble)
     - Finnish: Scrabble Suomi
     - Czech: Scrabble Czech edition
     - German: Scrabble Deutsch
     - Italian: Scrabble Italiano
     - Slovak: Scrabble Slovak edition
     - Latvian: Estimated from letter frequency

2. **Create Letter Values Module**:
   - Create `src/nhl_scrabble/scoring/letter_values.py`
   - Define `LETTER_VALUES_XX` for each locale
   - Define `LOCALE_LETTER_VALUES` mapping

3. **Update ScrabbleScorer**:
   - Add `locale` parameter to `__init__`
   - Load locale-specific letter values
   - Update `calculate_score` to use locale values
   - Maintain backward compatibility (default to English)

4. **Update CLI**:
   ```python
   @click.option(
       '--scoring-locale',
       type=click.Choice(SUPPORTED_LOCALES),
       help='Locale for Scrabble letter values (default: system locale)'
   )
   def analyze(scoring_locale: str | None):
       scorer = ScrabbleScorer(locale=scoring_locale)
       # ...
   ```

5. **Update Reports**:
   - Show scoring locale in report headers
   - Add note about locale-specific scoring

6. **Add Tests**:
   ```python
   def test_scrabble_scorer_locale_specific():
       # English
       scorer_en = ScrabbleScorer('en_US')
       assert scorer_en.calculate_score('Ö') == 0  # Not in English

       # Swedish
       scorer_sv = ScrabbleScorer('sv_SE')
       assert scorer_sv.calculate_score('Ö') == 4  # Swedish letter value

       # Russian
       scorer_ru = ScrabbleScorer('ru_RU')
       assert scorer_ru.calculate_score('Овечкин') > 0  # Cyrillic valued
   ```

7. **Documentation**:
   - Update docs/explanation/why-scrabble-scoring.md
   - Document locale-specific scoring
   - Add letter value tables for each locale
   - Explain fairness improvements

## Testing Strategy

1. **Unit Tests**:
   - Test each locale's letter values
   - Test scoring with accented characters
   - Test scoring with Cyrillic
   - Test fallback to English

2. **Integration Tests**:
   - Test CLI with `--scoring-locale`
   - Test Web UI locale selection
   - Test TUI locale switching

3. **Comparison Tests**:
   ```python
   def test_locale_fairness():
       player_ovechkin = "Alexander Ovechkin"

       # English scoring (unfair to Russian letters)
       scorer_en = ScrabbleScorer('en_US')
       score_en = scorer_en.calculate_score(player_ovechkin)

       # Russian scoring (values Cyrillic properly)
       scorer_ru = ScrabbleScorer('ru_RU')
       score_ru_latin = scorer_ru.calculate_score(player_ovechkin)  # Latinized name
       score_ru_cyrillic = scorer_ru.calculate_score("Александр Овечкин")  # Cyrillic

       # Cyrillic should have non-zero score with Russian locale
       assert score_ru_cyrillic > 0
   ```

## Acceptance Criteria

- [ ] Letter values module created with all 12 locales
- [ ] ScrabbleScorer supports locale parameter
- [ ] CLI has `--scoring-locale` option
- [ ] Web UI allows scoring locale selection
- [ ] TUI supports locale switching for scoring
- [ ] All locales use official Scrabble letter values
- [ ] Cyrillic letters valued correctly in ru_RU
- [ ] Accented characters valued correctly in all locales
- [ ] Tests cover all 12 locales
- [ ] Documentation updated with letter value tables
- [ ] Backward compatibility maintained (defaults to system locale)
- [ ] Reports show which scoring locale was used

## Related Files

- `src/nhl_scrabble/scoring/letter_values.py` - New letter values module
- `src/nhl_scrabble/scoring/scrabble_scorer.py` - Updated scorer
- `src/nhl_scrabble/cli.py` - Add --scoring-locale option
- `src/nhl_scrabble/web/app.py` - Add locale selector for scoring
- `src/nhl_scrabble/ui/tui.py` - Add locale switcher
- `tests/unit/test_scrabble_scorer.py` - Updated tests
- `docs/explanation/why-scrabble-scoring.md` - Updated docs

## Dependencies

- Task 044: I18n infrastructure - COMPLETE
- Research official Scrabble editions for each locale

## Additional Notes

### Letter Value Sources

**Official Scrabble Editions:**
- **English**: Hasbro Scrabble (North America), Mattel Scrabble (International)
- **French**: Scrabble Francophone (identical to English except K=10, W=10, Y=10)
- **Swedish**: Alfapet (Swedish Scrabble variant)
- **Russian**: Эрудит (Russian Scrabble)
- **Finnish**: Scrabble Suomi
- **Czech**: Scrabble (Czech edition with diacritics)
- **German**: Scrabble Deutsch (with Ä, Ö, Ü)
- **Italian**: Scrabble Italiano (no J, K, W, X, Y)
- **Slovak**: Scrabble (Slovak edition)
- **Latvian**: Based on letter frequency analysis (no official Scrabble edition)

### Fairness Examples

**Before (English-only scoring):**
```
# Ovechkin (Овечкин) in Cyrillic - 0 points (letters not recognized)
# Forsberg (Swedish Å) - 'Å' worth 0 points
# Hašek (Czech Š) - 'Š' worth 0 points
```

**After (Locale-specific scoring):**
```
# ru_RU locale: Овечкин - proper Cyrillic point values
# sv_SE locale: Forsberg with Å - Å worth 4 points
# cs_CZ locale: Hašek with Š - Š worth 4 points
```

### Configuration

Add to `pyproject.toml`:
```toml
[tool.nhl-scrabble.scoring]
# Default scoring locale (uses system locale if not set)
# locale = "en_US"

# Show scoring locale in reports
show_locale = true
```

### Performance

Letter value lookups are O(1) dictionary lookups - no performance impact.

### Future Enhancements

- **Multi-alphabet scoring**: Score names in both Latin and native scripts (e.g., Ovechkin + Овечкин)
- **Weighted scoring**: Combine locale weights for international teams
- **Custom values**: Allow users to define custom letter values
- **Tile frequency**: Consider tile distribution, not just point values

### Community Input

After implementation, seek feedback from international users:
- Are letter values accurate?
- Should we use Scrabble values or letter frequency?
- Any cultural considerations we missed?

## Implementation Notes

*To be filled during implementation:*
- Letter value sources verified
- Locale-specific testing results
- Community feedback received
- Challenges encountered
- Actual effort vs estimated
