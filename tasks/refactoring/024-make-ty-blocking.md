# Make 'ty' Blocking After Validation Period

**GitHub Issue**: #355 - https://github.com/bdperkin/nhl-scrabble/issues/355

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

30 minutes - 1 hour

## Description

Transition Astral's 'ty' type checker from validation/informational mode to blocking mode after sufficient validation period. Currently ty runs alongside mypy but doesn't fail builds when it finds issues. After confirming ty works reliably, it should be made blocking to enforce type safety.

## Current State

The 'ty' type checker is currently configured as non-blocking in three places:

**1. Pre-commit Hook** (`.pre-commit-config.yaml`):
```yaml
- id: ty
  name: ty - Astral type checker (validation mode - non-blocking)
  entry: bash -c 'ty check src || true'
  language: system
  types: [python]
  pass_filenames: false
  verbose: true
  # Non-blocking during validation period
  # Will show errors but not prevent commits
  # After validation, remove '|| true' to make blocking
```

**2. CI Workflow** (`.github/workflows/ci.yml`):
```yaml
- name: Run ty (Astral type checker - validation mode)
  run: ty check src
  continue-on-error: true
  # Non-blocking during validation period
  # Compare results with mypy before making blocking
```

**3. Tox Environment** (`tox.ini`):
```ini
[testenv:ty]
description = Run type checking (Astral ty - fast Rust-based checker)
extras = type
commands_pre = ty --version
commands = ty check src {posargs}
labels = type, quality
```

The tox environment is already blocking (no special handling), but pre-commit and CI are non-blocking.

## Proposed Solution

After a validation period (suggested: 2-4 weeks or 10-20 PRs), make ty blocking:

**1. Update Pre-commit Hook**:
```yaml
- id: ty
  name: ty - Astral type checker
  entry: ty check src
  language: system
  types: [python]
  pass_filenames: false
  verbose: true
  # Blocking: ty errors will prevent commits
```

**2. Update CI Workflow**:
```yaml
- name: Run ty (Astral type checker)
  run: ty check src
  # Blocking: ty errors will fail CI builds
```

**3. Update Documentation**:
- Update CLAUDE.md to reflect ty as a blocking check
- Update pre-commit hook comments
- Update CI workflow comments

## Implementation Steps

1. **Validation Assessment**:
   - Review recent PRs to see how many ty warnings/errors occurred
   - Compare ty results with mypy results for accuracy
   - Identify any false positives or configuration issues
   - Ensure ty version is stable (not alpha/beta)

2. **Configuration Updates**:
   - Remove `|| true` from pre-commit hook entry
   - Remove `continue-on-error: true` from CI workflow
   - Update hook name from "validation mode - non-blocking" to blocking
   - Update comments to reflect blocking status

3. **Documentation Updates**:
   - Update CLAUDE.md section on ty checker
   - Update pre-commit hook documentation
   - Add ty to list of blocking quality checks

4. **Communication**:
   - Document the change in PR description
   - Note that ty is now blocking in commit messages
   - Update contributing guidelines if necessary

## Testing Strategy

**Pre-deployment Testing**:
1. Temporarily make ty blocking in local environment
2. Run pre-commit hooks on all files: `pre-commit run ty --all-files`
3. Verify ty fails appropriately on type errors
4. Verify ty passes on clean codebase
5. Test that commit is blocked when ty finds errors

**Post-deployment Monitoring**:
1. Monitor first 5 PRs for ty-related failures
2. Track false positives and configuration issues
3. Be ready to revert to validation mode if issues arise
4. Adjust ty configuration if needed (via pyproject.toml)

## Acceptance Criteria

- [ ] ty validation period complete (2-4 weeks or 10-20 PRs)
- [ ] No consistent false positives identified
- [ ] Pre-commit hook blocks commits on ty errors
- [ ] CI workflow fails builds on ty errors
- [ ] Documentation updated to reflect blocking status
- [ ] CLAUDE.md updated
- [ ] Contributing guidelines updated (if applicable)
- [ ] All tests pass

## Related Files

- `.pre-commit-config.yaml` - Pre-commit hook configuration for ty
- `.github/workflows/ci.yml` - CI workflow with ty check
- `tox.ini` - Tox environment for ty (already blocking)
- `pyproject.toml` - ty configuration (if needed)
- `CLAUDE.md` - Project documentation
- `CONTRIBUTING.md` - Contributing guidelines (if applicable)

## Dependencies

**Prerequisite**:
- Validation period must be complete
- ty should have proven reliable and accurate
- No major false positive issues

**No blocking dependencies** on other tasks

## Additional Notes

**Validation Period Guidelines**:
- **Minimum**: 2 weeks or 10 PRs with ty enabled
- **Ideal**: 4 weeks or 20 PRs with ty enabled
- **Criteria**: < 5% false positive rate
- **Comparison**: ty results should align with mypy ~90%+

**Reversion Plan**:
If ty causes problems after making blocking:
1. Revert pre-commit hook to validation mode (`|| true`)
2. Revert CI workflow to non-blocking (`continue-on-error: true`)
3. Create issue to investigate ty configuration
4. Schedule another validation period after fixes

**Performance Considerations**:
- ty is 10-100x faster than mypy
- Should not significantly impact pre-commit or CI times
- Monitor CI build times before/after transition

**Configuration Options**:
If ty needs adjustment, configure via `pyproject.toml`:
```toml
[tool.ty]
# Configuration options if needed
# Docs: https://docs.astral.sh/ty/configuration/
```

**Benefits of Making Blocking**:
1. **Faster type checking**: ty is 10-100x faster than mypy
2. **Dual validation**: Both mypy and ty catch type errors
3. **Catch-all safety net**: Harder for type errors to slip through
4. **Modern tooling**: Uses latest Rust-based technology

**Trade-offs**:
1. **Additional CI step**: One more thing that can fail builds
2. **Potential false positives**: ty may have different interpretation than mypy
3. **Maintenance overhead**: Need to keep both ty and mypy configurations in sync

## Implementation Notes

*To be filled during implementation*
