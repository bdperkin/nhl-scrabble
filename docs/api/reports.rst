Reports Module
==============

Report generators for displaying NHL Scrabble analysis results.

The reports module provides various report formats for visualizing team standings,
playoff brackets, and statistics using Rich for terminal output.

.. automodule:: nhl_scrabble.reports
   :members:
   :undoc-members:
   :show-inheritance:

Base Report
-----------

.. automodule:: nhl_scrabble.reports.base
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource

BaseReport
~~~~~~~~~~

.. autoclass:: nhl_scrabble.reports.base.BaseReport
   :members:
   :undoc-members:
   :show-inheritance:

Abstract base class for all report generators.

All report classes inherit from BaseReport and implement the ``generate()`` method.

**Subclasses:**

* :class:`~nhl_scrabble.reports.conference_report.ConferenceReport`
* :class:`~nhl_scrabble.reports.division_report.DivisionReport`
* :class:`~nhl_scrabble.reports.playoff_report.PlayoffReport`
* :class:`~nhl_scrabble.reports.team_report.TeamReport`
* :class:`~nhl_scrabble.reports.stats_report.StatsReport`

Conference Report
-----------------

.. automodule:: nhl_scrabble.reports.conference_report
   :members:
   :undoc-members:
   :show-inheritance:

ConferenceReport
~~~~~~~~~~~~~~~~

.. autoclass:: nhl_scrabble.reports.conference_report.ConferenceReport
   :members:
   :undoc-members:
   :show-inheritance:

Generate conference standings report.

**Output Format:**

.. code-block:: text

    EASTERN CONFERENCE STANDINGS
    ════════════════════════════════════════════════════════════════

    Total Points: 32,456
    Total Teams: 16
    Average per Team: 2,028.5

    Rank  Team                          Total    Avg/Player  Players
    ────────────────────────────────────────────────────────────────
      1   Toronto Maple Leafs           2,234      93.1       24
      2   Boston Bruins                 2,189      91.2       24
      3   Tampa Bay Lightning           2,145      89.4       24
    ...

**Example:**

.. code-block:: python

    from nhl_scrabble.reports import ConferenceReport

    report = ConferenceReport(conference_standings)
    report.generate()

Division Report
---------------

.. automodule:: nhl_scrabble.reports.division_report
   :members:
   :undoc-members:
   :show-inheritance:

DivisionReport
~~~~~~~~~~~~~~

.. autoclass:: nhl_scrabble.reports.division_report.DivisionReport
   :members:
   :undoc-members:
   :show-inheritance:

Generate division standings report.

**Output Format:**

.. code-block:: text

    ATLANTIC DIVISION STANDINGS
    ════════════════════════════════════════════════════════════════

    Total Points: 16,234
    Total Teams: 8
    Average per Team: 2,029.3

    Rank  Team                          Total    Avg/Player  Players
    ────────────────────────────────────────────────────────────────
    y 1   Toronto Maple Leafs           2,234      93.1       24
    y 2   Boston Bruins                 2,189      91.2       24
    y 3   Tampa Bay Lightning           2,145      89.4       24
    ...

**Example:**

.. code-block:: python

    from nhl_scrabble.reports import DivisionReport

    report = DivisionReport(division_standings)
    report.generate()

Playoff Report
--------------

.. automodule:: nhl_scrabble.reports.playoff_report
   :members:
   :undoc-members:
   :show-inheritance:

PlayoffReport
~~~~~~~~~~~~~

.. autoclass:: nhl_scrabble.reports.playoff_report.PlayoffReport
   :members:
   :undoc-members:
   :show-inheritance:

Generate playoff bracket report.

**Output Format:**

.. code-block:: text

    NHL SCRABBLE PLAYOFF BRACKET
    ════════════════════════════════════════════════════════════════

    EASTERN CONFERENCE
    ────────────────────────────────────────────────────────────────
    p 1  Toronto Maple Leafs            2,234
    y 2  Boston Bruins                  2,189
    y 3  Tampa Bay Lightning            2,145
    x 4  Florida Panthers               2,098
    x 5  New York Rangers               2,067
      6  Carolina Hurricanes            2,045
      7  New Jersey Devils              2,023
      8  Pittsburgh Penguins            2,001

    WESTERN CONFERENCE
    ────────────────────────────────────────────────────────────────
    ...

**Playoff Indicators:**

* **p** - Presidents' Trophy (best overall)
* **z** - Conference leader
* **y** - Division leader
* **x** - Wild card team
* **e** - Eliminated

**Example:**

.. code-block:: python

    from nhl_scrabble.reports import PlayoffReport

    report = PlayoffReport(playoff_bracket)
    report.generate()

Team Report
-----------

.. automodule:: nhl_scrabble.reports.team_report
   :members:
   :undoc-members:
   :show-inheritance:

TeamReport
~~~~~~~~~~

.. autoclass:: nhl_scrabble.reports.team_report.TeamReport
   :members:
   :undoc-members:
   :show-inheritance:

Generate detailed team roster report.

**Output Format:**

.. code-block:: text

    TORONTO MAPLE LEAFS - DETAILED ROSTER
    ════════════════════════════════════════════════════════════════

    Team Total: 2,234 points
    Roster Size: 24 players
    Average per Player: 93.1 points

    Top Players:
    Rank  Player                   Pos    First   Last   Total
    ────────────────────────────────────────────────────────────────
      1   William Nylander         RW       65     59     124
      2   Auston Matthews          C        67     51     118
      3   Mitchell Marner          RW       63     50     113
    ...

**Example:**

.. code-block:: python

    from nhl_scrabble.reports import TeamReport

    # Report for specific team
    tor_team = next(t for t in team_scores if t.team.abbrev == "TOR")
    report = TeamReport(tor_team, top_n=10)
    report.generate()

Stats Report
------------

.. automodule:: nhl_scrabble.reports.stats_report
   :members:
   :undoc-members:
   :show-inheritance:

StatsReport
~~~~~~~~~~~

.. autoclass:: nhl_scrabble.reports.stats_report.StatsReport
   :members:
   :undoc-members:
   :show-inheritance:

Generate overall statistics report.

**Output Format:**

.. code-block:: text

    NHL SCRABBLE STATISTICS
    ════════════════════════════════════════════════════════════════

    Overall Statistics:
      Total Players: 768
      Total Teams: 32
      Average Players per Team: 24.0
      League Total Score: 71,456
      League Average Score: 93.1

    Top Individual Scores:
    Rank  Player                   Team   First   Last   Total
    ────────────────────────────────────────────────────────────────
      1   William Nylander         TOR      65     59     124
      2   Quinn Hughes             VAN      53     68     121
      3   Artemi Panarin           NYR      54     65     119
    ...

**Example:**

.. code-block:: python

    from nhl_scrabble.reports import StatsReport

    report = StatsReport(all_player_scores, team_scores, top_n=20)
    report.generate()

Usage Patterns
--------------

**Generate All Reports:**

.. code-block:: python

    from nhl_scrabble.reports import ConferenceReport, DivisionReport, PlayoffReport, StatsReport

    # Conference standings
    for conf_name, standings in conference_standings.items():
        report = ConferenceReport({conf_name: standings})
        report.generate()

    # Division standings
    for div_name, standings in division_standings.items():
        report = DivisionReport({div_name: standings})
        report.generate()

    # Playoff bracket
    playoff_report = PlayoffReport(playoff_bracket)
    playoff_report.generate()

    # Overall statistics
    stats_report = StatsReport(all_players, team_scores)
    stats_report.generate()

**Custom Report Output:**

.. code-block:: python

    from rich.console import Console
    import io

    # Capture report output
    string_io = io.StringIO()
    console = Console(file=string_io, force_terminal=True)

    report = ConferenceReport(conference_standings)
    report.generate()  # Uses default console

    # Get output as string
    output = string_io.getvalue()

**JSON Export:**

While reports generate text/terminal output, you can export the underlying
data structures as JSON:

.. code-block:: python

    import json
    from nhl_scrabble.models import TeamScore


    # Convert to dict for JSON serialization
    def team_score_to_dict(ts: TeamScore) -> dict:
        return {
            "team": ts.team.name,
            "total": ts.total,
            "avg_per_player": ts.avg_per_player,
            "player_count": ts.player_count,
            "players": [
                {"name": f"{ps.player.firstName} {ps.player.lastName}", "score": ps.total}
                for ps in ts.player_scores
            ],
        }


    # Export team scores
    data = [team_score_to_dict(ts) for ts in team_scores]
    with open("team_scores.json", "w") as f:
        json.dump(data, f, indent=2)

Rich Console Features
---------------------

All reports use Rich for enhanced terminal output:

* **Colors** - Team names, scores, headers
* **Tables** - Aligned columns with borders
* **Formatting** - Bold, italic, underline for emphasis
* **Unicode** - Box drawing characters for visual appeal

**Example with Rich:**

.. code-block:: python

    from rich.console import Console
    from rich.table import Table

    console = Console()

    table = Table(title="Top Scorers")
    table.add_column("Rank", justify="right")
    table.add_column("Player")
    table.add_column("Score", justify="right")

    for i, ps in enumerate(top_players[:10], 1):
        table.add_row(str(i), f"{ps.player.firstName} {ps.player.lastName}", str(ps.total))

    console.print(table)

Related Documentation
---------------------

* :doc:`../how-to/customize-output-format` - Customize report output
* :doc:`../how-to/export-to-json` - Export data as JSON
* :doc:`models` - Data models used in reports
* :doc:`processors` - Data processing for reports
* :doc:`../tutorials/02-understanding-output` - Understanding report content
