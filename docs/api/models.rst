Models Module
=============

Pydantic data models for NHL Scrabble Score Analyzer.

The models module provides type-safe data structures using Pydantic for validation,
serialization, and documentation.

Overview
--------

.. automodule:: nhl_scrabble.models
   :members:
   :undoc-members:
   :show-inheritance:

Player Models
-------------

.. automodule:: nhl_scrabble.models.player
   :members:
   :undoc-members:
   :show-inheritance:

Player
~~~~~~

.. autoclass:: nhl_scrabble.models.player.Player
   :members:
   :undoc-members:
   :show-inheritance:

Base player information from NHL API.

**Fields:**

* ``id`` - Player ID
* ``firstName`` - Player's first name
* ``lastName`` - Player's last name
* ``sweaterNumber`` - Jersey number (optional)
* ``positionCode`` - Position code (e.g., 'C', 'LW', 'RW', 'D', 'G')
* ``headshot`` - URL to player headshot image

PlayerScore
~~~~~~~~~~~

.. autoclass:: nhl_scrabble.models.player.PlayerScore
   :members:
   :undoc-members:
   :show-inheritance:

Player with calculated Scrabble score.

**Fields:**

* ``player`` - Player object
* ``first_score`` - Score for first name
* ``last_score`` - Score for last name
* ``total`` - Total combined score

**Example:**

.. code-block:: python

    from nhl_scrabble.models.player import Player, PlayerScore
    from nhl_scrabble.scoring import ScrabbleScorer

    player = Player(
        id=8478402, firstName="Alexander", lastName="Ovechkin", sweaterNumber=8, positionCode="LW"
    )

    scorer = ScrabbleScorer()
    player_score = scorer.score_player(player)
    print(f"{player_score.player.firstName} {player_score.player.lastName}: {player_score.total}")
    # Output: Alexander Ovechkin: 45

Team Models
-----------

.. automodule:: nhl_scrabble.models.team
   :members:
   :undoc-members:
   :show-inheritance:

Team
~~~~

.. autoclass:: nhl_scrabble.models.team.Team
   :members:
   :undoc-members:
   :show-inheritance:

NHL team information.

**Fields:**

* ``id`` - Team ID
* ``abbrev`` - Team abbreviation (e.g., 'TOR', 'MTL')
* ``name`` - Full team name
* ``division`` - Division name
* ``conference`` - Conference name
* ``logo`` - URL to team logo

TeamScore
~~~~~~~~~

.. autoclass:: nhl_scrabble.models.team.TeamScore
   :members:
   :undoc-members:
   :show-inheritance:

Team with aggregated player scores.

**Fields:**

* ``team`` - Team object
* ``player_scores`` - List of PlayerScore objects
* ``total`` - Total team score
* ``avg_per_player`` - Average score per player
* ``player_count`` - Number of players

**Example:**

.. code-block:: python

    from nhl_scrabble.processors import TeamProcessor

    processor = TeamProcessor()
    team_scores = processor.process_teams(teams, all_players)

    for team_score in team_scores:
        print(f"{team_score.team.name}: {team_score.total} points")

Standings Models
----------------

.. automodule:: nhl_scrabble.models.standings
   :members:
   :undoc-members:
   :show-inheritance:

DivisionStandings
~~~~~~~~~~~~~~~~~

.. autoclass:: nhl_scrabble.models.standings.DivisionStandings
   :members:
   :undoc-members:
   :show-inheritance:

Division standings with team rankings.

**Fields:**

* ``name`` - Division name
* ``teams`` - List of TeamScore objects
* ``total`` - Total division score
* ``player_count`` - Total players in division
* ``avg_per_team`` - Average score per team

ConferenceStandings
~~~~~~~~~~~~~~~~~~~

.. autoclass:: nhl_scrabble.models.standings.ConferenceStandings
   :members:
   :undoc-members:
   :show-inheritance:

Conference standings with team rankings.

**Fields:**

* ``name`` - Conference name
* ``teams`` - List of TeamScore objects
* ``total`` - Total conference score
* ``player_count`` - Total players in conference
* ``avg_per_team`` - Average score per team

Related Documentation
---------------------

* :doc:`scoring` - Scrabble scoring logic
* :doc:`processors` - Team processing and aggregation
* :doc:`../explanation/architecture` - System design
