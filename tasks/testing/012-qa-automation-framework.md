# QA Automation Framework

**GitHub Issue**: #311 - https://github.com/bdperkin/nhl-scrabble/issues/311

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

30-40 hours (main task coordination + sub-tasks)

## Description

Establish a comprehensive QA automation framework in a new `./qa/` directory for end-to-end testing of the web interface. This framework will be separate from the existing Python unit/integration tests and will focus on browser-based testing with multiple test types: functional, regression, visual, performance, and accessibility.

## Current State

**Existing Testing:**

The project has excellent Python test coverage (91.49%):

- ✅ Unit tests (`tests/unit/`)
- ✅ Integration tests (`tests/integration/`)
- ✅ Pytest framework with 170+ tests
- ✅ CI integration with GitHub Actions
- ✅ Codecov coverage tracking

**Missing:**

- ❌ No dedicated QA automation framework
- ❌ No browser-based end-to-end tests
- ❌ No visual regression testing
- ❌ No performance/load testing
- ❌ No automated accessibility testing
- ❌ No separate QA infrastructure

**Web Interface Exists:**

The project has a functional web interface (completed in PR #297):

- Flask-based web application
- Multiple pages (index, teams, divisions, conferences, playoffs, stats)
- JavaScript interactivity
- Data visualizations (Chart.js)
- Comprehensive manual testing completed

## Proposed Solution

### QA Directory Structure

Create a new `./qa/` directory for standalone quality assurance automation:

```
qa/
├── README.md                   # QA framework documentation
├── web/                        # Web automation tests
│   ├── README.md
│   ├── pyproject.toml          # Playwright dependencies
│   ├── playwright.config.py    # Playwright configuration
│   ├── conftest.py             # Pytest fixtures
│   ├── tests/
│   │   ├── functional/         # Functional tests
│   │   ├── visual/             # Visual regression tests
│   │   ├── performance/        # Load/performance tests
│   │   └── accessibility/      # A11y tests
│   ├── pages/                  # Page Object Model
│   │   ├── __init__.py
│   │   ├── base_page.py
│   │   ├── index_page.py
│   │   ├── teams_page.py
│   │   └── ...
│   ├── fixtures/               # Test data and fixtures
│   ├── screenshots/            # Visual test baselines
│   ├── reports/                # Test reports
│   └── scripts/                # Helper scripts
├── api/                        # Future: API automation tests (stub)
├── cli/                        # Future: CLI automation tests (stub)
├── tui/                        # Future: TUI automation tests (stub)
└── sdk/                        # Future: SDK tests (stub)
```

### Technology Stack

**Playwright** (Recommended choice for this Python project):

**Why Playwright:**

- ✅ **Python-native**: First-class Python support
- ✅ **Modern**: Built for modern web apps
- ✅ **Fast**: Auto-waiting, parallel execution
- ✅ **Cross-browser**: Chromium, Firefox, WebKit
- ✅ **Developer experience**: Excellent API, debugging tools
- ✅ **Visual testing**: Built-in screenshot comparison
- ✅ **Network control**: Intercept/mock requests
- ✅ **Accessibility**: Built-in a11y tools
- ✅ **Active development**: Microsoft-backed

**vs Selenium:**

- Selenium: Older, more verbose API, manual waits
- Playwright: Modern, auto-waiting, better DX

**vs Cypress:**

- Cypress: JavaScript-only, not ideal for Python project
- Playwright: Multi-language including Python

**Dependencies:**

```toml
[tool.qa.web]
dependencies = [
  "playwright>=1.40.0",
  "pytest-playwright>=0.4.0",
  "pytest-html>=4.1.0",
  "pytest-xdist>=3.5.0",      # Parallel execution
  "pillow>=10.0.0",           # Image comparison
  "axe-playwright>=0.1.0",    # Accessibility testing
  "locust>=2.20.0",           # Load testing
]
```

### Test Types

**1. Functional Testing** (Sub-task #015)

- User workflows (navigation, interactions)
- Form submissions
- Button clicks
- Data display validation
- Error handling

**2. Visual Regression Testing** (Sub-task #016)

- Screenshot comparison
- Layout validation
- CSS regression detection
- Cross-browser visual consistency

**3. Performance/Load Testing** (Sub-task #017)

- Page load times
- Response times
- Concurrent user simulation
- Resource utilization
- Bottleneck identification

**4. Accessibility Testing** (Sub-task #018)

- WCAG 2.1 compliance
- Keyboard navigation
- Screen reader compatibility
- Color contrast
- ARIA attributes

### Makefile Integration

Add QA targets to main Makefile:

```makefile
# ============================================================================
# QA Automation
# ============================================================================

.PHONY: qa-install qa-test qa-web qa-functional qa-visual qa-perf qa-a11y qa-report

## Install QA dependencies
qa-install:
	@echo "Installing QA automation dependencies..."
	cd qa/web && uv pip install -e ".[dev]" --system
	playwright install

## Run all QA tests
qa-test: qa-web

## Run all web automation tests
qa-web:
	@echo "Running web automation tests..."
	cd qa/web && pytest tests/ -v --html=reports/report.html

## Run functional tests only
qa-functional:
	cd qa/web && pytest tests/functional/ -v

## Run visual regression tests
qa-visual:
	cd qa/web && pytest tests/visual/ -v --update-snapshots

## Run performance tests
qa-perf:
	cd qa/web && pytest tests/performance/ -v

## Run accessibility tests
qa-a11y:
	cd qa/web && pytest tests/accessibility/ -v

## Generate QA test report
qa-report:
	@echo "Opening QA test report..."
	@open qa/web/reports/report.html || xdg-open qa/web/reports/report.html
```

## Implementation Steps

### Phase 1: Infrastructure Setup (Sub-task #013) - 4-6h

1. **Create QA Directory Structure**

   - Create `qa/` directory
   - Create `qa/web/` structure
   - Stub out future directories (api, cli, tui, sdk)
   - Add README files

1. **Configuration Setup**

   - Create `qa/web/pyproject.toml`
   - Create `qa/web/playwright.config.py`
   - Create `.gitignore` for QA artifacts

1. **Documentation**

   - Write `qa/README.md` (framework overview)
   - Write `qa/web/README.md` (web tests guide)
   - Document directory structure

### Phase 2: Playwright Framework (Sub-task #014) - 6-8h

1. **Install Playwright**

   - Set up Python environment
   - Install Playwright
   - Install browsers (Chromium, Firefox, WebKit)

1. **Page Object Model**

   - Create base page class
   - Create page objects for all web pages
   - Implement common interactions

1. **Test Fixtures**

   - Browser fixtures
   - Page fixtures
   - Test data fixtures

1. **Base Test Infrastructure**

   - Test helpers
   - Assertion utilities
   - Logging/reporting setup

### Phase 3: Test Implementation (Sub-tasks #015-018) - 16-24h

**Sub-task #015: Functional Tests** (6-8h)

- Navigation tests
- Form interaction tests
- Data display tests
- Error handling tests

**Sub-task #016: Visual Regression Tests** (4-6h)

- Screenshot baseline generation
- Visual comparison tests
- Cross-browser visual tests

**Sub-task #017: Performance Tests** (4-6h)

- Page load performance
- API response times
- Load testing with Locust
- Performance benchmarks

**Sub-task #018: Accessibility Tests** (2-4h)

- Axe-core integration
- WCAG compliance checks
- Keyboard navigation tests
- Screen reader compatibility

### Phase 4: CI/CD Integration (Sub-task #019) - 2-4h

1. **GitHub Actions Workflow**

   - Create `.github/workflows/qa.yml`
   - Run on PR and push to main
   - Parallel execution
   - Artifact uploads

1. **Reporting**

   - HTML test reports
   - Screenshot artifacts
   - Performance metrics
   - Coverage tracking

## Testing Strategy

### Running Tests Locally

```bash
# Install QA dependencies
make qa-install

# Run all QA tests
make qa-test

# Run specific test types
make qa-functional
make qa-visual
make qa-perf
make qa-a11y

# Run with specific browser
cd qa/web && pytest tests/ --browser chromium
cd qa/web && pytest tests/ --browser firefox
cd qa/web && pytest tests/ --browser webkit

# Run in headed mode (see browser)
cd qa/web && pytest tests/ --headed

# Debug mode
cd qa/web && pytest tests/ --headed --slowmo 1000

# Parallel execution
cd qa/web && pytest tests/ -n auto
```

### CI Execution

Automated runs on:

- Every PR
- Push to main
- Nightly comprehensive run
- On-demand via workflow_dispatch

## Acceptance Criteria

### Main Task

- [ ] QA directory structure created
- [ ] All 7 sub-tasks completed
- [ ] Documentation comprehensive
- [ ] Makefile targets functional
- [ ] CI/CD integrated
- [ ] All test types implemented

### Sub-tasks

- [ ] #013: QA Infrastructure Setup
- [ ] #014: Playwright Framework Setup
- [ ] #015: Functional Web Tests
- [ ] #016: Visual Regression Tests
- [ ] #017: Performance/Load Tests
- [ ] #018: Accessibility Tests
- [ ] #019: CI/CD Integration

### Quality Gates

- [ ] All tests pass locally
- [ ] All tests pass in CI
- [ ] Cross-browser compatibility verified
- [ ] Documentation complete
- [ ] Code review approved
- [ ] Performance benchmarks established

## Related Files

**New Files:**

- `qa/README.md` - QA framework documentation
- `qa/web/` - Complete web automation directory structure
- `qa/{api,cli,tui,sdk}/README.md` - Future test stubs
- `.github/workflows/qa.yml` - QA CI/CD workflow
- `Makefile` - QA targets added

**Modified Files:**

- `CLAUDE.md` - Document QA framework
- `CONTRIBUTING.md` - Add QA testing guidelines
- `.gitignore` - Add QA artifacts

## Dependencies

**Task Dependencies:**

- **Requires**: Web interface must be functional (already complete - PR #297)
- **Complements**: Existing pytest infrastructure
- **Enables**: Comprehensive end-to-end testing

**Tool Dependencies:**

- `playwright` - Browser automation
- `pytest-playwright` - Pytest integration
- `locust` - Performance testing
- `axe-playwright` - Accessibility testing
- `pytest-html` - HTML reports
- `pytest-xdist` - Parallel execution

**System Dependencies:**

- Modern browsers (auto-installed by Playwright)
- Python 3.12+
- UV for dependency management

## Additional Notes

### Why Separate from tests/?

**tests/** - Developer-focused unit/integration tests:

- Fast execution (< 1 minute)
- Python code testing
- Run on every commit
- Part of development workflow
- 91.49% code coverage

**qa/** - QA-focused end-to-end tests:

- Slower execution (5-10 minutes)
- Browser-based testing
- Run on PR/release
- Comprehensive validation
- Different tooling (Playwright vs pytest)

### Test Pyramid

```
        /\
       /  \      E2E (QA - Slower, Comprehensive)
      /____\
     /      \    Integration (tests/ - Medium)
    /________\
   /          \  Unit (tests/ - Fast, Focused)
  /____________\
```

### Page Object Model Example

```python
# qa/web/pages/teams_page.py
from playwright.sync_api import Page


class TeamsPage:
    def __init__(self, page: Page):
        self.page = page
        self.url = "http://localhost:5000/teams"

    def navigate(self):
        self.page.goto(self.url)

    def get_team_count(self):
        return self.page.locator(".team-card").count()

    def search_team(self, team_name):
        self.page.locator("#team-search").fill(team_name)
        self.page.locator("#search-button").click()
```

### Functional Test Example

```python
# qa/web/tests/functional/test_teams.py
import pytest
from pages.teams_page import TeamsPage


def test_teams_page_loads(page):
    teams_page = TeamsPage(page)
    teams_page.navigate()

    assert page.title() == "NHL Teams - NHL Scrabble"
    assert teams_page.get_team_count() == 32


def test_team_search(page):
    teams_page = TeamsPage(page)
    teams_page.navigate()
    teams_page.search_team("Capitals")

    assert page.locator(".team-card:visible").count() == 1
```

### Visual Test Example

```python
# qa/web/tests/visual/test_screenshots.py
def test_homepage_visual(page):
    page.goto("http://localhost:5000")
    expect(page).to_have_screenshot("homepage.png")


def test_teams_page_visual(page):
    page.goto("http://localhost:5000/teams")
    expect(page).to_have_screenshot("teams-page.png")
```

### Performance Test Example

```python
# qa/web/tests/performance/test_load.py
from locust import HttpUser, task, between


class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def load_homepage(self):
        self.client.get("/")

    @task
    def load_teams(self):
        self.client.get("/teams")
```

### Accessibility Test Example

```python
# qa/web/tests/accessibility/test_a11y.py
from axe_playwright import Axe


def test_homepage_accessibility(page):
    page.goto("http://localhost:5000")

    axe = Axe(page)
    results = axe.run()

    assert (
        len(results.violations) == 0
    ), f"Accessibility violations found: {results.violations}"
```

### CI/CD Workflow Example

```yaml
# .github/workflows/qa.yml
name: QA Automation Tests

on:
  pull_request:
  push:
    branches: [main]

jobs:
  qa-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v6

      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install uv
          make qa-install

      - name: Run QA tests
        run: make qa-test

      - name: Upload test report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: qa-test-report
          path: qa/web/reports/
```

### Best Practices

**Test Organization:**

- One test file per page/feature
- Clear test names (test_action_expected_result)
- Use Page Object Model
- Reusable fixtures

**Test Data:**

- Use fixtures for test data
- Mock external dependencies
- Isolate tests (no shared state)
- Clean up after tests

**Assertions:**

- Use specific assertions
- Clear error messages
- Multiple assertions per test OK if related
- Auto-waiting (Playwright handles this)

**Maintenance:**

- Update visual baselines when UI changes
- Keep page objects in sync with UI
- Regular test review
- Remove flaky tests

### Future Enhancements

**Additional Test Types:**

- Security testing (OWASP ZAP integration)
- Mobile responsiveness testing
- Cross-browser compatibility matrix
- PDF report generation testing
- API contract testing

**Advanced Features:**

- Test data generation
- Test result dashboard
- Flaky test detection
- Test execution analytics
- Parallel cross-browser testing

**Integration:**

- Slack notifications on failure
- Performance trending over time
- Visual regression history
- Accessibility compliance reporting

### Breaking Changes

**None** - This is purely additive:

- Existing tests unchanged
- New QA directory separate
- No impact on development workflow
- Optional execution (not in main CI yet)

### Migration Notes

**Gradual Rollout:**

1. **Phase 1**: Set up infrastructure
1. **Phase 2**: Implement core functional tests
1. **Phase 3**: Add visual/perf/a11y tests
1. **Phase 4**: Integrate into CI/CD
1. **Phase 5**: Make QA tests required for merges

**Adoption Strategy:**

- Start with critical user flows
- Expand test coverage gradually
- Train team on Playwright
- Establish QA practices

## Implementation Notes

*To be filled during implementation:*

### Infrastructure Setup

- Date started:
- Date completed:
- Actual effort:
- Challenges encountered:

### Framework Implementation

- Playwright version:
- Browsers tested:
- Initial test count:
- Performance baseline:

### CI/CD Integration

- Workflow execution time:
- Parallel jobs:
- Artifact size:
- Pass rate:

### Lessons Learned

- What worked well:
- What could be improved:
- Recommendations for future:
