#!/usr/bin/env python3
"""Detect and validate Bash script dependencies.

This script analyzes Bash scripts to:
- Identify external command dependencies
- Verify scripts check for command availability
- Generate documentation of required dependencies
"""

import re
import sys
from collections import defaultdict
from pathlib import Path

type CommandUsage = dict[str, list[int]]  # command -> line numbers

# Bash built-ins and common commands that don't need checking
COMMON_COMMANDS = {
    "bash",
    "sh",
    "cd",
    "echo",
    "printf",
    "exit",
    "return",
    "if",
    "then",
    "else",
    "elif",
    "fi",
    "for",
    "while",
    "until",
    "do",
    "done",
    "case",
    "esac",
    "function",
    "set",
    "unset",
    "export",
    "readonly",
    "local",
    "declare",
    "typeset",
    "source",
    ".",
    "eval",
    "exec",
    "true",
    "false",
    "test",
    "[",
    "[[",
    "read",
    "shift",
    "getopts",
    "break",
    "continue",
    "trap",
    "wait",
    "jobs",
    "bg",
    "fg",
    "kill",
    "sleep",
    "pwd",
    "pushd",
    "popd",
    "dirs",
    "alias",
    "unalias",
    "type",
    "hash",
    "times",
    "ulimit",
    "umask",
    "command",
}


def extract_commands(script_path: Path) -> CommandUsage:
    """Extract external commands used in Bash script.

    Args:
        script_path: Path to Bash script

    Returns:
        Dict mapping command name to list of line numbers where used
    """
    content = script_path.read_text()
    lines = content.split("\n")

    commands: defaultdict[str, list[int]] = defaultdict(list)

    for line_num, line in enumerate(lines, 1):
        # Skip comments and empty lines
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Find command calls using multiple patterns
        patterns = [
            r"\b([\w-]+)\s",  # command followed by space/args
            r"\$\(([\w-]+)",  # command substitution
            r"`([\w-]+)",  # backtick substitution
            r"\|\s*([\w-]+)",  # piped command
            r"&&\s*([\w-]+)",  # and command
            r"\|\|\s*([\w-]+)",  # or command
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, line):
                cmd = match.group(1)
                # Skip common commands and private functions (starting with _)
                if cmd not in COMMON_COMMANDS and not cmd.startswith("_"):
                    commands[cmd].append(line_num)

    return dict(commands)


def check_availability_check(script_path: Path, command: str) -> bool:
    """Check if script validates command availability.

    Args:
        script_path: Path to Bash script
        command: Command name to check for

    Returns:
        True if script checks for command availability, False otherwise
    """
    content = script_path.read_text()

    # Look for common availability check patterns
    patterns = [
        rf"command\s+-v\s+{re.escape(command)}",
        rf"which\s+{re.escape(command)}",
        rf"type\s+{re.escape(command)}",
        rf"hash\s+{re.escape(command)}",
        rf"\[\s+-x\s+.*{re.escape(command)}",  # test -x /path/to/command
    ]

    return any(re.search(pattern, content) for pattern in patterns)


def main() -> int:  # noqa: C901
    """Execute Bash script dependency analysis.

    Complexity justified: Orchestrates dependency extraction, validation,
    and reporting across multiple scripts. Breaking into smaller functions
    would scatter the control flow.

    Returns:
        Exit code: 0 if all dependencies validated, 1 if missing checks
    """
    scripts_dir = Path("scripts")
    if not scripts_dir.exists():
        print("No scripts/ directory found")
        return 0

    scripts = list(scripts_dir.glob("*.sh"))
    if not scripts:
        print("No Bash scripts found in scripts/")
        return 0

    print("Analyzing Bash script dependencies...")
    print("=" * 60)

    all_deps: defaultdict[str, set[str]] = defaultdict(set)
    missing_checks: list[tuple[str, str, list[int]]] = []

    for script in sorted(scripts):
        commands = extract_commands(script)

        if commands:
            print(f"\n{script.name}:")
            print(f"  External commands: {len(commands)}")

            for cmd, line_nums in sorted(commands.items()):
                all_deps[cmd].add(script.name)

                has_check = check_availability_check(script, cmd)
                status = "✓" if has_check else "✗"
                print(f"    {status} {cmd:<20} (lines: {', '.join(map(str, line_nums))})")

                if not has_check:
                    missing_checks.append((script.name, cmd, line_nums))
        else:
            print(f"\n{script.name}:")
            print("  No external commands detected")

    # Summary
    print("\n" + "=" * 60)
    print("DEPENDENCY SUMMARY")
    print("=" * 60)

    if all_deps:
        for cmd, scripts_set in sorted(all_deps.items()):
            print(f"  {cmd:<20} → {', '.join(sorted(scripts_set))}")
    else:
        print("  No external dependencies found")

    # Missing checks
    if missing_checks:
        print("\n" + "=" * 60)
        print("MISSING AVAILABILITY CHECKS")
        print("=" * 60)
        print("\nThe following commands are used but not validated:")

        for script_name, cmd, line_nums in missing_checks:
            print(f"  {script_name}:{min(line_nums)} → {cmd}")

        print("\n💡 Recommendation: Add availability checks like:")
        print("    if ! command -v COMMAND &> /dev/null; then")
        print('        echo "Error: COMMAND not found" >&2')
        print("        exit 1")
        print("    fi")

        return 1

    print("\n✅ All external commands have availability checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
