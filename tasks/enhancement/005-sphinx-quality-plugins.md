# Enhance Sphinx Documentation with Quality Plugins

**GitHub Issue**: #82 - https://github.com/bdperkin/nhl-scrabble/issues/82

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

2-4 hours

## Description

Enhance the Sphinx documentation build (enhancement/003) by implementing additional quality-focused plugins and tools for improved documentation building, CI/CD integration, coverage reporting, formatting, linting, publishing, security scanning, and testing.

**Note**: This task extends enhancement/003-sphinx-documentation.md and should be implemented after the base Sphinx setup is complete, or integrated directly into that implementation.

## Current State

The base Sphinx documentation (enhancement/003) includes 9 core extensions:

**Already Included**:
- ✅ sphinx - Core documentation engine
- ✅ sphinx-autobuild - Auto-rebuild during development
- ✅ sphinx-autodoc-typehints - Type hint integration
- ✅ sphinx-copybutton - Copy button for code blocks
- ✅ sphinx-design - Modern UI components
- ✅ sphinx-rtd-theme - Read the Docs theme
- ✅ sphinxcontrib-programoutput - CLI output in docs
- ✅ sphinxcontrib-spelling - Spell checking
- ✅ sphinxext-opengraph - Social sharing metadata

**Missing Quality Tools**:
- ❌ Documentation coverage enforcement
- ❌ Link validation tools
- ❌ Accessibility checking
- ❌ Performance optimization
- ❌ Security scanning
- ❌ Automated testing
- ❌ Advanced formatting/linting
- ❌ Multi-version support

## Proposed Solution

Add targeted quality plugins across different categories:

### 1. Documentation Coverage & Testing

**sphinx-coverage** (Built-in Extension)
```python
# conf.py
extensions = [
    ...
    'sphinx.ext.coverage',  # Doc coverage reporting
]

# Coverage configuration
coverage_show_missing_items = True
coverage_write_headline = True
coverage_ignore_modules = ['tests']
coverage_ignore_classes = ['_.*']  # Private classes
```

**pytest-sphinx** (Testing Framework)
```bash
# Install
uv pip install pytest-sphinx

# Test documentation builds
pytest --sphinx docs/
```

**doctest** (Built-in Extension)
```python
# conf.py
extensions = [
    ...
    'sphinx.ext.doctest',  # Test code examples
]

# Run doctests
cd docs && make doctest
```

### 2. Link Validation & Quality

**linkcheck** (Built-in Builder)
```bash
# Check all links in documentation
cd docs && make linkcheck

# Configure link checking
# conf.py
linkcheck_ignore = [
    r'http://localhost.*',  # Ignore local URLs
    r'https://example.com.*',  # Ignore example URLs
]
linkcheck_timeout = 10
linkcheck_retries = 3
linkcheck_workers = 5
```

**sphinx-linkcheck-plus** (Enhanced Link Checking)
```bash
uv pip install sphinx-linkcheck-plus

# Provides better reporting and retry logic
```

### 3. Accessibility & Standards

**sphinx-a11y** (Accessibility Checker)
```bash
uv pip install sphinx-a11y

# conf.py
extensions = [..., 'sphinx_a11y']

# Checks WCAG compliance
```

**sphinxcontrib-htmlhelp** (HTML Help Format)
```python
# conf.py  
extensions = [..., 'sphinx.ext.htmlhelp']

# Improves HTML accessibility
```

### 4. Performance & Optimization

**sphinx-needs** (Requirements Tracing)
```bash
uv pip install sphinx-needs

# Track requirements across docs
# Useful for tracing features to documentation
```

**sphinx-sitemap** (SEO Optimization)
```bash
uv pip install sphinx-sitemap

# conf.py
extensions = [..., 'sphinx_sitemap']

html_baseurl = 'https://bdperkin.github.io/nhl-scrabble/'
sitemap_url_scheme = "{link}"
```

