# Update Documentation

______________________________________________________________________

## title: 'Update Project Documentation' read_only: false type: 'command'

Comprehensively analyze and update all project documentation to match current state and best practices.

## Process

This command performs a complete documentation audit and update across the entire project:

1. **Comprehensive Project Analysis**

   - Scan entire repository structure
   - Analyze Python code (modules, classes, functions)
   - Review configuration files (pyproject.toml, tox.ini, etc.)
   - Examine build system and tooling
   - Inspect CI/CD pipelines (.github/workflows/)
   - Check test suite structure and coverage
   - Review existing documentation files
   - Identify documentation gaps and inconsistencies

1. **Update Internal Documentation**

   - **Python Docstrings**:
     - Module-level docstrings (file headers)
     - Class docstrings (purpose, attributes, examples)
     - Method/function docstrings (args, returns, raises, examples)
     - Follow PEP 257 and project style (Google/NumPy/Sphinx)
     - Ensure 100% docstring coverage (interrogate requirement)
   - **Inline Comments**:
     - Add comments for complex algorithms
     - Explain non-obvious business logic
     - Document "why" not "what"
     - Remove outdated/misleading comments
   - **Type Hints**:
     - Ensure all functions have type annotations
     - Update incorrect type hints
     - Add missing return type annotations

