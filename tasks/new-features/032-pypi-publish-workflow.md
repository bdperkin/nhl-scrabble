# PyPI Package Publishing Workflow

**GitHub Issue**: #299 - https://github.com/bdperkin/nhl-scrabble/issues/299

**Parent Task**: enhancement/022-comprehensive-github-workflows.md (#298)

## Priority

**HIGH** - Must Do (Next Sprint)

## Estimated Effort

4-6 hours

## Description

Implement automated PyPI package publishing workflow that builds, tests, and publishes Python distributions (sdist and wheel) to PyPI on version tags. This workflow eliminates manual release steps, ensures consistent builds, and reduces release time from 30 minutes to ~5 minutes.

## Current State

**Manual Release Process:**

Currently, releasing to PyPI requires multiple manual steps:

```bash
# Current manual workflow (30 minutes)
1. Update version in pyproject.toml
2. Build packages: python -m build
3. Check distributions: twine check dist/*
4. Upload to TestPyPI: twine upload -r testpypi dist/*
5. Test installation from TestPyPI
6. Upload to PyPI: twine upload dist/*
7. Create git tag
8. Push tag to GitHub
9. Create GitHub release manually
```

**Problems:**

- ❌ Error-prone manual steps
- ❌ Takes 30 minutes per release
- ❌ Easy to forget steps
- ❌ Inconsistent builds across environments
- ❌ No automated verification
- ❌ Security risk (API tokens)

**Existing Infrastructure:**

- ✅ PyPI project exists (nhl-scrabble)
- ✅ Build system configured (hatchling)
- ✅ GitHub Actions CI working
- ❌ No automated publishing
- ❌ No trusted publishing configured

## Proposed Solution

### Automated Publishing Workflow

Create `.github/workflows/publish.yml` that automates the entire publishing process:

```yaml
name: Build and Publish Python Package

on:
  push:
    tags:
      - v*    # Trigger on version tags (v1.0.0, v2.1.0, etc.)

permissions:
  contents: write  # For creating GitHub releases
  id-token: write  # For PyPI trusted publishing

jobs:
  build:
    name: Build Python Package
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v6
        with:
          fetch-depth: 0  # Full history for version detection

      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: '3.12'

      - name: Install UV and build tools
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          uv pip install build twine check-wheel-contents --system

      - name: Build distributions
        run: |
          python -m build --sdist --wheel

      - name: Verify distributions
        run: |
          twine check dist/*
          check-wheel-contents dist/*.whl

      - name: List built packages
        run: ls -lh dist/

      - name: Upload build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: python-package-distributions
          path: dist/
          retention-days: 7

  test-install:
    name: Test Package Installation
    needs: build
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ['3.12', '3.13', '3.14']

    steps:
      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: ${{ matrix.python-version }}

      - name: Download build artifacts
        uses: actions/download-artifact@v4
        with:
          name: python-package-distributions
          path: dist/

      - name: Install wheel (Unix)
        if: runner.os != 'Windows'
        run: |
          pip install dist/*.whl
          nhl-scrabble --version

      - name: Install wheel (Windows)
        if: runner.os == 'Windows'
        shell: pwsh
        run: |
          pip install (Get-ChildItem dist/*.whl)
          nhl-scrabble --version

      - name: Test basic functionality
        run: |
          python -c "import nhl_scrabble; print(nhl_scrabble.__version__)"

  publish-testpypi:
    name: Publish to TestPyPI
    needs: test-install
    runs-on: ubuntu-latest
    environment:
      name: testpypi
      url: https://test.pypi.org/p/nhl-scrabble

    steps:
      - name: Download build artifacts
        uses: actions/download-artifact@v4
        with:
          name: python-package-distributions
          path: dist/

      - name: Publish to TestPyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          repository-url: https://test.pypi.org/legacy/
          skip-existing: true

  publish-pypi:
    name: Publish to PyPI
    needs: publish-testpypi
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/p/nhl-scrabble

    steps:
      - name: Download build artifacts
        uses: actions/download-artifact@v4
        with:
          name: python-package-distributions
          path: dist/

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1

  github-release:
    name: Create GitHub Release
    needs: publish-pypi
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v6

      - name: Download build artifacts
        uses: actions/download-artifact@v4
        with:
          name: python-package-distributions
          path: dist/

      - name: Extract version from tag
        id: get_version
        run: echo "VERSION=${GITHUB_REF#refs/tags/v}" >> $GITHUB_OUTPUT

      - name: Extract release notes
        id: extract_notes
        run: |
          # Extract version section from CHANGELOG.md
          awk '/^## \[${{ steps.get_version.outputs.VERSION }}\]/{flag=1; next} /^## \[/{flag=0} flag' CHANGELOG.md > release_notes.md || echo "No release notes found" > release_notes.md

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          files: dist/*
          body_path: release_notes.md
          draft: false
          prerelease: false
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### PyPI Trusted Publishing Setup

**One-Time Configuration:**

1. **Configure PyPI Trusted Publisher:**

   - Go to: https://pypi.org/manage/project/nhl-scrabble/settings/publishing/
   - Add trusted publisher:
     - Owner: `bdperkin`
     - Repository: `nhl-scrabble`
     - Workflow: `publish.yml`
     - Environment: `pypi`

1. **Configure TestPyPI Trusted Publisher:**

   - Go to: https://test.pypi.org/manage/project/nhl-scrabble/settings/publishing/
   - Add same configuration with environment: `testpypi`

1. **Create GitHub Environments:**

   - Settings → Environments → New: `pypi`
   - Settings → Environments → New: `testpypi`
   - Optional: Add protection rules (require approval)

**Benefits:**

- ✅ No API tokens to manage
- ✅ OIDC-based authentication
- ✅ More secure (short-lived credentials)
- ✅ Automatic credential rotation
- ✅ Bound to specific repo/workflow

## Implementation Steps

1. **Create Workflow File** (1h)

   - Create `.github/workflows/publish.yml`
   - Configure trigger on version tags
   - Set up build job with verification
   - Configure multi-platform testing matrix

1. **Configure PyPI Trusted Publishing** (30min)

   - Set up trusted publisher on PyPI
   - Set up trusted publisher on TestPyPI
   - Create GitHub environments
   - Test authentication

1. **Create Release Documentation** (1h)

   - Create `docs/RELEASING.md`
   - Document release workflow
   - Document manual fallback process
   - Add troubleshooting guide

1. **Test Workflow** (1-2h)

   - Create test tag on branch
   - Verify build process
   - Test TestPyPI publishing
   - Verify package installation
   - Test GitHub release creation

1. **Create First Automated Release** (30min-1h)

   - Update CHANGELOG.md
   - Create version tag
   - Monitor workflow execution
   - Verify PyPI publication
   - Verify GitHub release

1. **Update Documentation** (30min)

   - Update CONTRIBUTING.md
   - Update CLAUDE.md
   - Add workflow badge to README
   - Document for contributors

## Testing Strategy

### Pre-Implementation Testing

```bash
# Test manual build process
python -m build

# Verify distributions
ls -lh dist/
twine check dist/*

# Test local installation
pip install dist/*.whl
nhl-scrabble --version

# Clean up
rm -rf dist/
```

### Workflow Testing

```bash
# Create test tag
git tag v0.0.1-test
git push origin v0.0.1-test

# Monitor workflow
gh run list --workflow=publish.yml
gh run watch

# Verify outputs
gh run view --log

# Clean up test tag
git tag -d v0.0.1-test
git push origin :refs/tags/v0.0.1-test
```

### PyPI Testing

```bash
# Test TestPyPI installation
pip install --index-url https://test.pypi.org/simple/ nhl-scrabble==0.0.1.test

# Test production PyPI installation
pip install nhl-scrabble==2.1.0

# Verify version
python -c "import nhl_scrabble; print(nhl_scrabble.__version__)"
```

### Cross-Platform Verification

```bash
# Automated via GitHub Actions matrix:
# - Ubuntu, macOS, Windows
# - Python 3.12, 3.13, 3.14

# Manual verification (if needed):
# Install on different OS and test:
pip install nhl-scrabble
nhl-scrabble --version
nhl-scrabble analyze
```

## Acceptance Criteria

- [ ] Workflow file created: `.github/workflows/publish.yml`
- [ ] Workflow triggers on version tags (`v*`)
- [ ] Builds both sdist and wheel distributions
- [ ] Verifies package metadata with `twine check`
- [ ] Verifies wheel contents with `check-wheel-contents`
- [ ] Tests installation on Ubuntu, macOS, Windows
- [ ] Tests installation on Python 3.12-3.14
- [ ] Publishes to TestPyPI successfully
- [ ] Publishes to PyPI successfully
- [ ] Creates GitHub Release automatically
- [ ] Attaches distribution artifacts to release
- [ ] Extracts release notes from CHANGELOG.md
- [ ] PyPI trusted publishing configured
- [ ] TestPyPI trusted publishing configured
- [ ] GitHub environments created (`pypi`, `testpypi`)
- [ ] Release documentation created (`docs/RELEASING.md`)
- [ ] CONTRIBUTING.md updated
- [ ] CLAUDE.md updated
- [ ] README badge added (optional)
- [ ] Test release completed successfully
- [ ] Package installs correctly from PyPI
- [ ] Package version matches git tag

## Related Files

**New Files:**

- `.github/workflows/publish.yml` - Publishing workflow
- `docs/RELEASING.md` - Release process documentation

**Modified Files:**

- `CONTRIBUTING.md` - Add release process section
- `CLAUDE.md` - Document release automation
- `README.md` - Add PyPI badge (optional)
- `pyproject.toml` - Already configured (no changes needed)

**External Configuration:**

- PyPI trusted publisher settings
- TestPyPI trusted publisher settings
- GitHub repository environments

## Dependencies

**Task Dependencies:**

- **Depends on**: refactoring/010-dynamic-versioning-from-git-tags (#222)
  - Automated versioning from git tags required
  - Must implement before this workflow

**Tool Dependencies:**

- `build` - Build distributions
- `twine` - Upload packages and verify metadata
- `check-wheel-contents` - Verify wheel structure
- GitHub Actions (already available)
- PyPI/TestPyPI accounts (already exist)

**GitHub Actions:**

- `actions/checkout@v6`
- `actions/setup-python@v6`
- `actions/upload-artifact@v4`
- `actions/download-artifact@v4`
- `pypa/gh-action-pypi-publish@release/v1`
- `softprops/action-gh-release@v2`

## Additional Notes

### Release Workflow (User Perspective)

**Before:**

```bash
# 30 minutes, 9 manual steps, error-prone
1. Edit pyproject.toml version
2. python -m build
3. twine check dist/*
4. twine upload -r testpypi dist/*
5. Test install
6. twine upload dist/*
7. git tag v2.1.0
8. git push --tags
9. Create GitHub release manually
```

**After:**

```bash
# 5 minutes, 2 steps, automated
1. Update CHANGELOG.md
2. git tag v2.1.0 && git push --tags
# Everything else happens automatically!
```

### Security Benefits

**Traditional API Tokens:**

- ❌ Need to create and rotate tokens
- ❌ Tokens can leak in logs
- ❌ Manual revocation required
- ❌ Long-lived credentials

**Trusted Publishing (OIDC):**

- ✅ No tokens to manage
- ✅ Short-lived credentials
- ✅ Automatic rotation
- ✅ Bound to specific workflow
- ✅ More secure

### Version Tagging Strategy

```bash
# Semantic versioning
git tag v2.1.0      # Minor release (new features)
git tag v2.0.1      # Patch release (bug fixes)
git tag v3.0.0      # Major release (breaking changes)

# Pre-releases
git tag v2.1.0rc1   # Release candidate
git tag v2.1.0b1    # Beta
git tag v2.1.0a1    # Alpha

# Always use annotated tags
git tag -a v2.1.0 -m "Release version 2.1.0"
```

### CHANGELOG Format

Follow [Keep a Changelog](https://keepachangelog.com/):

```markdown
# Changelog

## [Unreleased]

### Added
- Feature X

## [2.1.0] - 2026-04-22

### Added
- New feature Y

### Fixed
- Bug Z
```

### Rollback Strategy

**If release fails during workflow:**

- Workflow stops automatically
- No partial publishes
- Fix issue and re-push tag

**If release succeeds but has bugs:**

- Cannot delete PyPI releases
- Can "yank" release (discourages installation)
- Publish hotfix version immediately

### Performance

**Build Time:**

- Source distribution: ~5s
- Wheel distribution: ~5s
- Verification: ~2s
- **Total build**: ~15s

**Testing Time:**

- Matrix: 9 combinations (3 OS × 3 Python versions)
- Parallel execution: ~2-3 minutes

**Publishing Time:**

- TestPyPI upload: ~10s
- PyPI upload: ~10s
- GitHub release: ~5s
- **Total publish**: ~25s

**Total Workflow**: ~3-4 minutes (vs 30 minutes manual)

### Future Enhancements

- Add release signing (GPG)
- Add SBOM attachment
- Add provenance attestation
- Add security scanning
- Add conda-forge publishing
- Add Docker image publishing
- Add release announcement automation

## Implementation Notes

*To be filled during implementation:*

- Date started:
- Date completed:
- Actual effort:
- Challenges encountered:
- Deviations from plan:
- Workflow run time:
- First release version:
