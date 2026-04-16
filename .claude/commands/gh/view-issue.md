# View GitHub Issue

______________________________________________________________________

## title: 'View GitHub Issue' read_only: true type: 'command'

View detailed information about a specific GitHub issue.

## Process

1. Identify the issue:

   - Get issue number from user request
   - Validate issue number is valid
   - Check if viewing current repository issue or external

1. Fetch issue details:

   - Use `gh issue view <number>` for basic view
   - Add `--web` to open in browser if requested
   - Use `--json` for structured data when analyzing
   - Include comments with `--comments` flag

1. Present information:

   - Show issue title, number, and state
   - Display author and creation date
   - Show full description/body
   - List labels, assignees, milestone
   - Include comment count and recent comments
   - Show related PRs if linked

1. Suggest follow-up actions:

   - Close issue if resolved
   - Add comment if discussion needed
   - Assign or label if appropriate
   - Create PR to fix if applicable

## Examples

```bash
# View issue details
gh issue view 42

# View with comments
gh issue view 42 --comments

# Open in web browser
gh issue view 42 --web

# Get structured JSON data
gh issue view 42 --json title,body,state,labels,comments
```
