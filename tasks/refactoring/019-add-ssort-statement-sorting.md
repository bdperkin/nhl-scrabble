# Add ssort Python Statement Sorter

**GitHub Issue**: #246 - https://github.com/bdperkin/nhl-scrabble/issues/246

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

2-3 hours

## Description

Add ssort tool to automatically sort Python class members and functions in a consistent, standardized order (dunder methods, class methods, properties, regular methods). This improves code readability and reduces bike-shedding about member ordering.

## Current State

**Statement Ordering Gap:**

The project currently has:

- ✅ Import sorting (isort, ruff)
- ✅ Code formatting (black, ruff-format)
- ❌ **NO class member ordering**
- ❌ **Inconsistent method order across classes**
- ❌ **Manual organization required**

**Current Class Structure (Inconsistent):**

```python
# Example: Inconsistent ordering across classes

# Class A: Random order
class ClassA:
    def public_method(self):
        pass

    def __init__(self):
        pass

    @property
    def property_name(self):
        pass

    def _private_method(self):
        pass

# Class B: Different order
class ClassB:
    @property
    def property_name(self):
        pass

    def __init__(self):
        pass

    def public_method(self):
        pass
```

**Why Consistent Ordering Matters:**

1. **Readability**: Always know where to find methods
1. **Consistency**: Same structure across all classes
1. **Code Reviews**: Focus on logic, not order
1. **Onboarding**: Easier for new contributors
1. **Reduces Bike-shedding**: No debates about order

## Proposed Solution

### 1. Add ssort to Pre-commit Hooks

**Configuration:**

```yaml
# .pre-commit-config.yaml

  # ============================================================================
  # Python Statement Sorting - Class Member Organization
  # ============================================================================

  - repo: https://github.com/bwhmather/ssort
    rev: v0.13.0
    hooks:
      - id: ssort
        name: ssort
        description: Sort Python class members and statements
        # WARNING: Can be opinionated - review changes carefully
        # Start in check mode (--check) to see what would change
        args: []
        # Exclude files where order matters (e.g., migrations, specific patterns)
        exclude: ^(tests/fixtures/|migrations/)
```

**Why Pre-commit:**

- Automatic ordering on commit
- Consistent structure
- Fast execution (< 3 seconds)
- Zero manual effort

**⚠️ WARNING - Review Changes Carefully:**

- ssort can reorder statements in surprising ways
- Some intentional orderings may be changed
- Test thoroughly after initial application
- Consider starting in check-only mode

### 2. Add Configuration

**pyproject.toml:**

```toml
[tool.ssort]
# Sections to sort (in order):
# 1. __future__ imports
# 2. Module docstring
# 3. Imports
# 4. Module-level constants
# 5. Module-level code
# 6. Class definitions
# 7. Function definitions

# Skip sorting in these files
skip = [
    "tests/fixtures/",
    "migrations/",
]

# Files to sort (glob patterns)
src_paths = ["src/", "tests/"]
```

**Default ssort Ordering for Classes:**

1. **Dunder methods** (in specific order):

   - `__new__`
   - `__init__`
   - `__post_init__`
   - Other dunder methods (alphabetically)
   - `__repr__`
   - `__str__`
   - Comparison methods (`__eq__`, `__lt__`, etc.)
   - `__hash__`

1. **Class methods** (alphabetically):

   - `@classmethod` decorated methods

1. **Static methods** (alphabetically):

   - `@staticmethod` decorated methods

1. **Properties** (alphabetically):

   - `@property` decorated methods
   - Property setters/deleters

1. **Public methods** (alphabetically):

   - Regular methods (no leading underscore)

1. **Private methods** (alphabetically):

   - Methods with leading underscore

**Example Result:**

```python
class Example:
    """Class docstring."""

    # 1. Dunder methods
    def __init__(self, value: int):
        self.value = value

    def __repr__(self) -> str:
        return f"Example({self.value})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Example):
            return NotImplemented
        return self.value == other.value

    # 2. Class methods
    @classmethod
    def from_string(cls, s: str) -> "Example":
        return cls(int(s))

    # 3. Properties
    @property
    def doubled(self) -> int:
        return self.value * 2

    # 4. Public methods (alphabetically)
    def increment(self) -> None:
        self.value += 1

    def reset(self) -> None:
        self.value = 0

    # 5. Private methods (alphabetically)
    def _internal_helper(self) -> int:
        return self.value + 1
```

### 3. Add Tox Environment

**tox.ini:**

```ini
[testenv:ssort]
description = Sort Python class members and statements
deps = ssort>=0.13.0
commands =
    # Check mode (show what would change)
    ssort --check --diff src/ tests/

    # Apply sorting (uncomment after review)
    # ssort src/ tests/

[testenv:ssort-apply]
description = Apply ssort statement sorting
deps = {[testenv:ssort]deps}
commands = ssort src/ tests/
```

**Why Tox:**

- Check mode: `tox -e ssort` (dry run)
- Apply sorting: `tox -e ssort-apply`
- Safe testing before commit

### 4. Add Makefile Targets

**Makefile:**

```makefile
.PHONY: ssort ssort-check ssort-apply

ssort-check:  ## Check Python statement ordering (dry run)
	@echo "Checking Python statement ordering..."
	ssort --check --diff src/ tests/

ssort-apply:  ## Apply Python statement sorting
	@echo "Sorting Python statements..."
	ssort src/ tests/

ssort: ssort-check  ## Alias for ssort-check
```

**Why Makefile:**

- Quick check: `make ssort-check`
- Apply sorting: `make ssort-apply`
- Team consistency

### 5. Initial Application (WITH CAUTION)

**⚠️ IMPORTANT - Review Changes Carefully:**

```bash
# Install ssort
pip install ssort

# 1. Check what would change (DRY RUN - safe)
ssort --check --diff src/ tests/

# Review output carefully:
# - Are reorderings sensible?
# - Any intentional orderings disrupted?
# - Methods still logically grouped?

# 2. Apply to single file first (TEST)
ssort src/nhl_scrabble/models/player.py

# 3. Review changes
git diff src/nhl_scrabble/models/player.py

# 4. Run tests
pytest tests/

# 5. If tests pass and changes look good, apply to more files
ssort src/nhl_scrabble/models/

# 6. Review, test, repeat
git diff
pytest

# 7. Apply to entire codebase only after thorough testing
ssort src/ tests/

# 8. Final verification
pytest
ruff check src/
mypy src/

# 9. Commit if all checks pass
git add -A
git commit -m "style: Sort Python class members with ssort"
```

**When NOT to Use ssort:**

- **Migration files**: Order matters
- **Test fixtures**: Specific setup order required
- **Intentionally ordered code**: Performance-critical sequences
- **Generated code**: Auto-generated files

### 6. Exclude Intentional Orderings

**Files to exclude:**

```yaml
# .pre-commit-config.yaml
- id: ssort
  exclude: |
    (?x)^(
        tests/fixtures/|
        migrations/|
        src/nhl_scrabble/special_order.py
    )$
```

**Mark specific sections to preserve order:**

```python
# Use comments to document why order matters
class SpecialClass:
    """Class where method order is intentional."""

    # NOTE: Methods ordered by execution sequence, not alphabetically
    # DO NOT SORT - performance critical order
    def step_one(self):
        pass

    def step_two(self):
        pass

    def step_three(self):
        pass
```

## Implementation Steps

1. **Test ssort on Sample Files** (20 min)

   - Install ssort
   - Run `ssort --check --diff` on 2-3 files
   - Review proposed changes
   - Assess if changes are beneficial or disruptive

1. **Apply to Single Module** (15 min)

   - Choose a simple module (e.g., models)
   - Apply ssort: `ssort src/nhl_scrabble/models/player.py`
   - Review changes carefully
   - Run tests: `pytest tests/unit/test_models.py`
   - Verify no regressions

1. **Gradually Apply to Codebase** (30 min)

   - Apply module by module
   - Review each change
   - Run tests after each module
   - Identify files to exclude
   - Document intentional orderings

1. **Add Pre-commit Hook** (10 min)

   - Update `.pre-commit-config.yaml`
   - Add exclusions for problematic files
   - Test hook: `pre-commit run ssort --all-files`

1. **Add Tox Environments** (10 min)

   - Add `[testenv:ssort]` and `[testenv:ssort-apply]`
   - Test: `tox -e ssort`

1. **Add Makefile Targets** (5 min)

   - Add `ssort-check` and `ssort-apply` targets
   - Test: `make ssort-check`

1. **Update Documentation** (10 min)

   - Update CONTRIBUTING.md with ssort usage
   - Document excluded files and reasons
   - Note about reviewing ssort changes carefully

1. **Team Review** (20 min)

   - Share changes with team
   - Get feedback on reorderings
   - Adjust exclusions based on feedback
   - Document team preferences

## Testing Strategy

### Manual Testing

```bash
# Test check mode (dry run)
ssort --check --diff src/
# Verify: Shows what would change without modifying files

# Test apply mode on single file
cp src/nhl_scrabble/models/player.py player_backup.py
ssort src/nhl_scrabble/models/player.py
diff player_backup.py src/nhl_scrabble/models/player.py
# Verify: Only ordering changed, no logic changes
mv player_backup.py src/nhl_scrabble/models/player.py

# Test with intentionally ordered code
cat > test_ordered.py <<'EOF'
class TestClass:
    def third_method(self):
        pass
    def first_method(self):
        pass
    def second_method(self):
        pass
EOF

ssort test_ordered.py
cat test_ordered.py
# Verify: Methods reordered alphabetically
rm test_ordered.py
```

### Integration Testing

```bash
# Apply ssort to codebase
ssort src/ tests/

# Ensure code still works
pytest
# Verify: All tests pass

# Ensure formatters still work
black src/
ruff format src/
# Verify: No conflicts

# Ensure type checking still works
mypy src/
# Verify: No new type errors
```

