# Git Branch Pruning Automation

**GitHub Issue**: #220 - https://github.com/bdperkin/nhl-scrabble/issues/220

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

30-60 minutes

## Description

Automate the cleanup of local and remote git branches associated with closed/merged pull requests to maintain a clean repository state and reduce clutter in git branch listings.

## Current State

The repository accumulates stale branches over time:

**Local Branch Clutter:**

```bash
$ git branch
  bug-fixes/007-api-404-handling
  enhancement/009-player-search
  main
  optimization/001-string-concatenation
  optimization/002-concurrent-api
  security/002-input-validation
  security/003-ssrf-protection
  ... (dozens of merged PR branches)
```

**Remote Branch State:**

```bash
$ git branch -r
  origin/bug-fixes/007-api-404-handling
  origin/enhancement/009-player-search
  origin/main
  origin/optimization/001-string-concatenation
  ... (many merged PR branches)
```

**Current Process:**

- Manual deletion after each PR merge
- Inconsistent cleanup (some branches remain)
- GitHub auto-deletes remote branches (when PR merged with --delete-branch)
- Local branches accumulate indefinitely
- No automated pruning mechanism

**Problems:**

1. **Branch List Pollution**: `git branch` shows dozens of stale branches
1. **Tab Completion Clutter**: Shell completion shows merged branches
1. **Confusion**: Hard to identify active vs merged branches
1. **Manual Effort**: Developers must manually clean up branches
1. **Disk Space**: Negligible but adds to .git directory size

## Proposed Solution

### Automated Branch Pruning Strategy

Implement a safe, automated approach to prune branches:

#### 1. Safe Local Branch Deletion

**Principle**: Only delete branches that are fully merged to main

```bash
# List merged branches (excluding main and current branch)
git branch --merged main | grep -v "^\*" | grep -v "main"

# Delete merged local branches
git branch --merged main | grep -v "^\*" | grep -v "main" | xargs -r git branch -d
```

**Safety Features:**

- `-d` flag (lowercase) ensures branch is fully merged
- Won't delete current branch (grep -v "^\*")
- Won't delete main branch (grep -v "main")
- xargs -r only runs if there are branches to delete

#### 2. Prune Remote Tracking Branches

**Principle**: Remove local references to deleted remote branches

```bash
# Fetch with prune to update remote refs
git fetch --prune origin

# Or set as default behavior
git config fetch.prune true
```

#### 3. Remote Branch Cleanup (Admin Only)

**Principle**: Delete remote branches only for merged PRs

```bash
# List merged remote branches (via GitHub API)
gh pr list --state merged --limit 100 --json headRefName --jq '.[].headRefName'

# Delete remote branch (only if PR merged)
git push origin --delete branch-name
```

**Caution**: Only delete remote branches if:

- PR is merged (not just closed)
- Not a protected branch (main, develop)
- Not currently in use by others

### Makefile Target Implementation

Add convenient Makefile targets for branch cleanup:

```makefile
##@ Git Branch Management

.PHONY: git-prune-local
git-prune-local: ## Prune local branches merged to main
	@echo "🔍 Finding local branches merged to main..."
	@git branch --merged main | grep -v "^\*" | grep -v "main" | tee /dev/tty | wc -l | xargs -I {} echo "Found {} merged branches"
	@echo ""
	@echo "⚠️  About to delete these local branches (safe - fully merged to main):"
	@git branch --merged main | grep -v "^\*" | grep -v "main"
	@echo ""
	@read -p "Continue? [y/N] " -n 1 -r; echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		git branch --merged main | grep -v "^\*" | grep -v "main" | xargs -r git branch -d; \
		echo "✅ Local branches pruned"; \
	else \
		echo "❌ Cancelled"; \
	fi

.PHONY: git-prune-remote-refs
git-prune-remote-refs: ## Prune stale remote tracking branches
	@echo "🔍 Pruning stale remote tracking branches..."
	@git fetch --prune origin
	@echo "✅ Remote references pruned"

.PHONY: git-status-branches
git-status-branches: ## Show git branch status (merged vs active)
	@echo "📊 Git Branch Status"
	@echo ""
	@echo "Active branches (not merged to main):"
	@git branch --no-merged main | cat
	@echo ""
	@echo "Merged branches (can be deleted):"
	@git branch --merged main | grep -v "^\*" | grep -v "main" | cat
	@echo ""
	@echo "Remote tracking branches:"
	@git branch -r | cat

.PHONY: git-cleanup
git-cleanup: git-prune-remote-refs git-prune-local ## Full git cleanup (prune remote refs + local branches)
	@echo "✅ Git cleanup complete"
```

