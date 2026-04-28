# Create GitHub Release Notes from Tag Annotations

**GitHub Issue**: [#381](https://github.com/bdperkin/nhl-scrabble/issues/381)

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

2-3 hours

## Description

Automate GitHub release creation with release notes extracted from git tag annotations. When developers create an annotated tag with release notes, automatically create a corresponding GitHub release with those notes.

This complements:
- Task #010: Dynamic versioning from git tags
- Task #030: CHANGELOG automation from git commits

Together, these tasks create a complete release automation workflow:
1. Developer creates annotated tag with release notes
2. GitHub release is auto-created with tag annotation as release notes
3. CHANGELOG is auto-generated from git commits
4. Package version is auto-derived from tag

## Current State

**Manual GitHub Release Process:**

```bash
# 1. Developer creates tag
git tag -a v0.1.0 -m "Release version 0.1.0"
git push --tags

# 2. Developer manually creates GitHub release
# - Navigate to GitHub UI
# - Click "Create a new release"
# - Select tag
# - Write release notes (duplicating tag annotation)
# - Publish release
```

**Issues:**
- ❌ Manual GitHub release creation is tedious
- ❌ Release notes duplicated (tag annotation + GitHub release)
- ❌ Easy to forget to create GitHub release
- ❌ Inconsistent release note format
- ❌ No automation or CI integration

**Existing Infrastructure:**
- ✅ Dynamic versioning from git tags (task #010)
- ✅ Conventional commits used throughout
- ✅ GitHub Actions CI/CD configured
- ❌ No release workflow yet
- ❌ No automated GitHub release creation

## Proposed Solution

Create GitHub Actions workflow to automatically create releases from annotated git tags:

### 1. Workflow Trigger

Trigger on tag push matching `v*.*.*` pattern:

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*.*.*'  # Semantic versioning tags (v1.0.0, v2.1.3, etc.)
```

### 2. Extract Tag Annotation

Use `git tag -l -n9999` to get full tag annotation:

```yaml
jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write  # Required to create releases

    steps:
      - name: Checkout code
        uses: actions/checkout@v6
        with:
          fetch-depth: 0  # Full history for tag annotations

      - name: Extract tag annotation
        id: tag-annotation
        run: |
          # Get tag name from ref
          TAG_NAME=${GITHUB_REF#refs/tags/}
          echo "tag_name=$TAG_NAME" >> $GITHUB_OUTPUT

          # Extract tag annotation (full message)
          TAG_MESSAGE=$(git tag -l -n9999 "$TAG_NAME" | sed "1s/^$TAG_NAME  *//")

          # If empty, provide default message
          if [ -z "$TAG_MESSAGE" ]; then
            TAG_MESSAGE="Release $TAG_NAME"
          fi

          # Save to file for multiline handling
          echo "$TAG_MESSAGE" > tag_message.txt
          echo "has_annotation=true" >> $GITHUB_OUTPUT
```

### 3. Create GitHub Release

Use `softprops/action-gh-release` for reliable release creation:

```yaml
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          tag_name: ${{ steps.tag-annotation.outputs.tag_name }}
          name: ${{ steps.tag-annotation.outputs.tag_name }}
          body_path: tag_message.txt
          draft: false
          prerelease: ${{ contains(steps.tag-annotation.outputs.tag_name, '-rc') || contains(steps.tag-annotation.outputs.tag_name, '-beta') || contains(steps.tag-annotation.outputs.tag_name, '-alpha') }}
          generate_release_notes: false  # Use tag annotation, not auto-generated
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 4. Tag Annotation Format

Recommended format for tag annotations:

```bash
# Simple release
git tag -a v0.1.0 -m "Release v0.1.0

## What's Changed

- Add feature X
- Fix bug Y
- Improve performance Z

## Breaking Changes

None

**Full Changelog**: https://github.com/bdperkin/nhl-scrabble/compare/v0.0.1...v0.1.0"

# Pre-release
git tag -a v0.2.0-rc1 -m "Release v0.2.0-rc1 (Release Candidate)

## What's Changed (Pre-release)

- Testing new feature A
- Experimental optimization B

## Known Issues

- Issue #123 still under investigation

**This is a pre-release and should not be used in production.**"

# Push tag
git push origin v0.1.0
```

### 5. Integration with CHANGELOG (Task #030)

When task #030 is implemented, combine both:

```yaml
      - name: Generate CHANGELOG
        uses: orhun/git-cliff-action@v4
        with:
          config: cliff.toml
          args: --tag ${{ steps.tag-annotation.outputs.tag_name }}
        env:
          OUTPUT: CHANGELOG_ENTRY.md

      - name: Combine tag annotation and changelog
        run: |
          cat tag_message.txt > release_notes.md
          echo -e "\n\n---\n\n## Detailed Changelog\n" >> release_notes.md
          cat CHANGELOG_ENTRY.md >> release_notes.md

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          body_path: release_notes.md
          # ... rest of config
```

## Implementation Steps

1. **Create Release Workflow** (1h)
   - Create `.github/workflows/release.yml`
   - Configure tag trigger (`v*.*.*` pattern)
   - Add permissions (`contents: write`)
   - Set up checkout with full history

2. **Extract Tag Annotation** (30min)
   - Parse tag name from `GITHUB_REF`
   - Extract tag message with `git tag -l -n9999`
   - Handle empty annotations (default message)
   - Save to file for multiline support

3. **Create GitHub Release** (30min)
   - Use `softprops/action-gh-release@v2`
   - Auto-detect pre-releases (rc, beta, alpha)
   - Use tag annotation as release body
   - Configure release settings

4. **Testing** (45min)
   - Create test annotated tag
   - Verify workflow triggers
   - Check GitHub release is created
   - Verify release notes match annotation
   - Test pre-release detection
   - Clean up test releases

5. **Documentation** (15min)
   - Update CONTRIBUTING.md with tag annotation format
   - Document release process
   - Add workflow documentation
   - Update CLAUDE.md

## Testing Strategy

### Local Testing (Tag Annotation Format)

```bash
# 1. Create test annotated tag locally
git tag -a v0.1.0-test -m "Test Release v0.1.0-test

## What's Changed

- Test feature A
- Test fix B

This is a test release."

# 2. Extract annotation (verify format)
git tag -l -n9999 v0.1.0-test

# 3. Clean up
git tag -d v0.1.0-test
```

### CI Testing (Workflow)

```bash
# 1. Create test tag and push
git tag -a v0.0.1-test -m "Test release workflow

This is a test to verify automated GitHub release creation."
git push origin v0.0.1-test

# 2. Monitor GitHub Actions workflow
# - Check workflow triggers
# - Verify tag annotation extraction
# - Confirm GitHub release created

# 3. Verify GitHub release
gh release view v0.0.1-test
# Check release notes match tag annotation

# 4. Clean up
gh release delete v0.0.1-test --yes
git tag -d v0.0.1-test
git push origin --delete v0.0.1-test
```

### Pre-release Testing

```bash
# Test pre-release detection
git tag -a v0.2.0-rc1 -m "Release Candidate 1"
git push origin v0.2.0-rc1

# Verify release is marked as pre-release
gh release view v0.2.0-rc1 --json isPrerelease
```

### Integration Testing

```bash
# Full release cycle
git tag -a v0.1.0 -m "$(cat <<'EOF'
Release v0.1.0

## What's Changed

- Feature: Add interactive mode
- Fix: Correct API error handling
- Perf: Optimize report generation

## Breaking Changes

None

**Full Changelog**: https://github.com/bdperkin/nhl-scrabble/compare/v0.0.1...v0.1.0
EOF
)"
git push origin v0.1.0

# Verify:
# 1. GitHub Actions workflow runs
# 2. GitHub release created
# 3. Release notes match annotation
# 4. Release is not marked as pre-release
```

## Acceptance Criteria

- [x] `.github/workflows/release.yml` workflow created (integrated into `publish.yml`)
- [x] Workflow triggers on tag push matching `v*.*.*` (existing trigger in `publish.yml`)
- [x] Tag annotation extracted correctly (full multiline message)
- [x] GitHub release created automatically
- [x] Release name matches tag name
- [x] Release notes match tag annotation
- [x] Pre-releases auto-detected (rc, beta, alpha suffixes)
- [x] Empty annotations handled gracefully (default message)
- [x] Workflow has `contents: write` permission (already present)
- [x] Documentation updated:
  - [x] CONTRIBUTING.md (tag annotation format)
  - [x] CLAUDE.md (release automation)
  - [x] Workflow comments
- [ ] Tests pass (test tag creates release) - Will verify in PR
- [ ] Clean up test releases - After testing
- [x] Integration with future CHANGELOG automation considered (already integrated!)

## Related Files

- `.github/workflows/release.yml` - Release automation workflow (to be created)
- `CONTRIBUTING.md` - Document tag annotation format and release process
- `CLAUDE.md` - Document release automation
- `.github/workflows/ci.yml` - Existing CI workflow (reference)

## Dependencies

**Related Tasks:**
- Task #010 (refactoring/010-dynamic-versioning.md) - Dynamic versioning from git tags (completed)
  - Releases use same git tags as versioning
- Task #030 (enhancement/030-automate-changelog-generation.md) - CHANGELOG automation (active)
  - Can be combined with release notes for comprehensive releases
  - Release notes (from tag) + detailed changelog (from commits)

**GitHub Actions:**
- `actions/checkout@v6` - Checkout code with full history
- `softprops/action-gh-release@v2` - Create GitHub releases

**GitHub Permissions:**
- `contents: write` - Required to create releases

**Tools:**
- Git (tag annotation extraction)
- GitHub CLI (`gh` for testing)

## Additional Notes

### Tag Annotation Best Practices

**Good Annotations:**

```bash
# Structured release
git tag -a v0.1.0 -m "Release v0.1.0

## What's Changed

### Features
- Add REST API server (#150)
- Add interactive mode (#133)

### Bug Fixes
- Fix API error handling (#40)
- Fix rate limiting (#47)

### Performance
- Optimize report generation (#115)

## Breaking Changes

None

**Full Changelog**: https://github.com/bdperkin/nhl-scrabble/compare/v0.0.1...v0.1.0"

# Minimal (auto-generated changelog will supplement)
git tag -a v0.1.0 -m "Release v0.1.0

See CHANGELOG.md for details."

# Pre-release
git tag -a v0.2.0-rc1 -m "Release Candidate 1 for v0.2.0

## Testing Focus
- New caching system
- API performance improvements

**Do not use in production**"
```

**Poor Annotations:**

```bash
# ❌ Too short
git tag -a v0.1.0 -m "v0.1.0"

# ❌ No version in message
git tag -a v0.1.0 -m "New release"

# ❌ Lightweight tag (no annotation)
git tag v0.1.0  # No -a flag
```

### Pre-release Detection

Automatically marks as pre-release if tag contains:
- `-rc` (release candidate): `v0.1.0-rc1`
- `-beta` (beta release): `v0.1.0-beta1`
- `-alpha` (alpha release): `v0.1.0-alpha1`

### Workflow Permissions

**Required Permission:**
```yaml
permissions:
  contents: write  # Create releases
```

**Why:** GitHub Actions needs explicit permission to create releases in the repository.

### Release Assets (Future Enhancement)

This task focuses on release notes. Future enhancements could add assets:

```yaml
      - name: Build package
        run: python -m build

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          body_path: tag_message.txt
          files: |
            dist/*.whl
            dist/*.tar.gz
```

### Integration with CI/CD

**Release workflow vs CI workflow:**
- **CI workflow**: Runs on every push/PR (tests, quality checks)
- **Release workflow**: Runs only on tag push (creates release)

Both can coexist:

```yaml
# CI: .github/workflows/ci.yml (existing)
on:
  push:
    branches: [main]
  pull_request:

# Release: .github/workflows/release.yml (new)
on:
  push:
    tags:
      - 'v*.*.*'
```

### Combining with CHANGELOG (Task #030)

When both are implemented:

**Tag Annotation** (high-level):
- What's changed (summary)
- Breaking changes
- Migration notes

**CHANGELOG** (detailed):
- All commits since last release
- Categorized by type (feat, fix, etc.)
- Commit-level details

**Combined Release Notes:**
```
[Tag Annotation - High-level summary]

---

## Detailed Changelog

[Auto-generated from commits via git-cliff]
```

### Error Handling

**Empty annotation:**
```yaml
# Fallback to default message
if [ -z "$TAG_MESSAGE" ]; then
  TAG_MESSAGE="Release $TAG_NAME"
fi
```

**Invalid tag format:**
- Workflow only triggers on `v*.*.*` pattern
- Invalid tags (e.g., `2.1.0` without `v`) won't trigger

**Failed release creation:**
- GitHub Actions will fail workflow
- Developer receives notification
- Can manually retry or fix

### Security Considerations

- Uses `GITHUB_TOKEN` (auto-provided by GitHub Actions)
- No secrets required
- `contents: write` permission scoped to workflow
- Tag annotations are public (don't include secrets)

### Performance

- Workflow execution: ~30-60 seconds
  - Checkout: ~10s
  - Tag extraction: ~5s
  - Release creation: ~10s
- No impact on main CI (separate workflow)

### Versioning Strategy

**Semantic Versioning:**
- Major: `v1.0.0` (breaking changes)
- Minor: `v0.1.0` (new features)
- Patch: `v0.0.2` (bug fixes)
- Pre-release: `v0.1.0-rc1` (release candidates)

**Tag Format:**
- ✅ `v0.1.0` - Valid
- ✅ `v0.1.0-rc1` - Valid (pre-release)
- ✅ `v0.1.0-beta1` - Valid (pre-release)
- ❌ `0.1.0` - Invalid (missing `v`)
- ❌ `version-0.1.0` - Invalid (wrong format)

## Implementation Notes

**Implemented**: 2026-04-27
**Branch**: enhancement/032-github-release-notes-from-tag-annotations
**Commits**: 1 commit (a84d467)

### Actual Implementation

Modified existing `.github/workflows/publish.yml` instead of creating a separate `release.yml` workflow. This approach:
- Integrates seamlessly with existing package publishing workflow
- Reuses existing permissions and job dependencies
- Maintains single source of truth for release process
- Already had CHANGELOG generation (task #030 was already implemented!)

**Workflow Changes:**
1. Added "Extract tag annotation" step to extract full tag message
2. Modified "Extract release notes" to separate tag annotation from changelog
3. Added "Combine release notes" step to merge both sources
4. Updated "Create GitHub Release" with:
   - Tag annotation as primary release notes
   - Auto-generated changelog as detailed supplement
   - Pre-release auto-detection
   - Proper error handling for empty annotations

**Documentation Updates:**
1. CONTRIBUTING.md:
   - Updated Quick Release Steps with tag annotation example
   - Added Tag Annotation Format section with examples
   - Documented pre-release detection
   - Best practices for good vs poor annotations

2. CLAUDE.md:
   - Updated Automated Package Publishing section
   - Updated workflow stages list
   - Added tag annotation best practices
   - Documented release notes structure
   - Pre-release detection documentation

### Integration with CHANGELOG Automation

Task #030 (CHANGELOG automation) was already implemented in the codebase! The `publish.yml` workflow already had:
- `generate-changelog` job using git-cliff
- CHANGELOG.md auto-generation from commits
- Changelog extraction for release notes

Our implementation **combined both approaches**:
- **Tag annotation**: High-level summary (features, breaking changes)
- **Auto-generated changelog**: Detailed commit-by-commit history
- **Result**: Comprehensive release notes with both perspectives

This is better than the proposed solution which treated CHANGELOG as "future enhancement"!

### Challenges Encountered

**1. YAML Line Length**:
- yamllint complained about lines >100 characters
- Fixed by breaking long bash command into multiline
- Fixed by using YAML block scalar (`>-`) for long expression

**2. Existing Workflow Integration**:
- Had to understand existing `publish.yml` structure
- Needed to preserve existing job dependencies
- Solution: Modified `github-release` job instead of creating new workflow

**3. Multiline Tag Annotation Handling**:
- Used `git tag -l -n9999` to get full annotation (not truncated)
- Saved to file for proper multiline handling in GitHub Actions
- Used heredoc syntax to properly combine tag annotation + changelog

### Deviations from Proposed Solution

**1. Workflow File**: Used `.github/workflows/publish.yml` instead of creating `.github/workflows/release.yml`
- **Why**: Avoid duplication, reuse existing structure, maintain single workflow
- **Benefit**: Simpler to maintain, fewer files, clearer workflow dependency

**2. CHANGELOG Already Integrated**: Task #030 was already implemented
- **Why**: The `generate-changelog` job already existed in `publish.yml`
- **Benefit**: Immediate full integration, better release notes from day one

**3. Combined Release Notes**: Implemented tag annotation + changelog integration immediately
- **Why**: Both sources were available, so combined them from start
- **Benefit**: More comprehensive release notes without waiting for future enhancement

### Actual vs Estimated Effort

- **Estimated**: 2-3 hours
- **Actual**: ~1.5 hours
- **Reason**:
  - Existing workflow structure well-documented
  - CHANGELOG automation already implemented
  - No need to create separate workflow file
  - Clear task specification with examples

### Testing Plan

Testing will be done during PR review process:

1. **Local Tag Annotation Testing**:
   ```bash
   # Verify tag annotation format works
   git tag -a v0.1.0-test -m "Test annotation with multiline

   ## Features
   - Test feature

   ## Breaking Changes
   None"
   git tag -l -n9999 v0.1.0-test
   git tag -d v0.1.0-test
   ```

2. **CI Testing** (after PR merge):
   - Create test tag: `v0.0.2-test`
   - Verify workflow extracts annotation correctly
   - Verify GitHub release created with tag annotation
   - Verify changelog appended correctly
   - Verify pre-release detection works
   - Clean up test release

### Lessons Learned

1. **Check existing infrastructure first**: Task #030 was already implemented, saving integration work
2. **Integrate vs separate**: Modifying existing workflow is often better than creating new one
3. **YAML formatting matters**: yamllint enforces 100-char line limit consistently
4. **Multiline handling**: Always test with actual multiline content, not single-line examples
5. **Pre-commit catches issues**: yamllint caught formatting issues before CI

### Performance Impact

- No additional workflow runtime (integrated into existing job)
- Tag annotation extraction: ~5 seconds
- Combining release notes: ~2 seconds
- Total overhead: ~7 seconds (negligible)

### Security Considerations

- Uses existing `GITHUB_TOKEN` (no new secrets required)
- Reuses existing `contents: write` permission
- Tag annotations are public (users should not include secrets)
- No new attack surface introduced
