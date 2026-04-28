# Implement File-Based Logging for Uvicorn Web Server

**GitHub Issue**: [#398](https://github.com/bdperkin/nhl-scrabble/issues/398)

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

3-5 hours

## Description

Add permanent file-based logging capability to the Uvicorn web server to enable log retention, monitoring, and debugging in production environments. Currently, all logs (application logs and Uvicorn access logs) only go to STDOUT/STDERR with no file persistence.

## Current State

All logging goes to standard streams only:

**Application Logs** (`src/nhl_scrabble/logging_config.py`):
```python
def setup_logging(verbose: bool = False, json_output: bool = False, sanitize_logs: bool = True) -> None:
    # ...
    # Create console handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(log_level)

    # Only StreamHandler configured - no file output
    root_logger.addHandler(handler)
```

**Uvicorn Server Logs** (`src/nhl_scrabble/cli.py`):
```python
uvicorn.run(
    app,
    host=host,
    port=port,
    reload=reload,
    log_level="info",
    # No log_config parameter - uses defaults (STDOUT/STDERR only)
)
```

**To capture logs to files**, users must manually redirect:
```bash
nhl-scrabble serve > logs/access.log 2> logs/error.log
```

## Proposed Solution

### 1. Enhance `setup_logging()` with FileHandler Support

Add optional file-based logging with rotation:

```python
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging(
    verbose: bool = False,
    json_output: bool = False,
    sanitize_logs: bool = True,
    log_file: Path | None = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB default
    backup_count: int = 5,
) -> None:
    """Configure logging for the application.

    Args:
        verbose: Enable verbose (DEBUG level) logging
        json_output: Enable JSON structured logging
        sanitize_logs: Enable sanitization of sensitive data
        log_file: Optional path to log file (enables file logging)
        max_bytes: Maximum log file size before rotation (default: 10MB)
        backup_count: Number of backup files to keep (default: 5)
    """
    log_level = logging.DEBUG if verbose else logging.INFO

    # Remove existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers.copy():
        root_logger.removeHandler(handler)

    # Console handler (always present)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(log_level)

    # Add sensitive data filter if enabled
    if sanitize_logs:
        console_handler.addFilter(SensitiveDataFilter())

    # Determine formatter
    formatter: logging.Formatter
    if json_output:
        formatter = JSONFormatter()
    else:
        # Plain formatter (no colors for file output)
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)

        # Add sensitive data filter to file handler too
        if sanitize_logs:
            file_handler.addFilter(SensitiveDataFilter())

        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

        logger.info(f"File logging enabled: {log_file}")

    # Configure root logger
    root_logger.setLevel(log_level)

    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
```

### 2. Add Configuration Support

Update `src/nhl_scrabble/config.py` to include logging settings:

```python
@dataclass(frozen=True)
class Config:
    # Existing fields...

    # Logging configuration
    log_file: Path | None = None
    log_max_bytes: int = 10 * 1024 * 1024  # 10MB
    log_backup_count: int = 5

    @classmethod
    def from_env(cls) -> Config:
        """Create configuration from environment variables."""
        return cls(
            # Existing fields...

            # Logging
            log_file=Path(log_file) if (log_file := os.getenv("NHL_SCRABBLE_LOG_FILE")) else None,
            log_max_bytes=int(os.getenv("NHL_SCRABBLE_LOG_MAX_BYTES", "10485760")),
            log_backup_count=int(os.getenv("NHL_SCRABBLE_LOG_BACKUP_COUNT", "5")),
        )
```

### 3. Update CLI to Support File Logging

Add `--log-file` option to `serve` command:

```python
@click.option(
    "--log-file",
    type=click.Path(path_type=Path),
    help="Path to log file (enables file-based logging with rotation)",
)
def serve(host: str, port: int, reload: bool, log_file: Path | None) -> None:
    """Start web interface server."""
    try:
        import uvicorn
    except ImportError:
        click.echo(
            "Error: uvicorn not installed. Install with: pip install nhl-scrabble[web]",
            err=True,
        )
        raise click.Abort from None

    # Setup logging with optional file output
    setup_logging(
        verbose=False,  # Could add --verbose flag too
        log_file=log_file,
    )

    click.echo(f"Starting NHL Scrabble web server at http://{host}:{port}")
    if log_file:
        click.echo(f"Logging to: {log_file}")
    click.echo("Press CTRL+C to stop")

    # Import here to avoid loading FastAPI when not needed
    from nhl_scrabble.web.app import app

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )
```

### 4. Create Uvicorn Log Configuration (Optional Advanced Feature)

For more control over Uvicorn's own logging, create a custom log config:

```python
# src/nhl_scrabble/web/logging.py
"""Uvicorn logging configuration."""

import logging
from pathlib import Path

def get_uvicorn_log_config(
    access_log_file: Path | None = None,
    error_log_file: Path | None = None,
) -> dict:
    """Create Uvicorn log configuration with optional file output.

    Args:
        access_log_file: Path to access log file
        error_log_file: Path to error log file

    Returns:
        Uvicorn log configuration dictionary
    """
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(levelprefix)s %(message)s",
                "use_colors": None,
            },
            "access": {
                "()": "uvicorn.logging.AccessFormatter",
                "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["default"], "level": "INFO"},
            "uvicorn.error": {"level": "INFO"},
            "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
        },
    }

    # Add file handlers if paths provided
    if error_log_file:
        error_log_file.parent.mkdir(parents=True, exist_ok=True)
        config["handlers"]["error_file"] = {
            "formatter": "default",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(error_log_file),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        }
        config["loggers"]["uvicorn"]["handlers"].append("error_file")

    if access_log_file:
        access_log_file.parent.mkdir(parents=True, exist_ok=True)
        config["handlers"]["access_file"] = {
            "formatter": "access",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(access_log_file),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        }
        config["loggers"]["uvicorn.access"]["handlers"].append("access_file")

    return config
```

Then use it in CLI:

```python
from nhl_scrabble.web.logging import get_uvicorn_log_config

uvicorn.run(
    app,
    host=host,
    port=port,
    reload=reload,
    log_level="info",
    log_config=get_uvicorn_log_config(
        access_log_file=log_file.parent / f"{log_file.stem}_access.log" if log_file else None,
        error_log_file=log_file,
    ) if log_file else None,
)
```

## Implementation Steps

1. **Enhance `setup_logging()`**:
   - Add `log_file`, `max_bytes`, `backup_count` parameters
   - Add RotatingFileHandler when log_file provided
   - Ensure file logging gets same filters and formatters
   - Add parent directory creation

2. **Update Config**:
   - Add logging-related fields to Config dataclass
   - Add environment variable parsing in `from_env()`
   - Update `.env.example` with new variables

3. **Update CLI**:
   - Add `--log-file` option to `serve` command
   - Pass log_file to `setup_logging()`
   - Display log file path when enabled

4. **Add Documentation**:
   - Update README.md with logging examples
   - Add logging section to configuration documentation
   - Add environment variable documentation

5. **Create Tests**:
   - Test file handler creation
   - Test log rotation
   - Test directory creation
   - Test log file permissions
   - Test with/without file logging

6. **Optional: Uvicorn Log Config**:
   - Create `src/nhl_scrabble/web/logging.py`
   - Implement `get_uvicorn_log_config()`
   - Integrate with CLI
   - Add separate access/error logs

## Testing Strategy

### Unit Tests

Create `tests/unit/test_logging_config.py`:

```python
def test_setup_logging_with_file(tmp_path):
    """Test file-based logging."""
    log_file = tmp_path / "test.log"

    setup_logging(log_file=log_file)

    # Verify file created
    assert log_file.exists()

    # Verify logging works
    logger = logging.getLogger("test")
    logger.info("Test message")

    # Verify message in file
    assert "Test message" in log_file.read_text()

def test_setup_logging_rotation(tmp_path):
    """Test log rotation."""
    log_file = tmp_path / "test.log"

    setup_logging(log_file=log_file, max_bytes=100, backup_count=2)

    logger = logging.getLogger("test")
    for i in range(50):
        logger.info(f"Message {i} " * 10)  # Force rotation

    # Verify rotation occurred
    assert (tmp_path / "test.log.1").exists()

def test_setup_logging_creates_directory(tmp_path):
    """Test directory creation."""
    log_file = tmp_path / "logs" / "app" / "test.log"

    setup_logging(log_file=log_file)

    assert log_file.parent.exists()
    assert log_file.exists()
```

### Integration Tests

Create `tests/integration/test_web_logging.py`:

```python
def test_serve_with_log_file(tmp_path):
    """Test web server with file logging."""
    log_file = tmp_path / "server.log"

    # Start server in background with logging
    # Make requests
    # Verify logs written to file
    # Verify access logs present
```

### Manual Testing

```bash
# Test basic file logging
nhl-scrabble serve --log-file logs/server.log

# Test with environment variable
export NHL_SCRABBLE_LOG_FILE=logs/nhl-scrabble.log
nhl-scrabble serve

# Test rotation by generating many requests
ab -n 10000 -c 10 http://localhost:8000/

# Verify log files
ls -lh logs/
cat logs/server.log
cat logs/server.log.1
```

## Acceptance Criteria

- [ ] `setup_logging()` accepts optional `log_file` parameter
- [ ] File handler uses RotatingFileHandler with configurable size/count
- [ ] Log files are created in specified directory (creates parents if needed)
- [ ] Log rotation works correctly (creates .1, .2, etc. backup files)
- [ ] File logs receive same formatting and filtering as console logs
- [ ] CLI `serve` command has `--log-file` option
- [ ] Environment variable `NHL_SCRABBLE_LOG_FILE` is supported
- [ ] Documentation updated with logging examples
- [ ] Tests pass for file logging functionality
- [ ] Works on Linux, macOS, and Windows

## Related Files

- `src/nhl_scrabble/logging_config.py` - Main logging configuration
- `src/nhl_scrabble/cli.py` - CLI command that starts web server
- `src/nhl_scrabble/config.py` - Configuration dataclass
- `src/nhl_scrabble/web/app.py` - FastAPI application (logs messages)
- `docs/reference/configuration.md` - Configuration documentation
- `docs/reference/environment-variables.md` - Environment variable reference
- `.env.example` - Example environment file

## Dependencies

**Required Packages**: None (all in Python stdlib)
- `logging.handlers.RotatingFileHandler` - Built-in log rotation

**Optional Enhancements**:
- `python-json-logger` - Better structured JSON logging
- `loguru` - Alternative logging framework with auto-rotation

**Related Tasks**: None

## Additional Notes

### Design Considerations

**Log File Location**:
- Default: No file logging (backward compatible)
- User-specified: Via `--log-file` or environment variable
- Suggested: `logs/nhl-scrabble.log` or `/var/log/nhl-scrabble/app.log`

**Log Rotation Strategy**:
- Size-based: Rotate at 10MB (configurable)
- Keep 5 backups by default (configurable)
- Alternative: Time-based rotation (daily) using `TimedRotatingFileHandler`

**Separation of Concerns**:
- Application logs: Python logging (via setup_logging)
- Access logs: Uvicorn's access logger
- Can separate to different files or combine

**Production Deployment**:
- Consider using systemd journal instead: `journalctl -u nhl-scrabble -f`
- Or external log aggregation: Fluentd, Logstash, CloudWatch Logs
- File logging is good for simple deployments and debugging

### Security Considerations

**File Permissions**:
- Log files should be readable only by application user
- Use `os.chmod(log_file, 0o600)` after creation
- Parent directory should have appropriate permissions

**Sensitive Data**:
- SensitiveDataFilter already sanitizes logs
- Ensure file logs get same filtering as console
- Consider encryption for sensitive production logs

**Log Injection**:
- User input already sanitized by SensitiveDataFilter
- Newlines in log messages handled by logging framework
- No additional escaping needed

### Performance Implications

**Disk I/O**:
- File logging adds disk I/O overhead
- Use async file handlers for high-throughput scenarios
- Consider buffering for performance

**Log Rotation**:
- Rotation is fast (rename operation)
- Old logs compressed asynchronously would save space
- Monitor disk usage in production

### Migration Notes

**Backward Compatibility**:
- Default behavior unchanged (no file logging)
- Existing deployments continue to work
- Opt-in via CLI flag or environment variable

**Gradual Rollout**:
1. Deploy code with file logging support
2. Test in dev/staging with `--log-file`
3. Roll out to production via environment variable
4. Monitor disk usage and rotation

## Implementation Notes

**Implemented**: 2026-04-27
**Branch**: enhancement/036-file-based-logging-uvicorn
**PR**: #413 - https://github.com/bdperkin/nhl-scrabble/pull/413
**Commits**: 1 commit (f45693c)

### Actual Implementation

Followed the proposed solution closely with no major deviations:

1. **Enhanced `setup_logging()` in `src/nhl_scrabble/logging_config.py`**:
   - Added `log_file`, `max_bytes`, and `backup_count` parameters
   - Implemented RotatingFileHandler for automatic log rotation
   - File logs receive same security filters (SensitiveDataFilter) as console
   - UTF-8 encoding for international characters
   - Automatic parent directory creation

2. **Updated `Config` class in `src/nhl_scrabble/config.py`**:
   - Added `log_file`, `log_max_bytes`, `log_backup_count` fields
   - Environment variable validation (1MB-100MB for max_bytes, 1-50 for backup_count)
   - Updated docstring with logging configuration documentation

3. **Updated `serve` command in `src/nhl_scrabble/cli.py`**:
   - Added `--log-file` option
   - Added `--verbose` option
   - Integrated with Config logging settings

4. **Comprehensive testing**:
   - Created `tests/unit/test_logging_file_handler.py` with 12 tests
   - Updated `tests/unit/test_config.py` with 15 tests for logging config
   - All 27 tests passing

### Challenges Encountered

**Challenge 1**: Test compatibility with pytest's caplog fixture

- **Issue**: Initial tests using `caplog` failed because `setup_logging()` removes all handlers (including pytest's caplog handler)
- **Solution**: Rewrote tests to check handler existence and file content directly instead of relying on caplog

**Challenge 2**: Black formatting adjustments

- **Issue**: Pre-commit black hook reformatted test file after initial commit
- **Solution**: Re-added changes and committed again after black formatting

### Deviations from Plan

**Minor deviations**:

1. **Decided NOT to implement separate Uvicorn log config** (optional advanced feature from task):
   - **Reason**: The simple approach of adding file logging to `setup_logging()` is sufficient
   - **Benefit**: Simpler implementation, easier to maintain
   - **Trade-off**: No separate access/error log files, but single unified log is adequate for most use cases

2. **Added `--verbose` flag to serve command**:
   - **Reason**: Provides better debugging experience when file logging enabled
   - **Benefit**: Users can easily enable DEBUG level logging without environment variables
   - **Not in original plan**: But aligns well with existing CLI patterns

### Actual vs Estimated Effort

- **Estimated**: 3-5 hours
- **Actual**: ~3 hours
- **Breakdown**:
  - Code implementation: 1h
  - Test implementation: 1.5h
  - CI debugging and PR creation: 0.5h

**Reason for accuracy**: Task specification was very detailed with code examples, making implementation straightforward.

### Related PRs

- #413 - Main implementation (MERGED)

### Lessons Learned

1. **Pre-commit hooks can modify files**: Always run pre-commit before final commit to avoid extra commits for formatting
2. **Test isolation is important**: Tests that modify global state (like logging handlers) need careful cleanup
3. **Detailed task specifications accelerate implementation**: Having code examples in the task file reduced implementation time significantly
4. **pytest fixtures have limitations**: Not all pytest fixtures work well with code that modifies global state (e.g., caplog vs. logging.getLogger())
