# Validate Pre-commit Hook

______________________________________________________________________

## title: 'Validate Pre-commit Hook Configuration' read_only: false type: 'command'

Test a pre-commit hook against all repository files before committing to prevent CI failures.

## Purpose

Pre-commit hooks can fail in CI even after passing locally if they haven't been tested on all files. This command validates a hook configuration by:

1. Running the hook against all repository files
1. Detecting files that cause parse errors or failures
1. Suggesting appropriate exclusion patterns
1. Verifying the hook passes after exclusions

## Process

1. **Identify Hook to Test**

   - User specifies hook ID (e.g., `blacken-docs`, `ruff-check`)
   - Verify hook exists in `.pre-commit-config.yaml`
   - Extract current configuration

1. **Run Hook on All Files**

   - Execute: `pre-commit run <hook-id> --all-files`
   - Capture output and exit code
   - Identify any failures or errors

1. **Analyze Failures**

   - **Parse Errors**: Files with syntax issues (pseudo-code, placeholders)
   - **Format Changes**: Files that would be reformatted
   - **Lint Violations**: Code quality issues
   - **Dependency Issues**: Missing imports or tools

1. **Suggest Exclusions**

   - Analyze failed file paths
   - Identify common patterns:
     - `tasks/` - Task specification files (often have pseudo-code)
     - `.claude/commands/` - Command documentation (examples, placeholders)
     - `docs/examples/` - Documentation examples (illustrative code)
   - Generate exclusion regex pattern

1. **Apply Exclusions**

   - Show proposed `.pre-commit-config.yaml` change
   - Ask for confirmation
   - Update configuration file
   - Re-run hook to verify fix

1. **Verify Success**

   - Run hook again: `pre-commit run <hook-id> --all-files`
   - Confirm all files pass
   - Report success

## Usage

```bash
# Test a specific hook
/validate-pre-commit-hook blacken-docs

# Test with verbose output
/validate-pre-commit-hook ruff-check --verbose

# Dry run (show what would be excluded, don't modify)
/validate-pre-commit-hook pymarkdown --dry-run

# Auto-apply suggested exclusions (no confirmation)
/validate-pre-commit-hook mdformat --auto-fix
```

## Examples

### Example 1: Blacken-docs Parse Errors

```bash
# Run validation
/validate-pre-commit-hook blacken-docs

# Output:
# 🔍 Testing hook: blacken-docs
# Running: pre-commit run blacken-docs --all-files
#
# ❌ Hook failed on 21 files:
#
# Parse Errors (21 files):
#   tasks/bug-fixes/007-api-404-handling.md
#   tasks/enhancement/005-sphinx-quality-plugins.md
#   .claude/commands/implement-task.md
#   .claude/commands/create-task.md
#   ... 17 more
#
# Common pattern: Files with pseudo-code and placeholders
#
# Suggested exclusion:
#   exclude: ^(tasks/|\.claude/commands/|docs/examples/)
#
# This would exclude:
#   - tasks/ (task specifications with pseudo-code)
#   - .claude/commands/ (command docs with examples)
#   - docs/examples/ (documentation examples)
#
# Apply this exclusion? [y/N]: y
#
# ✏️  Updating .pre-commit-config.yaml...
#
# ✅ Exclusion applied. Re-testing...
# Running: pre-commit run blacken-docs --all-files
#
# ✅ All files passed!
#
# Summary:
#   Hook: blacken-docs
#   Files tested: 156
#   Files excluded: 21
#   Files passed: 135
#   Status: ✅ Ready to commit
```

### Example 2: Ruff-check Violations

```bash
# Run validation
/validate-pre-commit-hook ruff-check

# Output:
# 🔍 Testing hook: ruff-check
# Running: pre-commit run ruff-check --all-files
#
# ❌ Hook failed on 3 files:
#
# Lint Violations (3 files):
#   src/nhl_scrabble/api/nhl_client.py:142 - F401 'requests' imported but unused
#   tests/test_docs.py:33 - S603 subprocess call without shell=True
#   tests/test_docs.py:34 - S607 partial executable path
#
# Analysis:
#   - F401: Unused import (can be auto-fixed with ruff --fix)
#   - S603/S607: Security warnings on safe subprocess calls
#
# Recommendations:
#   1. Run 'ruff check --fix' to auto-fix F401
#   2. Add targeted noqa for S603/S607 (subprocess is safe here)
#   3. DO NOT exclude these files (real issues to fix)
#
# Would you like to:
#   [1] Auto-fix with 'ruff check --fix'
#   [2] Show noqa suggestions
#   [3] Exit and fix manually
#
# Choice: 2
#
# Suggested noqa additions:
#
# File: tests/test_docs.py
# Line 33-34:
#   result = subprocess.run(  # noqa: S603
#       [  # noqa: S607
#           "sphinx-build",
#           ...
#
# These subprocess calls are safe because:
#   - Command is hardcoded ("sphinx-build")
#   - Arguments are controlled (no user input)
#   - Only used in tests
#
# Apply manually or commit and let CI fail for review.
```

### Example 3: All Hooks Pass

```bash
# Run validation on well-configured hook
/validate-pre-commit-hook mypy

# Output:
# 🔍 Testing hook: mypy
# Running: pre-commit run mypy --all-files
#
# ✅ All files passed!
#
# Summary:
#   Hook: mypy
#   Files tested: 42 Python files
#   Files excluded: 0
#   Files passed: 42
#   Status: ✅ Ready to commit
```

## Common Exclusion Patterns

### Documentation Files with Examples

```yaml
# Exclude files with pseudo-code, placeholders, or illustrative examples
  - id: blacken-docs
    exclude: ^(tasks/|\.claude/commands/|docs/examples/|docs/tutorials/)
```

### Generated Files

```yaml
# Exclude auto-generated documentation
  - id: doc8
    exclude: ^docs/reference/api/ # Sphinx-generated API docs
```

### Configuration Files

```yaml
# Some hooks don't apply to config files
  - id: check-yaml
    exclude: ^\.github/ISSUE_TEMPLATE/ # YAML with frontmatter
```

### Test Files

```yaml
# Exclude test fixtures with intentionally bad code
  - id: ruff-check
    exclude: ^tests/fixtures/bad_code\.py$
```

## Hook-Specific Guidance

### Formatters (blacken-docs, mdformat, autopep8)

**Common Issues:**

- Parse errors on pseudo-code
- Placeholder text like `{variable}` or `...`
- Example code that's intentionally incomplete

**Solution:**

- Exclude documentation and example files
- Keep production code formatted

### Linters (ruff-check, flake8, pylint)

**Common Issues:**

- False positives on security checks (S603, S607)
- Complexity warnings on legitimate code (C901)
- Import issues in test files (F401)

**Solution:**

- Fix real issues first
- Add targeted noqa comments for false positives
- Avoid broad exclusions

### Type Checkers (mypy, pyright)

**Common Issues:**

- Third-party library stubs missing
- Dynamic code that can't be typed
- Test mocks confusing type checker

**Solution:**

- Install type stubs: `pip install types-*`
- Add `# type: ignore` comments sparingly
- Configure in pyproject.toml, not exclusions

### Documentation (doc8, rstcheck, pydocstyle)

**Common Issues:**

- Auto-generated docs (Sphinx API reference)
- External documentation pulled in
- Files with special formatting

**Solution:**

- Exclude generated directories
- Keep hand-written docs validated

## Pre-Flight Validation Workflow

Use this command as part of Pre-Flight Validation before pushing:

1. **Make code changes**
1. **Test locally**: `pytest`
1. **Validate each hook**: `/validate-pre-commit-hook <hook-id>`
1. **Run all hooks**: `pre-commit run --all-files`
1. **Commit changes**: `git commit`
1. **Push**: `git push`

This ensures hooks pass before CI runs, preventing failures.

## Best Practices

### When to Use

- ✅ After adding a new pre-commit hook
- ✅ After significant file reorganization
- ✅ When a hook fails in CI but passes locally
- ✅ Before pushing changes that add new file types
- ✅ When updating hook versions

### When NOT to Use

- ❌ For every single commit (too slow)
- ❌ When you know the hook already works
- ❌ For minor changes to existing files

### Exclusion Philosophy

**DO Exclude:**

- Documentation examples (pseudo-code)
- Task specifications (planning documents)
- Test fixtures (intentionally bad code)
- Generated files (build artifacts)

**DON'T Exclude:**

- Production source code
- Real test files
- Configuration files (usually)
- Documentation that should be valid

## Error Handling

### Hook Not Found

```
❌ Error: Hook 'unknown-hook' not found

Available hooks in .pre-commit-config.yaml:
  - trailing-whitespace
  - end-of-file-fixer
  - check-yaml
  - ruff-check
  - ruff-format
  - mypy
  ... 48 more

Usage: /validate-pre-commit-hook <hook-id>
```

### All Files Fail

```
❌ Error: Hook fails on ALL files

This suggests a configuration issue, not a file issue.

Recommendations:
1. Check hook configuration in .pre-commit-config.yaml
2. Verify hook dependencies are installed
3. Test hook with single file: pre-commit run <hook> --files path/to/file.py
4. Check hook version compatibility

DO NOT add broad exclusions - fix the configuration instead.
```

