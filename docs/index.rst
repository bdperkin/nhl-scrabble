NHL Scrabble Score Analyzer Documentation
==========================================

.. image:: https://github.com/bdperkin/nhl-scrabble/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/bdperkin/nhl-scrabble/actions/workflows/ci.yml
   :alt: CI Status

.. image:: https://codecov.io/gh/bdperkin/nhl-scrabble/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/bdperkin/nhl-scrabble
   :alt: Code Coverage

.. image:: https://img.shields.io/badge/python-3.10--3.13-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python 3.10-3.13

A Python application that fetches current NHL roster data and calculates
"Scrabble scores" for player names based on standard Scrabble letter values.

.. grid:: 2
    :gutter: 3

    .. grid-item-card:: 🚀 Getting Started
        :link: getting-started/index
        :link-type: doc

        New to NHL Scrabble? Start here to install and run your first analysis.

    .. grid-item-card:: 📖 User Guide
        :link: user-guide/index
        :link-type: doc

        Detailed guides for using NHL Scrabble, customization, and troubleshooting.

    .. grid-item-card:: 🔧 API Reference
        :link: api/index
        :link-type: doc

        Complete API documentation auto-generated from docstrings.

    .. grid-item-card:: 💻 Development
        :link: development/index
        :link-type: doc

        Contributing, testing, and development environment setup.

Features
--------

🏒 **Live NHL Data**
   Fetches current roster data from the official NHL API

📊 **Comprehensive Reports**
   Multiple report types including conference, division, playoff brackets, and statistics

🎯 **Flexible Output**
   Text or JSON format output

⚙️ **Configurable**
   Customize via environment variables or command-line options

🧪 **Well-Tested**
   Comprehensive test suite with >90% coverage on core modules

📦 **Modern Python**
   Type hints, Pydantic models, and best practices

Quick Example
-------------

.. code-block:: bash

    # Install
    pip install nhl-scrabble

    # Run analysis
    nhl-scrabble analyze

    # JSON output
    nhl-scrabble analyze --format json --output report.json

.. code-block:: text

    # Run nhl-scrabble --help to see all options
    $ nhl-scrabble --help

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: User Documentation

   getting-started/index
   user-guide/index
   reference/index

.. toctree::
   :maxdepth: 2
   :caption: API Documentation

   api/index

.. toctree::
   :maxdepth: 2
   :caption: Development

   development/index

.. toctree::
   :maxdepth: 1
   :caption: Project Links

   GitHub Repository <https://github.com/bdperkin/nhl-scrabble>
   Issue Tracker <https://github.com/bdperkin/nhl-scrabble/issues>
   Changelog <https://github.com/bdperkin/nhl-scrabble/blob/main/CHANGELOG.md>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
