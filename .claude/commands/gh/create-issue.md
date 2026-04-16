# Create GitHub Issue

______________________________________________________________________

## title: 'Create GitHub Issue' read_only: true type: 'command'

Create a new GitHub issue in the current repository.

## Process

1. Gather issue information:

   - Title: clear, concise issue title (required)
   - Body: detailed description of the issue (required)
   - Labels: appropriate labels (bug, enhancement, documentation, etc.)
   - Assignees: users to assign (optional)
   - Milestone: associated milestone (optional)

1. Validate information:

   - Ensure title is descriptive and specific
   - Check body includes necessary context
   - Verify labels exist in the repository
   - Confirm assignees are valid collaborators

1. Create the issue:

   - Use `gh issue create` with appropriate flags
   - Add `--title "title"` for the issue title
   - Add `--body "description"` for details
   - Add `--label label1,label2` for labels
   - Add `--assignee user1,user2` for assignees
   - Add `--milestone name` for milestone

1. Confirm creation and provide link:

   - Display the created issue number
   - Provide the GitHub URL
   - Show assigned labels and assignees
   - Suggest next actions (add to project, link PRs)

## Examples

```bash
# Simple issue
gh issue create --title "Fix typo in README" --body "Found typo on line 42"

# With labels and assignee
gh issue create \
  --title "Add feature X" \
  --body "Description..." \
  --label "enhancement,help wanted" \
  --assignee "@me"

# With milestone
gh issue create \
  --title "Bug in login" \
  --body "Steps to reproduce..." \
  --label "bug" \
  --milestone "v2.0"
```
