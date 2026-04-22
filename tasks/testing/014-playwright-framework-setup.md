# Playwright Framework Setup

**GitHub Issue**: #313 - https://github.com/bdperkin/nhl-scrabble/issues/313

**Parent Task**: testing/012-qa-automation-framework.md

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

6-8 hours

## Description

Set up the Playwright testing framework with Page Object Model, base test infrastructure, fixtures, and utilities. This provides the foundation for writing maintainable, reliable browser automation tests.

## Current State

**Infrastructure exists** (from task #013):

- ✅ QA directory structure created
- ✅ Configuration files in place
- ❌ No Playwright installation
- ❌ No page objects
- ❌ No test fixtures
- ❌ No base test utilities

## Proposed Solution

### Install Playwright

```bash
cd qa/web
uv pip install -e . --system
playwright install  # Install browsers
playwright install-deps  # Install system dependencies
```

### Page Object Model

**Base Page:**

```python
# qa/web/pages/base_page.py
from playwright.sync_api import Page, expect

class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.base_url = "http://localhost:5000"

    def navigate(self, path: str = ""):
        url = f"{self.base_url}{path}"
        self.page.goto(url)

    def get_title(self) -> str:
        return self.page.title()

    def wait_for_load(self):
        self.page.wait_for_load_state("networkidle")
```

**Specific Pages:**

```python
# qa/web/pages/index_page.py
from pages.base_page import BasePage

class IndexPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.url = "/"

    def navigate(self):
        super().navigate(self.url)

    def click_analyze_button(self):
        self.page.locator("#analyze-button").click()

    def get_welcome_message(self):
        return self.page.locator("h1").text_content()
```

### Test Fixtures

**conftest.py:**

```python
# qa/web/conftest.py
import pytest
from playwright.sync_api import Page

@pytest.fixture(scope="session")
def browser_context_args():
    return {
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
    }

@pytest.fixture
def page_fixture(page: Page):
    """Enhanced page fixture with common setup."""
    page.set_default_timeout(10000)
    yield page
    # Cleanup after test
    page.close()
```

## Implementation Steps

1. **Install Playwright** (30min)

   - Install Python package
   - Install browsers
   - Verify installation

1. **Create Base Page Class** (1-2h)

   - Common navigation methods
   - Wait utilities
   - Screenshot helpers
   - Element interaction methods

1. **Create Page Objects** (3-4h)

   - IndexPage
   - TeamsPage
   - DivisionsPage
   - ConferencesPage
   - PlayoffsPage
   - StatsPage

1. **Test Fixtures** (1-2h)

   - Browser fixtures
   - Page fixtures
   - Test data fixtures
   - Environment configuration

1. **Test Utilities** (1h)

   - Assertion helpers
   - Wait helpers
   - Data generators
   - Screenshot utilities

## Acceptance Criteria

- [ ] Playwright installed and browsers working
- [ ] Base page class implemented
- [ ] Page objects for all pages
- [ ] Test fixtures configured
- [ ] Utilities available
- [ ] Can run simple smoke test

## Dependencies

- **Requires**: testing/013-qa-infrastructure-setup.md
- **Enables**: All subsequent test implementations

## Implementation Notes

*To be filled during implementation:*

- Playwright version:
- Browsers installed:
- Page objects created:
