# Merge GitHub Pull Request

______________________________________________________________________

## title: 'Merge GitHub Pull Request' read_only: true type: 'command'

Merge an approved pull request into its base branch.

## Process

1. Verify PR is ready to merge:

   - Check PR is not a draft
   - Verify all required reviews are approved
   - Confirm all required CI checks are passing
   - Check for merge conflicts
   - Validate PR is still open

1. Determine merge strategy:

   - **Squash**: Combine all commits into one (default for most projects)
   - **Merge**: Keep all commits with a merge commit
   - **Rebase**: Rebase commits onto base branch
   - Consider project conventions and PR complexity

1. Prepare merge:

   - Review final changes one more time
   - Check if auto-delete branch is desired
   - Confirm base branch is correct

1. Execute merge:

   - Use `gh pr merge <number>` with chosen strategy
   - Add `--squash` for squash merge (default)
   - Add `--merge` for merge commit
   - Add `--rebase` for rebase merge
   - Add `--delete-branch` to remove after merge
   - Add `--auto` to enable auto-merge when checks pass

1. Verify merge success:

   - Confirm PR status changed to merged
   - Verify commits appear in base branch
   - Check if branch was deleted
   - Monitor CI on base branch
   - Close related issues if applicable

## Safety Checks

Before merging, always verify:

- ✅ Reviews approved by required reviewers
- ✅ All CI checks passing
- ✅ No merge conflicts
- ✅ Branch is up to date with base
- ✅ Not force-pushing to protected branch

## Examples

```bash
# Squash merge (default)
gh pr merge 42 --squash --delete-branch

# Regular merge with commit
gh pr merge 42 --merge --delete-branch

# Rebase merge
gh pr merge 42 --rebase --delete-branch

# Enable auto-merge (merges when checks pass)
gh pr merge 42 --auto --squash

# Merge with custom commit message
gh pr merge 42 --squash --subject "feat: add feature X"
```

## Merge Strategy Guidelines

**Use Squash when**:

- Multiple small commits refining a feature
- Want clean linear history
- Commits are not individually meaningful
- Most common choice

**Use Merge when**:

- Want to preserve detailed commit history
- Multiple authors on PR
- Commits are individually meaningful
- Creating release merges

**Use Rebase when**:

- Want linear history without merge commit
- All commits are clean and meaningful
- No merge conflicts
- Team prefers rebased workflow
