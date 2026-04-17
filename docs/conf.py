"""Sphinx configuration for NHL Scrabble documentation."""

# ruff: noqa: INP001

import sys
from datetime import datetime, timezone
from pathlib import Path

from nhl_scrabble import __version__

# Add source directory to path for autodoc
sys.path.insert(0, str(Path("../src").resolve()))

# -- Project information -----------------------------------------------------
project = "NHL Scrabble"
copyright = f"{datetime.now(tz=timezone.utc).year}, Brandon Perkins"  # noqa: A001
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
]
linkcheck_timeout = 10
linkcheck_retries = 3
linkcheck_workers = 5

# Doctest configuration
doctest_global_setup = """
import sys
from pathlib import Path
sys.path.insert(0, str(Path('..').resolve() / 'src'))
"""
doctest_test_doctest_blocks = "default"