### 5. Security & Validation

**doc8** (RST Linting - Already in pre-commit)
```bash
# Already configured in pre-commit
# Validates RST syntax and style
```

**rstcheck** (RST Syntax Checker - Already in pre-commit)
```bash
# Already configured in pre-commit  
# Validates RST code blocks
```

**bandit** (Security Linting for Code Examples)
```bash
uv pip install bandit

# Scan code examples in docs for security issues
bandit -r docs/ -f custom
```

### 6. Multi-Version Support

**sphinx-multiversion** (Version Documentation)
```bash
uv pip install sphinx-multiversion

# Build docs for multiple versions
sphinx-multiversion docs docs/_build/html

# Creates version selector
```

### 7. Advanced Formatting

**blacken-docs** (Format Code in Docs)
```bash
uv pip install blacken-docs

# Format Python code blocks in RST/markdown
blacken-docs docs/**/*.rst docs/**/*.md
```

**doc-formatter** (General Doc Formatting)
```bash
# Already using mdformat in pre-commit
# Can extend to RST with rst-formatter
```

### 8. CI/CD Integration

**sphinx-github-changelog** (Auto Changelog)
```bash
uv pip install sphinx-github-changelog

# Auto-generate changelog from GitHub releases
# conf.py
extensions = [..., 'sphinx_github_changelog']
```

**sphinx-versioning** (Automated Versioning)
```bash
# Integrates with git tags for version management
```

### 9. Enhanced Publishing

**sphinx-epub3** (EPUB Generation)
```python
# conf.py
extensions = [..., 'sphinx.ext.epub']

# Generate EPUB format for offline reading
# cd docs && make epub
```

**sphinxcontrib-pdf** (PDF Generation)
```bash
uv pip install rst2pdf sphinxcontrib-pdf

# Generate PDF documentation
# cd docs && make latexpdf
```

## Recommended Plugins (Priority Order)

### High Priority (Implement First)

1. **sphinx.ext.coverage** - Built-in, essential for quality
2. **sphinx.ext.doctest** - Built-in, validates examples
3. **linkcheck** - Built-in, prevents broken links
4. **sphinx-sitemap** - SEO, discoverability

### Medium Priority (Implement Second)

5. **pytest-sphinx** - Automated testing
6. **blacken-docs** - Code formatting consistency
7. **sphinx-a11y** - Accessibility compliance

### Low Priority (Nice to Have)

8. **sphinx-multiversion** - Multi-version support (when needed)
9. **sphinx-github-changelog** - Auto changelog (convenience)
10. **sphinx-needs** - Requirements tracing (advanced)

## Implementation Steps

### Phase 1: Built-in Extensions (1h)

1. **Add coverage extension**
   ```python
   # conf.py
   extensions = [
       ...
       'sphinx.ext.coverage',
       'sphinx.ext.doctest',
   ]
   
   coverage_show_missing_items = True
   ```

2. **Configure linkcheck**
   ```python
   # conf.py
   linkcheck_ignore = [r'http://localhost.*']
   linkcheck_timeout = 10
   ```

3. **Test coverage and links**
   ```bash
   cd docs
   make coverage
   make linkcheck
   make doctest
   ```

### Phase 2: SEO & Publishing (30min)

1. **Add sphinx-sitemap**
   ```bash
   uv pip install sphinx-sitemap
   ```

2. **Configure sitemap**
   ```python
   # conf.py
   extensions = [..., 'sphinx_sitemap']
   html_baseurl = 'https://bdperkin.github.io/nhl-scrabble/'
   ```

3. **Test sitemap generation**
   ```bash
   cd docs && make html
   ls _build/html/sitemap.xml
   ```

### Phase 3: Testing & Quality (1h)

1. **Add pytest-sphinx**
   ```bash
   uv pip install pytest-sphinx
   ```

