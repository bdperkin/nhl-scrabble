# Add Automated Code Example Testing to CI

**GitHub Issue**: #352 - https://github.com/bdperkin/nhl-scrabble/issues/352

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

2 hours

## Description

Add automated testing for code examples in docstrings and documentation to ensure they stay current as the codebase evolves. This prevents documentation drift where examples become outdated or broken.

## Current State

**Documentation Examples**:

- Python docstrings contain ~150+ code examples (estimated)
- Markdown docs contain ~50+ code examples (estimated)
- No automated testing of examples exists
- Examples could become outdated without detection

**Current Risk**:

- Code examples in docstrings may not execute correctly
- Markdown documentation examples may reference old APIs
- Breaking changes can invalidate examples silently
- Users may copy broken example code

**Example Documentation** (from `ScrabbleScorer`):

```python
def calculate_score(name: str) -> int:
    """Calculate the Scrabble score for a given name.

    Examples:
        >>> ScrabbleScorer.calculate_score("ALEX")
        11
        >>> ScrabbleScorer.calculate_score("Ovechkin")
        20
    """
```

**Issue**: No automated verification that these examples actually work!

## Proposed Solution

Add automated testing for code examples using pytest's doctest module and custom tooling for Markdown examples.

### Architecture Changes

**Add Doctest to CI**:

```yaml
# .github/workflows/ci.yml (update existing)
jobs:
  test:
    # ... existing test job

  doctest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install package with dependencies
        run: |
          pip install -e ".[dev]"

      - name: Run doctest on Python modules
        run: |
          pytest --doctest-modules src/nhl_scrabble/

      - name: Extract and test Markdown examples
        run: |
          python scripts/test_markdown_examples.py
```

**Add tox Environment**:

```ini
# tox.ini (add new environment)
[testenv:doctest]
description = Test code examples in docstrings and documentation
deps =
    pytest
    pytest-doctestplus
commands =
    pytest --doctest-modules src/nhl_scrabble/
    python scripts/test_markdown_examples.py
```

### New Testing Infrastructure

**Script to Extract Markdown Examples**:

````python
# scripts/test_markdown_examples.py
"""Extract and test code examples from Markdown documentation."""

import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple


class CodeBlock(NamedTuple):
    """Represents a code block in Markdown."""

    file: Path
    line: int
    language: str
    code: str


def extract_code_blocks(md_file: Path) -> list[CodeBlock]:
    """Extract all Python code blocks from a Markdown file.

    Args:
        md_file: Path to Markdown file

    Returns:
        List of CodeBlock objects
    """
    content = md_file.read_text()
    blocks = []

    # Pattern: ```python ... ```
    pattern = r"```python\n(.*?)```"

    for match in re.finditer(pattern, content, re.DOTALL):
        code = match.group(1)
        # Calculate line number
        line = content[: match.start()].count("\n") + 1

        blocks.append(CodeBlock(file=md_file, line=line, language="python", code=code))

    return blocks


def test_code_block(block: CodeBlock) -> tuple[bool, str]:
    """Test a code block by executing it.

    Args:
        block: CodeBlock to test

    Returns:
        Tuple of (success, error_message)
    """
    try:
        # Create test script
        test_script = f"""
import sys
sys.path.insert(0, 'src')

{block.code}
"""

        result = subprocess.run(
            ["python", "-c", test_script], capture_output=True, text=True, timeout=10
        )

        if result.returncode == 0:
            return True, ""
        else:
            return False, result.stderr

    except subprocess.TimeoutExpired:
        return False, "Timeout (10s exceeded)"
    except Exception as e:
        return False, str(e)


def main() -> int:
    """Extract and test all Markdown examples."""
    docs_dir = Path("docs")
    root_dir = Path(".")

    # Find all Markdown files
    md_files = list(docs_dir.rglob("*.md"))
    md_files += [f for f in root_dir.glob("*.md") if f.name != "sync-report.md"]

    total_blocks = 0
    failed_blocks = 0

    for md_file in md_files:
        blocks = extract_code_blocks(md_file)

        for block in blocks:
            total_blocks += 1
            success, error = test_code_block(block)

            if not success:
                failed_blocks += 1
                print(f"❌ FAILED: {block.file}:{block.line}")
                print(f"   Error: {error}")
                print()

    # Summary
    print(f"\n{'='*60}")
    print(f"Markdown Example Test Summary")
    print(f"{'='*60}")
    print(f"Total examples: {total_blocks}")
    print(f"Passed: {total_blocks - failed_blocks}")
    print(f"Failed: {failed_blocks}")

    return 1 if failed_blocks > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