### Regression Testing

```bash
# Before ssort
pytest --cov
# Record coverage: X%

# After ssort
pytest --cov
# Verify: Coverage unchanged (logic unchanged)

# Before ssort
time pytest
# Record time: Y seconds

# After ssort
time pytest
# Verify: Time similar (no performance regression)
```

## Acceptance Criteria

- [ ] ssort tested on sample files
- [ ] Team reviewed and approved approach
- [ ] ssort applied to codebase (or decided against)
- [ ] All tests pass after sorting
- [ ] No logic changes (only ordering)
- [ ] Pre-commit hook configured (if adopted)
- [ ] Tox environments working
- [ ] Makefile targets added
- [ ] Exclusions documented
- [ ] Documentation updated (CONTRIBUTING.md)

## Related Files

**Modified Files:**

- `.pre-commit-config.yaml` - Add ssort hook (if adopted)
- `pyproject.toml` - Add `[tool.ssort]` configuration
- `tox.ini` - Add ssort environments
- `Makefile` - Add ssort targets
- `CONTRIBUTING.md` - Document ssort usage and exclusions
- `src/**/*.py` - Reordered class members (if adopted)

**No New Files** - All configuration in existing files

## Dependencies

**Python Dependencies:**

- `ssort>=0.13.0` - Install via pip/uv

**No Task Dependencies** - Can implement independently

**Related Tasks:**

- refactoring/016 - Add trailing comma (complementary formatting)

## Additional Notes

### ssort Philosophy

**Consistent Structure:**

- Same member order across all classes
- Predictable locations for methods
- Easier to navigate code

**Opinionated Approach:**

- Has strong opinions on order
- May conflict with manual organization
- Requires team buy-in

**Trade-offs:**

- **Pro**: Zero bike-shedding about order
- **Pro**: Consistent structure
- **Con**: May reorder intentional groupings
- **Con**: Alphabetical order may not be logical order

### When ssort Works Well

**Good Candidates:**

- Data classes (models, DTOs)
- Simple classes with many methods
- Utility classes
- Classes with clear public API

**Poor Candidates:**

- State machines (order matters for flow)
- Performance-critical classes (order affects inlining)
- Classes with complex method interactions
- Legacy code with established patterns

### Alternative Approach: Manual Guidelines

Instead of using ssort, consider documenting guidelines:

```python
# Class Member Ordering Guidelines (manual)
class StandardClass:
    """
    Recommended order:
    1. Class variables
    2. __init__
    3. Other dunder methods
    4. @classmethod methods
    5. @property methods
    6. Public methods (grouped logically, not alphabetically)
    7. Private methods (grouped with related public methods)
    """
```

### Integration with Existing Tools

**With isort:**

- isort sorts imports
- ssort sorts everything else
- Complementary tools

**With black/ruff-format:**

- Formatters don't change order
- ssort changes order, not formatting
- Run ssort before formatters

### Performance Impact

- **Pre-commit hook**: +2-5 seconds
- **Tox environment**: ~10 seconds
- **Initial application**: ~30 seconds for full codebase
- **Minimal ongoing impact**: Only files changed

### Potential Issues

**Intentional Ordering Disrupted:**

```python
# Before ssort: Intentionally ordered by execution flow
def step_1_fetch_data(self):
    pass

def step_2_process_data(self):
    pass

def step_3_save_data(self):
    pass

# After ssort: Alphabetical order (loses flow context)
def step_1_fetch_data(self):
    pass

def step_3_save_data(self):  # Now before step 2!
    pass

def step_2_process_data(self):
    pass
```

**Solution**: Exclude file or rename methods to preserve order.

### Team Decision Required

**This task requires team consensus:**

1. **Trial Period**: Apply to small subset, get feedback
1. **Team Vote**: Decide if benefits outweigh costs
1. **Gradual Adoption**: Start with new files only
1. **Full Exclusion**: Document guidelines instead

**Decision Criteria:**

- Does team value consistent ordering?
- Are there many classes to organize?
- Is manual ordering causing review friction?
- Are intentional orderings common?

### Success Metrics (If Adopted)

- [ ] Consistent class member order across codebase
- [ ] Zero debates about method ordering in PRs
- [ ] Easier code navigation
- [ ] Team satisfied with ssort results
- [ ] No logic regressions from reordering

### Success Metrics (If Not Adopted)

- [ ] Team consensus on manual ordering guidelines
- [ ] Guidelines documented in CONTRIBUTING.md
- [ ] PRs follow guidelines
- [ ] Task closed as "decided against"

## Implementation Notes

*To be filled during implementation:*

- Team decision: Adopt ssort? Yes/No
- If yes: Number of files reordered, changes applied
- If no: Manual guidelines documented instead
- Issues encountered with reordering
- Files excluded and reasons
- Team feedback
- Deviations from plan
- Actual effort vs estimated
