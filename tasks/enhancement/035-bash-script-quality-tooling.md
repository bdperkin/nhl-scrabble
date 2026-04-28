# Add Comprehensive Bash Script Quality Tooling

**GitHub Issue**: [#424](https://github.com/bdperkin/nhl-scrabble/issues/424)

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

6-8 hours (phased implementation)

## Description

Add comprehensive Python-based quality tooling for Bash scripts to ensure consistent formatting, detect style violations, enforce security best practices, validate documentation, and track dependencies. Currently, the project has 2 Bash scripts (`scripts/codeql_local.sh`, `scripts/install_codeql.sh`) with no automated quality checks beyond basic pre-commit hooks (shebang check).

This enhancement will bring Bash scripts to the same quality standard as Python code, with automated formatting, linting, security scanning, documentation validation, and dependency tracking - all using Python-based tools to avoid system binary dependencies.

## Current State

**Bash Scripts in Project**:
- `scripts/codeql_local.sh` (107 lines) - CodeQL security analysis script
- `scripts/install_codeql.sh` (40 lines) - CodeQL CLI installation script
- **Total**: 147 lines of Bash code

**Existing Quality Checks**:
- ✅ Shebang validation (`check-shebang-scripts-are-executable`)
- ✅ Executable bit check
- ❌ No formatting standards
- ❌ No style linting
- ❌ No security pattern checking
- ❌ No documentation validation
- ❌ No dependency tracking

**Current Issues**:
1. Inconsistent indentation (no enforced standard)
2. No automated style checking
3. Security best practices not enforced (e.g., `set -euo pipefail`, `curl --fail`)
4. No validation that scripts document their purpose, usage, dependencies
5. No tracking of external command dependencies
6. No validation that scripts check for required commands before using them

**Constraint**: Must use Python-based or pygrep tools only (avoid system binaries like `shellcheck`, `shfmt`)

## Proposed Solution

Implement comprehensive Bash script quality tooling in three phases, using only Python-based tools to maintain consistency with project tooling philosophy.

### Phase 1: Essential Quality Tools (High Priority)

**1. beautysh - Bash Formatting**

Python-based Bash beautifier/formatter for consistent code style.

**Features**:
- Consistent indentation (2 spaces - project standard)
- Standardized spacing around operators
- Aligned continuation lines
- Function style enforcement (`function name()` or `name()`)

**Integration**:
```yaml
# .pre-commit-config.yaml
- repo: https://github.com/lovesegfault/beautysh
  rev: v6.2.1
  hooks:
    - id: beautysh
      name: beautysh - Format Bash scripts
      description: Auto-format Bash scripts with beautysh
      args: ['--indent-size', '2', '--force-function-style', 'fnpar']
      files: \.sh$
```

**Tox Environment**:
```ini
[testenv:beautysh]
description = Format Bash scripts with beautysh
skip_install = true
deps = beautysh>=6.2.1
commands =
    beautysh --indent-size 2 --force-function-style fnpar scripts/*.sh
labels = format, shell

[testenv:beautysh-check]
description = Check Bash script formatting (no changes)
skip_install = true
deps = beautysh>=6.2.1
commands =
    beautysh --check --indent-size 2 scripts/*.sh
labels = quality, shell
```

**Makefile Targets**:
```makefile
####################
# Shell Scripting
####################

beautysh: ## Shell - format Bash scripts with beautysh
	@printf "$(BLUE)Formatting Bash scripts with beautysh...$(NC)\n"
	@beautysh --indent-size 2 --force-function-style fnpar scripts/*.sh
	@printf "$(GREEN)✓ Bash scripts formatted$(NC)\n"

beautysh-check: ## Shell - check Bash script formatting
	@printf "$(BLUE)Checking Bash script formatting...$(NC)\n"
	@beautysh --check --indent-size 2 scripts/*.sh
```

**2. bashate - Bash Linting**

OpenStack Bash style checker (Python) for detecting style violations and syntax errors.

**Rules Enforced**:
- E001: Trailing whitespace
- E002: Tab indentation (prefer spaces)
- E003: Indent not multiple of 4 (customizable)
- E004: File did not end with newline
- E005: Line too long (>79 chars, customizable to 100)
- E006: Line starting with space
- E010: `do` not on same line as `for`/`while`
- E011: `then` not on same line as `if`
- E012: No semicolon after `esac`
- E020: Function declaration format
- E040: Syntax error

**Configuration**:
Create `.bashate` file:
```ini
[bashate]
# Allow 2-space indentation (project standard)
ignore = E003,E006
# Match project Python line length
max_line_length = 100
```

**Integration**:
```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: bashate
      name: bashate - Bash style checker
      description: Check Bash scripts for style violations and syntax errors
      entry: bashate
      language: python
      additional_dependencies: ['bashate>=2.1.1']
      files: \.sh$
      args: ['--ignore=E003,E006', '--max-line-length=100']
```

**Tox Environment**:
```ini
[testenv:bashate]
description = Lint Bash scripts with bashate
skip_install = true
deps = bashate>=2.1.1
commands =
    bashate --ignore=E003,E006 --max-line-length=100 scripts/*.sh
labels = lint, quality, shell
```

**Makefile Target**:
```makefile
bashate: ## Shell - lint Bash scripts with bashate
	@printf "$(BLUE)Linting Bash scripts with bashate...$(NC)\n"
	@bashate --ignore=E003,E006 --max-line-length=100 scripts/*.sh
	@printf "$(GREEN)✓ Bash linting complete$(NC)\n"
```

**3. Security Pattern Checking (pygrep)**

Add 8 custom pygrep patterns to enforce Bash security best practices.

**Patterns**:

```yaml
# .pre-commit-config.yaml

  # ============================================================================
  # Shell Script Security - Bash Best Practices
  # ============================================================================

  - repo: local
    hooks:
      - id: bash-check-set-errexit
        name: Bash - require error handling (set -e/-u/-o pipefail)
        description: |
          Ensure scripts use proper error handling flags.
          Scripts should start with: set -euo pipefail
        entry: '^(?!.*set\s+-[euo]|.*set\s+-o\s+(errexit|nounset|pipefail))'
        language: pygrep
        files: \.sh$
        args: ['--negate']

      - id: bash-no-eval
        name: Bash - prohibit eval usage
        description: Detect dangerous eval usage (security risk)
        entry: '\beval\b'
        language: pygrep
        files: \.sh$

      - id: bash-check-curl-fail
        name: Bash - ensure curl uses --fail flag
        description: curl should use --fail to catch HTTP errors
        entry: 'curl\s+(?!.*--fail)'
        language: pygrep
        files: \.sh$

      - id: bash-check-wget-quiet
        name: Bash - ensure wget uses --quiet/-q flag
        description: wget should use --quiet for cleaner CI output
        entry: 'wget\s+(?!.*(-q|--quiet))'
        language: pygrep
        files: \.sh$

      - id: bash-no-hardcoded-tmp
        name: Bash - no hardcoded /tmp paths
        description: Use $TMPDIR or mktemp instead of hardcoded /tmp
        entry: '(?<!#).*(?<!\$)\b/tmp/'
        language: pygrep
        files: \.sh$

      - id: bash-prefer-command-substitution
        name: Bash - prefer $() over backticks
        description: Use modern command substitution syntax $() instead of backticks
        entry: '`[^`]+`'
        language: pygrep
        files: \.sh$

      - id: bash-prefer-modern-test
        name: Bash - prefer [[ ]] over [ ]
        description: Use modern test syntax [[ ]] for better safety
        entry: '(?<!#).*\[\s+[^\[]'
        language: pygrep
        files: \.sh$

      - id: bash-check-quoted-variables
        name: Bash - check for potentially unquoted variables
        description: Variables should generally be quoted to prevent word splitting
        entry: '\$[A-Z_][A-Z0-9_]*(?!\}|\"|\[)'
        language: pygrep
        files: \.sh$
        # This is informational - may have false positives
```

**Expected Detections in Current Scripts**:
- ✅ Both scripts use `set -euo pipefail` (PASS)
- ✅ No `eval` usage (PASS)
- ⚠️ `wget` in `install_codeql.sh` missing `--quiet` flag (WARN)
- ✅ `curl` not used (N/A)
- ✅ No hardcoded `/tmp` paths (PASS)
- ✅ No backticks used (PASS)
- ⚠️ May have `[ ]` instead of `[[ ]]` (CHECK)
- ⚠️ May have unquoted variables (CHECK)

### Phase 2: Documentation & Dependency Validation (Medium Priority)

**4. Documentation Completeness Checker**

Custom Python script to validate Bash script documentation.

**Script**: `scripts/check_bash_docs.py`

**Checks**:
1. Shebang line present
2. File header comment exists (within first 10 lines)
3. Purpose/Description documented
4. Usage documented (if script accepts arguments)
5. Functions have description comments
6. Exit codes documented (if non-zero exits used)
7. Dependencies documented (if external commands used)

**Implementation**:
```python
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
from typing import TypeAlias

Issues: TypeAlias = list[str]


def check_bash_documentation(script_path: Path) -> Issues:
    """Check Bash script documentation completeness.

    Args:
        script_path: Path to Bash script to check

    Returns:
        List of documentation issues found (empty if all checks pass)
    """
    issues: Issues = []
    content = script_path.read_text()
    lines = content.split('\n')

    # Check 1: Shebang line
    if not lines[0].startswith('#!'):
        issues.append("Missing shebang line (should be #!/usr/bin/env bash)")

    # Check 2: File header comment (within first 10 lines)
    has_header = any(
        line.strip().startswith('#') and len(line.strip()) > 1
        for line in lines[1:10]
    )
    if not has_header:
        issues.append("Missing file header documentation (first 10 lines)")

    # Check 3: Purpose/Description
    header_text = '\n'.join(lines[:20])
    if not re.search(r'#.*(?:Purpose|Description):', header_text, re.I):
        issues.append("Missing Purpose/Description in header")

    # Check 4: Usage documentation (if script accepts arguments)
    uses_args = bool(re.search(r'\$\{?\d+\}?|\$@|\$\*', content))
    if uses_args:
        if not re.search(r'#.*(?:Usage|Arguments?):', header_text, re.I):
            issues.append("Script accepts arguments but missing Usage documentation")

    # Check 5: Function documentation
    functions = re.findall(r'^(?:function\s+)?(\w+)\s*\(\)', content, re.M)
    for func_name in functions:
        # Look for comment before function
        func_pattern = rf'^(?:function\s+)?{re.escape(func_name)}\s*\(\)'
        match = re.search(func_pattern, content, re.M)
        if match:
            lines_before = content[:match.start()].split('\n')[-5:]
            has_comment = any(line.strip().startswith('#') for line in lines_before)
            if not has_comment:
                issues.append(f"Function '{func_name}' missing documentation comment")

    # Check 6: Exit code documentation
    has_exit = 'exit' in content
    has_nonzero_exit = bool(re.search(r'exit\s+[1-9]', content))
    if has_exit and has_nonzero_exit:
        if not re.search(r'#.*(?:Exit [Cc]odes?|Returns?):', header_text):
            issues.append("Script uses non-zero exit codes but missing exit code documentation")

    # Check 7: Dependency documentation
    external_cmds = set(re.findall(
        r'\b(curl|wget|jq|git|docker|make|npm|yarn|pip|python|node|java|mvn|'
        r'gcc|cmake|go|rustc|cargo|kubectl|helm|terraform|ansible)\b',
        content
    ))
    if external_cmds:
        if not re.search(r'#.*(?:Dependencies|Requires?):', header_text, re.I):
            issues.append(
                f"Uses external commands but missing dependency documentation: "
                f"{', '.join(sorted(external_cmds))}"
            )

    return issues


def main() -> int:
    """Main entry point.

    Returns:
        Exit code: 0 if all scripts properly documented, 1 otherwise
    """
    scripts_dir = Path('scripts')
    if not scripts_dir.exists():
        print("No scripts/ directory found")
        return 0

    scripts = list(scripts_dir.glob('*.sh'))
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


if __name__ == '__main__':
    sys.exit(main())
```

**Pre-commit Hook**:
```yaml
- repo: local
  hooks:
    - id: check-bash-docs
      name: Check Bash script documentation
      description: Validate Bash script documentation completeness
      entry: python scripts/check_bash_docs.py
      language: python
      pass_filenames: false
      files: \.sh$
```

**Tox Environment**:
```ini
[testenv:check-bash-docs]
description = Check Bash script documentation completeness
skip_install = true
commands =
    python scripts/check_bash_docs.py
labels = docs, shell
```

**Makefile Target**:
```makefile
bash-docs: ## Shell - validate Bash script documentation
	@printf "$(BLUE)Checking Bash script documentation...$(NC)\n"
	@python scripts/check_bash_docs.py
```

**5. Dependency Detection & Validation**

Custom Python script to detect external command dependencies and validate availability checks.

**Script**: `scripts/check_bash_deps.py`

**Features**:
1. Extract all external command calls from scripts
2. Categorize commands (common vs external)
3. Check if script validates command availability before use
4. Generate dependency list for documentation
5. Suggest `command -v` checks for missing validations

**Implementation**:
```python
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
from typing import TypeAlias

CommandUsage: TypeAlias = dict[str, list[int]]  # command -> line numbers

# Bash built-ins and common commands that don't need checking
COMMON_COMMANDS = {
    'bash', 'sh', 'cd', 'echo', 'printf', 'exit', 'return',
    'if', 'then', 'else', 'elif', 'fi', 'for', 'while', 'until',
    'do', 'done', 'case', 'esac', 'function', 'set', 'unset',
    'export', 'readonly', 'local', 'declare', 'typeset',
    'source', '.', 'eval', 'exec', 'true', 'false', 'test',
    '[', '[[', 'read', 'shift', 'getopts', 'break', 'continue',
    'trap', 'wait', 'jobs', 'bg', 'fg', 'kill', 'sleep',
    'pwd', 'pushd', 'popd', 'dirs', 'alias', 'unalias',
    'type', 'hash', 'times', 'ulimit', 'umask',
}


def extract_commands(script_path: Path) -> CommandUsage:
    """Extract external commands used in Bash script.

    Args:
        script_path: Path to Bash script

    Returns:
        Dict mapping command name to list of line numbers where used
    """
    content = script_path.read_text()
    lines = content.split('\n')

    commands: defaultdict[str, list[int]] = defaultdict(list)

    for line_num, line in enumerate(lines, 1):
        # Skip comments and empty lines
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue

        # Find command calls using multiple patterns
        patterns = [
            r'\b([\w-]+)\s',          # command followed by space/args
            r'\$\(([\w-]+)',          # command substitution
            r'`([\w-]+)',             # backtick substitution
            r'\|\s*([\w-]+)',         # piped command
            r'&&\s*([\w-]+)',         # and command
            r'\|\|\s*([\w-]+)',       # or command
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, line):
                cmd = match.group(1)
                # Skip common commands and private functions (starting with _)
                if cmd not in COMMON_COMMANDS and not cmd.startswith('_'):
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
        rf'command\s+-v\s+{re.escape(command)}',
        rf'which\s+{re.escape(command)}',
        rf'type\s+{re.escape(command)}',
        rf'hash\s+{re.escape(command)}',
        rf'\[\s+-x\s+.*{re.escape(command)}',  # test -x /path/to/command
    ]

    return any(re.search(pattern, content) for pattern in patterns)


def main() -> int:
    """Main entry point.

    Returns:
        Exit code: 0 if all dependencies validated, 1 if missing checks
    """
    scripts_dir = Path('scripts')
    if not scripts_dir.exists():
        print("No scripts/ directory found")
        return 0

    scripts = list(scripts_dir.glob('*.sh'))
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


if __name__ == '__main__':
    sys.exit(main())
```

**Pre-commit Hook**:
```yaml
- repo: local
  hooks:
    - id: check-bash-deps
      name: Check Bash script dependencies
      description: Detect and validate external command dependencies
      entry: python scripts/check_bash_deps.py
      language: python
      pass_filenames: false
      files: \.sh$
      stages: [manual]  # Manual run only (informational)
```

**Tox Environment**:
```ini
[testenv:bash-deps]
description = Check Bash script dependencies
skip_install = true
commands =
    python scripts/check_bash_deps.py
labels = shell
```

**Makefile Target**:
```makefile
bash-deps: ## Shell - check Bash script dependencies
	@printf "$(BLUE)Analyzing Bash script dependencies...$(NC)\n"
	@python scripts/check_bash_deps.py
```

### Phase 3: Advanced Analysis (Optional)

**6. Static Coverage Analysis**

Custom Python script to calculate static analysis coverage metrics.

**Script**: `scripts/bash_coverage.py`

**Metrics**:
- Total lines vs comment lines (comment coverage %)
- Functions vs documented functions (function doc coverage %)
- Error handling presence (set -euo pipefail)
- Availability checks coverage (% of external commands checked)

**Implementation**: See full script in appendix

**7. Aggregate Quality Check**

Combined Makefile target to run all Bash quality checks.

```makefile
bash-validate: beautysh-check bashate bash-docs bash-deps ## Shell - run all Bash quality checks
	@printf "$(GREEN)✅ All Bash quality checks passed$(NC)\n"

bash-fix: beautysh ## Shell - auto-fix Bash quality issues
	@printf "$(GREEN)✅ Bash scripts auto-formatted$(NC)\n"
```

## Implementation Steps

### Phase 1: Essential Quality Tools (2-3 hours)

1. **Add Python dependencies to pyproject.toml**
   ```toml
   [project.optional-dependencies]
   shell = [
       "beautysh>=6.2.1",
       "bashate>=2.1.1",
   ]
   ```

2. **Add pre-commit hooks**
   - Add beautysh hook
   - Add bashate hook
   - Add 8 pygrep security pattern hooks
   - Update hook count in documentation

3. **Add tox environments**
   - `[testenv:beautysh]` - Format scripts
   - `[testenv:beautysh-check]` - Check formatting
   - `[testenv:bashate]` - Lint scripts
   - Add `shell` label to tox labels

4. **Add Makefile targets**
   - Add "Shell Scripting" section
   - Add beautysh, beautysh-check targets
   - Add bashate target
   - Update `make help` output

5. **Apply beautysh formatting to existing scripts**
   - Run `beautysh --indent-size 2 scripts/*.sh`
   - Review formatting changes
   - Commit as "style: format bash scripts with beautysh"

6. **Fix bashate violations**
   - Run `bashate --ignore=E003,E006 --max-line-length=100 scripts/*.sh`
   - Fix any violations found
   - Commit as "style: fix bashate violations"

7. **Update GitHub CI workflow**
   - Add Bash quality check job
   - Run `tox -e bashate,beautysh-check`

8. **Update CONTRIBUTING.md**
   - Add "Bash Script Development" section
   - Document beautysh and bashate usage
   - Document security patterns enforced

### Phase 2: Documentation & Dependencies (2-3 hours)

9. **Create check_bash_docs.py script**
   - Implement documentation validator
   - Add comprehensive docstrings
   - Make executable
   - Test on existing scripts

10. **Create check_bash_deps.py script**
    - Implement dependency detector
    - Add comprehensive docstrings
    - Make executable
    - Test on existing scripts

11. **Add scripts to pre-commit**
    - Add check-bash-docs hook
    - Add check-bash-deps hook (manual stage)

12. **Add tox environments**
    - `[testenv:check-bash-docs]`
    - `[testenv:bash-deps]`

13. **Add Makefile targets**
    - bash-docs target
    - bash-deps target
    - bash-validate aggregate target

14. **Update existing scripts to pass checks**
    - Add missing documentation headers
    - Document dependencies
    - Ensure availability checks present

### Phase 3: Advanced Analysis (1-2 hours, Optional)

15. **Create bash_coverage.py script**
    - Implement coverage analyzer
    - Generate coverage report

16. **Add coverage to CI**
    - Report metrics in workflow
    - Add to quality dashboard

17. **Create aggregate targets**
    - bash-validate (run all checks)
    - bash-fix (auto-fix issues)

## Testing Strategy

### Pre-Implementation Validation

1. **Inventory current Bash scripts**
   ```bash
   find scripts/ -name "*.sh" -type f
   ```

2. **Run beautysh in check mode**
   ```bash
   beautysh --check --indent-size 2 scripts/*.sh
   # Expect: Formatting changes needed
   ```

3. **Run bashate**
   ```bash
   bashate --ignore=E003,E006 --max-line-length=100 scripts/*.sh
   # Expect: May find E005 (line too long) or other violations
   ```

4. **Test pygrep patterns**
   ```bash
   # Test each pattern individually on existing scripts
   grep -E 'set\s+-[euo]' scripts/*.sh  # Should find error handling
   grep -E '\beval\b' scripts/*.sh      # Should find none
   grep -E 'wget' scripts/*.sh          # Check for --quiet flag
   ```

### Post-Implementation Validation

1. **Run all pre-commit hooks**
   ```bash
   pre-commit run --all-files
   # All hooks should pass
   ```

2. **Run all tox environments**
   ```bash
   tox -e beautysh-check,bashate,check-bash-docs,bash-deps
   # All should pass
   ```

3. **Run all Makefile targets**
   ```bash
   make beautysh-check
   make bashate
   make bash-docs
   make bash-deps
   make bash-validate
   ```

4. **Verify CI integration**
   ```bash
   # Push to feature branch
   # Verify CI runs Bash quality checks
   # All checks should pass
   ```

### Expected Initial Findings

**beautysh** (Formatting):
- Likely minor formatting changes needed
- Indentation should be mostly correct (scripts already use 2 spaces)
- May adjust spacing around operators

**bashate** (Linting):
- Both scripts likely already compliant
- May find E005 violations if any lines > 100 chars
- Scripts use `set -euo pipefail` ✓
- Scripts end with newline ✓

**pygrep Security Patterns**:
- ✅ Both scripts use `set -euo pipefail` (PASS)
- ✅ No `eval` usage (PASS)
- ⚠️ `install_codeql.sh` line 9: `wget -q` → Need to verify `--quiet` vs `-q`
- ✅ No hardcoded `/tmp` (PASS)
- ✅ No backticks (PASS)
- ⚠️ May need to update `[ ]` to `[[ ]]` if found
- ⚠️ May need to quote some variable expansions

**Documentation Checker**:
- ✅ Both scripts have shebang
- ⚠️ May need enhanced file header comments
- ⚠️ May need explicit "Purpose:" and "Usage:" sections
- ⚠️ May need explicit "Dependencies:" section
- ⚠️ Functions may need description comments

**Dependency Detector**:
- `codeql_local.sh`: Uses `codeql`, `python3`, `rm`, `mkdir`
  - ✅ `codeql` availability check exists (line 16-21)
  - ✅ `python3` availability implicit (shebang)
- `install_codeql.sh`: Uses `wget`, `unzip`, `git`
  - ⚠️ May need to add availability checks

## Acceptance Criteria

### Phase 1: Essential Quality Tools

- [x] beautysh added to pre-commit hooks
- [x] beautysh tox environments created (beautysh, beautysh-check)
- [x] beautysh Makefile targets added
- [x] bashate added to pre-commit hooks
- [x] bashate tox environment created
- [x] bashate Makefile target added
- [x] 8 pygrep security patterns added to pre-commit
- [x] All existing Bash scripts pass beautysh check
- [x] All existing Bash scripts pass bashate
- [x] All existing Bash scripts pass pygrep security patterns
- [x] Python dependencies added to pyproject.toml [shell] group
- [x] GitHub CI workflow includes Bash quality checks
- [x] CONTRIBUTING.md documents Bash development workflow
- [x] Pre-commit hook count updated (68 → 76+)

### Phase 2: Documentation & Dependencies

- [x] check_bash_docs.py script created and executable
- [x] check_bash_docs.py has comprehensive docstrings
- [x] check-bash-docs pre-commit hook added
- [x] check-bash-docs tox environment created
- [x] bash-docs Makefile target added
- [x] check_bash_deps.py script created and executable
- [x] check_bash_deps.py has comprehensive docstrings
- [x] check-bash-deps pre-commit hook added (manual stage)
- [x] bash-deps tox environment created
- [x] bash-deps Makefile target added
- [x] All existing Bash scripts pass documentation checks
- [x] All existing Bash scripts have dependency validation
- [x] bash-validate aggregate Makefile target created

### Phase 3: Advanced Analysis (Optional)

- [ ] bash_coverage.py script created
- [ ] Coverage metrics reported in CI
- [ ] bash-fix aggregate Makefile target created
- [ ] Coverage dashboard updated

### General

- [x] All pre-commit hooks pass on existing scripts
- [x] All tox environments pass
- [x] All Makefile targets work correctly
- [x] CI pipeline includes Bash quality checks
- [x] Documentation updated
- [x] No regressions in existing functionality

## Related Files

**New Files**:
- `scripts/check_bash_docs.py` - Documentation validator
- `scripts/check_bash_deps.py` - Dependency detector
- `scripts/bash_coverage.py` - Coverage analyzer (optional)
- `.bashate` - bashate configuration (optional)

**Modified Files**:
- `.pre-commit-config.yaml` - Add 10+ hooks
- `tox.ini` - Add 6+ environments
- `Makefile` - Add 8+ targets
- `pyproject.toml` - Add [shell] dependencies
- `.github/workflows/ci.yml` - Add Bash quality check job
- `CONTRIBUTING.md` - Add Bash development section
- `scripts/codeql_local.sh` - May need formatting/docs updates
- `scripts/install_codeql.sh` - May need formatting/docs updates

## Dependencies

**Required Python Packages**:
```toml
[project.optional-dependencies]
shell = [
    "beautysh>=6.2.1",    # Bash formatting
    "bashate>=2.1.1",     # Bash linting
]
```

**No System Dependencies** - All tools are pure Python

**Pre-commit Hook Dependencies**:
- beautysh (from repo)
- bashate (via additional_dependencies)
- pygrep patterns (built-in)
- Python 3.12+ (for custom scripts)

## Performance Impact

**Pre-commit Execution Time** (estimated):
- beautysh: ~0.5s (2 scripts)
- bashate: ~0.3s (2 scripts)
- 8 pygrep patterns: ~0.2s each = ~1.6s total
- check_bash_docs.py: ~0.3s
- check_bash_deps.py: ~0.3s
- **Total added time**: ~3s

**Tox Execution Time** (estimated):
- beautysh: ~5s (with setup)
- beautysh-check: ~5s
- bashate: ~5s
- check-bash-docs: ~3s
- bash-deps: ~3s
- **Total**: ~21s (can run in parallel)

**CI Pipeline Impact**:
- New job: "Bash Quality Checks" (~30s)
- Total impact: Minimal (< 1% of total CI time)

## Benefits

### Code Quality
- ✅ Consistent formatting across all Bash scripts
- ✅ Style violations caught before PR
- ✅ Syntax errors detected early
- ✅ Modern Bash best practices enforced

### Security
- ✅ Dangerous patterns blocked (eval, unquoted vars)
- ✅ Error handling enforced (set -euo pipefail)
- ✅ Safe command usage (curl --fail, wget --quiet)
- ✅ No hardcoded temporary paths

### Documentation
- ✅ All scripts fully documented
- ✅ Dependencies clearly listed
- ✅ Usage instructions validated
- ✅ Function documentation enforced

### Maintainability
- ✅ Lower barrier to contribution
- ✅ Easier code review
- ✅ Self-documenting scripts
- ✅ Dependency tracking automatic

### Developer Experience
- ✅ Auto-formatting available (beautysh)
- ✅ Fast feedback (pre-commit hooks)
- ✅ Clear error messages
- ✅ Consistent with Python tooling philosophy

## Risks & Mitigation

### Risk: beautysh Changes Script Logic
**Likelihood**: Very Low
**Impact**: High
**Mitigation**:
- Run beautysh first on copy of scripts
- Review all formatting changes carefully
- Test scripts after formatting
- Keep formatting change in separate commit

### Risk: bashate False Positives
**Likelihood**: Low
**Impact**: Low
**Mitigation**:
- Configure ignore flags appropriately (E003, E006)
- Allow inline ignores for exceptions
- Document why rules are ignored

### Risk: pygrep Patterns Too Strict
**Likelihood**: Medium
**Impact**: Low
**Mitigation**:
- Test patterns on existing scripts first
- Make some patterns informational only
- Document pattern rationale
- Allow inline exclusions

### Risk: Documentation Checks Too Strict
**Likelihood**: Low
**Impact**: Low
**Mitigation**:
- Make documentation checks comprehensive but reasonable
- Allow flexibility in documentation format
- Provide clear examples

### Risk: Performance Impact on Pre-commit
**Likelihood**: Very Low
**Impact**: Low
**Mitigation**:
- Total impact < 3s for 2 scripts
- Tools are fast Python-based
- Can disable specific hooks if needed

## Future Enhancements

### Additional Tools (If Constraints Change)
- **shellcheck** - Superior Bash linter (if system binaries allowed)
- **shfmt** - Superior Bash formatter (if system binaries allowed)
- **bats-core** - Bash test framework (if system binaries allowed)

### Additional Validation
- **Shellcheck annotations** - Validate shellcheck directives in comments
- **POSIX compliance** - Check for Bash-isms if POSIX compatibility needed
- **Complexity metrics** - Cyclomatic complexity for Bash functions
- **Security audit** - Deeper security analysis

### Integration Enhancements
- **VS Code integration** - beautysh format-on-save
- **Git hooks** - pre-push validation
- **Dashboard** - Bash quality metrics visualization
- **Badge** - Bash quality status badge for README

## Appendix: Full bash_coverage.py Script

```python
#!/usr/bin/env python3
"""Calculate static analysis coverage for Bash scripts.

This script provides static analysis metrics for Bash scripts:
- Comment coverage (% of lines with comments)
- Function documentation coverage (% of functions documented)
- Error handling coverage (presence of set -euo pipefail)
- Availability check coverage (% of external commands validated)
"""
import re
import sys
from pathlib import Path
from typing import TypedDict


class CoverageMetrics(TypedDict):
    """Coverage metrics for a Bash script."""
    total_lines: int
    comment_lines: int
    comment_coverage: float
    error_handling: bool
    functions: int
    documented_functions: int
    function_doc_coverage: float


def analyze_bash_coverage(script_path: Path) -> CoverageMetrics:
    """Analyze Bash script coverage metrics.

    Args:
        script_path: Path to Bash script

    Returns:
        Dict with coverage metrics
    """
    content = script_path.read_text()
    lines = [line for line in content.split('\n') if line.strip()]

    # Count comment lines
    comment_lines = sum(1 for line in lines if line.strip().startswith('#'))

    # Check error handling
    error_handling = bool(re.search(r'set\s+-[euo]|set\s+-o\s+(errexit|nounset|pipefail)', content))

    # Count functions
    functions = re.findall(r'^(?:function\s+)?(\w+)\s*\(\)', content, re.M)

    # Count documented functions (comment within 3 lines before function)
    documented_functions = 0
    for func_match in re.finditer(r'^(?:function\s+)?(\w+)\s*\(\)', content, re.M):
        lines_before = content[:func_match.start()].split('\n')[-3:]
        if any(line.strip().startswith('#') and len(line.strip()) > 1 for line in lines_before):
            documented_functions += 1

    # Calculate percentages
    comment_coverage = (comment_lines / len(lines) * 100) if lines else 0.0
    function_doc_coverage = (
        (documented_functions / len(functions) * 100)
        if functions
        else 100.0
    )

    return CoverageMetrics(
        total_lines=len(lines),
        comment_lines=comment_lines,
        comment_coverage=comment_coverage,
        error_handling=error_handling,
        functions=len(functions),
        documented_functions=documented_functions,
        function_doc_coverage=function_doc_coverage,
    )


def main() -> int:
    """Main entry point.

    Returns:
        Exit code: 0 (always succeeds, informational only)
    """
    scripts_dir = Path('scripts')
    if not scripts_dir.exists():
        print("No scripts/ directory found")
        return 0

    scripts = list(scripts_dir.glob('*.sh'))
    if not scripts:
        print("No Bash scripts found in scripts/")
        return 0

    print("Bash Script Coverage Report")
    print("=" * 60)

    for script in sorted(scripts):
        metrics = analyze_bash_coverage(script)

        print(f"\n{script.name}:")
        print(f"  Lines: {metrics['total_lines']}")
        print(f"  Comments: {metrics['comment_lines']} "
              f"({metrics['comment_coverage']:.1f}% coverage)")
        print(f"  Error handling: {'✓' if metrics['error_handling'] else '✗'}")
        print(f"  Functions: {metrics['functions']}")
        print(f"  Documented functions: {metrics['documented_functions']} "
              f"({metrics['function_doc_coverage']:.1f}% coverage)")

    print("\n" + "=" * 60)
    print("✅ Coverage analysis complete")
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

## Implementation Notes

*To be filled during implementation:*
- Actual formatting changes made by beautysh
- Bashate violations found and fixed
- Pygrep pattern matches/issues
- Documentation improvements needed
- Dependency validation findings
- Actual effort vs estimated