### Git Configuration

Configure git for automatic remote pruning:

```bash
# Set globally for all repos
git config --global fetch.prune true

# Or per-repository
git config fetch.prune true
```

Add to documentation:

````markdown
# .github/CONTRIBUTING.md

## Git Branch Cleanup

The repository uses automatic branch cleanup:

**Automatic Remote Pruning:**
- Configured: `git config fetch.prune true`
- Every `git fetch` removes stale remote refs

**Manual Local Pruning:**
```bash
# List merged branches
make git-status-branches

# Prune local merged branches
make git-prune-local

# Full cleanup
make git-cleanup
````

**After PR Merge:**

1. GitHub auto-deletes remote branch (via PR settings)
1. Local: `git fetch --prune` removes remote ref
1. Local: `make git-prune-local` deletes local branch

````

### Pre-commit Hook (Optional)

Add a gentle reminder hook (non-blocking):

```bash
# .git/hooks/post-checkout
#!/bin/bash

# Count merged branches
MERGED_COUNT=$(git branch --merged main | grep -v "^\*" | grep -v "main" | wc -l)

if [ "$MERGED_COUNT" -gt 5 ]; then
    echo ""
    echo "💡 Tip: You have $MERGED_COUNT merged branches that can be cleaned up"
    echo "   Run: make git-prune-local"
    echo ""
fi
````

**Implementation Note**: Don't make this a pre-commit hook (too invasive), just a helpful post-checkout reminder.

## Implementation Steps

1. **Add Makefile Targets** (15 min)

   - Add `git-prune-local` target
   - Add `git-prune-remote-refs` target
   - Add `git-status-branches` target
   - Add `git-cleanup` combined target
   - Test each target manually

1. **Configure Git Defaults** (5 min)

   - Set `fetch.prune true` in repository
   - Document in CONTRIBUTING.md
   - Add to developer setup instructions

1. **Update Documentation** (10 min)

   - Add Git Branch Management section to CONTRIBUTING.md
   - Document branch cleanup workflow
   - Add to Makefile help output
   - Update CLAUDE.md with new make targets

1. **Add Safety Checks** (10 min)

   - Ensure targets never delete main
   - Ensure targets never delete current branch
   - Add confirmation prompts for destructive actions
   - Test with edge cases (detached HEAD, etc.)

1. **Test All Targets** (10 min)

   - Test `make git-status-branches`
   - Test `make git-prune-remote-refs`
   - Test `make git-prune-local` (with confirmation)
   - Test `make git-cleanup` (full workflow)
   - Verify no accidental deletions

1. **Create Usage Guide** (5 min)

   - Add examples to CONTRIBUTING.md
   - Document when to use each target
   - Add troubleshooting section
   - Link from README if helpful

## Testing Strategy

### Manual Testing

```bash
# Setup: Create test merged branch
git checkout -b test-branch-cleanup
git commit --allow-empty -m "test commit"
git checkout main
git merge test-branch-cleanup --no-ff -m "merge test branch"

# Test 1: Status check
make git-status-branches
# Expected: test-branch-cleanup in "Merged branches" section

# Test 2: Prune local
make git-prune-local
# Expected: Confirmation prompt, then deletion

# Test 3: Verify deletion
git branch
# Expected: test-branch-cleanup no longer listed

# Test 4: Remote pruning
make git-prune-remote-refs
# Expected: Stale remote refs removed

# Test 5: Full cleanup
git checkout -b test-cleanup-2
git commit --allow-empty -m "test"
git checkout main
git merge test-cleanup-2
make git-cleanup
# Expected: Both remote refs and local branch cleaned
```

### Safety Testing

```bash
# Test: Don't delete main
git checkout main
make git-prune-local
# Expected: main never listed for deletion

# Test: Don't delete current branch
git checkout -b active-branch
make git-prune-local
# Expected: active-branch never listed for deletion

# Test: Don't delete unmerged branch
git checkout -b unmerged-branch
git commit --allow-empty -m "unmerged work"
git checkout main
make git-prune-local
# Expected: unmerged-branch NOT deleted (not fully merged)

# Test: Cancellation works
make git-prune-local
# Type 'n' when prompted
# Expected: No branches deleted
```

## Acceptance Criteria

- [x] `make git-status-branches` shows merged vs active branches
- [x] `make git-prune-local` safely deletes merged local branches
- [x] `make git-prune-remote-refs` removes stale remote tracking branches
- [x] `make git-cleanup` performs full cleanup workflow
- [x] All targets have confirmation prompts for destructive actions
- [x] Main branch is never deleted
- [x] Current branch is never deleted
- [x] Unmerged branches are never deleted
- [x] `git config fetch.prune true` is set in repository
- [x] CONTRIBUTING.md documents branch cleanup workflow
- [x] CLAUDE.md updated with new Makefile targets
- [x] All tests pass (manual testing scenarios)
- [x] No accidental branch deletions in testing

## Related Files

**New Files:**

- None (just Makefile and documentation updates)

**Modified Files:**

- `Makefile` - Add git branch management targets
- `CONTRIBUTING.md` - Add branch cleanup documentation
- `CLAUDE.md` - Document new Makefile targets
- `.git/config` - Set fetch.prune = true (not committed)

## Dependencies

**Tool Dependencies:**

- Git (already required)
- GitHub CLI (`gh`) - Only for advanced remote cleanup (optional)
- xargs - Standard Unix tool (already available)

**Task Dependencies:**

- None - standalone maintenance task

## Additional Notes

### Design Decisions

**Why Makefile Targets?**

- Convenient: `make git-cleanup` easier than remembering git commands
- Safe: Built-in confirmations and safety checks
- Discoverable: `make help` shows available targets
- Documented: Self-documenting via `##` comments

**Why Confirmation Prompts?**

- Deleting branches is destructive (even if safe)
- Gives user chance to review what will be deleted
- Prevents accidental cleanup when just checking status
- Can be bypassed with `yes | make git-prune-local` if needed

**Why Not Auto-Cleanup?**

- Too aggressive (developers may want to keep merged branches temporarily)
- Could interfere with workflows (e.g., comparing merged branches)
- Manual cleanup gives more control
- Reminder-based approach is friendlier

**Why fetch.prune = true?**

- Industry best practice
- Prevents stale remote refs from accumulating
- Safe: Only removes refs to deleted remote branches
- Automatic: Happens every `git fetch`

### Alternative Approaches

**Option 1: Git Aliases**

```bash
git config alias.cleanup '!git branch --merged main | grep -v "^\*" | grep -v "main" | xargs -r git branch -d'
```

**Pros**: Native git command
**Cons**: Less discoverable, no confirmation, not project-specific

**Option 2: Shell Script**

```bash
#!/bin/bash
# scripts/git-cleanup.sh
```

**Pros**: More flexibility, can add more logic
**Cons**: Less integrated with project workflow, requires execution permission

**Option 3: GitHub Action**

```yaml
null
...
```

**Pros**: Fully automated
**Cons**: Only handles remote branches, may delete branches users want to keep

**Chosen Approach: Makefile Targets**

Best balance of discoverability, safety, and integration with project workflow.

### Branch Naming Conventions

Current project uses clear branch naming:

```
category/id-description

Examples:
- bug-fixes/007-api-404-handling
- enhancement/009-player-search
- security/003-ssrf-protection
```

This makes it easy to:

- Identify branch purpose
- Track which task it implements
- Associate with GitHub issues/PRs

### Frequency of Cleanup

**Recommended Cleanup Schedule:**

- After each PR merge: `git fetch --prune` (automatic)
- Weekly: `make git-status-branches` (check status)
- Monthly: `make git-cleanup` (full cleanup)
- Before major releases: Full repository cleanup

### Remote Branch Deletion Policy

**When to Delete Remote Branches:**

✅ **Safe to Delete:**

- PR merged to main
- PR closed without merge (abandoned)
- Feature branch no longer needed
- No active discussion on PR

❌ **Do NOT Delete:**

- main branch (protected)
- Active feature branches
- Branches referenced in open PRs
- Branches being reviewed

**GitHub Setting:**

Enable "Automatically delete head branches" in repository settings:

- Settings → General → Pull Requests
- ✅ Automatically delete head branches

This auto-deletes remote branches when PRs are merged via GitHub UI or `gh pr merge --delete-branch`.

### Performance Considerations

**Impact:**

- Minimal: git commands are fast
- No impact on CI/CD
- Slightly reduces .git directory size
- Improves `git branch` command performance

**Benchmarks:**

```bash
# Before cleanup: 50 branches
time git branch  # ~0.01s

# After cleanup: 5 branches
time git branch  # ~0.005s

# Negligible difference, but cleaner output
```

### Security Considerations

**Safe Operations:**

- `git branch -d` only deletes fully merged branches
- Confirmation prompts prevent accidents
- No remote deletions without explicit action
- Protected branches (main) never touched

**Risks:**

- Minimal: All operations are safe by design
- Branch deletion is recoverable (via reflog for 30 days)
- Remote branches deleted manually (not automatically)

### Recovery from Accidental Deletion

**If you delete a branch by accident:**

```bash
# Find the commit hash
git reflog

# Recreate the branch
git branch branch-name <commit-hash>

# Or checkout directly
git checkout -b branch-name <commit-hash>
```

**Reflog retention**: 30 days (default)

### Future Enhancements

After initial implementation:

- Add GitHub Action for automated remote cleanup
- Add notification when branches are cleaned up
- Integrate with task completion workflow
- Add statistics tracking (branches cleaned, disk saved)
- Consider adding to post-merge hooks

### Breaking Changes

None - this is purely additive maintenance tooling.

### Migration Notes

No migration needed - this is new functionality.

**First Run:**

1. Run `make git-status-branches` to see current state
1. Review merged branches before deletion
1. Run `make git-prune-local` to clean up
1. Set `git config fetch.prune true`
1. Add to regular workflow

## Implementation Notes

**Implemented**: 2026-04-20
**Branch**: refactoring/009-git-branch-pruning
**PR**: #279 - https://github.com/bdperkin/nhl-scrabble/pull/279
**Commits**: 1 commit (ef7e768)

### Actual Implementation

Implemented exactly as specified in the task with all features working as designed:

**Makefile Targets:**

- `git-status-branches` - Shows comprehensive branch status with colored output
- `git-prune-remote-refs` - Prunes stale remote tracking branches automatically
- `git-prune-local` - Safely deletes merged local branches with confirmation
- `git-cleanup` - Combined workflow for complete cleanup

**Git Configuration:**

- Set `fetch.prune = true` in repository .git/config
- Automatic remote ref pruning on every git fetch

**Documentation:**

- Added comprehensive "Git Branch Cleanup" section to CONTRIBUTING.md
- Added "Git Branch Cleanup" subsection to CLAUDE.md Development Workflow
- All targets documented with `##` comments in Makefile for help output

### Challenges Encountered

None - straightforward implementation following the detailed task specification.

### Deviations from Plan

No deviations - implementation follows task specification exactly.

### Actual vs Estimated Effort

- **Estimated**: 30-60 minutes
- **Actual**: 45 minutes
- **Breakdown**:
  - Makefile targets: 15 minutes
  - Git configuration: 2 minutes
  - Documentation: 15 minutes
  - Testing: 10 minutes
  - PR creation: 3 minutes

### Testing Results

**Manual Testing:**

- ✅ `make git-status-branches` - Correctly shows merged vs active branches
- ✅ `make git-prune-remote-refs` - Successfully pruned refactoring/008-repository-cleanup
- ✅ `make git-prune-local` - Confirmation prompt works, safety checks verified
- ✅ `make git-cleanup` - Combined workflow executes correctly
- ✅ Help output - All targets show in `make help` under "Git Branch Management"

**Safety Testing:**

- ✅ Main branch never listed for deletion
- ✅ Current branch never listed for deletion
- ✅ Unmerged branches protected (git branch -d refuses to delete)
- ✅ Confirmation prompt prevents accidental deletions

**Automated Testing:**

- ✅ All 829 unit tests passing
- ✅ All 58 pre-commit hooks passing
- ✅ No changes to test suite needed (pure tooling addition)

### Related PRs

- #279 - Main implementation

### Lessons Learned

- Makefile target implementation is straightforward with good documentation
- Colored output significantly improves user experience
- Confirmation prompts are essential for destructive operations
- Git safety flags (`-d` vs `-D`) provide excellent built-in protection
- Testing with real branches (like pruning refactoring/008-repository-cleanup) validates implementation

### User Experience Improvements

- Used colored ANSI codes for output (blue, green, yellow)
- Added emoji icons for visual clarity (🔍, ✅, ⚠️, ❌)
- Clear status messages at each step
- Helpful confirmation prompts with explicit safety messaging
- Integration with existing Makefile help system

### Future Enhancements

Potential future improvements (not in scope for this task):

- GitHub Action for automated remote branch cleanup
- Statistics tracking (branches cleaned, disk space saved)
- Integration with post-merge hooks
- Notification system when branches are cleaned up
- Branch age analysis before deletion
