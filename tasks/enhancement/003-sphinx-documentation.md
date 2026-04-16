# Build Comprehensive Sphinx Documentation with GitHub Pages

**GitHub Issue**: #64 - https://github.com/bdperkin/nhl-scrabble/issues/64

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

12-16 hours

## Description

Build comprehensive, professional documentation using Sphinx with modern extensions and automated deployment to GitHub Pages. This will provide beautiful, searchable, version-controlled documentation with automatic API reference generation from the well-typed, well-documented codebase.

## Current State

The project has excellent documentation foundation:

**Strengths:**

- ✅ 100% docstring coverage (enforced by interrogate)
- ✅ Type hints throughout (strict mypy)
- ✅ Comprehensive markdown docs (README, CONTRIBUTING, CLAUDE.md, etc.)
- ✅ 12 documentation files in docs/ directory
- ✅ Well-structured codebase (15 modules)

**Gaps:**

- ❌ No rendered HTML documentation
- ❌ No automatic API reference generation
- ❌ No searchable documentation
- ❌ No version-controlled documentation hosting
- ❌ Documentation not discoverable via web

**Current Documentation:**

```
nhl-scrabble/
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── CLAUDE.md
├── SECURITY.md
├── SUPPORT.md
└── docs/
    ├── MAKEFILE.md
    ├── DEVELOPMENT.md
    ├── TOX.md
    ├── TOX-UV.md
    ├── UV.md
    ├── UV-QUICKREF.md
    ├── UV-ECOSYSTEM.md
    └── PRECOMMIT-UV.md
```

## Proposed Solution

Implement Sphinx documentation with comprehensive extensions and GitHub Pages deployment.

### Sphinx Extensions Analysis

All proposed extensions are valuable for this project:

| Extension                       | Value       | Justification                                                        |
| ------------------------------- | ----------- | -------------------------------------------------------------------- |
| **sphinx**                      | ✅ Required | Core documentation engine                                            |
| **sphinx-autobuild**            | ✅ High     | Auto-rebuild during development (huge productivity boost)            |
| **sphinx-autodoc-typehints**    | ✅ Critical | Leverages existing type hints (perfect fit for mypy-strict codebase) |
| **sphinx-copybutton**           | ✅ High     | Copy code examples with one click (excellent UX)                     |
| **sphinx-design**               | ✅ High     | Modern UI components (cards, tabs, grids) for beautiful docs         |
| **sphinx-rtd-theme**            | ✅ High     | Popular Read the Docs theme (clean, professional)                    |
| **sphinxcontrib-programoutput** | ✅ High     | Show CLI output in docs (perfect for CLI tool)                       |
| **sphinxcontrib-spelling**      | ✅ Medium   | Spell checking (complements codespell)                               |
| **sphinxext-opengraph**         | ✅ Medium   | Social sharing metadata (discoverability)                            |

**Recommendation: Implement ALL extensions** - Each provides clear value for comprehensive documentation.

### Documentation Structure

```
docs/
├── conf.py                    # Sphinx configuration
├── index.rst                  # Main documentation homepage
├── requirements.txt           # Sphinx dependencies
├── Makefile                   # Sphinx build commands
├── make.bat                   # Windows build script
│
├── getting-started/           # User documentation
│   ├── index.rst
│   ├── installation.rst
│   ├── quickstart.rst
│   └── configuration.rst
│
├── user-guide/                # Detailed user guides
│   ├── index.rst
│   ├── understanding-output.rst
│   ├── customization.rst
│   └── troubleshooting.rst
│
├── api/                       # Auto-generated API reference
│   ├── index.rst
│   ├── cli.rst                # CLI module
│   ├── api.rst                # API client module
│   ├── models.rst             # Data models
│   ├── scoring.rst            # Scoring logic
│   ├── processors.rst         # Business logic
│   └── reports.rst            # Report generators
│
├── development/               # Developer documentation
│   ├── index.rst
│   ├── setup.rst              # Dev environment setup
│   ├── testing.rst            # Testing guide
│   ├── contributing.rst       # Contribution workflow
│   └── architecture.rst       # System architecture
│
├── reference/                 # Reference documentation
│   ├── index.rst
│   ├── cli-reference.rst      # Complete CLI reference
│   ├── configuration.rst      # All config options
│   └── nhl-api.rst            # NHL API integration
│
└── _static/                   # Static files (CSS, images)
    └── custom.css             # Custom styling
```

### Sphinx Configuration (conf.py)

```python
# docs/conf.py
"""Sphinx configuration for NHL Scrabble documentation."""

import os
import sys
from datetime import datetime

# Add source directory to path for autodoc
sys.path.insert(0, os.path.abspath("../src"))

# -- Project information -----------------------------------------------------
project = "NHL Scrabble"
copyright = f"{datetime.now().year}, Brandon Perkins"
author = "Brandon Perkins"

# Get version from package
from nhl_scrabble import __version__
version = __version__
release = __version__

# -- General configuration ---------------------------------------------------
extensions = [
    # Core Sphinx extensions
    "sphinx.ext.autodoc",           # Auto-generate API docs from docstrings
    "sphinx.ext.napoleon",          # Support Google/NumPy docstring styles
    "sphinx.ext.viewcode",          # Add links to source code
    "sphinx.ext.intersphinx",       # Link to other project docs
    "sphinx.ext.todo",              # Support TODO directives
    "sphinx.ext.coverage",          # Check documentation coverage
    "sphinx.ext.githubpages",       # Create .nojekyll for GitHub Pages

    # Third-party extensions
    "sphinx_autodoc_typehints",     # Use type hints in signatures
    "sphinx_copybutton",            # Copy button for code blocks
    "sphinx_design",                # Modern UI components
    "sphinxcontrib.programoutput",  # Run programs and show output
    "sphinxcontrib.spelling",       # Spell checker
    "sphinxext.opengraph",          # OpenGraph metadata

    # Markdown support (optional, for including .md files)
    "myst_parser",                  # MyST markdown parser
]

# Add any paths that contain templates here
templates_path = ["_templates"]

# List of patterns to exclude
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

# Theme options
html_theme_options = {
    "display_version": True,
    "prev_next_buttons_location": "bottom",
    "style_external_links": False,
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
}

html_context = {
    "display_github": True,
    "github_user": "bdperkin",
    "github_repo": "nhl-scrabble",
    "github_version": "main",
    "conf_py_path": "/docs/",
}

# -- Extension configuration -------------------------------------------------

# Autodoc configuration
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
    "show-inheritance": True,
}

autodoc_typehints = "description"  # Show type hints in description
autodoc_typehints_description_target = "documented"

# Napoleon settings (Google-style docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "click": ("https://click.palletsprojects.com/en/8.1.x/", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
    "requests": ("https://requests.readthedocs.io/en/latest/", None),
}

# sphinx-copybutton configuration
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True
copybutton_remove_prompts = True

# OpenGraph configuration
ogp_site_url = "https://bdperkin.github.io/nhl-scrabble/"
ogp_image = "_static/logo.png"  # Add project logo
ogp_description_length = 200
ogp_type = "website"
ogp_site_name = "NHL Scrabble Score Analyzer Documentation"

# Spelling configuration
spelling_lang = "en_US"
spelling_word_list_filename = ["spelling_wordlist.txt"]
spelling_show_suggestions = True
spelling_exclude_patterns = ["api/*"]  # Skip API docs (code has many names)

# MyST parser configuration (for .md files)
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "substitution",
    "tasklist",
]

# Todo extension
todo_include_todos = True
```

### Main Index Page (index.rst)

```rst
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

.. programoutput:: nhl-scrabble --help

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
```

### API Documentation Example (api/cli.rst)

```rst
CLI Module
==========

.. automodule:: nhl_scrabble.cli
   :members:
   :undoc-members:
   :show-inheritance:

Command-Line Interface
----------------------

The CLI is built with Click and provides the main entry point for the application.

Main Command
~~~~~~~~~~~~

.. autofunction:: nhl_scrabble.cli.cli

Analyze Command
~~~~~~~~~~~~~~~

.. autofunction:: nhl_scrabble.cli.analyze

Examples
--------

Basic Usage
~~~~~~~~~~~

.. code-block:: bash

    nhl-scrabble analyze

.. programoutput:: nhl-scrabble analyze --help

Verbose Output
~~~~~~~~~~~~~~

.. code-block:: bash

    nhl-scrabble analyze --verbose

JSON Output
~~~~~~~~~~~

.. code-block:: bash

    nhl-scrabble analyze --format json --output report.json

See Also
--------

- :doc:`../reference/cli-reference` - Complete CLI reference
- :doc:`../getting-started/configuration` - Configuration options
```

### GitHub Pages Configuration

**1. Repository Settings:**

- Navigate to Settings → Pages
- Source: Deploy from a branch
- Branch: `gh-pages`, folder: `/ (root)`

**2. Create `.nojekyll` file:**

```bash
# Sphinx creates this automatically via sphinx.ext.githubpages
# But we'll ensure it exists
touch docs/_build/html/.nojekyll
```

**3. GitHub Actions Workflow (`.github/workflows/docs.yml`):**

```yaml
name: Documentation

on:
  push:
    branches: [main]
    paths:
      - 'docs/**'
      - 'src/**'
      - '.github/workflows/docs.yml'
      - 'pyproject.toml'
  pull_request:
    branches: [main]
    paths:
      - 'docs/**'
      - 'src/**'
  workflow_dispatch:

permissions:
  contents: write

jobs:
  build-docs:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for version info

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install UV
        uses: astral-sh/setup-uv@v4

      - name: Install dependencies
        run: |
          uv pip install --system -e ".[dev,docs]"

      - name: Build documentation
        run: |
          cd docs
          make html

      - name: Check documentation
        run: |
          cd docs
          make linkcheck  # Check all links work
          make doctest    # Run doctests
          make coverage   # Check doc coverage

      - name: Upload documentation artifacts
        uses: actions/upload-artifact@v4
        with:
          name: documentation
          path: docs/_build/html/

  deploy-docs:
    needs: build-docs
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - name: Download documentation artifacts
        uses: actions/download-artifact@v4
        with:
          name: documentation
          path: docs/_build/html/

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: docs/_build/html
          force_orphan: true
          user_name: 'github-actions[bot]'
          user_email: 'github-actions[bot]@users.noreply.github.com'
          commit_message: 'docs: Deploy documentation to GitHub Pages'
```

### Makefile Integration

Add Sphinx targets to main Makefile:

```makefile
# ============================================================================
# Documentation Targets
# ============================================================================

.PHONY: docs
docs: ## Build Sphinx documentation
	@echo "$(BLUE)Building Sphinx documentation...$(RESET)"
	cd docs && $(MAKE) html
	@echo "$(GREEN)✓ Documentation built: docs/_build/html/index.html$(RESET)"

.PHONY: docs-serve
docs-serve: ## Serve documentation with auto-rebuild
	@echo "$(BLUE)Serving documentation with auto-rebuild...$(RESET)"
	sphinx-autobuild docs docs/_build/html --open-browser

.PHONY: docs-clean
docs-clean: ## Clean documentation build
	@echo "$(BLUE)Cleaning documentation build...$(RESET)"
	cd docs && $(MAKE) clean

.PHONY: docs-linkcheck
docs-linkcheck: ## Check documentation links
	@echo "$(BLUE)Checking documentation links...$(RESET)"
	cd docs && $(MAKE) linkcheck

.PHONY: docs-coverage
docs-coverage: ## Check documentation coverage
	@echo "$(BLUE)Checking documentation coverage...$(RESET)"
	cd docs && $(MAKE) coverage

.PHONY: docs-spelling
docs-spelling: ## Check documentation spelling
	@echo "$(BLUE)Checking documentation spelling...$(RESET)"
	cd docs && $(MAKE) spelling
```

### pyproject.toml Updates

Add documentation dependencies:

```toml
[project.optional-dependencies]
docs = [
    "sphinx>=7.2.6",
    "sphinx-autobuild>=2024.2.4",
    "sphinx-autodoc-typehints>=2.0.0",
    "sphinx-copybutton>=0.5.2",
    "sphinx-design>=0.5.0",
    "sphinx-rtd-theme>=2.0.0",
    "sphinxcontrib-programoutput>=0.17",
    "sphinxcontrib-spelling>=8.0.0",
    "sphinxext-opengraph>=0.9.1",
    "myst-parser>=2.0.0",  # For markdown support
]
```