### Partial Failures

```
⚠️  Warning: Hook fails on 50% of files (78/156)

This is unusual. Common causes:
1. Hook recently added and project needs cleanup
2. Hook has incorrect arguments
3. File format change across repository

Recommendations:
1. Review failed files for commonality
2. Consider if this is a real issue to fix
3. Run hook with --show-diff-on-failure for details
4. Fix issues before excluding files
```

## Integration with Other Skills

### With /implement-task

```bash
# In Pre-Flight Validation step:
1. Run tests: pytest
2. Validate hooks: /validate-pre-commit-hook blacken-docs
3. Run all hooks: pre-commit run --all-files
4. Commit and push
```

### With /fix-security-finding

```bash
# After applying security fix:
1. Validate ruff-check: /validate-pre-commit-hook ruff-check
2. Ensure no new security warnings
3. Commit fix
```

### With /update-docs

```bash
# After documentation updates:
1. Validate doc8: /validate-pre-commit-hook doc8
2. Validate rstcheck: /validate-pre-commit-hook rstcheck
3. Validate mdformat: /validate-pre-commit-hook mdformat
4. Commit docs
```

## Advanced Usage

### Test Multiple Hooks

```bash
# Validate all documentation hooks
for hook in doc8 rstcheck mdformat pymarkdown; do
  /validate-pre-commit-hook $hook
done
```

### Test Hooks in CI Order

```bash
# Same order as .pre-commit-config.yaml
/validate-pre-commit-hook trailing-whitespace
/validate-pre-commit-hook end-of-file-fixer
/validate-pre-commit-hook check-yaml
# ... etc
```

### Compare Local vs CI

```bash
# Run exactly like CI does
pre-commit run --all-files --show-diff-on-failure

# Then validate specific failures
/validate-pre-commit-hook <failing-hook>
```

## Output Formats

### Standard Output

```
🔍 Testing hook: blacken-docs
Running: pre-commit run blacken-docs --all-files

❌ Failed on 21 files
✅ Exclusion suggested: ^(tasks/|\.claude/commands/)
⏭️  Apply exclusion? [y/N]
```

### Verbose Output

```
🔍 Testing hook: blacken-docs
Hook configuration:
  - id: blacken-docs
  - rev: 1.18.0
  - args: [--line-length=100]
  - files: \.(rst|md)$
  - exclude: (none)

Running: pre-commit run blacken-docs --all-files --verbose

Failed files (21):
  1. tasks/bug-fixes/007-api-404-handling.md
     Error: code block parse error Cannot parse: line 45
     Reason: Pseudo-code with ... ellipsis

  2. tasks/enhancement/005-sphinx-quality-plugins.md
     Error: code block parse error Cannot parse: line 123
     Reason: Placeholder {variable} syntax

  ... 19 more

Analysis:
  - All failures in tasks/ directory
  - Pattern: Pseudo-code and placeholders
  - Recommendation: Exclude tasks/ directory

Suggested fix:
  exclude: ^(tasks/|\.claude/commands/)

This would exclude:
  - 21 task files (planning documents)
  - 12 command files (documentation with examples)
  - Total: 33 files (21% of repository)

Apply this fix? [y/N]
```

## Safety Considerations

### Before Excluding Files

1. ✅ Verify files truly need exclusion (pseudo-code, examples)
1. ✅ Check if issue can be fixed instead of excluded
1. ✅ Use minimal exclusion pattern (don't exclude entire directories unnecessarily)
1. ✅ Document why files are excluded (comment in .pre-commit-config.yaml)

### After Excluding Files

1. ✅ Re-run hook to verify it passes
1. ✅ Run all hooks: `pre-commit run --all-files`
1. ✅ Test in clean environment: `tox -e py312`
1. ✅ Commit exclusion with explanation: `git commit -m "fix(pre-commit): Exclude pseudo-code from blacken-docs"`

## Related Commands

- `/implement-task` - Uses this in Pre-Flight Validation
- `/fix-security-finding` - Uses this to validate security fixes
- `/update-docs` - Uses this to validate documentation
- `/gh:wait-for-ci` - Shows failures this command prevents

## Notes

- **Time Saved**: 10-15 minutes per CI failure prevented
- **When to Run**: Before pushing new hooks or file types
- **Exit Codes**: 0 = success, 1 = hook failed, 2 = hook not found
- **Dry Run**: Use `--dry-run` to see suggestions without applying
- **Auto-fix**: Use `--auto-fix` to skip confirmation prompts
