# Make 'gitlint' Blocking (Everywhere Except GitHub CI Workflows) After Validation Period

**GitHub Issue**: [#357](https://github.com/bdperkin/nhl-scrabble/issues/357)

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

30 minutes - 1 hour

## Description

Transition 'gitlint' commit message linter from experimental/validation mode in CI to blocking mode after sufficient validation period. Currently gitlint runs in CI but is marked as experimental (non-blocking). After confirming gitlint works reliably without false positives, it should be made blocking to enforce consistent commit message quality. However, automated commits from GitHub CI workflows (Dependabot, GitHub Actions bots) should be exempted.

## Current State

The 'gitlint' linter is currently configured in three places:

**1. Pre-commit Hook** (`.pre-commit-config.yaml`):
```yaml
- repo: https://github.com/jorisroovers/gitlint
  rev: v0.19.1
  hooks:
    - id: gitlint
      # Comprehensive commit message linting (matches ruff's ALL rules philosophy)
      # Enforces consistent commit message style and documentation
      # Config is in .gitlint file
      stages: [commit-msg]
```
**Status**: ✅ Already blocking locally (runs in `commit-msg` stage)

**2. CI Workflow** (`.github/workflows/ci.yml`):
```yaml
matrix:
  include:
    # ...
    - tox-env: gitlint
      experimental: true
      # Non-blocking during validation period

continue-on-error: ${{ matrix.experimental }}
```
**Status**: ⚠️ Non-blocking in CI (experimental mode)

**3. Tox Environment** (`tox.ini`):
```ini
[testenv:gitlint]
description = Lint commit messages with gitlint
skip_install = true
deps =
    gitlint
commands_pre =
    gitlint --version
commands =
    gitlint --commit {posargs:HEAD}
labels = quality
```
**Status**: ✅ Already blocking when run directly (tox -e gitlint)

**4. Gitlint Configuration** (`.gitlint`):
```ini
[general]
verbosity = 2
ignore-merge-commits = true
ignore-revert-commits = true
ignore-fixup-commits = true
ignore-fixup-amend-commits = true
ignore-squash-commits = true
ignore = B6

[title-max-length]
line-length = 100

[title-min-length]
min-length = 5

[body-max-line-length]
line-length = 100

[body-min-length]
min-length = 10
```
**Status**: ✅ Comprehensive configuration already in place

## Proposed Solution

After a validation period (suggested: 2-4 weeks or 10-20 PRs), make gitlint blocking in CI with exceptions for automated commits:

**1. Update CI Workflow**:
```yaml
matrix:
  include:
    # ...
    - tox-env: gitlint
      # Blocking: gitlint errors will fail CI builds
      # Automated commits (Dependabot, GitHub Actions) are ignored via .gitlint config
```

Remove `experimental: true` for gitlint, making it a required check.

**2. Update .gitlint Configuration** (add bot commit exemptions):
```ini
[general]
verbosity = 2
ignore-merge-commits = true
ignore-revert-commits = true
ignore-fixup-commits = true
ignore-fixup-amend-commits = true
ignore-squash-commits = true
ignore = B6

# Exempt automated commits from GitHub Actions workflows
# These often have non-standard commit message formats
# Examples: Dependabot, pre-commit.ci bot, GitHub Actions auto-commits
ignore-authors-regex = ^(dependabot\[bot\]|pre-commit-ci\[bot\]|github-actions\[bot\])

[title-max-length]
line-length = 100

[title-min-length]
min-length = 5

[body-max-line-length]
line-length = 100

[body-min-length]
min-length = 10
```

**3. Update Documentation**:
- Update CLAUDE.md to reflect gitlint as a blocking CI check
- Update CI workflow comments
- Document bot commit exemptions and rationale

## Implementation Steps

1. **Validation Assessment**:
   - Review recent PRs to see how many gitlint violations occurred
   - Categorize violations by type:
     - Title too long/short
     - Body too long/short
     - Missing body
     - Non-conventional commit format
   - Identify any false positives
   - Check if automated bot commits trigger violations
   - Ensure gitlint version is stable

2. **Configuration Updates**:
   - Remove `experimental: true` from gitlint in CI workflow matrix
   - Add `ignore-authors-regex` to .gitlint for bot commits
   - Test configuration with recent commits
   - Verify bot commits are properly exempted

3. **Documentation Updates**:
   - Update CLAUDE.md section on gitlint
   - Update CI workflow comments to reflect blocking status
   - Document which bot commits are exempted and why
   - Add commit message guidelines to CONTRIBUTING.md

4. **Communication**:
   - Document the change in PR description
   - Note that gitlint is now blocking in CI
   - Provide commit message format examples
   - Update contributing guidelines

## Testing Strategy

**Pre-deployment Testing**:
1. Test gitlint locally on recent commits:
   ```bash
   # Test on last 10 commits
   gitlint --commits "HEAD~10..HEAD"

   # Test on specific commit
   gitlint --commit HEAD
   ```

2. Verify bot commit exemption:
   ```bash
   # Check if Dependabot commits are ignored
   git log --author="dependabot[bot]" --oneline | head -5
   # Run gitlint on those commits to verify exemption
   ```

3. Temporarily make gitlint blocking in CI:
   - Create test PR with gitlint as required
   - Verify it fails on bad commit messages
   - Verify it passes on good commit messages
   - Verify bot commits don't trigger failures

**Post-deployment Monitoring**:
1. Monitor first 10 PRs for gitlint-related failures
2. Track false positives from bot commits
3. Be ready to add more bot patterns to exemption list
4. Adjust gitlint configuration if needed

## Acceptance Criteria

- [ ] gitlint validation period complete (2-4 weeks or 10-20 PRs)
- [ ] No consistent false positives identified
- [ ] Bot commit exemption tested and working
- [ ] CI workflow fails builds on commit message violations (non-bot commits)
- [ ] CI workflow passes for bot commits despite message format
- [ ] Documentation updated to reflect blocking status
- [ ] CLAUDE.md updated
- [ ] CONTRIBUTING.md updated with commit message guidelines
- [ ] All tests pass

## Related Files

- `.github/workflows/ci.yml` - CI workflow with gitlint check
- `tox.ini` - Tox environment for gitlint
- `.gitlint` - Gitlint configuration
- `.pre-commit-config.yaml` - Pre-commit hook (already blocking locally)
- `CLAUDE.md` - Project documentation
- `CONTRIBUTING.md` - Contributing guidelines with commit message format

## Dependencies

**Prerequisite**:
- Validation period must be complete
- gitlint should have proven reliable and accurate
- No major false positive issues
- Bot commit exemption patterns identified

**No blocking dependencies** on other tasks

**Related tasks**:
- Task 024 - Make 'ty' blocking (parallel validation approach)
- Task 025 - Make 'refurb' blocking (parallel validation approach)

## Additional Notes

**Validation Period Guidelines**:
- **Minimum**: 2 weeks or 10 PRs with gitlint enabled in CI
- **Ideal**: 4 weeks or 20 PRs with gitlint enabled in CI
- **Criteria**: < 5% false positive rate
- **Bot commits**: Should be automatically exempted

**Why Bot Commit Exemptions?**:
Automated commits from tools like Dependabot, pre-commit.ci, and GitHub Actions often have commit messages that don't follow conventional commit format:
- Dependabot: "Bump package from 1.0 to 2.0"
- pre-commit.ci: "[pre-commit.ci] auto fixes from pre-commit hooks"
- GitHub Actions: "Auto-merge PR #123"

These are system-generated and shouldn't block PRs, but human commits should still be validated.

**Reversion Plan**:
If gitlint causes problems after making blocking:
1. Re-add `experimental: true` to CI workflow
2. Add more patterns to `ignore-authors-regex` if needed
3. Create issue to investigate gitlint configuration
4. Schedule another validation period after fixes

**Performance Considerations**:
- gitlint is fast (Python-based, low overhead)
- Should not significantly impact CI times
- Runs only on commit messages (not full codebase)
- Monitor CI build times before/after transition

**Configuration Options**:
If gitlint needs adjustment, configure via `.gitlint`:
```ini
[general]
# Example: Relax body length requirement
[body-min-length]
min-length = 0  # Allow commits without body

# Example: Add custom rules
contrib = contrib-title-conventional-commits
```

**Common Gitlint Violations**:
1. **Title too long**: > 100 characters
2. **Title too short**: < 5 characters
3. **Body too long**: Lines > 100 characters
4. **Body too short**: < 10 characters total
5. **Missing body**: For non-trivial changes

**Good Commit Message Examples**:
```
✅ feat(api): Add caching to NHL API client

Implement request-level caching with 1-hour TTL to reduce API calls
and improve performance. Cache is stored in memory and cleared on
process restart.

✅ fix(cli): Validate output path before writing

Check that output directory exists and is writable before attempting
to write report files. Prevents cryptic IOError messages.

✅ docs: Update installation instructions

Add UV installation instructions and update Python version requirements
to reflect 3.12+ support.
```

**Bad Commit Message Examples**:
```
❌ "fix" - Title too short (< 5 characters)

❌ "Add support for multiple output formats including JSON, CSV, Excel, HTML, and XML with comprehensive formatting options" - Title too long (> 100 characters)

❌ "feat: Add feature" - Body missing (non-trivial change needs explanation)
```

**Bot Commit Patterns to Exempt**:
```ini
# Dependabot commits
^dependabot\[bot\]

# pre-commit.ci bot
^pre-commit-ci\[bot\]

# GitHub Actions bot
^github-actions\[bot\]

# Other common bots
^renovate\[bot\]
^allcontributors\[bot\]
^imgbot\[bot\]
```

**Benefits of Making Blocking**:
1. **Consistent history**: All commits follow same format
2. **Better changelogs**: Automated changelog generation works better
3. **Clear communication**: Commit messages explain WHY, not just WHAT
4. **Professional**: Shows project maturity and attention to detail
5. **Searchable**: Consistent format makes git log searching easier

**Trade-offs**:
1. **Learning curve**: Contributors need to learn commit message format
2. **Additional overhead**: Takes slightly longer to write good messages
3. **Bot exemptions**: Need to maintain list of bot patterns
4. **Potential friction**: May frustrate new contributors initially

## Implementation Notes

*To be filled during implementation*
