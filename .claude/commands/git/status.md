# Git Status

______________________________________________________________________

## title: 'Git Status Check' read_only: true type: 'command'

Show the working tree status, including staged, unstaged, and untracked changes.

## Process

1. Execute status command:

   - Use `git status` for human-readable output
   - Use `git status -s` for short format
   - Use `git status -b` to show branch information
   - Use `git status --porcelain` for script-friendly output

1. Analyze output:

   - Check current branch name
   - Identify staged changes (ready to commit)
   - Identify unstaged changes (modified but not staged)
   - Identify untracked files (new files not in git)
   - Check branch tracking status (ahead/behind remote)
   - Look for merge conflicts

1. Provide recommendations:

   - Suggest staging files if changes are ready
   - Recommend committing if staged changes exist
   - Suggest adding .gitignore for unwanted files
   - Warn about uncommitted changes before switching branches
   - Recommend pulling if branch is behind remote

## Status Output Guide

**File Status Indicators:**

- `??` - Untracked file (new file)
- `A` (space) - Staged new file
- `M` (space) - Staged modification
- (space)`M` - Unstaged modification
- `MM` - Staged and unstaged modifications
- `D` (space) - Staged deletion
- (space)`D` - Unstaged deletion
- `R` (space) - Renamed file
- `UU` - Merge conflict (both modified)

**Branch Status:**

- `up to date` - In sync with remote
- `ahead by N` - Local has N commits not on remote
- `behind by N` - Remote has N commits not local
- `diverged` - Both local and remote have unique commits

## Examples

```bash
# Standard status
git status

# Short format
git status -s

# With branch info
git status -sb

# Porcelain format (for scripts)
git status --porcelain

# Show ignored files
git status --ignored

# Show untracked files in detail
git status -u
```

## Common Use Cases

**Check before committing:**

```bash
git status              # See what's changed
git diff               # Review unstaged changes
git add file.py        # Stage changes
git status             # Verify staging
git commit -m "msg"    # Commit
```

**Check branch status:**

```bash
git status             # Shows branch ahead/behind
git fetch              # Update remote info
git status             # Check again
```

**Find untracked files:**

```bash
git status             # See ?? files
# Add to .gitignore or git add as needed
```

**Check for conflicts:**

```bash
git status             # Shows UU conflicts
# Fix conflicts in affected files
git add fixed_file.py  # Mark as resolved
git status             # Verify resolved
```

## Understanding Output

**Clean working tree:**

```
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

**Staged and unstaged changes:**

```
On branch feature-branch
Changes to be committed:
  modified:   src/module.py

Changes not staged for commit:
  modified:   tests/test_module.py

Untracked files:
  new_file.py
```

**Branch ahead of remote:**

```
On branch feature-branch
Your branch is ahead of 'origin/feature-branch' by 2 commits.
  (use "git push" to publish your local commits)
```

**Merge conflict:**

```
On branch main
You have unmerged paths.
  (fix conflicts and run "git commit")

Unmerged paths:
  (use "git add <file>..." to mark resolution)
    both modified:   src/config.py
```

## Tips

- Run `git status` frequently to understand current state
- Use `git status -s` for quick overview
- Check status before switching branches
- Always check status after merge/rebase
- Use status to verify staging before committing
