CLI Module
==========

Command-line interface for NHL Scrabble Score Analyzer.

The CLI module provides the main entry point using Click for command-line argument
parsing and subcommand management.

.. automodule:: nhl_scrabble.cli
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource

Main Command
------------

.. autofunction:: nhl_scrabble.cli.cli

The main CLI entry point that serves as the command group.

Analyze Command
---------------

.. autofunction:: nhl_scrabble.cli.analyze

Run comprehensive NHL roster analysis with customizable output options.

**Options:**

* ``--format`` - Output format (text or json)
* ``--output`` - Output file path
* ``--verbose`` - Enable verbose logging
* ``--top-players`` - Number of top players to display
* ``--top-team-players`` - Number of players per team to display

**Examples:**

.. code-block:: bash

    # Basic usage
    nhl-scrabble analyze

    # JSON output
    nhl-scrabble analyze --format json --output report.json

    # Verbose mode
    nhl-scrabble analyze --verbose

    # Custom display limits
    nhl-scrabble analyze --top-players 50 --top-team-players 10

Usage Patterns
--------------

**Standard Analysis:**

.. code-block:: python

    from nhl_scrabble.cli import analyze
    from click.testing import CliRunner

    runner = CliRunner()
    result = runner.invoke(analyze)

**Custom Configuration:**

.. code-block:: python

    result = runner.invoke(analyze, [
        '--format', 'json',
        '--output', 'report.json',
        '--verbose'
    ])

Related Documentation
---------------------

* :doc:`../tutorials/01-getting-started` - First analysis tutorial
* :doc:`../how-to/customize-output-format` - Customize output
* :doc:`../reference/cli` - Complete CLI reference
