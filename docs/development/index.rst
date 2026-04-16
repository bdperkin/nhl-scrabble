Development Guide
=================

Contributing to NHL Scrabble Score Analyzer.

.. toctree::
   :maxdepth: 2
   :caption: Development Guides

   setup
   testing
   code-style
   contributing

Development Setup
-----------------

First Time Setup
~~~~~~~~~~~~~~~~

Clone the repository and set up development environment:

.. code-block:: bash

    git clone https://github.com/bdperkin/nhl-scrabble.git
    cd nhl-scrabble
    make init
    source .venv/bin/activate

Or using UV for faster setup:

.. code-block:: bash

    make uv-init
    source .venv/bin/activate

Verify setup:

.. code-block:: bash

    make check
    pytest

Testing
-------

Run Tests
~~~~~~~~~

.. code-block:: bash

    # Quick test run
    pytest

    # With coverage
    pytest --cov

    # Specific test file
    pytest tests/unit/test_scrabble.py

    # Via tox (all Python versions)
    tox

    # Parallel testing (10x faster with tox-uv)
    tox -p auto

Code Quality
~~~~~~~~~~~~

.. code-block:: bash

    # Run all quality checks
    make quality

    # Individual checks
    make ruff-check
    make ruff-format
    make mypy

    # Pre-commit hooks
    make pre-commit

Code Style
----------

The project follows strict code quality standards:

* **PEP 8** - Python style guide
* **Type hints** - All functions annotated (mypy strict)
* **Docstrings** - 100% coverage (Google style)
* **Line length** - 100 characters
* **Ruff** - Linting and formatting
* **Pre-commit hooks** - 55 automated checks

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
            >>> score = calculate_score("HELLO")
            >>> print(score)
            8

        Raises:
            ValueError: If text is empty.
        """
        if not text:
            raise ValueError("Text cannot be empty")

        return sum(SCRABBLE_VALUES.get(char.upper(), 0) for char in text)

Testing Philosophy
------------------

Write tests for:

* All public APIs
* Edge cases and error conditions
* Integration with external APIs
* Business logic (scoring, playoff calculation)

Test Structure
~~~~~~~~~~~~~~

.. code-block:: text

    tests/
    ├── unit/              # Unit tests for individual components
    │   ├── test_scrabble.py
    │   ├── test_models.py
    │   └── ...
    ├── integration/       # Integration tests for full workflows
    │   ├── test_api.py
    │   └── ...
    └── conftest.py        # Shared fixtures

Contributing
------------

Workflow
~~~~~~~~

1. Fork the repository
2. Create a feature branch: ``git checkout -b feature/my-feature``
3. Make changes with tests
4. Run quality checks: ``make check``
5. Commit with conventional commits
6. Push and create pull request

Commit Messages
~~~~~~~~~~~~~~~

Follow conventional commits format:

.. code-block:: text

    feat: Add new report type
    fix: Resolve API timeout issue
    docs: Update installation guide
    test: Add playoff calculation tests

Pull Requests
~~~~~~~~~~~~~

* Write descriptive PR title and description
* Link related issues
* Ensure all CI checks pass
* Request review from maintainers

See `CONTRIBUTING.md <https://github.com/bdperkin/nhl-scrabble/blob/main/CONTRIBUTING.md>`_ for full guidelines.

Building Documentation
----------------------

Build HTML documentation:

.. code-block:: bash

    cd docs
    make html

Auto-rebuild on changes:

.. code-block:: bash

    sphinx-autobuild docs docs/_build/html

View documentation:

.. code-block:: bash

    open docs/_build/html/index.html

Or via Makefile:

.. code-block:: bash

    make docs
    make serve-docs

Release Process
---------------

1. Update version in ``pyproject.toml``
2. Update ``CHANGELOG.md``
3. Run full test suite: ``make tox-parallel``
4. Create release commit: ``git commit -m "chore: Release v2.1.0"``
5. Tag release: ``git tag v2.1.0``
6. Push: ``git push && git push --tags``
7. GitHub Actions will build and publish to PyPI
