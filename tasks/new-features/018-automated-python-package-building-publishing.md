# Automated Python Package Building and Publishing

**GitHub Issue**: #224 - https://github.com/bdperkin/nhl-scrabble/issues/224

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

4-6 hours

## Description

Set up automated building and publishing infrastructure for all standard Python packaging formats (source distributions, wheels) with CI/CD integration, ensuring consistent, reliable, and automated releases to PyPI whenever a new version is tagged.

## Current State

**Manual Build and Publish Process:**

Currently, package releases require manual intervention:

```bash
# Manual release workflow (current)
1. Update version in pyproject.toml manually
2. Build packages: python -m build
3. Check distributions: twine check dist/*
4. Upload to PyPI: twine upload dist/*
5. Create Git tag: git tag v2.0.0
6. Push tag: git push --tags
```

**Problems:**

1. **Manual Steps**: Error-prone, requires remembering all steps
1. **Inconsistent Builds**: Different environments may produce different builds
1. **No Automation**: Release process takes 15-30 minutes of manual work
1. **Version Sync**: Must manually keep pyproject.toml and git tags in sync
1. **No Verification**: No automated pre-publish checks
1. **Missing Formats**: May forget to build all distribution formats

**Current Package Distribution:**

```toml
# pyproject.toml
[project]
name = "nhl-scrabble"
version = "2.0.0"  # Manual version management

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Existing Infrastructure:**

- ✅ GitHub Actions CI already configured
- ✅ PyPI project already exists (nhl-scrabble)
- ✅ Build system configured (hatchling)
- ❌ No automated release workflow
- ❌ No PyPI publishing automation
- ❌ No build artifact verification

## Proposed Solution

### Comprehensive Build and Publish Automation

Implement GitHub Actions workflow that automatically builds and publishes Python packages on version tags:

```
Git Tag (v2.0.0)
      ↓
GitHub Actions Trigger
      ↓
Build & Test Pipeline
      ↓
   ┌──────────────────┐
   │  Build Packages  │
   │  - sdist (.tar.gz)│
   │  - wheel (.whl)   │
   └────────┬─────────┘
            ↓
   ┌──────────────────┐
   │ Verify Packages  │
   │  - Check metadata│
   │  - Validate files│
   │  - Test install  │
   └────────┬─────────┘
            ↓
   ┌──────────────────┐
   │ Publish to PyPI  │
   │  - TestPyPI first│
   │  - Production PyPI│
   └────────┬─────────┘
            ↓
   ┌──────────────────┐
   │ Create Release   │
   │  - GitHub Release│
   │  - Release notes │
   │  - Attach files  │
   └──────────────────┘
```

### GitHub Actions Workflow

**.github/workflows/publish.yml:**

```yaml
name: Build and Publish Python Package

on:
  push:
    tags:
      - 'v*'  # Trigger on version tags (v1.0.0, v2.1.0, etc.)

permissions:
  contents: write  # For creating GitHub releases
  id-token: write  # For PyPI trusted publishing

jobs:
  build:
    name: Build Python Package
    runs-on: ubuntu-latest

    steps:
      - name: Check out repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for setuptools-scm/hatch-vcs

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install build dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine check-wheel-contents

      - name: Build source distribution
        run: python -m build --sdist

      - name: Build wheel distribution
        run: python -m build --wheel

      - name: Check distributions
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
        python-version: ['3.10', '3.11', '3.12', '3.13', '3.14']

    steps:
      - name: Set up Python
        uses: actions/setup-python@v5
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
      - name: Check out repository
        uses: actions/checkout@v4

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
          awk '/^## \[${{ steps.get_version.outputs.VERSION }}\]/{flag=1; next} /^## \[/{flag=0} flag' CHANGELOG.md > release_notes.md

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

### PyPI Trusted Publishing

**Setup (One-Time Configuration):**

1. **Enable Trusted Publishing on PyPI:**

   - Go to https://pypi.org/manage/project/nhl-scrabble/settings/publishing/
   - Add trusted publisher:
     - PyPI Project: nhl-scrabble
     - Owner: bdperkin
     - Repository: nhl-scrabble
     - Workflow: publish.yml
     - Environment: pypi

1. **Enable TestPyPI Publishing:**

   - Go to https://test.pypi.org/manage/project/nhl-scrabble/settings/publishing/
   - Add same configuration for testing

1. **Configure GitHub Environments:**

   - Settings → Environments → New environment: "pypi"
   - Settings → Environments → New environment: "testpypi"
   - Add protection rules (optional): require approval

**Benefits of Trusted Publishing:**

- ✅ No API tokens to manage
- ✅ More secure (OIDC-based authentication)
- ✅ Automatic credential rotation
- ✅ GitHub-native integration

