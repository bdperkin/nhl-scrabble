# Integrate Sphinx Doctest and Linkcheck into Build Process

**GitHub Issue**: #233 - https://github.com/bdperkin/nhl-scrabble/issues/233

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

1-2 hours

## Description

Integrate Sphinx's doctest and linkcheck builders into the regular documentation build process with dedicated Makefile targets, CI enforcement, and comprehensive reporting. Ensure all code examples in documentation are tested and all external links are validated.

## Current State

**Current Documentation Build:**

The project has Sphinx documentation with quality plugins (task 005 completed):

```python
# docs/conf.py
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.doctest",      # Available but not actively used
    "sphinx.ext.linkcheck",    # Available but not actively used
    # ... other extensions
]
```

**Current Build Process:**

```makefile
# Makefile
docs:  ## Build HTML documentation
	sphinx-build -b html docs docs/_build/html

serve-docs:  ## Serve docs with auto-rebuild
	sphinx-autobuild docs docs/_build/html --port 8000
```

**Current Limitations:**

1. **No Doctest Enforcement** - Code examples in documentation not tested
1. **No Link Validation** - External links not checked for validity
1. **No CI Integration** - Doctest/linkcheck not part of CI pipeline
1. **No Regular Checks** - These builders not run as part of normal workflow
1. **No Reporting** - No systematic tracking of broken links or failing doctests

**Existing Quality Plugins:**

Task 005 added sphinx-coverage, linkcheck, doctest, sitemap, pytest-sphinx, and blacken-docs plugins, but they're not integrated into the regular build workflow with dedicated targets and CI enforcement.

## Proposed Solution

### Add Dedicated Makefile Targets

Create specific targets for doctest and linkcheck validation:

**1. Doctest Target**

```makefile
# Makefile

.PHONY: docs-doctest docs-linkcheck docs-quality

docs-doctest:  ## Test code examples in documentation
	@echo "Testing documentation code examples..."
	sphinx-build -b doctest docs docs/_build/doctest
	@echo "Doctest results: docs/_build/doctest/output.txt"

docs-doctest-verbose:  ## Test code examples with verbose output
	@echo "Testing documentation code examples (verbose)..."
	sphinx-build -b doctest -v docs docs/_build/doctest
```

**2. Linkcheck Target**

```makefile
docs-linkcheck:  ## Check external links in documentation
	@echo "Checking documentation links..."
	sphinx-build -b linkcheck docs docs/_build/linkcheck
	@echo "Link check results: docs/_build/linkcheck/output.txt"

docs-linkcheck-verbose:  ## Check links with verbose output
	@echo "Checking documentation links (verbose)..."
	sphinx-build -b linkcheck -v docs docs/_build/linkcheck
```

**3. Combined Quality Target**

```makefile
docs-quality: docs-doctest docs-linkcheck  ## Run all documentation quality checks
	@echo "All documentation quality checks complete!"
	@echo ""
	@echo "Results:"
	@echo "  Doctest: docs/_build/doctest/output.txt"
	@echo "  Linkcheck: docs/_build/linkcheck/output.txt"
```

### Configure Doctest Behavior

**Update docs/conf.py:**

```python
# docs/conf.py

# Doctest configuration
doctest_default_flags = (
    doctest.ELLIPSIS |          # Allow ... in output
    doctest.NORMALIZE_WHITESPACE  # Ignore whitespace differences
)

doctest_global_setup = """
import sys
import os
sys.path.insert(0, os.path.abspath('../src'))
from nhl_scrabble import *
"""

doctest_test_doctest_blocks = "default"  # Test >>> blocks in docstrings

# Optional: Skip certain files from doctest
doctest_path = []
```

### Configure Linkcheck Behavior

**Update docs/conf.py:**

```python
# docs/conf.py

# Linkcheck configuration
linkcheck_timeout = 15  # Seconds to wait for link response
linkcheck_workers = 5   # Parallel workers for checking links
linkcheck_retries = 2   # Number of retries for failed links

# Ignore certain URLs (e.g., localhost, private URLs)
linkcheck_ignore = [
    r'http://localhost:\d+/',  # Local development servers
    r'https://github.com/.*/pull/\d+',  # PR URLs (may not exist yet)
]

# Anchors to ignore (some sites don't support anchor checking)
linkcheck_anchors_ignore = [
    r'^!',  # Ignore anchors starting with !
]

# Report file
linkcheck_report_timeouts_as_broken = True
linkcheck_allowed_redirects = {}
```

### Add Doctest Examples to Documentation

**Example in docs/tutorials/basic-usage.md:**

````markdown
## Calculating Scores

You can calculate Scrabble scores for player names:

```python
>>> from nhl_scrabble.scoring import ScrabbleScorer
>>> scorer = ScrabbleScorer()
>>> scorer.calculate_score("OVECHKIN")
23
>>> scorer.calculate_score("CROSBY")
13
```

The scorer handles both uppercase and lowercase:

```python
>>> scorer.calculate_score("McDavid")
15
>>> scorer.calculate_score("MCDAVID")
15
```
````

### Integrate into CI/CD

**Update .github/workflows/docs.yml:**

```yaml
# .github/workflows/docs.yml

name: Documentation

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  docs-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          pip install -e ".[docs]"

      - name: Build HTML docs
        run: make docs-html

      - name: Test documentation code examples
        run: make docs-doctest
        continue-on-error: false  # Fail CI if doctests fail

      - name: Check documentation links
        run: make docs-linkcheck
        continue-on-error: true   # Don't fail CI for broken external links
        # Note: External sites may be temporarily down

      - name: Upload doctest results
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: doctest-results
          path: docs/_build/doctest/

      - name: Upload linkcheck results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: linkcheck-results
          path: docs/_build/linkcheck/
```

### Add Pre-commit Hook (Optional)

**Update .pre-commit-config.yaml:**

```yaml
# .pre-commit-config.yaml

repos:
  - repo: local
    hooks:
      - id: docs-doctest
        name: Sphinx Doctest
        entry: make docs-doctest
        language: system
        pass_filenames: false
        files: '^docs/.*\.(rst|md)$'
        stages: [manual]  # Only run when explicitly invoked

      - id: docs-linkcheck
        name: Sphinx Linkcheck
        entry: make docs-linkcheck
        language: system
        pass_filenames: false
        files: '^docs/.*\.(rst|md)$'
        stages: [manual]  # Only run when explicitly invoked
```

Usage:

```bash
# Run manually
pre-commit run docs-doctest --all-files
pre-commit run docs-linkcheck --all-files
```

### Update Documentation

**Add to docs/contributing/documentation.md:**

````markdown
## Documentation Quality Checks

### Testing Code Examples

All code examples in documentation are tested automatically:

```bash
# Test all doctest examples
make docs-doctest

# Test with verbose output
make docs-doctest-verbose
```

Doctest checks code blocks marked with `>>>`:

```python
>>> from nhl_scrabble import ScrabbleScorer
>>> scorer = ScrabbleScorer()
>>> scorer.calculate_score("TEST")
4
```

### Checking External Links

Validate all external links in documentation:

```bash
# Check all external links
make docs-linkcheck

# Check with verbose output
make docs-linkcheck-verbose
```

Link checker verifies:
- HTTP/HTTPS URLs are accessible
- Anchors exist on target pages
- No broken links or redirects

### Combined Quality Checks

Run all quality checks together:

```bash
make docs-quality
```

This runs:
- Doctest (code example validation)
- Linkcheck (external link validation)
````

## Implementation Steps

1. **Add Makefile Targets** (15 min)

   - Create `docs-doctest` target
   - Create `docs-linkcheck` target
   - Create `docs-quality` combined target
   - Add verbose variants
   - Update `make help` output

1. **Configure Sphinx Builders** (15 min)

   - Add doctest configuration to docs/conf.py
   - Add linkcheck configuration to docs/conf.py
   - Configure doctest_default_flags
   - Configure linkcheck_ignore patterns
   - Set reasonable timeouts and retries

1. **Add Doctest Examples** (15 min)

   - Add doctest examples to key documentation pages
   - Add examples to API reference
   - Add examples to tutorials
   - Test examples work correctly
   - Ensure examples are realistic

1. **Update CI/CD** (10 min)

   - Add doctest step to GitHub Actions
   - Add linkcheck step to GitHub Actions
   - Configure failure behavior
   - Upload results as artifacts
   - Add status badges to README (optional)

1. **Test and Validate** (15 min)

   - Run `make docs-doctest` locally
   - Run `make docs-linkcheck` locally
   - Verify CI integration works
   - Check output formatting
   - Verify error reporting

