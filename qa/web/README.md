# Web Automation Tests

Comprehensive web interface testing using Playwright for the NHL Scrabble web application.

## Overview

This directory contains automated web tests that validate the NHL Scrabble web interface across multiple browsers and test scenarios.

## Test Framework

- **Framework**: Playwright (Python)
- **Test Runner**: pytest
- **Browsers**: Chromium, Firefox, WebKit
- **Pattern**: Page Object Model (POM)

## Directory Structure

```
web/
├── README.md                # This file
├── pyproject.toml          # Dependencies
├── playwright_config.py    # Playwright configuration
├── conftest.py             # Pytest fixtures
├── pytest.ini              # Pytest configuration
├── .gitignore              # Ignore patterns
├── tests/                  # Test suites
│   ├── functional/        # Functional tests
│   ├── visual/            # Visual regression tests
│   ├── performance/       # Performance tests
│   └── accessibility/     # Accessibility tests
├── pages/                  # Page Object Models
├── fixtures/               # Test fixtures and factories
├── screenshots/            # Visual test baselines
├── reports/                # Test reports
└── scripts/                # Helper scripts
```

## Test Types

### Functional Tests (`tests/functional/`)

End-to-end user workflows:

- Navigation and routing
- Data display and updates
- Form interactions
- User workflows

**Run**: `make qa-functional` or `pytest -m functional`

### Visual Regression Tests (`tests/visual/`)

Screenshot comparison testing:

- Layout consistency
- UI appearance
- Cross-browser visual parity
- Responsive design

**Run**: `make qa-visual` or `pytest -m visual`

### Performance Tests (`tests/performance/`)

Load and performance testing:

- Page load times
- Resource usage
- Concurrent user simulation
- Stress testing

**Run**: `make qa-performance` or `pytest -m performance`

### Accessibility Tests (`tests/accessibility/`)

WCAG 2.1 AA compliance:

- Semantic HTML
- ARIA attributes
- Keyboard navigation
- Screen reader compatibility

**Run**: `make qa-accessibility` or `pytest -m accessibility`

## Setup

### Prerequisites

- Python 3.12+
- Node.js (for Playwright browsers)

### Installation

```bash
# From project root
make qa-install

# Or manually
cd qa/web
pip install -e .
playwright install
```

## Running Tests

### All Tests

```bash
make qa-test
```

### Specific Test Types

```bash
make qa-functional        # Functional tests only
make qa-visual            # Visual regression tests
make qa-performance       # Performance tests
make qa-accessibility     # Accessibility tests
```

### Manual Execution

```bash
cd qa/web

# All tests
pytest

# Specific test file
pytest tests/functional/test_navigation.py

# Specific test
pytest tests/functional/test_navigation.py::test_home_page

# With specific browser
pytest --browser chromium
pytest --browser firefox
pytest --browser webkit

# Parallel execution
pytest -n auto

# With HTML report
pytest --html=reports/report.html --self-contained-html

# Headful mode (see browser)
pytest --headed

# Debug mode
pytest --headed --slowmo 1000
```

## Writing Tests

### Page Object Model

Always use Page Objects for better maintainability:

```python
# pages/home_page.py
from playwright.sync_api import Page


class HomePage:
    def __init__(self, page: Page):
        self.page = page
        self.url = "/"

    def navigate(self):
        self.page.goto(self.url)

    def get_title(self):
        return self.page.title()
```

### Test Example

```python
# tests/functional/test_home.py
import pytest
from pages.home_page import HomePage


@pytest.mark.functional
def test_home_page_title(page, base_url):
    """Verify home page title is correct."""
    home = HomePage(page)
    home.navigate()
    assert "NHL Scrabble" in home.get_title()
```

## Configuration

### Playwright Configuration

Edit `playwright_config.py`:

```python
config = {
    "base_url": "http://localhost:5000",
    "timeout": 30000,
    "screenshot_on_failure": True,
    "video_on_failure": True,
    "trace_on_failure": True,
}
```

### Pytest Configuration

Edit `pytest.ini`:

```ini
[pytest]
addopts =
    -v
    --tb=short
    --html=reports/report.html
```

## Best Practices

### Test Design

1. **Use Page Objects**: Don't use raw selectors in tests
1. **Isolation**: Each test should be independent
1. **Stability**: Use auto-waiting, avoid sleep()
1. **Readability**: Clear test names and assertions
1. **DRY**: Use fixtures and helper functions

### Selectors

Prefer stable selectors:

1. `data-testid` attributes (best)
1. Semantic roles (good)
1. Text content (acceptable)
1. CSS classes (avoid)
1. XPath (last resort)

```python
# Good
page.get_by_test_id("submit-button")
page.get_by_role("button", name="Submit")
page.get_by_text("Welcome")

# Avoid
page.locator(".btn-primary")
page.locator("//div[@class='container']/button")
```

### Fixtures

Use fixtures for common setup:

```python
@pytest.fixture
def logged_in_page(page, base_url):
    """Provide a page with user already logged in."""
    page.goto(f"{base_url}/login")
    page.fill("#username", "testuser")
    page.fill("#password", "testpass")
    page.click("#submit")
    return page
```

## Debugging

### Visual Debugging

```bash
# Run headful with slow motion
pytest --headed --slowmo 500

# Pause on failure
pytest --headed --pause-on-failure

# Debug specific test
pytest --headed --slowmo 1000 tests/functional/test_home.py::test_specific
```

### Playwright Inspector

```bash
# Launch inspector
PWDEBUG=1 pytest tests/functional/test_home.py
```

### Traces

View trace for failed tests:

```bash
# Traces are saved to test-results/ on failure
playwright show-trace test-results/trace.zip
```

## CI/CD Integration

Tests run in CI via GitHub Actions:

- **On PR**: Functional and accessibility tests
- **On merge**: Full test suite
- **Nightly**: Cross-browser comprehensive tests

See `.github/workflows/qa-web.yml` for configuration.

## Troubleshooting

### Browser Installation Issues

```bash
# Reinstall browsers
playwright install

# Specific browser
playwright install chromium
```

### Timeout Issues

Increase timeout in `playwright_config.py`:

```python
config = {
    "timeout": 60000,  # 60 seconds
}
```

### Flaky Tests

- Use Playwright's auto-waiting
- Avoid `time.sleep()`
- Use proper wait conditions
- Check for race conditions

## Reporting

Test reports are generated in `reports/`:

- `report.html`: HTML test report
- Test videos (on failure)
- Screenshots (on failure)
- Traces (on failure)

## Contributing

1. Follow Page Object Model pattern
1. Add appropriate test markers
1. Update this README for new test types
1. Ensure tests pass locally before PR

## Resources

- [Playwright Python Docs](https://playwright.dev/python/)
- [pytest Documentation](https://docs.pytest.org/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Project Documentation](https://bdperkin.github.io/nhl-scrabble/)
