Getting Started
===============

Welcome to NHL Scrabble! This guide helps you install and run your first analysis.

.. toctree::
   :maxdepth: 2
   :caption: Guides

   installation
   quickstart
   first-analysis

Installation
------------

The easiest way to install NHL Scrabble is via pip:

.. code-block:: bash

    pip install nhl-scrabble

For faster installation using UV:

.. code-block:: bash

    uv pip install nhl-scrabble

From Source
~~~~~~~~~~~

To install from source:

.. code-block:: bash

    git clone https://github.com/bdperkin/nhl-scrabble.git
    cd nhl-scrabble
    pip install -e .

Quick Start
-----------

Run your first analysis:

.. code-block:: bash

    nhl-scrabble analyze

This will:

1. Fetch current NHL roster data from the official API
2. Calculate Scrabble scores for all players
3. Generate comprehensive team standings
4. Display playoff bracket based on scores

Example Output
~~~~~~~~~~~~~~

.. code-block:: text

    NHL Scrabble Score Analyzer
    ============================

    Top 20 Individual Player Scores
    --------------------------------
    1. Alexander Ovechkin (WSH): 45 points
    2. Sidney Crosby (PIT): 42 points
    ...

    Conference Standings
    --------------------
    Eastern Conference:
    1. Boston Bruins: 1,234 total points
    ...

See :doc:`first-analysis` for detailed explanation of the output.

Next Steps
----------

* :doc:`first-analysis` - Understand the analysis output
* :doc:`../user-guide/index` - Learn advanced usage
* :doc:`../reference/index` - Explore all CLI options