1. **Update Documentation** (10 min)

   - Document doctest usage
   - Document linkcheck usage
   - Add troubleshooting section
   - Update contributing guide
   - Add examples of good doctest patterns

## Testing Strategy

### Manual Testing

```bash
# Test doctest locally
make docs-doctest
# Verify: All code examples pass
# Verify: Output shows test results
# Verify: Failures are reported clearly

# Test linkcheck locally
make docs-linkcheck
# Verify: All external links checked
# Verify: Broken links reported
# Verify: Results in docs/_build/linkcheck/output.txt

# Test combined
make docs-quality
# Verify: Both checks run
# Verify: Summary displayed

# Test verbose modes
make docs-doctest-verbose
make docs-linkcheck-verbose
# Verify: Detailed output shown
```

### CI Testing

```bash
# Trigger CI workflow
git push origin feature/sphinx-doctest-linkcheck

# Verify:
# - Doctest runs in CI
# - Linkcheck runs in CI
# - Artifacts uploaded on failure
# - Status reported correctly
```

### Doctest Example Testing

Add intentional failures to test error reporting:

```python
# Intentional failure for testing
>>> from nhl_scrabble import ScrabbleScorer
>>> scorer = ScrabbleScorer()
>>> scorer.calculate_score("WRONG")
999  # This will fail - actual result is different
```

Verify error message is clear and helpful.

### Linkcheck Testing

Add intentional broken link to test validation:

```markdown
Check out [this broken link](https://example.invalid/notfound)
```

Verify linkcheck detects and reports it.

## Acceptance Criteria

- [ ] Makefile target `docs-doctest` tests code examples
- [ ] Makefile target `docs-linkcheck` validates external links
- [ ] Makefile target `docs-quality` runs both checks
- [ ] Verbose variants of targets available
- [ ] Doctest configuration in docs/conf.py
- [ ] Linkcheck configuration in docs/conf.py
- [ ] At least 5 doctest examples in documentation
- [ ] CI runs doctest on every PR
- [ ] CI runs linkcheck on every PR
- [ ] Doctest failures fail CI build
- [ ] Linkcheck failures don't fail CI (external sites may be down)
- [ ] Results uploaded as artifacts
- [ ] Documentation updated with usage instructions
- [ ] Troubleshooting guide for common issues
- [ ] All existing code examples pass doctest

## Related Files

**Modified Files:**

- `Makefile` - Add doctest and linkcheck targets
- `docs/conf.py` - Configure doctest and linkcheck
- `.github/workflows/docs.yml` - Add CI integration
- `docs/contributing/documentation.md` - Document usage
- `docs/tutorials/*.md` - Add doctest examples
- `docs/reference/*.md` - Add doctest examples

**New Files:**

- None (output directories excluded from git)

## Dependencies

**Python Dependencies** (already installed):

- `sphinx>=7.0` - Includes doctest and linkcheck builders
- All documentation dependencies from task 003

**No Task Dependencies** - Can implement independently

**Builds Upon**:

- enhancement/003-sphinx-documentation.md (COMPLETE ✅) - Sphinx infrastructure
- enhancement/005-sphinx-quality-plugins.md (COMPLETE ✅) - Quality plugins foundation

## Additional Notes

### Doctest vs Pytest-Sphinx

**Doctest** (this task):

- Built into Sphinx
- Tests `>>>` blocks in documentation
- Validates documentation examples
- Runs during documentation build

**Pytest-Sphinx** (task 005):

- Tests documentation build process
- Validates Sphinx configuration
- Checks for warnings/errors
- Runs in test suite

Both are complementary and serve different purposes.

### Linkcheck Reliability

**External Link Checking Challenges**:

- External sites may be temporarily down
- Rate limiting may cause false positives
- Some sites block automated checkers
- HTTPS certificates may expire

**Solution**:

- Don't fail CI on linkcheck failures
- Run linkcheck regularly but treat as informational
- Review linkcheck results manually
- Add problematic URLs to ignore list

### Doctest Best Practices

**Good Doctest Examples**:

```python
# Simple, clear, verifiable
>>> from nhl_scrabble import ScrabbleScorer
>>> scorer = ScrabbleScorer()
>>> scorer.calculate_score("TEST")
4

# Use ellipsis for variable output
>>> import nhl_scrabble
>>> nhl_scrabble.__version__  # doctest: +ELLIPSIS
'...'

# Normalize whitespace
>>> scorer.calculate_score("MULTIPLE WORDS")  # doctest: +NORMALIZE_WHITESPACE
20
```

