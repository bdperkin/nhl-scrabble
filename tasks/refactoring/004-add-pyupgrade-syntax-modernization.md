# Add pyupgrade for Automatic Python Syntax Modernization

**GitHub Issue**: #118 - https://github.com/bdperkin/nhl-scrabble/issues/118

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

1-2 hours

## Description

Add pyupgrade to automatically modernize Python syntax to leverage features from Python 3.10+ while maintaining compatibility with the minimum supported version. Currently, the project targets Python 3.10-3.14 but doesn't automatically upgrade syntax to use newer Python features, leading to inconsistent code patterns and missed opportunities for cleaner, more Pythonic code.

**Impact**: Automatic syntax upgrades, reduced technical debt, improved code readability

**ROI**: High - minimal setup effort, automatic ongoing improvements

## Current State

The project has comprehensive linting and formatting tools (ruff, black, mypy) but lacks automatic syntax modernization:

**pyproject.toml (line 24)**:

```toml
requires-python = ">=3.10,<3.15"
```

**Current code patterns that could be modernized**:

```python
# Old-style type hints
from typing import Optional, Union, List, Dict

def process_data(items: Optional[List[str]]) -> Dict[str, Union[int, str]]:
    pass

# Could be modernized to:
def process_data(items: list[str] | None) -> dict[str, int | str]:
    pass
```

**Missing tool**:

- No pyupgrade in .pre-commit-config.yaml
- No pyupgrade in tox.ini
- No pyupgrade in CI workflows
- Manual syntax upgrades required

**Modernization opportunities**:

- `typing.Optional[X]` → `X | None` (PEP 604)
- `typing.Union[X, Y]` → `X | Y` (PEP 604)
- `typing.List`, `Dict`, `Set`, `Tuple` → built-in `list`, `dict`, `set`, `tuple` (PEP 585)
- Old string formatting → f-strings
- `format()` calls → f-strings where appropriate
- Unnecessary `__future__` imports for Python 3.10+
- Legacy syntax from Python 2

## Proposed Solution

Add pyupgrade as a comprehensive syntax modernization tool across all quality frameworks:

**Step 1: Add to Pre-commit (.pre-commit-config.yaml)**:

```yaml
# Add after ruff-format, before ruff-check
- repo: https://github.com/asottile/pyupgrade
  rev: v3.15.1  # Latest version
  hooks:
    - id: pyupgrade
      name: pyupgrade
      description: Automatically upgrade syntax for newer Python versions
      args:
        - --py310-plus  # Target Python 3.10+ syntax
      # Align with ruff's file exclusions
      exclude: ^(\.git|\.tox|\.venv|venv|build|dist|.*\.egg-info)
```

**Step 2: Add to tox.ini**:

```ini
[testenv:pyupgrade]
description = Modernize Python syntax with pyupgrade
skip_install = true
deps =
    pyupgrade
commands_pre =
    pyupgrade --version
commands =
    bash -c 'pyupgrade --py310-plus $(find src tests -name "*.py")'
allowlist_externals =
    bash
    find
labels = format, quality
```

**Step 3: Add to CI workflow (.github/workflows/ci.yml)**:

```yaml
# Add to tox matrix
strategy:
  matrix:
    tox-env:
      - pyupgrade  # Add alongside other quality checks
      # ... existing environments
```

**Step 4: Add to pyproject.toml dependencies** (optional for local use):

```toml
[project.optional-dependencies]
lint = [
    "ruff>=0.3.0",
    "pyupgrade>=3.15.0",  # Add syntax modernization
]
```

**Step 5: Add to CI simulation (tox ci environment)**:

```ini
[testenv:ci]
commands =
    # ... existing commands
    bash -c 'pyupgrade --py310-plus --check $(find src tests -name "*.py")'
```

## Implementation Steps

1. **Add pyupgrade to pre-commit configuration**:

   - Add hook after ruff-format, before ruff-check
   - Configure `--py310-plus` to target Python 3.10+ syntax
   - Align exclusions with existing tools

