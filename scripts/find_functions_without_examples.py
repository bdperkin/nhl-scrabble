#!/usr/bin/env python3
"""Find functions lacking usage examples in docstrings.

This script analyzes Python source files to identify functions that lack
usage examples in their docstrings. It helps track docstring example coverage
and identify which functions would benefit most from additional documentation.

Examples:
    Basic usage:

    >>> python scripts/find_functions_without_examples.py

    With statistics:

    >>> python scripts/find_functions_without_examples.py --stats

    Specific directory:

    >>> python scripts/find_functions_without_examples.py src/nhl_scrabble/formatters/
"""

from __future__ import annotations

import argparse
import ast
from pathlib import Path


def has_examples(docstring: str | None) -> bool:
    r"""Check if docstring contains usage examples.

    Args:
        docstring: The docstring to check (can be None)

    Returns:
        True if docstring contains examples, False otherwise

    Examples:
        Docstring with examples:

        >>> has_examples("Function description.\n\nExamples:\n    >>> foo()\n    42")
        True

        Docstring without examples:

        >>> has_examples("Just a description.")
        False

        No docstring:

        >>> has_examples(None)
        False
    """
    if not docstring:
        return False
    return "Examples:" in docstring or ">>>" in docstring


def find_functions_without_examples(file_path: Path) -> list[tuple[str, int]]:
    """Find functions in a file without examples.

    Args:
        file_path: Path to Python file to analyze

    Returns:
        List of tuples (function_name, line_number) for functions without examples

    Examples:
        Analyze a file:

        >>> from pathlib import Path
        >>> file_path = Path("src/nhl_scrabble/validators.py")
        >>> functions = find_functions_without_examples(file_path)
        >>> isinstance(functions, list)
        True
        >>> all(isinstance(item, tuple) and len(item) == 2 for item in functions)
        True
    """
    try:
        content = file_path.read_text()
        tree = ast.parse(content, filename=str(file_path))
    except (OSError, SyntaxError) as e:
        print(f"Error parsing {file_path}: {e}")
        return []

    functions_without_examples = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            # Skip private functions (leading _)
            if node.name.startswith("_") and not node.name.startswith("__"):
                continue

            docstring = ast.get_docstring(node)
            if not has_examples(docstring):
                functions_without_examples.append((node.name, node.lineno))

    return functions_without_examples


def analyze_directory(
    directory: Path,
    *,
    show_stats: bool = False,  # noqa: ARG001
) -> dict[str, list[tuple[str, int]]]:
    """Analyze all Python files in a directory.

    Args:
        directory: Directory to analyze
        show_stats: Whether to show statistics (passed to print_results)

    Returns:
        Dictionary mapping file paths to lists of (function_name, line_number)

    Examples:
        Analyze source directory:

        >>> from pathlib import Path
        >>> results = analyze_directory(Path("src/nhl_scrabble"))
        >>> isinstance(results, dict)
        True
    """
    results = {}

    for file_path in directory.rglob("*.py"):
        # Skip __init__.py files
        if file_path.name == "__init__.py":
            continue

        # Skip test files
        if "test" in str(file_path):
            continue

        functions = find_functions_without_examples(file_path)
        if functions:
            results[str(file_path.relative_to(directory.parent))] = functions

    return results


def print_results(
    results: dict[str, list[tuple[str, int]]],
    *,
    show_stats: bool = False,
) -> None:
    """Print analysis results.

    Args:
        results: Dictionary of file paths to functions without examples
        show_stats: Whether to show statistics

    Examples:
        Print results:

        >>> results = {"file.py": [("func1", 10), ("func2", 20)]}
        >>> print_results(results)
        file.py:
          func1 (line 10)
          func2 (line 20)
        <BLANKLINE>
        Total: 2 functions in 1 files
    """
    if not results:
        print("✅ All functions have examples!")
        return

    # Print detailed results
    for file_path, functions in sorted(results.items()):
        print(f"\n{file_path}:")
        for func_name, line_no in functions:
            print(f"  {func_name} (line {line_no})")

    # Print summary
    total_functions = sum(len(funcs) for funcs in results.values())
    total_files = len(results)
    print(f"\nTotal: {total_functions} functions in {total_files} files")

    # Print statistics if requested
    if show_stats:
        print("\n" + "=" * 60)
        print("STATISTICS")
        print("=" * 60)

        # Sort by number of functions
        sorted_files = sorted(
            results.items(),
            key=lambda x: len(x[1]),
            reverse=True,
        )

        print(f"\n{'File':<50} {'Functions':<10}")
        print("-" * 60)
        for file_path, functions in sorted_files[:10]:
            file_name = Path(file_path).name
            print(f"{file_name:<50} {len(functions):<10}")


def main() -> None:
    """Run the function example coverage analysis.

    Examples:
        Run as script:

        >>> # python scripts/find_functions_without_examples.py
        ... # Analyzes src/nhl_scrabble/ directory
    """
    parser = argparse.ArgumentParser(
        description="Find functions without usage examples in docstrings",
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default="src/nhl_scrabble",
        help="Directory to analyze (default: src/nhl_scrabble)",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show detailed statistics",
    )

    args = parser.parse_args()

    directory = Path(args.directory)
    if not directory.exists():
        print(f"Error: Directory not found: {directory}")
        return

    print(f"Analyzing: {directory}")
    print("=" * 60)

    results = analyze_directory(directory, show_stats=args.stats)
    print_results(results, show_stats=args.stats)


if __name__ == "__main__":
    main()
