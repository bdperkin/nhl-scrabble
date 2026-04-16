# List GitHub Issues

______________________________________________________________________

## title: 'List GitHub Issues' read_only: true type: 'command'

List and filter GitHub issues from the current repository.

## Process

1. Determine filters based on user request:

   - State: `open`, `closed`, or `all` (default: `open`)
   - Labels: specific labels to filter by (optional)
   - Limit: number of issues to display (default: 20)
   - Assignee: filter by assigned user (optional)

1. Execute the appropriate gh command:

   - Use `gh issue list` as the base command
   - Add `--state <state>` to filter by state
   - Add `--label <label>` to filter by labels
   - Add `--limit <number>` to control result count
   - Add `--assignee <user>` to filter by assignee
   - Use `--json` for structured data when needed

1. Present results to user:

   - Show issue number, title, labels, and state
   - Highlight important information (labels, assignees)
   - Provide quick actions (view, close, comment)
   - Summarize total count and filters applied

## Examples

```bash
# List open issues
gh issue list --state open --limit 20

# List bugs
gh issue list --label bug --state all --limit 10

# List issues assigned to user
gh issue list --assignee @me --state open

# Get detailed JSON
gh issue list --state open --json number,title,labels,state
```
