# Updating Dependencies

We keep dependencies up-to-date for security and features.

## Automated Dependency Management

The project includes an automated dependency update script at `scripts/update_dependencies.py`.

### Quick Start

```bash
# Check for available updates
make deps-check

# Apply updates (with tests)
make deps-update

# Apply updates with full tox validation
make deps-update-full
```

### Manual Usage

```bash
# Check for updates (dry run)
python scripts/update_dependencies.py --check

# Apply updates interactively
python scripts/update_dependencies.py --apply

# Apply with test validation
python scripts/update_dependencies.py --apply --test

# Apply with full tox validation
python scripts/update_dependencies.py --apply --test --tox
```

## What Gets Updated

The script updates:

- **Pre-commit hooks**: Updates all hooks in `.pre-commit-config.yaml` to latest stable versions
- **Python packages**: Updates packages in `uv.lock` to latest compatible versions

## Update Process

1. **Check**: Script scans for available updates
1. **Report**: Displays available updates with version changes
1. **Confirm**: Asks for confirmation before applying
1. **Apply**: Updates configurations and lock files
1. **Test**: Optionally runs tests to verify compatibility
1. **Validate**: Optionally runs full tox validation

## Update Schedule

Recommended update frequency:

- **Monthly**: Pre-commit hooks and Python packages
- **Quarterly**: Major version updates (with thorough testing)
- **Immediately**: Security patches and vulnerability fixes
- **Weekly**: Automated check (CI)

## Breaking Changes

The script flags major version changes with `⚠️  MAJOR` warning:

```
  mypy    1.13.0  →  2.0.0  ⚠️  MAJOR
```

For major updates:

1. Review package CHANGELOG for breaking changes
1. Check migration guides
1. Test thoroughly with full tox suite
1. Update code if needed

## Manual Updates

For manual updates without the script:

```bash
# Update pre-commit hooks
pre-commit autoupdate

# Update Python packages
uv lock --upgrade

# Verify updates
pytest
tox -p auto
```

## Pre-commit Hook Updates

Hook versions are automatically updated by [pre-commit.ci](https://pre-commit.ci).

- **Schedule**: Weekly (every Monday)
- **Process**: Automated PRs created when updates available
- **Review**: Maintainer reviews and merges PRs
- **Manual update**: Run `pre-commit autoupdate` if urgent

### When pre-commit.ci creates an update PR

1. Review version changes and changelogs
1. Ensure all CI checks pass
1. Test locally for major version bumps
1. Merge PR to apply updates

### Manual updates between automation cycles

```bash
# Update all hooks to latest versions
pre-commit autoupdate

# Update specific hook
pre-commit autoupdate --repo https://github.com/astral-sh/ruff-pre-commit

# Test updated hooks
pre-commit run --all-files

# Commit if tests pass
git commit -am "chore(deps): Update pre-commit hooks"
```

## Rollback

If updates cause issues:

```bash
# Revert changes
git checkout HEAD -- .pre-commit-config.yaml uv.lock

# Or revert commit
git revert <commit-hash>
```
