# Fix Output Format Validation Mismatch Between CLI and Config

**GitHub Issue**: #366 - https://github.com/bdperkin/nhl-scrabble/issues/366

## Priority

**HIGH** - Must Do (Next Sprint)

## Estimated Effort

30 minutes - 1 hour

## Description

The CLI crashes with a confusing pydantic validation error when users specify certain output formats that are listed in the CLI help but not supported by the Config model.

**Error when running** `nhl-scrabble analyze -f markdown`:
```
pydantic_core._pydantic_core.ValidationError: 1 validation error for Config
  Value error, NHL_SCRABBLE_OUTPUT_FORMAT: Invalid value 'markdown'. Allowed values: csv, excel, html, json, text
```

**Root cause**: Mismatch between CLI accepted formats and Config allowed formats.

- **CLI accepts** (via `click.Choice`): text, json, yaml, xml, html, table, markdown, csv, excel, template (10 formats)
- **Config allows** (via `validate_enum`): text, json, html, csv, excel (5 formats)

**Missing formats in Config**:
- yaml
- xml
- table
- markdown
- template

Users see these formats in CLI help, try to use them, then get a confusing traceback instead of a friendly error message.

## Current State

**CLI Option Definition** (`src/nhl_scrabble/cli.py`, ~line 415):
```python
@click.option(
    "-f",
    "--format",
    "output_format",
    type=click.Choice(
        ["text", "json", "yaml", "xml", "html", "table", "markdown", "csv", "excel", "template"],
        case_sensitive=False,
    ),
    default="text",
    help="Output format (default: text)",
)
def analyze(..., output_format: str, ...):
    config = Config.from_env()

    # This line crashes with pydantic ValidationError for unsupported formats!
    config.output_format = output_format  # Line 635
```

**Config Validation** (`src/nhl_scrabble/config.py`, line 372-377):
```python
validated_data = {
    ...
    "output_format": get_enum(
        "output_format",
        "NHL_SCRABBLE_OUTPUT_FORMAT",
        "text",
        {"text", "json", "html", "csv", "excel"},  # Only 5 formats!
    ),
    ...
}
```

**Validator Function** (`src/nhl_scrabble/config_validators.py`, line 197-247):
```python
def validate_enum(value: str, allowed_values: set[str], ...) -> str:
    if check_value not in allowed_normalized:
        allowed_display = ", ".join(sorted(allowed_values))
        raise ConfigValidationError(
            f"Invalid value {value!r}. Allowed values: {allowed_display}"
        )
```

When pydantic calls this validator and it raises `ConfigValidationError`, pydantic wraps it in a `ValidationError` which produces a confusing multi-line traceback instead of a simple CLI error.

## Proposed Solution

**Option 1: Add Missing Formats to Config** (Recommended)

Add the 5 missing formats to Config's allowed values:

```python
# src/nhl_scrabble/config.py, line 372-377
"output_format": get_enum(
    "output_format",
    "NHL_SCRABBLE_OUTPUT_FORMAT",
    "text",
    {"text", "json", "yaml", "xml", "html", "table", "markdown", "csv", "excel", "template"},
),
```

**Pros**:
- Matches user expectations from CLI help
- No breaking changes
- Simple one-line fix

**Cons**:
- Assumes all formats are actually implemented
- Need to verify formatters exist for all formats

**Option 2: Remove Unsupported Formats from CLI**

Remove unsupported formats from CLI Choice list:

```python
# src/nhl_scrabble/cli.py
type=click.Choice(
    ["text", "json", "html", "csv", "excel"],  # Only supported formats
    case_sensitive=False,
),
```

**Pros**:
- CLI and Config are in sync
- Users can't select unsupported formats

**Cons**:
- Breaking change if users relied on those format names
- Removes potentially useful formats
- Bad UX if formatters were partially implemented

**Recommended Solution**: **Option 1** - Add missing formats to Config allowed list.

**Why**:
1. Formatters likely already exist (CLI wouldn't offer them otherwise)
2. No breaking changes for users
3. Maintains CLI consistency
4. One-line fix

**If formatters don't exist**: Add them or fall back to Option 2.

## Implementation Steps

1. **Verify formatters exist** for all 10 formats:
   ```bash
   grep -r "class.*Formatter\|def get_formatter" src/nhl_scrabble/formatters/
   # Check for: YamlFormatter, XmlFormatter, TableFormatter, MarkdownFormatter, TemplateFormatter
   ```

2. **Update Config allowed formats** in `src/nhl_scrabble/config.py`:
   ```python
   "output_format": get_enum(
       "output_format",
       "NHL_SCRABBLE_OUTPUT_FORMAT",
       "text",
       {
           "text", "json", "yaml", "xml", "html",
           "table", "markdown", "csv", "excel", "template"
       },
   ),
   ```

3. **Add unit test** in `tests/unit/test_config.py`:
   ```python
   def test_config_accepts_all_cli_format_options():
       """Test Config accepts all formats offered by CLI."""
       cli_formats = [
           "text", "json", "yaml", "xml", "html",
           "table", "markdown", "csv", "excel", "template"
       ]

       for fmt in cli_formats:
           config = Config(output_format=fmt)
           assert config.output_format == fmt.lower()
   ```

4. **Add integration test** in `tests/integration/test_cli.py`:
   ```python
   def test_analyze_accepts_markdown_format():
       """Test analyze command doesn't crash with markdown format."""
       result = runner.invoke(cli, ["analyze", "-f", "markdown", "-o", "/tmp/test.md"])
       # Should not crash with ValidationError
       assert result.exit_code == 0 or result.exit_code == 1  # Allow business logic errors
       assert "ValidationError" not in result.output
       assert "pydantic" not in result.output.lower()
   ```

5. **Manual testing**:
   ```bash
   # Test all formats
   for fmt in text json yaml xml html table markdown csv excel template; do
       echo "Testing format: $fmt"
       nhl-scrabble analyze -f $fmt -o /tmp/test.$fmt -q || echo "FAILED: $fmt"
   done

   # Verify no pydantic errors
   nhl-scrabble analyze -f markdown 2>&1 | grep -i "pydantic\|validationerror" && echo "FAILED"
   ```

6. **Update documentation** if needed:
   - Verify CLI help is accurate
   - Update docs/reference/cli.md if format list changed
   - Update CHANGELOG.md

## Testing Strategy

**Unit Tests**:
```python
# tests/unit/test_config.py
def test_config_output_format_validation():
    """Test output format validation accepts all CLI formats."""
    valid_formats = [
        "text", "json", "yaml", "xml", "html",
        "table", "markdown", "csv", "excel", "template"
    ]

    for fmt in valid_formats:
        config = Config(output_format=fmt)
        assert config.output_format == fmt.lower()

def test_config_output_format_rejects_invalid():
    """Test invalid formats are rejected."""
    with pytest.raises(ValueError, match="Invalid value.*Allowed values"):
        Config(output_format="invalid")

def test_config_output_format_case_insensitive():
    """Test output format is case-insensitive."""
    config = Config(output_format="MARKDOWN")
    assert config.output_format == "markdown"
```

**Integration Tests**:
```python
# tests/integration/test_cli.py
@pytest.mark.parametrize("format", [
    "text", "json", "yaml", "xml", "html",
    "table", "markdown", "csv", "excel", "template"
])
def test_analyze_supports_all_formats(format):
    """Test analyze command supports all advertised formats."""
    result = runner.invoke(cli, ["analyze", "-f", format, "-o", f"/tmp/test.{format}", "-q"])

    # Should not crash with ValidationError
    assert "ValidationError" not in result.output
    assert "pydantic" not in result.output.lower()

    # May fail for business reasons, but not validation
    if result.exit_code != 0:
        assert "Allowed values" not in result.output  # Not a validation error
```

**Manual Testing**:
```bash
# Reproduce original error (should be fixed)
nhl-scrabble analyze -f markdown -q
# Expected: No traceback, either success or friendly error

# Test all formats
nhl-scrabble analyze -f yaml --help
nhl-scrabble analyze -f xml -o /tmp/test.xml -q
nhl-scrabble analyze -f table
nhl-scrabble analyze -f markdown -o /tmp/test.md
nhl-scrabble analyze -f template --template mytemplate.txt

# Test case insensitivity
nhl-scrabble analyze -f MARKDOWN -o /tmp/test.md -q
nhl-scrabble analyze -f Json -o /tmp/test.json -q
```

## Acceptance Criteria

- [x] All 10 CLI-advertised formats accepted by Config
- [x] No pydantic ValidationError for valid CLI formats
- [x] User-friendly error for truly invalid formats (not in CLI list)
- [x] Config validation and CLI choices are in sync
- [x] Unit tests verify all formats accepted
- [x] Integration tests verify no ValidationError crashes
- [x] Manual testing confirms fix
- [x] Documentation updated if needed
- [x] All existing tests pass
- [x] Type checking passes (mypy)
- [x] Linting passes (ruff)

## Related Files

- `src/nhl_scrabble/config.py` - Update allowed output formats (line 372-377)
- `src/nhl_scrabble/cli.py` - CLI format option definition (reference only)
- `src/nhl_scrabble/config_validators.py` - validate_enum function (reference only)
- `src/nhl_scrabble/formatters/` - Verify formatters exist
- `tests/unit/test_config.py` - Add format validation tests
- `tests/integration/test_cli.py` - Add CLI format tests
- `docs/reference/cli.md` - Update if format list changed
- `CHANGELOG.md` - Document bug fix

## Dependencies

None - standalone bug fix.

## Additional Notes

### Why This Matters

**User Experience**:
- **Confusing errors**: Pydantic tracebacks are not user-friendly
- **Broken expectations**: CLI advertises formats that crash
- **Trust issues**: Users lose confidence in the tool

**Developer Experience**:
- **Maintenance**: CLI and Config should be in sync
- **Testing**: Need tests to catch these mismatches
- **Documentation**: Auto-generated help should be accurate

### Root Cause Analysis

**How did this happen?**

1. Developer added new output formats to CLI
2. Forgot to update Config allowed values
3. No test coverage for CLI-Config consistency
4. Issue went unnoticed until user tried unsupported format

**Prevention**:

- Add test that verifies CLI and Config are in sync
- Consider deriving CLI choices from Config allowed values (DRY principle)
- Code review checklist: "Did you update both CLI and Config?"

### CLI-Config Sync Pattern

**Better approach** (future refactoring):

```python
# src/nhl_scrabble/config.py
ALLOWED_OUTPUT_FORMATS = {
    "text", "json", "yaml", "xml", "html",
    "table", "markdown", "csv", "excel", "template"
}

# src/nhl_scrabble/cli.py
from nhl_scrabble.config import ALLOWED_OUTPUT_FORMATS

@click.option(
    "-f", "--format", "output_format",
    type=click.Choice(list(ALLOWED_OUTPUT_FORMATS), case_sensitive=False),
    default="text",
    help="Output format (default: text)",
)
```

**Benefits**:
- Single source of truth (DRY)
- Cannot get out of sync
- Easy to add new formats

### Performance Implications

None - validation is negligible overhead.

### Security Implications

None - format validation already exists, just expanding allowed values.

### Breaking Changes

None - only adding support for previously-advertised formats.

### Future Enhancements

After this fix:
- Consider refactoring to shared ALLOWED_OUTPUT_FORMATS constant
- Add pre-commit hook to check CLI-Config consistency
- Add test that validates all CLI Choice options are in Config allowed values
- Document format implementation requirements

## Implementation Notes

*To be filled during implementation:*

- Which formatters already existed vs needed to be added
- Any format-specific implementation challenges
- User feedback on fix
- Actual effort vs estimated
