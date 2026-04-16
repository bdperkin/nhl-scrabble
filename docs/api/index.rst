API Reference
=============

Complete API documentation auto-generated from docstrings.

.. toctree::
   :maxdepth: 2
   :caption: API Modules

   cli
   models
   api
   scoring
   processors
   reports

Package Overview
----------------

The NHL Scrabble package is organized into several modules:

* :doc:`cli` - Command-line interface (Click)
* :doc:`models` - Data models (Pydantic)
* :doc:`api` - NHL API client
* :doc:`scoring` - Scrabble scoring logic
* :doc:`processors` - Business logic (team processing, playoff calculation)
* :doc:`reports` - Report generators

CLI Module
----------

.. automodule:: nhl_scrabble.cli
   :members:
   :undoc-members:
   :show-inheritance:

Models Module
-------------

.. automodule:: nhl_scrabble.models
   :members:
   :undoc-members:
   :show-inheritance:

Player Model
~~~~~~~~~~~~

.. autoclass:: nhl_scrabble.models.player.Player
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: nhl_scrabble.models.player.PlayerScore
   :members:
   :undoc-members:
   :show-inheritance:

Team Model
~~~~~~~~~~

.. autoclass:: nhl_scrabble.models.team.Team
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: nhl_scrabble.models.team.TeamScore
   :members:
   :undoc-members:
   :show-inheritance:

Standings Models
~~~~~~~~~~~~~~~~

.. autoclass:: nhl_scrabble.models.standings.DivisionStandings
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: nhl_scrabble.models.standings.ConferenceStandings
   :members:
   :undoc-members:
   :show-inheritance:

API Module
----------

.. automodule:: nhl_scrabble.api
   :members:
   :undoc-members:
   :show-inheritance:

NHL Client
~~~~~~~~~~

.. autoclass:: nhl_scrabble.api.nhl_client.NHLClient
   :members:
   :undoc-members:
   :show-inheritance:

Scoring Module
--------------

.. automodule:: nhl_scrabble.scoring
   :members:
   :undoc-members:
   :show-inheritance:

Scrabble Scorer
~~~~~~~~~~~~~~~

.. autoclass:: nhl_scrabble.scoring.scrabble.ScrabbleScorer
   :members:
   :undoc-members:
   :show-inheritance:

Processors Module
-----------------

.. automodule:: nhl_scrabble.processors
   :members:
   :undoc-members:
   :show-inheritance:

Team Processor
~~~~~~~~~~~~~~

.. autoclass:: nhl_scrabble.processors.team_processor.TeamProcessor
   :members:
   :undoc-members:
   :show-inheritance:

Playoff Calculator
~~~~~~~~~~~~~~~~~~

.. autoclass:: nhl_scrabble.processors.playoff_calculator.PlayoffCalculator
   :members:
   :undoc-members:
   :show-inheritance:

Reports Module
--------------

.. automodule:: nhl_scrabble.reports
   :members:
   :undoc-members:
   :show-inheritance:

Base Report
~~~~~~~~~~~

.. autoclass:: nhl_scrabble.reports.base.BaseReport
   :members:
   :undoc-members:
   :show-inheritance:

Conference Report
~~~~~~~~~~~~~~~~~

.. autoclass:: nhl_scrabble.reports.conference_report.ConferenceReport
   :members:
   :undoc-members:
   :show-inheritance:

Division Report
~~~~~~~~~~~~~~~

.. autoclass:: nhl_scrabble.reports.division_report.DivisionReport
   :members:
   :undoc-members:
   :show-inheritance:

Playoff Report
~~~~~~~~~~~~~~

.. autoclass:: nhl_scrabble.reports.playoff_report.PlayoffReport
   :members:
   :undoc-members:
   :show-inheritance:

Team Report
~~~~~~~~~~~

.. autoclass:: nhl_scrabble.reports.team_report.TeamReport
   :members:
   :undoc-members:
   :show-inheritance:

Stats Report
~~~~~~~~~~~~

.. autoclass:: nhl_scrabble.reports.stats_report.StatsReport
   :members:
   :undoc-members:
   :show-inheritance:
