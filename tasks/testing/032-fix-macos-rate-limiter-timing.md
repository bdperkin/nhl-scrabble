# Fix macOS Test Failure: test_fractional_tokens

**GitHub Issue**: #538 - https://github.com/bdperkin/nhl-scrabble/issues/538

## Priority

**MEDIUM** - Platform Support / Reliability

## Estimated Effort

3-4 hours

## Description

Fix test_rate_limiter.py::TestRateLimiterEdgeCases::test_fractional_tokens failing on macOS. Test fails with `assert True is False`, indicating a timing or precision issue specific to macOS platform.

## Current State

**Test failing on macOS:**
```
FAILED tests/unit/test_rate_limiter.py::TestRateLimiterEdgeCases::test_fractional_tokens
assert True is False
```

**Affected Platforms:**
- macOS (observed on Python 3.13, likely affects other versions)
- Windows: ✅ Passing
- Ubuntu: ✅ Passing

**Discovery:**
- Identified in nightly workflow run: https://github.com/bdperkin/nhl-scrabble/actions/runs/25503287135
- Intermittent failure (timing-dependent)

## Root Cause Analysis

**Likely Causes:**

1. **macOS Clock Precision:**
   - `time.time()` precision varies by platform
   - macOS may have different system clock granularity
   - Timing-sensitive assertions may fail at boundaries

2. **Sleep Accuracy:**
   - `time.sleep()` is not perfectly accurate
   - May sleep slightly longer or shorter than requested
   - macOS scheduler behavior differs from Linux

3. **Fractional Token Calculations:**
   - Test name suggests fractional rate limiting
   - Floating-point arithmetic precision
   - Rounding errors accumulate differently on macOS

4. **Race Conditions:**
   - Test may have timing race conditions
   - macOS thread scheduling differs
   - Brief delays cause test to fail

## Investigation Steps

### Step 1: Read the Test

```bash
# Examine test implementation
grep -A 50 "def test_fractional_tokens" tests/unit/test_rate_limiter.py
```

**Key questions:**
- What timing assertions are made?
- How tight are the timing tolerances?
- Does it use `time.sleep()` and `time.time()`?
- What is the "fractional tokens" concept?

### Step 2: Check Rate Limiter Implementation

```bash
# Review rate limiter code
cat src/nhl_scrabble/rate_limiter.py | grep -A 20 "class.*RateLimiter"
```

### Step 3: Understand Token Bucket Algorithm

Rate limiters typically use token bucket algorithm:
```python
# Tokens replenish over time
tokens_added = (time.time() - last_time) * rate
current_tokens = min(max_tokens, previous_tokens + tokens_added)

# Fractional tokens: 0.5 tokens, 1.5 tokens, etc.
# Timing precision critical for correct calculations
```

### Step 4: Run Test Locally (macOS if available)

```bash
# Run test multiple times to see if flaky
for i in {1..10}; do
    pytest tests/unit/test_rate_limiter.py::TestRateLimiterEdgeCases::test_fractional_tokens -v
done
```

## Proposed Solution

### Option 1: Add Timing Tolerance

Most likely fix - add margin for timing variations:

```python
def test_fractional_tokens(self):
    """Test rate limiter with fractional token rates."""
    limiter = RateLimiter(rate=0.5, capacity=2.0)  # 0.5 tokens/sec

    # Consume some tokens
    assert limiter.acquire(1.0)

    # Wait for partial replenishment
    time.sleep(1.0)  # Should add 0.5 tokens

    # BEFORE (too strict):
    assert limiter.available_tokens() == 1.5

    # AFTER (with tolerance):
    # Allow for timing variations (±0.1 tokens)
    tokens = limiter.available_tokens()
    assert 1.4 <= tokens <= 1.6, f"Expected ~1.5 tokens, got {tokens}"
```

### Option 2: Mock Time

Use freezegun or similar to control time:

```python
from freezegun import freeze_time
import time

def test_fractional_tokens(self):
    """Test rate limiter with fractional token rates."""
    with freeze_time("2024-01-01 12:00:00") as frozen_time:
        limiter = RateLimiter(rate=0.5, capacity=2.0)

        # Consume tokens
        limiter.acquire(1.0)

        # Advance time precisely
        frozen_time.tick(delta=timedelta(seconds=1.0))

        # Exact comparison works because time is mocked
        assert limiter.available_tokens() == 1.5
```

### Option 3: Use unittest.mock

Mock `time.time()` for deterministic behavior:

```python
from unittest.mock import patch

def test_fractional_tokens(self):
    """Test rate limiter with fractional token rates."""
    current_time = 1000.0

    def mock_time():
        return current_time

    with patch('time.time', side_effect=mock_time):
        limiter = RateLimiter(rate=0.5, capacity=2.0)
        limiter.acquire(1.0)

        # Advance mocked time
        current_time += 1.0

        # Exact comparison works with mocked time
        assert limiter.available_tokens() == 1.5
```

