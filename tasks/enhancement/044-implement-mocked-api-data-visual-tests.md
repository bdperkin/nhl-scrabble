# Implement Mocked API Data for Visual Regression Tests

**Category**: Enhancement
**Priority**: **LOW** - Testing Infrastructure
**Estimated Effort**: 6-8 hours
**Status**: Active
**GitHub Issue**: [#476](https://github.com/bdperkin/nhl-scrabble/issues/476) - Implement Mocked API Data for Visual Regression Tests

## Overview

Implement mocked or fixed NHL API data for visual regression tests to make them deterministic and reliable. Currently, visual tests capture screenshots of live NHL API data (player stats, scores, standings), which changes constantly and causes baseline mismatches even when the UI is correctly rendered.

## Problem Description

Visual regression tests in `qa/web/tests/visual/` use live NHL API data from the production NHL API endpoint. This causes several issues:

**Current Issues:**
- Visual tests fail in CI due to data differences (not UI bugs)
- Baselines generated locally show different data than CI sees
- Tests marked as `continue-on-error: true` in CI (non-blocking) due to unreliability
- Pixel differences range from 163,185 to 217,302 pixels on data-heavy pages
- Impossible to maintain stable baselines for pages displaying dynamic data

**Example Failure:**
```
AssertionError: Snapshots does not match
E   assert 163185 == 0  # 163,185 pixels differ due to different player names/scores
```

**Root Cause:**
1. Baselines generated at time T₁ with NHL API data snapshot
2. CI runs at time T₂ with updated NHL API data
3. Player stats, team scores, and standings have changed
4. Screenshots differ pixel-by-pixel despite identical UI rendering

**Background:**
- **Documented**: `qa/web/tests/visual/README.md` (Known Limitations section)
- **Related PR**: #475 - Fix web routes and update visual baselines
- **Related Issue**: #474 - Fix `/teams`, `/divisions`, `/conferences`, `/playoffs`, `/stats` routes showing same page
- **Merged**: 2026-05-01 (commit 37c51b7)

## Proposed Solution

### Approach 1: API Response Mocking (Recommended)

Mock NHL API responses at the application level using fixed JSON fixtures:

**Implementation:**
1. Create JSON fixture files with stable NHL data snapshots:
   - `qa/web/tests/visual/fixtures/nhl_standings.json`
   - `qa/web/tests/visual/fixtures/nhl_rosters.json`
2. Implement pytest fixture to mock `NHLClient` responses
3. Use `pytest-mock` or `unittest.mock` to intercept API calls
4. Return consistent fixture data for all visual test runs

**Benefits:**
- ✅ Deterministic test results
- ✅ Fast (no network calls)
- ✅ Works in all environments (local, CI, Docker)
- ✅ Can test edge cases with crafted data

**Drawbacks:**
- ❌ Fixtures need periodic updates for realism
- ❌ Doesn't test actual API integration (covered by functional tests)

### Approach 2: VCR-style Request Recording

Use `pytest-vcr` or similar to record/replay HTTP requests:

**Implementation:**
1. Install `pytest-vcr` or `vcrpy`
2. Record NHL API responses once
3. Replay recorded responses in tests
4. Update cassettes when API schema changes

**Benefits:**
- ✅ Real API responses (initially)
- ✅ Deterministic replay
- ✅ Can update cassettes when needed

**Drawbacks:**
- ❌ More complex setup
- ❌ Cassettes can be large
- ❌ Requires maintenance when API changes

### Approach 3: Test Database with Seed Data

Create a test database with fixed player/team data:

**Implementation:**
1. Create seed data SQL/JSON files
2. Load seed data before visual tests
3. Configure app to use test database
4. Clean up after tests

**Benefits:**
- ✅ Most realistic data flow
- ✅ Tests full application stack

**Drawbacks:**
- ❌ Requires database setup
- ❌ More complex test environment
- ❌ Slower than mocking

**Recommendation**: **Approach 1 (API Response Mocking)** - Simplest, fastest, most maintainable.

## Implementation Plan

### Phase 1: Create Fixture Data (2 hours)

1. **Capture Current NHL API Data**:
   - Run `nhl-scrabble analyze` locally
   - Save API responses to JSON files
   - Include standings, rosters, player stats

2. **Create Fixture Files**:
   ```bash
   mkdir -p qa/web/tests/visual/fixtures/
   # Create fixture files:
   qa/web/tests/visual/fixtures/
   ├── nhl_standings.json          # Team standings data
   ├── nhl_rosters.json             # Player roster data (all teams)
   └── README.md                    # Fixture documentation
   ```

3. **Document Fixture Structure**:
   - Add README.md explaining fixture format
   - Document how to update fixtures
   - Include capture date and NHL season info

### Phase 2: Implement Mocking Infrastructure (2-3 hours)

1. **Create Mock Fixtures** (`qa/web/tests/visual/conftest.py`):
   ```python
   import json
   from pathlib import Path
   import pytest
   from unittest.mock import Mock, patch

   FIXTURES_DIR = Path(__file__).parent / "fixtures"

   @pytest.fixture
   def nhl_standings_data():
       """Load NHL standings fixture data."""
       with open(FIXTURES_DIR / "nhl_standings.json") as f:
           return json.load(f)

   @pytest.fixture
   def nhl_rosters_data():
       """Load NHL rosters fixture data."""
       with open(FIXTURES_DIR / "nhl_rosters.json") as f:
           return json.load(f)

   @pytest.fixture
   def mock_nhl_client(nhl_standings_data, nhl_rosters_data):
       """Mock NHLClient with fixed fixture data."""
       with patch("nhl_scrabble.api.nhl_client.NHLClient") as mock:
           client_instance = Mock()
           client_instance.get_standings.return_value = nhl_standings_data
           client_instance.get_roster.side_effect = lambda team: nhl_rosters_data.get(team)
           mock.return_value.__enter__.return_value = client_instance
           yield client_instance
   ```

2. **Update Visual Test Configuration**:
   - Modify `qa/web/tests/visual/conftest.py` to use mocked client
   - Ensure fixtures are applied to all visual tests
   - Add environment variable to toggle mocking (enable for visual tests only)

3. **Test Mock Implementation**:
   - Run single visual test with mock
   - Verify data is consistent
   - Check screenshots match expected content

### Phase 3: Regenerate Baselines (1-2 hours)

1. **Run Visual Tests with Mocked Data**:
   ```bash
   ./scripts/pytest-playwright qa/web/tests/visual/ --update-snapshots \
     --browser chromium --browser firefox --browser webkit
   ```

2. **Verify Baseline Consistency**:
   - Run tests multiple times
   - Confirm baselines remain stable (pixel-perfect matches)
   - Test in different environments (local, Docker, CI)

3. **Commit New Baselines**:
   ```bash
   git add qa/web/tests/visual/__snapshots__/
   git add qa/web/tests/visual/fixtures/
   git commit -m "test(visual): Regenerate baselines with mocked API data"
   ```

### Phase 4: CI Integration (1 hour)

1. **Update CI Workflow** (`.github/workflows/qa-automation.yml`):
   - Remove `continue-on-error: true` from visual tests (now reliable)
   - Make visual tests blocking (failures indicate real UI bugs)
   - Add step to verify fixtures exist before tests

2. **Update Documentation** (`qa/web/tests/visual/README.md`):
   - Remove "Known Limitations" section
   - Update "Usage" section with mocking details
   - Add "Fixture Management" section:
     - How to update fixtures
     - When to update fixtures
     - How to capture new API data

3. **Test CI Integration**:
   - Push changes to feature branch
   - Verify visual tests pass in CI
   - Confirm tests are now blocking

### Phase 5: Documentation and Cleanup (1 hour)

1. **Update README Files**:
   - `qa/web/tests/visual/README.md`: Mocking approach, fixture management
   - `qa/web/README.md`: Visual test reliability improvements
   - `CLAUDE.md`: Update QA automation section

2. **Add Maintenance Notes**:
   - Document when to update fixtures (e.g., NHL season changes)
   - Add script to capture fresh fixture data: `scripts/capture-nhl-fixtures`
   - Include fixture update workflow in CONTRIBUTING.md

3. **Clean Up**:
   - Remove old baseline comments about non-blocking tests
   - Update task file with implementation notes
   - Close related GitHub issue

## Acceptance Criteria

- [ ] JSON fixture files created with stable NHL data snapshots
- [ ] Pytest fixtures implemented to mock `NHLClient` responses
- [ ] Visual tests use mocked data instead of live API
- [ ] All visual baselines regenerated with mocked data
- [ ] Visual tests pass consistently (100% pixel-perfect matches)
- [ ] Tests validated in Docker environment (matches CI)
- [ ] Tests validated in CI (all browsers: chromium, firefox, webkit)
- [ ] `continue-on-error: true` removed from CI workflow (tests now blocking)
- [ ] Documentation updated:
  - [ ] `qa/web/tests/visual/README.md` (remove Known Limitations, add Fixture Management)
  - [ ] `qa/web/README.md` (mention reliability improvement)
  - [ ] `CLAUDE.md` (update QA section)
- [ ] Fixture update script created: `scripts/capture-nhl-fixtures`
- [ ] All tests pass (unit, integration, functional, visual)
- [ ] Pre-commit hooks pass
- [ ] Type checking passes (mypy, ty)

## Testing Strategy

### Unit Tests

**File**: `qa/web/tests/unit/test_visual_fixtures.py`

Test fixture loading and validation:
- [ ] Test fixture files exist and are valid JSON
- [ ] Test fixture structure matches NHL API schema
- [ ] Test mock fixtures return correct data
- [ ] Test fixture data completeness (all teams, all players)

### Integration Tests

**File**: `qa/web/tests/integration/test_visual_mocking.py`

Test mocking integration:
- [ ] Test application uses mocked data when configured
- [ ] Test all pages render with mocked data
- [ ] Test mocked data doesn't affect functional tests
- [ ] Test fixture toggle (live API vs mocked for different test types)

### Visual Regression Tests

**Files**: `qa/web/tests/visual/test_*.py`

Verify deterministic behavior:
- [ ] Run visual tests 10 times consecutively (all must pass)
- [ ] Generate baselines, delete, regenerate (must be pixel-perfect identical)
- [ ] Test across all browsers (chromium, firefox, webkit)
- [ ] Test in Docker environment (matches CI)

## Timeline

- **Phase 1**: 2 hours (Fixture creation)
- **Phase 2**: 2-3 hours (Mocking implementation)
- **Phase 3**: 1-2 hours (Baseline regeneration)
- **Phase 4**: 1 hour (CI integration)
- **Phase 5**: 1 hour (Documentation)
- **Total**: 7-9 hours (estimated 6-8h with focus)

## Related Tasks

- ✅ **task 016**: Fix web routes showing same page (completed, PR #475)
- 🔄 **task 022**: Generate visual regression test baselines (completed, but will need regeneration with mocked data)

## Related Files

**Visual Test Infrastructure:**
- `qa/web/tests/visual/conftest.py` - Test configuration (will add mocking)
- `qa/web/tests/visual/__snapshots__/` - Baseline images (will regenerate)
- `qa/web/tests/visual/fixtures/` - NEW: Fixture data files
- `qa/web/tests/visual/README.md` - Documentation (will update)

**Application Code:**
- `src/nhl_scrabble/api/nhl_client.py` - NHLClient (will be mocked)
- `src/nhl_scrabble/web/app.py` - FastAPI application
- `src/nhl_scrabble/web/routes.py` - Route handlers

**CI/CD:**
- `.github/workflows/qa-automation.yml` - QA workflow (will update)

**Scripts:**
- `scripts/pytest-playwright` - Docker wrapper for Playwright tests
- `scripts/capture-nhl-fixtures` - NEW: Script to capture fresh fixture data

## References

- **PR**: #475 - Fix web routes and update visual baselines
- **Issue**: #474 - Fix web routes showing same page
- **Documentation**: `qa/web/tests/visual/README.md` (Known Limitations section)
- **Merged**: 2026-05-01 (commit 37c51b7)
- **Related Visual Baseline Update**: commit e60b33f

## Notes

- **Priority Rationale**: LOW priority because visual tests are currently non-blocking in CI and functional QA tests provide adequate coverage. However, this enhancement would improve test reliability and catch real UI regressions more effectively.

- **Maintenance**: Fixtures should be updated:
  - When NHL season changes (rosters, standings reset)
  - When major UI changes affect data display
  - Annually at minimum to keep data realistic

- **Alternative Approaches Considered**:
  - Using pytest-vcr for HTTP recording (more complex, larger files)
  - Test database with seed data (requires database setup)
  - Live API with retry logic (doesn't solve determinism issue)

- **Benefits**:
  - Visual tests become blocking in CI (catch real bugs)
  - Faster test execution (no network calls)
  - Consistent baselines across all environments
  - Can test edge cases with crafted data
  - Reduces false positive rate to near-zero
