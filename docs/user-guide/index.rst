User Guide
==========

Comprehensive guides for using NHL Scrabble Score Analyzer.

.. toctree::
   :maxdepth: 2
   :caption: User Guides

   basic-usage
   output-formats
   configuration
   troubleshooting

Basic Usage
-----------

The ``nhl-scrabble`` command provides the main interface:

.. code-block:: text

    # Run nhl-scrabble --help to see all options
    $ nhl-scrabble --help

Analyze Command
~~~~~~~~~~~~~~~

Run the NHL roster analysis:

.. code-block:: bash

    nhl-scrabble analyze

Options:

* ``--format [text|json]`` - Output format (default: text)
* ``-o, --output PATH`` - Output file (default: stdout)
* ``-v, --verbose`` - Enable verbose logging
* ``--top-players INTEGER`` - Number of top players to display (default: 20)
* ``--top-team-players INTEGER`` - Number of players per team (default: 5)

Output Formats
--------------

Text Output
~~~~~~~~~~~

Human-readable text format with color and formatting:

.. code-block:: bash

    nhl-scrabble analyze

JSON Output
~~~~~~~~~~~

Machine-readable JSON for integration with other tools:

.. code-block:: bash

    nhl-scrabble analyze --format json --output report.json

JSON structure:

.. code-block:: json

    {
        "top_players": [...],
        "conference_standings": {...},
        "division_standings": {...},
        "playoff_bracket": {...},
        "statistics": {...}
    }

Configuration
-------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

Configure NHL Scrabble via environment variables:

.. code-block:: bash

    export NHL_SCRABBLE_API_TIMEOUT=15
    export NHL_SCRABBLE_API_RETRIES=5
    export NHL_SCRABBLE_RATE_LIMIT_DELAY=0.5
    export NHL_SCRABBLE_TOP_PLAYERS=30
    export NHL_SCRABBLE_VERBOSE=true

See :doc:`../reference/configuration` for complete list.

.env File
~~~~~~~~~

Create a ``.env`` file in your project directory:

.. code-block:: ini

    NHL_SCRABBLE_API_TIMEOUT=15
    NHL_SCRABBLE_VERBOSE=true

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**API Timeout Errors**

If you see timeout errors, increase the timeout:

.. code-block:: bash

    export NHL_SCRABBLE_API_TIMEOUT=30

**Rate Limiting**

If requests are rate-limited, increase the delay:

.. code-block:: bash

    export NHL_SCRABBLE_RATE_LIMIT_DELAY=1.0

**Network Errors**

Check your internet connection and NHL API availability:

.. code-block:: bash

    curl -I https://api-web.nhle.com/v1/standings/now

See :doc:`troubleshooting` for more solutions.
