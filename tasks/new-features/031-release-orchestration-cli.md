# Release Automation: Orchestration and CLI Interface

**GitHub Issue**: #267 - https://github.com/bdperkin/nhl-scrabble/issues/267

**Parent Task**: #247 - Comprehensive Release Automation Skill (sub-task 7 of 7)

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

2-3 hours

## Description

Implement the /release command orchestration, CLI interface with options (--version, --type, --dry-run), progress tracking, state saving for rollback, and comprehensive error handling.

**Parent Task**: tasks/new-features/019-comprehensive-release-automation-skill.md (Final phase - orchestration)

## Proposed Solution

```python
@click.command()
@click.option('--version', help='Explicit version number')
@click.option('--type', type=click.Choice(['major', 'minor', 'patch']),
              help='Version bump type')
@click.option('--dry-run', is_flag=True, help='Preview without executing')
@click.option('--skip-tests', is_flag=True, help='Skip test execution')
@click.option('--skip-pypi', is_flag=True, help='Skip PyPI publishing')
def release(version, type, dry_run, skip_tests, skip_pypi):
    """Automate the complete release process."""
    try:
        # Save state for rollback
        save_release_state()

        # Execute phases
        with progress_tracker() as progress:
            progress.add_task("Pre-Release Validation", total=5)
            new_version = validate_pre_release()

            progress.add_task("Version Bumping", total=3)
            bump_version(new_version)

            # ... execute all 7 phases

        display_success(new_version)

    except ReleaseError as e:
        handle_release_error(e)
        offer_rollback()
```

## Acceptance Criteria

- [ ] /release command interface implemented
- [ ] All options working (--version, --type, --dry-run, etc.)
- [ ] Progress tracking working
- [ ] State saving for rollback implemented
- [ ] All 7 phases orchestrated correctly
- [ ] Error handling comprehensive
- [ ] Rollback support working
- [ ] Tests passing
- [ ] Documentation complete

## Dependencies

- **Parent**: #247
- **Prerequisites**: All other sub-tasks (1-6)

## Implementation Notes

*To be filled during implementation*
