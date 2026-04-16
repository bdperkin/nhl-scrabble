# Git Stash

______________________________________________________________________

## title: 'Git Stash Changes' read_only: true type: 'command'

Temporarily store uncommitted changes to clean working directory without committing.

## Process

1. Determine stash operation:

   - Save current changes to stash
   - List existing stashes
   - Apply stashed changes
   - Remove stashes
   - Inspect stash contents

1. Execute appropriate stash command:

   - Use `git stash` or `git stash push` to save changes
   - Use `git stash list` to view stashes
   - Use `git stash apply` to restore changes
   - Use `git stash pop` to apply and remove
   - Use `git stash drop` to delete stash

1. Verify operation:

   - Confirm working tree is clean after stashing
   - Verify changes restored correctly
   - Check for merge conflicts when applying
   - Ensure correct stash selected

## Stash Operations

**Save Changes:**

- `git stash` - Stash tracked files
- `git stash -u` - Include untracked files
- `git stash -a` - Include ignored files
- `git stash push -m "message"` - With description

**List Stashes:**

- `git stash list` - Show all stashes
- `git stash show` - Show latest stash
- `git stash show -p` - Show with diff

**Apply Changes:**

- `git stash apply` - Apply latest stash (keep stash)
- `git stash apply stash@{0}` - Apply specific stash
- `git stash pop` - Apply and remove latest
- `git stash pop stash@{0}` - Apply and remove specific

**Manage Stashes:**

- `git stash drop` - Delete latest stash
- `git stash drop stash@{0}` - Delete specific stash
- `git stash clear` - Delete all stashes
- `git stash branch <name>` - Create branch from stash

## Examples

```bash
# Stash current changes
git stash

# Stash with message
git stash push -m "WIP: working on feature X"

# Stash including untracked files
git stash -u

# Stash including ignored files
git stash -a

# Stash specific files
git stash push -m "message" -- file1.py file2.py

# List all stashes
git stash list

# Show latest stash
git stash show
git stash show -p  # With diff

# Show specific stash
git stash show stash@{1}

# Apply latest stash (keep in list)
git stash apply

# Apply specific stash
git stash apply stash@{1}

# Apply and remove latest stash
git stash pop

# Delete latest stash
git stash drop

# Delete specific stash
git stash drop stash@{1}

# Delete all stashes
git stash clear

# Create branch from stash
git stash branch feature-from-stash
```

## Common Use Cases

**Switch branches with uncommitted work:**

```bash
git stash                   # Save current work
git checkout other-branch   # Switch branches
# Do work on other branch...
git checkout original-branch
git stash pop               # Restore work
```

**Quick experiment:**

```bash
git stash                   # Save current work
# Try experimental changes...
git reset --hard           # Discard experiment
git stash pop              # Restore original work
```

**Separate related changes:**

```bash
git stash -u               # Stash everything
git stash pop              # Restore
git add specific-files     # Stage related changes
git commit -m "message"    # Commit
# Remaining unstaged changes
```

**Pull with uncommitted changes:**

```bash
git stash                  # Save local changes
git pull                   # Pull updates
git stash pop              # Restore changes (may conflict)
```

## Understanding Stash List

**List output:**

```
stash@{0}: WIP on main: abc123 Update feature
stash@{1}: On feature-branch: def456 Work in progress
stash@{2}: WIP on main: ghi789 Bug fix attempt
```

- `stash@{0}` - Most recent stash (index 0)
- `stash@{1}` - Second most recent (index 1)
- Numbers increase with age

**Show output:**

```
 file1.py | 10 +++++++---
 file2.py |  5 +++++
 2 files changed, 12 insertions(+), 3 deletions(-)
```

Shows files and line changes in stash

## Stash vs Commit

**Use Stash when:**

- Quick context switch needed
- Changes not ready to commit
- Experimental work
- Temporary work parking
- Changes span multiple logical commits

**Use Commit when:**

- Work is complete or coherent
- Permanent record needed
- Sharing with others
- Creating backup before risky operation

## Handling Conflicts

When applying stash causes conflicts:

```bash
git stash pop
# CONFLICT: Merge conflict in file.py

# Fix conflicts in file.py
git add file.py            # Mark resolved
# Stash automatically removed on successful pop

# If conflicts on apply (not pop):
git stash apply
# Fix conflicts
git add fixed-files
# Manually drop stash if desired
git stash drop
```

## Advanced Operations

**Stash specific files:**

```bash
git stash push -m "message" -- src/file1.py src/file2.py
```

**Stash interactively:**

```bash
git stash -p  # Choose which hunks to stash
```

**Create branch from stash:**

```bash
git stash branch new-feature-branch stash@{0}
# Creates branch and applies stash
```

**Apply stash to different branch:**

```bash
git stash
git checkout other-branch
git stash apply  # Apply from previous branch
```

**Keep staged changes:**

```bash
git stash --keep-index  # Stash unstaged, keep staged
```

## Safety Considerations

Before using stash:

- ✅ Stash is temporary, not permanent backup
- ✅ Use meaningful messages for multiple stashes
- ✅ Don't let stashes accumulate indefinitely
- ✅ Review stash before popping (`git stash show`)
- ✅ Be prepared for conflicts when applying
- ✅ Consider committing instead for important work

## Troubleshooting

**Stash pop conflicts:**

```bash
# Fix conflicts manually
git add fixed-files
# Pop automatically completes
# Or if using apply, drop manually:
git stash drop
```

**Recover dropped stash:**

```bash
# Find stash hash in reflog
git fsck --unreachable | grep commit
git show <hash>  # Verify it's your stash
git stash apply <hash>  # Recover
```

**Clear old stashes:**

```bash
git stash list             # Review stashes
git stash clear            # Delete all
# Or delete specific ones:
git stash drop stash@{2}
```

## Tips

- Use descriptive messages with `git stash push -m "message"`
- Review stash before applying with `git stash show -p`
- Use `pop` to automatically remove after applying
- Don't accumulate many stashes - commit or discard
- Check `git stash list` regularly
- Use `git stash -u` to include untracked files
- Create branch from stash if work becomes significant
