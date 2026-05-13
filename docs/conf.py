"""Sphinx configuration for NHL Scrabble documentation."""

# ruff: noqa: INP001

import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from nhl_scrabble import __version__

if TYPE_CHECKING:
    from sphinx.application import Sphinx

# Add source directory to path for autodoc
sys.path.insert(0, str(Path("../src").resolve()))

# -- Project information -----------------------------------------------------
project = "NHL Scrabble"
copyright = f"{datetime.now(tz=UTC).year}, Brandon Perkins"  # noqa: A001
author = "Brandon Perkins"

# Get version from package
version = __version__
release = __version__

# -- General configuration ---------------------------------------------------
extensions = [
    # Core Sphinx extensions
    "sphinx.ext.autodoc",  # Auto-generate API docs from docstrings
    "sphinx.ext.napoleon",  # Support Google/NumPy docstring styles
    "sphinx.ext.viewcode",  # Add links to source code
    "sphinx.ext.intersphinx",  # Link to other project docs
    "sphinx.ext.todo",  # Support TODO directives
    "sphinx.ext.coverage",  # Check documentation coverage
    "sphinx.ext.doctest",  # Test code examples in docstrings
    "sphinx.ext.githubpages",  # Create .nojekyll for GitHub Pages
    # Additional Sphinx extensions (enhancement/024)
    "sphinx.ext.autosummary",  # Auto-generate summary tables
    "sphinx.ext.graphviz",  # Diagram support
    "sphinx.ext.inheritance_diagram",  # Class hierarchy visualization
    "sphinx.ext.mathjax",  # Math equation support
    "sphinx.ext.ifconfig",  # Conditional content
    "sphinx.ext.extlinks",  # Shortened external links
    "sphinx.ext.duration",  # Build time tracking
    "sphinx.ext.autosectionlabel",  # Auto section labels
    "sphinx.ext.linkcode",  # Advanced source code links
    # Third-party extensions
    "sphinx_autodoc_typehints",  # Use type hints in signatures
    "sphinx_copybutton",  # Copy button for code blocks
    "sphinx_design",  # Modern UI components
    "sphinxcontrib.programoutput",  # Run programs and show output
    "sphinxcontrib.spelling",  # Spell checker
    "sphinxext.opengraph",  # OpenGraph metadata
    # Quality plugins (enhancement/005)
    "sphinx_sitemap",  # SEO sitemap generation
    # Markdown support (optional, for including .md files)
    "myst_parser",  # MyST markdown parser
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

# Logo and favicon
html_logo = "_static/logo.svg"
html_favicon = "_static/favicon.ico"

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

# Sitemap configuration (SEO)
html_baseurl = "https://bdperkin.github.io/nhl-scrabble/"
sitemap_url_scheme = "{link}"

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

# TODO: extension configuration
todo_include_todos = True

# Coverage configuration
coverage_show_missing_items = True
coverage_write_headline = True
coverage_ignore_modules = ["tests"]
coverage_ignore_classes = ["_.*"]  # Private classes

# Link checking configuration
linkcheck_ignore = [
    r"http://localhost.*",  # Ignore local URLs
    r"https://example.com.*",  # Ignore example URLs
    r"http://127\.0\.0\.1.*",  # Ignore localhost IP
    r"https://github.com/.*/pull/\d+",  # PR URLs may not exist yet
    r"https://github.com/.*/issues/\d+",  # Issue URLs may not exist yet
]
linkcheck_timeout = 15  # Seconds to wait for link response
linkcheck_retries = 2  # Number of retries for failed links
linkcheck_workers = 5  # Parallel workers for checking links

# Anchors to ignore (some sites don't support anchor checking)
linkcheck_anchors_ignore = [
    r"^!",  # Ignore anchors starting with !
]

# Report settings
linkcheck_report_timeouts_as_broken = True

# Doctest configuration
import doctest  # noqa: E402

doctest_default_flags = (
    doctest.ELLIPSIS  # Allow ... in output
    | doctest.NORMALIZE_WHITESPACE  # Ignore whitespace differences
)

doctest_global_setup = """
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.abspath('../src'))

# Import common modules for doctests
from nhl_scrabble.scoring import ScrabbleScorer
from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.team import TeamScore
from nhl_scrabble.models.standings import (
    ConferenceStandings,
    DivisionStandings,
    PlayoffTeam,
)

# Import filter and search modules
from nhl_scrabble.filters import AnalysisFilters
from nhl_scrabble.search import PlayerSearch

# Import utility modules
from nhl_scrabble.rate_limiter import RateLimiter

# Import security modules
from nhl_scrabble.security.circuit_breaker import CircuitBreaker, CircuitState
from nhl_scrabble.security.log_filter import SensitiveDataFilter

# Import formatter modules
from nhl_scrabble.formatters.template_formatter import TemplateFormatter

# Import processor modules
from nhl_scrabble.processors.team_processor import TeamProcessor

# Import API modules for API documentation doctests
from nhl_scrabble.api.nhl_client import NHLApiClient
from nhl_scrabble.cli import validate_output_path, validate_cli_arguments
"""

doctest_test_doctest_blocks = "default"  # Test >>> blocks in docstrings

# Note: API autodoc examples are skipped because they test external APIs
# and environment-specific behavior that's unreliable in CI

# -- Additional extension configuration (enhancement/024) -------------------

# Autosummary configuration
autosummary_generate = True  # Generate stub pages automatically
autosummary_imported_members = False  # Don't include imported members
autosummary_ignore_module_all = False  # Respect __all__

# Graphviz configuration
graphviz_output_format = "svg"  # SVG for better quality
graphviz_dot_args = ["-Grankdir=LR"]  # Left-to-right layout

# Inheritance diagram configuration
inheritance_graph_attrs = {"rankdir": "TB", "size": '"8.0, 10.0"'}
inheritance_node_attrs = {"shape": "box", "fontsize": 11, "height": 0.75}

# MathJax configuration
mathjax_path = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"
mathjax3_config = {
    "tex": {
        "inlineMath": [["$", "$"], ["\\(", "\\)"]],
        "displayMath": [["$$", "$$"], ["\\[", "\\]"]],
    },
}

# External links configuration
extlinks = {
    "issue": ("https://github.com/bdperkin/nhl-scrabble/issues/%s", "issue #%s"),
    "pr": ("https://github.com/bdperkin/nhl-scrabble/pull/%s", "PR #%s"),
    "commit": ("https://github.com/bdperkin/nhl-scrabble/commit/%s", "commit %s"),
    "nhl-api": ("https://api-web.nhle.com/v1/%s", "NHL API: %s"),
}

# Autosectionlabel configuration
autosectionlabel_prefix_document = True  # Prefix with document name
autosectionlabel_maxdepth = 3  # Max heading depth

# -- Options for multiple output formats ------------------------------------

# Man page configuration
man_pages = [
    (
        "index",  # Source document
        "nhl-scrabble",  # Man page name
        "NHL Scrabble Documentation",  # Description
        ["Brandon Perkins"],  # Authors
        1,  # Section (1 = commands)
    ),
]

# Texinfo configuration
texinfo_documents = [
    (
        "index",  # Source document
        "nhl-scrabble",  # Target name
        "NHL Scrabble Documentation",  # Title
        "Brandon Perkins",  # Author
        "nhl-scrabble",  # Dir menu entry
        "NHL player name Scrabble scoring system",  # Description
        "Miscellaneous",  # Category
    ),
]

# LaTeX/PDF configuration
latex_documents = [
    (
        "index",  # Source document
        "nhl-scrabble.tex",  # Target name
        "NHL Scrabble Documentation",  # Title
        "Brandon Perkins",  # Author
        "manual",  # Document class (manual or howto)
    ),
]

latex_elements = {
    "papersize": "letterpaper",
    "pointsize": "10pt",
    "preamble": "",
    "figure_align": "htbp",
}

# Text output configuration
text_newlines = "unix"
text_sectionchars = '*=-~"+`'

# EPUB configuration
epub_basename = "nhl-scrabble"
epub_title = project
epub_author = author
epub_publisher = "Brandon Perkins"
epub_copyright = copyright
epub_exclude_files = ["search.html"]
epub_tocdepth = 3
epub_tocdup = True
epub_show_urls = "footnote"
epub_use_index = True

# Gettext configuration (for i18n)
gettext_compact = False
gettext_uuid = True
gettext_location = True
gettext_auto_build = True


def linkcode_resolve(domain: str, info: dict[str, str]) -> str | None:
    """Link to GitHub source code.

    Args:
        domain: The language domain (e.g., 'py' for Python)
        info: Information about the object being documented

    Returns:
        URL to the source code on GitHub, or None if not applicable
    """
    if domain != "py":
        return None
    if not info["module"]:
        return None

    filename = info["module"].replace(".", "/")
    return f"https://github.com/bdperkin/nhl-scrabble/blob/main/src/{filename}.py"


def _configure_doctest_exclusions(app: "Sphinx") -> None:
    """Exclude API autodoc files from doctest builder.

    These contain examples that test external APIs and environment-specific paths.
    """
    if app.builder.name == "doctest":
        app.config.exclude_patterns.extend(
            [
                "api/cli.rst",
                "api/nhl-api.rst",
                "api/processors.rst",
                "api/scoring.rst",
            ],
        )


def _configure_builder_extensions(app: "Sphinx") -> None:
    """Configure extensions based on builder type.

    Some extensions are HTML-specific and should not run for other builders. Disconnect their event
    handlers to prevent errors.
    """
    # Builders that don't support HTML-specific extensions
    non_html_builders = ["json", "xml", "pickle", "pseudoxml", "gettext", "text"]

    if app.builder.name in non_html_builders:
        # Disconnect HTML-specific event handlers for non-HTML builders
        # This prevents extensions like opengraph from trying to process non-HTML output
        try:
            # Remove all handlers for html-page-context event (used by opengraph, etc.)
            if "html-page-context" in app.events.listeners:
                app.events.listeners["html-page-context"].clear()
        except (AttributeError, KeyError):
            # If the event doesn't exist or structure changed, silently continue
            pass


# -- Builder-specific configuration -----------------------------------------


def setup(app: "Sphinx") -> None:
    """Sphinx setup hook for builder-specific configuration."""
    # Connect to builder-inited event to configure extensions and exclusions
    app.connect("builder-inited", _configure_builder_extensions)
    app.connect("builder-inited", _configure_doctest_exclusions)

    # Add configuration values for ifconfig extension
    app.add_config_value("include_dev_docs", default=False, rebuild="html")
    app.add_config_value("include_internal_notes", default=False, rebuild="html")
