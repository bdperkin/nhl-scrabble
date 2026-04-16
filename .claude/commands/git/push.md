# Git Push

______________________________________________________________________

## title: 'Git Push Changes' read_only: true type: 'command'

Analyze local commits and update remote refs along with associated objects.

## Process

1. Analyze local state and remote relationship:

   - Use `git status` to check current branch and tracking information
   - Use `git log --oneline origin/<branch>..HEAD` to see commits that will be pushed
   - Use `git remote -v` to verify remote repository URLs
   - Check if current branch has an upstream branch set
   - Verify working tree is clean (no uncommitted changes)

1. Assess push requirements and provide recommendations:

   - Determine if this is a first-time push (needs `git push -u origin <branch>`)
   - Check for potential conflicts with `git fetch` and `git status`
   - Analyze commit history to recommend appropriate push strategy
   - Identify if force push might be needed (and warn about dangers)
   - Suggest branch protection considerations for main/master branch
   - Check if remote branch has new commits (needs pull first)

1. Execute push operation:

   - Use `git push` for standard pushes to tracked branches
   - Use `git push -u origin <branch>` to set upstream and push new branches
   - Use `git push origin <branch>` for explicit branch pushing
   - Consider `git push --force-with-lease` for safer force pushes when needed
   - NEVER use `git push --force` on main/master branches
   - Verify push success and provide confirmation of what was pushed

1. Handle push failures:

   - If rejected due to remote changes, fetch and rebase/merge first
   - If branch protection blocks push, check required status checks
   - If push is too large, investigate large files or history
   - Resolve conflicts before retrying push

## Safety Considerations

Before pushing, always verify:

- ✅ Commits are on correct branch
- ✅ No sensitive data in commits
- ✅ All tests pass
- ✅ Commit messages are clear
- ✅ Not force-pushing to protected branches
- ✅ Remote is correct (origin vs fork)

## Push Strategies

**Standard Push (Safe):**

- Pushes to tracked branch
- Fails if remote has new commits
- Recommended for most cases

**Push with Upstream (First Time):**

- Sets tracking branch and pushes
- Use for new branches
- Enables `git pull` and `git push` without arguments

**Force Push with Lease (Safer Force):**

- Force pushes but checks remote hasn't changed
- Use when you've rewritten local history
- Safer than `--force`

**Force Push (DANGEROUS):**

- Overwrites remote branch completely
- Can lose other people's work
- NEVER use on shared branches

## Examples

```bash
# Standard push (current branch)
git push

# First time push (set upstream)
git push -u origin feature-branch

# Push specific branch
git push origin feature-branch

# Push all branches
git push --all

# Push tags
git push --tags

# Push specific tag
git push origin v1.0.0

# Force push with safety (rewritten history)
git push --force-with-lease

# Delete remote branch
git push origin --delete old-branch

# Dry run (see what would be pushed)
git push --dry-run
```

## Common Use Cases

**First time pushing new branch:**

```bash
git checkout -b feature-new-feature
git add .
git commit -m "feat: add new feature"
git push -u origin feature-new-feature
```

**Regular push workflow:**

```bash
git status                    # Verify clean state
git log --oneline origin/main..HEAD  # See what will be pushed
git push                      # Push commits
```

**Push after rebase:**

```bash
git fetch origin
git rebase origin/main
# Resolve conflicts if any
git push --force-with-lease   # Safe force push
```

**Push rejected (remote has changes):**

```bash
git fetch origin
git status                    # See how far behind
git pull --rebase            # Rebase your commits
# Resolve conflicts if any
git push                     # Now push works
```

## IMPORTANT: Force Push Safety

⚠️ **NEVER force push to main/master or shared branches!**

**When force push is acceptable:**

- Your personal feature branch
- No one else is working on the branch
- You've coordinated with team
- After rebasing or amending commits

**Always use `--force-with-lease` instead of `--force`:**

```bash
# ✅ SAFE: Checks remote hasn't changed
git push --force-with-lease

# ❌ DANGEROUS: Blindly overwrites remote
git push --force
```

**Before force pushing:**

1. Confirm no one else is using the branch
1. Communicate with team
1. Use `--force-with-lease` not `--force`
1. Have a backup branch just in case

## Troubleshooting

**"rejected - non-fast-forward":**

```bash
# Remote has commits you don't have
git fetch origin
git pull --rebase origin/main
git push
```

**"rejected - protected branch":**

```bash
# Branch has protection rules
# Create pull request instead
gh pr create
```

**Push hanging/timeout:**

```bash
# Check network connection
# Check repository size
# Try SSH instead of HTTPS (or vice versa)
git remote set-url origin git@github.com:user/repo.git
```

**Wrong remote:**

```bash
# Check remotes
git remote -v

# Change remote URL
git remote set-url origin <correct-url>

# Or push to specific remote
git push upstream main
```
