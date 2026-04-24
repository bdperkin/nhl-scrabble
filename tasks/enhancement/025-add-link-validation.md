# Add Automated Documentation Link Validation to CI

**GitHub Issue**: #351 - https://github.com/bdperkin/nhl-scrabble/issues/351

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

1 hour

## Description

Add automated link checking to the CI pipeline to detect broken external and internal links in documentation before they reach production. This enhancement will improve documentation quality and user experience by catching broken links early.

## Current State

**Documentation Overview**:

- 54+ Markdown files across `docs/` and root directory
- Estimated 200+ internal and external links
- No automated link validation exists
- Links can break over time without detection

**Current Process**:

- Manual link checking is time-consuming and error-prone
- Broken links are only discovered when users report them
- No systematic way to validate links before merge

**Risk**:

- Broken external links (sites moved, URLs changed)
- Broken internal links (files renamed, reorganized)
- Poor user experience when documentation links fail
- Unprofessional appearance

## Proposed Solution

Add `linkchecker` tool to CI pipeline with monthly scheduled runs to automatically validate all internal and external links in documentation.

### Architecture Changes

**Add New CI Workflow**:

```yaml
# .github/workflows/link-checker.yml
name: Check Documentation Links

on:
  # Run on PR to catch issues before merge
  pull_request:
    paths:
      - 'docs/**'
      - '*.md'
      - '.github/workflows/link-checker.yml'

  # Run monthly to catch external link rot
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM UTC

  # Allow manual trigger
  workflow_dispatch:

jobs:
  check-links:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install linkchecker
        run: pip install linkchecker

      - name: Check documentation links
        run: |
          # Check all markdown files
          linkchecker \
            --check-extern \
            --ignore-url='^https://github.com/.*/actions' \
            --ignore-url='^https://codecov.io' \
            --timeout=30 \
            docs/ *.md
        continue-on-error: ${{ github.event_name == 'schedule' }}

      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: linkchecker-report
          path: linkchecker-out.html
```

**Configuration Options**:

```ini
# .linkcheckerrc (optional config file)
[checking]
threads=10
timeout=30
recursionlevel=1

[filtering]
# Ignore rate-limited sites
ignoreurl=
    ^https://github.com/.*/actions
    ^https://codecov.io
    ^https://shields.io

[output]
status=1
verbose=1
```

### Dependency Changes

**Add to pyproject.toml**:

```toml
[project.optional-dependencies]
docs = [
    # ... existing deps
    "linkchecker>=10.0.0",
]
```

### Documentation Updates

**Update docs/audit/README.md**:

````markdown
## Audit Tools

### Automated Tools

**Markdown Tools**:
- `pymarkdown` - Markdown linting
- `mdformat` - Markdown formatting
- `linkchecker` - Link validation ✅ NEW
- `doc8` - RST linting

### Running Tools

```bash
# Validate links
linkchecker docs/ --check-extern
````

````

## Implementation Steps

1. **Install linkchecker locally** (5 min)
   ```bash
   pip install linkchecker
````

2. **Test linkchecker manually** (10 min)

   ```bash
   # Test on a subset first
   linkchecker docs/audit/

   # Test on all docs
   linkchecker docs/ *.md --check-extern

   # Review output and identify false positives
   ```

1. **Create linkchecker configuration** (10 min)

   - Create `.linkcheckerrc` with exclusions
   - Exclude rate-limited sites (GitHub Actions, Codecov, etc.)
   - Set appropriate timeout and thread count
   - Test configuration locally

1. **Create GitHub Actions workflow** (15 min)

   - Create `.github/workflows/link-checker.yml`
   - Configure to run on PR (for docs changes)
   - Configure monthly scheduled run
   - Add manual trigger option
   - Set up artifact upload for reports

1. **Add to project dependencies** (5 min)

   - Add linkchecker to `[project.optional-dependencies.docs]`
   - Update UV lock file: `uv lock`

1. **Update documentation** (10 min)

   - Update `docs/audit/README.md` with linkchecker info
   - Add usage instructions
   - Document exclusion patterns
   - Add to audit checklist

1. **Test workflow** (5 min)

   - Commit workflow file
   - Push to branch
   - Trigger manual workflow run
   - Verify workflow executes successfully
   - Review linkchecker report

1. **Commit changes** (5 min)

   ```bash
   git add .github/workflows/link-checker.yml
   git add .linkcheckerrc
   git add pyproject.toml uv.lock
   git add docs/audit/README.md
   git commit -m "feat(ci): Add automated link validation"
   ```

## Testing Strategy

### Manual Testing

**Local Validation**:

```bash
# Test linkchecker installation
linkchecker --version

# Test on small subset
linkchecker docs/audit/README.md

# Test on all docs (takes ~2-3 minutes)
linkchecker docs/ *.md --check-extern

# Test with configuration
linkchecker --config .linkcheckerrc docs/

# Verify output format
linkchecker docs/ --output=html > report.html
```

**Expected Output**:

```
Start checking at 2026-04-23 12:00:00+000
URL        `https://github.com/bdperkin/nhl-scrabble'
Name       `NHL Scrabble'
Parent URL None, line 0, col 0
Real URL   https://github.com/bdperkin/nhl-scrabble
Check time 0.123 seconds
Result     Valid: 200 OK

Statistics:
Content types: 45 text/html, 12 application/json
URL lengths: min=25, max=150, avg=75
Downloaded: 1.2MB
Threads: 10
That's it. 57 links in 57 URLs checked. 0 warnings found. 0 errors found.
```

### CI Testing

**Workflow Validation**:

1. Create test PR with known broken link
1. Verify workflow runs on PR
1. Verify workflow fails with broken link
1. Fix link and verify workflow passes
1. Trigger manual workflow run
1. Verify monthly schedule is configured

### Link Categories to Test

- ✅ Internal links (relative paths)
- ✅ External links (HTTPS)
- ✅ Anchor links (headers)
- ✅ Badge URLs
- ✅ GitHub issue/PR links
- ⚠️ Rate-limited sites (should be excluded)

## Acceptance Criteria

- [x] linkchecker added to project dependencies
- [x] GitHub Actions workflow created (`.github/workflows/link-checker.yml`)
- [x] Workflow runs on PRs that modify documentation
- [x] Workflow runs on monthly schedule (every Monday)
- [x] Workflow can be triggered manually
- [x] Configuration file excludes rate-limited sites
- [x] Linkchecker reports uploaded as artifacts
- [x] Documentation updated with linkchecker usage
- [x] Workflow tested and passing
- [x] All existing links validated (0 broken links)

## Related Files

**New Files**:

- `.github/workflows/link-checker.yml` - GitHub Actions workflow
- `.linkcheckerrc` - Linkchecker configuration (optional)

**Modified Files**:

- `pyproject.toml` - Add linkchecker dependency
- `uv.lock` - Updated dependencies
- `docs/audit/README.md` - Document linkchecker usage
- `docs/audit/documentation-audit-2026-04-23.md` - Reference as resolved

## Dependencies

**Required Tools**:

- linkchecker >= 10.0.0 (Python package)
- GitHub Actions (already available)

**Task Dependencies**:

- Documentation audit completed (task 013) ✅

**Related Tasks**:

- Task 026: Add code example testing
- Task 027: Improve function example coverage

## Additional Notes

### Benefits

**Quality Assurance**:

- Detect broken links early (before users encounter them)
- Maintain professional documentation appearance
- Better user experience
- Automated quality checks

**Time Savings**:

- No manual link checking needed
- Issues caught in PR review
- Monthly monitoring catches link rot

**Best Practices**:

- Aligns with documentation audit recommendations
- Industry standard tooling (linkchecker)
- Automated, repeatable process

### Configuration Trade-offs

**Run Frequency**:

- **PR runs**: Catch issues before merge (fast feedback)
- **Monthly runs**: Catch external link rot (comprehensive)
- **Trade-off**: More frequent = more CI time, less frequent = delayed detection

**Chosen approach**: PR runs for changed files + monthly full scan

**External Link Checking**:

- **Enabled**: More comprehensive, catches all broken links
- **Risk**: External sites can be flaky, cause false failures
- **Mitigation**: Ignore rate-limited sites, set reasonable timeout

### Exclusion Patterns

**Sites to Exclude** (rate-limited or dynamic):

- GitHub Actions URLs (require authentication)
- Codecov (varies by commit)
- shields.io badges (can be slow)
- api.github.com (rate-limited)

### Performance Considerations

**Link Checking Speed**:

- ~10-20 links per second (with 10 threads)
- ~200 links = ~20 seconds
- External checks add ~1-2 minutes
- Total: ~2-3 minutes per run

**CI Impact**:

- Minimal (\<5 min per PR)
- Runs only on doc changes
- Parallel with other jobs

### Future Enhancements

**Potential Improvements**:

1. Generate link report badge for README
1. Add link freshness metadata (last checked)
1. Create dashboard of link health over time
1. Integrate with PR comments (auto-comment on failures)

**Not Included** (out of scope):

- Spell checking (already covered by codespell)
- Markdown linting (already covered by pymarkdown)
- Link suggestions/autocorrect

### Known Limitations

**Linkchecker Limitations**:

- Cannot check links requiring authentication
- May have false positives on dynamic sites
- Requires network access (not offline)

**Workarounds**:

- Exclude authenticated URLs
- Use `continue-on-error` for scheduled runs
- Manual verification for complex cases

### Documentation Audit Context

This task addresses **Gap #2** from the documentation audit:

> **Gap 2: No Automated Link Validation**
>
> **Impact**: MEDIUM
> **Affected**: All 54+ documentation files
>
> **Recommendation**: Add linkchecker to CI pipeline with monthly scheduled runs

**Audit Finding**:

- "With 54+ documentation files, external links can break over time without detection."
- "No automated link checking exists"
- Priority: MEDIUM
- Effort: 1 hour ✅

## Implementation Notes

*To be filled during implementation:*

- Actual linkchecker configuration used
- Exclusion patterns finalized
- Number of links validated
- Broken links found and fixed
- Workflow run time
- Any challenges encountered
- Deviations from plan
