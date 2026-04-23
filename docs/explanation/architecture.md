# Architecture Overview

Understanding NHL Scrabble's system design, component structure, and architectural decisions.

## High-Level Architecture

NHL Scrabble follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                       CLI Layer                             │
│                  (User Interface)                           │
│                                                             │
│   ┌──────────┐   Handles:                                  │
│   │ cli.py   │   - Argument parsing (Click)                │
│   └────┬─────┘   - Output formatting                       │
│        │         - Error presentation                       │
└────────┼─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                 Business Logic Layer                        │
│                 (Core Functionality)                        │
│                                                             │
│  ┌──────────────┐  ┌───────────┐  ┌─────────────┐         │
│  │ Processors   │  │ Scoring   │  │ Reports     │         │
│  ├──────────────┤  ├───────────┤  ├─────────────┤         │
│  │• TeamProc    │  │• Scrabble │  │• Conference │         │
│  │• PlayoffCalc │  │  Scorer   │  │• Division   │         │
│  └──────┬───────┘  └─────┬─────┘  │• Playoff    │         │
│         │                 │        │• Team       │         │
│         │                 │        │• Stats      │         │
└─────────┼─────────────────┼────────┴─────────────┘         │
          │                 │                                │
          ▼                 ▼                                │
┌─────────────────────────────────────────────────────────────┐
│                     Data Layer                              │
│               (Data Models & Access)                        │
│                                                             │
│  ┌──────────────┐  ┌─────────────────┐                    │
│  │ Models       │  │ API Client      │                    │
│  ├──────────────┤  ├─────────────────┤                    │
│  │• Player      │  │• NHLApiClient   │                    │
│  │• Team        │  │• Retry logic    │                    │
│  │• Standings   │  │• Rate limiting  │                    │
│  │• PlayerScore │  │• Caching        │                    │
│  │• TeamScore   │  │• Error handling │                    │
│  └──────────────┘  └────────┬────────┘                    │
└──────────────────────────────┼──────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │   NHL API        │
                    │  (External)      │
                    │                  │
                    │• Standings       │
                    │• Team Rosters    │
                    └──────────────────┘
```

## Layer Responsibilities

### 1. CLI Layer (`cli.py`)

**Purpose**: User interface and command orchestration.

**Responsibilities**:

- Parse command-line arguments (using Click)
- Validate input (especially output paths)
- Orchestrate the analysis workflow
- Format and present output
- Handle user-facing errors

**Key principle**: **Minimal logic**. The CLI delegates almost all work to lower layers.

**Example**:

```python
@cli.command()
@click.option("--format", type=click.Choice(["text", "json"]))
@click.option("--output", "-o", type=click.Path())
def analyze(output_format: str, output: str | None) -> None:
    # 1. Validate (early, before expensive operations)
    validate_output_path(output)

    # 2. Configure
    config = Config.from_env()
    config.output_format = output_format

    # 3. Delegate to business logic
    result = run_analysis(config)

    # 4. Present output
    if output:
        Path(output).write_text(result)
    else:
        print(result)
```

**Why this design?**

- CLI is just the interface - easy to add web UI later
- Business logic reusable from Python code
- Testing focuses on logic, not CLI quirks

### 2. Business Logic Layer

Contains the core application logic across three modules:

#### Processors (`processors/`)

**Purpose**: Coordinate data processing workflows.

**Components**:

- `TeamProcessor`: Aggregates scores, calculates standings
- `PlayoffCalculator`: Determines playoff seeding

**Responsibilities**:

- Fetch data via API client
- Score players via scorer
- Aggregate into team scores
- Calculate rankings and standings

**Example** (team_processor.py):

```python
class TeamProcessor:
    def process_all_teams(self) -> tuple[dict, list, list]:
        # 1. Fetch standings
        standings = self.api_client.fetch_standings()

        # 2. Process each team
        for team in standings:
            roster = self.api_client.fetch_roster(team.abbrev)
            team_score = self._score_roster(roster)
            team_scores[team.abbrev] = team_score

        # 3. Return aggregated data
        return team_scores, all_players, failed_teams
```

**Why processors?**

- Encapsulate complex workflows
- Testable without real API calls
- Clear separation from scoring logic

#### Scoring (`scoring/`)

**Purpose**: Calculate Scrabble scores for names.

**Components**:

- `ScrabbleScorer`: Core scoring algorithm

**Responsibilities**:

- Define letter values
- Calculate scores for text
- Score player models
- Handle edge cases (accents, special chars)

**Example** (scrabble.py):

```python
class ScrabbleScorer:
    SCRABBLE_VALUES = {
        'A': 1, 'E': 1, ...,  # Low-value
        'Q': 10, 'Z': 10,     # High-value
    }

    def calculate_score(self, text: str) -> int:
        return sum(
            self.SCRABBLE_VALUES.get(char.upper(), 0)
            for char in text if char.isalpha()
        )