1. **Update External Documentation**

   - **README.md**:
     - Project description and badges
     - Installation instructions (pip, UV, development setup)
     - Usage examples and quick start
     - Feature list
     - Requirements and compatibility
     - Links to detailed docs
   - **CONTRIBUTING.md**:
     - Development setup instructions
     - Code style guidelines
     - Testing requirements
     - PR process
     - Commit message conventions
   - **CHANGELOG.md**:
     - Version history
     - Release notes format
     - Unreleased changes section
   - **CLAUDE.md**:
     - Project overview for Claude Code
     - Architecture and structure
     - Development workflows
     - Common tasks and commands
     - Testing and CI information
   - **docs/** Directory:
     - Architecture documentation
     - API documentation
     - User guides
     - Developer guides
     - Troubleshooting
   - **SECURITY.md**:
     - Security policy
     - Vulnerability reporting
     - Supported versions
   - **LICENSE**:
     - Verify license file exists
     - Ensure license is correct

1. **Remove Unneeded Documentation**

   - **Outdated Content**:
     - Remove references to deleted files
     - Delete docs for removed features
     - Clean up obsolete configuration examples
   - **Redundant Documentation**:
     - Consolidate duplicate information
     - Remove unnecessary repetition
     - Merge overlapping guides
   - **Misleading Comments**:
     - Delete outdated inline comments
     - Remove TODO comments for completed work
     - Clean up debug comments
   - **Broken Links**:
     - Remove links to deleted files
     - Update moved file references
     - Fix broken external links

1. **Add Missing Documentation**

   - **Best Practice Documentation**:
     - CODE_OF_CONDUCT.md (community guidelines)
     - SECURITY.md (if missing)
     - SUPPORT.md (getting help)
     - .github/ISSUE_TEMPLATE/ (issue templates)
     - .github/PULL_REQUEST_TEMPLATE.md (PR template)
   - **Configuration Documentation**:
     - Document pyproject.toml sections
     - Explain tox environments
     - Document pre-commit hooks
     - Explain Makefile targets
   - **API Documentation**:
     - Public API reference
     - Module documentation
     - Class hierarchies
     - Usage examples
   - **Architecture Documentation**:
     - System design
     - Component relationships
     - Data flow diagrams
     - Decision records (ADR)

## Documentation Standards

### Python Docstrings (PEP 257 + Google Style)

**Module Docstring:**

```python
"""NHL Scrabble Score Analyzer.

This module provides functionality for calculating Scrabble scores
for NHL player names and generating comprehensive reports.

Example:
    from nhl_scrabble import NHLClient

    async with NHLClient() as client:
        teams = await client.fetch_all_teams()

Attributes:
    VERSION (str): Package version string.
    DEFAULT_TIMEOUT (int): Default API timeout in seconds.
"""
```

**Class Docstring:**

```python
class ScrabbleScorer:
    """Calculate Scrabble scores for player names.

    Uses standard Scrabble letter values to score player names,
    converting to uppercase and summing letter values.

    Attributes:
        scrabble_values (dict): Mapping of letters to point values.

    Example:
        scorer = ScrabbleScorer()
        score = scorer.calculate_score("Ovechkin")  # Returns 23
    """
```

**Function Docstring:**

```python
def score_player(self, player: Player) -> PlayerScore:
    """Calculate Scrabble score for a player.

    Args:
        player: Player object containing firstName and lastName.

    Returns:
        PlayerScore object with calculated score and player info.

    Raises:
        ValueError: If player name is empty or invalid.

    Example:
        player = Player(firstName="Alex", lastName="Ovechkin")
        score = scorer.score_player(player)
        print(score.total)  # 23
    """
```

### README.md Structure

```markdown
# Project Name

Brief one-line description.

[![PyPI](badge-url)](link)
[![Python](badge-url)](link)
[![Tests](badge-url)](link)
[![Coverage](badge-url)](link)

## Features

- Feature 1
- Feature 2
- Feature 3

## Installation

### From PyPI
### From Source
### Development Setup

## Quick Start

Simple example showing basic usage.

## Usage

Detailed usage examples.

## Documentation

Links to detailed docs.

## Development

How to set up dev environment.

## Testing

How to run tests.

## Contributing

Link to CONTRIBUTING.md.

## License

License information.
```

### CONTRIBUTING.md Structure

```markdown
# Contributing

## Development Setup

Step-by-step setup instructions.

## Code Style

- PEP 8
- Type hints
- Docstrings
- Pre-commit hooks

## Testing

How to write and run tests.

## Pull Request Process

1. Fork and branch
2. Make changes
3. Add tests
4. Run pre-commit
5. Submit PR

## Commit Messages

Conventional commits format.
```

## Analysis Strategy

### 1. Repository Structure Scan

```python
- Identify all Python files (.py)
- Find all documentation files (.md, .rst)
- Locate configuration files
- Map directory structure
- Identify main entry points
```

### 2. Code Analysis

```python
- Parse Python AST for all modules
- Extract class/function signatures
- Check for existing docstrings
- Identify missing type hints
- Find complex functions needing comments
```

### 3. Configuration Analysis

```python
- Parse pyproject.toml structure
- Review tox.ini environments
- Check .pre-commit-config.yaml
- Examine Makefile targets
- Review GitHub Actions workflows
```

### 4. Documentation Gap Analysis

```python
- Compare code vs docs
- Identify undocumented functions
- Find missing module docs
- Check for outdated examples
- Verify external doc accuracy
```

## Update Workflow

### Phase 1: Analysis (Read-Only)

1. Scan repository structure
1. Analyze all Python files
1. Review existing documentation
1. Identify gaps and issues
1. Generate update plan

### Phase 2: Internal Documentation

1. Update module docstrings
1. Update class docstrings
1. Update function docstrings
1. Add/update inline comments
1. Fix type hints
1. Run interrogate to verify coverage

### Phase 3: External Documentation

1. Update README.md
1. Update CONTRIBUTING.md
1. Update CLAUDE.md
1. Update CHANGELOG.md
1. Update docs/ files
1. Add missing policy files

### Phase 4: Cleanup

1. Remove outdated comments
1. Delete obsolete documentation files
1. Fix broken links
1. Consolidate duplicate content
1. Remove completed TODOs

### Phase 5: Validation

1. Run documentation linters (doc8, rstcheck)
1. Check docstring coverage (interrogate)
1. Validate links
1. Verify code examples
1. Run pre-commit hooks

## Examples

### Example: Missing Module Docstring

**Before:**

```python
# src/nhl_scrabble/scoring/scrabble.py
from typing import Dict

SCRABBLE_VALUES = {...}

class ScrabbleScorer:
    def calculate_score(self, text: str) -> int:
        return sum(...)
```

**After:**

```python
# src/nhl_scrabble/scoring/scrabble.py
"""Scrabble scoring logic for NHL player names.

This module implements standard Scrabble letter values to calculate
scores for player names. Used for ranking teams and generating reports.

Example:
    from nhl_scrabble.scoring import ScrabbleScorer

    scorer = ScrabbleScorer()
    score = scorer.calculate_score("Ovechkin")
    print(score)  # 23

Attributes:
    SCRABBLE_VALUES (dict): Standard Scrabble letter point values.
"""
from typing import Dict

SCRABBLE_VALUES: Dict[str, int] = {...}

class ScrabbleScorer:
    """Calculate Scrabble scores using standard letter values.

    Attributes:
        scrabble_values: Dictionary mapping letters to point values.
    """

    def calculate_score(self, text: str) -> int:
        """Calculate total Scrabble score for text.

        Args:
            text: Input text to score (case-insensitive).

        Returns:
            Total score as sum of letter values.

        Example:
            score = scorer.calculate_score("HELLO")
            # Returns: 8 (H=4, E=1, L=1, L=1, O=1)
        """
        return sum(...)
```

### Example: Outdated README

**Before:**

```markdown
# NHL Scrabble

Calculate scores.

## Install

pip install nhl-scrabble

## Usage

Run: nhl-scrabble
```

**After:**

````markdown
# NHL Scrabble Score Analyzer

[![PyPI](badge)](link)
[![Python 3.10+](badge)](link)
[![Tests](badge)](link)
[![Coverage](badge)](link)

Professional Python package for calculating Scrabble scores for NHL
player names and generating comprehensive team standings reports.

## Features

- Fetch current NHL roster data via official API
- Calculate Scrabble scores using standard letter values
- Generate team, division, and conference standings
- Create mock playoff bracket based on scores
- Multiple output formats (text, JSON, HTML)
- Rich terminal output with colors and formatting

## Installation

### From PyPI (Recommended)

```bash
pip install nhl-scrabble
````

### Using UV (10x Faster)

```bash
uv pip install nhl-scrabble
```

### From Source

```bash
git clone https://github.com/user/nhl-scrabble.git
cd nhl-scrabble
uv pip install -e .
```

## Quick Start

```bash
# Run analyzer
nhl-scrabble analyze

# JSON output
nhl-scrabble analyze --format json --output report.json

# Verbose mode
nhl-scrabble analyze --verbose
```

## Documentation

- [User Guide](docs/USER_GUIDE.md)
- [API Reference](docs/API.md)
- [Development Guide](CONTRIBUTING.md)
- [Project Overview](CLAUDE.md)

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup.

## License

MIT License - see [LICENSE](LICENSE)

```

## Validation Checks

After updates, verify:

- ✅ **Docstring Coverage**: 100% (interrogate passes)
- ✅ **Type Hints**: All functions annotated (mypy passes)
- ✅ **Link Validity**: All links work (no 404s)
- ✅ **Code Examples**: All examples run successfully
- ✅ **Formatting**: All docs pass linters (doc8, mdformat, pymarkdown)
- ✅ **Pre-commit**: All hooks pass
- ✅ **Best Practices**: All recommended files present

## Files to Check/Update

### Python Files (Internal Docs)

```

src/nhl_scrabble/
├── __init__.py
├── __main__.py
├── cli.py
├── config.py
├── logging_config.py
├── api/
│ ├── __init__.py
│ └── nhl_client.py
├── models/
│ ├── __init__.py
│ ├── player.py
│ ├── team.py
│ └── standings.py
├── scoring/
│ ├── __init__.py
│ └── scrabble.py
├── processors/
│ ├── __init__.py
│ ├── team_processor.py
│ └── playoff_calculator.py
└── reports/
├── __init__.py
├── base.py
├── conference_report.py
├── division_report.py
├── playoff_report.py
├── team_report.py
└── stats_report.py

```

### Documentation Files (External Docs)

```

Project Root:
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── LICENSE
├── CLAUDE.md
├── SECURITY.md (create if missing)
├── CODE_OF_CONDUCT.md (create if missing)
├── SUPPORT.md (create if missing)

docs/:
├── README.md
├── DEVELOPMENT.md
├── MAKEFILE.md
├── TOX.md
├── TOX-UV.md
├── UV.md
├── UV-QUICKREF.md
├── UV-ECOSYSTEM.md
├── PRECOMMIT-UV.md

.github/:
├── ISSUE_TEMPLATE/
│ ├── bug_report.md
│ ├── feature_request.md
│ └── question.md
└── PULL_REQUEST_TEMPLATE.md

```

### Configuration Files (Need Documentation)

```

├── pyproject.toml (add inline comments)
├── tox.ini (document environments)
├── .pre-commit-config.yaml (document hooks)
├── Makefile (document targets - already done)
├── .gitignore (add section comments)

````

## Usage

```bash
# Analyze and update all documentation
/update-docs

# The command will:
# 1. Scan entire project
# 2. Report documentation status
# 3. Show planned updates
# 4. Ask for confirmation
# 5. Perform updates
# 6. Run validation
# 7. Create commit with changes
````

## Output Example

```
📋 Documentation Analysis Complete

Project: NHL Scrabble Score Analyzer
Files: 42 Python files, 18 documentation files
Coverage: 49% docstrings, 87% type hints

Issues Found:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 Missing Docstrings (21 locations):
  - src/nhl_scrabble/__init__.py (module)
  - src/nhl_scrabble/cli.py:45 (function: analyze)
  - src/nhl_scrabble/models/player.py:10 (class: Player)
  ... 18 more

🟡 Outdated Documentation (8 locations):
  - README.md: Installation section references old setup.py
  - CONTRIBUTING.md: Mentions pytest-cov (not installed)
  - docs/DEVELOPMENT.md: References Python 3.9 (now 3.10+)
  ... 5 more

🟠 Missing Files (5 files):
  - SECURITY.md
  - CODE_OF_CONDUCT.md
  - .github/ISSUE_TEMPLATE/bug_report.md
  - .github/ISSUE_TEMPLATE/feature_request.md
  - .github/PULL_REQUEST_TEMPLATE.md

✅ Correct Documentation (145 locations):
  - pyproject.toml: Complete and accurate
  - CLAUDE.md: Up to date
  - All GitHub Actions workflows documented
  ... 142 more

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Planned Updates:
  ✏️  Add 21 missing docstrings
  🔄 Update 8 outdated documentation files
  ➕ Create 5 missing policy/template files
  🗑️  Remove 3 obsolete documentation files
  🔗 Fix 12 broken links

Estimated Impact:
  - Docstring coverage: 49% → 100%
  - Files created: 5
  - Files updated: 32
  - Files removed: 3
  - Lines added: ~850
  - Lines removed: ~120

Continue with updates? [y/N]
```

After confirmation:

```
🔄 Updating Documentation...

✅ Updated internal documentation (21 files)
✅ Updated external documentation (11 files)
✅ Created missing files (5 files)
✅ Removed obsolete files (3 files)
✅ Fixed broken links (12 links)

🔍 Running Validation...

✅ interrogate: 100% docstring coverage
✅ mypy: All type hints valid
✅ doc8: Documentation style check passed
✅ pymarkdown: Markdown linting passed
✅ Link checker: All links valid

📝 Creating commit...

Commit: docs: Comprehensive documentation update to 100% coverage
Files changed: 37
  +850 lines
  -120 lines

✅ Documentation update complete!

Next Steps:
1. Review changes: git diff
2. Run tests: make test
3. Push changes: git push
```

## Best Practices Applied

1. **Completeness**: 100% docstring coverage
1. **Consistency**: Uniform style across all docs
1. **Accuracy**: Docs match current code/config
1. **Discoverability**: Clear file organization
1. **Examples**: Working code examples throughout
1. **Maintainability**: Easy to update and extend
1. **Accessibility**: Clear, beginner-friendly language
1. **Standards**: Follow PEP 257, PEP 484, community best practices

## Safety Considerations

Before making changes:

- ✅ Create backup branch
- ✅ Run full test suite
- ✅ Check pre-commit hooks pass
- ✅ Verify examples actually run
- ✅ Test documentation builds (if using Sphinx)
- ✅ Get confirmation before large updates

## Related Commands

- `/interrogate` - Check docstring coverage
- `/mypy` - Verify type hints
- `/pre-commit` - Run all documentation linters
- `/git:commit` - Commit documentation updates

## Tips

- Run this command after major refactoring
- Run before releasing new versions
- Use as part of quarterly maintenance
- Helps with onboarding new contributors
- Improves project discoverability
- Makes code easier to maintain

## Notes

- Updates follow project's existing style
- Preserves intentionally sparse documentation
- Respects .gitignore and excluded paths
- Can be run incrementally (one phase at a time)
- Creates single commit with all changes
- Includes detailed commit message with statistics
