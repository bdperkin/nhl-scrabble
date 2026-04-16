# Git Reset

______________________________________________________________________

## title: 'Git Reset Changes' read_only: true type: 'command'

Reset current HEAD to specified state, with options for keeping or discarding changes.

## Process

1. Understand what to reset:

   - Last commit (HEAD~1)
   - Specific commit (hash)
   - Number of commits (HEAD~N)
   - Staging area only (files)
   - Working directory (DANGER)

1. Choose reset mode:

   - `--soft`: Keep changes staged
   - `--mixed` (default): Keep changes unstaged
   - `--hard`: Discard all changes (DANGEROUS)

1. Execute reset:

   - Use `git reset <commit>` for default (mixed)
   - Use `git reset --soft <commit>` to keep staged
   - Use `git reset --hard <commit>` to discard all
   - Use `git reset HEAD <file>` to unstage files

1. Verify and recover if needed:

   - Check status with `git status`
   - Review with `git log`
   - Recover with `git reflog` if needed

## Reset Modes

**Soft** (`--soft`):

- Moves HEAD only
- Keeps changes staged
- Preserves working directory
- Safe, reversible

**Mixed** (default):

- Moves HEAD
- Unstages changes
- Preserves working directory
- Safe, reversible

**Hard** (`--hard`):

- Moves HEAD
- Discards staged changes
- Discards working directory changes
- **DANGEROUS**, hard to reverse

## Examples

```bash
# Unstage file (most common)
git reset HEAD file.py
git reset file.py  # Same

# Unstage all files
git reset HEAD

# Undo last commit, keep changes staged
git reset --soft HEAD~1

# Undo last commit, keep changes unstaged
git reset HEAD~1
git reset --mixed HEAD~1  # Same

# Undo last commit, discard all changes (DANGEROUS)
git reset --hard HEAD~1

# Reset to specific commit
git reset abc123
git reset --hard abc123  # Discard changes

# Undo last 3 commits, keep changes
git reset HEAD~3

# Reset to match remote (DANGEROUS)
git fetch origin
git reset --hard origin/main
```

## Common Use Cases

**Unstage files:**

```bash
git add .                # Oops, staged too much
git reset HEAD file.py   # Unstage specific file
git reset HEAD           # Unstage everything
```

**Undo last commit (keep changes):**

```bash
git reset HEAD~1         # Undo commit, keep changes unstaged
# Or
git reset --soft HEAD~1  # Undo commit, keep changes staged
# Fix and recommit
```

**Start over from remote:**

```bash
git fetch origin
git reset --hard origin/main  # Match remote exactly
# ⚠️ Discards all local changes!
```

**Undo multiple commits:**

```bash
git reset --soft HEAD~3  # Undo 3 commits, keep changes
git status               # All changes now staged
git commit -m "message"  # Create single commit
```

**Fix wrong branch:**

```bash
# Committed to main instead of feature branch
git branch feature-branch   # Create branch at current commit
git reset --hard HEAD~1     # Remove commit from main
git checkout feature-branch # Switch to feature branch
```

## Reset vs Other Commands

**Reset vs Revert:**

- Reset: Rewrites history (dangerous for shared branches)
- Revert: Creates new commit (safe for shared branches)

**Reset vs Checkout:**

- Reset: Moves branch pointer
- Checkout: Moves HEAD only (or restores files)

**Reset vs Restore:**

- Reset: Moves HEAD/branch
- Restore: Restores files (modern, safer)

## Understanding Reset

**HEAD Notation:**

- `HEAD` - Current commit
- `HEAD~1` - One commit back
- `HEAD~2` - Two commits back
- `HEAD~3` - Three commits back
- `abc123` - Specific commit hash

**What Gets Reset:**

```
--soft:   HEAD → moves, Index → same,     Working → same
--mixed:  HEAD → moves, Index → changed,  Working → same
--hard:   HEAD → moves, Index → changed,  Working → changed
```

## Safety Considerations

**BEFORE using `--hard`:**

⚠️ **WARNING: `--hard` permanently deletes uncommitted work!**