2. **Create test suite**
   ```python
   # tests/test_docs.py
   def test_sphinx_build(sphinx_test_tempdir):
       """Test documentation builds successfully."""
       # pytest-sphinx provides fixtures
       pass
   ```

3. **Add blacken-docs to pre-commit**
   ```yaml
   # .pre-commit-config.yaml
   - repo: https://github.com/asottile/blacken-docs
     rev: v1.16.0
     hooks:
       - id: blacken-docs
         args: [--line-length=100]
   ```

### Phase 4: Accessibility (30min)

1. **Add sphinx-a11y**
   ```bash
   uv pip install sphinx-a11y
   ```

2. **Configure accessibility checks**
   ```python
   # conf.py
   extensions = [..., 'sphinx_a11y']
   ```

3. **Run accessibility audit**
   ```bash
   cd docs && make html
   # Review a11y warnings
   ```

## Testing Strategy

### Automated Tests

1. **Coverage check**
   ```bash
   make docs-coverage
   # Should report 100% coverage of documented items
   ```

2. **Link validation**
   ```bash
   make docs-linkcheck
   # Should have 0 broken links
   ```

3. **Doctest**
   ```bash
   make doctest
   # All code examples should execute successfully
   ```

4. **Build test**
   ```bash
   pytest tests/test_docs.py
   # Documentation build should succeed
   ```

### Manual Verification

1. **Sitemap**: Visit `/sitemap.xml`, verify all pages listed
2. **Accessibility**: Check WCAG compliance with browser tools
3. **Code formatting**: Verify all code blocks are formatted
4. **Multi-version**: Test version selector (if implemented)

### CI Integration

Add to `.github/workflows/docs.yml`:

```yaml
- name: Check documentation quality
  run: |
    cd docs
    make coverage
    make linkcheck
    make doctest
    
- name: Test documentation build
  run: |
    pytest tests/test_docs.py
    
- name: Check sitemap
  run: |
    test -f docs/_build/html/sitemap.xml
```

## Acceptance Criteria

### Essential (High Priority)

- [ ] sphinx.ext.coverage extension enabled
- [ ] Documentation coverage report generated (`make coverage`)
- [ ] Coverage shows 100% of public API documented
- [ ] sphinx.ext.doctest extension enabled
- [ ] All code examples pass doctest (`make doctest`)
- [ ] Link checking configured (`make linkcheck`)
- [ ] No broken links in documentation
- [ ] sphinx-sitemap extension installed and configured
- [ ] Sitemap.xml generated for SEO

### Recommended (Medium Priority)

- [ ] pytest-sphinx installed for automated testing
- [ ] Documentation build tests added
- [ ] blacken-docs configured in pre-commit
- [ ] Code blocks auto-formatted
- [ ] sphinx-a11y extension installed
- [ ] Accessibility report generated

### Optional (Low Priority)

- [ ] sphinx-multiversion configured (if versioning needed)
- [ ] sphinx-github-changelog configured (if auto-changelog desired)
- [ ] PDF/EPUB generation configured (if offline docs needed)

### CI/CD

- [ ] Coverage check in CI
- [ ] Link check in CI
- [ ] Doctest check in CI
- [ ] CI fails on broken links or failed doctests
- [ ] Sitemap validated in CI

## Related Files

- `docs/conf.py` - Add extension configurations
- `docs/Makefile` - Ensure coverage/linkcheck/doctest targets exist
- `pyproject.toml` - Add optional dependencies for quality plugins
- `.pre-commit-config.yaml` - Add blacken-docs hook
- `.github/workflows/docs.yml` - Add quality checks
- `tests/test_docs.py` - Documentation build tests (create)
- `Makefile` - Add quality check targets

## Dependencies

**Must complete first:**

- enhancement/003-sphinx-documentation.md - Base Sphinx setup required

**Blocks:**

- None

**Complements:**

- All documentation tasks benefit from quality enforcement

## Additional Notes

### Benefits

**For Documentation Quality:**

