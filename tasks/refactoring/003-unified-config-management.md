# Unified Configuration Management

**GitHub Issue**: #161 - https://github.com/bdperkin/nhl-scrabble/issues/161

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

5-6 hours

## Description

Consolidate configuration sources (env vars, files, CLI args) into single unified config system with clear precedence.

## Proposed Solution

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_timeout: int = 10
    rate_limit_delay: float = 0.3

    class Config:
        env_prefix = "NHL_SCRABBLE_"
        env_file = ".env"
        case_sensitive = False


# Precedence: CLI args > env vars > config file > defaults
```

## Acceptance Criteria

- [ ] Unified config class created
- [ ] Clear precedence order
- [ ] All config sources supported
- [ ] Tests pass

## Related Files

- `src/nhl_scrabble/config.py`

## Dependencies

- `pydantic-settings` (already have pydantic)

## Implementation Notes

*To be filled during implementation*
