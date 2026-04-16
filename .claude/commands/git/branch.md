# Git Branch

______________________________________________________________________

## title: 'Git Branch Management' read_only: true type: 'command'

List, create, rename, and delete branches for organizing development work.

## Process

1. Determine branch operation:

   - List branches (local, remote, or all)
   - Create new branch
   - Rename existing branch
   - Delete branch (local or remote)
   - View branch information

1. Execute appropriate command:

   - Use `git branch` to list local branches
   - Use `git branch <name>` to create branch
   - Use `git branch -m <new-name>` to rename
   - Use `git branch -d <name>` to delete
   - Use `git branch -a` to see all branches

1. Verify operation:

   - Confirm branch created/deleted/renamed
   - Check current branch with `git status`
   - Verify remote tracking if applicable
   - Ensure working tree is clean

## Branch Operations

**List Branches:**

- `git branch` - List local branches (\* = current)
- `git branch -r` - List remote branches
- `git branch -a` - List all branches (local + remote)
- `git branch -v` - List with last commit
- `git branch -vv` - List with tracking info

**Create Branch:**

- `git branch <name>` - Create branch (don't switch)
- `git checkout -b <name>` - Create and switch
- `git switch -c <name>` - Create and switch (newer)

**Rename Branch:**

- `git branch -m <new-name>` - Rename current branch
- `git branch -m <old> <new>` - Rename specific branch

**Delete Branch:**

- `git branch -d <name>` - Safe delete (merged only)
- `git branch -D <name>` - Force delete (unmerged OK)
- `git push origin --delete <name>` - Delete remote branch

## Examples

```bash
# List local branches
git branch

# List all branches
git branch -a

# List with commit info
git branch -v

# List with tracking info
git branch -vv

# Create new branch (stay on current)
git branch feature-new

# Create and switch to new branch
git checkout -b feature-new
git switch -c feature-new  # Modern alternative

# Create branch from specific commit
git branch feature-new abc123

# Rename current branch
git branch -m new-name

# Rename specific branch
git branch -m old-name new-name

# Delete local branch (safe)
git branch -d feature-old

# Delete local branch (force)
git branch -D feature-abandoned

# Delete remote branch
git push origin --delete feature-old

# View merged branches
git branch --merged

# View unmerged branches
git branch --no-merged

# Set upstream tracking
git branch -u origin/feature-branch
```

## Common Use Cases

**Start new feature:**

```bash
git checkout main           # Start from main
git pull                    # Get latest
git checkout -b feature-x   # Create feature branch
# Work on feature...
```

**List all branches:**

```bash
git branch -a               # See all branches
git branch -vv              # With tracking info
```

**Clean up old branches:**

```bash
git branch --merged         # See merged branches
git branch -d old-feature   # Delete merged branch
```

**Rename branch:**

```bash
git branch -m old-name new-name  # Rename
git push origin :old-name        # Delete old remote
git push -u origin new-name      # Push new remote
```

**Check branch status:**

```bash
git branch -vv              # See tracking status
git branch --merged main    # See what's merged to main
```

## Branch Naming Conventions

**Common Patterns:**

- `feature/description` - New features
- `fix/description` - Bug fixes
- `hotfix/description` - Urgent fixes
- `refactor/description` - Code refactoring
- `docs/description` - Documentation
- `test/description` - Test additions

**Examples:**

```bash
git checkout -b feature/user-authentication
git checkout -b fix/login-timeout
git checkout -b hotfix/security-patch
git checkout -b refactor/database-layer
```

## Understanding Branch Output

**List output:**

```
  feature-a
* main
  feature-b
  remotes/origin/main
  remotes/origin/feature-a
```

- `*` indicates current branch
- `remotes/` prefix shows remote branches

**Verbose output (`-v`):**

```
  feature-a  abc123 Add user auth
* main       def456 Update docs
  feature-b  ghi789 Refactor API
```

Shows last commit hash and message

**Tracking output (`-vv`):**

```
  feature-a  abc123 [origin/feature-a] Add user auth
* main       def456 [origin/main: ahead 2] Update docs
  feature-b  ghi789 Refactor API
```

Shows tracking branch and sync status

## Safety Considerations

Before deleting branches:

- ✅ Verify branch is fully merged
- ✅ Check if anyone else is using it
- ✅ Confirm you're deleting the right branch
- ✅ Use `-d` not `-D` unless certain
- ✅ Coordinate with team for shared branches

## Troubleshooting

**Can't delete current branch:**

```bash
# Switch to different branch first
git checkout main
git branch -d feature-old
```

**Delete fails (unmerged work):**

```bash
# Review what's unmerged
git log main..feature-branch

# Force delete if certain
git branch -D feature-branch
```

**Rename pushed branch:**

```bash
# 1. Rename local
git branch -m old-name new-name

# 2. Delete old remote
git push origin :old-name

# 3. Push new branch
git push -u origin new-name
```

**Branch not tracking remote:**

```bash
# Set upstream tracking
git branch -u origin/feature-branch

# Or push with -u
git push -u origin feature-branch
```

## Advanced Operations

**Copy branch:**

```bash
git branch new-branch existing-branch
```

**Create branch from tag:**

```bash
git branch hotfix-v1 v1.0.0
```

**List branches containing commit:**

```bash
git branch --contains abc123
```

**List branches merged to main:**

```bash
git branch --merged main
```

**Prune deleted remote branches:**

```bash
git fetch --prune
git remote prune origin
```

## Tips

- Use descriptive branch names
- Delete merged branches regularly
- Keep branch list clean
- Use `-vv` to check tracking status
- Coordinate deletions on shared branches
- Use branch prefixes for organization
- Check `--merged` before cleanup
