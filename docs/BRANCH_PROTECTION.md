# Branch Protection Guide

This document explains how to prevent accidental commits to the `main` branch and enforce PR-based workflows.

## Local Protections (Already Configured)

### 1. Pre-commit Hook

A pre-commit hook warns when committing directly to `main` or `master`:

**Location:** `.git-hooks/check-branch-protection.sh`
**Integration:** Added to `.pre-commit-config.yaml` as local hook

**Behavior:**

**In Local Development:**

- Warns when committing to protected branches
- Prompts for confirmation (Y/N)
- Provides instructions for proper workflow
- Can be bypassed with explicit confirmation

**In CI Environments:**

- Automatically detects CI environment
- Allows commits to main without prompting
- Logs informational message
- Enables CI to run on main branch after PR merges

**CI Detection:**

The hook automatically detects the following CI environments:

- GitHub Actions (`GITHUB_ACTIONS`)
- GitLab CI (`GITLAB_CI`)
- Travis CI (`TRAVIS`)
- CircleCI (`CIRCLECI`)
- Jenkins (`JENKINS_URL`)
- Generic CI (`CI`)

**Why CI Behavior Differs:**

In CI, commits to main are legitimate (result of PR merges via GitHub UI). The hook allows these commits to proceed without prompting since:

- PRs already passed all checks before merging
- CI has no interactive terminal for prompts
- Rejecting would break CI pipeline on main branch

**Test it:**

```bash
# Switch to main
git checkout main

# Try to commit
git commit --allow-empty -m "test"
# You'll see a warning and prompt
```

### 2. Git Configuration

Set up git to always require confirmation:

```bash
# Prevent accidental push to main
git config branch.main.pushRemote no_push

# Or globally for all repos
git config --global branch.main.pushRemote no_push
```

## GitHub Branch Protection Rules (Recommended)

Configure these settings on GitHub to enforce PR-based workflow:

### Step 1: Navigate to Settings

1. Go to your repository on GitHub
1. Click **Settings** → **Branches**
1. Click **Add rule** under "Branch protection rules"

### Step 2: Configure Protection

**Branch name pattern:** `main`

**Required Settings:**

- ✅ **Require a pull request before merging**

  - ✅ Require approvals: 1
  - ✅ Dismiss stale pull request approvals when new commits are pushed
  - ✅ Require review from Code Owners (if you have CODEOWNERS file)

- ✅ **Require status checks to pass before merging**

  - ✅ Require branches to be up to date before merging
  - ✅ Select required checks:
    - Pre-commit checks
    - Test on Python 3.12, 3.13, 3.14
    - Tox tests (all environments)

- ✅ **Require conversation resolution before merging**

- ✅ **Require linear history** (prevents merge commits)

- ✅ **Do not allow bypassing the above settings**

**Optional Settings:**

- ⚪ Require deployments to succeed before merging (if you have deployments)
- ⚪ Lock branch (prevents all pushes - very strict)
- ⚪ Restrict who can push to matching branches (for teams)

### Step 3: Save

Click **Create** or **Save changes**

## Workflow After Protection

### Correct Workflow

```bash
# 1. Ensure main is up to date
git checkout main
git pull origin main

# 2. Create feature branch
git checkout -b feature/my-feature

# 3. Make changes and commit
git add .
git commit -m "feat: add my feature"

# 4. Push feature branch
git push -u origin feature/my-feature

# 5. Create PR
gh pr create

# 6. Wait for CI and reviews

# 7. Merge via GitHub UI or CLI
gh pr merge --squash

# 8. Clean up
git checkout main
git pull origin main
git branch -d feature/my-feature
```

### If You Accidentally Commit to Main

If you already committed to main but haven't pushed:

```bash
# 1. Create feature branch from current state
git checkout -b feature/accidental-commits

# 2. Reset main to match origin
git checkout main
git reset --hard origin/main

# 3. Continue on feature branch
git checkout feature/accidental-commits

# 4. Push and create PR
git push -u origin feature/accidental-commits
gh pr create
```

### If You Accidentally Pushed to Main

If you already pushed to main (and branch protection isn't enabled):

```bash
# 1. Create feature branch
git checkout -b feature/fix-main

# 2. Push feature branch
git push -u origin feature/fix-main

# 3. Create PR
gh pr create

# 4. After PR is merged, force-push main back to previous state
# ⚠️ DANGEROUS - coordinate with team first!
git checkout main
git reset --hard origin/main~N  # N = number of commits to undo
git push --force origin main

# 5. Re-merge via the PR
gh pr merge feature/fix-main --squash
```

**Note:** This is complex and risky. Better to enable branch protection first!

## Testing Your Setup

### Test 1: Pre-commit Warning

```bash
git checkout main
echo "test" >> test.txt
git add test.txt
git commit -m "test commit on main"

# Expected: Warning and prompt
# Choose 'N' to abort
```

### Test 2: GitHub Branch Protection

```bash
# After configuring GitHub protection
git checkout main
echo "test" >> test.txt
git add test.txt
git commit -m "test commit on main" --no-verify
git push origin main

# Expected: GitHub rejects the push
# Error: Protected branch hook declined
```

### Test 3: PR Workflow

```bash
git checkout main
git pull origin main
git checkout -b feature/test-protection
echo "test" >> test.txt
git add test.txt
git commit -m "feat: test branch protection"
git push -u origin feature/test-protection
gh pr create --fill

# Expected: PR created successfully, CI runs
```

### Test 4: CI Environment Simulation

```bash
# Simulate GitHub Actions CI
export GITHUB_ACTIONS=true
git checkout main
echo "test" >> test.txt
git add test.txt
git commit -m "test: CI simulation"

# Expected: No prompt, commit succeeds with CI message
# Output: "ℹ️  CI environment detected: Allowing commit to 'main' branch"

# Clean up
unset GITHUB_ACTIONS
git reset HEAD~1
```

## Troubleshooting

### Pre-commit Hook Not Running

```bash
# Reinstall pre-commit hooks
pre-commit install

# Test hook
pre-commit run check-branch-protection --all-files

# Make script executable
chmod +x .git-hooks/check-branch-protection.sh
```

### Can't Push to Main (Branch Protection Active)

This is expected! Use the PR workflow:

```bash
# Don't fight the protection - use it!
git checkout -b feature/my-changes
git push -u origin feature/my-changes
gh pr create
```

### Need to Bypass Protection (Emergency)

**Pre-commit hook:**

```bash
git commit --no-verify -m "emergency fix"
```

**GitHub protection (requires admin):**

1. Temporarily disable branch protection
1. Make emergency push
1. Re-enable branch protection immediately
1. Create follow-up PR to document the emergency change

### CI Failing on Main Branch

**Problem:** Pre-commit hook fails in CI with exit code 1

**Solution:** This was fixed in PR #[TBD]. The hook now detects CI environments and skips the interactive prompt.

**Verify the fix:**

```bash
# Check hook has CI detection
grep -A 10 "is_ci()" .git-hooks/check-branch-protection.sh

# Should show function checking GITHUB_ACTIONS, CI, etc.
```

**If still failing:**

1. Verify the hook file is updated
1. Check CI environment variables are set
1. Review CI logs for the actual error
1. Ensure hook is executable: `chmod +x .git-hooks/check-branch-protection.sh`

## Best Practices

1. **Always work on feature branches**

   - Name: `feature/description`, `bugfix/issue-123`, `hotfix/critical`
   - Keep focused on single change
   - Delete after merge

1. **Keep main clean**

   - Only merge via PRs
   - Require CI to pass
   - Require code review
   - Use squash merge for clean history

1. **Use PR templates**

   - Document what changed
   - Link to issues
   - List testing done
   - Note breaking changes

1. **Automate everything**

   - CI runs all tests
   - Pre-commit enforces style
   - Branch protection enforces workflow
   - Merge automatically when ready

1. **Review your own PRs**

   - Check the diff before merging
   - Verify CI passed
   - Read your own code review
   - Think about edge cases

## Related Documentation

- Git Workflow
- [Contributing Guide](../CONTRIBUTING.md)
- [Pre-commit Hooks](../README.md#pre-commit-hooks)
- CI/CD Pipeline

## Summary

| Protection               | Enabled         | Enforced        | Bypassable        |
| ------------------------ | --------------- | --------------- | ----------------- |
| Pre-commit hook          | ✅ Yes          | ⚠️ Warning only | Yes (with prompt) |
| GitHub branch protection | ⚠️ Manual setup | ✅ Strict       | Admin only        |
| Git config               | ⚠️ Optional     | ⚠️ Warning only | Yes               |

**Recommendation:** Enable all three layers for maximum protection.