### Package Build Configuration

**pyproject.toml Enhancement:**

```toml
[build-system]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"

[project]
name = "nhl-scrabble"
dynamic = ["version"]  # Version from git tags (task #010)
description = "Calculate Scrabble scores for NHL player names"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
keywords = ["nhl", "scrabble", "hockey", "sports", "statistics"]
authors = [
    {name = "Brandon Perkins", email = "bperkins@example.com"}
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
    "Topic :: Games/Entertainment",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

[project.urls]
Homepage = "https://github.com/bdperkin/nhl-scrabble"
Documentation = "https://bdperkin.github.io/nhl-scrabble/"
Repository = "https://github.com/bdperkin/nhl-scrabble"
Issues = "https://github.com/bdperkin/nhl-scrabble/issues"
Changelog = "https://github.com/bdperkin/nhl-scrabble/blob/main/CHANGELOG.md"

[tool.hatch.version]
source = "vcs"  # Dynamic versioning from git tags

[tool.hatch.build.targets.sdist]
include = [
    "/src",
    "/tests",
    "/docs",
    "/README.md",
    "/LICENSE",
    "/CHANGELOG.md",
    "/pyproject.toml",
]

[tool.hatch.build.targets.wheel]
packages = ["src/nhl_scrabble"]
```

### Release Workflow Documentation

**docs/RELEASING.md:**

````markdown
# Release Process

## Automated Release Workflow

Releases are fully automated via GitHub Actions. To create a new release:

### 1. Prepare Release

```bash
# Ensure main branch is clean
git checkout main
git pull origin main

# Run full test suite
make tox-parallel

# Verify all checks pass
make check
````

### 2. Update CHANGELOG

Edit `CHANGELOG.md`:

```markdown
## [2.1.0] - 2026-04-19

### Added
- New feature X
- Enhancement Y

### Fixed
- Bug Z

### Changed
- Improved performance of A
```

Commit changelog:

```bash
git add CHANGELOG.md
git commit -m "docs: Update CHANGELOG for v2.1.0"
git push origin main
```

### 3. Create Version Tag

```bash
# Create annotated tag
git tag -a v2.1.0 -m "Release version 2.1.0"

# Push tag (triggers release workflow)
git push --tags
```

### 4. Automated Pipeline

GitHub Actions automatically:

1. ✅ Builds source distribution (sdist)
1. ✅ Builds wheel distribution
1. ✅ Verifies package metadata
1. ✅ Tests installation on multiple platforms
1. ✅ Publishes to TestPyPI
1. ✅ Publishes to PyPI
1. ✅ Creates GitHub Release with artifacts
1. ✅ Attaches release notes from CHANGELOG

### 5. Verify Release

```bash
# Check PyPI
pip install --upgrade nhl-scrabble
python -c "import nhl_scrabble; print(nhl_scrabble.__version__)"

# Check GitHub Release
gh release view v2.1.0
```

### Emergency Rollback

If a release has issues:

```bash
# Delete tag locally and remotely
git tag -d v2.1.0
git push origin :refs/tags/v2.1.0

# Delete GitHub release
gh release delete v2.1.0

# Yank PyPI release (keeps it available but discourages installation)
# Must be done manually at: https://pypi.org/manage/project/nhl-scrabble/releases/
```

## Pre-Release Versions

For beta/RC releases:

```bash
git tag -a v2.1.0rc1 -m "Release candidate 1 for 2.1.0"
git push --tags
```

PyPI will mark as pre-release automatically.

## Manual Release (Emergency)

If GitHub Actions is unavailable:

```bash
# Build packages
python -m build

