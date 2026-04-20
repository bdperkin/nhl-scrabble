# Release Automation: Build and Validate Phase

**GitHub Issue**: #263 - https://github.com/bdperkin/nhl-scrabble/issues/263

**Parent Task**: #247 - Comprehensive Release Automation Skill (sub-task 3 of 7)

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

1-2 hours

## Description

Implement package building (wheel and sdist), validation with twine, and test installation in an isolated environment to ensure the package is publishable.

**Parent Task**: tasks/new-features/019-comprehensive-release-automation-skill.md (Phase 3)

## Proposed Solution

```python
def build_and_validate():
    """Phase 3: Build and Validate."""
    # Build packages
    run_command("python -m build")

    # Validate with twine
    run_command("twine check dist/*")

    # Test install in isolated venv
    with temp_venv() as venv:
        venv.install_from_wheel("dist/*.whl")
        venv.run("nhl-scrabble --version")

    # Verify metadata
    validate_package_metadata()
```

## Acceptance Criteria

- [ ] Build command automation working
- [ ] Twine check integrated
- [ ] Isolated installation test working
- [ ] Metadata validation implemented
- [ ] Tests passing

## Dependencies

- **Parent**: #247
- **Prerequisite**: Sub-task 2 (Version Bumping)

## Implementation Notes

*To be filled during implementation*
