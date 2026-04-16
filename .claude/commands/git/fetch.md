# Git Fetch

______________________________________________________________________

## title: 'Git Fetch Updates' read_only: true type: 'command'

Download objects and refs from remote repository without merging into working tree.

## Process

1. Determine what to fetch:

   - All remotes or specific remote
   - All branches or specific branch
   - Tags and references
   - Prune deleted remote branches

1. Execute fetch command:

   - Use `git fetch` for default remote
   - Use `git fetch <remote>` for specific remote
   - Use `git fetch --all` for all remotes
   - Use `git fetch --prune` to clean up deleted branches

1. Review fetched changes:

   - Use `git log HEAD..origin/main` to see new commits
   - Use `git diff origin/main` to see changes
   - Decide whether to merge, rebase, or leave
   - Check branch status with `git status`

1. Take action:

   - Merge fetched changes: `git merge origin/main`
   - Rebase on fetched changes: `git rebase origin/main`
   - Or just review for now

## Fetch vs Pull

**Fetch** (safe, review first):

- Downloads changes only
- Doesn't modify working tree
- Allows review before merging
- More control

**Pull** (fetch + merge):

- Downloads and merges
- Modifies working tree immediately
- Less control
- Convenient for simple updates

## Examples

```bash
# Fetch from default remote (origin)
git fetch

# Fetch from specific remote
git fetch origin
git fetch upstream

# Fetch specific branch
git fetch origin main

# Fetch all remotes
git fetch --all

# Fetch and prune deleted branches
git fetch --prune
git fetch -p  # Short form

# Fetch tags
git fetch --tags

# Fetch with verbose output
git fetch -v

# Dry run (see what would be fetched)
git fetch --dry-run

# Fetch depth (shallow)
git fetch --depth=1

# Fetch specific ref
git fetch origin refs/heads/main:refs/remotes/origin/main
```

## Common Use Cases

**Check for updates without merging:**

```bash
git fetch                  # Download updates
git status                 # See if behind
git log HEAD..origin/main  # See new commits
git diff origin/main       # See changes
# Decide to merge or not
```

**Update fork from upstream:**

```bash
git fetch upstream         # Fetch from upstream
git checkout main
git merge upstream/main    # Merge into local main
git push origin main       # Push to fork
```

**Review changes before pulling:**

```bash
git fetch origin           # Get updates
git log -p HEAD..origin/main  # Review commits
git diff origin/main       # See full diff
git merge origin/main      # Merge if satisfied
```

**Clean up deleted remote branches:**

```bash
git fetch --prune          # Remove stale references
git branch -vv             # See tracking status
# Delete corresponding local branches
git branch -d old-feature
```

**Check all remotes:**

```bash
git fetch --all            # Fetch from all remotes
git remote -v              # List remotes
git branch -r              # See all remote branches
```

## Review Fetched Changes

**See new commits:**

```bash
git log HEAD..origin/main           # List commits
git log --oneline HEAD..origin/main # Compact view
git log -p HEAD..origin/main        # With diffs
```

**See changes:**

```bash
git diff origin/main                # All changes
git diff --stat origin/main         # Summary
git diff HEAD origin/main -- file.py # Specific file
```

**Check what changed:**

```bash
git fetch
git status                          # Shows behind/ahead
git log --graph --all --oneline     # Visual graph
```

## After Fetching

**Option 1: Merge** (preserves history):

```bash
git fetch origin
git merge origin/main
```

**Option 2: Rebase** (linear history):

```bash
git fetch origin
git rebase origin/main
```

**Option 3: Fast-forward** (if no local commits):

```bash
git fetch origin
git merge --ff-only origin/main
```

**Option 4: Create new branch**:

```bash
git fetch origin
git checkout -b review-changes origin/main
```

## Prune Remote Branches

**Why prune:**

- Removes stale remote-tracking branches
- Cleans up deleted remote branches
- Keeps `git branch -r` output clean

**How to prune:**

```bash
# Fetch and prune
git fetch --prune
git fetch -p

# Only prune (no fetch)
git remote prune origin

# Auto-prune on fetch (set in config)
git config fetch.prune true
```

**See what would be pruned:**

```bash
git remote prune origin --dry-run
```

## Configuration

**Set fetch options:**

```bash
# Auto-prune on fetch
git config fetch.prune true

# Show verbose output
git config fetch.verbose true

# Set default remote
git config branch.main.remote origin
```

## Safety Considerations

Fetch is safe because:

- ✅ Doesn't modify working tree
- ✅ Doesn't change current branch
- ✅ Allows review before integrating
- ✅ Can't cause merge conflicts
- ✅ No risk of losing work

## Understanding Fetch Output

**Example output:**

```
remote: Counting objects: 10, done.
remote: Compressing objects: 100% (8/8), done.
remote: Total 10 (delta 2), reused 0 (delta 0)
Unpacking objects: 100% (10/10), done.
From github.com:user/repo
   abc123..def456  main       -> origin/main
 * [new branch]    feature-x  -> origin/feature-x
```

**What it means:**

- Downloaded 10 objects
- Updated origin/main reference
- New branch origin/feature-x

## Advanced Usage

**Fetch specific commits:**

```bash
git fetch origin <commit-hash>
```

**Fetch pull request:**

```bash
git fetch origin pull/42/head:pr-42
git checkout pr-42
```

**Fetch and merge in one step (pull):**

```bash
# These are equivalent:
git pull origin main
# =
git fetch origin main
git merge origin/main
```

**Fetch depth (shallow clone):**

```bash
git fetch --depth=10       # Last 10 commits
git fetch --shallow-since=2024-01-01
```

## Troubleshooting

**Fetch hangs:**

```bash
# Try verbose mode
git fetch -v

# Check network
ping github.com

# Try different protocol
git remote set-url origin git@github.com:user/repo.git
```

**Authentication fails:**

```bash
# Verify remote URL
git remote -v

# Update credentials
# For HTTPS:
git config --global credential.helper store

# For SSH:
ssh -T git@github.com
```

**Fetch brings too much:**

```bash
# Fetch specific branch only
git fetch origin main

# Use shallow fetch
git fetch --depth=1
```

## Best Practices

**1. Fetch regularly:**

- Stay aware of remote changes
- Catch conflicts early
- Plan integration strategy

**2. Review before merging:**

- Check what's coming
- Review commits and diffs
- Verify tests pass

**3. Keep clean:**

- Use `--prune` regularly
- Delete old local branches
- Sync tracking branches

**4. Use fetch when:**

- Want to review first
- Checking status
- Multiple remotes
- Learning what changed

## Tips

- Fetch is safe - use it liberally
- Review changes with `git log HEAD..origin/main`
- Use `--prune` to clean up deleted branches
- Set `fetch.prune true` in config
- Use `--all` to update all remotes
- Fetch before branching to get latest
- Use fetch to check status before pull
