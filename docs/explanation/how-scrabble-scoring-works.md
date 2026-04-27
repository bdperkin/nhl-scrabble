# How Scrabble Scoring Works

Technical explanation of how NHL Scrabble calculates player name scores and generates standings.

## Overview

NHL Scrabble analyzes NHL player names using standard Scrabble letter point values to create alternative team standings. This document explains the technical implementation.

## Scrabble Letter Values

Standard Scrabble letter point values used for scoring:

| Points | Letters                      |
| ------ | ---------------------------- |
| **1**  | A, E, I, O, U, L, N, S, T, R |
| **2**  | D, G                         |
| **3**  | B, C, M, P                   |
| **4**  | F, H, V, W, Y                |
| **5**  | K                            |
| **8**  | J, X                         |
| **10** | Q, Z                         |

**Implementation:**

```python
SCRABBLE_VALUES = {
    "A": 1,
    "E": 1,
    "I": 1,
    "O": 1,
    "U": 1,
    "L": 1,
    "N": 1,
    "S": 1,
    "T": 1,
    "R": 1,
    "D": 2,
    "G": 2,
    "B": 3,
    "C": 3,
    "M": 3,
    "P": 3,
    "F": 4,
    "H": 4,
    "V": 4,
    "W": 4,
    "Y": 4,
    "K": 5,
    "J": 8,
    "X": 8,
    "Q": 10,
    "Z": 10,
}
```

**Scoring Rules:**

1. **Case-insensitive**: All letters converted to uppercase before scoring
1. **Letters only**: Non-alphabetic characters (spaces, hyphens, apostrophes) are ignored
1. **Full name**: First name + last name are scored together

**Examples:**

```python
>>> from nhl_scrabble.scoring import ScrabbleScorer
>>> scorer = ScrabbleScorer()

# High-scoring names (rare letters)
>>> scorer.calculate_score("Alexander Ovechkin")  # V, H, K
37

>>> scorer.calculate_score("Zdeno Chara")  # Z worth 10!
25

>>> scorer.calculate_score("Pavel Zacha")  # Another Z
29

# Lower-scoring names (common letters)
>>> scorer.calculate_score("Connor McDavid")  # All common letters
24

>>> scorer.calculate_score("Leon Draisaitl")  # No high-value letters
14
```

## Workflow

### Step 1: Fetch NHL Data

Retrieve current NHL team rosters from the NHL API:

```
GET https://api-web.nhle.com/v1/standings/now
  → Returns team metadata (division, conference, abbreviations)

For each team:
  GET https://api-web.nhle.com/v1/roster/{team_abbrev}/current
    → Returns roster (forwards, defensemen, goalies)
```

**Implementation Details:**

- **Rate Limiting**: 0.3 second delay between roster fetches
- **Retry Logic**: 3 retries with exponential backoff (1s, 2s, 4s)
- **Timeout**: 10 seconds per request
- **Error Handling**: Graceful degradation (skip failed teams)
- **Progress Tracking**: Real-time progress bars during fetching

**API Response Processing:**

```python
# Standings endpoint
{
  "standings": [
    {
      "teamAbbrev": {"default": "TOR"},
      "teamName": {"default": "Maple Leafs"},
      "divisionName": "Atlantic",
      "conferenceName": "Eastern",
      ...
    }
  ]
}

# Roster endpoint
{
  "forwards": [
    {
      "id": 8477404,
      "firstName": {"default": "Auston"},
      "lastName": {"default": "Matthews"},
      ...
    }
  ],
  "defensemen": [...],
  "goalies": [...]
}
```

### Step 2: Calculate Scrabble Scores

For each player, calculate the Scrabble value of their full name:

```python
def calculate_score(text: str) -> int:
    """Calculate Scrabble score for any text string.

    Args:
        text: Text to score (player name)

    Returns:
        Total Scrabble score (sum of all letter values)
    """
    score = 0
    for char in text.upper():
        if char in SCRABBLE_VALUES:
            score += SCRABBLE_VALUES[char]
    return score
```

