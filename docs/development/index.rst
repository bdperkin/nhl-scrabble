Development Guide
=================

Contributing to NHL Scrabble Score Analyzer.

.. toctree::
   :maxdepth: 2
   :caption: Development Documentation

   ../how-to/contribute-code
   ../how-to/run-tests
   ../how-to/setup-pre-commit-hooks
   ../explanation/architecture
   ../explanation/testing-philosophy

Quick Links for Contributors
-----------------------------

**Getting Started**
   :doc:`../how-to/contribute-code`
      Complete workflow for submitting code contributions

   :doc:`../how-to/setup-pre-commit-hooks`
      Configure 55 automated quality checks

**Testing**
   :doc:`../how-to/run-tests`
      Run tests with pytest, tox, and coverage

   :doc:`../explanation/testing-philosophy`
      Understand the testing strategy and quality goals

**Architecture**
   :doc:`../explanation/architecture`
      System design and component organization

   :doc:`../explanation/nhl-api-strategy`
      NHL API integration approach

**Additional Resources**
   :doc:`../reference/makefile`
      55 Makefile targets for automation

   :doc:`../tutorials/03-first-contribution`
      Step-by-step first contribution tutorial

Development Setup
-----------------

Quick Start
~~~~~~~~~~~

.. code-block:: bash

    # Clone repository
    git clone https://github.com/bdperkin/nhl-scrabble.git
    cd nhl-scrabble

    # Setup with UV (10-100x faster)
    make uv-init
    source .venv/bin/activate

    # Or standard setup
    make init
    source .venv/bin/activate

    # Verify setup
    make check

Testing
-------

.. code-block:: bash

    # Quick test run
    pytest

    # With coverage
    make test-cov

    # All Python versions (uses tox-uv automatically)
    make tox

    # Parallel testing (10x faster)
    make tox-parallel

Code Quality
------------

.. code-block:: bash

    # Run all quality checks
    make quality

    # Individual checks
    make ruff-check
    make ruff-format
    make mypy

    # Pre-commit hooks (55 checks)
    make pre-commit

Code Style Standards
--------------------

* **PEP 8** - Python style guide (line length: 100)
* **Type hints** - All functions annotated (mypy strict mode)
* **Docstrings** - 100% coverage required (Google style)
* **Ruff** - ALL rules enabled (comprehensive linting)
* **Pre-commit hooks** - 55 automated checks before commit

Example Code
~~~~~~~~~~~~

.. code-block:: python

    def calculate_score(text: str) -> int:
        """Calculate Scrabble score for text.

        Args:
            text: Input text to score (case-insensitive).

        Returns:
            Total score as sum of letter values.

        Example:
            >>> calculate_score("HELLO")
            8

        Raises:
            ValueError: If text is empty.
        """
        if not text:
            raise ValueError("Text cannot be empty")

        return sum(SCRABBLE_VALUES.get(char.upper(), 0) for char in text)

Contributing Workflow
---------------------

1. Fork repository on GitHub
2. Create feature branch: ``git checkout -b feature/my-feature``
3. Make changes with tests
4. Run quality checks: ``make check``
5. Commit with conventional commits (see below)
6. Push and create pull request
7. Respond to review feedback

Commit Message Format
~~~~~~~~~~~~~~~~~~~~~

Follow conventional commits:

.. code-block:: text

    <type>(<scope>): <subject>

    <body>

    <footer>

**Types:** feat, fix, docs, test, refactor, perf, chore, ci, build

**Examples:**

.. code-block:: text

    feat(api): Add retry logic for NHL API requests
    fix(scoring): Handle special characters in player names
    docs(tutorials): Update installation guide
    test(processors): Add playoff calculator edge cases

Building Documentation
----------------------

.. code-block:: bash

    # Build HTML docs
    make docs

    # Auto-rebuild on changes
    sphinx-autobuild docs docs/_build/html

    # Serve locally
    make serve-docs
    # Visit http://localhost:8000

    # Check spelling
    tox -e docs -- -b spelling

    # Check links
    sphinx-build -b linkcheck docs docs/_build/linkcheck

Release Process
---------------

1. Update version in ``pyproject.toml``
2. Update ``CHANGELOG.md`` with release notes
3. Run full test suite: ``make tox-parallel``
4. Run CI simulation: ``make ci``
5. Create release commit: ``git commit -m "chore: Release v2.1.0"``
6. Tag release: ``git tag -a v2.1.0 -m "Release v2.1.0"``
7. Push: ``git push && git push --tags``
8. GitHub Actions builds and publishes to PyPI automatically

Project Resources
-----------------

**Repository**
   https://github.com/bdperkin/nhl-scrabble

**Issues**
   https://github.com/bdperkin/nhl-scrabble/issues

**Pull Requests**
   https://github.com/bdperkin/nhl-scrabble/pulls

**Discussions**
   https://github.com/bdperkin/nhl-scrabble/discussions

**CI/CD**
   https://github.com/bdperkin/nhl-scrabble/actions

Development Tools
-----------------

**UV Package Manager** (10-100x faster)
   See :doc:`../how-to/use-uv` for details

**Tox-UV Integration** (10x faster testing)
   Automatic when using tox, see :doc:`../reference/makefile`

**Pre-commit-UV** (9x faster hooks)
   Automatic with pre-commit, see :doc:`../how-to/setup-pre-commit-hooks`

**Makefile** (55 documented targets)
   Complete automation, see :doc:`../reference/makefile`

Community
---------

* **Code of Conduct**: Be respectful and inclusive
* **Security Policy**: See ``SECURITY.md`` for vulnerability reporting
* **Support**: GitHub Discussions for questions
* **Contributing**: See ``CONTRIBUTING.md`` for detailed guidelines