### Option 4: Skip on macOS (Last Resort)

Only if test is fundamentally incompatible with macOS timing:

```python
import sys
import pytest

@pytest.mark.skipif(
    sys.platform == "darwin",
    reason="macOS clock precision causes timing failures"
)
def test_fractional_tokens(self):
    # Test logic
    pass
```

**Note:** Skipping should be last resort; prefer fixing timing assumptions.

## Implementation Steps

1. **Reproduce failure** (if macOS available):
   ```bash
   pytest tests/unit/test_rate_limiter.py::TestRateLimiterEdgeCases::test_fractional_tokens -v --count=20
   ```

2. **Analyze test timing requirements**:
   - Identify exact vs approximate assertions
   - Check sleep durations and tolerances
   - Review timing-dependent calculations

3. **Add debug output** to understand failure:
   ```python
   print(f"Platform: {sys.platform}")
   print(f"Expected: 1.5, Got: {limiter.available_tokens()}")
   print(f"Time precision: {time.get_clock_info('time')}")
   ```

4. **Implement fix** (likely Option 1: timing tolerance):
   - Replace exact assertions with range checks
   - Add reasonable tolerance (±0.1 or ±0.05)
   - Document why tolerance is needed

5. **Test on all platforms**:
   - macOS: Should pass consistently
   - Linux: Should still pass
   - Windows: Should still pass

## Testing Strategy

**Local Testing (macOS):**
```bash
# Run test multiple times
pytest tests/unit/test_rate_limiter.py::TestRateLimiterEdgeCases::test_fractional_tokens -v --count=50

# Run all rate limiter tests
pytest tests/unit/test_rate_limiter.py -v

# Check for other timing-sensitive tests
pytest tests/unit/test_rate_limiter.py -v -k "time"
```

**CI Testing:**
```bash
# Push and verify on all platforms
git push origin feature/fix-macos-rate-limiter
```

**Stress Testing:**
```bash
# Run under load to find race conditions
pytest tests/unit/test_rate_limiter.py -v -n auto --count=100
```

## Acceptance Criteria

- [ ] Test passes consistently on macOS (100 consecutive runs)
- [ ] Test still passes on Ubuntu
- [ ] Test still passes on Windows
- [ ] Timing tolerance clearly documented in test
- [ ] No flakiness under parallel execution
- [ ] Other rate limiter tests still pass
- [ ] Performance not significantly degraded

## Related Files

- `tests/unit/test_rate_limiter.py` - Test file (TestRateLimiterEdgeCases class)
- `src/nhl_scrabble/rate_limiter.py` - Rate limiter implementation
- `.github/workflows/nightly.yml` - Workflow (can be updated to remove macOS experimental if needed)

## Dependencies

None - standalone bug fix

## Related Issues

Windows issues (separate failures):
- #533: test_search_to_file
- #534: test_success_messages_translatable
- #535: Windows permission test failures
- #536: test_save_season_unicode_data
- #537: test_list_continues_after_individual_error

## Additional Notes

**Platform Clock Differences:**
- Linux: High-resolution monotonic clock available
- macOS: Clock resolution varies (can be ~1ms)
- Windows: Different clock implementation
- All platforms: `time.sleep()` not perfectly accurate

**Rate Limiter Testing Best Practices:**
- Avoid exact timing assertions
- Use tolerance ranges for time-based calculations
- Consider mocking time for deterministic tests
- Test logic separately from timing precision
- Use monotonic time (`time.monotonic()`) when possible

**Flaky Test Detection:**
```bash
# Run test many times to check for flakiness
pytest-flakefinder tests/unit/test_rate_limiter.py::TestRateLimiterEdgeCases::test_fractional_tokens
```

**Time Mocking Libraries:**
- `freezegun`: Popular time-mocking library
- `time-machine`: Faster alternative
- `unittest.mock`: Built-in, no dependencies

**Similar Issues in Testing:**
- pytest itself has timing-tolerant test utilities
- Many projects use ±10% tolerance for timing tests
- Some use pytest-timeout to catch hanging tests

**Timing Test Patterns:**
```python
# AVOID: Exact time assertions
assert elapsed_time == 1.0

# PREFER: Range assertions
assert 0.95 <= elapsed_time <= 1.05

# BEST: Mock time for deterministic behavior
with freeze_time():
    # Test logic
    pass
```

## Implementation Notes

*To be filled during implementation:*
- Test failure pattern analyzed (consistent vs intermittent)
- Root cause identified (precision vs race vs calculation)
- Fix approach chosen (tolerance vs mock vs skip)
- Tolerance value selected (if applicable)
- Timing measurements on macOS
- Test stability verified (N consecutive passes)
- Files modified
- Date of fix completion
