# Add to_dict() Methods to Dataclasses for Fast JSON Serialization

**GitHub Issue**: #117 - https://github.com/bdperkin/nhl-scrabble/issues/117

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

2-3 hours

## Description

Current JSON generation uses `dataclasses.asdict()` which uses reflection to convert dataclass instances to dictionaries. This is slow for large datasets. Adding explicit `to_dict()` methods provides 2-3x faster serialization by avoiding reflection overhead.

**Impact**: 2-3x faster JSON serialization

**ROI**: Medium - moderate code changes, significant speedup for JSON output

## Current State

**cli.py (lines 320-354)** uses `asdict()` for JSON serialization:

```python
def generate_json_report(...) -> str:
    """Generate JSON format report."""
    import json
    from dataclasses import asdict  # ❌ Uses reflection

    # Convert dataclasses to dictionaries
    teams_data = {
        abbrev: {
            "total": team.total,
            "players": [asdict(p) for p in team.players],  # ❌ Reflection for each player
            "division": team.division,
            "conference": team.conference,
            "avg_per_player": team.avg_per_player,
        }
        for abbrev, team in team_scores.items()
    }
    # For 32 teams × 25 players = 800 asdict() calls
    # Each asdict() uses reflection to inspect fields

    divisions_data = {
        name: asdict(standing)  # ❌ More reflection
        for name, standing in division_standings.items()
    }

    conferences_data = {
        name: asdict(standing)  # ❌ More reflection
        for name, standing in conference_standings.items()
    }

    playoffs_data = {
        conf: [asdict(team) for team in teams]  # ❌ Even more reflection
        for conf, teams in playoff_standings.items()
    }

    return json.dumps(report_data, indent=2)
```

**Performance bottleneck**:

- `asdict()` uses `dataclasses.fields()` to inspect class
- Reflection overhead for 800+ objects
- Slower than direct attribute access
- Unnecessary when we know the fields

## Proposed Solution

Add explicit `to_dict()` methods to all dataclasses:

**models/player.py (optimized)**:

```python
@dataclass
class PlayerScore:
    """Represents a player with their Scrabble score information."""

    first_name: str
    last_name: str
    full_name: str
    first_score: int
    last_score: int
    full_score: int
    team: str
    division: str
    conference: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation of player

        Note:
            This is 2-3x faster than dataclasses.asdict()
            because it uses direct attribute access instead of reflection.
        """
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "first_score": self.first_score,
            "last_score": self.last_score,
            "full_score": self.full_score,
            "team": self.team,
            "division": self.division,
            "conference": self.conference,
        }

    def __repr__(self) -> str:
        """Return a string representation of the player."""
        return f"PlayerScore(name='{self.full_name}', score={self.full_score}, team='{self.team}')"
```

**models/team.py (optimized)**:

```python
@dataclass
class TeamScore:
    """Represents a team with aggregated Scrabble score information."""

    abbrev: str
    total: int
    players: list[PlayerScore]
    division: str
    conference: str
    avg_per_player: float = field(init=False)

    def __post_init__(self) -> None:
        """Calculate average score per player after initialization."""
        self.avg_per_player = self.total / len(self.players) if self.players else 0.0

    def to_dict(self, include_players: bool = True) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization.

        Args:
            include_players: Whether to include full player list (default: True)

        Returns:
            Dictionary representation of team
        """
        result = {
            "abbrev": self.abbrev,
            "total": self.total,
            "division": self.division,
            "conference": self.conference,
            "avg_per_player": self.avg_per_player,
            "player_count": len(self.players),
        }

        if include_players:
            result["players"] = [p.to_dict() for p in self.players]

        return result

    @property
    def player_count(self) -> int:
        """Return the number of players on the team."""
        return len(self.players)

    def __repr__(self) -> str:
        """Return a string representation of the team."""
        return f"TeamScore(abbrev='{self.abbrev}', total={self.total}, players={self.player_count})"
```

**models/standings.py (optimized)**:

```python
@dataclass
class DivisionStandings:
    """Division-level standings."""

    name: str
    total: int
    teams: list[str]
    player_count: int
    avg_per_team: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "total": self.total,
            "teams": self.teams,
            "player_count": self.player_count,
            "avg_per_team": self.avg_per_team,
        }


@dataclass
class ConferenceStandings:
    """Conference-level standings."""

    name: str
    total: int
    teams: list[str]
    player_count: int
    avg_per_team: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "total": self.total,
            "teams": self.teams,
            "player_count": self.player_count,
            "avg_per_team": self.avg_per_team,
        }


@dataclass
class PlayoffTeam:
    """Team information for playoff standings."""

    abbrev: str
    total: int
    players: int
    avg: float
    conference: str
    division: str
    seed_type: str = ""
    in_playoffs: bool = False
    division_rank: int = 0
    status_indicator: StatusIndicator = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "abbrev": self.abbrev,
            "total": self.total,
            "players": self.players,
            "avg": self.avg,
            "conference": self.conference,
            "division": self.division,
            "seed_type": self.seed_type,
            "in_playoffs": self.in_playoffs,
            "division_rank": self.division_rank,
            "status_indicator": self.status_indicator,
        }
```

**cli.py (optimized)**:

```python
def generate_json_report(...) -> str:
    """Generate JSON format report."""
    import json
    # ✅ No longer need dataclasses.asdict

    # Convert dataclasses to dictionaries
    teams_data = {
        abbrev: team.to_dict()  # ✅ Fast direct access
        for abbrev, team in team_scores.items()
    }

    divisions_data = {
        name: standing.to_dict()  # ✅ Fast direct access
        for name, standing in division_standings.items()
    }

    conferences_data = {
        name: standing.to_dict()  # ✅ Fast direct access
        for name, standing in conference_standings.items()
    }

    playoffs_data = {
        conf: [team.to_dict() for team in teams]  # ✅ Fast direct access
        for conf, teams in playoff_standings.items()
    }

    report_data = {
        "teams": teams_data,
        "divisions": divisions_data,
        "conferences": conferences_data,
        "playoffs": playoffs_data,
        "summary": {
            "total_teams": len(team_scores),
            "total_players": len(all_players),
        },
    }

    return json.dumps(report_data, indent=2)
```

## Implementation Steps

1. **Add to_dict() to PlayerScore**:

   - Return dictionary with all fields
   - Use direct attribute access
   - Add docstring with performance note

1. **Add to_dict() to TeamScore**:

   - Include optional `include_players` parameter
   - Call player.to_dict() for nested objects
   - Include derived fields (player_count)

1. **Add to_dict() to DivisionStandings**:

   - Return dictionary with all fields
   - Handle list fields properly

1. **Add to_dict() to ConferenceStandings**:

   - Same as DivisionStandings

1. **Add to_dict() to PlayoffTeam**:

   - Return dictionary with all fields
   - Include status_indicator properly

1. **Update cli.py**:

   - Remove `from dataclasses import asdict`
   - Replace all `asdict(obj)` with `obj.to_dict()`
   - Clean up imports

1. **Add type hints**:

   - Import `Any` from typing
   - Return type: `dict[str, Any]`

1. **Test thoroughly**:

   - Verify JSON output unchanged
   - Benchmark performance
   - Test all dataclasses

## Testing Strategy

**Unit Tests**:

```python
# tests/unit/test_to_dict_methods.py
import json
import pytest
from dataclasses import asdict
from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.team import TeamScore

def test_player_to_dict_matches_asdict(sample_player):
    """Verify to_dict() produces same output as asdict()."""
    manual_dict = sample_player.to_dict()
    asdict_output = asdict(sample_player)

    # Should be identical
    assert manual_dict == asdict_output

def test_team_to_dict_matches_asdict(sample_team):
    """Verify to_dict() produces same output as asdict()."""
    manual_dict = sample_team.to_dict()

    # asdict would recursively convert players too
    asdict_output = asdict(sample_team)

    # Should be identical
    assert manual_dict == asdict_output

def test_to_dict_serializable_to_json(sample_player, sample_team):
    """Verify to_dict() output is JSON-serializable."""
    player_dict = sample_player.to_dict()
    team_dict = sample_team.to_dict()

    # Should not raise
    json.dumps(player_dict)
    json.dumps(team_dict)

def test_to_dict_performance_vs_asdict():
    """Verify to_dict() is faster than asdict()."""
    import time
    import random

    # Create test data
    players = [
        PlayerScore(
            first_name="First",
            last_name="Last",
            full_name="First Last",
            first_score=random.randint(1, 50),
            last_score=random.randint(1, 50),
            full_score=random.randint(1, 100),
            team="TOR",
            division="Atlantic",
            conference="Eastern"
        )
        for _ in range(100)
    ]

    iterations = 1000

    # Benchmark asdict()
    start = time.perf_counter()
    for _ in range(iterations):
        for player in players:
            result = asdict(player)
    asdict_time = time.perf_counter() - start

    # Benchmark to_dict()
    start = time.perf_counter()
    for _ in range(iterations):
        for player in players:
            result = player.to_dict()
    to_dict_time = time.perf_counter() - start

    # to_dict() should be faster
    speedup = asdict_time / to_dict_time
    assert speedup > 1.5, f"Expected >1.5x speedup, got {speedup:.2f}x"

    print(f"Speedup: {speedup:.2f}x (asdict: {asdict_time:.3f}s, to_dict: {to_dict_time:.3f}s)")

def test_team_to_dict_include_players_flag(sample_team):
    """Verify include_players parameter works."""
    # With players
    with_players = sample_team.to_dict(include_players=True)
    assert "players" in with_players
    assert len(with_players["players"]) > 0

    # Without players
    without_players = sample_team.to_dict(include_players=False)
    assert "players" not in without_players
    assert "player_count" in without_players
```

**Integration Tests**:

```python
def test_json_output_unchanged_with_to_dict(baseline_json):
    """Verify to_dict() produces same JSON as asdict()."""
    client = NHLApiClient(cache_enabled=True)
    scorer = ScrabbleScorer()
    processor = TeamProcessor(client, scorer)

    team_scores, all_players, _ = processor.process_all_teams()
    division_standings = processor.calculate_division_standings(team_scores)
    conference_standings = processor.calculate_conference_standings(team_scores)

    calculator = PlayoffCalculator()
    playoff_standings = calculator.calculate_playoff_standings(team_scores)

    # Generate JSON using to_dict()
    from nhl_scrabble.cli import generate_json_report
    json_output = generate_json_report(
        team_scores,
        all_players,
        division_standings,
        conference_standings,
        playoff_standings
    )

    # Should match baseline
    import json
    assert json.loads(json_output) == json.loads(baseline_json)
```

**Manual Testing**:

```bash
# Generate JSON before optimization
nhl-scrabble analyze --format json --output /tmp/before.json

# Apply optimization

# Generate JSON after optimization
nhl-scrabble analyze --format json --output /tmp/after.json

# Compare
diff <(jq -S . /tmp/before.json) <(jq -S . /tmp/after.json)
# Should be identical

# Benchmark
time nhl-scrabble analyze --format json --output /tmp/benchmark.json
# Should be ~2-3x faster for JSON generation
```

## Acceptance Criteria

- [ ] to_dict() method added to all dataclasses
- [ ] PlayerScore.to_dict() implemented
- [ ] TeamScore.to_dict() implemented with include_players parameter
- [ ] DivisionStandings.to_dict() implemented
- [ ] ConferenceStandings.to_dict() implemented
- [ ] PlayoffTeam.to_dict() implemented
- [ ] cli.py updated to use to_dict() instead of asdict()
- [ ] JSON output byte-identical to previous version
- [ ] 2-3x speedup for JSON serialization
- [ ] All existing tests pass
- [ ] New performance tests added
- [ ] Type hints correct (dict[str, Any])

## Related Files

- `src/nhl_scrabble/models/player.py` - Add to_dict()
- `src/nhl_scrabble/models/team.py` - Add to_dict()
- `src/nhl_scrabble/models/standings.py` - Add to_dict() to all classes
- `src/nhl_scrabble/cli.py` - Use to_dict() instead of asdict()
- `tests/unit/test_to_dict_methods.py` - New performance tests
- `tests/integration/test_json_output.py` - JSON output tests

## Dependencies

**None** - Pure Python optimization

**Recommended order** (Phase 2 optimizations):

