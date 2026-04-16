# Git Checkout

______________________________________________________________________

## title: 'Git Checkout Branches/Files' read_only: true type: 'command'

Switch branches or restore working tree files (older command, see also `git switch` and `git restore`).

## Process

1. Determine checkout operation:

   - Switch to existing branch
   - Create and switch to new branch
   - Checkout specific commit (detached HEAD)
   - Restore files to previous state
   - Checkout specific file from commit

1. Execute appropriate command:

   - Use `git checkout <branch>` to switch branches
   - Use `git checkout -b <branch>` to create and switch
   - Use `git checkout <commit>` for specific commit
   - Use `git checkout -- <file>` to restore files

1. Verify operation:

   - Check current branch with `git status`
   - Verify files restored correctly
   - Ensure no uncommitted changes lost

## Modern Alternatives

**Git 2.23+ introduced:**

- `git switch` - For switching branches
- `git restore` - For restoring files

**These are clearer and recommended for new work:**

```bash
# Old way (checkout)
git checkout main
git checkout -b feature
git checkout -- file.py

# New way (switch/restore)
git switch main
git switch -c feature
git restore file.py
```

## Checkout Operations

**Switch branches:**

```bash
git checkout main
git checkout feature-branch
```

**Create and switch:**

```bash
git checkout -b new-feature
git checkout -b new-feature main  # From specific branch
```

**Detached HEAD (commit/tag):**

```bash
git checkout abc123        # Specific commit
git checkout v1.0.0        # Tag
git checkout HEAD~3        # 3 commits back
```

**Restore files:**

```bash
git checkout -- file.py            # Restore one file
git checkout -- .                  # Restore all files
git checkout -- src/               # Restore directory
git checkout HEAD -- file.py       # From specific commit
git checkout main -- file.py       # From specific branch
```

## Examples

```bash
# Switch to existing branch
git checkout main
git checkout feature-branch

# Create new branch and switch
git checkout -b new-feature
git checkout -b hotfix main  # From main

# Create from specific commit
git checkout -b recovery abc123

# Checkout remote branch
git checkout -b feature origin/feature
git checkout --track origin/feature  # Shorter

# Discard changes to file
git checkout -- file.py

# Restore file from specific commit
git checkout abc123 -- file.py

# Discard all changes
git checkout -- .

# Checkout specific commit (detached HEAD)
git checkout abc123

# Checkout tag
git checkout v1.0.0

# Previous branch
git checkout -

# Force checkout (discard changes)
git checkout -f branch-name
```

## Common Use Cases

**Switch branches:**

```bash
git checkout main          # Switch to main
git status                 # Verify branch
```

**Create feature branch:**

```bash
git checkout main          # Start from main
git pull                   # Update
git checkout -b feature-x  # Create feature branch
```

**Discard local changes:**

```bash
git status                 # See modified files
git checkout -- file.py    # Discard changes to file
git checkout -- .          # Discard all changes
```

**Get file from another branch:**

```bash
git checkout main -- config.py
# Copies config.py from main to current branch
```

**Checkout remote branch:**

```bash
git fetch origin
git checkout -b feature origin/feature
# Or
git checkout --track origin/feature
```

**Return to previous branch:**

```bash
git checkout feature-a
git checkout main
git checkout -            # Back to feature-a
```

## Detached HEAD State

**What is it:**

- HEAD points to commit, not branch
- Changes won't belong to any branch
- Warning when checking out commits/tags

**Example:**

```bash
git checkout abc123
# Warning: You are in 'detached HEAD' state
```

**Working in detached HEAD:**

```bash
git checkout abc123       # Enter detached HEAD
# Make changes
git commit -m "fix"       # Commit (will be lost!)

# Save work by creating branch
git checkout -b saved-work
# Or
git branch saved-work abc123  # Save commit to branch
```

**Exit detached HEAD:**

```bash
git checkout main         # Return to branch
```

## Checkout with Conflicts

**Uncommitted changes:**

```bash
git checkout other-branch
# error: Your local changes would be overwritten

# Options:
# 1. Commit changes
git add .
git commit -m "WIP"
git checkout other-branch

# 2. Stash changes
git stash
git checkout other-branch
git stash pop

# 3. Force checkout (lose changes!)
git checkout -f other-branch
```

