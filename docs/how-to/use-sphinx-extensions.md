# Using Sphinx Extensions

This guide demonstrates how to use the extended Sphinx extensions available in the NHL Scrabble documentation.

## Autosummary - API Tables

Generate comprehensive API summary tables with automatic stub page generation:

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

**Features**:

- Automatic table generation for modules, classes, and functions
- Stub pages created automatically (with `autosummary_generate = True`)
- Respects `__all__` attribute in modules
- Excludes imported members by default

**Use Cases**:

- API reference pages
- Module overviews
- Quick navigation to symbols

## Graphviz - Diagrams

Create architecture diagrams, workflows, and data flow visualizations:

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

**Features**:

- SVG output for high quality
- Left-to-right layout by default (configurable)
- Full Graphviz DOT language support
- Automatic diagram rendering

**Requirements**:

- System `graphviz` package must be installed:
  - Ubuntu/Debian: `sudo apt-get install graphviz`
  - macOS: `brew install graphviz`
  - Fedora/RHEL: `sudo dnf install graphviz`

**Use Cases**:

- System architecture diagrams
- Workflow visualizations
- Data flow diagrams
- State machines

## Inheritance Diagrams

Visualize class hierarchies and inheritance relationships:

```rst
Report Classes
==============

.. inheritance-diagram:: nhl_scrabble.reports.base.BaseReport nhl_scrabble.reports.team_report.TeamReporter
   :parts: 1
```

**Features**:

- Automatic class hierarchy visualization
- Top-to-bottom layout
- Customizable node appearance
- SVG output

**Requirements**:

- Requires `graphviz` (same as Graphviz extension above)

**Use Cases**:

- Object-oriented design documentation
- Understanding class relationships
- API architecture documentation

## Math Equations

Add mathematical formulas using LaTeX syntax with MathJax rendering:

```rst
Scoring Formula
===============

The total team score is calculated as:

.. math::

   TeamScore = \sum_{i=1}^{n} PlayerScore_i

where :math:`n` is the number of players on the team.

Individual player scores use standard Scrabble letter values:

.. math::

   PlayerScore = \sum_{j=1}^{m} LetterValue_j

where :math:`m` is the number of letters in the player's name.
```

**Features**:

- LaTeX-style equation syntax
- Beautiful MathJax rendering
- Inline math with `:math:`...\`\`
- Display math with `.. math::` directive
- Loaded from CDN (no local installation needed)

**Syntax**:

- Inline: `:math:`E = mc^2\`\`
- Display block: `.. math::`
- Supports standard LaTeX commands

**Use Cases**:

- Scoring formulas
- Statistical calculations
- Algorithm complexity
- Mathematical explanations

## Conditional Content

Include content based on build configuration tags:

```rst
.. ifconfig:: include_dev_docs

   Development Notes
   =================

   This section is only visible when built with dev docs enabled.

   Build with: sphinx-build -D include_dev_docs=True ...

.. ifconfig:: include_internal_notes

   Internal Implementation Details
   ================================

   Database schema notes and migration history.
```

**Features**:

- Content shown/hidden based on config values
- Configure in `docs/conf.py` or via command line
- Separate dev/prod documentation
- Hide internal notes from public docs

**Configuration**:

```python
# In docs/conf.py setup() function
app.add_config_value("include_dev_docs", False, "html")
app.add_config_value("include_internal_notes", False, "html")
```

**Build with flags**:

```bash
# Build with dev docs
sphinx-build -b html -D include_dev_docs=True docs docs/_build/html

# Build with internal notes
sphinx-build -b html -D include_internal_notes=True docs docs/_build/html
```

**Use Cases**:

- Separate public/internal documentation
- Development vs production docs
- Feature-flagged documentation
- Version-specific content

## Shortened Links

Use abbreviated external link references for cleaner RST:

```rst
See :issue:`232` for details.

Merged in :pr:`330`.

Fixed in :commit:`d085c8f`.

Uses :nhl-api:`standings/now` endpoint.
```

**Configured Links**:

- `:issue:`123\`\` → GitHub issue #123
- `:pr:`456\`\` → GitHub pull request #456
- `:commit:`abc123\`\` → GitHub commit abc123
- `:nhl-api:`standings/now\`\` → NHL API endpoint

**Features**:

- DRY principle for external links
- Consistent GitHub references
- Easy to update link patterns
- Cleaner RST source

**Configuration** (in `docs/conf.py`):

```python
extlinks = {
    "issue": ("https://github.com/bdperkin/nhl-scrabble/issues/%s", "issue #%s"),
    "pr": ("https://github.com/bdperkin/nhl-scrabble/pull/%s", "PR #%s"),
    "commit": ("https://github.com/bdperkin/nhl-scrabble/commit/%s", "commit %s"),
    "nhl-api": ("https://api-web.nhle.com/v1/%s", "NHL API: %s"),
}
```

**Use Cases**:

- GitHub issue/PR references
- API endpoint documentation
- Commit references
- External resource links

## Build Duration Tracking

Automatically measure and display build duration:

**Output** (appears in Sphinx build logs):

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

**Features**:

- Automatic performance tracking
- Identifies slow documentation pages
- No configuration needed
- Helps optimize build performance

**Use Cases**:

- Performance monitoring
- Build optimization
- Identify expensive pages
- Track build time trends

## Auto Section Labels

Reference sections by title instead of manual labels:

```rst
Installation Guide
==================

See the installation section for setup instructions.

...

Getting Started
===============

See :ref:`how-to/installation:Installation Guide` for setup.
```

**Features**:

- Automatic reference labels for all sections
- Document name prefix (avoids collisions)
- Max depth of 3 heading levels
- No manual label maintenance

**Reference Format**:

```
:ref:`document-name:Section Title`
```

**Examples**:

```rst
:ref:`how-to/build-documentation:Building HTML`
:ref:`tutorials/getting-started:Installation`
:ref:`reference/cli:Command Reference`
```

**Use Cases**:

- Cross-document references
- Cleaner RST source
- Automatic label management
- Easier refactoring

## Advanced Source Code Links

Provide links to specific lines in GitHub repository:

**Output**: Adds "[source]" links pointing to GitHub

**Features**:

- Links to exact source on GitHub (not local viewer)
- Better for open source projects
- Users see code in repository context
- Configured via `linkcode_resolve()` function

**Configuration** (already in `docs/conf.py`):

```python
def linkcode_resolve(domain, info):
    """Link to GitHub source code."""
    if domain != "py":
        return None
    if not info["module"]:
        return None

    filename = info["module"].replace(".", "/")
    return f"https://github.com/bdperkin/nhl-scrabble/blob/main/src/{filename}.py"
```

**Use Cases**:

- API documentation
- Open source projects
- Code browsing
- Developer documentation

## Tips and Best Practices

### Graphviz Diagrams

- Keep diagrams simple and focused
- Use meaningful node names
- Consider left-to-right (`LR`) vs top-to-bottom (`TB`) layout
- Test diagram rendering locally before committing

### Math Equations

- Use display blocks for complex equations
- Use inline math for simple expressions
- Add explanatory text for variables
- Test MathJax rendering in browser

### Conditional Content

- Use sparingly to avoid documentation drift
- Document which flags enable which content
- Consider separate docs instead of many conditions
- Test builds with and without flags

### External Links

- Add extlinks for frequently referenced URLs
- Use descriptive link text
- Keep URL patterns stable
- Document available link shortcuts

### Performance

- Monitor build duration output
- Optimize slow pages (reduce autosummary scope, simplify diagrams)
- Use caching when possible
- Profile builds regularly

## Troubleshooting

### Graphviz Not Found

**Error**: `graphviz command 'dot' not found`

**Solution**: Install system graphviz package:

```bash
# Ubuntu/Debian
sudo apt-get install graphviz

# macOS
brew install graphviz

# Fedora/RHEL
sudo dnf install graphviz
```

### Math Equations Not Rendering

**Error**: Equations show as plain text

**Solution**: Check browser console for MathJax errors. Ensure internet connection (CDN required).

### Auto Section Labels Conflict

**Error**: Duplicate label warnings

**Solution**: Use unique section titles or add manual labels with `:name:` option.

### Slow Documentation Builds

**Solution**: Check duration output for slow pages. Consider:

- Reducing autosummary scope
- Simplifying complex diagrams
- Using build caching
- Splitting large documents

## Additional Resources

- [Sphinx Extensions Documentation](https://www.sphinx-doc.org/en/master/usage/extensions/index.html)
- [Graphviz DOT Language](https://graphviz.org/doc/info/lang.html)
- [MathJax Documentation](https://www.mathjax.org/)
- [NHL Scrabble Documentation](https://bdperkin.github.io/nhl-scrabble/)