### Documentation Spelling Wordlist

Create `docs/spelling_wordlist.txt`:

```
Scrabble
NHL
API
JSON
Pydantic
CLI
pytest
mypy
ruff
UV
Codecov
FastAPI
Ovechkin
McDavid
codebase
docstrings
autodoc
sphinxcontrib
OpenGraph
```

## Implementation Steps

### Phase 1: Sphinx Setup (3-4h)

1. **Install Sphinx and extensions**

   ```bash
   uv pip install -e ".[docs]"
   ```

1. **Initialize Sphinx**

   ```bash
   mkdir -p docs
   cd docs
   sphinx-quickstart
   ```

1. **Configure extensions** in `conf.py`

   - Add all 9 extensions
   - Configure autodoc for type hints
   - Set up theme and styling
   - Configure intersphinx

1. **Create directory structure**

   ```bash
   mkdir -p docs/{getting-started,user-guide,api,development,reference,_static}
   ```

1. **Test basic build**

   ```bash
   cd docs
   make html
   python -m http.server --directory _build/html
   ```

### Phase 2: Content Creation (4-6h)

1. **Create main index** (index.rst)

   - Overview with sphinx-design cards
   - Quick example with programoutput
   - Navigation structure

1. **Getting Started section** (1-2h)

   - installation.rst
   - quickstart.rst
   - configuration.rst

1. **User Guide section** (1-2h)

   - understanding-output.rst
   - customization.rst
   - troubleshooting.rst

1. **Reference section** (1h)

   - cli-reference.rst (complete CLI docs)
   - configuration.rst (all env vars)
   - nhl-api.rst (API integration)

1. **Development section** (1h)

   - setup.rst
   - testing.rst
   - contributing.rst
   - architecture.rst

### Phase 3: API Documentation (2-3h)

1. **Create API reference structure**

   ```rst
   api/
   ├── index.rst
   ├── cli.rst
   ├── api.rst
   ├── models.rst
   ├── scoring.rst
   ├── processors.rst
   └── reports.rst
   ```

1. **Generate API docs** with autodoc

   ```rst
   .. automodule:: nhl_scrabble.cli
      :members:
      :undoc-members:
      :show-inheritance:
   ```

1. **Add examples and usage** for each module

1. **Cross-reference** between modules and guides

### Phase 4: GitHub Pages Setup (1-2h)

1. **Create GitHub Actions workflow**

   - `.github/workflows/docs.yml`
   - Build on push to main
   - Deploy to gh-pages branch

1. **Enable GitHub Pages** in repository settings

   - Source: gh-pages branch
   - Verify deployment

1. **Add documentation badge** to README.md

   ```markdown
   [![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://bdperkin.github.io/nhl-scrabble/)
   ```

1. **Test deployment**

   - Push to main
   - Verify workflow runs
   - Check deployed site

### Phase 5: Polish and Integration (2-3h)

1. **Add custom styling** (\_static/custom.css)

   - Brand colors
   - Improved code block styling
   - Responsive design tweaks

1. **Create documentation** Makefile targets

   - `make docs` - Build docs
   - `make docs-serve` - Auto-rebuild server
   - `make docs-linkcheck` - Check links
   - `make docs-coverage` - Doc coverage

1. **Update existing docs** to link to Sphinx

   - README.md
   - CONTRIBUTING.md
   - CLAUDE.md

1. **Add to CI checks**

   - Build docs in CI
   - Check links
   - Check spelling

## Testing Strategy

### Local Testing

1. **Build documentation**

   ```bash
   cd docs
   make html
   ```

1. **Serve locally**

   ```bash
   make docs-serve
   # Opens browser with auto-reload
   ```

1. **Check links**

   ```bash
   make linkcheck
   # Verifies all internal and external links
   ```

1. **Check coverage**

   ```bash
   make coverage
   # Shows documentation coverage stats
   ```

1. **Check spelling**

   ```bash
   make spelling
   # Spell checks all documentation
   ```

### CI Testing

**GitHub Actions workflow tests:**

- ✅ Documentation builds without errors
- ✅ All links are valid
- ✅ Doctests pass
- ✅ Documentation coverage meets threshold
- ✅ Deployment to GitHub Pages succeeds