**Player Model:**

```python
@dataclass
class PlayerScore:
    """A player with their Scrabble score."""

    id: int
    first_name: str
    last_name: str
    full_name: str
    score: int
    team: str
```

**Scoring Process:**

1. Extract first name and last name from API response
1. Combine to create full name: `f"{first_name} {last_name}"`
1. Calculate Scrabble score for full name
1. Create `PlayerScore` object with all details

### Step 3: Aggregate Team Scores

For each team, aggregate player scores into team totals:

```python
@dataclass
class TeamScore:
    """Team with aggregated Scrabble scores."""

    abbreviation: str
    name: str
    division: str
    conference: str
    players: list[PlayerScore]
    total: int  # Sum of all player scores
    average: float  # Mean score per player
    player_count: int  # Number of players on roster
```

**Aggregation Logic:**

1. Group players by team
1. Calculate `total` = sum of all player scores
1. Calculate `average` = total / player_count
1. Sort players by score (descending) for display

### Step 4: Generate Standings

Create division and conference standings from team scores:

**Division Standings:**

```python
@dataclass
class DivisionStandings:
    """Standings for a single division."""

    division: str
    teams: list[TeamScore]  # Sorted by total score
```

**Conference Standings:**

```python
@dataclass
class ConferenceStandings:
    """Standings for a single conference."""

    conference: str
    teams: list[TeamScore]  # Sorted by total score
```

**Sorting Rules:**

1. **Primary**: Total Scrabble score (descending)
1. **Tiebreaker 1**: Average score per player (descending)
1. **Tiebreaker 2**: Team abbreviation (alphabetical)

### Step 5: Determine Playoff Bracket

Calculate playoff seeding based on NHL playoff format:

**Playoff Structure:**

- **Division Leaders** (Top 3 per division): Automatic playoff spots
- **Wild Cards** (2 per conference): Next best teams by total score
- **Conference Leaders**: Best record in each conference
- **Presidents' Trophy**: Best overall record

**Playoff Indicators:**

- `y` - Clinched division
- `x` - Clinched playoff spot (wild card)
- `z` - Clinched conference
- `p` - Presidents' Trophy winner
- `e` - Eliminated from playoffs

**Seeding Logic:**

```python
def calculate_playoff_seeding(teams: list[TeamScore]) -> dict[str, list[PlayoffTeam]]:
    # For each conference:
    # 1. Top 3 teams per division (6 teams total)
    # 2. Next 2 best teams across conference (wild cards)
    # 3. Seed 1-8 based on points
    # 4. Generate matchups: 1v8, 2v7, 3v6, 4v5
```

### Step 6: Generate Reports

Create comprehensive reports from the analyzed data:

**Report Types:**

1. **Top Players Report** - Highest-scoring individual players
1. **Team Report** - All teams with top players per team
1. **Division Report** - Teams grouped by division
1. **Conference Report** - Eastern vs Western standings
1. **Playoff Report** - Mock playoff bracket
1. **Stats Report** - League-wide statistics

**Report Formats:**

- **Text** - Human-readable terminal output with Rich formatting
- **JSON** - Machine-readable structured data
- **HTML** - Browser-friendly formatted report

## NHL API Endpoints

### Standings Endpoint

```
GET https://api-web.nhle.com/v1/standings/now
```

**Purpose**: Get current team standings and metadata

**Response**: Team abbreviations, names, divisions, conferences

**Usage**: Initial team list for roster fetching

### Roster Endpoint

```
GET https://api-web.nhle.com/v1/roster/{team_abbrev}/current
```

**Purpose**: Get current team roster

**Parameters**: `team_abbrev` - Team abbreviation (e.g., "TOR", "BOS")

**Response**: Forwards, defensemen, goalies with player details

**Usage**: Fetch all players for Scrabble score calculation

### Error Handling

**Network Errors:**

- Automatic retry with exponential backoff
- Timeout after 10 seconds
- Graceful degradation (skip failed teams)

**API Errors:**

- 404 Not Found: Team not found (skip)
- 500 Server Error: Retry with backoff
- Rate limiting: Respect 0.3s delay

**Data Errors:**

- Missing player name: Skip player (log warning)
- Invalid JSON: Skip team (log error)
- Empty roster: Report zero-score team

## Performance Characteristics

**Timing:**

- **API Fetching**: ~30 seconds (32 teams × ~1s each)
- **Scoring**: \<100ms (simple arithmetic on ~750 players)
- **Report Generation**: \<200ms (formatting and output)
- **Total Runtime**: ~30-35 seconds

**Optimization Techniques:**

1. **Rate Limiting**: Prevent API throttling
1. **Retry Logic**: Handle transient errors
1. **Progress Bars**: Show real-time status
1. **Caching**: Optional response caching for development
1. **Parallel Processing**: Not used (respects API rate limits)

## Data Flow Diagram

```
┌─────────────┐
│  NHL API    │
│ /standings  │
└─────┬───────┘
      │
      ▼
┌─────────────┐     ┌──────────────┐
│ Team List   │────▶│  NHL API     │
│ (32 teams)  │     │ /roster/{id} │
└─────────────┘     └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Player Data  │
                    │ (~750 total) │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Scrabble   │
                    │   Scorer     │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Team       │
                    │ Processor    │
                    └──────┬───────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌────────────────┐  ┌──────────┐   ┌──────────────┐
│ Division       │  │Conference│   │   Playoff    │
│ Standings      │  │Standings │   │   Bracket    │
└────────┬───────┘  └────┬─────┘   └──────┬───────┘
         │               │                │
         └───────────────┼────────────────┘
                         ▼
                  ┌──────────────┐
                  │   Reports    │
                  │ (Text/JSON/  │
                  │    HTML)     │
                  └──────────────┘
```

## Code Examples

### Basic Scoring

```python
from nhl_scrabble.scoring import ScrabbleScorer

scorer = ScrabbleScorer()
score = scorer.calculate_score("Alexander Ovechkin")
print(f"Score: {score}")  # Score: 37
```

### Full Analysis

```python
from nhl_scrabble.api import NHLClient
from nhl_scrabble.processors import TeamProcessor
from nhl_scrabble.scoring import ScrabbleScorer

# Initialize components
client = NHLClient()
scorer = ScrabbleScorer()
processor = TeamProcessor(client, scorer)

# Process all teams
teams, players, failed = processor.process_all_teams()

# Display results
for team in sorted(teams.values(), key=lambda t: t.total, reverse=True):
    print(f"{team.name}: {team.total} points ({team.average:.2f} avg)")
```

### Custom Report

```python
from nhl_scrabble.reports import TeamReport

# Generate team report
report = TeamReport(top_players_per_team=10)
output = report.generate(teams)
print(output)
```

## See Also

- [Why Scrabble Scoring?](why-scrabble-scoring.md) - Philosophy and rationale
- [Architecture Overview](architecture.md) - System design
- [NHL API Strategy](nhl-api-strategy.md) - API integration details
- [Getting Started Tutorial](../tutorials/01-getting-started.md) - Try it yourself
- [Understanding Output](../tutorials/understanding-output.md) - Interpreting results

## Implementation Notes

**Design Decisions:**

1. **Standard Scrabble values**: Use official values for familiarity
1. **Full name scoring**: First + last for complete player identity
1. **Case-insensitive**: Normalize for consistent scoring
1. **Ignore non-letters**: Focus on alphabetic characters only
1. **NHL API**: Use official data for accuracy and freshness

**Limitations:**

1. **API availability**: Depends on NHL API uptime
1. **Rate limiting**: ~30 second runtime due to API delays
1. **No historical data**: Only current rosters (API limitation)
1. **Name changes**: Player name changes not tracked historically

**Future Enhancements:**

1. **Caching**: Store results for faster repeated access
1. **Historical analysis**: Track scores across seasons
1. **Alternative scoring**: Custom letter values
1. **International support**: Handle diacritics and special characters
1. **Statistical analysis**: Correlations with actual hockey metrics
