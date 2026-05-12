# Expand Test Coverage of Business Logic Modules

**GitHub Issue**: [#588](https://github.com/bdperkin/nhl-scrabble/issues/588)

## Priority

**HIGH** - Must Do (Next Sprint)

## Estimated Effort

20-28 hours

## Description

Critical business logic modules have zero or minimal test coverage, leaving core application functionality untested. Current coverage for these modules is critically low at **3.27%**, with **~576 untested statements** across 4 major subsystems:

- **dashboard.py**: 0.00% (136 statements untested)
- **filters.py**: 0.00% (86 statements untested)
- **processors/**: 0.00% average (247 statements untested across 4 files)
- **scoring/**: 21.05% average (107 statements untested across 2 files)

**Total missing coverage**: ~576 statements across 9 files

This represents **critical gaps** in quality assurance for:
- Dashboard data aggregation and presentation
- Player/team filtering logic
- Team processing and roster management
- Playoff qualification calculations
- Scrabble scoring algorithms
- Grouping logic (birthplace, position)

These are **core business logic** modules that directly affect the accuracy of NHL Scrabble scores and standings.

## Current State

### Files with Tests (but critically low coverage):

**tests/unit/test_dashboard.py** - EXISTS but 0% coverage
- File exists but dashboard.py has 0% coverage (136 statements)
- Need comprehensive dashboard aggregation tests

**tests/unit/test_filters.py** - EXISTS but 0% coverage
- File exists but filters.py has 0% coverage (86 statements)
- Additional file: test_filters_country.py (also 0% coverage)
- Need comprehensive filtering logic tests

**tests/unit/test_team_processor.py** - EXISTS but 0% coverage
- File exists but team_processor.py has 0% coverage (92 statements)
- Need comprehensive team processing tests

**tests/unit/test_scoring_config.py** - EXISTS but 0% coverage
- File exists but scoring/config.py has 0% coverage (62 statements)
- Need scoring configuration tests

**tests/unit/test_scrabble.py** - EXISTS but 30.38% coverage
- File exists along with test_scrabble_scorer_custom.py
- Missing: 45 of 69 statements
- Partial coverage but needs completion

**tests/unit/scoring/test_scrabble_birthplace.py** - Specialized tests
- Exists but doesn't cover core scrabble.py functionality

**No tests for:**
- processors/grouping.py (62 statements)
- processors/playoff_calculator.py (89 statements)

### Coverage Breakdown by Module:

**dashboard.py (136 statements, 0% coverage):**
```
Lines missing: 3-331
Features untested:
- Dashboard data aggregation
- Statistics calculation
- Top players aggregation
- Team standings aggregation
- Conference/division aggregation
- Playoff bracket data
- Dashboard formatting
- Cache management
- Error handling
```

**filters.py (86 statements, 0% coverage):**
```
Lines missing: 3-577
Features untested:
- Player filtering by team
- Player filtering by position
- Player filtering by score range
- Player filtering by name/search
- Player filtering by birthplace/country
- Team filtering by division
- Team filtering by conference
- Filter composition/chaining
- Query parameter parsing
- Filter validation
```

**processors/grouping.py (62 statements, 0% coverage):**
```
Lines missing: 7-412
Features untested:
- Group players by birthplace
- Group players by position
- Group players by team
- Group aggregation logic
- Top scorers per group
- Group statistics
- Group sorting
- Group formatting
```

**processors/playoff_calculator.py (89 statements, 0% coverage):**
```
Lines missing: 3-303
Features untested:
- Playoff qualification logic
- Division leaders identification
- Wild card selection
- Conference seeding
- Playoff matchup generation
- Tiebreaker logic
- Playoff bracket structure
- Playoff indicators (x, y, z, p, e)
- Edge case handling
```

**processors/team_processor.py (92 statements, 0% coverage):**
```
Lines missing: 3-345
Features untested:
- Team data fetching
- Roster processing
- Player score calculation
- Team score aggregation
- Concurrent roster fetching
- Error handling for missing teams
- API client integration
- Scorer integration
- Team statistics calculation
```

**scoring/config.py (62 statements, 0% coverage):**
```
Lines missing: 3-245
Features untested:
- Letter value configuration
- Standard Scrabble values
- Custom scoring systems
- Score validation
- Configuration loading
- Configuration validation
- Default values
```

**scoring/scrabble.py (69 statements, 30.38% coverage):**
```
Lines missing: 84-85, 102-103, 132-133, 154-155, 199-255, 290-291, 304-322, 330-331
Features untested:
- Name normalization (lines 84-85)
- Special character handling (102-103)
- Case sensitivity (132-133)
- Unicode handling (154-155)
- Batch scoring (199-255) - **MAJOR GAP**
- Score caching logic (290-291)
- Score validation (304-322)
- Edge cases (330-331)
```

## Proposed Solution

### 1. Test Coverage Expansion Strategy

Create comprehensive test suites for each module following existing patterns:

#### A. Dashboard (Priority 1 - User-Facing Critical)

**dashboard.py** (136 statements):
```python
# tests/unit/test_dashboard.py (enhance existing)
class TestDashboard:
    """Comprehensive dashboard tests."""

    @pytest.fixture
    def sample_dashboard_data(self):
        """Sample data for dashboard testing."""
        return {
            "standings": [...],
            "teams": [...],
            "players": [...],
        }

    def test_dashboard_initialization(self):
        """Test dashboard initialization."""
        dashboard = Dashboard()
        assert dashboard is not None

    def test_get_top_players_overall(self, sample_dashboard_data):
        """Test getting top players across all teams."""
        dashboard = Dashboard(data=sample_dashboard_data)
        top_players = dashboard.get_top_players(limit=10)
        assert len(top_players) == 10
        assert top_players[0].score >= top_players[1].score  # Sorted

    def test_get_top_players_by_team(self, sample_dashboard_data):
        """Test getting top players per team."""
        dashboard = Dashboard(data=sample_dashboard_data)
        top_by_team = dashboard.get_top_players_by_team(limit=5)
        assert "WSH" in top_by_team
        assert len(top_by_team["WSH"]) == 5

    def test_get_team_standings(self, sample_dashboard_data):
        """Test team standings aggregation."""
        dashboard = Dashboard(data=sample_dashboard_data)
        standings = dashboard.get_team_standings()
        assert len(standings) == 32  # All NHL teams
        # Verify sorting by total score

    def test_get_conference_standings(self, sample_dashboard_data):
        """Test conference standings aggregation."""
        dashboard = Dashboard(data=sample_dashboard_data)
        eastern = dashboard.get_conference_standings("Eastern")
        western = dashboard.get_conference_standings("Western")
        assert len(eastern) == 16
        assert len(western) == 16

    def test_get_division_standings(self, sample_dashboard_data):
        """Test division standings aggregation."""
        dashboard = Dashboard(data=sample_dashboard_data)
        metro = dashboard.get_division_standings("Metropolitan")
        assert len(metro) == 8

    def test_get_playoff_bracket_data(self, sample_dashboard_data):
        """Test playoff bracket data generation."""
        dashboard = Dashboard(data=sample_dashboard_data)
        bracket = dashboard.get_playoff_bracket()
        assert "Eastern" in bracket
        assert "Western" in bracket
        # Verify matchups

    def test_get_statistics_summary(self, sample_dashboard_data):
        """Test statistics summary calculation."""
        dashboard = Dashboard(data=sample_dashboard_data)
        stats = dashboard.get_statistics()
        assert "total_players" in stats
        assert "average_score" in stats
        assert "highest_score" in stats
        assert "lowest_score" in stats

    def test_dashboard_caching(self, sample_dashboard_data):
        """Test dashboard data caching."""
        dashboard = Dashboard(data=sample_dashboard_data, cache_enabled=True)
        # First call
        result1 = dashboard.get_top_players(limit=10)
        # Second call (should use cache)
        result2 = dashboard.get_top_players(limit=10)
        assert result1 == result2

    def test_dashboard_refresh(self, sample_dashboard_data):
        """Test dashboard data refresh."""
        dashboard = Dashboard(data=sample_dashboard_data)
        dashboard.refresh()
        # Verify data is reloaded

    def test_dashboard_error_handling(self):
        """Test dashboard with missing/invalid data."""
        dashboard = Dashboard(data=None)
        # Should handle gracefully

    # Cover all 136 statements
```

#### B. Filters (Priority 1 - Core Functionality)

**filters.py** (86 statements):
```python
# tests/unit/test_filters.py (enhance existing)
class TestFilters:
    """Comprehensive filtering tests."""

    @pytest.fixture
    def sample_players(self):
        """Sample player data for filtering."""
        return [
            Player(name="Alex Ovechkin", team="WSH", position="LW", score=42, birthplace="RUS"),
            Player(name="Sidney Crosby", team="PIT", position="C", score=38, birthplace="CAN"),
            Player(name="Connor McDavid", team="EDM", position="C", score=45, birthplace="CAN"),
            # More players...
        ]

    def test_filter_by_team(self, sample_players):
        """Test filtering players by team."""
        filtered = filter_by_team(sample_players, team="WSH")
        assert all(p.team == "WSH" for p in filtered)
        assert len(filtered) >= 1

    def test_filter_by_position(self, sample_players):
        """Test filtering players by position."""
        centers = filter_by_position(sample_players, position="C")
        assert all(p.position == "C" for p in centers)

    def test_filter_by_score_range(self, sample_players):
        """Test filtering by score range."""
        high_scorers = filter_by_score_range(
            sample_players,
            min_score=40,
            max_score=50
        )
        assert all(40 <= p.score <= 50 for p in high_scorers)

    def test_filter_by_name_search(self, sample_players):
        """Test filtering by name search."""
        results = filter_by_name(sample_players, query="Ovechkin")
        assert len(results) >= 1
        assert "Ovechkin" in results[0].name

    def test_filter_by_name_case_insensitive(self, sample_players):
        """Test case-insensitive name search."""
        results = filter_by_name(sample_players, query="ovechkin")
        assert len(results) >= 1

    def test_filter_by_birthplace(self, sample_players):
        """Test filtering by birthplace/country."""
        canadians = filter_by_birthplace(sample_players, country="CAN")
        assert all(p.birthplace == "CAN" for p in canadians)

    def test_filter_composition(self, sample_players):
        """Test chaining multiple filters."""
        result = filter_by_team(
            filter_by_position(
                filter_by_score_range(sample_players, min_score=40),
                position="C"
            ),
            team="EDM"
        )
        # Should get McDavid (EDM, C, score 45)
        assert len(result) >= 1

    def test_team_filter_by_division(self, sample_teams):
        """Test filtering teams by division."""
        metro = filter_teams_by_division(sample_teams, division="Metropolitan")
        assert all(t.division == "Metropolitan" for t in metro)
        assert len(metro) == 8

    def test_team_filter_by_conference(self, sample_teams):
        """Test filtering teams by conference."""
        eastern = filter_teams_by_conference(sample_teams, conference="Eastern")
        assert all(t.conference == "Eastern" for t in eastern)
        assert len(eastern) == 16

    def test_filter_validation(self, sample_players):
        """Test filter parameter validation."""
        with pytest.raises(ValueError, match="Invalid position"):
            filter_by_position(sample_players, position="INVALID")

    def test_empty_filter_results(self, sample_players):
        """Test filters that match no players."""
        results = filter_by_team(sample_players, team="XXX")
        assert len(results) == 0

    # Cover all 86 statements
```

#### C. Processors (Priority 1 - Business Logic Critical)

**processors/grouping.py** (62 statements):
```python
# tests/unit/test_grouping.py (create new)
class TestGrouping:
    """Test player grouping logic."""

    def test_group_by_birthplace(self, sample_players):
        """Test grouping players by birthplace."""
        groups = group_by_birthplace(sample_players)
        assert "CAN" in groups
        assert "USA" in groups
        assert "RUS" in groups
        # Verify all players are grouped

    def test_group_by_position(self, sample_players):
        """Test grouping players by position."""
        groups = group_by_position(sample_players)
        assert "C" in groups
        assert "LW" in groups
        assert "D" in groups

    def test_group_by_team(self, sample_players):
        """Test grouping players by team."""
        groups = group_by_team(sample_players)
        assert "WSH" in groups
        assert len(groups) <= 32

    def test_group_statistics(self, sample_players):
        """Test group statistics calculation."""
        groups = group_by_birthplace(sample_players)
        stats = calculate_group_stats(groups)
        assert stats["CAN"]["count"] > 0
        assert stats["CAN"]["avg_score"] > 0
        assert stats["CAN"]["total_score"] > 0

    def test_top_scorers_per_group(self, sample_players):
        """Test getting top scorers per group."""
        groups = group_by_birthplace(sample_players)
        top_per_group = get_top_scorers_per_group(groups, limit=5)
        for country, players in top_per_group.items():
            assert len(players) <= 5
            # Verify sorted by score

    def test_group_sorting(self, sample_players):
        """Test group sorting by total score."""
        groups = group_by_birthplace(sample_players)
        sorted_groups = sort_groups_by_score(groups)
        # Verify descending order

    # Cover all 62 statements
```

**processors/playoff_calculator.py** (89 statements):
```python
# tests/unit/test_playoff_calculator.py (create new)
class TestPlayoffCalculator:
    """Test playoff qualification logic."""

    @pytest.fixture
    def sample_standings(self):
        """Sample standings data."""
        return [
            # Teams with scores and divisions
            Team("WSH", "Metropolitan", "Eastern", points=100),
            Team("PIT", "Metropolitan", "Eastern", points=95),
            # ... more teams
        ]

    def test_identify_division_leaders(self, sample_standings):
        """Test identifying division leaders."""
        calc = PlayoffCalculator(standings=sample_standings)
        leaders = calc.get_division_leaders()
        assert len(leaders) == 4  # 4 divisions
        # Verify each is highest in division

    def test_identify_wild_cards(self, sample_standings):
        """Test wild card selection."""
        calc = PlayoffCalculator(standings=sample_standings)
        eastern_wc = calc.get_wild_cards(conference="Eastern")
        western_wc = calc.get_wild_cards(conference="Western")
        assert len(eastern_wc) == 2
        assert len(western_wc) == 2

    def test_playoff_seeding(self, sample_standings):
        """Test conference playoff seeding."""
        calc = PlayoffCalculator(standings=sample_standings)
        eastern_seeds = calc.get_playoff_seeds(conference="Eastern")
        assert len(eastern_seeds) == 8
        # Verify seeding order

    def test_playoff_matchups(self, sample_standings):
        """Test first-round matchup generation."""
        calc = PlayoffCalculator(standings=sample_standings)
        matchups = calc.generate_matchups(conference="Eastern")
        assert len(matchups) == 4  # 4 first-round series
        # 1 vs 8, 2 vs 7, 3 vs 6, 4 vs 5

    def test_tiebreaker_logic(self, sample_standings):
        """Test tiebreaker for teams with same points."""
        # Two teams with identical points
        tied_teams = [
            Team("WSH", points=100, avg_score=25.5),
            Team("PIT", points=100, avg_score=24.3),
        ]
        calc = PlayoffCalculator()
        winner = calc.break_tie(tied_teams)
        assert winner.team == "WSH"  # Higher avg score

    def test_playoff_indicators(self, sample_standings):
        """Test playoff indicator assignment (x, y, z, p, e)."""
        calc = PlayoffCalculator(standings=sample_standings)
        indicators = calc.assign_indicators()
        # y = division leader
        # x = wild card
        # z = conference leader
        # p = Presidents' Trophy
        # e = eliminated

    def test_playoff_bracket_structure(self, sample_standings):
        """Test full playoff bracket generation."""
        calc = PlayoffCalculator(standings=sample_standings)
        bracket = calc.generate_bracket()
        assert "Eastern" in bracket
        assert "Western" in bracket

    def test_edge_cases(self):
        """Test edge cases (ties, insufficient teams, etc.)."""
        # Test with < 8 teams per conference

    # Cover all 89 statements
```

**processors/team_processor.py** (92 statements):
```python
# tests/unit/test_team_processor.py (enhance existing)
class TestTeamProcessor:
    """Test team processing logic."""

    @pytest.fixture
    def mock_api_client(self):
        """Mock API client."""
        client = Mock(spec=APIClientProtocol)
        client.get_standings.return_value = [...]
        client.get_roster.return_value = [...]
        return client

    @pytest.fixture
    def mock_scorer(self):
        """Mock scorer."""
        scorer = Mock(spec=ScorerProtocol)
        scorer.calculate_score.return_value = 25
        return scorer

    def test_fetch_team_data(self, mock_api_client, mock_scorer):
        """Test fetching team data."""
        processor = TeamProcessor(
            api_client=mock_api_client,
            scorer=mock_scorer
        )
        team = processor.fetch_team("WSH")
        assert team.abbrev == "WSH"
        mock_api_client.get_roster.assert_called_once()

    def test_process_roster(self, mock_api_client, mock_scorer):
        """Test processing team roster."""
        processor = TeamProcessor(
            api_client=mock_api_client,
            scorer=mock_scorer
        )
        roster = processor.process_roster("WSH")
        assert len(roster) > 0
        # Verify scores calculated

    def test_calculate_team_score(self, mock_api_client, mock_scorer):
        """Test team score aggregation."""
        processor = TeamProcessor(
            api_client=mock_api_client,
            scorer=mock_scorer
        )
        team_score = processor.calculate_team_score("WSH")
        assert team_score > 0

    def test_concurrent_roster_fetching(self, mock_api_client, mock_scorer):
        """Test concurrent fetching of multiple team rosters."""
        processor = TeamProcessor(
            api_client=mock_api_client,
            scorer=mock_scorer,
            max_workers=5
        )
        teams = ["WSH", "PIT", "EDM", "TOR", "MTL"]
        results = processor.fetch_teams_concurrent(teams)
        assert len(results) == 5

    def test_error_handling_missing_team(self, mock_api_client, mock_scorer):
        """Test handling of missing team."""
        mock_api_client.get_roster.side_effect = NHLApiNotFoundError("Team not found")
        processor = TeamProcessor(
            api_client=mock_api_client,
            scorer=mock_scorer
        )
        with pytest.raises(NHLApiNotFoundError):
            processor.fetch_team("XXX")

    def test_error_handling_api_failure(self, mock_api_client, mock_scorer):
        """Test handling of API failures."""
        mock_api_client.get_roster.side_effect = NHLApiError("API error")
        processor = TeamProcessor(
            api_client=mock_api_client,
            scorer=mock_scorer
        )
        # Should handle gracefully

    def test_team_statistics(self, mock_api_client, mock_scorer):
        """Test team statistics calculation."""
        processor = TeamProcessor(
            api_client=mock_api_client,
            scorer=mock_scorer
        )
        stats = processor.calculate_statistics("WSH")
        assert "total_players" in stats
        assert "total_score" in stats
        assert "avg_score" in stats

    # Cover all 92 statements
```

#### D. Scoring (Priority 2 - Core Algorithm)

**scoring/config.py** (62 statements):
```python
# tests/unit/test_scoring_config.py (enhance existing)
class TestScoringConfig:
    """Test scoring configuration."""

    def test_standard_scrabble_values(self):
        """Test standard Scrabble letter values."""
        config = ScoringConfig.standard()
        assert config.get_value("A") == 1
        assert config.get_value("Q") == 10
        assert config.get_value("Z") == 10

    def test_custom_scoring_system(self):
        """Test custom scoring values."""
        custom_values = {"A": 5, "B": 10, ...}
        config = ScoringConfig(values=custom_values)
        assert config.get_value("A") == 5

    def test_value_validation(self):
        """Test validation of letter values."""
        with pytest.raises(ValueError):
            ScoringConfig(values={"A": -1})  # Negative value

    def test_configuration_loading(self):
        """Test loading configuration from file."""
        config = ScoringConfig.from_file("config.json")
        # Verify loaded values

    def test_default_values(self):
        """Test default value handling."""
        config = ScoringConfig()
        # Missing letters get default value

    # Cover all 62 statements
```

**scoring/scrabble.py** (45 missing statements):
```python
# tests/unit/test_scrabble.py (enhance existing)
class TestScrabbleScorer:
    """Enhanced Scrabble scorer tests."""

    def test_name_normalization(self):
        """Test name normalization (lines 84-85)."""
        scorer = ScrabbleScorer()
        assert scorer.normalize_name("  Alex  ") == "ALEX"
        assert scorer.normalize_name("o'reilly") == "OREILLY"

    def test_special_character_handling(self):
        """Test special character handling (lines 102-103)."""
        scorer = ScrabbleScorer()
        # Hyphens, apostrophes, accents
        score = scorer.calculate_score("Jean-Claude")
        assert score > 0

    def test_case_sensitivity(self):
        """Test case handling (lines 132-133)."""
        scorer = ScrabbleScorer()
        assert scorer.calculate_score("ALEX") == scorer.calculate_score("alex")

    def test_unicode_handling(self):
        """Test Unicode character handling (lines 154-155)."""
        scorer = ScrabbleScorer()
        # Czech, Russian, Swedish names
        score = scorer.calculate_score("Jágr")
        assert score > 0

    def test_batch_scoring(self):
        """Test batch scoring functionality (lines 199-255) - MAJOR GAP."""
        scorer = ScrabbleScorer()
        names = ["Ovechkin", "Crosby", "McDavid", "Matthews"]
        scores = scorer.calculate_batch(names)
        assert len(scores) == 4
        assert all(s > 0 for s in scores.values())

    def test_score_caching(self):
        """Test score caching logic (lines 290-291)."""
        scorer = ScrabbleScorer(cache_enabled=True)
        name = "Ovechkin"
        score1 = scorer.calculate_score(name)
        score2 = scorer.calculate_score(name)  # Should use cache
        assert score1 == score2

    def test_score_validation(self):
        """Test score validation (lines 304-322)."""
        scorer = ScrabbleScorer()
        # Empty name
        with pytest.raises(ValueError):
            scorer.calculate_score("")
        # Invalid characters
        with pytest.raises(ValueError):
            scorer.calculate_score("123")

    def test_edge_cases(self):
        """Test edge cases (lines 330-331)."""
        scorer = ScrabbleScorer()
        # Single letter
        assert scorer.calculate_score("A") == 1
        # Very long name
        long_name = "A" * 100
        score = scorer.calculate_score(long_name)
        assert score == 100

    # Cover all 45 missing statements
```

### 2. Testing Infrastructure

#### Pytest Fixtures (conftest.py enhancements):
```python
# tests/conftest.py

@pytest.fixture
def sample_dashboard_data():
    """Sample dashboard data."""
    return {
        "standings": [...],
        "teams": [...],
        "players": [...],
    }

@pytest.fixture
def sample_players():
    """Sample player list for filtering/grouping."""
    return [
        Player(name="Alex Ovechkin", team="WSH", position="LW", score=42, birthplace="RUS"),
        Player(name="Sidney Crosby", team="PIT", position="C", score=38, birthplace="CAN"),
        # More players...
    ]

@pytest.fixture
def sample_teams():
    """Sample team list."""
    return [
        Team(abbrev="WSH", division="Metropolitan", conference="Eastern", ...),
        # More teams...
    ]
```

### 3. Coverage Targets

- **dashboard.py**: 0% → 95%+
- **filters.py**: 0% → 95%+
- **processors/grouping.py**: 0% → 95%+
- **processors/playoff_calculator.py**: 0% → 95%+
- **processors/team_processor.py**: 0% → 95%+
- **scoring/config.py**: 0% → 95%+
- **scoring/scrabble.py**: 30.38% → 98%+

**Overall target**: Increase coverage from 3.27% to 95%+ for these modules

### 4. Test Organization

```
tests/
├── unit/
│   ├── test_dashboard.py                ✓ enhance (136 statements)
│   ├── test_filters.py                  ✓ enhance (86 statements)
│   ├── test_filters_country.py          ✓ enhance
│   ├── test_scoring_config.py           ✓ enhance (62 statements)
│   ├── test_scrabble.py                 ✓ enhance (45 missing statements)
│   ├── test_scrabble_scorer_custom.py   ✓ keep/enhance
│   ├── test_team_processor.py           ✓ enhance (92 statements)
│   ├── processors/
│   │   ├── test_grouping.py             + create (62 statements)
│   │   └── test_playoff_calculator.py   + create (89 statements)
│   └── scoring/
│       └── test_scrabble_birthplace.py  ✓ keep
└── integration/
    ├── test_dashboard_integration.py    + create
    ├── test_playoff_workflow.py         + create
    └── test_end_to_end_scoring.py       + create
```

## Implementation Steps

1. **Phase 1: Critical Business Logic** (8-10 hours)
   - Enhance tests/unit/test_dashboard.py (136 statements)
   - Enhance tests/unit/test_filters.py (86 statements)
   - User-facing functionality - highest priority

2. **Phase 2: Processors** (8-10 hours)
   - Create tests/unit/processors/test_grouping.py (62 statements)
   - Create tests/unit/processors/test_playoff_calculator.py (89 statements)
   - Enhance tests/unit/test_team_processor.py (92 statements)
   - Core business logic - critical accuracy

3. **Phase 3: Scoring Algorithms** (4-6 hours)
   - Enhance tests/unit/test_scoring_config.py (62 statements)
   - Enhance tests/unit/test_scrabble.py (45 missing statements)
   - Core algorithm - accuracy critical

4. **Phase 4: Integration Testing** (2-4 hours)
   - Create integration test suites
   - Test end-to-end workflows
   - Verify component interactions

5. **Phase 5: Documentation** (2 hours)
   - Update test documentation
   - Add coverage reports to CI
   - Document business logic test patterns

## Testing Strategy

### Unit Tests
- Test each module in isolation
- Mock external dependencies (API client, scorer)
- Test all code paths (happy path, error paths, edge cases)
- Use parametrize for testing multiple inputs
- Test boundary conditions

### Integration Tests
- Test dashboard with real data aggregation
- Test playoff calculator end-to-end
- Test team processor with mock API
- Verify component integration

### Business Logic Testing
- **Accuracy Critical**: Playoff qualification, scoring algorithms
- Test edge cases: ties, insufficient teams, special characters
- Test with real NHL data patterns
- Verify mathematical correctness

### Test Patterns
```python
# Dashboard pattern
def test_dashboard_aggregation(sample_data):
    dashboard = Dashboard(data=sample_data)
    result = dashboard.get_top_players(limit=10)
    assert len(result) == 10
    assert result[0].score >= result[-1].score

# Filter composition pattern
def test_filter_chaining(sample_players):
    result = filter_by_team(
        filter_by_position(sample_players, "C"),
        "WSH"
    )
    assert all(p.team == "WSH" and p.position == "C" for p in result)

# Playoff calculator pattern
def test_playoff_seeding(sample_standings):
    calc = PlayoffCalculator(standings=sample_standings)
    seeds = calc.get_playoff_seeds(conference="Eastern")
    assert seeds[0].seed == 1
    assert seeds[-1].seed == 8
```

## Acceptance Criteria

- [ ] **dashboard.py** coverage: 0% → 95%+
- [ ] **filters.py** coverage: 0% → 95%+
- [ ] **processors/grouping.py** coverage: 0% → 95%+
- [ ] **processors/playoff_calculator.py** coverage: 0% → 95%+
- [ ] **processors/team_processor.py** coverage: 0% → 95%+
- [ ] **scoring/config.py** coverage: 0% → 95%+
- [ ] **scoring/scrabble.py** coverage: 30.38% → 98%+
- [ ] All new tests pass in CI (all platforms: Linux, macOS, Windows)
- [ ] All new tests pass with Python 3.12, 3.13, 3.14, 3.15-dev
- [ ] No test flakiness detected
- [ ] Overall project coverage increases significantly
- [ ] diff-cover shows 100% coverage on new test files
- [ ] All tests have comprehensive docstrings
- [ ] Test code follows project style guidelines (ruff, mypy)
- [ ] Integration tests verify module interactions
- [ ] Business logic accuracy verified with real NHL data patterns
- [ ] Playoff qualification logic matches NHL rules
- [ ] Scoring algorithms produce correct results
- [ ] Documentation updated with testing patterns

## Related Files

### Source Files to Test:
- `src/nhl_scrabble/dashboard.py` - Dashboard aggregation (136 statements)
- `src/nhl_scrabble/filters.py` - Filtering logic (86 statements)
- `src/nhl_scrabble/processors/grouping.py` - Player grouping (62 statements)
- `src/nhl_scrabble/processors/playoff_calculator.py` - Playoff logic (89 statements)
- `src/nhl_scrabble/processors/team_processor.py` - Team processing (92 statements)
- `src/nhl_scrabble/processors/__init__.py` - Processor exports (4 statements)
- `src/nhl_scrabble/scoring/config.py` - Scoring configuration (62 statements)
- `src/nhl_scrabble/scoring/scrabble.py` - Scrabble algorithm (69 statements, 45 untested)

### Test Files to Create/Enhance:
- `tests/unit/test_dashboard.py` - Enhance with 136 statements coverage
- `tests/unit/test_filters.py` - Enhance with 86 statements coverage
- `tests/unit/test_filters_country.py` - Enhance specialization tests
- `tests/unit/test_team_processor.py` - Enhance with 92 statements coverage
- `tests/unit/test_scoring_config.py` - Enhance with 62 statements coverage
- `tests/unit/test_scrabble.py` - Enhance with 45 missing statements
- `tests/unit/test_scrabble_scorer_custom.py` - Keep/enhance custom scorer tests
- `tests/unit/processors/test_grouping.py` - Create with 62 statements coverage
- `tests/unit/processors/test_playoff_calculator.py` - Create with 89 statements coverage
- `tests/unit/scoring/test_scrabble_birthplace.py` - Keep birthplace tests
- `tests/integration/test_dashboard_integration.py` - Create
- `tests/integration/test_playoff_workflow.py` - Create
- `tests/conftest.py` - Add fixtures for dashboard, filters, processors

### Configuration Files:
- `.github/workflows/test.yml` - CI test workflow
- `pyproject.toml` - Test configuration (pytest, coverage)

## Dependencies

- **Complements Tasks 033 & 034**: This task covers business logic modules
- Should be completed alongside or after tasks 033 and 034
- No blocking dependencies - can start immediately
- **HIGH priority** due to business logic criticality

## Additional Notes

### Why This Matters

1. **Business Logic Critical**: These modules determine the correctness of scores, standings, and playoffs
2. **User-Facing**: Dashboard and filters are directly used by end users
3. **Accuracy Required**: Playoff calculations must match NHL rules exactly
4. **Algorithm Correctness**: Scoring algorithms must produce accurate results

### Testing Philosophy

- **Accuracy First**: Business logic must be 100% correct
- **Real Data Patterns**: Test with patterns from real NHL data
- **Edge Cases Critical**: Ties, special characters, missing data
- **Integration Important**: Components must work together correctly

### Comparison with Tasks 033 & 034

**Task 033** (#586):
- Infrastructure modules (config_validators, di, interfaces, search, storage, ui, etc.)
- ~445 statements
- 16-24 hours

**Task 034** (#587):
- Application modules (logging_config, validators, api_server, reports, utils)
- ~642 statements
- 24-32 hours

**Task 035** (this task):
- **Business logic modules** (dashboard, filters, processors, scoring)
- ~576 statements
- 20-28 hours
- **HIGH priority** (business logic critical)

**Combined Impact**:
- ~1,663 statements covered (tasks 033, 034, 035)
- 60-84 hours total effort
- Coverage increase: 90.21% → 96%+ (estimated)

### Platform Compatibility

All tests must pass on:
- Linux (primary CI platform)
- macOS (test for timing issues)
- Windows (test for path/encoding issues)

### Performance Considerations

- Dashboard tests use sample data (fast)
- Filter tests are pure logic (very fast)
- Playoff calculator tests use sample standings (fast)
- Scoring tests are algorithmic (very fast)
- All tests should complete in < 2 minutes total

### NHL Rules Accuracy

Playoff calculator tests must verify:
- Top 3 teams per division qualify
- 2 wild cards per conference
- Correct seeding (1-8)
- Correct matchups (1v8, 2v7, 3v6, 4v5)
- Tiebreaker logic matches NHL rules

### Scoring Accuracy

Scrabble scorer tests must verify:
- Standard Scrabble letter values
- Correct name normalization
- Unicode/special character handling
- Batch scoring efficiency
- Caching correctness

## Implementation Notes

*To be filled during implementation:*
- Actual test patterns discovered
- Challenges with testing specific modules
- Coverage improvements achieved
- Actual effort vs estimated
- Patterns to reuse for future test expansion
- Business logic edge cases discovered
- Playoff calculation accuracy verification
- Scoring algorithm correctness validation