### Manual Verification

1. **Navigation**: Verify all sections accessible
1. **Search**: Test documentation search
1. **Mobile**: Check responsive design
1. **API docs**: Verify autodoc generated correctly
1. **Code examples**: Verify syntax highlighting and copy buttons work
1. **Cross-references**: Check intersphinx links work
1. **Social sharing**: Verify OpenGraph metadata appears

## Acceptance Criteria

- [ ] Sphinx configured with all 9 extensions
- [ ] Documentation builds locally without errors (`make html`)
- [ ] Auto-rebuild works with sphinx-autobuild (`make docs-serve`)
- [ ] Complete API reference generated with autodoc + type hints
- [ ] Copy buttons work on all code blocks
- [ ] Modern UI components used (cards, tabs, grids)
- [ ] Read the Docs theme applied and styled
- [ ] CLI examples show actual program output
- [ ] Spell checking configured and passing
- [ ] OpenGraph metadata for social sharing
- [ ] Markdown files can be included (myst-parser)
- [ ] Getting Started section complete (3+ pages)
- [ ] User Guide section complete (3+ pages)
- [ ] API Reference section complete (all modules)
- [ ] Development section complete (4+ pages)
- [ ] Reference section complete (CLI, config, NHL API)
- [ ] All documentation cross-referenced
- [ ] GitHub Pages enabled in repository settings
- [ ] GitHub Actions workflow created (`.github/workflows/docs.yml`)
- [ ] Documentation deploys to GitHub Pages on push to main
- [ ] Documentation accessible at https://bdperkin.github.io/nhl-scrabble/
- [ ] Documentation badge added to README.md
- [ ] Link checking passes (`make linkcheck`)
- [ ] Documentation coverage reported (`make coverage`)
- [ ] Spelling check passes (`make spelling`)
- [ ] Makefile targets added (docs, docs-serve, docs-clean, etc.)
- [ ] pyproject.toml updated with [docs] dependencies
- [ ] All existing markdown docs integrated or linked
- [ ] CI builds and verifies documentation

## Related Files

- `docs/conf.py` - Sphinx configuration (create)
- `docs/index.rst` - Main documentation page (create)
- `docs/Makefile` - Sphinx build commands (create)
- `docs/requirements.txt` - Documentation dependencies (create)
- `.github/workflows/docs.yml` - GitHub Actions workflow (create)
- `pyproject.toml` - Add [docs] dependencies
- `Makefile` - Add documentation targets
- `README.md` - Add documentation badge and link
- `CONTRIBUTING.md` - Add documentation contribution guide
- `CLAUDE.md` - Reference new documentation location

## Dependencies

**Recommended to complete first:**

- enhancement/002-procida-documentation.md - Organize content first, then render with Sphinx

**Recommended to complete after:**

- This becomes the foundation for all future documentation

## Additional Notes

### Benefits

**For Users:**

- 🔍 **Searchable**: Full-text search across all documentation
- 📱 **Responsive**: Works on mobile, tablet, desktop
- 🎨 **Beautiful**: Modern, professional appearance
- 📋 **Organized**: Clear navigation and structure
- 🔗 **Discoverable**: SEO optimized with OpenGraph

**For Developers:**

- 🤖 **Automated**: API docs auto-generated from docstrings
- ⚡ **Fast**: Auto-rebuild during development
- ✅ **Validated**: Link checking, spell checking, coverage
- 🔄 **CI/CD**: Automatic deployment on push
- 📊 **Coverage**: Track documentation completeness

**For Project:**

- 🌟 **Professional**: High-quality documentation reflects well
- 📈 **Adoption**: Good docs increase user adoption
- 💡 **Contribution**: Easier for contributors to understand
- 🎯 **Discoverability**: Better SEO and social sharing

### Extension Details

**sphinx-autobuild**:

```bash
# Auto-rebuilds on file changes, opens browser
sphinx-autobuild docs docs/_build/html --open-browser
# Massive productivity boost during development
```

**sphinx-autodoc-typehints**:

```python
# Leverages existing type hints
def calculate_score(self, text: str) -> int:
    """Calculate Scrabble score.

    Args:
        text: Input text to score.

    Returns:
        Total score.
    """
# Type hints appear automatically in docs!
```

