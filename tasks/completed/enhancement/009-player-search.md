# Add Player Search Functionality

**GitHub Issue**: #149 - https://github.com/bdperkin/nhl-scrabble/issues/149

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

3-4 hours

## Description

Add player search functionality to quickly find and display Scrabble scores for specific players by name.

Currently must scan full reports to find specific players.

## Proposed Solution

```bash
# Search by exact name
nhl-scrabble search "Connor McDavid"

# Fuzzy search
nhl-scrabble search McDavid

# Search with wildcards
nhl-scrabble search "Connor*"

# Search with score threshold
nhl-scrabble search --min-score 50
```

```python
from difflib import get_close_matches


class PlayerSearch:
    def search(self, query: str, fuzzy: bool = True):
        all_players = self.get_all_players()

        if fuzzy:
            names = [p.name for p in all_players]
            matches = get_close_matches(query, names, n=10, cutoff=0.6)
            return [p for p in all_players if p.name in matches]
        else:
            return [p for p in all_players if query.lower() in p.name.lower()]
```

## Implementation Steps

1. Implement player search
1. Add fuzzy matching
1. Add CLI search command
1. Add tests
1. Update documentation

## Acceptance Criteria

- [ ] Exact search works
- [ ] Fuzzy search works
- [ ] Wildcard search works
- [ ] Score filtering works
- [ ] Tests pass
- [ ] Documentation updated

## Related Files

- `src/nhl_scrabble/search.py` - New module
- `src/nhl_scrabble/cli.py` - Add search command

## Dependencies

None (uses difflib from stdlib)

## Additional Notes

**Benefits**: Quick player lookup, better UX, convenient queries

## Implementation Notes

*To be filled during implementation*
