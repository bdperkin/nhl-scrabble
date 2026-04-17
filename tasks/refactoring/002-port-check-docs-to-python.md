# Port check_docs.sh Shell Script to Python

**GitHub Issue**: #100 - https://github.com/bdperkin/nhl-scrabble/issues/100

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

2-3 hours

## Description

Port the `tools/check_docs.sh` shell script to an equivalent Python script (`tools/check_docs.py`). The shell script currently checks if generated documentation is up-to-date by regenerating docs and comparing with git. Converting to Python improves cross-platform compatibility, maintainability, and consistency with other project tooling.

## Current State

The project has a bash script for checking generated documentation:

**tools/check_docs.sh** (45 lines):

```bash
#!/usr/bin/env bash
# Check if generated documentation is up-to-date

set -e  # Exit on error

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Checking generated documentation...${NC}"

# Check if nhl_scrabble package is importable
if ! python -c "import nhl_scrabble" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Skipping documentation check...${NC}"
    exit 0
fi

# Generate API docs
echo -e "${BLUE}Generating API reference documentation...${NC}"
mkdir -p docs/reference/api
pdoc nhl_scrabble -o docs/reference/api -d markdown

# Generate CLI docs
echo -e "${BLUE}Generating CLI reference documentation...${NC}"
python tools/generate_cli_docs.py

# Check if any files were modified
if ! git diff --exit-code docs/reference/api/ docs/reference/cli-generated.md > /dev/null 2>&1; then
    echo -e "${RED}✗ Generated docs are out of date!${NC}"
    echo -e "${RED}Run 'make docs-gen' to regenerate documentation${NC}"
    echo ""
    echo "Modified files:"
    git diff --name-only docs/reference/api/ docs/reference/cli-generated.md
    exit 1
fi

echo -e "${GREEN}✓ Generated docs are up-to-date${NC}"
exit 0
```

**Pre-commit hook** (.pre-commit-config.yaml):

```yaml
- repo: local
  hooks:
    - id: check-generated-docs
      name: Check generated documentation is up-to-date
      entry: bash tools/check_docs.sh
      language: system
      pass_filenames: false
      files: ^(src/nhl_scrabble/.*\.py|tools/generate_cli_docs\.py)$
```

**Issues**:

1. **Platform Dependency**: Requires bash (not native on Windows)
1. **Color Code Duplication**: Terminal colors hard-coded
1. **Inconsistency**: Other tools use Python (generate_cli_docs.py)
1. **Limited Error Handling**: No structured error messages
1. **Testing Difficulty**: Bash scripts are harder to unit test
1. **Maintenance**: Shell syntax less familiar to Python developers

## Proposed Solution

Create `tools/check_docs.py` following the same patterns as `tools/generate_cli_docs.py`:

**tools/check_docs.py** (Python equivalent):

