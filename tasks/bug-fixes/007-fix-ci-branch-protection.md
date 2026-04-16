# Fix Branch Protection Hook Failures in CI

**GitHub Issue**: #58 - https://github.com/bdperkin/nhl-scrabble/issues/58

## Priority

**HIGH** - Must Do (Next Sprint)

## Estimated Effort

1-2 hours

## Description

The branch protection pre-commit hook (`.git-hooks/check-branch-protection.sh`) fails in GitHub Actions CI when commits are pushed to the main branch. This blocks the CI/CD pipeline and prevents successful merges.

**Issue**: The hook prompts for user input when committing to protected branches (main/master), but CI environments cannot provide interactive input, causing the hook to fail with exit code 1.

**Impact**:

- CI fails on all commits to main branch
- Blocks PR merges (even though the PR itself passed all checks)
- Forces use of `--no-verify` to bypass hooks
- Defeats the purpose of having CI validation

## Current State

The current implementation in `.git-hooks/check-branch-protection.sh`:

```bash
#!/usr/bin/env bash
# Git hook to warn about committing directly to protected branches

set -e

BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || echo "")
PROTECTED_BRANCHES="^(main|master)$"

if [[ "$BRANCH" =~ $PROTECTED_BRANCHES ]]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⚠️  WARNING: You are committing directly to the '$BRANCH' branch!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    # ... warning message ...

    read -p "⚠️  Continue committing to '$BRANCH'? [y/N] " -n 1 -r  # FAILS IN CI
    echo ""

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Commit aborted."
        exit 1
    fi
fi

exit 0
```

**Problem**: The `read -p` command requires user input, which is not available in CI.

**Example Failure**: https://github.com/bdperkin/nhl-scrabble/actions/runs/24514400370/job/71654128092

```
Check Branch Protection..................................................Failed
- hook id: check-branch-protection
- exit code: 1

⚠️  WARNING: You are committing directly to the 'main' branch!
To proceed anyway: Continue below (not recommended)
To abort and create a feature branch: Press Ctrl+C

##[error]Process completed with exit code 1.
```

## Proposed Solution

Modify the branch protection hook to detect CI environments and skip the interactive prompt:

```bash
#!/usr/bin/env bash
# Git hook to warn about committing directly to protected branches

set -e

BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || echo "")
PROTECTED_BRANCHES="^(main|master)$"

# Check if running in CI environment
is_ci() {
    # GitHub Actions
    [[ -n "${GITHUB_ACTIONS}" ]] && return 0
    # GitLab CI
    [[ -n "${GITLAB_CI}" ]] && return 0
    # Travis CI
    [[ -n "${TRAVIS}" ]] && return 0
    # CircleCI
    [[ -n "${CIRCLECI}" ]] && return 0
    # Jenkins
    [[ -n "${JENKINS_URL}" ]] && return 0
    # Generic CI indicator
    [[ -n "${CI}" ]] && return 0

    return 1
}

if [[ "$BRANCH" =~ $PROTECTED_BRANCHES ]]; then
    # In CI: Allow the commit (it's already on main after PR merge)
    if is_ci; then
        echo "ℹ️  CI environment detected: Allowing commit to '$BRANCH' branch"
        exit 0
    fi

    # Local: Warn and prompt for confirmation
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⚠️  WARNING: You are committing directly to the '$BRANCH' branch!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "✅ Best practice workflow:"
    echo "   1. Create a feature branch:"
    echo "      git checkout -b feature/your-feature-name"
    echo ""
    echo "   2. Make your commits on the feature branch"
    echo ""
    echo "   3. Push and create a PR:"
    echo "      git push -u origin feature/your-feature-name"
    echo "      gh pr create"
    echo ""
    echo "   4. Merge via PR after CI passes"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "To proceed anyway: Continue below (not recommended)"
    echo "To abort and create a feature branch: Press Ctrl+C"
    echo ""
    read -p "⚠️  Continue committing to '$BRANCH'? [y/N] " -n 1 -r
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Commit aborted."
        echo ""
        echo "💡 Quick fix if you already made commits to main:"
        echo "   # Move commits to a feature branch"
        echo "   git checkout -b feature/your-feature-name"
        echo "   git checkout main"
        echo "   git reset --hard origin/main"
        echo "   git checkout feature/your-feature-name"
        echo ""
        exit 1
    fi

    echo "✅ Proceeding with commit to '$BRANCH' (you chose to bypass protection)..."
    echo ""
fi

exit 0
```

### Key Changes

1. **Added `is_ci()` function** that detects common CI environments:

   - GitHub Actions (`GITHUB_ACTIONS`)
   - GitLab CI (`GITLAB_CI`)
   - Travis CI (`TRAVIS`)
   - CircleCI (`CIRCLECI`)
   - Jenkins (`JENKINS_URL`)
   - Generic (`CI`)

1. **CI-specific behavior**: Skip interactive prompt and allow commits

   - Commits on main in CI are expected (result of PR merges)
   - Log informational message for transparency

1. **Preserve local behavior**: Interactive prompt still works for developers

## Implementation Steps

1. **Update hook script**

   - Add `is_ci()` function to `.git-hooks/check-branch-protection.sh`
   - Add CI detection before interactive prompt
   - Exit early with success if in CI environment

