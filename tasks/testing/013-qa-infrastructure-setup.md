# QA Infrastructure Setup

**GitHub Issue**: #312 - https://github.com/bdperkin/nhl-scrabble/issues/312

**Parent Task**: testing/012-qa-automation-framework.md

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

4-6 hours

## Description

Create the QA directory structure, configuration files, and foundational infrastructure for the automated testing framework. This establishes the foundation for all subsequent QA automation work.

## Current State

**No QA Infrastructure:**

- No `./qa/` directory exists
- No automation framework configuration
- No dedicated QA testing structure

## Proposed Solution

### Directory Structure

```
qa/
├── README.md                   # QA framework overview
├── web/                        # Web automation tests
│   ├── README.md              # Web testing guide
│   ├── pyproject.toml         # Dependencies
│   ├── playwright.config.py   # Playwright config
│   ├── conftest.py            # Pytest fixtures
│   ├── pytest.ini             # Pytest configuration
│   ├── .gitignore             # QA-specific ignores
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── functional/
│   │   │   └── __init__.py
│   │   ├── visual/
│   │   │   └── __init__.py
│   │   ├── performance/
│   │   │   └── __init__.py
│   │   └── accessibility/
│   │       └── __init__.py
│   ├── pages/
│   │   └── __init__.py
│   ├── fixtures/
│   │   └── __init__.py
│   ├── screenshots/           # Visual test baselines
│   │   └── .gitkeep
│   ├── reports/               # Test reports
│   │   └── .gitkeep
│   └── scripts/
│       └── __init__.py
├── api/                        # Future: API tests
│   └── README.md
├── cli/                        # Future: CLI tests
│   └── README.md
├── tui/                        # Future: TUI tests
│   └── README.md
└── sdk/                        # Future: SDK tests
    └── README.md
```

### Configuration Files

**pyproject.toml:**

```toml
[project]
name = "nhl-scrabble-qa-web"
version = "1.0.0"
description = "Web automation tests for NHL Scrabble"
requires-python = ">=3.10"

dependencies = [
    "playwright>=1.40.0",
    "pytest>=7.4.0",
    "pytest-playwright>=0.4.0",
    "pytest-html>=4.1.0",
    "pytest-xdist>=3.5.0",
    "pillow>=10.0.0",
    "axe-playwright>=0.1.0",
    "locust>=2.20.0",
]

[project.optional-dependencies]
dev = [
    "pytest-cov>=4.1.0",
    "pytest-timeout>=2.2.0",
]
```

**playwright.config.py:**

```python
from playwright.sync_api import sync_playwright

# Playwright configuration
config = {
    "base_url": "http://localhost:5000",
    "timeout": 30000,
    "screenshot_on_failure": True,
    "video_on_failure": True,
    "trace_on_failure": True,
}

BROWSERS = ["chromium", "firefox", "webkit"]
HEADLESS = True
SLOW_MO = 0  # Slow down by N ms for debugging
```

**pytest.ini:**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --tb=short
    --strict-markers
    --html=reports/report.html
    --self-contained-html
markers =
    functional: Functional tests
    visual: Visual regression tests
    performance: Performance tests
    accessibility: Accessibility tests
    smoke: Smoke tests (critical paths)
    regression: Regression tests
```

**.gitignore:**

```
# Test artifacts
__pycache__/
*.pyc
.pytest_cache/
.coverage
htmlcov/
reports/*.html
reports/*.xml

# Playwright artifacts
test-results/
traces/
videos/
downloads/

# Screenshots (except baselines)
screenshots/*-actual.png
screenshots/*-diff.png

# Performance test results
*.log
locust-*.csv
```

## Implementation Steps

1. **Create Directory Structure** (1h)

   - Create `qa/` and subdirectories
   - Add `__init__.py` files
   - Add `.gitkeep` for empty directories
   - Create stub directories for future tests

1. **Configuration Files** (1-2h)

   - Create `pyproject.toml`
   - Create `playwright.config.py`
   - Create `pytest.ini`
   - Create `.gitignore`

1. **Documentation** (1-2h)

   - Write `qa/README.md`
   - Write `qa/web/README.md`
   - Document directory structure
   - Add setup instructions

1. **Makefile Integration** (30min-1h)

   - Add QA targets to main Makefile
   - Test installation commands
   - Verify integration

1. **Verification** (30min)

   - Test directory structure
   - Verify configurations
   - Test Makefile targets

## Testing Strategy

```bash
# Verify directory structure
ls -R qa/

# Test Makefile targets
make qa-install

# Verify Playwright installation
playwright --version
```

## Acceptance Criteria

- [ ] All directories created with proper structure
- [ ] Configuration files created and valid
- [ ] Documentation comprehensive
- [ ] Makefile targets functional
- [ ] .gitignore appropriate
- [ ] Stub directories for future tests
- [ ] All __init__.py files present
- [ ] README files in all directories

## Related Files

**New Files:**

- All files in `qa/` directory structure
- Makefile (QA targets section)

**Modified Files:**

- `.gitignore` (root - add qa artifacts)
- `CLAUDE.md` (document QA structure)

## Dependencies

- Parent task: testing/012-qa-automation-framework.md
- No technical dependencies

## Additional Notes

### Stub Directories

Create README.md in each stub directory explaining future purpose:

```markdown
# API Automation Tests (Future)

This directory will contain automated API tests for the NHL Scrabble API.

**Planned test types:**
- Contract testing
- Response validation
- Error handling
- Performance testing

**Tools under consideration:**
- requests/httpx
- pytest
- Tavern (API testing framework)
```

Similar READMEs for cli/, tui/, sdk/.

## Implementation Notes

*To be filled during implementation:*

- Date completed:
- Actual effort:
- Directory count:
- File count:
