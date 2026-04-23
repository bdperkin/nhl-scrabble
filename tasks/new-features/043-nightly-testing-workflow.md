# Nightly Comprehensive Testing Workflow

**GitHub Issue**: #310 - https://github.com/bdperkin/nhl-scrabble/issues/310

**Parent Task**: enhancement/022-comprehensive-github-workflows.md (#298)

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

2-3 hours

## Description

Implement nightly comprehensive testing workflow that runs extended test suite, integration tests, and checks on all supported Python versions. Catches environment-specific issues and provides comprehensive quality assurance.

## Current State

**PR-Based Testing Only:**

Currently:

- Tests run on PRs and pushes
- Limited to quick tests
- Single Python version primarily
- No extended testing
- No comprehensive integration tests

## Proposed Solution

Create `.github/workflows/nightly.yml`:

```yaml
name: Nightly Comprehensive Testing

on:
  schedule:
    # Run every night at 2 AM UTC
    - cron: 0 2 * * *
  workflow_dispatch:

permissions:
  contents: read
  issues: write

jobs:
  comprehensive-test:
    name: Test on ${{ matrix.os }} / Python ${{ matrix.python-version }}
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ['3.12', '3.13', '3.14', 3.15-dev]

    steps:
      - name: Checkout repository
        uses: actions/checkout@v6

      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install UV
        uses: astral-sh/setup-uv@v7

      - name: Install dependencies
        run: uv pip install -e ".[dev]" --system

      - name: Run full test suite
        run: |
          pytest -v --cov --cov-report=xml --cov-report=term

      - name: Run integration tests
        run: |
          pytest tests/integration/ -v --slow

      - name: Upload coverage
        uses: codecov/codecov-action@v6
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          flags: nightly-${{ matrix.os }}-py${{ matrix.python-version }}

  performance-test:
    name: Performance Tests
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v6

      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install uv
          uv pip install -e ".[dev]" --system

      - name: Run benchmark tests
        run: |
          pytest tests/benchmark/ --benchmark-only --benchmark-autosave

  dependency-audit:
    name: Dependency Security Audit
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v6

      - name: Set up Python
        uses: actions/setup-python@v6

      - name: Run pip-audit
        run: |
          pip install pip-audit
          pip-audit --desc

      - name: Run safety check
        run: |
          pip install safety
          safety check

  notify-failures:
    name: Notify on Failure
    needs: [comprehensive-test, performance-test, dependency-audit]
    if: failure()
    runs-on: ubuntu-latest

    steps:
      - name: Create issue on failure
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: '🌙 Nightly Test Failure - ' + new Date().toISOString().split('T')[0],
              body: `Nightly comprehensive tests failed.

              **Workflow Run:** ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}

              Please investigate the failure.`,
              labels: ['ci/cd', 'nightly-failure']
            });
```

## Implementation Steps

1. **Create Workflow File** (1h)

   - Create comprehensive test matrix
   - Add performance tests
   - Add security audits
   - Configure notifications

1. **Add Extended Tests** (1-1.5h)

   - Mark slow tests
   - Create integration test suite
   - Add stress tests
   - Configure timeouts

1. **Configure Notifications** (30min)

   - Create issues on failure
   - Configure severity
   - Add summary

1. **Test Workflow** (30min)

   - Trigger manually
   - Verify all jobs run
   - Test failure notification

1. **Documentation** (15min)

   - Document nightly tests
   - Add to CLAUDE.md

## Acceptance Criteria

- [ ] Workflow file created
- [ ] Runs nightly at 2 AM UTC
- [ ] Tests all OS platforms
- [ ] Tests all Python versions
- [ ] Runs extended test suite
- [ ] Runs performance benchmarks
- [ ] Runs security audits
- [ ] Creates issue on failure
- [ ] Manual trigger available
- [ ] Documentation updated

## Related Files

**New Files:**

- `.github/workflows/nightly.yml`

**Modified Files:**

- `CLAUDE.md` - Document nightly workflow
- `tests/conftest.py` - Add slow test marker

## Additional Notes

### Test Categories

**Quick Tests (PR/Push):**

- Unit tests
- Fast integration tests
- Basic validation

**Nightly Tests:**

- All quick tests
- Slow integration tests
- Performance benchmarks
- Security audits
- Multi-platform
- All Python versions

### Benefits

- Catch environment-specific bugs
- Comprehensive coverage
- Early issue detection
- Performance tracking
- Security monitoring

## Implementation Notes

*To be filled during implementation:*

- Average runtime:
- First issue created:
