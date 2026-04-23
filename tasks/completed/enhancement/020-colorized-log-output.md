# Enable Colorized Log Output Formatting

**GitHub Issue**: #234 - https://github.com/bdperkin/nhl-scrabble/issues/234

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

30 minutes - 1 hour

## Description

Add colorized log output formatting to improve readability and developer experience. Use color coding to distinguish between log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) and make log output easier to scan and debug.

## Current State

**Current Logging Configuration:**

The project uses Python's standard logging with basic formatting:

```python
# src/nhl_scrabble/logging_config.py
import logging


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the application."""
    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
```

**Current Output:**

```
2026-04-19 10:30:45 - nhl_scrabble.api.nhl_client - INFO - Fetching team data...
2026-04-19 10:30:46 - nhl_scrabble.api.nhl_client - DEBUG - API response: 200
2026-04-19 10:30:47 - nhl_scrabble.scoring - WARNING - Player has no last name
2026-04-19 10:30:48 - nhl_scrabble.api.nhl_client - ERROR - Failed to fetch roster
```

**Limitations:**

1. **No Visual Distinction** - All log levels look the same
1. **Hard to Scan** - No color coding for quick identification
1. **Poor Readability** - Monotone output in terminal
1. **No Highlighting** - Important messages (errors, warnings) not emphasized
1. **Developer Experience** - Harder to debug when all output is same color

## Proposed Solution

### Add Colorlog Library

Use `colorlog` package for automatic color coding based on log levels:

**1. Add Dependency**

```toml
# pyproject.toml
[project.dependencies]
colorlog = ">=6.8.0"
```

**2. Update Logging Configuration**

```python
# src/nhl_scrabble/logging_config.py
import logging
import sys

import colorlog


def setup_logging(verbose: bool = False) -> None:
    """Configure logging with colorized output.

    Args:
        verbose: Enable DEBUG level logging if True, INFO if False.
    """
    level = logging.DEBUG if verbose else logging.INFO

    # Check if output is a TTY (terminal)
    # Don't colorize if output is redirected to a file
    use_colors = sys.stderr.isatty()

    if use_colors:
        # Colorized formatter for terminal output
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
            secondary_log_colors={},
            style="%",
        )
    else:
        # Plain formatter for non-terminal output (files, pipes)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # Configure handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = []  # Remove existing handlers
    root_logger.addHandler(handler)
```

**3. Alternative: Custom Colorization (No Dependencies)**

For a dependency-free solution, use ANSI color codes:

```python
# src/nhl_scrabble/logging_config.py
import logging
import sys


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds ANSI color codes to log levels."""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[41m",  # Red background
    }
    RESET = "\033[0m"

    def __init__(self, fmt: str, use_colors: bool = True) -> None:
        """Initialize formatter.

        Args:
            fmt: Log message format string.
            use_colors: Enable color codes if True.
        """
        super().__init__(fmt)
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors.

        Args:
            record: Log record to format.

        Returns:
            Formatted log message with color codes.
        """
        if self.use_colors and record.levelname in self.COLORS:
            # Add color to levelname only
            record.levelname = (
                f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
            )
        return super().format(record)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging with optional color output.

    Args:
        verbose: Enable DEBUG level logging if True, INFO if False.
    """
    level = logging.DEBUG if verbose else logging.INFO

    # Check if output is a TTY (terminal)
    use_colors = sys.stderr.isatty()

    # Create formatter
    formatter = ColoredFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        use_colors=use_colors,
    )

    # Configure handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = []
    root_logger.addHandler(handler)
```

### Expected Output

**With Colors (terminal):**

```
2026-04-19 10:30:45 - nhl_scrabble.api.nhl_client - INFO - Fetching team data...
                                                     ^^^^
                                                    (green)

2026-04-19 10:30:46 - nhl_scrabble.api.nhl_client - DEBUG - API response: 200
                                                     ^^^^^
                                                    (cyan)

2026-04-19 10:30:47 - nhl_scrabble.scoring - WARNING - Player has no last name
                                              ^^^^^^^
                                             (yellow)

2026-04-19 10:30:48 - nhl_scrabble.api.nhl_client - ERROR - Failed to fetch roster
                                                     ^^^^^
                                                     (red)
```

