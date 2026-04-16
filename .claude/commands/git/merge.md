# Git Merge

______________________________________________________________________

## title: 'Git Merge Branches' read_only: true type: 'command'

Join two or more development histories together by integrating changes from another branch.

## Process

1. Prepare for merge:

   - Ensure working tree is clean
   - Identify branch to merge from
   - Checkout target branch (usually main)
   - Review changes to be merged
   - Verify tests pass on both branches

1. Execute merge:

   - Use `git merge <branch>` to merge
   - Use `git merge --no-ff` to create merge commit always
   - Use `git merge --ff-only` for fast-forward only
   - Use `git merge --squash` to squash commits

1. Handle conflicts if they occur:

   - Identify conflicted files
   - Resolve conflicts manually
   - Mark files as resolved with `git add`
   - Complete merge with `git commit`

1. Verify merge:

   - Run tests to ensure nothing broke
   - Review merge commit
   - Check branch history
   - Push merged changes

## Merge Strategies

**Fast-Forward** (default if possible):

- No merge commit created
- Linear history
- Only when target hasn't diverged

**No Fast-Forward** (`--no-ff`):

- Always creates merge commit
- Shows feature integration
- Better for feature branches

**Squash** (`--squash`):

- Combines all commits into one
- Creates new commit (not merge)
- Clean history but loses detail

## Examples

```bash
# Standard merge
git checkout main
git merge feature-branch

# Create merge commit always
git merge --no-ff feature-branch

# Fast-forward only (fail if diverged)
git merge --ff-only feature-branch

# Squash merge
git merge --squash feature-branch
git commit -m "Add feature X"

# Merge with commit message
git merge feature-branch -m "Merge feature X"

# Abort merge
git merge --abort

# Continue merge after conflicts
git add resolved-file.py
git commit

# Merge specific commit
git merge abc123
```

## Common Use Cases

**Merge feature to main:**

```bash
git checkout main           # Switch to main
git pull                    # Update main
git merge feature-branch    # Merge feature
git push                    # Push merged main
```

**Merge with no-ff (preserve branch history):**

```bash
git checkout main
git merge --no-ff feature-branch
# Creates merge commit showing feature integration
```

**Squash merge (clean history):**

```bash
git checkout main
git merge --squash feature-branch
git commit -m "feat: add complete feature X"
# All feature commits become one
```

**Merge and delete branch:**

```bash
git checkout main
git merge feature-branch
git branch -d feature-branch     # Delete local
git push origin --delete feature-branch  # Delete remote
```

**Merge after reviewing:**

```bash
git checkout main
git fetch origin
git diff main origin/feature-branch  # Review changes
git merge origin/feature-branch      # Merge if satisfied
```

## Handling Merge Conflicts

**When conflicts occur:**

```bash
git merge feature-branch
# CONFLICT: Merge conflict in file.py
# Auto-merging file.py
# Automatic merge failed; fix conflicts and then commit.

# 1. See conflicted files
git status

# 2. Open conflicted files, look for:
# <<<<<<< HEAD
# Your changes
# =======
# Their changes
# >>>>>>> feature-branch

# 3. Edit files to resolve conflicts

# 4. Mark as resolved
git add file.py

# 5. Complete merge
git commit  # Uses pre-filled merge message

# Or abort merge
git merge --abort
```

**Conflict markers:**

```python
def calculate_score(name):
<<<<<<< HEAD
    # Calculate based on all letters
    total = sum(SCRABBLE_VALUES.get(c, 0) for c in name.upper())
=======
    # Only count alphabetic characters
    total = sum(SCRABBLE_VALUES.get(c, 0) for c in name.upper() if c.isalpha())
>>>>>>> feature-branch
    return total
```

**Resolve by choosing:**

- Keep HEAD version (current branch)
- Keep incoming version (merging branch)
- Combine both changes
- Write completely new solution

## Merge Strategies (Advanced)

**Recursive** (default):

```bash
git merge -s recursive feature-branch
```

**Ours** (favor current branch):

```bash
git merge -X ours feature-branch
```

**Theirs** (favor incoming branch):

```bash
git merge -X theirs feature-branch
```

**Octopus** (multiple branches):

```bash
git merge branch1 branch2 branch3
```

## Before Merging

Checklist:

- ✅ Working tree is clean (`git status`)
- ✅ On correct target branch (`git branch`)
- ✅ Target branch is up to date (`git pull`)
- ✅ Source branch tests pass
- ✅ Reviewed changes to merge
- ✅ Coordinated with team if shared branch

## After Merging

Checklist:

- ✅ Run tests
- ✅ Verify application works
- ✅ Review merge commit
- ✅ Push to remote
- ✅ Delete merged branch if done
- ✅ Close related issues/PRs

## Fast-Forward vs No-FF

**Fast-Forward:**

```
Before:  A---B---C (main)
              \
               D---E (feature)

After:   A---B---C---D---E (main, feature)
```

No merge commit, linear history.

**No Fast-Forward:**

```
Before:  A---B---C (main)
              \
               D---E (feature)

After:   A---B---C-------F (main)
              \         /
               D---E---  (feature)
```

Merge commit F shows feature integration.

## Merge vs Rebase

**Use Merge when:**

- Working on shared branch
- Want to preserve complete history
- Multiple developers on branch
- Integrating feature branches

**Use Rebase when:**

- Working on personal branch
- Want linear history
- Cleaning up before merge
- Syncing feature with main

## Safety Considerations

Before merging:

- ✅ Commit or stash uncommitted changes
- ✅ Verify on correct branch
- ✅ Pull latest from remote
- ✅ Ensure tests pass
- ✅ Coordinate on shared branches
- ✅ Have backup branch for complex merges

**NEVER:**

- ❌ Force merge without resolving conflicts
- ❌ Merge without testing
- ❌ Merge to main without review (use PRs)
- ❌ Merge with failing tests

## Troubleshooting

**Merge aborted accidentally:**

```bash
# Reset to MERGE_HEAD
git merge --continue
# Or start over
git merge feature-branch
```

**Want to undo merge:**

```bash
# Before pushing
git reset --hard HEAD~1

# After pushing (creates new commit)
git revert -m 1 HEAD
```

**Merge commit message wrong:**

```bash
# Before pushing
git commit --amend

# After pushing
# Create new commit to fix
```

**Conflicts too complex:**

```bash
# Abort and try different approach
git merge --abort

# Try with strategy
git merge -X patience feature-branch

# Or rebase instead
git rebase feature-branch
```

## Best Practices

**1. Clean working tree:**

- Commit all changes first
- Stash if needed
- Verify with `git status`

**2. Use feature branches:**

- Merge features to main
- Keep main stable
- Delete after merging

**3. Test before merging:**

- Run test suite
- Verify manually
- Check CI passes

**4. Use pull requests:**

- Code review
- CI/CD checks
- Team visibility
- Better than direct merge

**5. Keep main clean:**

- Only merge complete features
- Ensure tests pass
- Use squash for messy history

## Advanced Options

```bash
--no-commit         # Merge but don't commit
--no-ff             # Create merge commit always
--ff-only           # Fast-forward only
--squash            # Squash commits
--strategy=<type>   # Merge strategy
-X <option>         # Strategy option (ours, theirs, patience)
--allow-unrelated-histories  # Merge unrelated projects
-m <msg>            # Merge commit message
--log               # Include commit messages in merge
```

## Tips

- Use `--no-ff` for feature branch merges
- Use `--ff-only` for safe merges
- Review changes before merging
- Test after merging
- Delete merged branches
- Use PRs for team visibility
- Keep merge commits descriptive
- Abort if conflicts are too complex
