# Check Pull Request Status

______________________________________________________________________

## title: 'Check Pull Request Status' read_only: true type: 'command'

Check the comprehensive status of a pull request including CI checks, reviews, and merge readiness.

## Process

1. Fetch PR status information:

   - Use `gh pr view <number>` with JSON output
   - Get review status and decisions
   - Get CI/CD check status
   - Get mergeable status
   - Get conflict information

1. Analyze review status:

   - Count approved reviews
   - Identify reviewers requesting changes
   - List pending review requests
   - Check if minimum reviews met

1. Analyze CI/CD status:

   - List all status checks
   - Identify failing checks
   - Show pending/in-progress checks
   - Report successful checks
   - Highlight required checks

1. Assess merge readiness:

   - Check if mergeable (no conflicts)
   - Verify all checks passing
   - Confirm reviews approved
   - Identify blockers

1. Present comprehensive status report:

   - **PR State**: Open/Closed/Merged/Draft
   - **Reviews**: Approved/Changes Requested/Pending
   - **CI Checks**: Passing/Failing/Pending count
   - **Mergeable**: Yes/No with reasons
   - **Blockers**: List of issues preventing merge
   - **Next Steps**: Clear actions needed

## Examples

```bash
# Check basic PR status
gh pr view 42 --json \
  state,isDraft,mergeable,reviewDecision,statusCheckRollup \
  --jq '
    "State: \(.state)",
    "Draft: \(.isDraft)",
    "Mergeable: \(.mergeable)",
    "Reviews: \(.reviewDecision)",
    "Checks: \([.statusCheckRollup[].conclusion] | group_by(.) | map({(.[0]): length}) | add)"
  '

# Check detailed status
gh pr checks 42

# View PR status in browser
gh pr view 42 --web
```

## Sample Output

```
=== PR #42 Status ===

Title: Add feature X
State: OPEN
Draft: false

Reviews: APPROVED
  ✓ alice (approved)
  ✓ bob (approved)

CI Checks: 8 passing, 1 failing
  ✓ test (ubuntu)
  ✓ test (macos)
  ✓ test (windows)
  ✓ lint
  ✓ type-check
  ✓ build
  ✓ security-scan
  ✗ integration-test
  ⏳ deploy-preview (pending)

Mergeable: CONFLICTING
  ⚠ Merge conflicts with base branch

Blockers:
  1. integration-test check failing
  2. Merge conflicts need resolution

Next Steps:
  1. Fix integration test failures
  2. Resolve merge conflicts: git pull origin main
  3. Re-run checks after fixes
```