````

### Pytest Configuration

**Update pytest configuration**:

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "-ra",
]

# Doctest configuration
doctest_optionflags = [
    "NORMALIZE_WHITESPACE",
    "ELLIPSIS",
    "IGNORE_EXCEPTION_DETAIL",
]
```

### Makefile Integration

**Add doctest target**:

```makefile
# Makefile
.PHONY: doctest
doctest: ## Run doctest on all docstrings and markdown examples
	@echo "Running doctest on Python modules..."
	pytest --doctest-modules src/nhl_scrabble/
	@echo "Testing Markdown code examples..."
	python scripts/test_markdown_examples.py
```

## Implementation Steps

1. **Add pytest-doctestplus dependency** (5 min)

   ```bash
   # Add to pyproject.toml [project.optional-dependencies.dev]
   uv add --dev pytest-doctestplus
   ```

1. **Create Markdown example test script** (45 min)

   - Create `scripts/test_markdown_examples.py`
   - Implement code block extraction
   - Implement example execution
   - Add error reporting
   - Test on sample Markdown files

1. **Configure pytest for doctest** (10 min)

   - Update `pyproject.toml` with doctest options
   - Configure whitespace normalization
   - Configure ellipsis handling
   - Test locally

1. **Add tox environment** (10 min)

   - Create `[testenv:doctest]` in tox.ini
   - Configure to run pytest --doctest-modules
   - Configure to run Markdown example tests
   - Test locally: `tox -e doctest`

1. **Update CI workflow** (15 min)

   - Add doctest job to `.github/workflows/ci.yml`
   - Configure to run on all commits
   - Set up proper dependencies
   - Test workflow

1. **Add Makefile target** (5 min)

   - Create `doctest` target
   - Add to help text
   - Test: `make doctest`

1. **Fix failing examples** (30 min)

   - Run doctest on all modules
   - Identify failing examples
   - Fix outdated examples
   - Update examples to current API
   - Verify all pass

1. **Update documentation** (10 min)

   - Update `docs/audit/README.md`
   - Add doctest to testing section
   - Document usage
   - Add to quality checklist

1. **Commit changes** (5 min)

   ```bash
   git add scripts/test_markdown_examples.py
   git add pyproject.toml uv.lock
   git add tox.ini
   git add .github/workflows/ci.yml
   git add Makefile
   git add docs/audit/README.md
   git commit -m "feat(ci): Add automated code example testing"
   ```

## Testing Strategy

### Manual Testing

**Test Doctest Locally**:

```bash
# Test single module
pytest --doctest-modules src/nhl_scrabble/scoring/scrabble.py -v

# Test all modules
pytest --doctest-modules src/nhl_scrabble/ -v

# Expected output:
# src/nhl_scrabble/scoring/scrabble.py::scrabble.ScrabbleScorer.calculate_score PASSED
```

**Test Markdown Examples**:

```bash
# Run the extraction script
python scripts/test_markdown_examples.py

# Expected output:
# Testing docs/how-to/installation.md
# ✅ PASSED: example at line 42
# ✅ PASSED: example at line 67
#
# Summary: 15 examples, 15 passed, 0 failed
```

**Test via Tox**:

```bash
tox -e doctest

