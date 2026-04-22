# PR Size Checker Workflow

**GitHub Issue**: #303 - https://github.com/bdperkin/nhl-scrabble/issues/303

**Parent Task**: enhancement/022-comprehensive-github-workflows.md (#298)

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

1-2 hours

## Description

Implement PR size checking workflow that comments on large pull requests, warns about review difficulty, and suggests splitting into smaller PRs. Encourages better PR practices and faster review cycles.

## Current State

**No Size Guidance:**

Currently, contributors can create PRs of any size without warnings:

- No automatic size checking
- No suggestions to split large PRs
- Reviewers must manually identify oversized PRs
- No documentation about preferred PR sizes

## Proposed Solution

Create `.github/workflows/pr-size.yml`:

```yaml
name: PR Size Checker

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write

jobs:
  check-size:
    name: Check PR Size
    runs-on: ubuntu-latest

    steps:
      - name: Check PR size and comment
        uses: actions/github-script@v7
        with:
          script: |
            const pr = context.payload.pull_request;
            const additions = pr.additions;
            const deletions = pr.deletions;
            const changedFiles = pr.changed_files;
            const totalChanges = additions + deletions;

            // Size thresholds
            const SMALL = 100;
            const MEDIUM = 500;
            const LARGE = 1000;

            let message = '';
            let shouldComment = false;

            if (totalChanges > LARGE) {
              shouldComment = true;
              message = `## ⚠️ Very Large PR (${totalChanges} lines changed)

This PR is very large and may be difficult to review effectively.

**Statistics:**
- 📝 Lines added: ${additions}
- 🗑️ Lines deleted: ${deletions}
- 📁 Files changed: ${changedFiles}
- 📊 Total changes: ${totalChanges}

**Recommendations:**
1. **Consider splitting** this PR into smaller, focused PRs
2. Each PR should ideally be **< 500 lines** for optimal review
3. Group related changes together
4. Create a tracking issue linking multiple PRs if needed

**Benefits of smaller PRs:**
- ✅ Faster review cycles
- ✅ Easier to understand changes
- ✅ Lower chance of bugs
- ✅ Easier to revert if needed
- ✅ Better git history

**If this PR cannot be split:**
- Add detailed description explaining the scope
- Consider scheduling a review session
- Break review into multiple passes

---
*This is an automated message to help improve code review quality.*`;
            } else if (totalChanges > MEDIUM) {
              shouldComment = true;
              message = `## 📏 Large PR (${totalChanges} lines changed)

This PR is getting large. Consider if it can be split for easier review.

**Statistics:**
- 📝 Lines added: ${additions}
- 🗑️ Lines deleted: ${deletions}
- 📁 Files changed: ${changedFiles}
- 📊 Total changes: ${totalChanges}

**Suggestions:**
- Ideal PR size: **< 500 lines**
- Current size: **${totalChanges} lines**
- Consider splitting if possible

---
*This is an automated reminder about PR best practices.*`;
            } else if (totalChanges > SMALL && totalChanges <= MEDIUM) {
              // Good size - post positive comment occasionally
              if (Math.random() < 0.1) {  // 10% of the time
                shouldComment = true;
                message = `## ✅ Well-Sized PR (${totalChanges} lines changed)

Great! This PR is a good size for review.

**Statistics:**
- 📝 Lines added: ${additions}
- 🗑️ Lines deleted: ${deletions}
- 📁 Files changed: ${changedFiles}

Keep up the good work! 🎉`;
              }
            }

            if (shouldComment) {
              // Check if we already commented
              const comments = await github.rest.issues.listComments({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: pr.number
              });

              const botComment = comments.data.find(comment =>
                comment.user.type === 'Bot' &&
                comment.body.includes('PR Size') || comment.body.includes('lines changed')
              );

              if (botComment) {
                // Update existing comment
                await github.rest.issues.updateComment({
                  owner: context.repo.owner,
                  repo: context.repo.repo,
                  comment_id: botComment.id,
                  body: message
                });
              } else {
                // Create new comment
                await github.rest.issues.createComment({
                  owner: context.repo.owner,
                  repo: context.repo.repo,
                  issue_number: pr.number,
                  body: message
                });
              }
            }
```

## Implementation Steps

1. **Create Workflow File** (30min)

   - Create `.github/workflows/pr-size.yml`
   - Configure triggers
   - Set up size calculation logic
   - Add comment logic

1. **Define Size Thresholds** (15min)

   - Determine appropriate sizes
   - Consider project context
   - Set warning levels

1. **Create Comment Templates** (30min)

   - Write helpful messages
   - Add actionable suggestions
   - Include statistics
   - Add positive reinforcement

1. **Test Workflow** (30min)

   - Create small PR (verify no comment/positive)
   - Create medium PR (verify no/light warning)
   - Create large PR (verify warning)
   - Create very large PR (verify strong warning)
   - Verify comment updates on PR changes

1. **Update Documentation** (15min)

   - Add PR size guidelines to CONTRIBUTING.md
   - Document best practices
   - Add examples

## Testing Strategy

```bash
# Test 1: Small PR (<100 lines)
git checkout -b test/small-pr
# Make small change
gh pr create --title "test: Small PR"
# Expected: No comment or occasional positive comment

# Test 2: Medium PR (100-500 lines)
git checkout -b test/medium-pr
# Make ~300 line change
gh pr create --title "test: Medium PR"
# Expected: Light suggestion to keep it small

# Test 3: Large PR (500-1000 lines)
git checkout -b test/large-pr
# Make ~700 line change
gh pr create --title "test: Large PR"
# Expected: Warning with suggestions

# Test 4: Very large PR (>1000 lines)
git checkout -b test/very-large-pr
# Make ~1500 line change
gh pr create --title "test: Very large PR"
# Expected: Strong warning, split recommendation

# Test 5: Update existing PR
# Push more changes to test/large-pr
git push
# Expected: Comment updated with new stats
```

## Acceptance Criteria

- [ ] Workflow file created: `.github/workflows/pr-size.yml`
- [ ] Size thresholds configured appropriately
- [ ] Comments post on large PRs (>500 lines)
- [ ] Strong warnings on very large PRs (>1000 lines)
- [ ] Statistics included in comments
- [ ] Actionable suggestions provided
- [ ] Positive reinforcement for good-sized PRs
- [ ] Comments update when PR changes
- [ ] No duplicate comments created
- [ ] CONTRIBUTING.md updated with size guidelines
- [ ] Test PRs verified
- [ ] Documentation complete

## Related Files

**New Files:**

- `.github/workflows/pr-size.yml` - Size checking workflow

**Modified Files:**

- `CONTRIBUTING.md` - Add PR size guidelines
- `CLAUDE.md` - Document size checking workflow

## Dependencies

**Tool Dependencies:**

- `actions/github-script@v7` - For PR size checking

**No Task Dependencies:**

- Can be implemented independently

## Additional Notes

### Size Thresholds

**Recommended:**

- **< 100 lines**: Excellent, fast review
- **100-500 lines**: Good, manageable review
- **500-1000 lines**: Large, consider splitting
- **> 1000 lines**: Very large, strongly suggest splitting

**Project-Specific:**
Adjust thresholds based on:

- Team size
- Review capacity
- Type of changes
- Codebase complexity

### PR Splitting Strategies

**By Feature:**

```
Large PR: "Add user authentication system"

Split into:
1. "Add authentication models"
2. "Add authentication API endpoints"
3. "Add authentication UI"
4. "Add authentication tests"
```

**By Layer:**

```
Large PR: "Implement caching system"

Split into:
1. "Add caching infrastructure"
2. "Integrate caching in API layer"
3. "Add cache invalidation"
4. "Add caching documentation"
```

### Benefits

**For Contributors:**

- Clear size expectations
- Guidance on splitting
- Positive feedback

**For Reviewers:**

- Smaller, focused reviews
- Better review quality
- Faster turnaround

**For Project:**

- Better git history
- Easier debugging
- Lower bug risk
- Faster merges

### Comment Examples

**Small PR:**

```
## ✅ Well-Sized PR (87 lines changed)

Great! This PR is a good size for review.

**Statistics:**
- 📝 Lines added: 65
- 🗑️ Lines deleted: 22
- 📁 Files changed: 3

Keep up the good work! 🎉
```

**Very Large PR:**

```
## ⚠️ Very Large PR (1543 lines changed)

This PR is very large and may be difficult to review effectively.

**Statistics:**
- 📝 Lines added: 1320
- 🗑️ Lines deleted: 223
- 📁 Files changed: 42
- 📊 Total changes: 1543

**Recommendations:**
1. **Consider splitting** this PR into smaller, focused PRs
2. Each PR should ideally be **< 500 lines** for optimal review
...
```

### Exceptions

Some PRs legitimately need to be large:

- Generated code updates
- Major refactoring
- Database migrations
- Dependency updates
- Documentation overhauls

**For these cases:**

- Add detailed PR description
- Explain why splitting isn't feasible
- Request specific review focus areas
- Consider breaking review into phases

## Implementation Notes

*To be filled during implementation:*

- Date started:
- Date completed:
- Actual effort:
- Final thresholds chosen:
- Test results:
- Developer feedback:
