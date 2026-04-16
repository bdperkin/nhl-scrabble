# Git Rebase

______________________________________________________________________

## title: 'Git Rebase Branches' read_only: true type: 'command'

Reapply commits on top of another base branch, creating a linear history.

## Process

1. Prepare for rebase:

   - Ensure working tree is clean
   - Identify base branch to rebase onto
   - Review commits that will be replayed
   - Create backup branch if complex rebase
   - Coordinate with team if shared branch

1. Execute rebase:

   - Use `git rebase <base>` to rebase
   - Use `git rebase -i <base>` for interactive
   - Use `git pull --rebase` to sync with remote
   - Handle conflicts as they occur

1. Handle conflicts:

   - Resolve conflicts in affected files
   - Mark as resolved with `git add`
   - Continue with `git rebase --continue`
   - Or abort with `git rebase --abort`

1. Complete rebase:

   - Verify history looks correct
   - Run tests to ensure nothing broke
   - Force push if already pushed (use `--force-with-lease`)
   - Coordinate with team about force push

## Rebase vs Merge

**Rebase** (linear history):

- Replays commits on new base
- Rewrites commit hashes
- Clean linear history
- Better for feature branches

**Merge** (preserves history):

- Creates merge commit
- Preserves original hashes
- Shows parallel development
- Better for shared branches

## Examples

```bash
# Rebase current branch onto main
git checkout feature-branch
git rebase main

# Rebase with pull
git pull --rebase origin main

# Interactive rebase (edit commits)
git rebase -i HEAD~3

# Rebase onto specific commit
git rebase abc123

# Continue after conflicts
git add resolved-file.py
git rebase --continue

# Skip current commit
git rebase --skip

# Abort rebase
git rebase --abort

# Force push after rebase (use with caution)
git push --force-with-lease
```

## Interactive Rebase

**Start interactive rebase:**

```bash
git rebase -i HEAD~5  # Last 5 commits
git rebase -i main    # All commits since main
```

**Commands in editor:**

```
pick abc123 Add feature A
reword def456 Fix bug B
edit ghi789 Update docs
squash jkl012 Typo fix
fixup mno345 Another typo
drop pqr678 Remove debug
```

**Command meanings:**

- `pick` - Use commit as-is
- `reword` - Use commit but edit message
- `edit` - Use commit but stop to amend
- `squash` - Combine with previous, keep both messages
- `fixup` - Combine with previous, discard this message
- `drop` - Remove commit
- `exec` - Run shell command

## Common Use Cases

**Update feature branch with main:**

```bash
git checkout feature-branch
git fetch origin
git rebase origin/main
# Resolve conflicts if any
git push --force-with-lease
```

**Clean up commits before merge:**

```bash
git rebase -i main
# Squash, reorder, reword commits
git push --force-with-lease
```

**Pull with rebase:**

```bash
git pull --rebase
# Cleaner than merge commit
```

**Squash last N commits:**

```bash
git rebase -i HEAD~3
# Mark later commits as 'squash'
```

**Edit commit message:**

```bash
git rebase -i HEAD~1
# Change 'pick' to 'reword'
```

## Handling Conflicts

**When conflicts occur:**

```bash
git rebase main
# CONFLICT: Merge conflict in file.py
# Resolve all conflicts and mark as resolved with git add

# 1. See conflicted files
git status

# 2. Fix conflicts in files

# 3. Mark as resolved
git add file.py

# 4. Continue rebase
git rebase --continue

# If more conflicts, repeat 2-4
# Or abort entire rebase
git rebase --abort
```

**After each conflict:**

- Fix the conflict
- `git add` resolved files
- `git rebase --continue`
- Repeat until done

## Rebase Workflow

**Typical workflow:**

```bash
# 1. Update main
git checkout main
git pull

# 2. Rebase feature branch
git checkout feature-branch
git rebase main

# 3. Resolve conflicts (if any)
# Fix conflicts
git add .
git rebase --continue

# 4. Force push (if previously pushed)
git push --force-with-lease

# 5. Create/update PR
gh pr create
```