# Check distributions
twine check dist/*

# Upload to PyPI
twine upload dist/*

# Create GitHub release
gh release create v2.1.0 dist/* --title "v2.1.0" --notes-file CHANGELOG.md
```

````

## Implementation Steps

1. **Create GitHub Actions Workflow** (1-2h)

   - Create `.github/workflows/publish.yml`
   - Configure trigger on version tags
   - Set up build job with all checks
   - Configure artifact uploads

2. **Configure PyPI Trusted Publishing** (30min)

   - Set up trusted publisher on PyPI
   - Set up trusted publisher on TestPyPI
   - Create GitHub environments (pypi, testpypi)
   - Test authentication

3. **Enhance Package Metadata** (30min)

   - Update pyproject.toml with comprehensive metadata
   - Add classifiers for PyPI discoverability
   - Configure project URLs
   - Set up sdist/wheel build targets

4. **Add Package Verification** (1h)

   - Install check-wheel-contents
   - Add twine check step
   - Add cross-platform installation tests
   - Verify package metadata completeness

5. **Create Release Documentation** (1h)

   - Write docs/RELEASING.md
   - Document automated workflow
   - Document manual fallback process
   - Add troubleshooting section

6. **Add GitHub Release Automation** (30min-1h)

   - Configure GitHub release creation
   - Extract release notes from CHANGELOG.md
   - Attach distribution artifacts
   - Set up release environment

7. **Test Release Workflow** (1-2h)

   - Create test tag on fork/branch
   - Verify build process
   - Test TestPyPI publishing
   - Verify package installation
   - Test GitHub release creation

8. **Update Documentation** (30min)

   - Update CONTRIBUTING.md with release process
   - Update CLAUDE.md with automation details
   - Update README badges if needed
   - Document dependencies (task #010)

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
````

### GitHub Actions Testing

```bash
# Test workflow syntax
gh workflow view publish.yml

# Trigger test run (on test tag)
git tag v0.0.1-test
git push origin v0.0.1-test

# Monitor workflow
gh run list --workflow=publish.yml
gh run watch

# Clean up test tag
git tag -d v0.0.1-test
git push origin :refs/tags/v0.0.1-test
```

### PyPI Publishing Testing

```bash
# Test TestPyPI installation
pip install --index-url https://test.pypi.org/simple/ nhl-scrabble

# Test production PyPI installation
pip install nhl-scrabble

# Verify version
python -c "import nhl_scrabble; print(nhl_scrabble.__version__)"
```

### Cross-Platform Testing

```bash
# Automated via GitHub Actions matrix:
# - ubuntu-latest, macos-latest, windows-latest
# - Python 3.10, 3.11, 3.12, 3.13, 3.14

# Manual verification (if needed):
# Install on different OS and verify:
pip install nhl-scrabble
nhl-scrabble --version
```

## Acceptance Criteria

- [ ] GitHub Actions workflow created: `.github/workflows/publish.yml`
- [ ] Workflow triggers on version tags (`v*`)
- [ ] Builds both sdist and wheel distributions
- [ ] Verifies package metadata with twine check
- [ ] Verifies wheel contents with check-wheel-contents
- [ ] Tests installation on Ubuntu, macOS, Windows
- [ ] Tests installation on Python 3.10-3.14
- [ ] Publishes to TestPyPI successfully
- [ ] Publishes to PyPI successfully
- [ ] Creates GitHub Release automatically
- [ ] Attaches distribution artifacts to release
- [ ] Extracts release notes from CHANGELOG.md
- [ ] PyPI trusted publishing configured
- [ ] TestPyPI trusted publishing configured
- [ ] GitHub environments created (pypi, testpypi)
- [ ] Package metadata enhanced in pyproject.toml
- [ ] Comprehensive classifiers added
- [ ] Project URLs configured
- [ ] Release documentation created (docs/RELEASING.md)
- [ ] CONTRIBUTING.md updated with release process
- [ ] CLAUDE.md updated with automation details
- [ ] Test release completed successfully
- [ ] Package installs correctly from PyPI
- [ ] Package version matches git tag

## Related Files

**New Files:**

- `.github/workflows/publish.yml` - GitHub Actions publish workflow
- `docs/RELEASING.md` - Release process documentation

**Modified Files:**

- `pyproject.toml` - Enhanced package metadata
- `CONTRIBUTING.md` - Add release process section
- `CLAUDE.md` - Document release automation
- `README.md` - Update badges (optional)

**External Configuration:**

- PyPI project settings (trusted publishing)
- TestPyPI project settings (trusted publishing)
- GitHub repository settings (environments)

## Dependencies

**Task Dependencies:**

- **Depends on**: refactoring/010-dynamic-versioning-from-git-tags (#222)
  - Automated publishing requires dynamic versioning
  - Git tags must be source of truth for version numbers
  - Must implement task #010 first

**Tool Dependencies:**

- `build` - Build package distributions
- `twine` - Upload packages and verify metadata
- `check-wheel-contents` - Verify wheel structure
- GitHub Actions (already available)
- PyPI/TestPyPI accounts (already exist)

**No Breaking Changes** - This is purely additive automation

## Additional Notes

### Package Distribution Formats

**Source Distribution (sdist):**

- Format: `.tar.gz`
- Contains: Source code, tests, docs, metadata
- Install: Requires build tools (pip, setuptools)
- Use case: Source installation, verification, archival

**Wheel Distribution:**

- Format: `.whl`
- Contains: Pre-built bytecode, metadata
- Install: Fast, no build required
- Use case: Standard installation method

**Both formats published** for maximum compatibility.

### PyPI vs TestPyPI

**TestPyPI:**

- URL: https://test.pypi.org/
- Purpose: Test releases before production
- Separate package index
- Can be wiped periodically
- Use for testing workflow

**PyPI:**

- URL: https://pypi.org/
- Purpose: Production package distribution
- Permanent package index
- Cannot delete versions (can yank)
- Use for official releases

### Trusted Publishing Benefits

**Traditional API Tokens:**

- ❌ Need to create and store tokens
- ❌ Tokens can leak in logs
- ❌ Manual rotation required
- ❌ Revocation is manual

**Trusted Publishing (OIDC):**

- ✅ No tokens to manage
- ✅ Automatic authentication via GitHub
- ✅ Short-lived credentials
- ✅ Bound to specific repository/workflow
- ✅ More secure

### Version Tagging Strategy

**Format**: `vMAJOR.MINOR.PATCH`

```bash
# Major release (breaking changes)
git tag v3.0.0

# Minor release (new features)
git tag v2.1.0

# Patch release (bug fixes)
git tag v2.0.1

# Pre-release
git tag v2.1.0rc1  # Release candidate
git tag v2.1.0b1   # Beta
git tag v2.1.0a1   # Alpha
```

**Tag Annotations:**

```bash
# Annotated tag (recommended)
git tag -a v2.1.0 -m "Release version 2.1.0"

# Lightweight tag (not recommended)
git tag v2.1.0
```

Use annotated tags for releases (includes author, date, message).

### CHANGELOG.md Format

Follow [Keep a Changelog](https://keepachangelog.com/):

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Feature X

## [2.0.0] - 2026-04-15

### Added
- New feature Y

### Changed
- Breaking change Z

### Fixed
- Bug fix A
```

### GitHub Release Notes

Automatically extracted from CHANGELOG.md using awk:

```bash
awk '/^## \[2.0.0\]/{flag=1; next} /^## \[/{flag=0} flag' CHANGELOG.md
```

Extracts content between version headers.

### Security Considerations

**Supply Chain Security:**

- ✅ Trusted publishing (no token leakage)
- ✅ Signed commits (GPG, optional)
- ✅ Reproducible builds (hatchling)
- ✅ Dependency pinning (uv.lock)
- ✅ Build verification (twine check)
- ✅ Multi-platform testing

**Best Practices:**

- Never commit API tokens
- Use trusted publishing instead of tokens
- Enable 2FA on PyPI account
- Protect version tags
- Review release artifacts before publishing

### Performance Considerations

**Build Time:**

- Source distribution build: ~5s
- Wheel distribution build: ~5s
- Verification: ~2s
- Total build phase: ~15s

**Publish Time:**

- TestPyPI upload: ~10s
- PyPI upload: ~10s
- GitHub release: ~5s
- Total publish phase: ~25s

**Full Workflow:**

- Build + verify: ~15s
- Installation testing: ~2-3 min (parallel)
- Publishing: ~25s
- Total: **3-4 minutes**

Much faster than manual process (15-30 minutes).

### Monitoring and Notifications

**GitHub Actions:**

- Workflow run notifications
- Failure alerts via email
- Status badges in README

**PyPI:**

- Download statistics
- Version analytics
- Security advisories

**Recommended Monitoring:**

```bash
# Watch workflow status
gh run list --workflow=publish.yml

# Check recent releases
gh release list

# Monitor PyPI downloads
pip install pypistats
pypistats recent nhl-scrabble
```

### Rollback Strategy

**If release fails during workflow:**

- Workflow stops automatically
- No partial publishes (atomic operations)
- Fix issue and re-push tag

**If release succeeds but has bugs:**

1. Cannot delete PyPI releases
1. Can "yank" release (discourages installation)
1. Publish hotfix version immediately
1. Update documentation

**Yank Release:**

```bash
# Via PyPI web interface only
# https://pypi.org/manage/project/nhl-scrabble/releases/
```

**Hotfix Release:**

```bash
git checkout v2.0.0
git checkout -b hotfix/2.0.1
# Fix bug
git commit -m "fix: Critical bug"
git tag v2.0.1
git push --tags
```

### Future Enhancements

After initial implementation:

- Add release signing (GPG)
- Add SBOM (Software Bill of Materials)
- Add provenance attestation
- Add security scanning in workflow
- Add automatic changelog generation
- Add release announcement automation
- Add conda-forge publishing
- Add Docker image publishing

### Breaking Changes

**None** - This is purely additive:

- No changes to package functionality
- No changes to existing release process
- Manual releases still possible
- Automated releases opt-in via tags

### Migration Notes

**First Automated Release:**

1. Implement this task completely
1. Test with pre-release version (v2.0.1rc1)
1. Verify all steps work
1. Create real release (v2.1.0)
1. Monitor and verify
1. Document any issues

**Existing PyPI Project:**

- Project already exists on PyPI
- No migration needed
- Just add trusted publishing
- Continue existing version sequence
