#!/usr/bin/env python3
"""Check Bash script documentation completeness.

This script validates that Bash scripts follow documentation best practices:
- File headers with purpose/description
- Usage documentation for scripts with arguments
- Function documentation
- Exit code documentation
- Dependency documentation
"""

import re
import sys
from pathlib import Path

type Issues = list[str]


def check_bash_documentation(script_path: Path) -> Issues:
    """Check Bash script documentation completeness.

    Complexity justified: Must check 7 different documentation requirements
    (shebang, header, purpose, usage, functions, exit codes, dependencies).
    Breaking into smaller functions would reduce readability.

    Args:
        script_path: Path to Bash script to check

    Returns:
        List of documentation issues found (empty if all checks pass)
    """
    issues: Issues = []
    content = script_path.read_text()
    lines = content.split("\n")

    # Check 1: Shebang line
    if not lines[0].startswith("#!"):
        issues.append("Missing shebang line (should be #!/usr/bin/env bash)")

    # Check 2: File header comment (within first 10 lines)
    has_header = any(line.strip().startswith("#") and len(line.strip()) > 1 for line in lines[1:10])
    if not has_header:
        issues.append("Missing file header documentation (first 10 lines)")

    # Check 3: Purpose/Description
    header_text = "\n".join(lines[:20])
    if not re.search(r"#.*(?:Purpose|Description):", header_text, re.IGNORECASE):
        issues.append("Missing Purpose/Description in header")

    # Check 4: Usage documentation (if script accepts arguments)
    uses_args = bool(re.search(r"\$\{?\d+\}?|\$@|\$\*", content))
    if uses_args and not re.search(r"#.*(?:Usage|Arguments?):", header_text, re.IGNORECASE):
        issues.append("Script accepts arguments but missing Usage documentation")

    # Check 5: Function documentation
    functions = re.findall(r"^(?:function\s+)?(\w+)\s*\(\)", content, re.MULTILINE)
    for func_name in functions:
        # Look for comment before function
        func_pattern = rf"^(?:function\s+)?{re.escape(func_name)}\s*\(\)"
        match = re.search(func_pattern, content, re.MULTILINE)
        if match:
            lines_before = content[: match.start()].split("\n")[-5:]
            has_comment = any(line.strip().startswith("#") for line in lines_before)
            if not has_comment:
                issues.append(f"Function '{func_name}' missing documentation comment")

    # Check 6: Exit code documentation
    has_exit = "exit" in content
    has_nonzero_exit = bool(re.search(r"exit\s+[1-9]", content))
    if (
        has_exit
        and has_nonzero_exit
        and not re.search(r"#.*(?:Exit [Cc]odes?|Returns?):", header_text)
    ):
        issues.append("Script uses non-zero exit codes but missing exit code documentation")

    # Check 7: Dependency documentation
    external_cmds = set(
        re.findall(
            r"\b(curl|wget|jq|git|docker|make|npm|yarn|pip|python|node|java|mvn|"
            r"gcc|cmake|go|rustc|cargo|kubectl|helm|terraform|ansible|"
            r"codeql|unzip)\b",
            content,
        ),
    )
    if external_cmds and not re.search(
        r"#.*(?:Dependencies|Requires?):",
        header_text,
        re.IGNORECASE,
    ):
        issues.append(
            f"Uses external commands but missing dependency documentation: "
            f"{', '.join(sorted(external_cmds))}",
        )

    return issues


def main() -> int:
    """Execute Bash script documentation validation.

    Returns:
        Exit code: 0 if all scripts properly documented, 1 otherwise
    """
    scripts_dir = Path("scripts")
    if not scripts_dir.exists():
        print("No scripts/ directory found")
        return 0

    scripts = list(scripts_dir.glob("*.sh"))
    if not scripts:
        print("No Bash scripts found in scripts/")
        return 0

    print("Checking Bash script documentation...")
    print("=" * 60)

    total_issues = 0
    for script in sorted(scripts):
        issues = check_bash_documentation(script)
        if issues:
            print(f"\n{script}:")
            for issue in issues:
                print(f"  ✗ {issue}")
            total_issues += len(issues)
        else:
            print(f"\n{script}:")
            print("  ✓ All documentation checks passed")

    print("\n" + "=" * 60)
    if total_issues:
        print(f"❌ Found {total_issues} documentation issue(s)")
        return 1

    print("✅ All Bash scripts properly documented")
    return 0


if __name__ == "__main__":
    sys.exit(main())
