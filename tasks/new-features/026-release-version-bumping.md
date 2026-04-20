# Release Automation: Version Bumping Phase

**GitHub Issue**: #262 - https://github.com/bdperkin/nhl-scrabble/issues/262

**Parent Task**: #247 - Comprehensive Release Automation Skill (sub-task 2 of 7)

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

1-2 hours

## Description

Implement version bumping across multiple files (pyproject.toml, __init__.py) and automatic CHANGELOG.md generation from git commit history using conventional commits.

**Parent Task**: tasks/new-features/019-comprehensive-release-automation-skill.md (Phase 2)

## Proposed Solution

```python
def bump_version(new_version):
    """Phase 2: Version Bumping."""
    # Update pyproject.toml
    update_pyproject_version(new_version)

    # Update __init__.py
    update_init_version(new_version)

    # Generate changelog entry
    changelog_entry = generate_changelog_from_commits()
    update_changelog(new_version, changelog_entry)

    # Preview changes
    show_diff()

    # Confirm with user
    if not confirm("Proceed with version bump?"):
        raise ReleaseAborted()
```

## Acceptance Criteria

- [ ] pyproject.toml version update working
- [ ] __init__.py version update working
- [ ] CHANGELOG.md generation from commits working
- [ ] Conventional commit parsing implemented
- [ ] Preview and confirmation working
- [ ] Tests passing

## Dependencies

- **Parent**: #247
- **Prerequisite**: Sub-task 1 (Pre-Release Validation)

## Implementation Notes

*To be filled during implementation*
