# List GitHub Pull Requests

______________________________________________________________________

## title: 'List GitHub Pull Requests' read_only: true type: 'command'

List and filter GitHub pull requests from the current repository.

## Process

1. Determine filters based on user request:

   - State: `open`, `closed`, `merged`, or `all` (default: `open`)
   - Labels: specific labels to filter by (optional)
   - Limit: number of PRs to display (default: 20)
   - Author: filter by PR author (optional)
   - Draft status: include or exclude draft PRs

1. Execute the appropriate gh command:

   - Use `gh pr list` as the base command
   - Add `--state <state>` to filter by state
   - Add `--label <label>` to filter by labels
   - Add `--limit <number>` to control result count
   - Add `--author <user>` to filter by author
   - Add `--draft` or `--no-draft` for draft status
   - Use `--json` for structured data when needed

1. Present results to user:

   - Show PR number, title, author, and state
   - Highlight CI status (passing, failing, pending)
   - Show review status (approved, changes requested, pending)
   - Indicate draft status if applicable
   - Display branch names and merge status

1. Suggest next actions:

   - Review PRs needing attention
   - Merge approved PRs
   - Address failing CI checks
   - Request reviews for unreviewed PRs

## Examples

```bash
# List open PRs
gh pr list --state open --limit 20

# List merged PRs
gh pr list --state merged --limit 10

# List PRs by author
gh pr list --author "@me" --state all

# List ready-to-merge PRs (JSON)
gh pr list --json number,title,state,reviewDecision,statusCheckRollup

# List draft PRs
gh pr list --draft
```