1. Task 002 (concurrent API) - Higher impact
1. Task 004 (single-pass stats) - Independent
1. **This task (006)** - JSON-specific optimization

**Enables**:

- Faster JSON API responses (if web interface added)
- Better performance for data export
- Cleaner serialization code

## Additional Notes

**Why asdict() is Slow**:

```python
# asdict() implementation (simplified)
def asdict(obj):
    fields = dataclasses.fields(obj)  # ❌ Reflection - inspect class
    return {
        field.name: getattr(obj, field.name)  # ❌ Reflection - get attribute
        for field in fields
    }

# to_dict() implementation
def to_dict(self):
    return {
        "field1": self.field1,  # ✅ Direct access
        "field2": self.field2,  # ✅ Direct access
    }
```

**Performance Comparison**:

```
For PlayerScore with 9 fields:

asdict():
- fields() call: inspect class structure
- 9× getattr() calls: dynamic attribute lookup
- Dictionary construction
- Total: ~5-10 microseconds per object

to_dict():
- 9× direct attribute access
- Dictionary construction
- Total: ~2-3 microseconds per object

Speedup: 5-10µs / 2-3µs = 2-3x faster

For 800 players:
- asdict: 800 × 8µs = 6.4ms
- to_dict: 800 × 3µs = 2.4ms
- Time saved: 4ms (not huge, but cleaner code)
```

**When to Use Each**:

- `asdict()`: Quick prototyping, unknown dataclass structure
- `to_dict()`: Production code, performance-critical, known structure
- `Pydantic`: Even better - use `model_dump()` if using Pydantic

**Code Maintenance**:

```python
# ⚠️  Must keep to_dict() in sync with dataclass fields
@dataclass
class Player:
    name: str
    score: int
    new_field: str  # ❌ Easy to forget updating to_dict()

    def to_dict(self):
        return {
            "name": self.name,
            "score": self.score,
            # Missing new_field! ❌
        }

# Solution: Add test
def test_to_dict_includes_all_fields():
    from dataclasses import fields

    player = Player("John", 10, "value")
    dict_output = player.to_dict()

    # Verify all fields present
    field_names = {f.name for f in fields(Player)}
    dict_keys = set(dict_output.keys())

    assert field_names == dict_keys, f"Missing fields: {field_names - dict_keys}"
```

**Alternatives Considered**:

1. **Pydantic BaseModel**: Better but requires migration
1. **__dict__**: Includes private fields, not ideal
1. **vars()**: Same as __dict__
1. **Custom JSON encoder**: More complex, not faster
1. **Keep asdict()**: Rejected due to performance

**Future Pydantic Migration**:

```python
# If migrating to Pydantic in future:
from pydantic import BaseModel

class PlayerScore(BaseModel):
    first_name: str
    last_name: str
    # ... fields ...

    # No to_dict() needed! Use model_dump()
    # player.model_dump()  # Fast, built-in

# Even faster with Pydantic v2 (Rust core)
```

**JSON Encoder Alternative** (not recommended):

```python
# Could use custom JSONEncoder instead
class DataclassEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        return super().default(obj)

# Usage
json.dumps(data, cls=DataclassEncoder)

# But this is less explicit than obj.to_dict()
```

**Best Practices**:

1. ✅ Add to_dict() to all serializable dataclasses
1. ✅ Use direct attribute access (not getattr)
1. ✅ Handle nested objects recursively
1. ✅ Test that to_dict() matches asdict()
1. ✅ Document performance benefit
1. ✅ Add type hints (dict[str, Any])

**Real-world Impact**:

```
JSON generation breakdown (32 teams):
- Data collection: 15s (see task 002)
- Dictionary conversion: 10ms
  - asdict: 6-8ms
  - to_dict: 2-3ms
- JSON encoding: 5-10ms
- Total: 15-25ms (to_dict saves 4-5ms)

Not a huge absolute time, but:
- Cleaner code
- More explicit
- Better for future API usage
- Good practice
```

## Implementation Notes

*To be filled during implementation:*

- Actual performance measurements
- Any fields that needed special handling
- Decision on error handling for None values
- Testing edge cases discovered
- Comparison with asdict() on real data
