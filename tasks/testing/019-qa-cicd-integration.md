# QA CI/CD Integration

**GitHub Issue**: #315 - https://github.com/bdperkin/nhl-scrabble/issues/315

**Parent Task**: testing/012-qa-automation-framework.md

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

2-4 hours

## Description

Integrate QA automation tests into GitHub Actions CI/CD pipeline with proper reporting, artifact management, and failure notifications.

## Proposed Solution

### GitHub Actions Workflow

```yaml
name: QA Automation Tests

on:
  pull_request:
    paths:
      - 'src/nhl_scrabble/web/**'
      - 'qa/web/**'
  push:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # Nightly at 2 AM
  workflow_dispatch:

jobs:
  qa-tests:
    name: QA Tests (${{ matrix.browser }})
    runs-on: ubuntu-latest
    strategy:
      matrix:
        browser: [chromium, firefox, webkit]

    steps:
      - uses: actions/checkout@v6

      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: make qa-install

      - name: Run QA tests
        run: |
          cd qa/web
          pytest tests/ --browser ${{ matrix.browser }} \
                        --html=reports/report-${{ matrix.browser }}.html

      - name: Upload test reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: qa-reports-${{ matrix.browser }}
          path: qa/web/reports/

      - name: Upload screenshots
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: screenshots-${{ matrix.browser }}
          path: qa/web/screenshots/
```

## Implementation Steps

1. **Create Workflow File** (1h)
1. **Configure Matrix** (30min)
1. **Artifact Management** (1h)
1. **Test and Verify** (1-2h)

## Acceptance Criteria

- [ ] Workflow file created
- [ ] Runs on PR and main
- [ ] Cross-browser testing
- [ ] Reports uploaded
- [ ] Screenshots on failure
- [ ] Nightly runs configured

## Dependencies

- **Requires**: All previous QA sub-tasks (013-018)

## Implementation Notes

*To be filled during implementation:*

- Workflow execution time:
- Artifact sizes:
