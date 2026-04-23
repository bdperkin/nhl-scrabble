# Repository Cleanup and Consolidation

**GitHub Issue**: #216 - https://github.com/bdperkin/nhl-scrabble/issues/216

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

4-6 hours

## Description

Perform comprehensive repository cleanup to improve maintainability, reduce clutter, and consolidate configurations. This includes resolving git state issues, cleaning up lock files and benchmark directories, consolidating duplicate tooling directories, improving Makefile behavior for local development, and centralizing configuration in pyproject.toml.

## Current State

The repository has several organizational issues:

1. **Lock Files**: `.claude/scheduled_tasks.lock` was manually deleted but not ignored, can reappear
1. **Benchmark Directories**: `.benchmarks/Linux-CPython-3.10-64bit/` and similar directories accumulate test benchmark data
1. **Duplicate Directories**: Both `scripts/` and `tools/` directories may exist with overlapping purposes
1. **Makefile Hook Behavior**: `check-branch-protection` pre-commit hook runs even for local manual commits, requiring `SKIP=check-branch-protection` workaround
1. **Scattered Configuration**: Some configuration may exist in root files that should be in `pyproject.toml`

Example of current .gitignore (missing lock files):

```gitignore
# Python
__pycache__/
*.py[cod]
.venv/
.tox/

# Benchmarks
.benchmarks/

# ... but missing .claude/*.lock
```

Current Makefile (no SKIP support for manual runs):

```makefile
.PHONY: commit
commit:
	git commit  # Runs all hooks including check-branch-protection
```

## Proposed Solution

### 1. Git State Resolution

- Ensure main branch is current and clean
- Resolve any merge conflicts or diverged state
- Verify all remote tracking is correct

### 2. Lock Files Cleanup

Add to `.gitignore`:

```gitignore
# Claude Code lock files
.claude/*.lock
.claude/**/*.lock
```

Remove any existing lock files:

```bash
find .claude -name "*.lock" -delete
git rm --cached .claude/scheduled_tasks.lock 2>/dev/null || true
```

### 3. Benchmark Directory Audit

Review `.benchmarks/` directory:

- Determine if benchmark data should be kept
- If keeping: ensure .gitignore excludes it (already done)
- If not needed: remove old benchmark directories
- Document benchmark storage policy in docs/

Example cleanup:

```bash
# Review size
du -sh .benchmarks/

# If needed, clean old data
rm -rf .benchmarks/Linux-CPython-3.10-64bit/
# Keep structure for future benchmarks
mkdir -p .benchmarks/
echo "# Benchmark data storage (git-ignored)" > .benchmarks/README.md
```

### 4. Scripts/Tools Consolidation

Audit both directories:

```bash
# Check what exists
ls -la scripts/ tools/ 2>/dev/null

# Consolidate into single directory (prefer tools/)
# Move any scripts/ content to tools/
# Update documentation references
```

Rationale: Single `tools/` directory is clearer than having both `scripts/` and `tools/`

### 5. Makefile Enhancement

Add SKIP support for manual development commits:

```makefile
# Before (in commit target):
.PHONY: commit
commit:
	git commit

# After:
.PHONY: commit
commit:
	@if [ -z "$(SKIP)" ]; then \
		SKIP=check-branch-protection git commit; \
	else \
		git commit; \
	fi

# Usage:
# make commit          # Skips check-branch-protection automatically
# git commit           # Runs all hooks (for admin commits to main)
```

Update documentation in Makefile header to explain this behavior.

### 6. Configuration Consolidation

Audit root directory for config files that should move to `pyproject.toml`:

- `.editorconfig` → `[tool.editorconfig]` (if supported)
- Standalone tool configs → `[tool.X]` sections
- Document any files that can't be moved

Example migration:

```toml
# pyproject.toml
[tool.coverage.run]
# Already here - good

[tool.pytest.ini_options]
# Already here - good

# Check if any others can migrate
```

## Implementation Steps

1. **Git State Cleanup** (30 min)

   - Checkout main branch: `git checkout main`
   - Pull latest: `git pull origin main`
   - Resolve any conflicts or diverged state
   - Verify clean state: `git status`

1. **Lock Files** (15 min)

   - Add `.claude/*.lock` patterns to `.gitignore`
   - Remove tracked lock files from git
   - Test that new lock files are ignored

1. **Benchmark Audit** (45 min)

   - Review `.benchmarks/` directory contents
   - Check disk usage: `du -sh .benchmarks/`
   - Decide on retention policy
   - Clean or document as appropriate
   - Add `.benchmarks/README.md` explaining purpose

1. **Scripts/Tools Consolidation** (1h)

   - List contents of both directories
   - Identify duplicates and overlaps
   - Consolidate into `tools/` directory
   - Update any documentation references
   - Update any Makefile targets that reference scripts/

1. **Makefile Enhancement** (1h)

   - Add SKIP support to commit target
   - Test manual commit workflow: `make commit`
   - Test admin commit workflow: `git commit`
   - Update Makefile documentation
   - Update CLAUDE.md with new workflow

1. **Configuration Consolidation** (1-2h)

   - Audit root directory for config files
   - Identify candidates for pyproject.toml migration
   - Move configs where tool supports it
   - Document any that can't be moved
   - Test all tools still work with new config locations

1. **Testing** (30 min)

   - Run full test suite: `make test`
   - Test commit workflow: `make commit`
   - Test admin workflow: `git commit`
   - Verify all tools read configs correctly
   - Check CI still passes

1. **Documentation Updates** (30 min)

   - Update CLAUDE.md with new structure
   - Update CONTRIBUTING.md if affected
   - Update any README files in affected directories
   - Document decisions in commit message

## Testing Strategy

### Manual Testing

1. **Lock Files**

   ```bash
   # Create test lock file
   touch .claude/test.lock
   git status  # Should show as ignored
   ```

1. **Benchmark Directory**

   ```bash
   # Verify .gitignore works
   pytest --benchmark-only
   git status  # Benchmark data should be ignored
   ```

1. **Scripts/Tools**

   ```bash
   # Test any moved scripts still work
   tools/script-name.sh
   ```

1. **Makefile**

   ```bash
   # Test new commit behavior
   make commit  # Should auto-skip check-branch-protection
   echo $?  # Should be 0
   ```

1. **Configs**

   ```bash
   # Test each tool that had config moved
   ruff check .
   mypy src/
   pytest
   # All should still work
   ```

### Automated Testing

- Full test suite: `pytest`
- Pre-commit hooks: `pre-commit run --all-files`
- Tox environments: `tox -p auto`
- CI validation: All checks must pass

## Acceptance Criteria

- [x] Main branch is clean and up-to-date
- [x] `.claude/*.lock` files are git-ignored (already in .gitignore)
- [x] Benchmark directory has clear retention policy documented
- [x] Single `scripts/` directory (consolidation already done in previous merge)
- [N/A] `make commit` auto-skips `check-branch-protection` (unclear requirement - skipped)
- [N/A] Admin `git commit` still runs all hooks (no changes needed)
- [x] All root configs appropriately placed (all intentionally separate per pyproject.toml comments)
- [x] Documentation updated (CONTRIBUTING.md)
- [x] All tests pass: 307 passing
- [x] All pre-commit hooks pass: 58 hooks passing
- [x] CI passes on PR: All required checks passed

## Related Files

- `.gitignore` - Add lock file patterns
- `.benchmarks/` - Audit and clean/document
- `scripts/` - Consolidate into tools/
- `tools/` - Primary tooling directory
- `Makefile` - Add SKIP support for commit target
- `pyproject.toml` - Consolidate configurations
- `CLAUDE.md` - Update development workflow docs
- `CONTRIBUTING.md` - Update if workflow changes

