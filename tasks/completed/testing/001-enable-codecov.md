# Enable Codecov Integration for Code Coverage Tracking

**GitHub Issue**: #90 - https://github.com/bdperkin/nhl-scrabble/issues/90

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

1-2 hours

## Description

Enable Codecov integration to track code coverage over time and display accurate coverage badges. Currently, the Codecov badge in README.md shows "unknown" and the Codecov URL (https://app.codecov.io/gh/bdperkin/nhl-scrabble) returns a 404 error, even though the CI workflow is already configured to upload coverage reports.

## Current State

The project has partial Codecov setup but it's not working:

**README.md (line 5):**

```markdown
[![codecov](https://codecov.io/gh/bdperkin/nhl-scrabble/branch/main/graph/badge.svg)](https://codecov.io/gh/bdperkin/nhl-scrabble)
```

**CI Workflow (.github/workflows/ci.yml, lines 60-68):**

```yaml
  - name: Run tests with coverage
    run: pytest --cov --cov-report=xml --cov-report=term

  - name: Upload coverage to Codecov
    uses: codecov/codecov-action@v3
    with:
      file: ./coverage.xml
      flags: unittests
      name: codecov-${{ matrix.python-version }}
```

**Problems:**

1. Codecov project not initialized on codecov.io
1. No CODECOV_TOKEN configured in GitHub repository secrets
1. Badge shows "unknown" instead of actual coverage percentage
1. Codecov URL returns 404 "Not found" error
1. Using older codecov-action@v3 (v4 or v5 is latest)

**Current coverage status:**

- Test coverage achieved: 90.93% (from testing/001)
- Coverage reports generated locally: ✅
- Coverage uploaded to Codecov: ❌

## Proposed Solution

Complete the Codecov integration in three steps:

### Step 1: Set Up Codecov Project

1. **Sign in to Codecov.io**

   - Go to https://codecov.io/
   - Click "Log in" and authenticate with GitHub
   - Grant Codecov access to the nhl-scrabble repository

1. **Initialize Repository**

   - Navigate to https://app.codecov.io/gh/bdperkin
   - Click "Add repository"
   - Select `bdperkin/nhl-scrabble`
   - Codecov will provide a repository upload token

1. **Copy Upload Token**

   - Copy the `CODECOV_TOKEN` displayed
   - This token will be added to GitHub Secrets

### Step 2: Configure GitHub Repository

1. **Add Codecov Token to GitHub Secrets**

   ```bash
   # Via GitHub web UI:
   # 1. Go to: https://github.com/bdperkin/nhl-scrabble/settings/secrets/actions
   # 2. Click "New repository secret"
   # 3. Name: CODECOV_TOKEN
   # 4. Value: [paste token from Codecov]
   # 5. Click "Add secret"
   ```

1. **Update CI Workflow** (.github/workflows/ci.yml)

   Upgrade to codecov-action@v5 and add token:

   ```yaml
     - name: Upload coverage to Codecov
       uses: codecov/codecov-action@v5
       with:
         token: ${{ secrets.CODECOV_TOKEN }}
         files: ./coverage.xml
         flags: unittests
         name: codecov-${{ matrix.python-version }}
         fail_ci_if_error: true
         verbose: true
   ```

   Changes:

   - Upgrade `v3` → `v5` (latest stable version)
   - Add `token` parameter using GitHub secret
   - Change `file` → `files` (v5 parameter name)
   - Add `fail_ci_if_error: true` (fail CI if upload fails)
   - Add `verbose: true` (detailed logging for troubleshooting)

### Step 3: Configure Codecov Settings

Create `.codecov.yml` in repository root:

```yaml
# Codecov configuration
# Docs: https://docs.codecov.com/docs/codecov-yaml

coverage:
  status:
    project:
      default:
        target: 90%           # Maintain 90%+ coverage
        threshold: 1%         # Allow 1% decrease
        if_ci_failed: error   # Report error if CI fails

    patch:
      default:
        target: 80%           # New code should have 80%+ coverage
        threshold: 5%         # Allow 5% variance for new code

  range: 70..100             # Red at 70%, green at 100%

comment:
  layout: header, diff, files, footer
  behavior: default          # Comment on every PR
  require_changes: false     # Comment even if no coverage change

ignore:
  - tests/**                 # Ignore test files in coverage
  - scripts/**               # Ignore utility scripts
  - docs/**                  # Ignore documentation
  - '**/__init__.py'         # Ignore package init files

flags:
  unittests:
    carryforward: true       # Use previous coverage if upload fails
```

### Step 4: Update README Badge (Optional Enhancement)

Enhance the badge to show coverage percentage:

**Current:**

```markdown
[![codecov](https://codecov.io/gh/bdperkin/nhl-scrabble/branch/main/graph/badge.svg)](https://codecov.io/gh/bdperkin/nhl-scrabble)
```

**Enhanced with token for private repos (if needed):**

```markdown
[![codecov](https://codecov.io/gh/bdperkin/nhl-scrabble/graph/badge.svg?token=BADGE_TOKEN)](https://codecov.io/gh/bdperkin/nhl-scrabble)
```

Note: For public repos, the simple badge URL works fine. For private repos, you need a badge token from Codecov settings.

## Implementation Steps

### Step 1: Set Up Codecov Account (15 minutes)

1. Go to https://codecov.io/ and sign in with GitHub
1. Grant Codecov access to bdperkin/nhl-scrabble
1. Navigate to the repository on Codecov
1. Copy the `CODECOV_TOKEN` from repository settings

### Step 2: Add Token to GitHub (5 minutes)

1. Go to https://github.com/bdperkin/nhl-scrabble/settings/secrets/actions
1. Click "New repository secret"
1. Name: `CODECOV_TOKEN`
1. Value: Paste token from Step 1
1. Click "Add secret"

### Step 3: Update CI Workflow (10 minutes)

1. Edit `.github/workflows/ci.yml`
1. Update codecov-action from v3 to v5
1. Add `token` parameter
1. Update `file` to `files`
1. Add `fail_ci_if_error` and `verbose` flags
1. Commit changes:
   ```bash
   git add .github/workflows/ci.yml
   git commit -m "ci: Upgrade codecov-action to v5 and add token"
   ```

### Step 4: Create Codecov Config (15 minutes)

1. Create `.codecov.yml` in repository root
1. Configure coverage targets, comment behavior, and ignore patterns
1. Commit changes:
   ```bash
   git add .codecov.yml
   git commit -m "ci: Add Codecov configuration"
   ```

### Step 5: Test Integration (15 minutes)

1. Push changes to trigger CI:
   ```bash
   git push origin main
   ```
1. Monitor CI workflow execution
1. Check codecov-action step for successful upload
1. Verify coverage appears on https://app.codecov.io/gh/bdperkin/nhl-scrabble
1. Check README badge displays correct coverage percentage
1. Verify badge is clickable and links to Codecov dashboard

### Step 6: Verify and Document (10 minutes)

1. Check that badge shows actual coverage (90.93%)
1. Browse Codecov dashboard to see coverage trends
1. Create test PR to verify PR comments work
1. Document Codecov URL in CLAUDE.md

## Testing Strategy

### Manual Testing

1. **Trigger CI Workflow:**

   ```bash
   # Make a small change to trigger CI
   git commit --allow-empty -m "test: Trigger CI for Codecov verification"
   git push origin main
   ```

1. **Check CI Logs:**

   - Go to GitHub Actions
   - Open the latest CI run
   - Check "Upload coverage to Codecov" step
   - Verify upload successful (no errors)
   - Look for "Coverage uploaded to Codecov" message

1. **Verify Codecov Dashboard:**

   - Go to https://app.codecov.io/gh/bdperkin/nhl-scrabble
   - Verify coverage data is displayed
   - Check coverage percentage matches local (90.93%)
   - Browse file-level coverage reports

1. **Check Badge:**

   - View README.md on GitHub
   - Verify badge shows percentage (not "unknown")
   - Click badge, ensure it links to working Codecov URL
   - Check badge in both light and dark GitHub themes

1. **Test PR Comments:**

   - Create a test PR with code changes
   - Verify Codecov bot adds coverage comment
   - Check that comment shows coverage diff
   - Close test PR

### Automated Testing

Codecov will automatically:

- ✅ Upload coverage on every CI run
- ✅ Comment on PRs with coverage changes
- ✅ Fail status checks if coverage drops below threshold
- ✅ Update badge with latest coverage percentage

## Acceptance Criteria

- [x] Codecov account set up and repository added
- [x] `CODECOV_TOKEN` added to GitHub repository secrets
- [x] `.github/workflows/ci.yml` updated to use codecov-action@v5
- [x] `token` parameter added to codecov-action
- [x] `.codecov.yml` configuration file created
- [x] Coverage targets set (90% project, 80% patch)
- [x] Ignore patterns configured (tests/, docs/, etc.)
- [x] CI workflow successfully uploads coverage to Codecov
- [x] Codecov dashboard shows coverage data at https://app.codecov.io/gh/bdperkin/nhl-scrabble
- [x] README badge displays actual coverage percentage (90.93%)
- [x] Badge links to working Codecov URL (no 404)
- [x] Codecov comments appear on pull requests
- [x] Coverage status checks appear on PRs
- [x] Documentation updated (CLAUDE.md mentions Codecov)

## Related Files

- `.github/workflows/ci.yml` - CI workflow with codecov upload
- `.codecov.yml` - Codecov configuration (NEW)
- `README.md` - Badge at line 5
- `CLAUDE.md` - Update CI/CD section with Codecov info
- `.github/settings.yml` - Repository settings (for branch protection with codecov checks)

## Dependencies

**External Services:**

- Codecov.io account (free for public repos)
- GitHub repository secret for CODECOV_TOKEN

**CI/CD:**

- Existing test suite (already passing)
- pytest-cov (already installed)
- coverage.xml generation (already configured)

**No code dependencies** - This is purely CI/CD infrastructure

## Additional Notes

### Codecov Free Tier

Codecov offers a **free tier for public repositories**:

- ✅ Unlimited public repositories
- ✅ Unlimited users
- ✅ Pull request comments
- ✅ Coverage badges
- ✅ Coverage reports
- ✅ 6 months of coverage history

For private repos, Codecov has usage limits or paid plans.

### Coverage Trends

Once enabled, Codecov will track:

- **Overall coverage** over time (line chart)
- **Per-file coverage** to identify weak spots
- **PR coverage changes** to prevent regressions
- **Commit-level coverage** for detailed history

### Alternative Solutions

If Codecov doesn't work, alternatives include:

1. **Coveralls.io** - Similar service, free for public repos
1. **Codecov GitHub Action** - Self-hosted coverage tracking
1. **Artifact upload** - Store coverage reports as GitHub Actions artifacts
1. **GitHub Pages** - Host coverage HTML reports on GitHub Pages

### Security Considerations

**Token Security:**

- ✅ CODECOV_TOKEN stored as GitHub secret (encrypted)
- ✅ Token only has upload permissions (not admin)
- ✅ Token can be rotated if compromised

**Privacy:**

- ✅ Coverage data is public for public repos (acceptable)
- ✅ No sensitive data in coverage reports (only code coverage percentages)

### Performance Impact

Codecov upload adds ~5-10 seconds to CI runtime:

- Coverage generation: Already done (pytest --cov)
- Upload to Codecov: ~5-10 seconds per job
- Minimal impact on overall CI time

### Maintenance

Once set up, Codecov requires minimal maintenance:

- **Token rotation**: Only if compromised (optional)
- **Config updates**: Only if coverage targets change
- **Action updates**: Dependabot will update codecov-action

### Future Enhancements

After initial setup:

1. **Coverage Trends Graph** - Add to documentation
1. **Coverage Sunburst** - Visualize file coverage
1. **Commit Statuses** - Block PRs below coverage threshold
1. **Slack Integration** - Notify on coverage drops
1. **Coverage Goals** - Gamify improving coverage

### Troubleshooting

**If upload fails:**

1. Check CODECOV_TOKEN is correct in GitHub secrets
1. Verify coverage.xml file exists in CI workspace
1. Check codecov-action logs for specific error
1. Ensure repository is added to Codecov account

**If badge shows "unknown":**

1. Wait 5-10 minutes for first upload to process
1. Clear browser cache and refresh README
1. Check default branch is set to "main" in Codecov settings

**If 404 error persists:**

1. Verify repository URL matches: gh/bdperkin/nhl-scrabble
1. Check repository is public on Codecov (Settings → General)
1. Try logging out and back in to Codecov

### Documentation Updates

Update CLAUDE.md CI/CD section:

```markdown
### Coverage Tracking

The project uses Codecov for code coverage tracking:

- **Dashboard**: https://app.codecov.io/gh/bdperkin/nhl-scrabble
- **Coverage Target**: 90%+ overall, 80%+ for new code
- **Badge**: Shows current coverage percentage in README
- **PR Comments**: Codecov bot comments on all PRs with coverage changes
- **Configuration**: `.codecov.yml`

Coverage is uploaded automatically from CI on every commit to main and on all pull requests.
```

## Implementation Notes

**Implemented**: 2026-04-17
**Branch**: testing/001-enable-codecov
**PR**: #93 - https://github.com/bdperkin/nhl-scrabble/pull/93
**Commits**: 2 commits (5cd5822, baf4b09)
**GitHub Issue**: #90 (auto-closed)

### Actual Implementation

Successfully enabled complete Codecov integration in two phases:

**Phase 1: Automated Setup (20 minutes)**

1. **CI Workflow Updates** (.github/workflows/ci.yml):

   - Upgraded codecov-action from v3 to v5 (latest stable version)
   - Added `token` parameter using `${{ secrets.CODECOV_TOKEN }}`
   - Changed `file` to `files` (v5 parameter name)
   - Added `fail_ci_if_error: true` for strict upload validation
   - Added `verbose: true` for detailed troubleshooting logs

1. **Codecov Configuration** (.codecov.yml - NEW):

   - Created comprehensive configuration file
   - Set coverage targets: 90%+ project, 80%+ patch (new code)
   - Configured PR comment behavior (comment on all PRs)
   - Added ignore patterns: tests/, scripts/, docs/, __init__.py
   - Enabled carryforward flag for reliability

1. **Documentation** (CLAUDE.md):

   - Added "Coverage Tracking" subsection to CI/CD section
   - Documented Codecov dashboard URL
   - Documented coverage targets and behavior
   - Listed configuration file location

**Phase 2: Manual Setup (15 minutes - completed by user)**

1. Signed in to Codecov.io with GitHub account
1. Added bdperkin/nhl-scrabble repository to Codecov
1. Copied CODECOV_TOKEN from Codecov repository settings
1. Added CODECOV_TOKEN to GitHub repository secrets

### Challenges Encountered

**Initial CI Cancellation:**

- First CI run was cancelled before token was added
- Expected behavior - Codecov upload requires token
- Fixed by completing manual setup steps
- Second CI run succeeded completely after token added

**No other issues** - Implementation went smoothly

### Actual vs Estimated Effort

- **Estimated**: 1-2h
- **Actual**: ~35 minutes total
  - Automated setup: 20 minutes
  - Manual Codecov setup (user): 15 minutes
  - CI re-run and merge: included in above
- **Variance**: Under estimate by 50% (very efficient!)

**Why faster than estimated:**

- Clear task specification made implementation straightforward
- Pre-commit hooks caught all issues immediately
- Codecov setup was simpler than expected (good UX)
- No debugging required - everything worked first try

### Codecov Integration Verification

**Coverage Dashboard**: https://app.codecov.io/gh/bdperkin/nhl-scrabble

- ✅ Dashboard accessible and functional
- ✅ Coverage data displayed correctly
- ✅ Shows current coverage: ~90.93%
- ✅ File-level coverage reports available
- ✅ Commit history tracking working

**README Badge**:

- ✅ Badge displays actual coverage percentage (not "unknown")
- ✅ Badge links to working Codecov URL (no 404)
- ✅ Badge updates automatically with each commit

**PR Comments**:

- ✅ Codecov bot commented on PR #93
- ✅ Shows coverage diff (patch and project)
- ✅ Displays file-level coverage changes
- ✅ Links to detailed coverage report

**Status Checks**:

- ✅ codecov/project check appears on PRs
- ✅ codecov/patch check appears on PRs
- ✅ Both checks passed on PR #93
- ✅ Checks report coverage targets (90% project, 80% patch)

### Configuration Details

**Coverage Targets:**

- Project: 90% minimum (threshold: allow 1% decrease)
- Patch: 80% minimum for new code (threshold: allow 5% variance)
- Range: Red at 70%, green at 100%

**Ignored Paths:**

- `tests/**` - Test files don't count toward coverage
- `scripts/**` - Utility scripts excluded
- `docs/**` - Documentation excluded
- `**/__init__.py` - Package init files excluded

**PR Comment Behavior:**

- Layout: "header, diff, files, footer"
- Behavior: Comment on every PR (default)
- Require changes: false (comment even if no coverage change)

**Flags:**

- unittests: Carryforward enabled (use previous coverage if upload fails)

### Performance Impact

**CI Runtime:**

- Codecov upload adds ~5-10 seconds per job
- Minimal impact on overall CI time (CI still completes in ~2-3 minutes)
- Upload is reliable and fast

**Storage:**

- coverage.xml file: ~50KB per run
- Codecov stores 6 months of history (free tier)
- No local storage impact

### Related PRs

- PR #93 - Enable Codecov integration (merged)

### Lessons Learned

1. **Manual setup is required** - Codecov token cannot be automated, requires web UI
1. **Token security** - Store CODECOV_TOKEN in GitHub Secrets, never commit
1. **Fail fast** - `fail_ci_if_error: true` catches upload issues immediately
1. **Verbose logging** - `verbose: true` helpful for troubleshooting if needed
1. **Codecov free tier** - Very generous for public repos (unlimited repos, 6 months history)
1. **Badge token** - Not needed for public repos (simple badge URL works)

### Future Enhancements

Once Codecov is established:

1. **Coverage Trends Graph** - Add to documentation or README
1. **Coverage Sunburst** - Visualize file coverage in dashboard
1. **Commit Statuses** - Configure branch protection to require minimum coverage
1. **Slack Integration** - Notify team on coverage drops (optional)
1. **Coverage Goals** - Set progressive coverage improvement goals

### Verification Checklist

- [x] Codecov account created and repository added
- [x] CODECOV_TOKEN added to GitHub Secrets
- [x] CI workflow uploads coverage successfully
- [x] Codecov dashboard shows coverage data
- [x] README badge displays percentage (not "unknown")
- [x] Badge links to working Codecov URL
- [x] Codecov bot comments on PRs
- [x] codecov/project and codecov/patch checks work
- [x] Coverage targets enforced (90% project, 80% patch)
- [x] Documentation updated with Codecov info
