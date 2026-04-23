# Add Database Backend for Data Persistence

**GitHub Issue**: #151 - https://github.com/bdperkin/nhl-scrabble/issues/151

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

12-16 hours

## Description

Add database backend (SQLite/PostgreSQL) for persisting historical data, caching API responses, and enabling advanced queries.

## Proposed Solution

```python
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    team = Column(String)
    score = Column(Integer)
    season = Column(String)
    updated_at = Column(DateTime)
```

```bash
# Initialize database
nhl-scrabble db init

# Store current season data
nhl-scrabble db sync

# Query database
nhl-scrabble db query --sql "SELECT * FROM players WHERE score > 50"
```

## Implementation Steps

1. Add SQLAlchemy
1. Define database models
1. Implement migrations
1. Add CLI database commands
1. Add tests
1. Update documentation

## Acceptance Criteria

- [ ] Database models defined
- [ ] Migrations system working
- [ ] CLI commands added
- [ ] Tests pass
- [ ] Documentation updated

## Related Files

- `src/nhl_scrabble/db/` - New module

## Dependencies

- `sqlalchemy` (new)
- `alembic` (migrations)

## Additional Notes

**Benefits**: Historical queries, faster analysis, complex filtering

## Implementation Notes

*To be filled during implementation*
