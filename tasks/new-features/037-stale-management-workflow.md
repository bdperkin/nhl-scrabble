# Stale Issue and PR Management Workflow

**GitHub Issue**: #304 - https://github.com/bdperkin/nhl-scrabble/issues/304

**Parent Task**: enhancement/022-comprehensive-github-workflows.md (#298)

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

1 hour

## Description

Implement automated stale issue and PR management workflow that marks inactive items as stale and closes them if they remain inactive. Keeps the issue tracker clean and relevant while giving contributors fair warning.

## Current State

**Manual Issue Management:**

Currently, stale issues and PRs accumulate:

- No automatic identification of stale items
- Manual review and closure required
- Contributors not notified of pending closure
- Issue tracker becomes cluttered
- Hard to identify active issues

## Proposed Solution

Create `.github/workflows/stale.yml`:

```yaml
name: Stale Issue and PR Management

on:
  schedule:
    # Run daily at 1 AM UTC
    - cron: '0 1 * * *'
  workflow_dispatch:  # Allow manual trigger

permissions:
  contents: read
  issues: write
  pull-requests: write

jobs:
  stale:
    name: Mark Stale Items
    runs-on: ubuntu-latest

    steps:
      - name: Stale issue and PR management
        uses: actions/stale@v9
        with:
          # General settings
          repo-token: ${{ secrets.GITHUB_TOKEN }}
          days-before-stale: 60
          days-before-close: 7
          remove-stale-when-updated: true
          ascending: true  # Process oldest first

          # Issue-specific settings
          stale-issue-message: |
            This issue has been automatically marked as stale because it has not had any activity for 60 days.

            It will be closed in 7 days if no further activity occurs.

            **To keep this issue open:**
            - Add a comment explaining current status
            - Add the `keep-open` label
            - Continue working on it

            Thank you for your contributions! 🙏

          close-issue-message: |
            This issue has been automatically closed due to inactivity.

            If this issue is still relevant, please:
            - Reopen it with updated information
            - Create a new issue with current details

            Thank you! 🙏

          stale-issue-label: 'stale'
          close-issue-label: 'closed-by-bot'
          exempt-issue-labels: 'keep-open,pinned,security,good-first-issue,help-wanted,enhancement,bug'

          # PR-specific settings (more aggressive)
          days-before-pr-stale: 30
          days-before-pr-close: 7

          stale-pr-message: |
            This pull request has been automatically marked as stale because it has not had any activity for 30 days.

            It will be closed in 7 days if no further activity occurs.

            **To keep this PR open:**
            - Push new commits
            - Add a comment with an update
            - Add the `keep-open` label
            - Request review

            If this PR is blocked on something, please add a comment explaining the situation.

            Thank you for your contribution! 🙏

          close-pr-message: |
            This pull request has been automatically closed due to inactivity.

            If you would like to resume work on this PR:
            - Reopen it and push new commits
            - Create a new PR with updated changes

            Thank you for your contribution! 🙏

          stale-pr-label: 'stale'
          close-pr-label: 'closed-by-bot'
          exempt-pr-labels: 'keep-open,pinned,security,work-in-progress,wip'

          # Performance settings
          operations-per-run: 100
          remove-pr-stale-when-updated: true
          remove-issue-stale-when-updated: true

          # Debugging
          debug-only: false
```

## Implementation Steps

1. **Create Workflow File** (20min)

   - Create `.github/workflows/stale.yml`
   - Configure schedule (daily)
   - Set stale thresholds
   - Configure messages

1. **Create Exempt Labels** (10min)

   - Create `keep-open` label
   - Create `stale` label
   - Create `closed-by-bot` label
   - Document label usage

1. **Configure Timeframes** (10min)

   - Issues: 60 days stale, 7 days to close
   - PRs: 30 days stale, 7 days to close
   - Adjust based on project needs

1. **Test Workflow** (20-30min)

   - Create test issue (manually mark as old)
   - Trigger workflow manually
   - Verify stale label applied
   - Verify comment posted
   - Remove stale label and verify removed
   - Test auto-close

1. **Update Documentation** (10min)

   - Add to CONTRIBUTING.md
   - Explain stale policy
   - Document `keep-open` label

## Testing Strategy

### Manual Testing

```bash
# Test 1: Create test issue
gh issue create --title "Test stale issue" --body "This is a test"
# Get issue number

# Test 2: Trigger workflow manually
gh workflow run stale.yml

# Test 3: Wait for workflow to complete
gh run watch

# Test 4: Verify stale label applied
gh issue view <issue-number> --json labels

# Test 5: Remove stale label
gh issue edit <issue-number> --remove-label "stale"

# Test 6: Add comment to issue
gh issue comment <issue-number> --body "Still relevant"

# Test 7: Verify stale label not re-added immediately
gh workflow run stale.yml
gh issue view <issue-number> --json labels
```

### Production Testing

```bash
# Monitor first few runs
gh run list --workflow=stale.yml --limit 5

# Check which items were marked stale
gh issue list --label stale
gh pr list --label stale

# Verify messages are helpful
gh issue view <stale-issue-number>
```

## Acceptance Criteria

- [ ] Workflow file created: `.github/workflows/stale.yml`
- [ ] Scheduled to run daily
- [ ] Issues marked stale after 60 days
- [ ] PRs marked stale after 30 days
- [ ] Items closed 7 days after stale
- [ ] Helpful messages posted
- [ ] `keep-open` label exempts items
- [ ] Important labels exempt items (security, etc.)
- [ ] Stale label removed when updated
- [ ] Manual trigger available
- [ ] Required labels created
- [ ] CONTRIBUTING.md updated
- [ ] Workflow tested
- [ ] No false positives in first run

## Related Files

**New Files:**

- `.github/workflows/stale.yml` - Stale management workflow

**Modified Files:**

- `CONTRIBUTING.md` - Document stale policy
- `CLAUDE.md` - Document stale workflow

**Repository Configuration:**

- Create `stale` label (yellow, #fbca04)
- Create `keep-open` label (green, #0e8a16)
- Create `closed-by-bot` label (gray, #d1d5da)

## Dependencies

**Tool Dependencies:**

- `actions/stale@v9` - Stale issue/PR management

**No Task Dependencies:**

- Can be implemented independently

## Additional Notes

### Timeframe Rationale

**Issues: 60 days**

- Gives ample time for discussion
- Allows for intermittent work
- Balances cleanup with contributor respect

**PRs: 30 days**

- PRs should move faster than issues
- Encourages active development
- Prevents abandoned PRs from accumulating

**Warning period: 7 days**

- Fair warning to contributors
- Time to respond and update
- Not so long that it's forgotten

### Exempt Labels

**Always exempt:**

- `keep-open` - Explicitly keep open
- `pinned` - Important to keep visible
- `security` - Security issues never stale
- `good-first-issue` - Keep available for newcomers
- `help-wanted` - Soliciting contributions

**Consider exempting:**

- `enhancement` - Features may take time
- `bug` - Bugs don't go away
- `documentation` - Docs always relevant
- `work-in-progress` - Active development

### Message Tone

**Friendly and helpful:**

- Thank contributors
- Explain why closing
- Provide clear next steps
- Make reopening easy

**Avoid:**

- Sounding punitive
- Making contributors feel bad
- Complicated reopen process
- Unclear reasoning

### Stale Policy Documentation

Add to CONTRIBUTING.md:

```markdown
## Stale Issue/PR Policy

To keep the issue tracker relevant and manageable:

- **Issues** inactive for 60 days are marked stale
- **Pull requests** inactive for 30 days are marked stale
- Items are closed 7 days after being marked stale

**To prevent closure:**
- Add a comment with an update
- Add the `keep-open` label
- Continue working on it

**Closed items can be reopened** at any time if still relevant.
```

### Statistics

Track effectiveness:

```bash
# How many items marked stale per month
gh issue list --label stale --state all --json createdAt

# How many auto-closed
gh issue list --label closed-by-bot --state closed

# How many reopened after stale
# (manual check needed)
```

### False Positive Prevention

**First run:**

- Test on a small subset first
- Review stale candidates manually
- Adjust timeframes if needed
- Monitor community feedback

**Ongoing:**

- Review stale items periodically
- Add `keep-open` to important items
- Adjust exempt labels as needed
- Listen to contributor feedback

## Implementation Notes

*To be filled during implementation:*

- Date started:
- Date completed:
- Actual effort:
- Items marked stale in first run:
- Items closed in first month:
- Adjustments made to timeframes:
- Community feedback:
