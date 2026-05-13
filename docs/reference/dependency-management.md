# Dependency Management

This document describes the dependency management system for the NHL Scrabble project.

## Overview

The project uses **UV** (Astral's fast Python package installer) for dependency management with automated lock file upgrades to keep dependencies current and secure.

## Lock Files

The project maintains two separate lock files:

1. **Main Project**: `uv.lock`

   - Core application dependencies
   - Development, testing, and documentation tools
   - Optional dependency groups (export, i18n, branding, etc.)

1. **QA Web App**: `qa/web/uv.lock`

   - Playwright browser automation
   - Locust load testing
   - Axe-core accessibility testing
   - Visual regression testing tools

## Automated Lock File Upgrades

### Pre-commit Hook (Automatic)

When you modify `pyproject.toml`, a pre-commit hook automatically upgrades both lock files:

```bash
# Modify dependencies in pyproject.toml
vim pyproject.toml

# On commit, lock files are automatically upgraded
git add pyproject.toml
git commit -m "feat: add new dependency"
# Hook runs: scripts/upgrade_lock_files.sh --upgrade
# Lock files are upgraded and staged automatically
```

**Configuration**: `.pre-commit-config.yaml` → `upgrade-lock-files` hook

### Make Targets (Manual)

Manual commands for managing lock files:

```bash
# Check if lock files are up-to-date
make lock-check

# Upgrade lock files to latest compatible versions
make lock-upgrade

# Check for outdated packages
make lock-outdated
```

### GitHub Actions (Automated PRs)

A weekly GitHub Actions workflow automatically:

1. Upgrades all lock files
1. Runs quality checks (mypy, ruff, tests)
1. Creates a PR if updates are available

**Schedule**: Mondays at 9 AM UTC (4 AM ET)

**Manual trigger**: Can be triggered manually via GitHub UI

**Workflow**: `.github/workflows/dependency-upgrade.yml`

## Lock File Upgrade Script

The core upgrade logic is in `scripts/upgrade_lock_files.sh`:

```bash
# Upgrade both lock files
./scripts/upgrade_lock_files.sh --upgrade

# Check if lock files are current
./scripts/upgrade_lock_files.sh --check

# Preview outdated packages
./scripts/upgrade_lock_files.sh --check-outdated
```

### Options

- `--upgrade` (default) - Upgrade all dependencies to latest compatible versions
- `--check` - Verify lock files are up-to-date (exit 1 if not)
- `--check-outdated` - Show outdated packages without upgrading

### Environment Variables

- `UV_VERBOSE` - Enable verbose UV output

## Dependency Update Workflow

### Regular Updates (Weekly)

1. **Automated PR** created by GitHub Actions
1. **Review changes** in the PR (package versions, changelogs)
1. **CI validation** runs automatically
1. **Merge PR** when all checks pass

### Manual Updates (As Needed)

```bash
# Check for updates
make lock-outdated

# Upgrade lock files
make lock-upgrade

# Run quality checks
make quality

# Commit changes
git add uv.lock qa/web/uv.lock
git commit -m "chore(deps): upgrade dependencies"
```

### Adding New Dependencies

1. **Edit pyproject.toml**:

   ```toml
   dependencies = [
       # ... existing dependencies ...
       "new-package>=1.0.0",
   ]
   ```

1. **Commit changes**:

   ```bash
   git add pyproject.toml
   git commit -m "feat: add new-package dependency"
   # Pre-commit hook automatically upgrades lock files
   ```

1. **Lock files updated automatically** by pre-commit hook

## Dependency Groups

The project uses optional dependency groups:

```bash
# Development tools
pip install -e ".[dev]"

# Type checking
pip install -e ".[type]"

# Linting
pip install -e ".[lint]"

# Testing
pip install -e ".[test]"

# Security scanning
pip install -e ".[security]"

# Export formats (Excel, YAML, templates)
pip install -e ".[export]"

# Internationalization
pip install -e ".[i18n]"

# Documentation
pip install -e ".[docs]"

# All development dependencies
pip install -e ".[dev,type,lint,test,security,export,i18n,docs]"
```

## Security

### Vulnerability Scanning

Dependencies are automatically scanned for security vulnerabilities:

1. **Dependabot** - Weekly security updates
1. **pip-audit** - Pre-commit hook scans for CVEs
1. **Safety** - Pre-commit hook checks vulnerability databases
1. **Dependency Review** - GitHub Actions PR checks

### License Compliance

All dependencies must use approved licenses:

- **Allowed**: MIT, Apache-2.0, BSD, ISC, Python-2.0
- **Denied**: GPL-3.0, AGPL-3.0

Check licenses:

```bash
make licenses-check
```

## UV Performance

UV provides 10-100x speedup over pip:

- **Dependency resolution**: Parallel downloads, Rust-based solver
- **Lock file updates**: ~1-2 seconds vs 10-30 seconds (pip)
- **Cache management**: Automatic caching, shared across projects

## Troubleshooting

### Lock Files Out of Sync

```bash
# Check status
make lock-check

# Force upgrade
make lock-upgrade
```

### Pre-commit Hook Failures

```bash
# Upgrade lock files manually
./scripts/upgrade_lock_files.sh --upgrade

# Stage and commit
git add uv.lock qa/web/uv.lock
git commit --amend --no-edit
```

### CI Failures After Dependency Updates

1. **Check CI logs** for specific test failures
1. **Review package changelogs** for breaking changes
1. **Pin problematic package** if needed:
   ```toml
   dependencies = [
       "package-name==1.2.3",  # Pin to working version
   ]
   ```
1. **Create issue** for investigation

## Best Practices

1. **Review PRs carefully** - Check changelogs for breaking changes
1. **Test locally** before merging dependency upgrades
1. **Use version ranges** in pyproject.toml (avoid exact pins)
1. **Keep lock files committed** - Essential for reproducible builds
1. **Upgrade regularly** - Don't let dependencies get too outdated
1. **Check security advisories** - Review CVEs in automated PRs

## Related Documentation

- [UV Documentation](https://docs.astral.sh/uv/)
- [UV Lock Files](https://docs.astral.sh/uv/concepts/lockfile/)
- [CLAUDE.md](../../CLAUDE.md#dependency-management) - Quick reference
- [Makefile](../reference/makefile.md) - All make targets

## Integration Points

### Pre-commit Hooks

- **uv-lock** - Validates lock files match pyproject.toml
- **upgrade-lock-files** - Auto-upgrades on pyproject.toml changes

### GitHub Actions

- **dependency-upgrade.yml** - Weekly automated upgrades
- **dependency-review.yml** - PR dependency security checks
- **dependabot.yml** - GitHub native security updates

### Make Targets

- `lock-check` - Verify lock files are current
- `lock-upgrade` - Upgrade to latest versions
- `lock-outdated` - Check for available updates
- `deps-check` - Check for dependency updates
- `deps-update` - Interactive dependency updates

### Scripts

- `scripts/upgrade_lock_files.sh` - Core upgrade logic
- `scripts/update_dependencies.py` - Dependency management tool