- ✅ Verify working tree state
- ✅ Ensure changes are committed or backed up
- ✅ Double-check command before running
- ✅ Know how to recover from reflog
- ✅ Coordinate with team for shared branches

**Safer alternatives:**

```bash
# Instead of --hard, consider:
git stash              # Save changes first
git reset --mixed      # Keep changes unstaged
git restore .          # Modern alternative
```

## Recovering from Reset

**Find lost commits:**

```bash
git reflog             # See all HEAD movements
# Find the commit hash before reset
git reset --hard <hash>  # Restore to that point
```

**Example recovery:**

```bash
git reset --hard HEAD~3  # Oops! Lost 3 commits

git reflog
# abc123 HEAD@{0}: reset: moving to HEAD~3
# def456 HEAD@{1}: commit: Last commit
# ghi789 HEAD@{2}: commit: Second commit

git reset --hard def456  # Recover lost commits
```

## Reset Specific Files

**Unstage specific files:**

```bash
git reset HEAD file.py        # Unstage file
git reset HEAD src/*.py       # Unstage pattern
git reset HEAD src/           # Unstage directory
```

**Reset file to specific commit:**

```bash
git reset <commit> -- file.py  # Reset file only
# Note: This stages the change!
```

## Troubleshooting

**Accidentally reset --hard:**

```bash
# Find lost commit in reflog
git reflog
git reset --hard <hash-before-reset>
```

**Reset wrong branch:**

```bash
# Checkout correct branch first
git checkout feature-branch
# Then reset
git reset --hard origin/feature-branch
```

**Can't reset (conflicts):**

```bash
# Ensure working tree is clean
git stash
git reset <commit>
git stash pop  # If you want changes back
```

## Best Practices

**1. Use appropriate mode:**

- Unstaging files: `git reset HEAD file.py`
- Undo last commit: `git reset HEAD~1`
- Match remote: `git reset --hard origin/branch`

**2. Never reset public commits:**

- ❌ Don't reset pushed commits on shared branches
- ✅ Use `git revert` for public commits instead

**3. Create backup:**

```bash
git branch backup-before-reset
git reset --hard <commit>
# If problems: git reset --hard backup-before-reset
```

**4. Check reflog regularly:**

```bash
git reflog  # Know what's recoverable
```

**5. Use --soft for commit squashing:**

```bash
git reset --soft HEAD~3  # Combine 3 commits
git commit -m "Combined commit"
```

## Advanced Usage

**Reset keeping some changes:**

```bash
git reset HEAD~1         # Undo commit
git stash               # Stash some changes
git add specific-file.py # Stage what you want
git commit -m "message"
git stash pop           # Get other changes back
```

**Reset to remote but keep local changes:**

```bash
git fetch origin
git reset origin/main   # Reset branch
# Local changes still in working tree
```

**Interactive reset:**

```bash
# Use rebase for more control
git rebase -i HEAD~3
```

## Reset Options

```bash
--soft        # Keep changes staged
--mixed       # Keep changes unstaged (default)
--hard        # Discard all changes
--merge       # Safe reset with checks
--keep        # Reset but keep local changes
-p            # Interactive mode
```

## When to Use Reset

**Good uses:**

- Unstaging files
- Undoing local commits (not pushed)
- Combining commits
- Fixing wrong branch

**Bad uses:**

- Undoing pushed commits (use revert)
- Removing shared history
- On branches others use
- Without understanding consequences

## Alternatives to Consider

**Instead of reset --hard:**

```bash
git restore .           # Restore files
git checkout .          # Restore files (older)
git clean -fd           # Remove untracked
```

**Instead of reset for public commits:**

```bash
git revert <commit>     # Create inverse commit
```

**Instead of unstaging:**

```bash
git restore --staged file.py  # Modern way (Git 2.23+)
```

## Tips

- Use `git reset HEAD file.py` to unstage files
- Use `--soft` to combine commits
- Use `--mixed` (default) to undo commits but keep work
- **NEVER** use `--hard` without understanding consequences
- Always check `git reflog` if you lose commits
- Use `git revert` for public/shared branches
- Create backup branch before complex resets
- Double-check command before using `--hard`
