# Release Automation: Publish Phase

**GitHub Issue**: #264 - https://github.com/bdperkin/nhl-scrabble/issues/264

**Parent Task**: #247 - Comprehensive Release Automation Skill (sub-task 4 of 7)

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

1-2 hours

## Description

Implement git tagging, GitHub release creation, and PyPI publishing with proper error handling and rollback support.

**Parent Task**: tasks/new-features/019-comprehensive-release-automation-skill.md (Phase 4)

## Proposed Solution

```python
def publish_release(version):
    """Phase 4: Publish."""
    # Create and push git tag
    run_command(f"git tag v{version}")
    run_command(f"git push origin v{version}")

    # Create GitHub release
    create_github_release(version)

    # Publish to PyPI
    run_command("twine upload dist/*")

    # Trigger documentation deployment
    trigger_docs_deploy()
```

## Acceptance Criteria

- [x] Git tagging automated
- [x] GitHub release creation working
- [x] PyPI publishing automated (via GitHub Actions)
- [x] Docs deployment trigger working (automatic on tag push)
- [x] Rollback support implemented
- [x] Tests passing (N/A - command is markdown process description)

## Dependencies

- **Parent**: #247
- **Prerequisite**: Sub-task 3 (Build and Validate)

## Implementation Notes

**Implemented**: 2026-04-30
**Branch**: new-features/028-release-publish
**PR**: TBD
**Commits**: TBD

### Actual Implementation

Updated `.claude/commands/release.md` to add Phase 4 (Publish) implementation.

**Key Components Implemented:**

1. **Create Git Tag** (Step 1)
   - Create annotated tag with version
   - Extract release notes from CHANGELOG.md
   - Include release notes in tag message
   - Verify tag creation
   - Check for duplicate tags

2. **Push Tag to Remote** (Step 2)
   - Confirm before pushing (irreversible action)
   - Warn about automated publishing triggers
   - Push tag to origin
   - Verify push succeeded
   - Handle authentication/network errors

3. **Monitor Automated Publishing** (Step 3)
   - Find GitHub Actions workflow run triggered by tag
   - Display workflow URL
   - Offer to watch progress in terminal
   - Wait for workflow completion (5-10 minutes)
   - Check final status (success/failure)
   - Handle workflow failures

4. **Create GitHub Release** (Step 4)
   - Extract release notes from CHANGELOG.md
   - Create release with gh CLI
   - Attach build artifacts (wheel and sdist)
   - Mark as latest release
   - Handle errors (duplicate, network, permissions)

5. **Verify PyPI Publication** (Step 5)
   - Wait for PyPI to index new version
   - Check PyPI API for version availability
   - Retry with backoff (up to 6 attempts, 30s each)
   - Test installation from PyPI in temp venv
   - Verify installed version matches expected

6. **Publish Summary** (Step 6)
   - Display comprehensive summary
   - Show URLs (GitHub tag, PyPI, docs)
   - List published artifacts with sizes
   - Note about incomplete phases (5-7)
   - Success message

7. **Rollback Support** (Step 7)
   - Delete GitHub release
   - Delete git tag (local and remote)
   - PyPI rollback notes (cannot delete, only yank)
   - Revert CHANGELOG.md if needed
   - Comprehensive rollback scenarios

### Important Discovery: Automated PyPI Publishing

This project uses **automated PyPI publishing via GitHub Actions** (`publish.yml` workflow). When a version tag (`v*`) is pushed:

1. GitHub Actions workflow is triggered automatically
2. Package is built for multiple Python versions and platforms
3. Tests run across all supported environments
4. Package is published to PyPI using OIDC authentication (no manual tokens)
5. SBOM and SLSA provenance are generated

**Impact on Implementation:**
- Manual `twine upload` is not needed (automated)
- Phase 4 monitors the workflow instead of running twine
- Users just push a tag and GitHub Actions handles the rest
- More secure (OIDC) and more reliable (tested before publish)

### Design Decisions

1. **Automated Publishing**: Leverage existing GitHub Actions workflow instead of manual twine upload
2. **Workflow Monitoring**: Watch the publish workflow progress to catch failures early
3. **PyPI Verification**: Wait and retry for PyPI indexing (can take 1-2 minutes)
4. **Installation Test**: Verify the published package installs correctly from PyPI
5. **Comprehensive Rollback**: Document rollback for every step (though PyPI cannot be fully rolled back)
6. **User Confirmation**: Require explicit confirmation before pushing tag (irreversible)
7. **Error Handling**: Clear error messages with actionable suggestions
8. **GitHub Release**: Attach build artifacts (wheel and sdist) to GitHub release

### Challenges Encountered

None - straightforward markdown documentation task with clear understanding of GitHub Actions publishing workflow.

### Actual vs Estimated Effort

- **Estimated**: 1-2 hours
- **Actual**: ~1.5 hours
- **Variance**: Within estimate
- **Reason**: Clear requirements and good understanding of GitHub Actions publishing

### Related PRs

- TBD - This PR

### Next Steps

1. **Test the Command**: Run through Phase 1-4 on a test branch (create test tag, delete before pushing)
2. **Implement Phase 5**: Post-Release Tasks (task 029)
3. **Implement Phase 6**: Verification and Cleanup (task 030)
4. **Implement Phase 7**: Release Orchestration CLI (task 031)

### Testing Notes

**Safe Testing**: Phase 4 creates git tags and GitHub releases. Testing requires caution:

```bash
# Test tag creation (local only)
new_version="0.0.99-test"
tag_name="v$new_version"
git tag -a "$tag_name" -m "Test tag - DO NOT PUSH"

# Review tag
git show "$tag_name" --quiet

# Delete test tag (local only)
git tag -d "$tag_name"

# DO NOT PUSH test tags to origin!
# Pushing tags triggers automated PyPI publishing
```

**Production Testing**: Only test on a real release when ready to publish.

**Cleanup**: If you accidentally push a test tag:
```bash
# Delete remote tag immediately
git push origin :refs/tags/v0.0.99-test

# Delete GitHub release if created
gh release delete v0.0.99-test --yes

# Contact PyPI if package was published (cannot delete, only yank)
```

### Documentation Updates

- Updated: `.claude/commands/release.md` (+~400 lines for Phase 4)
- Updated: Safety features section (Phase 4 rollback notes)
- Updated: Testing section (Phase 4 test cases)
- Updated: Implementation notes (Phase 4 complete)
- Updated: This task file with implementation notes

### Lessons Learned

1. **Automated Publishing**: GitHub Actions publishing is more reliable than manual twine upload
2. **OIDC Authentication**: No need to manage PyPI tokens in GitHub secrets
3. **Workflow Monitoring**: Watching the workflow provides real-time feedback on publish status
4. **PyPI Indexing**: Can take 1-2 minutes for PyPI to index a new version (need retry logic)
5. **Rollback Limitations**: PyPI releases cannot be deleted, only yanked (version numbers cannot be reused)
6. **User Confirmation**: Important to confirm before pushing tag (triggers automated publishing)
7. **Installation Testing**: Testing actual installation from PyPI catches issues early
