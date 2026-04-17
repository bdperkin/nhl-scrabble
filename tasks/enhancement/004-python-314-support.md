# Add Python 3.14 Support and Testing

**GitHub Issue**: #97 - https://github.com/bdperkin/nhl-scrabble/issues/97

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

2-3 hours

## Description

Add official support and comprehensive testing for Python 3.14 across the entire project. Python 3.14 is scheduled for release in October 2025, and the project should stay current with the latest Python versions to ensure compatibility and access to new features.

## Current State

The project currently supports Python 3.10-3.13:

**pyproject.toml**:

```toml
[project]
requires-python = ">=3.10,<3.14"
classifiers = [
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
]
```

**CI Workflow (.github/workflows/ci.yml)**:

```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.11", "3.12", "3.13"]
```

**Tox Configuration (tox.ini)**:

```ini
env_list =
    # ...
    py{313, 312, 311, 310}
```

**Issues**:

- Python 3.14 is explicitly excluded in `requires-python = ">=3.10,<3.14"`
- CI/CD does not test on Python 3.14
- Tox does not include py314 environment
- Classifiers do not list Python 3.14
- Documentation does not mention Python 3.14 support

## Proposed Solution

### 1. Update pyproject.toml

Update Python version constraint and classifiers:

```toml
[project]
requires-python = ">=3.10,<3.15"  # Changed from <3.14 to <3.15
classifiers = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",  # NEW
    # ...
]
```

### 2. Update CI Workflow

Add Python 3.14 to the test matrix:

**.github/workflows/ci.yml**:

```yaml
jobs:
  test:
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13", "3.14"]  # Added 3.14
```

Also update tox job if it uses Python version:

```yaml
  tox:
    strategy:
      matrix:
        tox-env:
          - py310
          - py311
          - py312
          - py313
          - py314  # NEW
          # ... other envs
```

### 3. Update Tox Configuration

Add py314 to tox environments:

**tox.ini**:

```ini
[tox]
env_list =
    # ...
    py{314, 313, 312, 311, 310}  # Added 314
```

### 4. Update Documentation

Update any documentation that mentions supported Python versions:

**README.md** (if it mentions Python versions):

```markdown
## Requirements

- Python 3.10, 3.11, 3.12, 3.13, or 3.14
```

**CLAUDE.md** (environment section):

```markdown
# Environment
- Python: 3.10-3.14
```

**docs/** (any Python version references):

- Update installation instructions
- Update compatibility tables
- Update troubleshooting guides

### 5. Update Lock File

Regenerate UV lock file with Python 3.14 constraints:

```bash
uv lock
```

This ensures dependencies are resolved for Python 3.14 compatibility.

## Implementation Steps

1. **Update pyproject.toml**

   - Change `requires-python = ">=3.10,<3.15"`
   - Add Python 3.14 classifier

1. **Update CI Workflow**

   - Add "3.14" to python-version matrix in test job
   - Add py314 to tox-env matrix in tox job

1. **Update tox.ini**

   - Add 314 to py{...} environments

1. **Update Lock File**

   - Run `uv lock` to regenerate with new Python version
   - Verify lock file includes Python 3.14 compatible versions

1. **Local Testing** (if Python 3.14 available)

   - Install Python 3.14
   - Run `tox -e py314`
   - Verify all tests pass

1. **Update Documentation**

   - Update README.md
   - Update CLAUDE.md
   - Update docs/ files
   - Update any version references

1. **Commit Changes**

   - Create feature branch
   - Commit all updates
   - Push to GitHub

1. **Verify CI/CD**

   - Create PR
   - Wait for CI to run on Python 3.14
   - Fix any compatibility issues that arise

## Testing Strategy

### Pre-commit Checks

```bash
# Run pre-commit hooks
pre-commit run --all-files
```

### Local Testing (if Python 3.14 available)

```bash
# Install Python 3.14 (via pyenv, asdf, or system package manager)
pyenv install 3.14.0  # or latest 3.14.x

# Test with tox
tox -e py314

# Test directly
python3.14 -m pip install -e ".[test]"
python3.14 -m pytest

# Test CLI
python3.14 -m nhl_scrabble analyze
```

### CI/CD Testing

After pushing changes:

1. GitHub Actions will automatically test on Python 3.14
1. Verify all test jobs pass
1. Check coverage reports
1. Verify pre-commit hooks pass
1. Check tox py314 environment passes

### Compatibility Testing

Verify no breaking changes:

```bash
# Run full test suite
pytest

# Run quality checks
make quality

# Run tox on all Python versions
tox -p auto
```

## Acceptance Criteria

- [ ] `pyproject.toml` updated with `requires-python = ">=3.10,<3.15"`
- [ ] Python 3.14 classifier added to `pyproject.toml`
- [ ] CI workflow tests on Python 3.14 (test job)
- [ ] Tox workflow includes py314 environment
- [ ] `tox.ini` includes py314 in env_list
- [ ] UV lock file regenerated
- [ ] README.md mentions Python 3.14 support
- [ ] CLAUDE.md updated with Python 3.14
- [ ] All documentation updated
- [ ] CI tests pass on Python 3.14
- [ ] No dependency conflicts for Python 3.14
- [ ] All existing tests pass on Python 3.14

## Related Files

- `pyproject.toml` - Python version constraints and classifiers
- `.github/workflows/ci.yml` - CI/CD workflow with test matrix
- `tox.ini` - Tox environments
- `uv.lock` - Dependency lock file
- `README.md` - User documentation
- `CLAUDE.md` - Developer documentation
- `docs/tutorials/01-getting-started.md` - Installation instructions
- `docs/reference/installation.md` - Installation reference
- `docs/how-to/installation.md` - Installation how-to

## Dependencies

None - This is a configuration change that does not depend on other tasks.

## Additional Notes

### Python 3.14 Timeline

- **Release Date**: October 2025 (estimated)
- **Pre-release**: Alpha/beta versions may be available earlier
- **EOL**: October 2030 (5 years of support)

### Compatibility Considerations

1. **Dependencies**: Most dependencies should already support Python 3.14 if they support 3.13
1. **Type Hints**: Python 3.14 may have enhanced type hint features
1. **Performance**: Python 3.14 includes continued performance improvements from 3.11+
1. **Deprecations**: Check for any deprecated features that may be removed in 3.14

### Testing Strategy

- **Early Testing**: Consider testing with Python 3.14 alpha/beta releases before official release
- **CI/CD**: GitHub Actions supports Python 3.14 via setup-python@v6
- **Local Testing**: May require pyenv or manual installation until 3.14 is widely available

### Breaking Changes

This change should be **non-breaking**:

- Existing Python 3.10-3.13 users are unaffected
- Python 3.14 is added as a **new** supported version
- No features are removed or changed
- No APIs are modified

### Performance Impact

- **None**: Adding Python 3.14 support has no performance impact on existing versions
- **Benefit**: Python 3.14 users may see performance improvements from latest interpreter optimizations

### Security Considerations

- **Security Updates**: Python 3.14 will receive security updates until 2030
- **Vulnerability Fixes**: Staying current with Python versions ensures access to latest security fixes
- **Best Practice**: Supporting latest Python versions is a security best practice

## Implementation Notes

*To be filled during implementation:*

- Actual approach taken
- Challenges encountered
- Deviations from plan
- Actual effort vs estimated
- Python 3.14 availability at time of implementation
- Any dependency issues discovered
- CI/CD configuration adjustments needed