**sphinx-copybutton**:

```rst
.. code-block:: python

    from nhl_scrabble import ScrabbleScorer
    scorer = ScrabbleScorer()

# Adds copy button to code block - excellent UX
```

**sphinx-design**:

```rst
.. grid:: 2

    .. grid-item-card:: Getting Started
        :link: getting-started

    .. grid-item-card:: API Reference
        :link: api

# Beautiful modern UI components
```

**sphinxcontrib-programoutput**:

```rst
.. programoutput:: nhl-scrabble --help

# Shows ACTUAL CLI output in docs - stays up-to-date!
```

**sphinxcontrib-spelling**:

```python
# Spell checks all documentation
# Complements codespell with Sphinx-specific checking
```

**sphinxext-opengraph**:

```html
<!-- Auto-generated OpenGraph metadata -->
<meta property="og:title" content="NHL Scrabble Documentation">
<meta property="og:description" content="...">
<meta property="og:image" content="...">
<!-- Beautiful previews when sharing links! -->
```

### GitHub Pages Features

- **Custom domain support**: Can use custom domain later
- **HTTPS**: Automatic HTTPS
- **CDN**: Fast global delivery
- **Version control**: Documentation versioned with code
- **Free**: No hosting costs
- **Automatic**: Deploys on every push

### Versioning Strategy

**For future versions**, can maintain multiple doc versions:

```
gh-pages/
├── latest/         # Main branch docs
├── v2.0/           # Release 2.0 docs
├── v1.0/           # Release 1.0 docs
└── index.html      # Version selector
```

Implement when needed with tools like:

- **sphinx-multiversion**: Multiple versions in one site
- **mike**: Version manager for MkDocs (alternative to Sphinx)

### Maintenance

**Documentation stays up-to-date:**

1. **Autodoc**: API docs regenerate from code automatically
1. **CI/CD**: Deploys on every merge to main
1. **Link checking**: Catches broken links in CI
1. **Spell checking**: Maintains quality
1. **Coverage**: Ensures completeness

**Estimated ongoing effort:** 1-2h per release for updates

### Integration with Procida Model

If enhancement/002-procida-documentation is implemented first:

```
docs/
├── tutorials/      # Maps to Sphinx getting-started/
├── how-to/         # Maps to Sphinx user-guide/
├── reference/      # Maps to Sphinx reference/
└── explanation/    # Maps to Sphinx development/

# Sphinx renders the organized content beautifully!
```

**Recommended order:**

1. Implement Procida structure (organize content)
1. Implement Sphinx (render content beautifully)
1. Best of both worlds!

### Alternative: MkDocs vs Sphinx

**Sphinx Advantages** (why we chose it):

- ✅ Better Python integration (autodoc)
- ✅ More powerful extensions
- ✅ Intersphinx (link to other Python docs)
- ✅ Type hint integration
- ✅ Industry standard for Python

**MkDocs Advantages**:

- Simpler configuration
- Markdown-native (vs RST)
- Material theme is beautiful

**Verdict**: Sphinx is better for Python packages with extensive API documentation.

### Documentation Examples

**Well-documented projects using Sphinx:**

- Python: https://docs.python.org/
- Django: https://docs.djangoproject.com/
- Requests: https://requests.readthedocs.io/
- Click: https://click.palletsprojects.com/
- Pydantic: https://docs.pydantic.dev/

All use Sphinx with similar extension sets!

### Build Performance

**Expected build times:**

- Initial build: 10-20 seconds
- Incremental rebuild: 1-3 seconds
- Full rebuild with linkcheck: 30-60 seconds

**sphinx-autobuild** makes development fast with instant rebuilds.

### Accessibility

Sphinx + RTD theme provide:

- ✅ Keyboard navigation
- ✅ Screen reader support
- ✅ Semantic HTML
- ✅ ARIA labels
- ✅ High contrast mode
- ✅ Responsive design

## Implementation Notes

*To be filled during implementation:*

- Actual Sphinx configuration decisions
- Extension configuration details
- GitHub Pages setup steps
- CI/CD workflow adjustments
- Documentation structure decisions
- Actual effort vs estimated effort
- User feedback on documentation
- Search quality and performance
