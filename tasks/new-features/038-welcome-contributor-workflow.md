# First-Time Contributor Welcome Workflow

**GitHub Issue**: #305 - https://github.com/bdperkin/nhl-scrabble/issues/305

**Parent Task**: enhancement/022-comprehensive-github-workflows.md (#298)

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

30 minutes - 1 hour

## Description

Implement automated welcome workflow that posts friendly welcome messages to first-time contributors when they open their first PR or issue. Creates a welcoming community atmosphere and helps onboard new contributors.

## Current State

**No Automated Welcome:**

Currently, first-time contributors receive no special welcome:

- No automated greeting
- Must discover CONTRIBUTING.md on their own
- May feel unsure if contribution is welcome
- No guidance on what happens next

## Proposed Solution

Create `.github/workflows/welcome.yml`:

```yaml
name: Welcome First-Time Contributors

on:
  pull_request_target:
    types: [opened]
  issues:
    types: [opened]

permissions:
  contents: read
  issues: write
  pull-requests: write

jobs:
  welcome:
    name: Welcome New Contributor
    runs-on: ubuntu-latest

    steps:
      - name: Welcome first-time PR contributors
        if: github.event_name == 'pull_request_target'
        uses: actions/github-script@v7
        with:
          script: |
            // Check if this is the user's first PR
            const creator = context.payload.pull_request.user.login;

            // Get all PRs by this user
            const { data: prs } = await github.rest.pulls.list({
              owner: context.repo.owner,
              repo: context.repo.repo,
              state: 'all',
              creator: creator
            });

            // If this is their first PR, welcome them!
            if (prs.length === 1) {
              const message = `## 👋 Welcome to NHL Scrabble!

Thank you **@${creator}** for your first pull request! 🎉

We're excited to have you as a contributor to this project!

### What happens next?

1. **Automated checks** will run on your PR
2. A **maintainer will review** your changes
3. We may **request changes** or ask questions
4. Once approved, your PR will be **merged**!

### Resources

- 📚 [Contributing Guide](https://github.com/${context.repo.owner}/${context.repo.repo}/blob/main/CONTRIBUTING.md)
- 📖 [Documentation](https://bdperkin.github.io/nhl-scrabble/)
- 💬 Feel free to ask questions in comments
- 🐛 [Report issues](https://github.com/${context.repo.owner}/${context.repo.repo}/issues/new)

### Tips for a smooth review

- ✅ Make sure all CI checks pass
- ✅ Respond to review comments
- ✅ Keep commits focused and clear
- ✅ Update documentation if needed

Thank you for contributing! We'll review your PR as soon as possible. 🚀

---
*This is an automated welcome message for first-time contributors.*`;

              await github.rest.issues.createComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: context.payload.pull_request.number,
                body: message
              });
            }

      - name: Welcome first-time issue reporters
        if: github.event_name == 'issues'
        uses: actions/github-script@v7
        with:
          script: |
            // Check if this is the user's first issue
            const creator = context.payload.issue.user.login;

            // Get all issues by this user
            const { data: issues } = await github.rest.issues.listForRepo({
              owner: context.repo.owner,
              repo: context.repo.repo,
              state: 'all',
              creator: creator
            });

            // Filter out pull requests (they show up in issues API)
            const actualIssues = issues.filter(issue => !issue.pull_request);

            // If this is their first issue, welcome them!
            if (actualIssues.length === 1) {
              const message = `## 👋 Welcome!

Thank you **@${creator}** for opening your first issue! 🎉

### What happens next?

1. A **maintainer will review** your issue
2. We may **ask for clarification** or additional details
3. If it's a bug, we'll work on a fix
4. If it's a feature request, we'll discuss feasibility

### Want to contribute?

If you're interested in working on this yourself:

- 📚 Check out our [Contributing Guide](https://github.com/${context.repo.owner}/${context.repo.repo}/blob/main/CONTRIBUTING.md)
- 💬 Comment below to express interest
- 🚀 We're happy to help guide you through the process!

### Resources

- 📖 [Documentation](https://bdperkin.github.io/nhl-scrabble/)
- 🐛 [Report a bug](https://github.com/${context.repo.owner}/${context.repo.repo}/issues/new?labels=bug)
- ✨ [Request a feature](https://github.com/${context.repo.owner}/${context.repo.repo}/issues/new?labels=enhancement)

Thank you for helping improve NHL Scrabble! 🙏

---
*This is an automated welcome message for first-time issue reporters.*`;

              await github.rest.issues.createComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: context.payload.issue.number,
                body: message
              });
            }
```

## Implementation Steps

1. **Create Workflow File** (15min)

   - Create `.github/workflows/welcome.yml`
   - Configure triggers
   - Set up first-time detection
   - Add welcome messages

1. **Customize Messages** (15min)

   - Write welcoming PR message
   - Write welcoming issue message
   - Add project-specific links
   - Include helpful tips

1. **Test Workflow** (15-30min)

   - Create test account
   - Open first PR from test account
   - Verify welcome message
   - Open first issue from test account
   - Verify welcome message
   - Verify no message on second contribution

1. **Update Documentation** (10min)

   - Ensure CONTRIBUTING.md is current
   - Add note about welcome message
   - Update links in message if needed

## Testing Strategy

```bash
# Test 1: First-time PR (requires test account)
# 1. Create GitHub test account
# 2. Fork repository
# 3. Make change and create PR
# 4. Verify welcome comment appears

# Test 2: First-time issue (requires test account)
# 1. Use same test account
# 2. Create new issue
# 3. Verify welcome comment appears

# Test 3: Second PR (should not trigger)
# 1. Create another PR from test account
# 2. Verify NO welcome comment

# Verification
gh pr view <pr-number> --comments
gh issue view <issue-number> --comments
```

## Acceptance Criteria

- [ ] Workflow file created: `.github/workflows/welcome.yml`
- [ ] Triggers on PR open from first-timers
- [ ] Triggers on issue open from first-timers
- [ ] Welcome message friendly and helpful
- [ ] Links to CONTRIBUTING.md included
- [ ] Links to documentation included
- [ ] Next steps clearly explained
- [ ] Only triggers on first contribution
- [ ] No duplicate messages
- [ ] Works for both PRs and issues
- [ ] CONTRIBUTING.md is current and helpful
- [ ] Workflow tested with real accounts
- [ ] Messages reviewed for tone

## Related Files

**New Files:**

- `.github/workflows/welcome.yml` - Welcome workflow

**Modified Files:**

- `CONTRIBUTING.md` - Ensure comprehensive and current
- `CLAUDE.md` - Document welcome workflow

## Dependencies

**Tool Dependencies:**

- `actions/github-script@v7` - For welcome logic

**No Task Dependencies:**

- Can be implemented independently

## Additional Notes

### Message Tone

**Welcoming and friendly:**

- Use emojis sparingly (🎉👋🚀)
- Thank contributor sincerely
- Reduce uncertainty
- Provide clear next steps
- Offer help

**Avoid:**

- Overly formal language
- Too many rules upfront
- Intimidating tone
- Walls of text

### First-Time Detection

The workflow checks:

1. Count all PRs/issues by user
1. If count == 1, this is first contribution
1. Post welcome message

**Note:** Uses `pull_request_target` for PRs to have write permissions for PRs from forks.

### Security Considerations

Using `pull_request_target`:

- ✅ Has write permissions for forks
- ⚠️ Runs in context of base repository
- ✅ Safe here (only posts comments, no code execution)
- ✅ Does not checkout PR code

### Personalization Options

**Can customize by contribution type:**

- Good first issue → Extra encouraging
- Bug report → Thank for finding bugs
- Feature request → Mention community discussion
- Documentation → Appreciate clarity focus

**Can customize by user:**

- Check if user is member/collaborator
- Adjust message accordingly
- Different welcome for external vs internal

### Community Building

**Welcome messages help:**

- Reduce contributor anxiety
- Set positive tone
- Encourage more contributions
- Build inclusive community
- Clarify expectations

### Alternative Approaches

**GitHub built-in:**

- Repository settings → "Saved replies"
- Manually post on first contribution
- Less automated, more personal

**Dedicated bot:**

- More features (welcome issues)
- More complex to set up
- May be overkill for small projects

**This approach:**

- Simple and effective
- No external dependencies
- Fully customizable
- GitHub Actions native

## Implementation Notes

*To be filled during implementation:*

- Date started:
- Date completed:
- Actual effort:
- First contributor welcomed:
- Contributor feedback:
- Message adjustments:
