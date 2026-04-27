# Code Style Guidelines

Follow these style guidelines to maintain consistency across the codebase.

## Python Style

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use [type hints](https://docs.python.org/3/library/typing.html) for all function signatures
- Maximum line length: 100 characters
- Use descriptive variable names
- Add [docstrings](https://peps.python.org/pep-0257/) to all public modules, classes, and functions

## Docstring Format

Use Google-style docstrings:

```python
def calculate_score(name: str) -> int:
    """Calculate the Scrabble score for a given name.

    Args:
        name: The name to score (can include spaces and special characters)

    Returns:
        The total Scrabble score (non-letter characters are worth 0 points)

    Raises:
        ValueError: If name is None

    Examples:
        >>> scorer = ScrabbleScorer()
        >>> scorer.calculate_score("ALEX")
        11
    """
    pass
```

## Type Hints

Always use type hints:

```python
# Good
def process_teams(teams: dict[str, TeamScore]) -> list[PlayerScore]:
    pass


# Bad
def process_teams(teams):
    pass
```

## Class Member Ordering

The project uses [ssort](https://github.com/bwhmather/ssort) to automatically sort class members and module-level statements for consistency:

**Standard Order:**

1. **Dunder methods** (special methods like `__init__`, `__repr__`)
1. **Class methods** (`@classmethod` decorated)
1. **Static methods** (`@staticmethod` decorated)
1. **Properties** (`@property` decorated)
1. **Public methods** (regular methods, alphabetically)
1. **Private methods** (leading underscore, alphabetically)

**Example:**

```python
class Example:
    """Example class with proper member ordering."""

    def __init__(self, value: int):
        """Initialize with value."""
        self.value = value

    def __repr__(self) -> str:
        """String representation."""
        return f"Example({self.value})"

    @classmethod
    def from_string(cls, s: str) -> "Example":
        """Create instance from string."""
        return cls(int(s))

    @property
    def doubled(self) -> int:
        """Return doubled value."""
        return self.value * 2

    def increment(self) -> None:
        """Increment value."""
        self.value += 1

    def _internal_helper(self) -> int:
        """Private helper method."""
        return self.value + 1
```

**Usage:**

```bash
# Check what would change (dry run)
make ssort-check

# Apply sorting
make ssort-apply

# Or use tox
tox -e ssort         # Check mode
tox -e ssort-apply   # Apply sorting
```

**Note:** ssort runs automatically in pre-commit hooks. Files in `tests/fixtures/` and `migrations/` are excluded.

## Trailing Commas

The project uses [add-trailing-comma](https://github.com/asottile/add-trailing-comma) to automatically add trailing commas to multi-line Python structures. This improves git diffs by making adding/removing items single-line changes and reduces merge conflicts.

**Benefits:**

- **Better Git Diffs**: Adding an item = 1 line changed (not 2)
- **Fewer Merge Conflicts**: Independent changes merge cleanly
- **Consistent Style**: All multi-line structures have trailing commas

**Examples:**

```python
# Multi-line function call
result = function_name(
    arg1,
    arg2,
    arg3,  # Trailing comma added automatically
)

# Multi-line list
items = [
    "item1",
    "item2",
    "item3",  # Trailing comma added automatically
]

# Multi-line dict
config = {
    "key1": "value1",
    "key2": "value2",
    "key3": "value3",  # Trailing comma added automatically
}
```

**Usage:**

```bash
# Check/apply trailing commas
make trailing-comma

# Or use tox
tox -e add-trailing-comma
```

**Note:** Trailing commas are automatically added by pre-commit hooks. No manual management needed!
