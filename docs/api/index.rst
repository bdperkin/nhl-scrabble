API Reference
=============

Complete Python API documentation auto-generated from docstrings.

This section provides comprehensive documentation for all Python modules, classes,
and functions in the NHL Scrabble package.

.. toctree::
   :maxdepth: 2
   :caption: API Modules

   cli
   models
   nhl-api
   scoring
   processors
   reports

Package Overview
----------------

The NHL Scrabble package is organized into six main modules:

Command-Line Interface
~~~~~~~~~~~~~~~~~~~~~~

:doc:`cli`
   Click-based CLI with analyze command and customizable options.

Data Models
~~~~~~~~~~~

:doc:`models`
   Pydantic models for type-safe data structures:

   * **Player models** - Player, PlayerScore
   * **Team models** - Team, TeamScore
   * **Standings models** - DivisionStandings, ConferenceStandings

NHL API Client
~~~~~~~~~~~~~~

:doc:`nhl-api`
   Async HTTP client for NHL API integration:

   * Automatic retry with exponential backoff
   * Rate limiting and timeout handling
   * Session management with context manager
   * Comprehensive error handling

Scoring Logic
~~~~~~~~~~~~~

:doc:`scoring`
   Scrabble letter value calculations:

   * Standard Scrabble point values (A=1, Z=10, etc.)
   * Player name scoring with breakdown
   * Case-insensitive text scoring

Business Logic
~~~~~~~~~~~~~~

:doc:`processors`
   Team aggregation and playoff calculations:

   * **TeamProcessor** - Aggregate player scores into team totals
   * **PlayoffCalculator** - Generate NHL playoff bracket

Report Generators
~~~~~~~~~~~~~~~~~

:doc:`reports`
   Rich terminal output formatters:

   * **ConferenceReport** - Conference standings
   * **DivisionReport** - Division standings
   * **PlayoffReport** - Playoff bracket
   * **TeamReport** - Detailed team roster
   * **StatsReport** - Overall statistics

Module Dependency Graph
-----------------------

.. code-block:: text

    ┌─────────┐
    │   CLI   │
    └────┬────┘
         │
         ├─────> ┌──────────┐      ┌─────────┐
         │       │ NHL API  │─────>│ Models  │
         │       └──────────┘      └─────────┘
         │                              │
         ├─────> ┌─────────┐            │
         │       │ Scoring │<───────────┘
         │       └─────────┘
         │             │
         ├─────> ┌────────────┐
         │       │ Processors │
         │       └────────────┘
         │             │
         └─────> ┌─────────┐
                 │ Reports │
                 └─────────┘

Quick Example
-------------

Complete workflow using all modules:

.. code-block:: python

    from nhl_scrabble.api import NHLClient
    from nhl_scrabble.scoring import ScrabbleScorer
    from nhl_scrabble.processors import TeamProcessor, PlayoffCalculator
    from nhl_scrabble.reports import ConferenceReport, PlayoffReport, StatsReport
    import asyncio


    async def analyze():
        # 1. Fetch NHL data
        async with NHLClient() as client:
            teams = await client.fetch_all_teams()
            rosters = await client.fetch_all_rosters()

        # 2. Score all players
        scorer = ScrabbleScorer()
        all_players = []
        for roster in rosters.values():
            all_players.extend(scorer.score_player(p) for p in roster)

        # 3. Process teams
        processor = TeamProcessor()
        team_scores = processor.process_teams(teams, all_players)
        conference_standings = processor.get_conference_standings(team_scores)

        # 4. Calculate playoffs
        calculator = PlayoffCalculator()
        playoff_bracket = calculator.calculate_playoff_bracket(team_scores)

        # 5. Generate reports
        ConferenceReport(conference_standings).generate()
        PlayoffReport(playoff_bracket).generate()
        StatsReport(all_players, team_scores).generate()


    # Run the analysis
    asyncio.run(analyze())

Type Hints and Type Safety
---------------------------

All modules use comprehensive type hints for IDE support and type checking:

.. code-block:: python

    from nhl_scrabble.models import Player, PlayerScore
    from nhl_scrabble.scoring import ScrabbleScorer

    # Type hints provide autocomplete and error detection
    scorer: ScrabbleScorer = ScrabbleScorer()
    player: Player = Player(id=1, firstName="Alex", lastName="Ovechkin")
    score: PlayerScore = scorer.score_player(player)

    # MyPy validates types
    reveal_type(score.total)  # Revealed type is 'int'

Async/Await Support
-------------------

The NHL API client uses async/await for efficient I/O:

.. code-block:: python

    import asyncio
    from nhl_scrabble.api import NHLClient


    async def fetch_parallel():
        """Fetch multiple teams in parallel."""
        async with NHLClient() as client:
            # Fetch sequentially
            tor = await client.fetch_team_roster("TOR")
            mtl = await client.fetch_team_roster("MTL")

            # Or use asyncio.gather for parallel fetching
            tasks = [
                client.fetch_team_roster("TOR"),
                client.fetch_team_roster("MTL"),
                client.fetch_team_roster("NYR"),
            ]
            results = await asyncio.gather(*tasks)

        return results


    rosters = asyncio.run(fetch_parallel())

Pydantic Data Validation
-------------------------

All data models use Pydantic for automatic validation:

.. code-block:: python

    from nhl_scrabble.models import Player
    from pydantic import ValidationError

    try:
        # Valid player
        player = Player(id=1, firstName="Alex", lastName="Ovechkin", positionCode="LW")

        # Invalid - missing required fields
        bad_player = Player(firstName="Alex")  # Raises ValidationError

    except ValidationError as e:
        print(e)

Related Documentation
---------------------

* :doc:`../tutorials/index` - Learn by doing with step-by-step lessons
* :doc:`../how-to/add-report-type` - Create custom report generators
* :doc:`../explanation/architecture` - System design and structure
* :doc:`../reference/cli` - CLI reference documentation
