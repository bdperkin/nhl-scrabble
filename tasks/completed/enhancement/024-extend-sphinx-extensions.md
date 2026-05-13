# Extend Sphinx Extension Functionality

**GitHub Issue**: [#332](https://github.com/bdperkin/nhl-scrabble/issues/332)

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

3-5 hours

## Description

Extend the NHL Scrabble Sphinx documentation configuration to include additional valuable Sphinx extensions beyond the currently enabled 16 extensions. Add support for autosummary, graphviz, inheritance diagrams, math support, conditional content, and other useful documentation features.

This enhancement builds upon the existing comprehensive Sphinx configuration to provide even more powerful documentation capabilities.

## Current State

**Currently Enabled Extensions** (16 total):

**Core Sphinx Extensions (8):**

- `sphinx.ext.autodoc` - Auto-generate API docs from docstrings
- `sphinx.ext.napoleon` - Support Google/NumPy docstring styles
- `sphinx.ext.viewcode` - Add links to source code
- `sphinx.ext.intersphinx` - Link to other project docs
- `sphinx.ext.todo` - Support TODO directives
- `sphinx.ext.coverage` - Check documentation coverage
- `sphinx.ext.doctest` - Test code examples in docstrings
- `sphinx.ext.githubpages` - Create .nojekyll for GitHub Pages

**Third-Party Extensions (8):**

- `sphinx_autodoc_typehints` - Use type hints in signatures
- `sphinx_copybutton` - Copy button for code blocks
- `sphinx_design` - Modern UI components
- `sphinxcontrib.programoutput` - Run programs and show output
- `sphinxcontrib.spelling` - Spell checker
- `sphinxext.opengraph` - OpenGraph metadata
- `sphinx_sitemap` - SEO sitemap generation
- `myst_parser` - MyST markdown parser

**Current Configuration Location**: `docs/conf.py`

**Limitations**:

- No module/class summary tables (autosummary)
- No graphical diagrams (graphviz)
- No class inheritance visualization
- No math equation support
- No conditional content based on tags
- No shortened external link markup
- No build duration tracking
- No automatic section reference labels

## Proposed Solution

### Add 9 Additional Sphinx Extensions

Implement support for the following valuable Sphinx extensions:

#### 1. sphinx.ext.autosummary - API Summary Tables

Auto-generate summary tables for modules, classes, and functions.

**Configuration**:

```python
# docs/conf.py additions
extensions = [
    # ... existing extensions ...
    "sphinx.ext.autosummary",
]

# Autosummary configuration
autosummary_generate = True  # Generate stub pages automatically
autosummary_imported_members = False  # Don't include imported members
autosummary_ignore_module_all = False  # Respect __all__
```

**Usage in RST**:

```rst
API Summary
===========

.. autosummary::
   :toctree: _autosummary
   :recursive:

   nhl_scrabble.api
   nhl_scrabble.models
   nhl_scrabble.scoring
```

#### 2. sphinx.ext.graphviz - Diagram Support

Include Graphviz graphs for architecture diagrams, workflows, etc.

**Configuration**:

```python
extensions = [
    # ... existing extensions ...
    "sphinx.ext.graphviz",
]

# Graphviz configuration
graphviz_output_format = "svg"  # SVG for better quality
graphviz_dot_args = ["-Grankdir=LR"]  # Left-to-right layout
```

**Usage in RST**:

```rst
System Architecture
===================

.. graphviz::

   digraph architecture {
       "NHL API" -> "API Client";
       "API Client" -> "Team Processor";
       "Team Processor" -> "Scrabble Scorer";
       "Scrabble Scorer" -> "Report Generator";
   }
```

**Dependency**: Requires `graphviz` system package

- Ubuntu/Debian: `sudo apt-get install graphviz`
- macOS: `brew install graphviz`
- Fedora/RHEL: `sudo dnf install graphviz`

#### 3. sphinx.ext.inheritance_diagram - Class Hierarchies

Visualize class inheritance hierarchies.

**Configuration**:

```python
extensions = [
    # ... existing extensions ...
    "sphinx.ext.inheritance_diagram",
]

# Inheritance diagram configuration
inheritance_graph_attrs = {"rankdir": "TB", "size": '"8.0, 10.0"'}
inheritance_node_attrs = {"shape": "box", "fontsize": 11, "height": 0.75}
```

**Usage in RST**:

```rst
Report Classes
==============

.. inheritance-diagram:: nhl_scrabble.reports.base.BaseReport nhl_scrabble.reports.team_report.TeamReporter
   :parts: 1
```

**Dependency**: Requires graphviz (same as above)

#### 4. sphinx.ext.mathjax - Math Equation Support

Render mathematical equations using MathJax.

**Configuration**:

```python
extensions = [
    # ... existing extensions ...
    "sphinx.ext.mathjax",
]

# MathJax configuration
mathjax_path = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"
mathjax3_config = {
    "tex": {
        "inlineMath": [["$", "$"], ["\\(", "\\)"]],
        "displayMath": [["$$", "$$"], ["\\[", "\\]"]],
    },
}
```

**Usage in RST**:

```rst
Scoring Formula
===============

The total team score is calculated as:

.. math::

   TeamScore = \sum_{i=1}^{n} PlayerScore_i

where :math:`n` is the number of players on the team.
```

#### 5. sphinx.ext.ifconfig - Conditional Content

Include content conditionally based on configuration tags.

**Configuration**:

```python
extensions = [
    # ... existing extensions ...
    "sphinx.ext.ifconfig",
]


# Define configuration values for conditional content
def setup(app):
    app.add_config_value("include_dev_docs", False, "html")
    app.add_config_value("include_internal_notes", False, "html")
```

**Usage in RST**:

```rst
.. ifconfig:: include_dev_docs

   Development Notes
   =================

   This section is only visible when built with dev docs enabled.
```

#### 6. sphinx.ext.extlinks - Shortened External Links

Define abbreviated external link references.

**Configuration**:

```python
extensions = [
    # ... existing extensions ...
    "sphinx.ext.extlinks",
]

# External links configuration
extlinks = {
    "issue": ("https://github.com/bdperkin/nhl-scrabble/issues/%s", "issue #%s"),
    "pr": ("https://github.com/bdperkin/nhl-scrabble/pull/%s", "PR #%s"),
    "commit": ("https://github.com/bdperkin/nhl-scrabble/commit/%s", "commit %s"),
    "nhl-api": ("https://api-web.nhle.com/v1/%s", "NHL API: %s"),
}
```

**Usage in RST**:

```rst
See :issue:`232` for details.

Merged in :pr:`330`.

Fixed in :commit:`d085c8f`.

Uses :nhl-api:`standings/now` endpoint.
```

#### 7. sphinx.ext.duration - Build Time Tracking

Measure and display build duration for performance monitoring.

**Configuration**:

```python
extensions = [
    # ... existing extensions ...
    "sphinx.ext.duration",
]
```

**Output**: Automatically shows build duration in Sphinx output

```
build succeeded.

The HTML pages are in _build/html.
Slowest 5 pages:
  1. 0.234s: reference/cli
  2. 0.189s: api/index
  3. 0.156s: tutorials/getting-started
  4. 0.142s: how-to/build-documentation
  5. 0.128s: explanation/architecture
```

#### 8. sphinx.ext.autosectionlabel - Auto Section Labels

Automatically create reference labels for sections.

**Configuration**:

```python
extensions = [
    # ... existing extensions ...
    "sphinx.ext.autosectionlabel",
]

# Autosectionlabel configuration
autosectionlabel_prefix_document = True  # Prefix with document name
autosectionlabel_maxdepth = 3  # Max heading depth
```

**Usage in RST**:

```rst
See :ref:`how-to/build-documentation:Building HTML` for details.
```

#### 9. sphinx.ext.linkcode - Advanced Source Code Links

Provide links to specific lines in source repository (alternative to viewcode).

**Configuration**:

```python
extensions = [
    # ... existing extensions ...
    "sphinx.ext.linkcode",
]


# Linkcode configuration
def linkcode_resolve(domain, info):
    """Link to GitHub source code."""
    if domain != "py":
        return None
    if not info["module"]:
        return None

    filename = info["module"].replace(".", "/")
    return f"https://github.com/bdperkin/nhl-scrabble/blob/main/src/{filename}.py"
```

**Output**: Adds "[source]" links pointing to GitHub instead of local code viewer

### Update Documentation

Add section to `docs/how-to/use-sphinx-extensions.md` (new file):

```markdown
# Using Sphinx Extensions

## Autosummary - API Tables

Generate comprehensive API summary tables:

\`\`\`rst
.. autosummary::
   :toctree: _autosummary
   :recursive:

   nhl_scrabble.api
\`\`\`

## Graphviz - Diagrams

Create architecture diagrams:

\`\`\`rst
.. graphviz::

   digraph G {
       A -> B;
       B -> C;
   }
\`\`\`

## Inheritance Diagrams

Visualize class hierarchies:

\`\`\`rst
.. inheritance-diagram:: module.Class
   :parts: 1
\`\`\`

## Math Equations

Add mathematical formulas:

\`\`\`rst
.. math::

   E = mc^2
\`\`\`

## Conditional Content

Include content based on build config:

\`\`\`rst
.. ifconfig:: include_dev_docs

   Developer content here
\`\`\`

## Shortened Links

Use abbreviated link references:

\`\`\`rst
:issue:`123` - GitHub issue
:pr:`456` - Pull request
:commit:`abc123` - Commit
\`\`\`

## Auto Section Labels

Reference sections by title:

\`\`\`rst
See :ref:`document:Section Title`
\`\`\`
```

### Update pyproject.toml

Add graphviz dependency (optional):

```toml
[project.optional-dependencies]
docs = [
  # ... existing dependencies ...
  "graphviz>=0.20.1", # Python graphviz bindings (optional)
]
```

**Note**: Python `graphviz` package is optional - Sphinx graphviz extension uses system `graphviz` command.

## Implementation Steps

1. **Update docs/conf.py**:

   - Add all 9 extensions to extensions list
   - Add configuration sections for each extension
   - Add setup() function for ifconfig
   - Add linkcode_resolve() function for linkcode

1. **Test Each Extension**:

   - Create example RST files in docs/examples/ (temporary)
   - Test autosummary with API module
   - Test graphviz with simple diagram
   - Test inheritance_diagram with report classes
   - Test mathjax with scoring formula
   - Test ifconfig with conditional sections
   - Test extlinks with issue/pr references
   - Test duration (automatic in build)
   - Test autosectionlabel with cross-references
   - Test linkcode with API documentation

1. **Update Documentation**:

   - Create docs/how-to/use-sphinx-extensions.md
   - Update CLAUDE.md with new extension capabilities
   - Add examples to existing docs using new extensions

1. **Add System Dependency Notes**:

   - Document graphviz system requirement in:
     - docs/how-to/build-documentation.md
     - CONTRIBUTING.md
     - CLAUDE.md
   - Include installation commands for different platforms

1. **Add Tests**:

   - Update tests/test_docs_builds.py with tests for new extensions
   - Verify graphviz diagrams render
   - Verify inheritance diagrams generate
   - Verify math equations display
   - Verify extlinks expand correctly

1. **Commit Changes**:

   - docs/conf.py
   - docs/how-to/use-sphinx-extensions.md
   - tests/test_docs_builds.py
   - CLAUDE.md
   - docs/how-to/build-documentation.md
   - CONTRIBUTING.md

## Testing Strategy

### Unit Tests

**Test Extension Configuration**:

```python
def test_sphinx_extensions_configured():
    """Test that all expected extensions are configured."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("conf", "docs/conf.py")
    conf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(conf)

    expected_extensions = [
        "sphinx.ext.autosummary",
        "sphinx.ext.graphviz",
        "sphinx.ext.inheritance_diagram",
        "sphinx.ext.mathjax",
        "sphinx.ext.ifconfig",
        "sphinx.ext.extlinks",
        "sphinx.ext.duration",
        "sphinx.ext.autosectionlabel",
        "sphinx.ext.linkcode",
    ]

    for ext in expected_extensions:
        assert ext in conf.extensions, f"Extension {ext} not enabled"
```

**Test Extension Build**:

```python
def test_docs_build_with_graphviz():
    """Test documentation builds with graphviz diagrams."""
    # Skip if graphviz not installed
    if shutil.which("dot") is None:
        pytest.skip("graphviz not installed")

    result = subprocess.run(
        ["sphinx-build", "-b", "html", "docs", "docs/_build/html"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0

    # Verify graphviz SVG files created
    svg_files = list(Path("docs/_build/html/_images").glob("graphviz-*.svg"))
    assert len(svg_files) > 0


def test_docs_build_with_inheritance_diagrams():
    """Test documentation builds with inheritance diagrams."""
    if shutil.which("dot") is None:
        pytest.skip("graphviz not installed")

    result = subprocess.run(
        ["sphinx-build", "-b", "html", "docs", "docs/_build/html"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0

    # Verify inheritance diagram files created
    inheritance_files = list(Path("docs/_build/html/_images").glob("inheritance-*.svg"))
    assert len(inheritance_files) > 0
```

### Integration Tests

**Test End-to-End Documentation Build**:

```bash
# Build documentation with all extensions
make docs-html

# Verify autosummary pages generated
ls docs/_build/html/_autosummary/

# Verify graphviz diagrams created
ls docs/_build/html/_images/graphviz-*.svg

# Verify inheritance diagrams created
ls docs/_build/html/_images/inheritance-*.svg

# Check build duration appears in output
grep "Slowest" docs/_build/html/output.txt
```

### Manual Testing

1. Build documentation: `make docs-html`
1. Open in browser: `docs/_build/html/index.html`
1. Verify autosummary tables display correctly
1. Verify graphviz diagrams render as SVG
1. Verify inheritance diagrams show class hierarchies
1. Verify math equations render with MathJax
1. Verify extlinks expand to correct URLs
1. Verify section cross-references work
1. Check "[source]" links point to GitHub

## Acceptance Criteria

- [ ] All 9 Sphinx extensions configured in docs/conf.py
- [ ] Autosummary configuration with generate=True
- [ ] Graphviz configuration with SVG output
- [ ] Inheritance diagram configuration
- [ ] MathJax configuration with CDN
- [ ] Ifconfig setup function defined
- [ ] Extlinks for issue/pr/commit/nhl-api
- [ ] Duration extension enabled
- [ ] Autosectionlabel with document prefix
- [ ] Linkcode resolver function for GitHub links
- [ ] docs/how-to/use-sphinx-extensions.md created with examples
- [ ] CLAUDE.md updated with extension capabilities
- [ ] docs/how-to/build-documentation.md updated with graphviz dependency
- [ ] CONTRIBUTING.md updated with graphviz requirement
- [ ] Tests added to tests/test_docs_builds.py
- [ ] Test skips if graphviz not installed (pytest.mark.skipif)
- [ ] Example diagrams added to documentation
- [ ] Example inheritance diagrams added
- [ ] Example math equations added
- [ ] Example extlinks usage added
- [ ] All tests pass
- [ ] Pre-commit hooks pass
- [ ] Tox passes
- [ ] Documentation builds successfully with new extensions

## Related Files

- `docs/conf.py` - Main Sphinx configuration file
- `docs/how-to/use-sphinx-extensions.md` - New guide for extension usage
- `docs/how-to/build-documentation.md` - Build documentation guide
- `CLAUDE.md` - Project documentation
- `CONTRIBUTING.md` - Contribution guide
- `tests/test_docs_builds.py` - Documentation build tests
- `pyproject.toml` - Optional graphviz dependency

## Dependencies

**System Dependencies** (optional, for graphviz features):

- `graphviz` - System package for diagram generation
  - Ubuntu/Debian: `sudo apt-get install graphviz`
  - macOS: `brew install graphviz`
  - Fedora/RHEL: `sudo dnf install graphviz`

**Python Dependencies** (all built-in to Sphinx):

- All 9 extensions are core Sphinx extensions (no additional packages needed)
- Optional: `graphviz` Python package for programmatic diagram generation

**Related Tasks**:

- Enhancement/018 - Support Additional Sphinx Output Formats (completed)
- Enhancement/023 - Extend Sphinx Builder Functionality (active)

## Additional Notes

### Extension Benefits

**Autosummary**:

- Automatic API reference table generation
- Reduces manual documentation maintenance
- Generates stub pages for modules/classes

**Graphviz**:

- Visualize system architecture
- Create workflow diagrams
- Document data flow

**Inheritance Diagram**:

- Understand class hierarchies at a glance
- Valuable for object-oriented design documentation
- Auto-generated from code structure

**MathJax**:

- Beautiful equation rendering
- LaTeX-style syntax
- Useful for scoring formulas, statistics

**Ifconfig**:

- Create separate dev/prod documentation
- Hide internal notes from public docs
- Conditional feature documentation

**Extlinks**:

- DRY principle for external links
- Consistent GitHub issue/PR references
- Easier to update link patterns

**Duration**:

- Identify slow documentation pages
- Optimize build performance
- Track build time trends

**Autosectionlabel**:

- Reference sections by title instead of manual labels
- Automatic cross-reference maintenance
- Cleaner RST source

**Linkcode**:

- Links to exact source code on GitHub
- Better for open source projects
- Users can view code in context

### Performance Implications

- **Graphviz**: Adds ~5-10 seconds to build time if many diagrams
- **Inheritance Diagram**: Adds ~2-5 seconds for class hierarchy analysis
- **Autosummary**: Adds ~10-20 seconds for stub page generation
- **MathJax**: Loaded from CDN, no build time impact
- **Duration**: Negligible overhead (\<1 second)
- **Other extensions**: Minimal performance impact

### Security Considerations

- **MathJax CDN**: Uses jsdelivr.net CDN (reputable, fast)
- **Graphviz**: Only processes content from RST files (safe)
- **Linkcode**: Static GitHub URLs (safe)
- **Extlinks**: URL patterns defined in config (controlled)

### Breaking Changes

- None - all extensions are additive
- Existing documentation continues to work
- New features are opt-in via RST directives

### Migration Requirements

- No migration needed
- Existing documentation unaffected
- New extensions available for future use

## Implementation Notes

*To be filled during implementation:*

- Actual approach taken
- Challenges encountered
- Deviations from plan
- Actual effort vs estimated
- Extension usage patterns
- Performance measurements
- User feedback