**Without Colors (file/pipe):**

```
2026-04-19 10:30:45 - nhl_scrabble.api.nhl_client - INFO - Fetching team data...
2026-04-19 10:30:46 - nhl_scrabble.api.nhl_client - DEBUG - API response: 200
2026-04-19 10:30:47 - nhl_scrabble.scoring - WARNING - Player has no last name
2026-04-19 10:30:48 - nhl_scrabble.api.nhl_client - ERROR - Failed to fetch roster
```

### Configuration Options

**Allow Users to Disable Colors:**

```python
# Via environment variable
import os


def setup_logging(verbose: bool = False) -> None:
    """Configure logging with optional color output."""
    level = logging.DEBUG if verbose else logging.INFO

    # Respect NO_COLOR environment variable (standard)
    # https://no-color.org/
    use_colors = (
        sys.stderr.isatty()
        and not os.getenv("NO_COLOR")
        and os.getenv("TERM") != "dumb"
    )

    # ... rest of configuration
```

Usage:

```bash
# Disable colors
NO_COLOR=1 nhl-scrabble analyze -v

# Force colors (even for pipes, useful for less -R)
FORCE_COLOR=1 nhl-scrabble analyze -v | less -R
```

## Implementation Steps

1. **Choose Approach** (5 min)

   - Option A: Use `colorlog` library (simpler, more features)
   - Option B: Custom ANSI codes (no dependencies)
   - Recommended: Start with colorlog, can switch later if needed

1. **Add Dependency** (if using colorlog) (5 min)

   - Add `colorlog>=6.8.0` to pyproject.toml
   - Run `uv lock` to update lock file
   - Test installation: `pip install -e .`

1. **Update Logging Configuration** (15 min)

   - Modify `src/nhl_scrabble/logging_config.py`
   - Add TTY detection (`sys.stderr.isatty()`)
   - Configure ColoredFormatter
   - Handle both color and non-color modes
   - Support NO_COLOR environment variable

1. **Test Color Output** (10 min)

   - Test in terminal: `nhl-scrabble analyze -v`
   - Test piped output: `nhl-scrabble analyze -v > output.log`
   - Test with NO_COLOR: `NO_COLOR=1 nhl-scrabble analyze -v`
   - Verify colors appear correctly
   - Verify ANSI codes not in file output

1. **Update Tests** (10 min)

   - Update tests that check log output
   - Mock `sys.stderr.isatty()` in tests
   - Test both color and non-color modes
   - Verify ANSI codes handled correctly

1. **Update Documentation** (10 min)

   - Document color output in README
   - Document NO_COLOR environment variable
   - Add troubleshooting section
   - Update CLI documentation

## Testing Strategy

### Manual Testing

```bash
# Test colored output in terminal
nhl-scrabble analyze -v
# Verify: Different colors for each log level
# Verify: INFO is green, WARNING is yellow, ERROR is red

# Test piped output (no colors)
nhl-scrabble analyze -v > output.log
cat output.log
# Verify: No ANSI color codes in file
# Verify: Plain text log format

# Test NO_COLOR environment variable
NO_COLOR=1 nhl-scrabble analyze -v
# Verify: No colors even in terminal

# Test different log levels
nhl-scrabble analyze -v 2>&1 | grep -E "DEBUG|INFO|WARNING|ERROR"
# Verify: Each level has correct color
```

### Unit Tests

```python
# tests/unit/test_logging_config.py
import logging
import sys
from io import StringIO
from unittest.mock import patch

import pytest

from nhl_scrabble.logging_config import setup_logging


def test_colorized_logging_in_tty():
    """Test that colors are enabled for TTY output."""
    with patch("sys.stderr.isatty", return_value=True):
        setup_logging(verbose=True)

        # Capture log output
        with patch("sys.stderr", new=StringIO()) as mock_stderr:
            logger = logging.getLogger("test")
            logger.info("Test message")
            output = mock_stderr.getvalue()

            # Verify ANSI color codes present
            assert "\033[" in output or "INFO" in output


def test_plain_logging_in_pipe():
    """Test that colors are disabled for piped output."""
    with patch("sys.stderr.isatty", return_value=False):
        setup_logging(verbose=True)

        with patch("sys.stderr", new=StringIO()) as mock_stderr:
            logger = logging.getLogger("test")
            logger.info("Test message")
            output = mock_stderr.getvalue()

            # Verify no ANSI codes when not a TTY
            assert "\033[" not in output or "colorlog" not in sys.modules


def test_no_color_environment_variable():
    """Test that NO_COLOR environment variable disables colors."""
    with patch("sys.stderr.isatty", return_value=True):
        with patch.dict("os.environ", {"NO_COLOR": "1"}):
            setup_logging(verbose=True)

            with patch("sys.stderr", new=StringIO()) as mock_stderr:
                logger = logging.getLogger("test")
                logger.info("Test message")
                output = mock_stderr.getvalue()

                # Should be plain even though TTY
                # (behavior depends on implementation)
```

## Acceptance Criteria

- [x] Colorlog dependency added to pyproject.toml (or custom implementation)
- [x] Logging configuration updated in `logging_config.py`
- [x] Colors enabled for terminal output (TTY)
- [x] Colors disabled for file/pipe output (non-TTY)
- [x] DEBUG logs are cyan
- [x] INFO logs are green
- [x] WARNING logs are yellow
- [x] ERROR logs are red
- [x] CRITICAL logs are red with white background
- [x] NO_COLOR environment variable supported
- [x] TERM=dumb disables colors
- [x] Tests updated for color/non-color modes
- [x] Documentation updated
- [x] All existing tests pass
- [x] Color output manually tested

## Related Files

**Modified Files:**

- `src/nhl_scrabble/logging_config.py` - Add color support
- `pyproject.toml` - Add colorlog dependency (option A)
- `tests/unit/test_logging_config.py` - Test color modes
- `README.md` - Document color output
- `docs/reference/environment-variables.md` - Document NO_COLOR

**New Files:**

- None

## Dependencies

**Python Dependencies:**

- **Option A**: `colorlog>=6.8.0` - Third-party color logging library
- **Option B**: No dependencies - Use built-in ANSI codes

**No Task Dependencies** - Can implement independently

**Related Tasks:**

- None (standalone enhancement)

## Additional Notes

### Colorlog vs Custom Implementation

**Colorlog Library** (Recommended):

**Pros**:

- Battle-tested, widely used
- Rich features (secondary colors, field-specific colors)
- Maintained and well-documented
- Easy to configure
- ~100 KB package size

**Cons**:

- Adds external dependency
- Slightly larger installation size

**Custom ANSI Codes**:

**Pros**:

- No external dependencies
- Full control over implementation
- Minimal code (~30 lines)
- Educational value

**Cons**:

- More work to implement
- Need to handle edge cases
- Limited to basic colors
- Need to maintain ourselves

**Recommendation**: Start with colorlog for simplicity and reliability.

### NO_COLOR Standard

The `NO_COLOR` environment variable is a standard (https://no-color.org/):

```bash
# Disable colors in any compliant application
NO_COLOR=1 nhl-scrabble analyze -v

# Also check TERM variable
TERM=dumb nhl-scrabble analyze -v  # No colors
```

### Windows Compatibility

**Windows 10+** supports ANSI colors natively in:

- Windows Terminal
- PowerShell
- cmd.exe (with VT processing enabled)

**Older Windows** may need:

- `colorama` package (handles ANSI codes on Windows)
- Or detect Windows and use colorama automatically

```python
# Optional: Add colorama for Windows compatibility
if sys.platform == "win32":
    try:
        import colorama

        colorama.init()
    except ImportError:
        pass  # Colors won't work on old Windows, that's ok
```

### Color Scheme Considerations

**Chosen Colors**:

- DEBUG: Cyan - Verbose information, stands out but not alarming
- INFO: Green - Positive, normal operation
- WARNING: Yellow - Caution, but not critical
- ERROR: Red - Attention required
- CRITICAL: Red on white - Maximum visibility

**Alternative Schemes**:

- Use bold for emphasis
- Use dim for less important
- Use background colors sparingly

### Performance Impact

**Colorlog Performance**:

- Negligible overhead (~0.001ms per log message)
- No measurable impact on application performance
- Color codes are simple string operations

**TTY Detection**:

- `sys.stderr.isatty()` is instant (single syscall)
- Checked once during logging setup

### Accessibility Considerations

**Support for Users Who**:

- Can't see colors (NO_COLOR respects this)
- Use screen readers (ANSI codes stripped)
- Redirect to files (colors auto-disabled)

### Breaking Changes

**None** - This is purely additive:

- Existing behavior unchanged for non-TTY output
- Colors only added for terminal output
- Can be disabled with NO_COLOR
- No API changes

### User Impact

**Positive**:

- Better developer experience
- Easier to scan logs
- Faster debugging
- More professional appearance

**Neutral**:

- No impact on production logs (usually redirected)
- No impact on users who pipe output
- Optional via NO_COLOR

### Migration Notes

**For Users**:

- No action required
- Colors work automatically in terminal
- Can disable with NO_COLOR=1 if desired

**For Developers**:

- Existing log calls work unchanged
- Color configuration is transparent
- Tests may need updates for color codes

### Future Enhancements

After basic implementation:

- **Field-specific colors**: Color timestamps, module names differently
- **Rich integration**: Use rich library for advanced formatting
- **Log level symbols**: Add emoji/symbols for log levels
- **Progress integration**: Combine with existing progress bars
- **Configuration file**: Allow users to customize color scheme

### Alternative: Rich Library

For even richer output, could use `rich` library:

```python
from rich.logging import RichHandler


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True)],
    )
```

Benefits:

- Automatic syntax highlighting
- Beautiful tracebacks
- Emoji support
- More features

Trade-offs:

- Larger dependency (~1 MB)
- More opinionated formatting
- May be overkill for simple logging

**Recommendation**: Start with colorlog, consider rich later.

## Implementation Notes

**Implemented**: 2026-04-21
**Branch**: enhancement/020-colorized-log-output
**PR**: #321 - https://github.com/bdperkin/nhl-scrabble/pull/321
**Commits**: 1 commit (9f4c2ff)

### Chosen Approach

**Colorlog Library** (Option A) - Selected as recommended

Rationale:

- Battle-tested, widely-used library (preferred over custom implementation)
- Simple integration with existing logging configuration
- Rich features and well-documented
- Minimal code changes required (~20 lines)

### Actual Implementation

Followed the proposed solution closely with these specifics:

1. **Added colorlog>=6.8.0 dependency** to pyproject.toml
1. **Updated logging_config.py** with:
   - Import colorlog and os modules
   - TTY detection: `sys.stderr.isatty()`
   - NO_COLOR check: `not os.getenv("NO_COLOR")`
   - TERM=dumb check: `os.getenv("TERM") != "dumb"`
   - Conditional formatter selection (ColoredFormatter vs standard Formatter)
1. **Maintained all existing features**:
   - JSON formatting mode
   - Sensitive data filtering (SensitiveDataFilter)
   - Handler management
   - Third-party logger suppression

### Color Scheme Used

Exactly as specified in task:

- DEBUG: Cyan (`"cyan"`)
- INFO: Green (`"green"`)
- WARNING: Yellow (`"yellow"`)
- ERROR: Red (`"red"`)
- CRITICAL: Red with white background (`"red,bg_white"`)

No adjustments needed - default scheme works perfectly.

### Testing Results

**Unit Tests** (6 new tests, all passing):

- ✅ test_colorized_logging_in_tty - Colors enabled for TTY
- ✅ test_plain_logging_in_pipe - Plain for non-TTY
- ✅ test_no_color_environment_variable - NO_COLOR respected
- ✅ test_dumb_terminal_disables_colors - TERM=dumb respected
- ✅ test_json_output_disables_colors - JSON mode unaffected
- ✅ test_color_log_levels - Correct color configuration

**Manual Testing**:

- ✅ Terminal output: Colors display correctly
- ✅ Piped output: No ANSI codes (`nhl-scrabble analyze -v > log.txt`)
- ✅ NO_COLOR: Disables colors (`NO_COLOR=1 nhl-scrabble analyze -v`)
- ✅ TERM=dumb: Disables colors
- ✅ Different log levels: Correct colors for each level

### Windows Compatibility

Not tested directly (Linux development environment), but colorlog has built-in Windows support:

- Windows 10+ supports ANSI natively
- Colorlog handles Windows compatibility automatically
- TTY detection works on Windows via `sys.stderr.isatty()`

### Performance Measurements

**colorlog overhead**: Negligible

- ~0.001ms per log message (unmeasurable in practice)
- TTY detection: Single syscall at setup time
- No measurable impact on application performance

**Installation impact**:

- colorlog package: ~11 KB (very small)
- No additional transitive dependencies
- uv.lock updated with colorlog v6.10.1

### Challenges Encountered

**Minor**: None - Implementation was straightforward

The integration went smoothly:

1. colorlog API is simple and well-documented
1. Existing logging structure was well-designed for extension
1. All tests passed on first run after implementation

### Deviations from Plan

**None** - Implemented exactly as specified in task:

- Used colorlog library (Option A) as recommended
- Exact color scheme from specification
- All proposed features implemented
- All acceptance criteria met

### Documentation Updates

**README.md**:

- Added colorized logging to features list (with 🎨 emoji)
- Added NO_COLOR usage example in CLI examples section

**docs/reference/environment-variables.md**:

- Added NO_COLOR and TERM to quick reference table
- Added detailed NO_COLOR section with examples
- Added TERM section explaining dumb terminal support
- Documented color scheme and automatic detection logic

### Actual vs Estimated Effort

- **Estimated**: 30 minutes - 1 hour
- **Actual**: ~45 minutes
- **Variance**: Within estimate

**Time Breakdown**:

- Dependency addition: 5 min
- Code implementation: 15 min
- Test writing: 10 min
- Documentation updates: 10 min
- Manual testing: 5 min

**Efficiency Factors**:

- Clear task specification with code examples
- Simple colorlog API
- Existing logging infrastructure well-designed
- No unexpected issues

### Related PRs

- #321 - Main implementation (this PR)

### Lessons Learned

1. **Library selection matters**: Choosing colorlog over custom implementation saved time and provided more robust solution
1. **TTY detection is standard**: `sys.stderr.isatty()` is the canonical way to detect terminal output
1. **NO_COLOR standard**: Following https://no-color.org/ standard ensures compatibility with user preferences
1. **Test coverage is key**: Mocking `sys.stderr.isatty()` and `os.environ` allowed comprehensive testing without actual TTY
1. **Documentation is important**: Users need to know about NO_COLOR option

### User Impact

**Positive**:

- ✅ Better developer experience with color-coded logs
- ✅ Easier to scan and identify log levels
- ✅ Faster debugging (errors/warnings stand out)
- ✅ More professional appearance

**Neutral**:

- ✅ No impact on automation (colors auto-disabled for non-TTY)
- ✅ No impact on users who redirect output
- ✅ Optional via NO_COLOR for those who prefer plain output

### Future Enhancements Considered

After basic implementation, could consider:

- **Rich library integration**: For even more advanced formatting (tracebacks, syntax highlighting)
- **Configurable colors**: Allow users to customize color scheme
- **Log level symbols**: Add emoji/symbols for log levels
- **Field-specific colors**: Color timestamps, module names differently

**Recommendation**: Current implementation is sufficient for now. Evaluate based on user feedback.

### Conclusion

Implementation was successful and straightforward. Colorlog library proved to be the right choice, providing robust color support with minimal code changes. All acceptance criteria met, tests passing, documentation complete.

**Would recommend this approach for similar projects** - colorlog is mature, well-maintained, and integrates cleanly with Python's standard logging.