```python
"""Check if generated documentation is up-to-date.

This script regenerates API and CLI documentation and verifies that it matches
the committed versions. Used in pre-commit hooks to ensure documentation stays
in sync with code changes.

Usage:
    python tools/check_docs.py

Exit Codes:
    0: Documentation is up-to-date
    1: Documentation is out-of-date (needs regeneration)
    0: Package not installed (skip check in isolated environments)

Environment:
    Works in both local development and CI environments.
    Gracefully skips check if nhl_scrabble package is not importable
    (expected in pre-commit isolated environments).
"""

# ruff: noqa: INP001, S603, S607, T201
# INP001: tools directory is not a package
# S603/S607: subprocess calls are to trusted tools (pdoc, python, git)
# T201: print statements are appropriate for utility script

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""

    BLUE = "\033[0;34m"
    GREEN = "\033[0;32m"
    RED = "\033[0;31m"
    YELLOW = "\033[0;33m"
    NC = "\033[0m"  # No Color


def print_colored(message: str, color: str) -> None:
    """Print colored message to stdout.

    Args:
        message: Message to print
        color: ANSI color code
    """
    print(f"{color}{message}{Colors.NC}")


def check_package_importable() -> bool:
    """Check if nhl_scrabble package is importable.

    Returns:
        True if package can be imported, False otherwise
    """
    try:
        result = subprocess.run(
            [sys.executable, "-c", "import nhl_scrabble"],
            capture_output=True,
            check=False,
        )
        return result.returncode == 0
    except subprocess.CalledProcessError:
        return False


def generate_api_docs() -> None:
    """Generate API reference documentation using pdoc.

    Raises:
        subprocess.CalledProcessError: If pdoc fails
    """
    print_colored("Generating API reference documentation...", Colors.BLUE)

    # Create output directory
    api_dir = Path("docs/reference/api")
    api_dir.mkdir(parents=True, exist_ok=True)

    # Run pdoc
    subprocess.run(
        ["pdoc", "nhl_scrabble", "-o", str(api_dir), "-d", "markdown"],
        check=True,
        capture_output=True,
    )


def generate_cli_docs() -> None:
    """Generate CLI reference documentation.

    Raises:
        subprocess.CalledProcessError: If generation fails
    """
    print_colored("Generating CLI reference documentation...", Colors.BLUE)

    subprocess.run(
        [sys.executable, "tools/generate_cli_docs.py"],
        check=True,
        capture_output=True,
    )


def check_docs_modified() -> bool:
    """Check if generated documentation differs from committed version.

    Returns:
        True if docs are modified (out of date), False if up-to-date

    Raises:
        subprocess.CalledProcessError: If git command fails
    """
    result = subprocess.run(
        [
            "git",
            "diff",
            "--exit-code",
            "docs/reference/api/",
            "docs/reference/cli-generated.md",
        ],
        capture_output=True,
        check=False,
    )
    return result.returncode != 0


def get_modified_files() -> list[str]:
    """Get list of modified documentation files.

    Returns:
        List of modified file paths
    """
    result = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            "docs/reference/api/",
            "docs/reference/cli-generated.md",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return [f for f in result.stdout.strip().split("\n") if f]


def main() -> int:
    """Main entry point for documentation check.

    Returns:
        0 if docs are up-to-date or package not installed, 1 if out-of-date
    """
    print_colored("Checking generated documentation...", Colors.BLUE)

    # Check if package is importable
    if not check_package_importable():
        print_colored(
            "⚠️  Skipping documentation check: nhl_scrabble package not installed",
            Colors.YELLOW,
        )
        print_colored(
            "This is expected in pre-commit isolated environments.",
            Colors.YELLOW,
        )
        print_colored(
            "Documentation checks will run in CI via tox.",
            Colors.YELLOW,
        )
        return 0

    try:
        # Generate documentation
        generate_api_docs()
        generate_cli_docs()

        # Check if docs were modified
        if check_docs_modified():
            print_colored("✗ Generated docs are out of date!", Colors.RED)
            print_colored(
                "Run 'make docs-gen' to regenerate documentation",
                Colors.RED,
            )
            print()
            print("Modified files:")
            for file in get_modified_files():
                print(f"  {file}")
            return 1

        print_colored("✓ Generated docs are up-to-date", Colors.GREEN)
        return 0

    except subprocess.CalledProcessError as e:
        print_colored(f"✗ Error generating documentation: {e}", Colors.RED)
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

**Update .pre-commit-config.yaml**:

```yaml
- repo: local
  hooks:
    - id: check-generated-docs
      name: Check generated documentation is up-to-date
      entry: python tools/check_docs.py  # Changed from bash to python
      language: system
      pass_filenames: false
      files: ^(src/nhl_scrabble/.*\.py|tools/generate_cli_docs\.py)$
```

## Implementation Steps

1. **Create Python script**

   - Create `tools/check_docs.py`
   - Implement all functions from shell script
   - Add proper docstrings and type hints
   - Follow project's ruff rules and style

1. **Update pre-commit hook**

   - Change entry from `bash tools/check_docs.sh` to `python tools/check_docs.py`
   - Verify hook still triggers on correct files

1. **Test functionality**

   - Test when package is importable
   - Test when package is not importable (skip scenario)
   - Test when docs are up-to-date
   - Test when docs are out-of-date
   - Verify error messages and colors display correctly

1. **Update documentation**

   - Update any references to check_docs.sh
   - Document the new Python script
   - Update CONTRIBUTING.md if it mentions the script

1. **Remove old script**

   - Delete `tools/check_docs.sh`
   - Ensure no other files reference it

1. **Verify pre-commit**

   - Run pre-commit manually: `pre-commit run check-generated-docs --all-files`
   - Verify it works in isolated environment
   - Verify it works when docs are out of date

## Testing Strategy

### Manual Testing

```bash
# 1. Test with package installed and docs up-to-date
python tools/check_docs.py
# Expected: "✓ Generated docs are up-to-date" (exit 0)

# 2. Test with docs out of date
# Modify a docstring in src/nhl_scrabble/cli.py
python tools/check_docs.py
# Expected: "✗ Generated docs are out of date!" (exit 1)

# 3. Test package not importable
# Create isolated environment without package
python -m venv test-env
source test-env/bin/activate
python tools/check_docs.py
# Expected: "⚠️  Skipping documentation check..." (exit 0)
deactivate && rm -rf test-env

