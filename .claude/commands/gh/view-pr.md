# View GitHub Pull Request

______________________________________________________________________

## title: 'View GitHub Pull Request' read_only: true type: 'command'

View detailed information about a specific GitHub pull request.

## Process

1. Identify the pull request:

   - Get PR number from user request
   - Validate PR number is valid
   - Check if viewing current repository PR or external

1. Fetch comprehensive PR details:

   - Use `gh pr view <number>` for basic view
   - Add `--web` to open in browser if requested
   - Use `--json` for structured data analysis
   - Include comments with `--comments` flag

1. Analyze and present PR status:

   - Show PR title, number, and state
   - Display author, branch names, and creation date
   - Show full description/body
   - List labels, assignees, reviewers, milestone
   - Show review status (approved, changes requested, pending)
   - Display CI/CD check status (passing, failing, pending)
   - Show mergeable status and conflicts
   - Include comment count and recent discussions

1. Suggest follow-up actions based on status:

   - Request reviews if none pending
   - Address review comments if changes requested
   - Fix failing CI checks if any
   - Resolve merge conflicts if present
   - Merge if approved and passing
   - Mark as ready if draft and complete

## Examples

```bash
# View PR details
gh pr view 42

# View with comments
gh pr view 42 --comments

# Open in web browser
gh pr view 42 --web

# Get structured JSON for analysis
gh pr view 42 --json \
  number,title,state,isDraft,mergeable,\
  reviews,reviewDecision,statusCheckRollup,\
  commits,additions,deletions

# View PR diff
gh pr diff 42
```