**Avoid**:

```python
# Don't test implementation details
>>> scorer._internal_cache  # Bad - testing private API
...

# Don't test timing-dependent code
>>> import time
>>> time.sleep(1)  # Bad - unreliable in doctest
...

# Don't test external API calls
>>> fetch_nhl_data()  # Bad - depends on external service
...
```

### Doctest Directives

Common directives for doctest:

```python
# Skip a test
>>> slow_operation()  # doctest: +SKIP

# Allow ellipsis in output
>>> long_output()  # doctest: +ELLIPSIS
'Start ... End'

# Normalize whitespace
>>> formatted_output()  # doctest: +NORMALIZE_WHITESPACE
Expected   output

# Ignore exception details
>>> raise ValueError("Error")  # doctest: +IGNORE_EXCEPTION_DETAIL
Traceback (most recent call last):
ValueError: ...
```

### Linkcheck Configuration Examples

**Ignore Patterns**:

```python
# Ignore localhost URLs
linkcheck_ignore = [
    r'http://localhost.*',
    r'http://127\.0\.0\.1.*',
]

# Ignore GitHub PR/issue URLs that may not exist yet
linkcheck_ignore = [
    r'https://github.com/.*/issues/\d+',
    r'https://github.com/.*/pull/\d+',
]

# Ignore sites that block automated checkers
linkcheck_ignore = [
    r'https://linkedin\.com/.*',
    r'https://facebook\.com/.*',
]
```

**Timeout Configuration**:

```python
# Increase timeout for slow sites
linkcheck_timeout = 30  # Default: 15 seconds

# Reduce workers to avoid rate limiting
linkcheck_workers = 3   # Default: 5
```

### CI Integration Strategy

**Doctest Failures**:

- **Fail CI**: Documentation examples must work
- Broken code examples indicate outdated docs
- Forces documentation to stay synchronized with code

**Linkcheck Failures**:

- **Don't Fail CI**: External sites outside our control
- Report as informational
- Review periodically and update ignore list
- Use GitHub issue to track broken links

### Performance Considerations

**Doctest Performance**:

- Fast: Usually \<5 seconds for entire documentation
- Runs synchronously (one test at a time)
- Minimal overhead

**Linkcheck Performance**:

- Slow: Can take 30-60 seconds depending on link count
- Runs in parallel (configurable workers)
- May trigger rate limiting on some sites

**Optimization**:

- Run linkcheck less frequently (weekly scheduled job)
- Cache linkcheck results
- Skip linkcheck on draft PRs
- Increase linkcheck_workers for faster checking

### Scheduled Linkcheck (Future Enhancement)

Add weekly scheduled linkcheck:

```yaml
# .github/workflows/linkcheck-weekly.yml

name: Weekly Link Check

on:
  schedule:
    - cron: '0 0 * * 0'  # Every Sunday at midnight

jobs:
  linkcheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: pip install -e ".[docs]"
      - name: Check links
        run: make docs-linkcheck
      - name: Create issue if broken links found
        if: failure()
        run: |
          gh issue create \
            --title "Broken documentation links detected" \
            --body "See workflow run for details" \
            --label "documentation"
```

### Breaking Changes

**None** - This is purely additive:

- No changes to existing documentation build
- New targets are optional
- CI integration is informational
- No impact on users

### User Impact

**Positive**:

- Documentation examples guaranteed to work
- Broken links detected automatically
- Higher documentation quality
- Confidence in code examples

**Neutral**:

- No impact on users reading documentation
- CI runs slightly longer (30-60s)
- Developers must fix failing doctests

### Success Metrics

**Quantitative**:

- [ ] 100% of code examples pass doctest
- [ ] \<5% broken external links
- [ ] Doctest runs in \<10 seconds
- [ ] Linkcheck runs in \<60 seconds
- [ ] Zero false positive doctest failures

**Qualitative**:

- [ ] Documentation examples are reliable
- [ ] External links are up-to-date
- [ ] Developers trust documentation code
- [ ] Users can copy-paste examples successfully

## Implementation Notes

*To be filled during implementation:*

- Actual number of doctest examples added
- Linkcheck performance measurements
- CI integration challenges
- Ignored URL patterns needed
- Doctest directive usage patterns
- Deviations from plan
- Actual effort vs estimated
