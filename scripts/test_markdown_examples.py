#!/usr/bin/env python3
"""Extract and test code examples from Markdown documentation.

This script validates that Python code examples in Markdown documentation are executable and
correct. It helps prevent documentation drift by catching broken examples during CI.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple


class CodeBlock(NamedTuple):
    """Represents a code block in Markdown.

    Attributes:
        file: Path to the Markdown file
        line: Line number where the code block starts
        language: Language identifier (e.g., 'python')
        code: The actual code content
    """

    file: Path
    line: int
    language: str
    code: str


def extract_code_blocks(md_file: Path) -> list[CodeBlock]:
    """Extract all Python code blocks from a Markdown file.

    Args:
        md_file: Path to Markdown file

    Returns:
        List of CodeBlock objects containing Python code
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


def should_skip_code_block(block: CodeBlock) -> tuple[bool, str]:
    """Check if a code block should be skipped.

    Args:
        block: CodeBlock to check

    Returns:
        Tuple of (should_skip, reason)
    """
    code = block.code.strip()

    # Skip doctest-style examples (handled by pytest --doctest-modules)
    if code.startswith(">>>"):
        return True, "Doctest format (use pytest --doctest-modules)"

    # Skip pseudo-code patterns
    pseudo_code_patterns = [
        "def test_<",  # Template test names
        "nhl_scrabble.reports.your_report",  # Hypothetical imports
        "nhl_scrabble.mymodule",  # Example module names
        "from your_report import",  # Hypothetical imports
    ]

    if any(pattern in code for pattern in pseudo_code_patterns):
        return True, "Pseudo-code example"

    return False, ""


def test_code_block(block: CodeBlock) -> tuple[bool, str]:
    """Test a code block by executing it.

    Args:
        block: CodeBlock to test

    Returns:
        Tuple of (success, error_message)
    """
    # Check if block should be skipped
    should_skip, skip_reason = should_skip_code_block(block)
    if should_skip:
        return True, f"SKIPPED: {skip_reason}"

    try:
        # Create test script
        test_script = f"""
import sys
sys.path.insert(0, 'src')

{block.code}
"""

        # Safe: Command is hardcoded, test_script contains validated code blocks
        result = subprocess.run(
            ["python", "-c", test_script],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        if result.returncode == 0:
            return True, ""
        return False, result.stderr

    except subprocess.TimeoutExpired:
        return False, "Timeout (10s exceeded)"
    except Exception as e:  # noqa: BLE001
        return False, str(e)


def main() -> int:
    """Extract and test all Markdown examples.

    Returns:
        Exit code (0 for success, 1 for failures)
    """
    docs_dir = Path("docs")
    root_dir = Path()

    # Directories to exclude (contain pseudo-code/illustrative examples)
    exclude_patterns = [
        "docs/explanation/",  # Architectural docs with pseudo-code
        "docs/contributing/",  # Guidelines with example patterns
        "docs/how-to/",  # How-to guides with pseudo-code and context-dependent examples
        "docs/testing/",  # Testing documentation with pytest examples
        "CLAUDE.md",  # Project documentation with illustrative examples
        "DEVELOPMENT.md",  # Development docs with pseudo-code
        "tasks/",  # Task files with pseudo-code
        ".claude/commands/",  # Command docs with examples
    ]

    # Find all Markdown files
    md_files = list(docs_dir.rglob("*.md")) if docs_dir.exists() else []
    md_files += [f for f in root_dir.glob("*.md") if f.name != "sync-report.md"]

    # Filter out excluded paths
    def should_include(file_path: Path) -> bool:
        """Check if a file path should be included in testing."""
        path_str = str(file_path)
        return not any(pattern in path_str for pattern in exclude_patterns)

    md_files = [f for f in md_files if should_include(f)]

    total_blocks = 0
    failed_blocks = 0
    skipped_blocks = 0

    for md_file in md_files:
        blocks = extract_code_blocks(md_file)

        for block in blocks:
            total_blocks += 1
            success, message = test_code_block(block)

            if not success:
                failed_blocks += 1
                print(f"❌ FAILED: {block.file}:{block.line}")
                print(f"   Error: {message}")
                print()
            elif message.startswith("SKIPPED"):
                skipped_blocks += 1

    # Summary output (CLI script, print is appropriate)
    print(f"\n{'='*60}")
    print("Markdown Example Test Summary")
    print(f"{'='*60}")
    print(f"Total examples: {total_blocks}")
    print(f"Passed: {total_blocks - failed_blocks - skipped_blocks}")
    print(f"Skipped: {skipped_blocks}")
    print(f"Failed: {failed_blocks}")

    return 1 if failed_blocks > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
