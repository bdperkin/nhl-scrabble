# Add Custom Scoring Rules

**GitHub Issue**: #146 - https://github.com/bdperkin/nhl-scrabble/issues/146

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

3-4 hours

## Description

Allow users to define custom letter point values for alternative scoring systems (e.g., Wordle scoring, custom weights).

Currently locked to standard Scrabble values. Users cannot experiment with alternative scoring.

## Proposed Solution

```bash
# Use custom scoring file
nhl-scrabble analyze --scoring-config custom_values.json

# Built-in alternatives
nhl-scrabble analyze --scoring wordle  # Wordle-style scoring
nhl-scrabble analyze --scoring uniform # All letters worth 1 point
```

```json
// custom_values.json
{
  "A": 5, "B": 2, "C": 2, "D": 1,
  "E": 10, "I": 8, ...
}
```

## Implementation Steps

1. Create scoring config loader
1. Add CLI options
1. Support multiple scoring systems
1. Add tests
1. Update documentation

## Acceptance Criteria

- [ ] Custom scoring configs supported
- [ ] Built-in alternatives included
- [ ] CLI options added
- [ ] Tests pass
- [ ] Documentation updated

## Related Files

- `src/nhl_scrabble/scoring/config.py` - New module
- `src/nhl_scrabble/cli.py` - Add options

## Dependencies

None

## Additional Notes

**Benefits**: Experimental analysis, fun variations, educational use

## Implementation Notes

*To be filled during implementation*
