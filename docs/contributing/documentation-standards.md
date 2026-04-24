# Documentation Standards

**Purpose**: This guide establishes documentation standards for the NHL Scrabble project to ensure consistency, completeness, and maintainability across all documentation.

**Audience**: Contributors, maintainers, and anyone writing documentation for this project

**Last Updated**: 2026-04-23

______________________________________________________________________

## Table of Contents

- [Python Docstrings](#python-docstrings)
  - [Module-Level Docstrings](#module-level-docstrings)
  - [Class Docstrings](#class-docstrings)
  - [Function/Method Docstrings](#functionmethod-docstrings)
  - [Type Hints](#type-hints)
  - [Inline Comments](#inline-comments)
- [Markdown Documentation](#markdown-documentation)
  - [File Structure](#file-structure)
  - [Code Examples](#code-examples)
  - [Links](#links)
  - [Tables](#tables)
- [Examples](#examples)
- [Quality Checklist](#quality-checklist)
- [Tools](#tools)

______________________________________________________________________

## Python Docstrings

We use **Google-style docstrings** consistently throughout the codebase. This style is readable, well-structured, and supported by all major documentation tools.

### Why Google Style?

- ✅ Clear, scannable format
- ✅ Supported by Sphinx, pdoc, and other doc generators
- ✅ Easy to write and maintain
- ✅ Industry standard

### General Rules

1. **Always include a docstring** for modules, classes, and public functions/methods
1. **Use triple double-quotes** (`"""`) for all docstrings
1. **Start with a one-line summary** followed by a blank line
1. **Provide details** in a longer description if needed
1. **Include examples** for non-trivial functions and classes
1. **Document all parameters, returns, and raises** explicitly
1. **Use type hints** in function signatures (not in docstrings)

______________________________________________________________________

### Module-Level Docstrings

**Purpose**: Explain what the module does and how it fits into the project architecture.

**Location**: First thing in the file, before any imports

**Format**:

```python
"""Short one-line description of the module.

Longer description providing context about this module's purpose,
main classes/functions, and how it fits into the overall architecture.
This can span multiple lines.

Examples:
    Basic usage of this module:

    >>> from nhl_scrabble.module import MainClass
    >>> obj = MainClass()
    >>> obj.do_something()
    42

Attributes:
    MODULE_CONSTANT (int): Description of module-level constant.
    ANOTHER_CONSTANT (str): Another constant.

See Also:
    - related_module: How this module relates to related_module
    - another_module: Another relationship
"""
```

**Key Sections**:

- **Summary**: One-line overview of module purpose
- **Description**: Multi-line explanation (optional if summary is sufficient)
- **Examples**: Usage examples showing how to import and use the module
- **Attributes**: Module-level constants and variables
- **See Also**: Related modules and their relationships

**Real Example** (from `scrabble.py`):

```python
"""Scrabble scoring logic for player names."""
```

**Enhanced Example**:

```python
"""Scrabble scoring logic for player names.

This module provides the core scoring functionality for calculating
Scrabble letter values for NHL player names. It includes configurable
scoring systems and caching for performance.

Examples:
    Calculate a player's score:

    >>> from nhl_scrabble.scoring import ScrabbleScorer
    >>> scorer = ScrabbleScorer()
    >>> scorer.calculate_score("McDavid")
    16

Attributes:
    LETTER_VALUES (dict): Standard Scrabble letter point values
"""
```

______________________________________________________________________

### Class Docstrings

**Purpose**: Explain what the class represents, its responsibilities, and how to use it.

**Location**: Immediately after the class definition

**Format**:

```python
class Example:
    """Short one-line description of the class.

    Longer description of the class purpose, responsibilities,
    and key behaviors. Explain what the class is for and when
    to use it.

    Attributes:
        attr1 (str): Description of attr1.
        attr2 (int): Description of attr2 with more details.
        _private_attr (bool): Private attributes should also be documented.

    Examples:
        Create and use the class:

        >>> example = Example(attr1="test", attr2=42)
        >>> example.do_something()
        'result'

        Advanced usage:

        >>> example = Example(attr1="advanced", attr2=100)
        >>> with example:
        ...     example.process()
        True

    Note:
        Important behavioral notes, gotchas, or caveats go here.
        For example: "This class is thread-safe" or
        "Always use as a context manager".
    """
```

**Key Sections**:

- **Summary**: One-line overview of what the class represents
- **Description**: Detailed explanation of purpose and responsibilities
- **Attributes**: All instance and class attributes (public and private)
- **Examples**: How to create and use instances
- **Note**: Important behavioral information, gotchas, thread-safety

**Real Example** (from `player.py`):

```python
@dataclass(slots=True)
class PlayerScore:
    """Represents a player with their Scrabble score information.

    Attributes:
        first_name: Player's first name
        last_name: Player's last name
        full_name: Player's full name (first + last)
        first_score: Scrabble score for first name
        last_score: Scrabble score for last name
        full_score: Total Scrabble score (first + last)
        team: Team abbreviation (e.g., 'TOR', 'MTL')
        division: Division name
        conference: Conference name
    """
```

______________________________________________________________________

### Function/Method Docstrings

**Purpose**: Explain what the function does, its parameters, return value, and any exceptions raised.

**Location**: Immediately after the function/method definition

**Format**:

```python
def example_function(param1: str, param2: int = 10) -> bool:
    """Short one-line summary of what the function does.

    Longer description if needed. Explain the algorithm, behavior,
    or any important implementation details. This can span multiple
    paragraphs if necessary.

    Args:
        param1: Description of param1. Be specific about what values
            are valid and what the parameter controls.
        param2: Description of param2. Include default value in the
            description if it's not obvious (default: 10).

    Returns:
        Description of return value. Be specific about type and meaning.
        Explain what different return values mean if applicable.

    Raises:
        ValueError: Describe when this exception is raised, e.g.,
            "Raised if param1 is empty or contains invalid characters".
        TypeError: Describe when this exception is raised.

    Examples:
        Basic usage:

        >>> example_function("test")
        True

        With custom parameter:

        >>> example_function("test", param2=20)
        False

        Error case:

        >>> example_function("")
        Traceback (most recent call last):
            ...
        ValueError: param1 cannot be empty

    Note:
        Performance considerations, thread-safety, or other important
        notes go here. For example: "This function uses caching and
        is thread-safe" or "This is an expensive operation on large inputs".
    """
```

**Key Sections**:

- **Summary**: One-line description (required)
- **Description**: Longer explanation (optional, use when summary isn't enough)
- **Args**: All parameters with descriptions (required if function has params)
- **Returns**: What the function returns (required if function returns a value)
- **Raises**: All exceptions that can be raised (required if function raises exceptions)
- **Examples**: Usage examples (recommended for public APIs and complex functions)
- **Note**: Performance, thread-safety, or other important considerations (optional)

**When to Include Examples**:

✅ **Do include examples**:

- Public API functions
- Complex algorithms
- Non-obvious usage patterns
- Functions with multiple calling patterns
- Functions commonly misunderstood

❌ **Don't need examples**:

- Trivial getters/setters
- Obvious utility functions
- Internal/private functions (usually)
- Self-explanatory functions

**Real Example** (from `scrabble.py`):

```python
@staticmethod
def calculate_score(name: str) -> int:
    """Calculate the Scrabble score for a given name using standard values.

    This static method provides convenient scoring with default Scrabble letter values.
    For custom scoring values, create a ScrabbleScorer instance and use
    the calculate_score_custom() method.

    This method uses LRU caching to avoid recomputing scores for duplicate
    names, which significantly improves performance when processing ~700 NHL
    players with many duplicate first/last names.

    Cache size: 2048 entries (sufficient for all unique name components)

    Args:
        name: The name to score (can include spaces and special characters)

    Returns:
        The total Scrabble score (non-letter characters are worth 0 points)

    Examples:
        >>> ScrabbleScorer.calculate_score("ALEX")
        11
        >>> ScrabbleScorer.calculate_score("Ovechkin")
        20
    """
```

______________________________________________________________________

### Type Hints

**Purpose**: Provide static type information for better code quality and IDE support.

**Rules**:

1. **Always use type hints** on function signatures
1. **Use modern syntax**: `dict[str, int]` not `Dict[str, int]` (Python 3.12+)
1. **Avoid redundant type info in docstrings** - type hints provide this
1. **Use `| None` instead of `Optional`** (Python 3.10+)
1. **Import from `typing` or `collections.abc`** as needed

**Examples**:

```python
from collections.abc import Callable
from typing import Any, ClassVar, TypeVar

T = TypeVar("T")


# Good: Modern type hints
def process_data(data: dict[str, int], flag: bool = True) -> list[str]:
    """Process data and return results."""
    ...


# Good: Optional with | None
def find_player(name: str) -> PlayerScore | None:
    """Find a player by name, or None if not found."""
    ...


# Good: Generic type
def cache_result(func: Callable[[str], T]) -> T:
    """Cache the result of a function call."""
    ...


# Good: ClassVar for class variables
class Config:
    """Configuration class."""

    DEFAULT_TIMEOUT: ClassVar[int] = 30


# Avoid: Old-style Optional
from typing import Optional


def old_style(name: str) -> Optional[str]:  # Use str | None instead
    ...


# Avoid: Redundant docstring type info
def bad_example(name: str) -> int:
    """Calculate score.

    Args:
        name (str): Player name  # ❌ Don't include type in docstring
                                  # ✅ Type hint already provides this
    """
```

**When Type Hints Are Not Needed**:

- `self` and `cls` parameters
- `*args` and `**kwargs` (unless you know the specific types)

______________________________________________________________________

### Inline Comments

**Purpose**: Explain complex or non-obvious logic within function bodies.

**Rules**:

1. **Explain WHY, not WHAT** - code shows what, comments explain why
1. **Keep comments up-to-date** - outdated comments are worse than no comments
1. **Use comments sparingly** - prefer self-documenting code
1. **Comment complex algorithms** and non-obvious logic
1. **Note performance optimizations** and their rationale

**Examples**:

```python
# Good: Explains WHY
# Use larger buffer for network operations to reduce syscalls
buffer_size = 8192

# Good: Explains non-obvious logic
# Sort by full_score descending, then by full_name ascending for ties
players.sort(key=lambda p: (-p.full_score, p.full_name))

# Good: Documents workaround
# Work around API bug where empty rosters return 200 instead of 404
if response.status_code == 200 and not response.json().get("players"):
    raise NHLApiNotFoundError("Empty roster")

# Bad: Explains WHAT (code already shows this)
# Increment counter
counter += 1

# Bad: Obvious comment
# Return the result
return result

# Good: Security or performance note
# Safe: sphinx-build is trusted tool from project dependencies
result = subprocess.run(  # noqa: S603, S607
    ["sphinx-build", "-b", "html", str(docs_dir), str(build_dir)], ...
)
```

**When to Use Comments**:

✅ **Do comment**:

- Complex algorithms
- Non-obvious optimizations
- Workarounds for bugs
- Security considerations
- Performance rationale
- Surprising behavior

❌ **Don't comment**:

- Obvious code
- What the code does (use docstrings instead)
- Redundant information

______________________________________________________________________

## Markdown Documentation

### File Structure

**Standard Structure**:

```markdown
# Document Title

Brief introduction (1-2 sentences explaining what this document covers).

## Table of Contents

- [Section 1](#section-1)
- [Section 2](#section-2)
- [Section 3](#section-3)

## Section 1

Content for section 1...

### Subsection 1.1

Content for subsection...

### Subsection 1.2

Content for subsection...

## Section 2

Content for section 2...

## Conclusion

Summary and next steps (if applicable).
```

**Rules**:

1. **Start with an H1 heading** (`#`) for the title
1. **Include a brief intro** (1-2 sentences) right after the title
1. **Add Table of Contents** for docs longer than 3 sections
1. **Use hierarchical headings** (H1 → H2 → H3, don't skip levels)
1. **End with conclusion or summary** (if appropriate)

______________________________________________________________________

### Code Examples

**Purpose**: Show users how to accomplish tasks with working, runnable code.

**Rules**:

1. **Always include complete, runnable examples**
1. **Show expected output** when relevant
1. **Include error cases** if they're instructive
1. **Test examples** before committing (or automate testing)
1. **Use syntax highlighting** with language tags

**Format**:

````markdown
### Example: Calculating Player Scores

Calculate scores for player names:

```python
from nhl_scrabble.scoring import ScrabbleScorer

# Create scorer with default values
scorer = ScrabbleScorer()

# Calculate score for a name
score = scorer.calculate_score("McDavid")
print(f"Score: {score}")  # Output: Score: 16
```

**Expected Output**:
```
Score: 16
```

### Example: Using Custom Scoring

Use custom letter values:

```python
# Custom scoring: all letters worth 1 point
uniform_values = {chr(i): 1 for i in range(65, 91)}
scorer = ScrabbleScorer(letter_values=uniform_values)

score = scorer.calculate_score("McDavid")
print(f"Score: {score}")  # Output: Score: 7
```
````

**Shell Examples**:

````markdown
### Example: Running the Analyzer

Run the analyzer from the command line:

```bash
# Basic usage
nhl-scrabble analyze

# Expected output:
# 🏒 NHL Roster Scrabble Score Analyzer 🏒
# Fetching standings...
# ...

# With JSON output
nhl-scrabble analyze --format json --output results.json

# Verbose mode for debugging
nhl-scrabble analyze --verbose
```
````

**What to Include in Examples**:

- ✅ Import statements
- ✅ Complete setup code
- ✅ The actual operation
- ✅ Expected output
- ✅ Comments explaining non-obvious steps
- ❌ Don't: Half-finished examples
- ❌ Don't: Examples that won't run
- ❌ Don't: Examples without output

______________________________________________________________________

### Links

**Purpose**: Connect related documentation and external resources.

**Rules**:

1. **Use relative links for internal docs**: `[Guide](../how-to/guide.md)`
1. **Use absolute URLs for external links**: `[NHL API](https://api.nhle.com/)`
1. **Check links regularly** (monthly) or use automated link checker
1. **Use descriptive link text** - avoid "click here"
1. **Include link descriptions** when helpful

**Examples**:

```markdown
<!-- Good: Relative internal link -->
See the [How-to Guide](../how-to/installation.md) for setup instructions.

<!-- Good: Absolute external link -->
Read the [NHL API Documentation](https://gitlab.com/dword4/nhlapi) for API details.

<!-- Good: Descriptive link text -->
Consult the [Python Style Guide](https://google.github.io/styleguide/pyguide.html)
for coding conventions.

<!-- Bad: Generic link text -->
Click [here](../how-to/guide.md) for more info.

<!-- Bad: Absolute path for internal link -->
See [Guide](https://github.com/user/repo/blob/main/docs/how-to/guide.md)
<!-- ❌ Will break if repo moves -->

<!-- Good: Link with description -->
- [Diátaxis Framework](https://diataxis.fr/) - Documentation structure guide
- [pytest](https://pytest.org/) - Testing framework
```

**Link Organization**:

```markdown
## Related Documentation

- [Architecture Overview](../explanation/architecture.md) - System design
- [API Reference](../reference/api.md) - API documentation
- [Testing Guide](../how-to/run-tests.md) - How to run tests

## External Resources

- [NHL API](https://api-web.nhle.com/) - Official NHL data source
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Web framework
- [Pydantic](https://docs.pydantic.dev/) - Data validation
```

______________________________________________________________________

### Tables

**Purpose**: Present structured data clearly.

**Format**:

```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value A  | Value B  | Value C  |
| Value D  | Value E  | Value F  |
```

**Alignment**:

```markdown
| Left-aligned | Center-aligned | Right-aligned |
|:-------------|:--------------:|--------------:|
| Text         | Text           | 123           |
| More text    | More text      | 456           |
```

**Example**:

```markdown
## Scrabble Letter Values

| Points | Letters |
|--------|---------|
| 1      | A, E, I, O, U, L, N, S, T, R |
| 2      | D, G |
| 3      | B, C, M, P |
| 4      | F, H, V, W, Y |
| 5      | K |
| 8      | J, X |
| 10     | Q, Z |
```

______________________________________________________________________

## Examples

### Complete Module Example

```python
"""NHL API client for fetching team and roster data.

This module provides a client for interacting with the NHL API,
including retry logic, rate limiting, and SSL/TLS security.

Examples:
    Basic usage:

    >>> from nhl_scrabble.api import NHLApiClient
    >>> client = NHLApiClient()
    >>> standings = client.fetch_standings()

    With custom configuration:

    >>> client = NHLApiClient(timeout=30, retries=5)
    >>> with client:
    ...     roster = client.fetch_team_roster("TOR")

Attributes:
    BASE_URL (str): Default NHL API base URL
"""

from typing import Any
import logging

logger = logging.getLogger(__name__)

BASE_URL = "https://api-web.nhle.com/v1"


class NHLApiClient:
    """Client for interacting with the NHL API.

    This client provides methods to fetch team standings and roster data
    from the official NHL API with built-in retry logic, rate limiting,
    and SSL/TLS security.

    Attributes:
        base_url: Base URL for the NHL API
        timeout: Request timeout in seconds
        retries: Number of retry attempts

    Examples:
        >>> client = NHLApiClient()
        >>> with client:
        ...     standings = client.fetch_standings()

    Note:
        Always use as a context manager to ensure proper cleanup.
    """

    def __init__(
        self, base_url: str | None = None, timeout: int = 10, retries: int = 3
    ) -> None:
        """Initialize the NHL API client.

        Args:
            base_url: API base URL (default: NHL API)
            timeout: Request timeout in seconds (default: 10)
            retries: Number of retry attempts (default: 3)

        Examples:
            >>> client = NHLApiClient(timeout=30)
            >>> client.timeout
            30
        """
        self.base_url = base_url or BASE_URL
        self.timeout = timeout
        self.retries = retries

    def fetch_standings(self) -> dict[str, Any]:
        """Fetch current NHL standings.

        Returns:
            Dictionary containing standings data with teams, divisions,
            and conferences.

        Raises:
            NHLApiError: If API request fails after all retries.

        Examples:
            >>> client = NHLApiClient()
            >>> with client:
            ...     standings = client.fetch_standings()
            ...     len(standings["teams"]) >= 32
            True
        """
        # Implementation...
        return {}
```

### Complete Markdown Document Example

````markdown
# How to Install NHL Scrabble

This guide explains different methods for installing the NHL Scrabble analyzer.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
  - [Using pip (Standard)](#using-pip-standard)
  - [Using UV (Fast)](#using-uv-fast)
  - [Development Install](#development-install)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before installing, ensure you have:

- Python 3.12 or later
- pip (included with Python)
- Virtual environment tool (recommended)

## Installation Methods

### Using pip (Standard)

Install using pip in a virtual environment:

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install package
pip install nhl-scrabble

# Verify installation
nhl-scrabble --version
````

**Expected output**:

```
nhl-scrabble version 2.0.0
```

### Using UV (Fast)

Install using UV for 10-100x faster installation:

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create environment and install
uv venv
source .venv/bin/activate
uv pip install nhl-scrabble
```

See [UV Documentation](../explanation/uv-ecosystem.md) for more details.

### Development Install

For development with editable install:

```bash
# Clone repository
git clone https://github.com/bdperkin/nhl-scrabble.git
cd nhl-scrabble

# Install in editable mode
make init

# Verify development setup
make check
```

## Verification

Verify your installation:

```bash
# Check version
nhl-scrabble --version

# Run help
nhl-scrabble --help

# Test analysis (requires internet)
nhl-scrabble analyze --top-players 5
```

## Troubleshooting

**Issue: Command not found**

Make sure virtual environment is activated:

```bash
source .venv/bin/activate  # Linux/Mac
.venv\\Scripts\\activate     # Windows
```

**Issue: Import errors**

Reinstall with development dependencies:

```bash
pip install -e ".[dev]"
```

## Related Documentation

- [Getting Started Tutorial](../tutorials/01-getting-started.md)
- [Configuration Guide](configure-api-settings.md)
- [Development Setup](../reference/development.md)

````

---

## Quality Checklist

Use this checklist when writing or reviewing documentation:

### Python Docstrings

- [ ] Module has a docstring explaining its purpose
- [ ] All classes have docstrings with attributes documented
- [ ] All public functions have docstrings
- [ ] All parameters documented in Args section
- [ ] Return value documented in Returns section
- [ ] All exceptions documented in Raises section
- [ ] Complex functions have usage examples
- [ ] Type hints present on all function signatures
- [ ] Examples use `>>>` for doctest compatibility

### Markdown Documentation

- [ ] Document starts with clear H1 title
- [ ] Brief introduction explains document purpose
- [ ] Table of contents for docs >3 sections
- [ ] Hierarchical headings (H1 → H2 → H3)
- [ ] Code examples are complete and runnable
- [ ] Expected output shown for examples
- [ ] Relative links for internal docs
- [ ] Absolute URLs for external links
- [ ] No broken links
- [ ] Consistent formatting throughout

### General Quality

- [ ] Clear and concise language
- [ ] No jargon without explanation
- [ ] Appropriate technical level for audience
- [ ] Examples provided where helpful
- [ ] No typos or grammatical errors
- [ ] Up-to-date information
- [ ] Tested examples (manually or automatically)

---

## Tools

### Documentation Linters (Pre-commit Hooks)

These tools run automatically on commit:

- **interrogate** - Enforces 100% docstring coverage
- **pydocstyle** - Checks docstring style (PEP 257)
- **doc8** - Lints RST files
- **pymarkdown** - Lints Markdown files
- **mdformat** - Formats Markdown files

### Manual Tools

Run these manually for deeper checks:

```bash
# Check docstring coverage
interrogate src/ --verbose

# Lint Markdown
pymarkdown scan docs/ *.md

# Check links (install linkchecker first)
linkchecker docs/

# Test docstring examples
pytest --doctest-modules src/
````

### Documentation Generation

Generate API documentation:

```bash
# Sphinx (HTML docs)
make docs

# pdoc (auto API docs)
pdoc nhl_scrabble -o api-docs/
```

______________________________________________________________________

## References

**Official Guidelines**:

- [PEP 257](https://peps.python.org/pep-0257/) - Docstring Conventions
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) - Docstrings
- [Diátaxis Framework](https://diataxis.fr/) - Documentation structure

**Tools**:

- [Sphinx](https://www.sphinx-doc.org/) - Documentation generator
- [pytest](https://pytest.org/) - Testing framework (supports doctest)
- [interrogate](https://interrogate.readthedocs.io/) - Docstring coverage

**Community**:

- [Write the Docs](https://www.writethedocs.org/) - Documentation community
- [Read the Docs](https://readthedocs.org/) - Documentation hosting

______________________________________________________________________

**Last Updated**: 2026-04-23
**Maintainer**: Documentation team
**Questions**: Open an issue on GitHub