## Interactive Rebase Examples

**Squash last 3 commits:**

```bash
git rebase -i HEAD~3

# In editor:
pick abc123 First commit
squash def456 Second commit
squash ghi789 Third commit

# Save and exit
# Edit combined commit message
```

**Reorder commits:**

```bash
git rebase -i HEAD~4

# In editor, reorder lines:
pick ghi789 Third commit
pick abc123 First commit
pick def456 Second commit
pick jkl012 Fourth commit
```

**Split a commit:**

```bash
git rebase -i HEAD~1

# Change 'pick' to 'edit'
# After rebase stops:
git reset HEAD~1      # Unstage changes
git add file1.py      # Stage first part
git commit -m "Part 1"
git add file2.py      # Stage second part
git commit -m "Part 2"
git rebase --continue
```

## Safety Considerations

**NEVER rebase:**

- ❌ Commits that have been pushed to shared branches
- ❌ Commits that others are basing work on
- ❌ Public release commits
- ❌ Main/master branch (usually)

**Safe to rebase:**

- ✅ Personal feature branches
- ✅ Commits not yet pushed
- ✅ After coordinating with team
- ✅ Branches you own

**Before rebasing:**

- ✅ Create backup branch
- ✅ Ensure working tree is clean
- ✅ Coordinate with team
- ✅ Know how to abort

## After Rebasing

**Must force push:**

```bash
# ✅ SAFE: Checks remote hasn't changed
git push --force-with-lease

# ❌ DANGEROUS: Blindly overwrites
git push --force
```

**Verify rebase:**

```bash
git log --oneline --graph  # Check history
git diff origin/feature    # Check changes
```

**Run tests:**

```bash
# Ensure everything still works
make test
```

## Troubleshooting

**Rebase conflicts too complex:**

```bash
# Abort and try merge instead
git rebase --abort
git merge main
```

**Lost commits after rebase:**

```bash
# Find lost commits
git reflog
git log --walk-reflogs

# Recover
git reset --hard <hash>
```

**Force push rejected:**

```bash
# Someone pushed to your branch
git fetch
git reset --hard origin/feature-branch
git rebase main
git push --force-with-lease
```

**Accidentally rebased shared branch:**

```bash
# Reset to before rebase
git reset --hard origin/branch-name

# Or create new branch from backup
git checkout -b recovered backup-branch
```

## Best Practices

**1. Rebase frequently:**

- Keep feature branch in sync
- Smaller conflicts
- Easier resolution

**2. Interactive rebase before PR:**

- Clean up commit history
- Squash fixup commits
- Improve commit messages

**3. Never rebase shared branches:**

- Coordinate with team
- Use merge for public branches
- Only rebase personal work

**4. Create backup:**

```bash
git branch backup-feature
git rebase main
# If problems: git reset --hard backup-feature
```

**5. Use --force-with-lease:**

- Safer than --force
- Prevents overwriting others' work

## Advanced Options

```bash
-i, --interactive     # Interactive mode
--onto <newbase>      # Rebase onto different branch
--continue            # Continue after conflicts
--skip                # Skip current commit
--abort               # Abort rebase
--autosquash          # Auto-squash fixup! commits
--autostash           # Auto-stash/unstash
--committer-date-is-author-date  # Preserve dates
--preserve-merges     # Keep merge commits
-p                    # Preserve merges (legacy)
```

## Git Rebase Onto

**Rebase onto different base:**

```bash
# Move branch from old-base to new-base
git rebase --onto new-base old-base feature-branch

# Example: Move feature from develop to main
git rebase --onto main develop feature-branch
```

## Tips

- Use rebase for clean linear history
- Interactive rebase before merging
- Always use `--force-with-lease` not `--force`
- Create backup branch for complex rebases
- Abort if conflicts are too complex
- Rebase frequently to avoid large conflicts
- Coordinate with team before rebasing shared branches
- Use `git pull --rebase` for routine updates