# Should test both docstrings and markdown
```

**Test via Makefile**:

```bash
make doctest
```

### CI Testing

**Workflow Validation**:

1. Create test PR with known failing example
1. Verify doctest job runs
1. Verify job fails with clear error
1. Fix example and verify job passes

### Example Types to Test

- ✅ Simple function calls with expected output
- ✅ Class instantiation examples
- ✅ Error/exception examples
- ✅ Multi-line examples
- ✅ Import statements
- ⚠️ Examples requiring external API (should be mocked or skipped)

## Acceptance Criteria

- [x] pytest-doctestplus added to dev dependencies
- [x] Markdown example extraction script created
- [x] Pytest configured for doctest
- [x] Tox environment created for doctest
- [x] CI workflow updated with doctest job
- [x] Makefile target created
- [x] All existing docstring examples pass
- [x] All existing Markdown examples pass (or skipped with reason)
- [x] Documentation updated
- [x] CI tests passing

## Related Files

**New Files**:

- `scripts/test_markdown_examples.py` - Markdown example tester

**Modified Files**:

- `pyproject.toml` - Add pytest-doctestplus dependency
- `uv.lock` - Updated dependencies
- `tox.ini` - Add doctest environment
- `.github/workflows/ci.yml` - Add doctest job
- `Makefile` - Add doctest target
- `docs/audit/README.md` - Document example testing

**Files with Examples to Test**:

- `src/nhl_scrabble/**/*.py` - All Python modules (~150 examples)
- `docs/**/*.md` - All documentation (~50 examples)
- `README.md` - Project README examples

## Dependencies

**Required Tools**:

- pytest >= 8.0.0 (already available)
- pytest-doctestplus >= 1.0.0 (new dependency)

**Task Dependencies**:

- Documentation audit completed (task 013) ✅

**Related Tasks**:

- Task 025: Add link validation
- Task 027: Improve function example coverage

## Additional Notes

### Benefits

**Quality Assurance**:

- Examples always work (tested on every commit)
- Breaking changes caught immediately
- Refactoring safe (examples updated automatically)
- Better user experience

**Development Workflow**:

- Examples serve as integration tests
- Documentation stays current with code
- Catch API changes early

**Best Practices**:

- Industry standard (pytest doctest)
- Aligns with documentation audit recommendations
- Automated, repeatable process

### Doctest Best Practices

**Good Docstring Examples**:

```python
def calculate_score(name: str) -> int:
    """Calculate Scrabble score.

    Examples:
        >>> calculate_score("ALEX")
        11
        >>> calculate_score("TEST")
        4
    """
```

**Examples with Ellipsis** (for variable output):

```python
def get_stats() -> dict:
    """Get statistics.

    Examples:
        >>> stats = get_stats()
        >>> stats['total']  # doctest: +ELLIPSIS
        <number>
    """
```

**Skipping Examples**:

```python
def fetch_api() -> dict:
    """Fetch from API.

    Examples:
        >>> # doctest: +SKIP
        >>> data = fetch_api()  # Requires network
    """
```

### Markdown Example Guidelines

**Testable Examples** (should work):

```python
from nhl_scrabble import ScrabbleScorer

scorer = ScrabbleScorer()
score = scorer.calculate_score("Test")
assert score == 4
```

**Non-testable Examples** (skip):

- Examples requiring user input
- Examples requiring network access
- Examples showing error output
- Pseudo-code or illustrative examples

### Performance Considerations

**Doctest Performance**:

- Fast: ~100 examples in ~5 seconds
- Runs on every commit
- Minimal CI time impact

**Markdown Example Performance**:

- Slower: ~50 examples in ~30 seconds
- Each example is subprocess
- Still acceptable for CI

**Total CI Impact**: ~35-40 seconds per run

### Known Limitations

**Doctest Limitations**:

- Output must match exactly (use ELLIPSIS for variable parts)
- Floating point comparisons need care
- Cannot test interactive code
- Cannot test code requiring external services

**Workarounds**:

- Use `# doctest: +SKIP` for untestable examples
- Use `# doctest: +ELLIPSIS` for variable output
- Mock external services in examples

### Documentation Audit Context

This task addresses **Gap #3** from the documentation audit:

> **Gap 3: No Automated Code Example Testing**
>
> **Impact**: MEDIUM
> **Affected**: Documentation with code examples
>
> **Recommendation**: Add doctest or example extraction to CI

**Audit Finding**:

- "Documentation contains code examples that could become outdated as the codebase evolves"
- "No automated testing ensures examples stay current"
- Priority: MEDIUM
- Effort: 2 hours ✅

### Future Enhancements

**Potential Improvements**:

1. Add example coverage metrics (% of functions with examples)
1. Generate example report (working vs broken)
1. Add example freshness tracking (last verified)
1. Create example gallery in documentation

**Not Included** (out of scope):

- Interactive example playground
- Example auto-generation
- Example performance benchmarking

## Implementation Notes

*To be filled during implementation:*

- Number of docstring examples found
- Number of Markdown examples found
- Examples that failed initially
- Examples that needed fixing
- Examples that needed skip markers
- Workflow run time
- Any challenges encountered
- Deviations from plan