1. **Add pyupgrade to tox environments**:

   - Create `[testenv:pyupgrade]` with proper configuration
   - Add to `env_list` for standard testing
   - Add `allowlist_externals` for bash and find

1. **Add pyupgrade to CI workflow**:

   - Add to tox matrix in `.github/workflows/ci.yml`
   - Ensures syntax modernization runs on every PR

1. **Run pyupgrade on entire codebase**:

   - Run: `pyupgrade --py310-plus $(find src tests -name "*.py")`
   - Review and commit automated changes
   - Verify all tests still pass

1. **Update documentation**:

   - Document pyupgrade in CONTRIBUTING.md
   - Add to list of quality tools
   - Explain syntax modernization approach

1. **Test integration**:

   - Run full pre-commit: `pre-commit run --all-files`
   - Run tox: `tox -e pyupgrade`
   - Verify CI passes

## Testing Strategy

**Pre-commit Testing**:

```bash
# Test pre-commit hook
pre-commit run pyupgrade --all-files

# Should show modernized syntax changes
```

**Tox Testing**:

```bash
# Test tox environment
tox -e pyupgrade

# Expected output: List of files that would be modified
# In check mode: Exit code 1 if changes needed
```

**Integration Testing**:

```bash
# Run with other formatters
pre-commit run --all-files

# Verify:
# 1. pyupgrade modernizes syntax
# 2. black/ruff-format adjust formatting
# 3. ruff-check validates result
# 4. All tools work harmoniously
```

**Manual Verification**:

```bash
# Find old-style type hints
grep -r "Optional\[" src/
grep -r "Union\[" src/
grep -r "from typing import List, Dict" src/

# After pyupgrade:
# - Optional[X] → X | None
# - Union[X, Y] → X | Y
# - List, Dict → list, dict
```

**Regression Testing**:

```bash
# After modernization, verify:
pytest  # All tests pass
mypy src  # Type checking passes
tox -e py310  # Works on minimum Python version
```

## Acceptance Criteria

- [ ] pyupgrade hook added to .pre-commit-config.yaml
- [ ] pyupgrade configured with `--py310-plus` argument
- [ ] pyupgrade tox environment created in tox.ini
- [ ] pyupgrade added to CI workflow matrix
- [ ] Pre-commit hook runs successfully on all files
- [ ] Tox environment executes without errors
- [ ] CI includes pyupgrade checks
- [ ] All existing tests pass after syntax modernization
- [ ] Type checking (mypy) passes after changes
- [ ] Code works on Python 3.10 (minimum version)
- [ ] Documentation updated with pyupgrade information
- [ ] No breaking changes introduced

## Related Files

- `.pre-commit-config.yaml` - Add pyupgrade hook
- `tox.ini` - Add pyupgrade environment
- `.github/workflows/ci.yml` - Add to tox matrix
- `pyproject.toml` - Optional: Add to lint dependencies
- `CONTRIBUTING.md` - Document syntax modernization tool
- `src/**/*.py` - All Python source files (modernized)
- `tests/**/*.py` - All test files (modernized)

## Dependencies

**None** - Independent enhancement

**Recommended order**:

- Can be implemented independently
- Complements existing formatters (black, ruff-format)
- Works alongside ruff-check and mypy

**Conflicts**: None - pyupgrade works harmoniously with existing tools

## Additional Notes

**Why pyupgrade?**

- **Automatic modernization**: No manual refactoring needed
- **Consistent syntax**: Entire codebase uses modern idioms
- **Future-proof**: Automatically adopts new Python features
- **Educational**: Teaches modern Python patterns
- **Safe**: Only applies syntax changes, not logic changes

**Python 3.10+ Features Enabled**:

```python
# PEP 604: Union types with |
Optional[str] → str | None
Union[int, str] → int | str

# PEP 585: Built-in generics
List[int] → list[int]
Dict[str, int] → dict[str, int]
Set[str] → set[str]
Tuple[int, ...] → tuple[int, ...]

# PEP 563: Postponed evaluation of annotations (implicit)
# Enables forward references without string quotes

# Better string formatting
"{}".format(x) → f"{x}"
"{0} {1}".format(a, b) → f"{a} {b}"

# Remove unnecessary __future__ imports
from __future__ import annotations  # Can be removed in some cases
```

**Configuration Options**:

```bash
# Target specific Python version
--py310-plus  # Python 3.10+ (our choice)
--py311-plus  # Python 3.11+
--py312-plus  # Python 3.12+

# Keep certain patterns
--keep-percent-format  # Keep % formatting
--keep-mock  # Keep mock imports
--keep-runtime-typing  # Keep typing imports at runtime
```

**Integration with Existing Tools**:

| Tool            | Role           | Interaction with pyupgrade               |
| --------------- | -------------- | ---------------------------------------- |
| **black**       | Formatting     | Runs after pyupgrade, adjusts formatting |
| **ruff-format** | Formatting     | Runs after pyupgrade, adjusts formatting |
| **ruff-check**  | Linting        | Validates modernized syntax              |
| **mypy**        | Type checking  | Works with modernized type hints         |
| **isort**       | Import sorting | Handles removed typing imports           |

**Order in pre-commit** (important):

1. `pyupgrade` - Modernize syntax first
1. `black` - Format code
1. `ruff-format` - Additional formatting
1. `ruff-check --fix` - Fix linting issues

**Gradual Adoption Strategy**:

```bash
# Phase 1: Add to pre-commit only
# - New commits get modernized automatically
# - Existing code unchanged

# Phase 2: Run on entire codebase
pyupgrade --py310-plus $(find src tests -name "*.py")
git commit -m "refactor: Modernize Python syntax with pyupgrade"

# Phase 3: Enforce in CI
# - Add to tox matrix
# - Block PRs with outdated syntax
```

**Common Transformations** (examples from this project):

```python
# Before
from typing import Optional, Union, List, Dict
from nhl_scrabble.models.player import PlayerScore

def get_player(name: str) -> Optional[PlayerScore]:
    players: List[PlayerScore] = fetch_players()
    mapping: Dict[str, PlayerScore] = {p.full_name: p for p in players}
    return mapping.get(name)

# After
from nhl_scrabble.models.player import PlayerScore

def get_player(name: str) -> PlayerScore | None:
    players: list[PlayerScore] = fetch_players()
    mapping: dict[str, PlayerScore] = {p.full_name: p for p in players}
    return mapping.get(name)
```

**False Positives** (rare):

- Runtime type checking (e.g., `isinstance(x, typing.List)`) needs `typing.List`
- Type aliases exported as public API should be carefully reviewed
- Some dynamic typing scenarios may need manual review

**Alternatives Considered**:

1. **Manual refactoring**: Too time-consuming, error-prone
1. **Ruff's UP rules**: Good, but less specialized than pyupgrade
1. **Keep old syntax**: Misses benefits of modern Python

**pyupgrade vs ruff UP rules**:

- **ruff UP**\*: Subset of pyupgrade features in ruff-check
- **pyupgrade**: Dedicated tool, more comprehensive
- **Best practice**: Use both - pyupgrade for syntax, ruff for validation

**Benefits for This Project**:

- **Cleaner type hints**: `str | None` is more readable than `Optional[str]`
- **Reduced imports**: No need for `typing.List`, `Dict`, etc.
- **Modern idioms**: Code looks like current Python best practices
- **Easier onboarding**: New contributors see modern Python

**Metrics to Track**:

- Number of files modernized
- Lines of code changed
- Typing imports removed
- Test suite still passing

## Implementation Notes

*To be filled during implementation:*

- Actual number of files/lines changed by pyupgrade
- Any edge cases or manual adjustments needed
- Integration with other tools (any conflicts?)
- Performance impact (if any)
- Developer feedback on modernized syntax