- 📊 **Coverage**: Track documentation completeness
- 🔗 **Reliability**: No broken links
- ✅ **Validation**: Code examples actually work
- ♿ **Accessible**: WCAG compliance
- 🔍 **Discoverable**: SEO optimized with sitemap

**For Maintenance:**

- 🤖 **Automated**: Quality checks in CI
- 🎨 **Formatted**: Consistent code examples
- 📝 **Tested**: Documentation builds reliably
- 🔒 **Secure**: Code examples scanned for issues

### Plugin Selection Philosophy

**Prefer built-in Sphinx extensions:**
- Already maintained by Sphinx team
- No extra dependencies
- Well-documented
- Stable

**Add third-party only when:**
- Clear value proposition
- Active maintenance
- Wide adoption
- No alternative built-in

### Integration with Existing Tools

**Already in pre-commit:**
- ✅ doc8 (RST linting)
- ✅ rstcheck (RST validation)
- ✅ codespell (spell checking)
- ✅ mdformat (markdown formatting)

**This task adds:**
- sphinx.ext.coverage (doc coverage)
- linkcheck (link validation)
- doctest (example testing)
- blacken-docs (code formatting)

### Cost-Benefit Analysis

| Plugin | Effort | Value | ROI |
|--------|--------|-------|-----|
| sphinx.ext.coverage | 15min | High | ⭐⭐⭐⭐⭐ |
| linkcheck | 10min | High | ⭐⭐⭐⭐⭐ |
| sphinx.ext.doctest | 20min | High | ⭐⭐⭐⭐⭐ |
| sphinx-sitemap | 15min | Medium | ⭐⭐⭐⭐ |
| pytest-sphinx | 30min | Medium | ⭐⭐⭐ |
| blacken-docs | 15min | Medium | ⭐⭐⭐ |
| sphinx-a11y | 20min | Low | ⭐⭐ |
| sphinx-multiversion | 1h+ | Low* | ⭐ |

*Low value initially, becomes important with multiple versions

**Recommended minimum:**
- sphinx.ext.coverage (15min)
- linkcheck (10min)
- sphinx.ext.doctest (20min)
- sphinx-sitemap (15min)

**Total minimum effort:** 60 minutes for high-value plugins

### Alternative: Integrate into enhancement/003

Rather than creating a separate task, these plugins could be integrated directly into enhancement/003-sphinx-documentation.md implementation.

**Pros:**
- ✅ Single comprehensive Sphinx implementation
- ✅ Avoid duplication
- ✅ Ensures quality from start

**Cons:**
- ❌ Increases complexity of enhancement/003
- ❌ Longer implementation time
- ❌ Harder to implement incrementally

**Recommendation:**
- If enhancement/003 not yet started: **Integrate into enhancement/003**
- If enhancement/003 already implemented: **Implement as separate task**
- If enhancement/003 in progress: **Pause and integrate high-priority plugins**

### Maintenance Strategy

**Weekly:**
- Run `make linkcheck` (automated in CI)

**Per release:**
- Run `make coverage` and review
- Run `make doctest` to verify examples

**Monthly:**
- Review accessibility report
- Update sphinx-sitemap configuration

**Annually:**
- Evaluate new Sphinx extensions
- Update extension versions
- Review and update configuration

### Documentation Quality Metrics

Track these metrics over time:

```markdown
## Documentation Quality Dashboard

**Coverage**: 100% (sphinx.ext.coverage)
**Links**: 0 broken (linkcheck)
**Doctests**: 45/45 passing (100%)
**Accessibility**: WCAG AA compliant
**SEO**: Sitemap with 52 pages
**Build Time**: 12 seconds
**Last Updated**: 2026-04-16
```

## Implementation Notes

*To be filled during implementation:*

- Plugins actually installed and configured
- Configuration decisions made
- CI integration approach
- Challenges encountered
- Actual effort vs estimated
- Quality improvements observed
