Processors Module
=================

Business logic for team processing and playoff calculations.

The processors module handles aggregation of player scores into team totals and
NHL playoff bracket generation based on Scrabble scores.

.. automodule:: nhl_scrabble.processors
   :members:
   :undoc-members:
   :show-inheritance:

Team Processor
--------------

.. automodule:: nhl_scrabble.processors.team_processor
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource

TeamProcessor
~~~~~~~~~~~~~

.. autoclass:: nhl_scrabble.processors.team_processor.TeamProcessor
   :members:
   :undoc-members:
   :show-inheritance:

Aggregate player scores into team totals.

**Methods:**

* ``process_teams()`` - Process all teams and calculate totals
* ``get_division_standings()`` - Group teams by division
* ``get_conference_standings()`` - Group teams by conference

**Example:**

.. code-block:: python

    from nhl_scrabble.processors import TeamProcessor
    from nhl_scrabble.scoring import ScrabbleScorer

    # Score all players
    scorer = ScrabbleScorer()
    all_players = []
    for team_abbrev, roster in rosters.items():
        all_players.extend(scorer.score_player(p) for p in roster)

    # Process teams
    processor = TeamProcessor()
    team_scores = processor.process_teams(teams, all_players)

    # Get standings
    division_standings = processor.get_division_standings(team_scores)
    conference_standings = processor.get_conference_standings(team_scores)

process_teams
~~~~~~~~~~~~~

.. automethod:: nhl_scrabble.processors.team_processor.TeamProcessor.process_teams

Aggregate player scores by team.

**Parameters:**

* ``teams`` - List of Team objects
* ``player_scores`` - List of PlayerScore objects (all players)

**Returns:**

* List of TeamScore objects sorted by total (descending)

**Example:**

.. code-block:: python

    team_scores = processor.process_teams(teams, all_players)

    for team_score in team_scores[:5]:
        print(f"{team_score.team.name}: {team_score.total} points")
        print(f"  Players: {team_score.player_count}")
        print(f"  Average: {team_score.avg_per_player:.1f}")

get_division_standings
~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: nhl_scrabble.processors.team_processor.TeamProcessor.get_division_standings

Group teams by division with rankings.

**Parameters:**

* ``team_scores`` - List of TeamScore objects

**Returns:**

* Dictionary mapping division names to DivisionStandings objects

**Example:**

.. code-block:: python

    divisions = processor.get_division_standings(team_scores)

    for division_name, standings in divisions.items():
        print(f"\n{division_name} Division:")
        for i, team in enumerate(standings.teams, 1):
            print(f"  {i}. {team.team.name}: {team.total}")

get_conference_standings
~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: nhl_scrabble.processors.team_processor.TeamProcessor.get_conference_standings

Group teams by conference with rankings.

**Parameters:**

* ``team_scores`` - List of TeamScore objects

**Returns:**

* Dictionary mapping conference names to ConferenceStandings objects

**Example:**

.. code-block:: python

    conferences = processor.get_conference_standings(team_scores)

    for conf_name, standings in conferences.items():
        print(f"\n{conf_name} Conference:")
        print(f"  Total: {standings.total}")
        print(f"  Teams: {len(standings.teams)}")
        print(f"  Average: {standings.avg_per_team:.1f}")

Playoff Calculator
------------------

.. automodule:: nhl_scrabble.processors.playoff_calculator
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource

PlayoffCalculator
~~~~~~~~~~~~~~~~~

.. autoclass:: nhl_scrabble.processors.playoff_calculator.PlayoffCalculator
   :members:
   :undoc-members:
   :show-inheritance:

Calculate NHL playoff bracket based on Scrabble scores.

Follows NHL playoff structure:

* 8 teams per conference (16 total)
* 3 division leaders per conference
* 2 wild card teams per conference
* Playoff indicators: y (clinched), x (wild card), z (conference leader), p (Presidents' Trophy)

**Example:**

.. code-block:: python

    from nhl_scrabble.processors import PlayoffCalculator

    calculator = PlayoffCalculator()
    bracket = calculator.calculate_playoff_bracket(team_scores)

    print("Eastern Conference Playoffs:")
    for team in bracket["Eastern"][:8]:
        indicator = team.get("playoff_indicator", "")
        print(f"  {indicator} {team.team.name}: {team.total}")

calculate_playoff_bracket
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: nhl_scrabble.processors.playoff_calculator.PlayoffCalculator.calculate_playoff_bracket

Generate playoff bracket with seeding and indicators.

**Parameters:**

* ``team_scores`` - List of TeamScore objects

**Returns:**

* Dictionary with playoff structure:
  * Conference brackets
  * Division leaders
  * Wild card teams
  * Seeding information

**Example:**

.. code-block:: python

    bracket = calculator.calculate_playoff_bracket(team_scores)

    # Access playoff teams
    eastern_playoffs = bracket["Eastern"][:8]
    western_playoffs = bracket["Western"][:8]

    # Find Presidents' Trophy winner
    all_teams = eastern_playoffs + western_playoffs
    presidents_trophy = max(all_teams, key=lambda t: t.total)

Playoff Indicators
~~~~~~~~~~~~~~~~~~

Teams receive playoff indicators based on standing:

.. list-table::
   :header-rows: 1
   :widths: 10 90

   * - Indicator
     - Meaning
   * - **p**
     - Presidents' Trophy (best overall record)
   * - **z**
     - Conference leader (best in conference)
   * - **y**
     - Division leader (top 3 per division)
   * - **x**
     - Wild card team (4th & 5th best in conference)
   * - **e**
     - Eliminated (not in playoff position)

**Example:**

.. code-block:: python

    for team_score in team_scores:
        indicator = team_score.playoff_indicator
        if indicator == "p":
            print(f"{team_score.team.name} - Presidents' Trophy!")
        elif indicator == "y":
            print(f"{team_score.team.name} - Division Leader")
        elif indicator == "x":
            print(f"{team_score.team.name} - Wild Card")

Tiebreakers
~~~~~~~~~~~

When teams have equal total scores, tiebreakers are applied:

1. **Average points per player** (higher is better)
2. **Alphabetical order** by team abbreviation

**Example:**

.. code-block:: python

    # Two teams with same total
    team_a = TeamScore(total=2000, player_count=25, avg_per_player=80.0)
    team_b = TeamScore(total=2000, player_count=24, avg_per_player=83.3)

    # team_b wins tiebreaker (higher average)

Usage Patterns
--------------

**Complete Workflow:**

.. code-block:: python

    from nhl_scrabble.api import NHLClient
    from nhl_scrabble.scoring import ScrabbleScorer
    from nhl_scrabble.processors import TeamProcessor, PlayoffCalculator
    import asyncio


    async def analyze():
        # Fetch data
        async with NHLClient() as client:
            teams = await client.fetch_all_teams()
            rosters = await client.fetch_all_rosters()

        # Score players
        scorer = ScrabbleScorer()
        all_players = []
        for roster in rosters.values():
            all_players.extend(scorer.score_player(p) for p in roster)

        # Process teams
        processor = TeamProcessor()
        team_scores = processor.process_teams(teams, all_players)

        # Calculate playoffs
        calculator = PlayoffCalculator()
        bracket = calculator.calculate_playoff_bracket(team_scores)

        return team_scores, bracket


    team_scores, bracket = asyncio.run(analyze())

**Division Analysis:**

.. code-block:: python

    processor = TeamProcessor()
    divisions = processor.get_division_standings(team_scores)

    # Find strongest division
    strongest = max(divisions.items(), key=lambda x: x[1].total)
    print(f"Strongest division: {strongest[0]} ({strongest[1].total} points)")

**Playoff Matchups:**

.. code-block:: python

    calculator = PlayoffCalculator()
    bracket = calculator.calculate_playoff_bracket(team_scores)

    # First round matchups (simplified)
    eastern = bracket["Eastern"][:8]
    print("Eastern Conference First Round:")
    print(f"  {eastern[0].team.name} vs {eastern[7].team.name}")
    print(f"  {eastern[1].team.name} vs {eastern[6].team.name}")
    print(f"  {eastern[2].team.name} vs {eastern[5].team.name}")
    print(f"  {eastern[3].team.name} vs {eastern[4].team.name}")

Related Documentation
---------------------

* :doc:`models` - Team and standings models
* :doc:`scoring` - Scrabble scoring logic
* :doc:`../explanation/architecture` - System design
* :doc:`../tutorials/02-understanding-output` - Understanding playoff brackets
