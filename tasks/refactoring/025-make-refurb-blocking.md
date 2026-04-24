# Make 'refurb' Blocking After Validation Period

**GitHub Issue**: [#356](https://github.com/bdperkin/nhl-scrabble/issues/356)

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

30 minutes - 1 hour

## Description

Transition 'refurb' Python code modernization linter from warning/validation mode to blocking mode after sufficient validation period. Currently refurb runs in pre-commit but doesn't fail commits when it finds modernization opportunities. After confirming refurb suggestions are valuable and don't cause disruption, it should be made blocking to enforce modern Python idioms.

## Current State

The 'refurb' linter is currently configured as non-blocking in one place:

**Pre-commit Hook** (`.pre-commit-config.yaml`):
```yaml
- id: refurb
  name: refurb (warning mode - non-blocking)
  description: Python code modernization linter (pathlib, comprehensions, modern idioms)
  entry: bash -c 'refurb src/ --enable-all || true'
  language: system
  types: [python]
  pass_filenames: false
  verbose: true
  # Non-blocking during adoption phase (remove '|| true' after team training)
  # Configuration is read automatically from pyproject.toml
```

**Configuration** (`pyproject.toml`):
```toml
[tool.refurb]
enable_all = true
python_version = "3.12"
ignore = []
```

The configuration uses comprehensive checking (`enable_all = true`) matching ruff's ALL rules philosophy, but the pre-commit hook is non-blocking during the adoption phase.

## Proposed Solution

After a validation period (suggested: 4-8 weeks or 20-40 PRs), make refurb blocking:

**1. Update Pre-commit Hook**:
```yaml
- id: refurb
  name: refurb - Python code modernization
  description: Python code modernization linter (pathlib, comprehensions, modern idioms)
  entry: refurb src/ --enable-all
  language: system
  types: [python]
  pass_filenames: false
  verbose: true
  # Blocking: refurb suggestions will prevent commits
  # Configuration is read automatically from pyproject.toml
```

**2. Update pyproject.toml (if needed)**:
```toml
[tool.refurb]
enable_all = true
python_version = "3.12"
# Add specific ignores only after validation if certain checks are too noisy
ignore = []  # Start with no ignores, add only if necessary
```

**3. Update Documentation**:
- Update CLAUDE.md to reflect refurb as a blocking check
- Update pre-commit hook comments
- Update hook count (67 hooks → 67 hooks, status change only)

## Implementation Steps

1. **Validation Assessment**:
   - Review recent PRs to see how many refurb suggestions occurred
   - Categorize suggestions by type:
     - Pathlib usage (Path vs os.path)
     - Modern comprehensions
     - Dict merging with | operator
     - Type hint improvements
     - Iterator improvements
   - Identify any false positives or unhelpful suggestions
   - Assess developer feedback on refurb suggestions
   - Ensure refurb version is stable

2. **Build Ignore List (if needed)**:
   - If certain checks are consistently unhelpful or create churn, add to ignore list
   - Document WHY each check is ignored (add comments in pyproject.toml)
   - Prefer selective ignores over disabling entire categories
   - Re-evaluate ignores quarterly

3. **Configuration Updates**:
   - Remove `|| true` from pre-commit hook entry
   - Update hook name from "warning mode - non-blocking" to blocking
   - Update comments to reflect blocking status
   - Test hook fails appropriately on refurb suggestions

4. **Documentation Updates**:
   - Update CLAUDE.md section on refurb linter
   - Update pre-commit hook documentation
   - Add refurb to list of blocking quality checks
   - Document any ignores and their rationale

5. **Communication**:
   - Document the change in PR description
   - Note that refurb is now blocking in commit messages
   - Provide examples of common refurb patterns to fix
   - Update contributing guidelines if necessary

## Testing Strategy

**Pre-deployment Testing**:
1. Temporarily make refurb blocking in local environment
2. Run pre-commit hooks on all files: `pre-commit run refurb --all-files`
3. Verify refurb fails appropriately on modernization opportunities
4. Verify refurb passes on already-modernized code
5. Test that commit is blocked when refurb finds issues
6. Document time to fix all refurb suggestions (baseline for developers)

**Post-deployment Monitoring**:
1. Monitor first 10 PRs for refurb-related failures
2. Track false positives and unhelpful suggestions
3. Be ready to add ignores or revert to warning mode if too disruptive
4. Adjust refurb configuration if needed (via pyproject.toml)
5. Collect developer feedback on refurb usefulness

## Acceptance Criteria

- [ ] refurb validation period complete (4-8 weeks or 20-40 PRs)
- [ ] Refurb suggestions reviewed and categorized
- [ ] False positives identified and added to ignore list (if any)
- [ ] Pre-commit hook blocks commits on refurb suggestions
- [ ] Documentation updated to reflect blocking status
- [ ] CLAUDE.md updated
- [ ] Contributing guidelines updated (if applicable)
- [ ] All tests pass
- [ ] Developer training materials created (if needed)

## Related Files

- `.pre-commit-config.yaml` - Pre-commit hook configuration for refurb
- `pyproject.toml` - refurb configuration
- `CLAUDE.md` - Project documentation
- `CONTRIBUTING.md` - Contributing guidelines (if applicable)
- `src/nhl_scrabble/` - Source code that will be checked

## Dependencies

**Prerequisite**:
- Validation period must be complete
- refurb should have proven valuable and not too disruptive
- Team should be familiar with common refurb patterns
- No major false positive issues or unhelpful suggestions

**No blocking dependencies** on other tasks

**Related task**:
- Task 024 - Make 'ty' blocking (parallel effort, same validation approach)

## Additional Notes

**Validation Period Guidelines**:
- **Minimum**: 4 weeks or 20 PRs with refurb enabled
- **Ideal**: 8 weeks or 40 PRs with refurb enabled
- **Criteria**: < 10% unhelpful suggestions rate
- **Developer feedback**: Positive or neutral on refurb value

**Why Longer Than ty?**:
- refurb suggests STYLE changes, not correctness issues
- Style preferences can be subjective
- Need more time to assess if suggestions improve code quality
- Need to build consensus on which patterns to enforce

**Reversion Plan**:
If refurb causes problems after making blocking:
1. Revert pre-commit hook to warning mode (`|| true`)
2. Add specific unhelpful checks to ignore list
3. Create issue to investigate refurb configuration
4. Schedule another validation period after adjustments

**Performance Considerations**:
- refurb is written in Python (not Rust like ruff/ty)
- Performance is acceptable for pre-commit usage
- Should not significantly impact pre-commit times
- Monitor pre-commit times before/after transition

**Configuration Options**:
If refurb needs adjustment, configure via `pyproject.toml`:
```toml
[tool.refurb]
enable_all = true
python_version = "3.12"
# Example: Disable specific checks if unhelpful
ignore = [
    "FURB123",  # Example: Specific check to ignore
]
```

**Common refurb Patterns**:
1. **Pathlib usage**: `Path("file.txt").read_text()` vs `open("file.txt").read()`
2. **Dict merging**: `a | b` vs `{**a, **b}`
3. **Comprehensions**: `[x for x in items if cond]` vs `filter(lambda x: cond, items)`
4. **Type hints**: Modern union syntax `str | None` vs `Optional[str]`
5. **Iterator improvements**: `next(iter(items), default)` vs manual iteration

**Benefits of Making Blocking**:
1. **Modern Python**: Enforces Python 3.12+ idioms and patterns
2. **Consistency**: All code uses modern patterns
3. **Readability**: Modern Python is often more readable
4. **Educational**: Developers learn modern Python patterns
5. **Complementary**: Works alongside pyupgrade (syntax) and ruff (lint)

**Trade-offs**:
1. **Style enforcement**: Some patterns are subjective preferences
2. **Learning curve**: Developers need to learn modern patterns
3. **Potential churn**: Existing code may trigger many suggestions
4. **Maintenance overhead**: Need to manage ignore list over time

**Examples of refurb Suggestions**:

**Before** (old pattern):
```python
# os.path usage
import os
filepath = os.path.join("data", "file.txt")
if os.path.exists(filepath):
    with open(filepath) as f:
        content = f.read()

# Dict merging
merged = {**dict1, **dict2}

# Optional type hint
from typing import Optional
def func(x: Optional[str] = None) -> None:
    pass
```

**After** (refurb suggestion):
```python
# pathlib usage
from pathlib import Path
filepath = Path("data") / "file.txt"
if filepath.exists():
    content = filepath.read_text()

# Dict merging with |
merged = dict1 | dict2

# Modern union syntax
def func(x: str | None = None) -> None:
    pass
```

## Implementation Notes

*To be filled during implementation*
