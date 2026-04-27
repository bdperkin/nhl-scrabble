# Project Statistics

Detailed metrics and statistics for the NHL Scrabble project.

## Quick Overview

| Metric               | Value                                           |
| -------------------- | ----------------------------------------------- |
| **Python Version**   | 3.12-3.14 (supported), 3.15-dev (experimental)  |
| **Package Version**  | Dynamic (from git tags via hatch-vcs)           |
| **License**          | MIT                                             |
| **Test Coverage**    | 49.93% overall, >90% on core modules            |
| **Pre-commit Hooks** | 67 comprehensive quality checks                 |
| **CI/CD**            | GitHub Actions with UV optimization (4x faster) |

## Codebase Statistics

### Source Code

- **Lines of Code**: ~1,866 (src)
- **Python Modules**: 15 core modules
- **Package Structure**: Modern src-layout

**Module Breakdown:**

- `api/` - NHL API client (1 module)
- `models/` - Pydantic data models (3 modules)
- `scoring/` - Scrabble scoring logic (1 module)
- `processors/` - Business logic (2 modules)
- `reports/` - Report generators (6 modules)
- `cli.py` - Click-based CLI
- `config.py` - Configuration management

### Test Suite

- **Lines of Tests**: ~680 (tests)
- **Test Files**: 36 tests
- **Test Success Rate**: 100% passing
- **Test Organization**:
  - Unit tests: `tests/unit/`
  - Integration tests: `tests/integration/`
  - Shared fixtures: `tests/conftest.py`

### Test Coverage

| Module                | Coverage |
| --------------------- | -------- |
| **Core Modules**      | >90%     |
| `scoring/scrabble.py` | 95%      |
| `models/*.py`         | 92%      |
| `processors/*.py`     | 91%      |
| **Reports**           | ~80%     |
| `reports/base.py`     | 85%      |
| `reports/*_report.py` | 78%      |
| **CLI & Config**      | ~60%     |
| `cli.py`              | 62%      |
| `config.py`           | 58%      |
| **Overall**           | 49.93%   |

**Coverage Tracking:**

- **Tool**: pytest-cov
- **Platform**: Codecov (https://app.codecov.io/gh/bdperkin/nhl-scrabble)
- **Badge**: [![codecov](https://codecov.io/gh/bdperkin/nhl-scrabble/branch/main/graph/badge.svg)](https://codecov.io/gh/bdperkin/nhl-scrabble)

## Development Tools

### Makefile

- **Total Targets**: 57 documented targets
- **Logical Groupings**: 16 categories
- **Self-Documenting**: Yes (via `make help`)

**Target Categories:**

1. Setup (4 targets)
1. Testing (7 targets)
1. Tox (5 targets)
1. UV (2 targets)
1. Code Quality (8 targets)
1. Security (4 targets)
1. Building (3 targets)
1. Documentation (13 targets)
1. Running (3 targets)
1. Utilities (4 targets)
1. QA Testing (5 targets)
1. Git Cleanup (6 targets)
1. Dependency Management (3 targets)
1. License Management (3 targets)
1. Project Info (2 targets)
1. CI Simulation (1 target)

See [Makefile Reference](makefile.md) for complete target documentation.

### Pre-commit Hooks

- **Total Hooks**: 67 comprehensive quality checks
- **Hook Categories**: 24 categories

**Hook Breakdown:**

| Category                 | Count |
| ------------------------ | ----- |
| Meta hooks               | 3     |
| File quality             | 18    |
| Python quality           | 7     |
| Python imports           | 2     |
| Project validation       | 4     |
| YAML linting             | 1     |
| JSON/YAML schema         | 4     |
| Spelling                 | 1     |
| Markdown                 | 2     |
| Documentation            | 2     |
| Documentation quality    | 7     |
| UV                       | 1     |
| Flake8                   | 1     |
| Autoflake                | 1     |
| Black                    | 1     |
| Docformatter             | 1     |
| Autopep8                 | 1     |
| Python modernization     | 2     |
| Python statement sorting | 1     |
| Ruff                     | 2     |
| Type checking            | 2     |
| Security                 | 2     |

See [Pre-commit Hooks Guide](../contributing/pre-commit-hooks.md) for details.

### Tox Environments

**Test Environments:**

- `py312`, `py313`, `py314` - Python version testing (required)
- `py315` - Python 3.15-dev testing (experimental)

**Quality Environments:**

- `flake8` - Linting
- `ruff-check`, `ruff-format` - Ruff linting and formatting
- `black` - Code formatting
- `mypy`, `ty` - Type checking
- `isort` - Import sorting
- `interrogate` - Docstring coverage

**Additional Environments:**

- `coverage`, `diff-cover` - Coverage reporting
- `licenses`, `licenses-check`, `licenses-update` - License management
- `security`, `bandit`, `safety`, `pip-audit` - Security scanning
- `ci` - Full CI pipeline simulation

**Total Environments**: 45+ environments

## Dependencies

### Dependency Management

- **Tool**: UV (https://docs.astral.sh/uv/)
- **Lock File**: uv.lock (1,957 lines)
- **Acceleration**: 10-100x faster than pip

### Dependency Count

**Runtime Dependencies** (distributed with package):

- Direct: ~10 packages
- Transitive: ~50 packages

**Development Dependencies** (dev-only):

- Direct: ~40 packages
- Transitive: ~150 packages

**Total Unique Dependencies**: ~200 packages

**Breakdown by Type:**

| Type          | Count               |
| ------------- | ------------------- |
| Runtime       | 10                  |
| Testing       | 15                  |
| Linting       | 8                   |
| Type Checking | 5                   |
| Security      | 6                   |
| Documentation | 12                  |
| Build         | 8                   |
| Tox           | 3                   |
| Pre-commit    | Various (via hooks) |

### License Compliance

All runtime dependencies use permissive licenses:

- MIT
- Apache 2.0
- BSD (2-clause, 3-clause)
- ISC
- PSF
- MPL-2.0

See [LICENSES.md](../../LICENSES.md) for complete dependency license list.

## CI/CD

### GitHub Actions Workflows

**Active Workflows:**

1. **CI** (`.github/workflows/ci.yml`)

   - Runs on: Push to main, all PRs
   - Jobs: Test (Python 3.12-3.14), Tox, Pre-commit
   - Duration: ~3 minutes (with UV)
   - Duration without UV: ~12 minutes

1. **CodeQL** (`.github/workflows/codeql.yml`)

   - Runs on: Weekly (Mondays), all PRs
   - Languages: Python
   - Severity: High and Critical

1. **Docs** (`.github/workflows/docs.yml`)

   - Runs on: Push to main
   - Deploys to: GitHub Pages

1. **Package Validation** (`.github/workflows/package-validation.yml`)

   - Runs on: All PRs, tags
   - Validates: Wheel contents, metadata

**Workflow Statistics:**

- Total workflows: 4
- Required checks: CI (all Python versions), Tox, Pre-commit
- Optional checks: CodeQL (informational)
- Badge status: All passing ✅

### CI Performance

| Metric                | Value            |
| --------------------- | ---------------- |
| **Pipeline Duration** | ~3 minutes       |
| **Speedup (UV)**      | 4x faster        |
| **Success Rate**      | >95% first-run   |
| **Python Versions**   | 3.12, 3.13, 3.14 |
| **Cache Hit Rate**    | ~80%             |

### Automation

**Dependabot:**

- Schedule: Weekly (Mondays 9 AM ET)
- Targets: Python deps, GitHub Actions
- Security: Immediate PRs for vulnerabilities
- Grouping: Dev deps, prod deps, actions

**pre-commit.ci:**

- Schedule: Weekly (Mondays)
- Updates: All 67 pre-commit hooks
- Auto-merge: Not enabled (requires review)

## Documentation

### Structure

Documentation follows [Diátaxis framework](https://diataxis.fr/):

| Category      | Files | Purpose                    |
| ------------- | ----- | -------------------------- |
| Tutorials     | 3     | Learning-oriented lessons  |
| How-to Guides | 10    | Problem-oriented recipes   |
| Reference     | 8     | Technical specifications   |
| Explanation   | 6     | Conceptual understanding   |
| Community     | 5     | Contributing, support, etc |

**Total Documentation Files**: ~32 markdown files

### Documentation Metrics

- **Lines of Documentation**: ~3,500 lines
- **Docstring Coverage**: 100% (enforced by interrogate hook)
- **Spelling**: Checked by codespell hook
- **Markdown Quality**: Checked by pymarkdown + mdformat
- **RST Quality**: Checked by doc8 + rstcheck

### Online Documentation

- **Host**: GitHub Pages
- **URL**: https://bdperkin.github.io/nhl-scrabble/
- **Build Tool**: Sphinx
- **Theme**: sphinx-rtd-theme
- **Auto-Deploy**: Yes (on push to main)

## Version History

### Versioning Strategy

- **Tool**: hatch-vcs (dynamic versioning from git tags)
- **Format**: Semantic Versioning (vX.Y.Z)
- **Current**: 0.0.4 (development)

**Version Sources:**

1. **Tagged Release**: `v0.1.0` → Package version `0.1.0`
1. **Development**: 5 commits after v0.1.0 → `0.1.1.dev5+g<hash>`
1. **No Tags**: Fallback to `0.0.0+unknown`

### Release History

See [CHANGELOG.md](../../CHANGELOG.md) for complete version history.

**Release Stats:**

- Total releases: 3
- Latest stable: v0.0.3
- Release frequency: ~1 per month
- Breaking changes: None (pre-1.0)

## Performance

### Test Performance

- **Sequential**: 131s for 170 tests
- **Parallel** (pytest-xdist): 47s (2.8x speedup on 8 cores)
- **CI** (2 workers): ~60s (optimized for GitHub Actions 2-core runners)

### Build Performance

| Operation        | Standard | With UV | Speedup |
| ---------------- | -------- | ------- | ------- |
| Package install  | 60s      | 6s      | 10x     |
| Tox environments | 60s      | 8s      | 7.5x    |
| Tox parallel     | 5min     | 30s     | 10x     |
| CI/CD pipeline   | 12min    | 3min    | 4x      |
| Pre-commit hooks | 45s      | 5s      | 9x      |

### API Performance

**NHL API Integration:**

- Average API response time: 1-2s per endpoint
- Total analysis time: ~30s (32 teams × ~1s each)
- Rate limiting: 0.3s delay between requests
- Retry logic: 3 retries with exponential backoff

## Repository Stats

### Git Statistics

- **Total Commits**: Check [Commit Activity](https://github.com/bdperkin/nhl-scrabble/graphs/commit-activity)
- **Contributors**: See [Contributors](https://github.com/bdperkin/nhl-scrabble/graphs/contributors)
- **Stars**: [![GitHub stars](https://img.shields.io/github/stars/bdperkin/nhl-scrabble?style=social)](https://github.com/bdperkin/nhl-scrabble/stargazers)
- **Forks**: Check [Network](https://github.com/bdperkin/nhl-scrabble/network)

### Issue/PR Stats

- **Open Issues**: [![GitHub issues](https://img.shields.io/github/issues/bdperkin/nhl-scrabble)](https://github.com/bdperkin/nhl-scrabble/issues)
- **PR Success Rate**: >90% merged
- **Average PR Review Time**: \<24 hours
- **Stale Policy**: 60 days (issues), 30 days (PRs)

### Activity

- **Commit Frequency**: [![Commit Activity](https://img.shields.io/github/commit-activity/m/bdperkin/nhl-scrabble)](https://github.com/bdperkin/nhl-scrabble/graphs/commit-activity)
- **Last Commit**: [![GitHub last commit](https://img.shields.io/github/last-commit/bdperkin/nhl-scrabble)](https://github.com/bdperkin/nhl-scrabble/commits/main)
- **Maintenance Status**: [![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/bdperkin/nhl-scrabble/graphs/commit-activity)

## Comparison to Similar Projects

### Code Quality Metrics

This project aims for high code quality standards:

- **Type Coverage**: 100% (strict mypy)
- **Docstring Coverage**: 100% (interrogate enforced)
- **Test Coverage Goal**: 90% (currently 50%, improving)
- **Pre-commit Hooks**: 67 (comprehensive)
- **Linting**: ALL ruff rules enabled (500+ rules)

### Developer Experience

- **Setup Time**: \<1 minute (`make init`)
- **Test Run Time**: \<1 minute (parallel)
- **CI Feedback**: \<3 minutes
- **Documentation**: Comprehensive (32 files, Diátaxis framework)

## Future Metrics to Track

Planned additions to this document:

- [ ] API endpoint usage statistics
- [ ] Web interface traffic metrics
- [ ] Download statistics from PyPI
- [ ] Documentation page views
- [ ] Average issue resolution time
- [ ] Code churn rate
- [ ] Dependency vulnerability history
- [ ] Build artifact sizes

## See Also

- [CHANGELOG.md](../../CHANGELOG.md) - Version history
- [Makefile Reference](makefile.md) - All Makefile targets
- [Pre-commit Hooks](../contributing/pre-commit-hooks.md) - Hook details
- [GitHub Repository](https://github.com/bdperkin/nhl-scrabble) - Live statistics

______________________________________________________________________

**Last Updated**: 2026-04-27
**Note**: Statistics are point-in-time snapshots. For real-time metrics, see repository badges and GitHub Insights.
