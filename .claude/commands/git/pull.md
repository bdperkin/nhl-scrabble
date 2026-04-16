# Git Pull

______________________________________________________________________

## title: 'Git Pull Updates' read_only: true type: 'command'

Fetch from remote repository and integrate changes into current branch.

## Process

1. Verify current state:

   - Check current branch with `git status`
   - Verify working tree is clean
   - Identify tracking remote branch
   - Check for uncommitted changes

1. Determine pull strategy:

   - Default merge (creates merge commit)
   - Rebase (replays local commits)
   - Fast-forward only (no merge commit)
   - With specific options

1. Execute pull command:

   - Use `git pull` for default merge
   - Use `git pull --rebase` for linear history
   - Use `git pull --ff-only` for safe fast-forward
   - Handle merge conflicts if they occur

1. Verify and resolve:

   - Confirm pull succeeded
   - Resolve conflicts if any
   - Verify code still works after merge
   - Check branch status

## Pull Strategies

**Merge (Default):**

- Creates merge commit if diverged
- Preserves complete history
- Shows parallel development
- Safe for shared branches

**Rebase:**

- Replays local commits on top
- Creates linear history
- Cleaner commit history
- Rewrites commit hashes

**Fast-Forward:**

- Only pulls if no local commits
- No merge commit created
- Safest option
- Fails if diverged

## Examples

```bash
# Default pull (merge)
git pull

# Pull with rebase
git pull --rebase

# Fast-forward only (safe)
git pull --ff-only

# Pull specific branch
git pull origin main

# Pull from specific remote
git pull upstream main

# Pull and rebase with autostash
git pull --rebase --autostash

# Pull all branches
git pull --all

# Dry run (see what would be pulled)
git fetch
git log HEAD..origin/main
```

## Common Use Cases

**Update current branch:**

```bash
git status                 # Verify clean state
git pull                   # Pull updates
# Or with rebase for cleaner history:
git pull --rebase
```

**Pull with uncommitted changes:**

```bash
# Option 1: Stash first
git stash
git pull
git stash pop

# Option 2: Auto-stash with rebase
git pull --rebase --autostash
```

**Safe pull (fast-forward only):**

```bash
git pull --ff-only
# Fails if you have local commits
```

**Sync fork with upstream:**

```bash
git pull upstream main     # Pull from upstream
git push origin main       # Push to your fork
```

**Update feature branch from main:**

```bash
git checkout feature-branch
git pull origin main       # Pull main into feature
# Or better, rebase:
git pull --rebase origin main
```

## Pull vs Fetch

**Pull = Fetch + Merge:**

```bash
git pull origin main
# Equivalent to:
git fetch origin
git merge origin/main

# Or with rebase:
git pull --rebase origin main
# Equivalent to:
git fetch origin
git rebase origin/main
```

**When to use Fetch instead:**

- Want to review changes first
- Need to compare before merging
- Working on risky operation
- Want more control

## Handling Conflicts

When pull creates conflicts:

```bash
git pull
# CONFLICT: Merge conflict in file.py

# 1. View conflicted files
git status

# 2. Open and fix conflicts in files
# Look for markers: <<<<<<<, =======, >>>>>>>

# 3. Mark as resolved
git add fixed-file.py

# 4. Complete merge/rebase
git commit  # For merge
# Or
git rebase --continue  # For rebase

# If things go wrong:
git merge --abort     # Abort merge
git rebase --abort    # Abort rebase
```

## Configuration

**Set default pull strategy:**

```bash
# Use rebase by default
git config pull.rebase true

# Use merge by default (default)
git config pull.rebase false

# Fast-forward only
git config pull.ff only

# Per-repository:
git config --local pull.rebase true

# Globally:
git config --global pull.rebase true
```

## Safety Considerations

Before pulling:

- ✅ Commit or stash uncommitted changes
- ✅ Verify you're on correct branch
- ✅ Check you're pulling from correct remote
- ✅ Consider `--ff-only` for safety
- ✅ Be prepared to resolve conflicts
- ✅ Have clean working tree

## Troubleshooting

**"Your local changes would be overwritten":**

```bash
# Commit or stash changes first
git stash
git pull
git stash pop
```

**"Divergent branches" error:**

```bash
# Choose a strategy:
git pull --rebase       # Rebase (cleaner)
git pull --no-rebase    # Merge (safer)
git pull --ff-only      # Fail if diverged
```

**Pull hangs or fails:**

```bash
# Check network connection
# Try fetch first to diagnose
git fetch -v

# Check remote URL
git remote -v

# Try different protocol (HTTPS vs SSH)
```

**After pull, tests fail:**

```bash
# Reset to before pull
git reset --hard ORIG_HEAD

# Investigate what came in
git log HEAD..origin/main
git diff origin/main

# Pull again and fix issues
```

## Best Practices

**1. Pull frequently:**

- Reduces merge conflicts
- Keeps work integrated
- Easier conflict resolution

**2. Clean working tree:**

- Commit before pulling
- Or stash if needed
- Avoid pulling with changes

**3. Choose right strategy:**

- Merge for shared branches
- Rebase for clean history
- Fast-forward for safety

**4. After pull:**

- Run tests
- Verify application works
- Check for unexpected changes

## Advanced Options

**Pull options:**

```bash
--rebase               # Rebase instead of merge
--ff-only              # Fast-forward only
--no-ff                # Create merge commit always
--autostash            # Auto-stash/unstash
--all                  # Pull all remotes
-v, --verbose          # Show detailed output
--dry-run              # Show what would be done
--depth=<depth>        # Shallow pull
```

**Rebase options:**

```bash
git pull --rebase=interactive  # Interactive rebase
git pull --rebase=preserve     # Preserve merges
```

## Tips

- Use `git pull --rebase` for cleaner history
- Use `--autostash` to auto-handle uncommitted changes
- Use `--ff-only` when you want safety
- Set default strategy in config
- Run tests after pulling
- Pull frequently to avoid large merges
- Review what's coming with `git fetch` first
- Keep working tree clean before pulling
