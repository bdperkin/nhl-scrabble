# Release Process

For maintainers only.

## Pre-Release Package Validation

Before creating a release, validate the package:

```bash
# Build and validate package
make package

# Or run individual steps:
make build          # Build wheel and sdist
make check-wheel    # Validate wheel contents
```

This runs comprehensive package validation:

- **Build**: Creates wheel and source distribution
- **check-wheel-contents**: Validates wheel structure
  - ✅ LICENSE included
  - ✅ README metadata present
  - ✅ No test files
  - ✅ No `__pycache__` or `.pyc` files
  - ✅ Correct package structure
- **twine check**: Validates package metadata for PyPI

### Common Issues

- Missing LICENSE: Ensure `LICENSE` file exists in root
- Test files in wheel: Check `.gitignore` and `pyproject.toml` excludes
- `__pycache__` in wheel: Run `make clean` before building

## Release Steps

**Note:** This project uses **dynamic versioning** from Git tags via [hatch-vcs](https://github.com/ofek/hatch-vcs). Version numbers are automatically determined from Git tags—no manual version updates needed!

### 1. Update Changelog

- Update `CHANGELOG.md` with release notes
- Document all changes since last release

### 2. Ensure Clean State

```bash
git checkout main
git pull origin main
make test  # Ensure all tests pass
```

### 3. Validate Package

```bash
make package  # Build and validate
```

### 4. Create Git Tag (This sets the version!)

```bash
# Tag format: vX.Y.Z (Semantic Versioning)
git tag -a v2.1.0 -m "Release v2.1.0"

# The tag becomes the package version automatically
# v2.1.0 → Package version 2.1.0
# v2.1.0-rc1 → Package version 2.1.0rc1
```

### 5. Push Tag

```bash
git push --tags  # Triggers CI/CD release workflow
```

### 6. Create GitHub Release

- Create release from tag with changelog notes

### 7. Publish to PyPI (Optional)

```bash
# Test on TestPyPI first
make publish-test

# Verify installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ nhl-scrabble

# If successful, publish to PyPI
make publish
```

## Package Validation in CI

The package validation workflow runs automatically on:

- All pull requests to `main`
- All pushes to `main`
- All release tags (`v*`)

### The workflow

1. Builds wheel and source distribution
1. Validates with `check-wheel-contents`
1. Validates with `twine check`
1. Verifies LICENSE is included
1. Verifies no test files in wheel
1. Verifies no `__pycache__` in wheel
1. Uploads artifacts (wheel and sdist)

### CI Failure Troubleshooting

If package validation fails in CI:

1. Check the workflow logs for specific errors
1. Run `make package` locally to reproduce
1. Fix identified issues
1. Commit and push changes
1. CI will re-run validation