```

**Why separate scorer?**

- Single Responsibility Principle
- Easy to modify scoring rules
- Reusable in other contexts
- Simple to test

#### Reports (`reports/`)

**Purpose**: Generate formatted output.

**Components**:

- `BaseReport`: Abstract base class
- `ConferenceReporter`: Conference standings
- `DivisionReporter`: Division standings
- `PlayoffReporter`: Playoff bracket
- `TeamReporter`: Individual team details
- `StatsReporter`: League statistics

**Architecture**: **Template Method pattern**.

```python
class BaseReport(ABC):
    @abstractmethod
    def generate(self, data) -> str:
        """Subclasses implement specific formatting."""
        pass


class ConferenceReporter(BaseReport):
    def generate(self, standings) -> str:
        # Conference-specific formatting
        return formatted_report
```

**Why plugin architecture?**

- Easy to add new report types
- Each reporter focuses on one concern
- Can mix and match reports
- Testable in isolation

### 3. Data Layer

#### Models (`models/`)

**Purpose**: Define data structures with validation.

**Technology**: **Pydantic** for runtime type safety.

**Components**:

- `Player`: Player information from API
- `Team`: Team metadata
- `PlayerScore`: Player with calculated score
- `TeamScore`: Aggregated team data
- `DivisionStandings`: Division rankings
- `ConferenceStandings`: Conference rankings

**Example** (player.py):

```python
from pydantic import BaseModel, Field


class Player(BaseModel):
    """NHL player from API."""

    firstName: str = Field(..., min_length=1)
    lastName: str = Field(..., min_length=1)
    sweaterNumber: int | None = None
    positionCode: str

    class Config:
        frozen = True  # Immutable
```

**Why Pydantic?**

- **Runtime validation**: Catch bad data early
- **Type safety**: IDE autocomplete, type checking
- **JSON serialization**: Easy API handling
- **Documentation**: Self-documenting code

#### API Client (`api/nhl_client.py`)

**Purpose**: Interact with NHL API reliably.

**Responsibilities**:

- Make HTTP requests
- Handle failures (retry logic)
- Respect rate limits
- Cache responses
- Parse JSON into models

**Key features**:

1. **Retry logic** (exponential backoff):

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((RequestException, Timeout)),
)
def _fetch_with_retry(self, url: str) -> dict:
    response = self.session.get(url, timeout=self.timeout)
    response.raise_for_status()
    return response.json()
```

2. **Rate limiting**:

```python
def fetch_roster(self, team_abbrev: str) -> list[Player]:
    # Delay between requests
    time.sleep(self.rate_limit_delay)
    data = self._fetch_with_retry(url)
    return [Player(**p) for p in data["forwards"] + data["defensemen"]]
```

3. **Caching**:

```python
@lru_cache(maxsize=128)
def fetch_standings(self) -> list[Team]:
    # Cached for session duration
    return self._fetch_standings_uncached()
```

**Why this design?**

- **Resilient**: Handles network issues gracefully
- **Polite**: Rate limiting respects API provider
- **Fast**: Caching reduces redundant requests
- **Testable**: Easy to mock for tests

## Design Principles

### 1. Separation of Concerns

Each layer/module has one job:

- CLI: User interface
- Processors: Workflow orchestration
- Scorer: Calculation logic
- Reports: Formatting
- Models: Data structure
- API Client: External communication

**Benefit**: Changes in one area don't cascade.

### 2. Dependency Injection

Components receive dependencies rather than creating them:

```python
class TeamProcessor:
    def __init__(self, api_client: NHLApiClient, scorer: ScrabbleScorer):
        self.api_client = api_client  # Injected
        self.scorer = scorer  # Injected
```

**Benefit**: Easy to mock for testing.

### 3. Type Safety

Comprehensive type hints throughout:

```python
def score_player(self, player: Player) -> PlayerScore:
    """Type hints document and enforce."""
    ...
```

**Benefit**: Catch errors at development time, not runtime.

### 4. Immutability

Data models are immutable (Pydantic `frozen=True`):

```python
player = Player(firstName="Alex", lastName="Ovechkin")
# player.firstName = "Alexander"  # Error: frozen
```

**Benefit**: Prevents accidental mutation bugs.

### 5. Error Handling

Explicit error handling at boundaries:

```python
try:
    roster = api_client.fetch_roster(team_abbrev)
except NHLApiError as e:
    logger.error(f"Failed to fetch {team_abbrev}: {e}")
    failed_teams.append(team_abbrev)
    continue  # Graceful degradation
```

**Benefit**: System continues working even when parts fail.

## Data Flow

Typical analysis workflow:

```
1. User invokes CLI
   ↓
2. CLI validates inputs (output path)
   ↓
3. CLI creates Config from environment/args
   ↓
4. CLI calls run_analysis(config)
   ↓
5. run_analysis creates components:
   - API client
   - Scorer
   - Team processor
   - Playoff calculator
   - Reporters
   ↓
6. Team processor fetches data:
   - Standings from NHL API
   - Rosters for each team (with delays)
   ↓
7. Scorer calculates player scores
   ↓
8. Processor aggregates team scores
   ↓
9. Playoff calculator determines seeding
   ↓
10. Reporters generate formatted output
   ↓
11. CLI presents results (stdout or file)
```

## Testing Strategy

### Test Pyramid

```
           /\
          /  \         E2E (integration tests)
         /____\           - Full workflow
        /      \          - Real CLI invocation
       /  Unit  \         - Mocked API
      /__________\
     Unit Tests
     - Individual functions
     - Mocked dependencies
     - Fast execution
```

**Unit tests** (80%):

- Test each component in isolation
- Mock all dependencies
- Fast (\<1s total)

**Integration tests** (20%):

- Test component interactions
- Mock only external APIs
- Slower (~20s total)

See [Testing Philosophy](testing-philosophy.md) for details.

## Extension Points

The architecture makes certain extensions easy:

### 1. Add New Report Type

Subclass `BaseReport`:

```python
class PlayerComparisonReport(BaseReport):
    def generate(self, players: list[Player]) -> str:
        # Custom formatting
        ...
```

Register in CLI:

```python
comparison_reporter = PlayerComparisonReport()
result = comparison_reporter.generate(selected_players)
```

### 2. Add New Data Source

Implement API client interface:

```python
class NBAApiClient:
    def fetch_standings(self) -> list[Team]: ...

    def fetch_roster(self, team_abbrev: str) -> list[Player]: ...
```

Use dependency injection:

```python
nba_client = NBAApiClient()
processor = TeamProcessor(nba_client, scorer)
```

### 3. Add New Output Format

Add format to CLI:

```python
@click.option("--format", type=click.Choice(["text", "json", "html"]))
```

Implement generator:

```python
if config.output_format == "html":
    return generate_html_report(data)
```

## Performance Considerations

### Bottleneck: API Calls

Fetching 32 team rosters takes ~10-15 seconds due to:

- Network latency (~300ms per request)
- Rate limiting (delays between requests)
- API processing time

**Mitigation**:

- Caching (reduces subsequent runs to \<2s)
- Could parallelize (but respect rate limits)

### Memory: Minimal

- ~750 player objects
- ~32 team objects
- Total: \<5MB in memory

**No optimization needed** for current scale.

### CPU: Negligible

Scoring calculations:

- Simple dictionary lookups
- String iteration
- Total: \<100ms for all players

**Not a bottleneck.**

## Trade-offs

### Pydantic vs Dataclasses

**Chose Pydantic**:

- ✅ Runtime validation
- ✅ JSON serialization
- ✅ Better error messages
- ❌ Slight overhead (negligible here)

### Async vs Sync

**Chose Sync**:

- ✅ Simpler code
- ✅ Easier to understand
- ✅ Adequate performance
- ❌ Could parallelize API calls (future)

### Rich vs Plain Text

**Chose Rich**:

- ✅ Beautiful terminal output
- ✅ Progress indicators
- ✅ Color coding
- ❌ Additional dependency

### Click vs Argparse

**Chose Click**:

- ✅ Cleaner syntax
- ✅ Better help formatting
- ✅ Easier testing
- ❌ Additional dependency

## Future Architecture

Potential enhancements:

### 1. Plugin System

Allow third-party reports:

```python
# plugins/custom_report.py
class CustomReport(BaseReport): ...


# Auto-discovered via entry points
```

### 2. Web API

FastAPI backend:

```python
@app.get("/api/teams/{abbrev}")
def get_team_score(abbrev: str):
    return team_scores[abbrev]
```

### 3. Database Storage

Store historical data:

```sql
CREATE TABLE team_scores (
    date DATE,
    team_abbrev VARCHAR(3),
    total_score INTEGER,
    ...
);
```

Track changes over time.

### 4. Async API Client

Parallel roster fetching:

```python
async def fetch_all_rosters(self, teams):
    tasks = [self.fetch_roster(t) for t in teams]
    return await asyncio.gather(*tasks)
```

Could reduce runtime to 3-5 seconds.

## Related

- [Why Scrabble Scoring?](why-scrabble-scoring.md) - The concept
- [NHL API Strategy](nhl-api-strategy.md) - API integration details
- [Testing Philosophy](testing-philosophy.md) - Testing approach
- [Python API Reference](../reference/code-api.md) - API documentation
