# Add Plugin System

**GitHub Issue**: #156 - https://github.com/bdperkin/nhl-scrabble/issues/156

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

10-14 hours

## Description

Add plugin system for extending functionality with custom scorers, reports, and exporters.

## Proposed Solution

```python
# Plugin API
class Plugin:
    def register_scorer(self, name: str, scorer: Callable):
        pass

    def register_report(self, name: str, report_class: Type[BaseReport]):
        pass
```

```bash
# Install plugin
nhl-scrabble plugin install my-custom-scorer

# Use plugin
nhl-scrabble analyze --scorer custom
```

## Acceptance Criteria

- [ ] Plugin loading working
- [ ] Plugin registration working
- [ ] Example plugins created
- [ ] Tests pass

## Related Files

- `src/nhl_scrabble/plugins/`

## Dependencies

None

## Implementation Notes

*To be filled during implementation*
