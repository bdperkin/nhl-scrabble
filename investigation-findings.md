# Phase 0 Investigation Findings: Web Module Test Coverage

**Date**: 2026-05-12
**Task**: #039 - Expand Test Coverage of Web Modules

## Executive Summary

**The task description was based on outdated/incorrect coverage data.** The web module does NOT have 0% coverage. Actual coverage is significantly higher than claimed.

## Actual Coverage Status

Running all web integration tests (`test_web*.py` + `test_api_server.py`):

| File                     | Task Claimed        | Actual Coverage | Statements | Missing | Gap to 95%                         |
| ------------------------ | ------------------- | --------------- | ---------- | ------- | ---------------------------------- |
| `web/__init__.py`        | 0% (3 statements)   | **100%** ✅     | 3          | 0       | **None - Complete!**               |
| `web/app.py`             | 0% (783 statements) | **49.95%**      | 783        | 379     | Need +45.05% (353 more statements) |
| `web/utils/__init__.py`  | 0% (2 statements)   | **100%** ✅     | 2          | 0       | **None - Complete!**               |
| `web/utils/auto_link.py` | 0% (53 statements)  | **85.33%**      | 53         | 4       | Need +9.67% (5 more statements)    |

**Total**: 841 statements total, 462 covered (54.94%), 379 missing

## Key Findings

### 1. Tests DO Work ✅

- Integration tests in `tests/integration/test_web*.py` correctly import modules:
  ```python
  from nhl_scrabble.web.app import app
  ```
- 138 tests pass, providing substantial coverage
- FastAPI TestClient DOES contribute to coverage (contrary to hypothesis)

### 2. Coverage Collection Works ✅

- pytest-cov is correctly configured
- Coverage is being collected for all imports
- No configuration issues found

### 3. Why Not 0%?

The task description appears to be based on either:

- Outdated coverage report (before integration tests were written)
- Coverage report from a subset of tests (not all web tests)
- Misread coverage data (perhaps diff-cover showing 0% on a specific PR)

### 4. What's Actually Missing?

**web/app.py (379 statements, 49.95% → 95% target):**

Missing coverage areas (from coverage report):

```
Lines: 140-143, 175-191, 217-220, 235, 254-328, 342-412, 469, 625-646,
       689-711, 725, 737, 755-766, 829, 848-880, 903-1021, 1066-1068,
       1121-1127, 1137, 1144, 1210-1211, 1259-1261, 1295, 1306,
       1336-1337, 1371-1373, 1392-1490, 1510-1595, 1614-1712,
       1732-1823, 1843-1940, 1988-1990, 2027, 2082-2084, 2103-2134,
       2189-2191, 2240-2242
```

These are likely:

- Error handling paths not tested
- Edge cases in endpoint handlers
- Locale/i18n code paths
- Template filter functions
- Data transformation logic
- Error pages (404, 500)
- Security middleware edge cases

**web/utils/auto_link.py (4 statements, 85.33% → 95% target):**

Missing coverage (lines 147-153):

```python
# Likely edge cases in auto-linking logic
# Possibly: overlapping matches, special character handling, etc.
```

**VERY SMALL GAP** - only 4 statements!

## Test File Analysis

**Existing Tests (~2,393 lines across 6 files):**

1. `test_web.py` (~500 lines) - Basic endpoints, health, CORS ✅
1. `test_web_routes.py` (~400 lines) - Route functionality ✅
1. `test_web_api.py` (~350 lines) - API endpoints ✅
1. `test_web_i18n.py` (~300 lines) - Internationalization ✅
1. `test_web_infrastructure.py` (~250 lines) - Infrastructure ✅
1. `test_web_interactivity.py` (~150 lines) - Interactive features ✅

All tests are integration tests using FastAPI TestClient. They work well but don't cover all code paths.

## Revised Implementation Strategy

**Original task estimated 20-28 hours** based on 0% coverage.
**Actual work needed:** Much less - we're starting from 49.95% (app.py) and 85.33% (auto_link.py)!

### Revised Phases

1. ~~**Phase 0: Investigation** (2-3 hours)~~ ✅ **COMPLETE**

   - Findings documented here
   - Root cause identified: Outdated task data

1. **Phase 1: Unit Tests for web/app.py** (6-8 hours, reduced from 8-10)

   - Focus on 379 missing statements
   - Test error handlers, edge cases, template logic
   - Add unit tests with mocks for untested code paths

1. **Phase 2: Complete auto_link.py coverage** (30 minutes, reduced from 2-3 hours)

   - **Only 4 statements missing!**
   - Likely just edge case tests (lines 147-153)
   - Should be very quick

1. **Phase 3: Verify and document** (1 hour)

   - Run full test suite
   - Verify 95% coverage targets met
   - Update documentation

**Revised Total Estimate: 8-12 hours** (down from 20-28 hours)

## Code Paths Still Needing Tests

### Priority 1: Error Handling (High Impact)

- 404 error handler code paths
- 500 error handler code paths
- NHL API error handling in web context
- Timeout handling
- Exception cases in endpoints

### Priority 2: Edge Cases (Medium Impact)

- Locale detection edge cases
- Empty/invalid query parameters
- Missing/malformed data from API
- Template rendering errors
- Security middleware edge cases

### Priority 3: Utility Functions (Low Impact)

- Template filter functions
- Data transformation helpers
- Auto-link edge cases (4 statements)

## Recommendations

1. **Update task description** to reflect actual coverage (not 0%)
1. **Reduce effort estimate** from 20-28h to 8-12h
1. **Focus on missing 379 statements** in web/app.py
1. **Quick win: auto_link.py** - only 4 statements to cover
1. **Keep existing integration tests** - they provide good baseline coverage

## Testing Patterns That Work

The existing integration tests show the right pattern:

```python
from nhl_scrabble.web.app import app  # Direct import ✅


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_endpoint(client):
    response = client.get("/")  # Tests via HTTP ✅
    # This DOES contribute to coverage!
```

For missing coverage, we need to add:

1. More edge case tests (error conditions, invalid inputs)
1. Unit tests for template filters/helpers
1. Unit tests for security middleware
1. Tests for error handlers

## Conclusion

**The mystery is solved:** The task description was based on incorrect data. Coverage is actually 54.94% overall (49.95% for app.py, 85.33% for auto_link.py, 100% for __init__ files).

**Path forward:** Add targeted unit tests for the 379 missing statements in web/app.py and the 4 missing statements in auto_link.py to reach 95% coverage target.

**Effort reduced by ~60%** thanks to existing integration test coverage.