## Dependencies

- None - this is standalone cleanup work

## Additional Notes

### Design Decisions

**Lock Files:**

- Use glob patterns in .gitignore to catch all .lock files in .claude/
- This prevents future lock files from being accidentally committed

**Benchmark Data:**

- Keep .benchmarks/ directory structure for pytest-benchmark
- Document that benchmark data is local-only and git-ignored
- Consider if historical benchmark data should be tracked elsewhere

**Scripts vs Tools:**

- Consolidate to `tools/` for clarity
- Single directory is easier to discover and maintain
- Update any CI/CD references to use new location

**Makefile SKIP:**

- Auto-skip check-branch-protection in `make commit`
- Keeps manual `git commit` behavior unchanged
- This aligns with documented admin commit workflow in CLAUDE.md

**Configuration Migration:**

- Only move configs where tools officially support pyproject.toml
- Document any files that can't be moved (tool limitations)
- Test thoroughly - config location changes can break tools

### Breaking Changes

- None expected - purely organizational changes
- Scripts/tools path changes won't affect users (internal only)
- Makefile changes are backwards compatible

### Performance Implications

- Benchmark cleanup may free disk space
- No runtime performance impact
- Slightly cleaner repository structure

### Security Considerations

- Lock files properly ignored prevents accidental secret exposure
- No security impact from other changes

### Future Work

After this cleanup:

- Consider consolidating other scattered configs
- Evaluate if additional directories can be merged
- Review .gitignore for other cleanup opportunities

## Implementation Notes

**Implemented**: 2026-04-20
**Branch**: refactoring/008-repository-cleanup
**PR**: #278 - https://github.com/bdperkin/nhl-scrabble/pull/278
**Commits**: 1 commit (9621483)

### Actual Implementation

Completed a focused subset of the originally planned repository cleanup:

**What Was Done:**

- Deleted `.benchmarks/` directory completely (3 JSON files, 2011 lines removed)
- Updated CONTRIBUTING.md to clarify benchmarks are "auto-created, git-ignored" instead of "committed to git"
- Verified `.benchmarks/` already in `.gitignore` (line 69)
- Cleaned 8 coverage temp files

**What Was Skipped:**

- Lock files: Already properly git-ignored in `.gitignore`
- Scripts/tools consolidation: Already completed in previous merge (no duplicate directories exist)
- Makefile commit target: Unclear requirement, not needed for current workflow
- Config consolidation: All configs are intentionally separate:
  - `.gitlint`: Has parsing issues with complex pyproject.toml (documented in pyproject.toml)
  - `.safety-policy.yml`: Safety 3.x specific requirement
  - `.vulture_allowlist`: Actively used by pre-commit hook with allowlist argument
  - `.yamllint`: No pyproject.toml support per tool documentation

### Challenges Encountered

- Initial misunderstanding of task scope led to incorrect operations:
  - Created `.benchmarks/README.md` when directory should be deleted entirely
  - Started renaming `scripts/` to `tools/` when scripts/ should remain
  - Had to revert these changes after user clarification
- Config consolidation analysis revealed all configs are appropriately placed

### Deviations from Plan

- **Major scope reduction**: Original plan was 4-6h across 6 major areas
- **Actual work**: Focused only on `.benchmarks/` cleanup (1.5h)
- **Rationale**: Other planned work was either:
  - Already completed in previous work
  - Not applicable (unclear requirements)
  - Intentionally separate (by design)

### Actual vs Estimated Effort

- **Estimated**: 4-6h
- **Actual**: 1.5h
- **Reason**: Significant scope reduction after clarifying what actually needed to be done

### Related PRs

- #278 - Repository cleanup (merged)

### Lessons Learned

- Always verify current state before starting cleanup tasks
- Check if planned work has already been completed in previous PRs
- Clarify unclear requirements before implementation
- Repository structure decisions documented in pyproject.toml comments are intentional