1. **Test locally**

   - Test that local commits to main still prompt for confirmation
   - Test that choosing "No" still aborts the commit
   - Test that choosing "Yes" allows the commit
   - Verify hook still works on feature branches (should pass silently)

1. **Test in CI**

   - Create test branch with the hook changes
   - Create PR and merge to main
   - Verify CI passes on main branch after merge
   - Check that pre-commit hook shows "CI environment detected" message

1. **Update documentation**

   - Update `docs/BRANCH_PROTECTION.md` to explain CI behavior
   - Add troubleshooting section for CI failures
   - Document the environment variables checked

## Testing Strategy

### Unit Testing (Manual)

1. **Test local main branch commit** (should prompt):

   ```bash
   git checkout main
   echo "test" >> test.txt
   git add test.txt
   git commit -m "test: local commit to main"
   # Expected: Prompt appears, can choose Y/N
   ```

1. **Test CI environment simulation** (should skip prompt):

   ```bash
   export GITHUB_ACTIONS=true
   git checkout main
   echo "test" >> test.txt
   git add test.txt
   git commit -m "test: simulated CI commit"
   # Expected: No prompt, commit succeeds with CI message
   unset GITHUB_ACTIONS
   ```

1. **Test feature branch** (should pass silently):

   ```bash
   git checkout -b test/feature
   echo "test" >> test.txt
   git add test.txt
   git commit -m "test: feature branch commit"
   # Expected: No prompt, commit succeeds immediately
   ```

### Integration Testing (CI)

1. **Create PR with fix**

   - Branch: `bug-fixes/007-fix-ci-branch-protection`
   - Changes: Updated `.git-hooks/check-branch-protection.sh`
   - Verify all PR checks pass

1. **Merge PR**

   - Merge via GitHub (squash merge)
   - Watch CI run on main branch
   - Verify pre-commit checks pass
   - Check logs show "CI environment detected" message

1. **Subsequent commits**

   - Make another simple change via PR
   - Merge to main
   - Verify CI continues to pass

## Acceptance Criteria

- [ ] Hook detects CI environment using standard environment variables
- [ ] Hook allows commits to main in CI without prompting
- [ ] Hook logs informational message when skipping prompt in CI
- [ ] Hook still prompts for confirmation when committing to main locally
- [ ] Hook allows bypass via "Y" response locally
- [ ] Hook aborts commit via "N" response locally
- [ ] Hook passes silently on feature branches (local and CI)
- [ ] CI passes on commits to main branch (no more exit code 1)
- [ ] Documentation updated with CI behavior explanation
- [ ] All tests pass

## Related Files

- `.git-hooks/check-branch-protection.sh` - Hook script to modify
- `.pre-commit-config.yaml` - Pre-commit configuration (no changes needed)
- `.github/workflows/ci.yml` - GitHub Actions CI workflow (no changes needed)
- `docs/BRANCH_PROTECTION.md` - Documentation to update

## Dependencies

None - This is a standalone fix to the hook script

## Additional Notes

### Why This Happens

The branch protection hook was designed for local development to prevent accidental commits to main. However, in CI:

1. PRs are merged via GitHub UI (not local git)
1. GitHub creates merge commits on main branch
1. CI runs pre-commit hooks on the merge commit
1. Hook detects main branch and prompts for input
1. CI has no interactive terminal, so prompt fails
1. CI fails with exit code 1

### Design Decision: Allow vs Reject in CI

**Decision**: Allow commits to main in CI (chosen approach)

**Rationale**:

- Commits on main in CI are legitimate (result of PR merges)
- PRs already passed all checks before merging
- Rejecting would prevent all CI runs on main
- Local protection is sufficient to prevent accidental direct commits

**Alternative considered**: Reject in CI and require `--no-verify`

- **Rejected because**: Defeats purpose of CI validation
- Would require modifying GitHub merge process
- Adds complexity without benefit

### CI Environment Detection

The hook checks multiple environment variables to ensure broad compatibility:

| Variable         | CI System      | Priority |
| ---------------- | -------------- | -------- |
| `GITHUB_ACTIONS` | GitHub Actions | Primary  |
| `GITLAB_CI`      | GitLab CI      | Common   |
| `TRAVIS`         | Travis CI      | Common   |
| `CIRCLECI`       | CircleCI       | Common   |
| `JENKINS_URL`    | Jenkins        | Common   |
| `CI`             | Generic        | Fallback |

This ensures the fix works across different CI platforms if the project moves in the future.

### Security Considerations

**Question**: Does this weaken branch protection?

**Answer**: No, because:

- GitHub branch protection rules still apply
- PRs still require reviews and passing checks
- Local commits to main still prompt for confirmation
- Only CI environment bypasses the prompt
- CI runs are triggered by legitimate merges, not arbitrary commits

### Future Enhancements

After fixing this issue, consider:

1. **GitHub branch protection rules**: Require PRs for main branch
1. **CODEOWNERS file**: Require specific reviewers
1. **Status checks**: Require all checks pass before merge
1. **Squash merge only**: Enforce in GitHub settings

## Implementation Notes

*To be filled during implementation:*

- Actual approach taken
- Challenges encountered
- Deviations from plan
- Actual effort vs estimated
- CI test results
- Any edge cases discovered
