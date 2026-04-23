# GitHub Release Automation Workflow

**GitHub Issue**: #300 - https://github.com/bdperkin/nhl-scrabble/issues/300

**Parent Task**: enhancement/022-comprehensive-github-workflows.md (#298)

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

2-3 hours

## Description

Implement automated GitHub Release creation workflow that extracts release notes from CHANGELOG.md, generates release summary, and attaches build artifacts when version tags are pushed. This ensures consistent, professional release documentation.

## Current State

**Manual Release Creation:**

Currently, GitHub Releases are created manually after PyPI publishing:

```bash
# Current manual process
1. Push version tag
2. Wait for PyPI publish to complete
3. Go to GitHub web interface
4. Click "Create new release"
5. Select tag
6. Copy/paste from CHANGELOG.md
7. Upload distribution files manually
8. Click "Publish release"
```

**Problems:**

- ❌ Manual, time-consuming process
- ❌ Inconsistent release note formatting
- ❌ Easy to forget to attach artifacts
- ❌ No automated verification
- ❌ Release notes may not match CHANGELOG

**Existing:**

- ✅ CHANGELOG.md maintained
- ✅ Version tags created
- ✅ Build artifacts generated
- ❌ No automated release creation
- ❌ No release note extraction

## Proposed Solution

### Automated Release Workflow

Note: This workflow is **integrated into** the PyPI publishing workflow (task #032) as a final step. This task documents the GitHub release creation portion specifically.

**Workflow Integration:**

```yaml
# Part of .github/workflows/publish.yml
jobs:
  # ... build and publish jobs ...

  github-release:
    name: Create GitHub Release
    needs: publish-pypi  # Run after PyPI publish succeeds
    runs-on: ubuntu-latest

    permissions:
      contents: write  # Required to create releases

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
        run: |
          echo "VERSION=${GITHUB_REF#refs/tags/v}" >> $GITHUB_OUTPUT
          echo "TAG=${GITHUB_REF#refs/tags/}" >> $GITHUB_OUTPUT

      - name: Extract release notes from CHANGELOG
        id: extract_notes
        run: |
          # Extract version section from CHANGELOG.md
          echo "Extracting release notes for version ${{ steps.get_version.outputs.VERSION }}"

          if [ -f CHANGELOG.md ]; then
            awk '/^## \[${{ steps.get_version.outputs.VERSION }}\]/{flag=1; next} /^## \[/{flag=0} flag' CHANGELOG.md > release_notes.md

            if [ ! -s release_notes.md ]; then
              echo "⚠️ No release notes found in CHANGELOG.md for version ${{ steps.get_version.outputs.VERSION }}" > release_notes.md
              echo "" >> release_notes.md
              echo "See [CHANGELOG.md](https://github.com/${{ github.repository }}/blob/main/CHANGELOG.md) for details." >> release_notes.md
            fi
          else
            echo "Release ${{ steps.get_version.outputs.TAG }}" > release_notes.md
          fi

          echo "Release notes:"
          cat release_notes.md

      - name: Generate release summary
        id: summary
        run: |
          {
            echo "## 📦 Distribution Files"
            echo ""
            echo "This release includes:"
            echo ""
            for file in dist/*; do
              filename=$(basename "$file")
              size=$(ls -lh "$file" | awk '{print $5}')
              echo "- \`$filename\` ($size)"
            done
            echo ""
            echo "## 📥 Installation"
            echo ""
            echo "\`\`\`bash"
            echo "# Install from PyPI"
            echo "pip install nhl-scrabble==${{ steps.get_version.outputs.VERSION }}"
            echo ""
            echo "# Upgrade existing installation"
            echo "pip install --upgrade nhl-scrabble"
            echo "\`\`\`"
            echo ""
            echo "## 📚 Documentation"
            echo ""
            echo "- [Documentation](https://bdperkin.github.io/nhl-scrabble/)"
            echo "- [CHANGELOG](https://github.com/${{ github.repository }}/blob/main/CHANGELOG.md)"
            echo "- [PyPI Package](https://pypi.org/project/nhl-scrabble/${{ steps.get_version.outputs.VERSION }}/)"
          } > summary.md

      - name: Combine release notes and summary
        run: |
          {
            cat release_notes.md
            echo ""
            echo "---"
            echo ""
            cat summary.md
          } > final_release_notes.md

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          files: dist/*
          body_path: final_release_notes.md
          draft: false
          prerelease: ${{ contains(github.ref, 'rc') || contains(github.ref, 
            'beta') || contains(github.ref, 'alpha') }}
          generate_release_notes: false  # We provide our own
          fail_on_unmatched_files: true
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Verify release created
        run: |
          sleep 5  # Wait for release to be created
          gh release view ${{ steps.get_version.outputs.TAG }} || exit 1
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### CHANGELOG.md Format

Ensure CHANGELOG.md follows the standard format:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Feature X in progress

## [2.1.0] - 2026-04-22

### Added
- New PyPI publishing workflow (#298)
- Automated GitHub releases

### Changed
- Improved release process documentation

### Fixed
- Release note extraction from CHANGELOG

## [2.0.0] - 2026-04-15

### Added
- Major feature Y
```

### Pre-Release Detection

The workflow automatically detects pre-releases:

```yaml
prerelease: ${{ contains(github.ref, 'rc') || contains(github.ref, 'beta') || 
  contains(github.ref, 'alpha') }}
```

**Examples:**

- `v2.1.0` → Regular release
- `v2.1.0rc1` → Pre-release (release candidate)
- `v2.1.0b1` → Pre-release (beta)
- `v2.1.0a1` → Pre-release (alpha)

## Implementation Steps

1. **Integrate into Publish Workflow** (30min)

   - Add `github-release` job to `publish.yml`
   - Configure job dependencies
   - Set proper permissions

1. **Implement Release Note Extraction** (1h)

   - Add version extraction step
   - Add CHANGELOG parsing logic
   - Add fallback handling
   - Add verification

1. **Implement Release Summary Generation** (30min)

   - Generate artifact list
   - Add installation instructions
   - Add documentation links
   - Combine with release notes

1. **Configure Release Action** (30min)

   - Set up artifact uploads
   - Configure pre-release detection
   - Set release options
   - Add verification step

1. **Test Release Creation** (30min-1h)

   - Create test tag
   - Verify release created
   - Verify artifacts attached
   - Verify release notes formatted correctly
   - Clean up test release

1. **Update Documentation** (15min)

   - Update RELEASING.md
   - Add CHANGELOG format requirements
   - Document release process

## Testing Strategy

### CHANGELOG Format Testing

```bash
# Create test CHANGELOG entry
cat >> CHANGELOG.md << 'EOF'

## [0.0.1-test] - 2026-04-22

### Added
- Test release workflow

### Fixed
- Release note extraction
EOF

# Test extraction
awk '/^## \[0.0.1-test\]/{flag=1; next} /^## \[/{flag=0} flag' CHANGELOG.md
```

### Release Creation Testing

```bash
# Create test tag
git tag v0.0.1-test
git push origin v0.0.1-test

# Monitor workflow
gh run list --workflow=publish.yml
gh run watch

# Verify release created
gh release view v0.0.1-test

# Check release content
gh release view v0.0.1-test --json body --jq .body

# Check attached files
gh release view v0.0.1-test --json assets --jq '.assets[].name'

# Clean up
gh release delete v0.0.1-test --yes
git tag -d v0.0.1-test
git push origin :refs/tags/v0.0.1-test
```

### Pre-Release Testing

```bash
# Test pre-release detection
git tag v0.0.1-rc1
git push origin v0.0.1-rc1

# Verify marked as pre-release
gh release view v0.0.1-rc1 --json isPrerelease --jq .isPrerelease
# Should output: true
```

## Acceptance Criteria

- [ ] GitHub release job integrated into publish workflow
- [ ] Release created automatically on version tags
- [ ] Release notes extracted from CHANGELOG.md
- [ ] Release summary generated with artifacts
- [ ] Installation instructions included
- [ ] Documentation links included
- [ ] Distribution files attached
- [ ] Pre-release detection working
- [ ] Fallback handling for missing CHANGELOG entries
- [ ] Release verification step included
- [ ] RELEASING.md updated with CHANGELOG format
- [ ] Test release created successfully
- [ ] Release formatting matches expectations

## Related Files

**Modified Files:**

- `.github/workflows/publish.yml` - Add github-release job
- `docs/RELEASING.md` - Document CHANGELOG format
- `CHANGELOG.md` - Ensure proper formatting

**No New Files:**

- This is integrated into the publish workflow

## Dependencies

**Task Dependencies:**

- **Integrated with**: new-features/032-pypi-publish-workflow
  - This is a job within the publish workflow
  - Runs after PyPI publish succeeds

**Tool Dependencies:**

- `softprops/action-gh-release@v2` - GitHub Action for releases
- `gh` CLI - For verification
- `awk` - For CHANGELOG parsing

## Additional Notes

### Release Note Extraction Logic

The workflow uses `awk` to extract version-specific content:

```bash
awk '/^## \[2.1.0\]/{flag=1; next} /^## \[/{flag=0} flag' CHANGELOG.md
```

**How it works:**

1. Finds line starting with `## [2.1.0]`
1. Sets flag to start capturing
1. Captures all lines until next `## [` header
1. Outputs captured lines

### Release Structure

**Generated Release:**

````
## 📋 Release Notes (from CHANGELOG)

### Added
- New feature X

### Fixed
- Bug Y

---

## 📦 Distribution Files

- `nhl_scrabble-2.1.0.tar.gz` (45K)
- `nhl_scrabble-2.1.0-py3-none-any.whl` (32K)

## 📥 Installation

```bash
pip install nhl-scrabble==2.1.0
````

## 📚 Documentation

- [Documentation](...)
- [CHANGELOG](...)
- [PyPI Package](...)

````

### Error Handling

**Missing CHANGELOG Entry:**
```markdown
⚠️ No release notes found in CHANGELOG.md for version 2.1.0

See [CHANGELOG.md](...) for details.
````

**Missing CHANGELOG File:**

```markdown
Release v2.1.0
```

### Best Practices

**CHANGELOG Maintenance:**

1. Update CHANGELOG.md with every PR
1. Add entries to `[Unreleased]` section
1. Before release: move entries to version section
1. Follow Keep a Changelog format
1. Use consistent section headers (Added, Changed, Fixed, etc.)

**Version Section Format:**

```markdown
## [2.1.0] - 2026-04-22

### Added
- Item 1
- Item 2

### Changed
- Item 3

### Fixed
- Item 4
```

### Automation Benefits

**Before:**

- Manual release creation: 5-10 minutes
- Inconsistent formatting
- Easy to forget artifacts
- Manual CHANGELOG copying

**After:**

- Automatic release creation: ~10 seconds
- Consistent formatting
- All artifacts attached
- Automatic CHANGELOG extraction

## Implementation Notes

*To be filled during implementation:*

- Date started:
- Date completed:
- Actual effort:
- Challenges encountered:
- CHANGELOG parsing issues (if any):
- First automated release:
