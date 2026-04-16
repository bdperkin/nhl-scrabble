# Create GitHub Pull Request

______________________________________________________________________

## title: 'Create GitHub Pull Request' read_only: true type: 'command'

Create a new GitHub pull request from the current branch.

## Process

1. Analyze current git state:

   - Check current branch name
   - Verify branch has commits ahead of base
   - Check if branch is pushed to remote
   - Identify base branch (usually `main` or `develop`)

1. Gather PR information:

   - Title: clear, descriptive PR title
   - Body: detailed description with context
   - Base branch: target branch for merge
   - Draft status: whether PR should be draft
   - Reviewers: team members to review
   - Labels: appropriate classification

1. Generate comprehensive PR description:

   - Summary of changes
   - Motivation and context
   - Testing approach
   - Checklist of items addressed
   - Related issues (Closes #X, Fixes #Y)
   - Breaking changes if any
   - Screenshots/examples if UI changes

1. Create the pull request:

   - Push branch if not already pushed
   - Use `gh pr create` with appropriate flags
   - Add `--title "title"` for PR title
   - Add `--body "description"` for details
   - Add `--base branch` for target branch
   - Add `--draft` if work in progress
   - Add `--reviewer user1,user2` for reviewers
   - Add `--label label1,label2` for labels

1. Confirm creation and provide link:

   - Display the created PR number
   - Provide the GitHub URL
   - Show CI status when available
   - Suggest enabling auto-merge if applicable

## Examples

```bash
# Simple PR
gh pr create --title "Fix bug in login" --body "Fixes #42"

# With reviewers and labels
gh pr create \
  --title "Add feature X" \
  --body "$(cat <<'EOF'
## Summary
Implements feature X

## Test Plan
- [ ] Unit tests pass
- [ ] Integration tests pass
EOF
)" \
  --reviewer user1,user2 \
  --label enhancement

# Draft PR
gh pr create \
  --title "WIP: Refactor authentication" \
  --draft \
  --body "Work in progress..."

# PR to different base branch
gh pr create \
  --title "Release v2.0" \
  --base develop \
  --body "Release notes..."
```