# 4. Test pre-commit integration
pre-commit run check-generated-docs --all-files
# Expected: Same behavior as direct script execution

# 5. Test on Windows (if available)
# Verify script works without bash dependency
```

### Pre-commit Testing

```bash
# Install pre-commit hooks
pre-commit install

# Test hook triggers
touch src/nhl_scrabble/cli.py
git add src/nhl_scrabble/cli.py
git commit -m "test"
# Should run check-generated-docs hook

# Test hook with out-of-date docs
# Modify docstring
python -c "
with open('src/nhl_scrabble/cli.py', 'a') as f:
    f.write('\n# Test comment\n')
"
git add src/nhl_scrabble/cli.py
git commit -m "test"
# Should fail if docs become out of date
```

## Acceptance Criteria

- [x] `tools/check_docs.py` created with equivalent functionality
- [x] Script follows project style (ruff, mypy, docstrings)
- [x] Type hints added throughout
- [x] Color output works correctly
- [x] Package importability check works
- [x] API docs generation works (pdoc)
- [x] CLI docs generation works
- [x] Git diff check works correctly
- [x] Modified files listed correctly
- [x] Exit codes match original (0 = success/skip, 1 = out-of-date)
- [x] Pre-commit hook updated to use Python script
- [x] Pre-commit hook works in isolated environment
- [x] Pre-commit hook works when docs out of date
- [x] `tools/check_docs.sh` deleted
- [x] No references to old shell script remain
- [x] Documentation updated
- [x] Works on Windows (no bash dependency)
- [x] All ruff/mypy checks pass

## Related Files

- `tools/check_docs.sh` - Original shell script (to be deleted)
- `tools/check_docs.py` - New Python script (to be created)
- `tools/generate_cli_docs.py` - Similar Python tool (reference for style)
- `.pre-commit-config.yaml` - Pre-commit hook configuration
- `docs/reference/api/` - Generated API documentation directory
- `docs/reference/cli-generated.md` - Generated CLI documentation
- `CONTRIBUTING.md` - May reference the script
- `CLAUDE.md` - Developer documentation

## Dependencies

None - This is a standalone refactoring task.

## Additional Notes

### Benefits

**Cross-Platform Compatibility**:

- Works on Windows without bash/WSL
- No shell-specific syntax
- Consistent behavior across platforms

**Maintainability**:

- Python developers more familiar with Python than bash
- Easier to add features and error handling
- Can be unit tested (unlike shell scripts)
- Type checking with mypy
- Linting with ruff

**Consistency**:

- Matches `tools/generate_cli_docs.py` patterns
- Uses pathlib, subprocess module
- Proper docstrings and type hints
- Follows project style guide

**Better Error Handling**:

- Structured exception handling
- Clear error messages
- Exit codes well-defined

### Breaking Changes

None - This is a drop-in replacement:

- Same command-line interface (no arguments)
- Same exit codes
- Same output format
- Same behavior in all scenarios

### Performance Impact

Negligible - Python interpreter overhead is minimal compared to:

- Running pdoc (major time consumer)
- Git operations
- File I/O

Expected performance difference: \<100ms overhead, which is insignificant for a pre-commit hook that already runs pdoc.

### Security Considerations

**Subprocess Calls**:

- All subprocess calls are to trusted tools (pdoc, python, git)
- No user input in commands
- Proper noqa comments document security exceptions (S603, S607)

**Same Security Profile as Shell Script**:

- Python version has same security characteristics
- Uses same external tools
- No new security concerns introduced

### Migration Notes

**For Developers**:

- Pre-commit hook updates automatically (just pull latest)
- No action needed - script called by pre-commit infrastructure

**For CI/CD**:

- No changes needed - pre-commit calls the script
- Same behavior in CI environments

**Testing the Migration**:

1. Before merging: Test pre-commit hook manually
1. After merging: Verify hook works in CI
1. Monitor first few commits for any issues

### Future Enhancements

After this refactoring, the Python script could be enhanced with:

- **Parallel generation**: Run pdoc and CLI docs concurrently
- **Progress indicators**: Show progress during generation
- **Caching**: Skip regeneration if source files unchanged
- **Verbose mode**: Add `--verbose` flag for debugging
- **Dry run mode**: `--dry-run` to check without generating

These are outside the scope of this task but are easier to implement in Python.

## Implementation Notes

*To be filled during implementation:*

- Actual approach taken
- Challenges encountered
- Deviations from plan
- Actual effort vs estimated
- Testing results
- Any issues discovered with the original shell script