## Safety Considerations

**Before checkout:**

- ✅ Commit or stash uncommitted changes
- ✅ Verify target branch exists
- ✅ Know that `--` discards changes permanently
- ✅ Use `git switch` for clarity (Git 2.23+)
- ✅ Create branch from detached HEAD if needed

**CAUTION:**

```bash
git checkout -- file.py   # ⚠️ Permanently discards changes
git checkout -f branch    # ⚠️ Force discards all changes
```

## Checkout Specific Files

**From HEAD:**

```bash
git checkout -- file.py            # Discard changes
git checkout HEAD -- file.py       # Explicit
```

**From specific commit:**

```bash
git checkout abc123 -- file.py     # Get version from commit
git checkout main -- file.py       # Get version from main
git checkout HEAD~3 -- file.py     # Get version from 3 commits ago
```

**From tag:**

```bash
git checkout v1.0.0 -- config.py   # Get config from v1.0.0
```

**Multiple files:**

```bash
git checkout main -- file1.py file2.py
git checkout abc123 -- src/*.py
```

## Checkout Options

```bash
-b <branch>         # Create new branch and checkout
-B <branch>         # Create/reset branch and checkout
-t, --track         # Set up tracking when creating branch
--orphan <branch>   # Create branch with no history
-f, --force         # Force checkout (discard changes)
-m, --merge         # Merge changes when switching
--conflict=<style>  # Conflict style (merge, diff3)
--detach            # Detach HEAD at current branch tip
-                   # Checkout previous branch
```

## Migration to Switch/Restore

**Old checkout:**

```bash
git checkout main                 # Switch branch
git checkout -b feature           # Create branch
git checkout -- file.py           # Restore file
```

**New commands (Git 2.23+):**

```bash
git switch main                   # Switch branch
git switch -c feature             # Create branch
git restore file.py               # Restore file
```

**Why split:**

- Clearer intent
- Safer (separate operations)
- Better error messages
- Recommended for new users

## Troubleshooting

**Can't switch branches:**

```bash
# Uncommitted changes blocking switch
git status                # See what's changed

# Option 1: Commit
git add .
git commit -m "WIP"

# Option 2: Stash
git stash
git checkout other-branch

# Option 3: Force (lose changes!)
git checkout -f other-branch
```

**Branch doesn't exist:**

```bash
git branch -a             # List all branches
git fetch                 # Update remote branches
git checkout --track origin/feature  # Checkout remote
```

**Detached HEAD accidentally:**

```bash
# Create branch to save work
git checkout -b saved-work

# Or just return to branch
git checkout main
```

**Lost commits in detached HEAD:**

```bash
git reflog                # Find commit
git checkout -b recover <hash>  # Save to branch
```

## Best Practices

**1. Use modern commands:**

```bash
# Prefer
git switch main
git restore file.py

# Over
git checkout main
git checkout -- file.py
```

**2. Commit before switching:**

```bash
git add .
git commit -m "WIP"
git checkout other-branch
```

**3. Use stash for quick switches:**

```bash
git stash
git checkout other-branch
# Do work
git checkout -
git stash pop
```

**4. Create branch from detached HEAD:**

```bash
# If you made commits in detached HEAD
git checkout -b saved-work
```

**5. Use descriptive branch names:**

```bash
git checkout -b feature/user-auth
git checkout -b fix/login-timeout
git checkout -b hotfix/security-patch
```

## Advanced Usage

**Checkout with merge:**

```bash
git checkout -m other-branch
# Tries to merge local changes
```

**Checkout orphan branch:**

```bash
git checkout --orphan gh-pages
# New branch with no history
```

**Checkout specific path from commit:**

```bash
git checkout abc123 -- src/
# Restore entire directory
```

## Tips

- Use `git switch` instead for branch switching (Git 2.23+)
- Use `git restore` instead for file restoration (Git 2.23+)
- Checkout creates detached HEAD for commits/tags
- Use `checkout -` to return to previous branch
- Always commit or stash before switching branches
- `checkout --` discards changes permanently
- Create branch when in detached HEAD to save work
- Use `--track` to set up remote tracking
- Force checkout (`-f`) discards all changes
