# Integrate Astral 'ty' Type Checker/LSP

**GitHub Issue**: #228 - https://github.com/bdperkin/nhl-scrabble/issues/228

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

2-3 hours

## Description

Supplement the existing ruff linting with Astral's 'ty' type checker/LSP across the repository. Ty is a next-generation type checker from the creators of ruff, designed for speed and accuracy. This enhancement improves type safety, developer experience, and IDE integration while leveraging the Astral ecosystem already in use (ruff, uv).

## Current State

**Existing Type Checking:**

The project currently uses MyPy for static type checking:

```toml
# pyproject.toml
[tool.mypy]
strict = true
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
# ... 20+ strict configuration options
```

**Pre-commit Hook:**

```yaml
# .pre-commit-config.yaml
- repo: https://github.com/pre-commit/mirrors-mypy
  rev: v1.13.0
  hooks:
    - id: mypy
      additional_dependencies:
        - types-requests
        - types-setuptools
```

**Tox Environment:**

```ini
# tox.ini
[testenv:mypy]
description = Run MyPy type checking
deps =
    mypy>=1.7.0
    types-requests
    types-setuptools
commands =
    mypy src/ tests/
```

**Current Workflow:**

- MyPy runs in pre-commit hooks (on staged files)
- MyPy runs in tox environments (full codebase)
- MyPy runs in CI (GitHub Actions)
- IDE integration via MyPy LSP (varies by editor)

**Pain Points:**

1. **Speed**: MyPy can be slow on large codebases
1. **Configuration Complexity**: 20+ mypy options to maintain
1. **Type Stub Management**: Manual maintenance of types-\* packages
1. **IDE Integration**: LSP can be heavyweight
1. **Ecosystem**: Not from Astral (unlike ruff, uv)

## Proposed Solution

### Astral 'ty' Type Checker

**What is 'ty'?**

- Next-generation type checker from Astral (creators of ruff, uv)
- Written in Rust for blazing speed (similar to ruff)
- Built-in Language Server Protocol (LSP)
- Designed to work seamlessly with ruff
- Part of the unified Astral Python tooling ecosystem

**Key Benefits:**

1. **Speed**: 10-100x faster than MyPy (Rust-based)
1. **Unified Ecosystem**: Same team as ruff and uv
1. **Modern Design**: Built from scratch with Python 3.10+ in mind
1. **LSP Integration**: Native language server for IDE features
1. **Simplified Config**: Fewer configuration options needed
1. **Better Error Messages**: Clear, actionable type errors

### Integration Strategy

**Option 1: Supplement MyPy (Recommended Initial Approach)**

Keep MyPy running alongside ty for validation period:

```yaml
# .pre-commit-config.yaml
- repo: https://github.com/astral-sh/ty
  rev: v0.1.0  # Example version
  hooks:
    - id: ty
      name: ty type checker

- repo: https://github.com/pre-commit/mirrors-mypy
  rev: v1.13.0
  hooks:
    - id: mypy
      name: mypy type checker (validation)
```

**Benefits:**

- Validate ty results against mypy
- Gradual migration path
- Compare performance and error quality
- No immediate disruption

**Option 2: Replace MyPy (After Validation)**

Once ty proves reliable, replace mypy completely:

```yaml
# .pre-commit-config.yaml
- repo: https://github.com/astral-sh/ty
  rev: v0.1.0
  hooks:
    - id: ty
```

**Benefits:**

- Simplified toolchain
- Faster CI/pre-commit
- Unified Astral ecosystem
- Reduced dependency count

**Option 3: Parallel with Different Scopes**

Use ty for rapid feedback, mypy for deep validation:

```yaml
# ty: Fast checks in pre-commit
- repo: https://github.com/astral-sh/ty
  rev: v0.1.0
  hooks:
    - id: ty
      stages: [commit]

# mypy: Deep validation in CI only
- repo: https://github.com/pre-commit/mirrors-mypy
  rev: v1.13.0
  hooks:
    - id: mypy
      stages: [manual]
```

### Configuration

**pyproject.toml (ty configuration):**

```toml
[tool.ty]
# Python version targeting
python-version = "3.10"

# Type checking strictness
strict = true

# Paths to check
include = ["src/", "tests/"]

# Paths to exclude
exclude = [
    "*.pyc",
    "__pycache__",
    "build/",
    "dist/",
]

# LSP settings
[tool.ty.lsp]
enabled = true
diagnostics = true
code-actions = true
```

**Pre-commit Hook:**

```yaml
# .pre-commit-config.yaml
- repo: https://github.com/astral-sh/ty
  rev: v0.1.0
  hooks:
    - id: ty
      name: ty - Astral type checker
      args: [--strict]
      types: [python]
```

**Tox Environment:**

```ini
# tox.ini
[testenv:ty]
description = Run Astral ty type checking
deps =
    ty
commands =
    ty check src/ tests/

[testenv:type-check]
description = Run all type checkers (ty + mypy validation)
deps =
    ty
    mypy>=1.7.0
    types-requests
    types-setuptools
commands =
    ty check src/ tests/
    mypy src/ tests/
```

**Makefile Targets:**

```makefile
# Add to existing Makefile
.PHONY: ty
ty:  ## Run ty type checking
	@echo "Running Astral ty type checker..."
	@tox -e ty

.PHONY: type-check
type-check:  ## Run all type checkers (ty + mypy)
	@echo "Running comprehensive type checking..."
	@tox -e type-check
```

### IDE Integration

**VS Code (settings.json):**

```json
{
  "python.languageServer": "ty",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },
  "ty.path": ["/path/to/venv/bin/ty"],
  "ty.args": ["--strict"]
}
```

**PyCharm/IntelliJ:**

- Settings → Tools → External Tools
- Add ty as external tool
- Configure file watcher for real-time checking

**Neovim (nvim-lspconfig):**

```lua
-- lua/lsp/ty.lua
local lspconfig = require('lspconfig')

lspconfig.ty.setup({
  cmd = {"ty", "lsp"},
  filetypes = {"python"},
  root_dir = lspconfig.util.root_pattern("pyproject.toml", ".git"),
  settings = {
    ty = {
      strict = true,
      pythonVersion = "3.10"
    }
  }
})
```

## Implementation Steps

1. **Research ty Current Status** (15 min)

   - Check Astral's GitHub for ty repository
   - Review documentation and examples
   - Verify ty is production-ready
   - Check Python version compatibility
   - Review community adoption

1. **Install ty Locally** (10 min)

   - Add to pyproject.toml dev dependencies:
     ```toml
     [project.optional-dependencies.dev]
     ty = ">=0.1.0"  # Latest version
     ```
   - Install: `uv pip install -e ".[dev]"`
   - Verify installation: `ty --version`
   - Test basic usage: `ty check src/`

1. **Configure ty** (20 min)

   - Create `[tool.ty]` section in pyproject.toml
   - Set strict mode: `strict = true`
   - Configure paths: `include`, `exclude`
   - Enable LSP: `[tool.ty.lsp]`
   - Test configuration: `ty check --strict src/`

1. **Add Pre-commit Hook** (15 min)

   - Add ty hook to `.pre-commit-config.yaml`
   - Position after ruff-check, before mypy
   - Configure args: `[--strict]`
   - Test hook: `pre-commit run ty --all-files`
   - Compare runtime vs mypy

1. **Add Tox Environment** (10 min)

   - Create `[testenv:ty]` in tox.ini
   - Add ty to deps
   - Configure check command
   - Test: `tox -e ty`
   - Measure execution time

1. **Run ty on Codebase** (30 min)

   - Execute: `ty check src/ tests/`
   - Review all type errors reported
   - Compare with mypy output
   - Categorize errors:
     - Real issues to fix
     - False positives
     - Differences from mypy
   - Document findings

1. **Fix Type Issues** (20 min)

   - Address any real type errors found
   - Add type ignores for false positives
   - Update type annotations if needed
   - Ensure both ty and mypy pass
   - Run tests to verify no regressions

1. **Add CI Integration** (15 min)

   - Update `.github/workflows/ci.yml`
   - Add ty check step
   - Run in parallel with mypy (validation phase)
   - Configure failure behavior
   - Test CI pipeline

1. **Update Makefile** (5 min)

   - Add `make ty` target
   - Add `make type-check` (ty + mypy)
   - Test targets locally
   - Update `make help` documentation

1. **Update Documentation** (15 min)

   - Update CONTRIBUTING.md with ty usage
   - Update CLAUDE.md with ty in toolchain
   - Document IDE setup (VS Code, PyCharm, etc.)
   - Add troubleshooting section
   - Update README badges if applicable

1. **Validation Period** (15 min)

   - Run both ty and mypy for 1-2 weeks
   - Monitor for discrepancies
   - Collect performance metrics
   - Gather team feedback
   - Decide on final integration strategy

1. **Final Decision** (10 min)

   - Evaluate: Supplement, Replace, or Parallel
   - Update configuration based on decision
   - Remove mypy if replacing
   - Document decision rationale
   - Communicate to team

## Testing Strategy

### Functional Testing

```bash
# Test 1: ty executes successfully
ty check src/ tests/
echo $?  # Should be 0 (no errors)

# Test 2: ty catches type errors
# Introduce intentional type error
# Verify ty reports it

# Test 3: ty performance
time ty check src/ tests/
time mypy src/ tests/
# Compare execution times

# Test 4: Pre-commit integration
pre-commit run ty --all-files
# Should pass on valid code

# Test 5: Tox integration
tox -e ty
# Should complete successfully

# Test 6: CI integration
# Push changes, verify CI runs ty
```

### Comparison Testing

**Create comparison script:**

```python
# scripts/compare_type_checkers.py
"""Compare ty and mypy output."""

import subprocess
import time
from pathlib import Path

def run_checker(cmd: list[str]) -> tuple[str, float]:
    """Run type checker and return output + time."""
    start = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    duration = time.time() - start
    return result.stdout + result.stderr, duration

def main():
    print("Running type checker comparison...\n")

    # Run ty
    ty_output, ty_time = run_checker(["ty", "check", "src/", "tests/"])

    # Run mypy
    mypy_output, mypy_time = run_checker(["mypy", "src/", "tests/"])

    # Results
    print(f"ty:   {ty_time:.2f}s")
    print(f"mypy: {mypy_time:.2f}s")
    print(f"Speedup: {mypy_time / ty_time:.1f}x")

    # Error comparison
    ty_errors = ty_output.count("error:")
    mypy_errors = mypy_output.count("error:")

    print(f"\nty errors:   {ty_errors}")
    print(f"mypy errors: {mypy_errors}")

if __name__ == "__main__":
    main()
```

### LSP Testing

**VS Code:**

1. Open Python file
1. Introduce type error
1. Verify red squiggle appears
1. Check error message quality
1. Test code actions (auto-fixes)

**Command Line:**

```bash
# Test LSP mode
ty lsp --stdio < test_input.json

# Verify diagnostics
# Verify hover information
# Verify code completion
```

## Acceptance Criteria

- [ ] ty installed as dev dependency in pyproject.toml
- [ ] ty configured in `[tool.ty]` section
- [ ] ty pre-commit hook added and passing
- [ ] ty tox environment created (`tox -e ty`)
- [ ] ty integrated into CI pipeline
- [ ] Makefile targets added (`make ty`, `make type-check`)
- [ ] All existing type checks still pass
- [ ] ty runs faster than mypy (measured)
- [ ] ty catches same or more type errors
- [ ] LSP integration documented for major IDEs
- [ ] Documentation updated (CONTRIBUTING.md, CLAUDE.md)
- [ ] Comparison metrics documented
- [ ] Validation period completed (if applicable)
- [ ] Final integration strategy decided and implemented

## Related Files

**Modified Files:**

- `pyproject.toml` - Add ty dependency and configuration
- `.pre-commit-config.yaml` - Add ty hook
- `tox.ini` - Add ty environment
- `.github/workflows/ci.yml` - Add ty CI check
- `Makefile` - Add ty targets
- `CONTRIBUTING.md` - Document ty usage
- `CLAUDE.md` - Update toolchain documentation
- `README.md` - Update badges if applicable

**New Files:**

- `scripts/compare_type_checkers.py` - Comparison utility
- `docs/development/TYPE_CHECKING.md` - Comprehensive type checking guide

**Potentially Modified:**

- `src/**/*.py` - Fix any new type errors discovered
- `.vscode/settings.json` - VS Code ty LSP configuration
- `.idea/` - PyCharm external tool configuration

## Dependencies

**Python Package:**

- `ty` - Astral type checker (main package)
- Python 3.10+ (already required)

**No Task Dependencies** - Standalone enhancement

**Related Tools:**

- Works alongside: ruff, uv (Astral ecosystem)
- Compares with: mypy (current type checker)

## Additional Notes

### Astral Ecosystem Benefits

**Unified Toolchain:**

The project already uses Astral tools:

- **uv**: Package management (10-100x faster)
- **ruff**: Linting and formatting (10-100x faster than flake8/black)
- **ty**: Type checking (proposed, expected 10-100x faster than mypy)

**Benefits of Ecosystem Alignment:**

1. **Consistent Performance**: All tools Rust-based, blazing fast
1. **Unified Configuration**: Similar config patterns across tools
1. **Better Integration**: Tools designed to work together
1. **Single Vendor**: Easier to get support, report issues
1. **Future Compatibility**: Coordinated updates and features

### ty vs MyPy Comparison

| Feature             | ty (Astral)       | MyPy (Python)      |
| ------------------- | ----------------- | ------------------ |
| **Language**        | Rust              | Python             |
| **Speed**           | Very Fast (Rust)  | Moderate (Python)  |
| **LSP**             | Built-in          | Separate (dmypy)   |
| **Ecosystem**       | Astral (ruff, uv) | Independent        |
| **Config**          | Simplified        | Complex (20+ opts) |
| **Type Stubs**      | Built-in (many)   | Separate packages  |
| **Error Messages**  | Modern, clear     | Detailed, verbose  |
| **Python Version**  | 3.10+ focused     | Wide support       |
| **Maturity**        | Newer             | Battle-tested      |
| **Community**       | Growing rapidly   | Large, established |
| **Strictness**      | Strict by default | Configurable       |
| **Incremental**     | Yes               | Yes                |
| **Cache**           | Automatic         | Manual config      |
| **IDE Integration** | Native LSP        | Via plugins        |
| **CI Performance**  | ~30s (typical)    | ~2min (typical)    |

### Migration Strategies

**Strategy 1: Gradual Supplement (Recommended)**

```
Week 1-2: Install ty, run alongside mypy
Week 3-4: Validate ty results, fix discrepancies
Week 5-6: Optimize ty configuration
Week 7-8: Decide: replace or keep both
```

**Strategy 2: Immediate Replacement (Aggressive)**

```
Day 1: Install ty, remove mypy
Day 2-3: Fix all ty-specific errors
Day 4-5: Update documentation
Day 6-7: Monitor for issues
```

**Strategy 3: Permanent Parallel (Conservative)**

```
Ongoing: Run both ty and mypy
ty: Fast pre-commit checks
mypy: Deep CI validation
```

### Performance Expectations

**Based on Similar Tools (ruff vs flake8):**

| Operation          | MyPy (Baseline) | ty (Expected) | Speedup    |
| ------------------ | --------------- | ------------- | ---------- |
| Full repository    | ~120s           | ~3-5s         | **24-40x** |
| Single file        | ~2s             | ~0.1s         | **20x**    |
| Pre-commit (delta) | ~10s            | ~0.5s         | **20x**    |
| CI pipeline        | ~2min           | ~5-10s        | **12-24x** |
| LSP response       | ~500ms          | ~50ms         | **10x**    |
| Incremental check  | ~5s             | ~0.5s         | **10x**    |

**CI Time Savings:**

```
Current CI (with mypy): ~12 minutes total
With ty:                ~10 minutes total (-17%)
If replace mypy:        ~8 minutes total  (-33%)
```

### Error Quality Comparison

**Example Type Error:**

```python
# Code:
def greet(name: str) -> str:
    return name + 123  # Type error

# MyPy output:
src/example.py:2: error: Unsupported operand types for + ("str" and "int")
Found 1 error in 1 file (checked 42 source files)

# ty output (expected):
src/example.py:2:12 error: Cannot add str and int
  return name + 123
             ^
Help: Did you mean to convert 123 to string? Try str(123)
```

**ty Advantages:**

- More concise
- Shows exact position
- Provides actionable suggestions
- Faster to parse visually

### IDE Setup Examples

**VS Code (Complete Setup):**

```json
{
  "python.languageServer": "ty",
  "python.analysis.typeCheckingMode": "strict",
  "ty.path": ["${workspaceFolder}/.venv/bin/ty"],
  "ty.args": ["--strict"],
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true,
      "source.fixAll": true
    },
    "editor.rulers": [100]
  },
  "editor.inlayHints.enabled": "on",
  "ty.inlayHints.variableTypes": true,
  "ty.inlayHints.functionReturnTypes": true
}
```

**PyCharm External Tool:**

```
Name: ty
Program: $ProjectFileDir$/.venv/bin/ty
Arguments: check $FilePath$
Working directory: $ProjectFileDir$
```

**Vim/Neovim (ALE):**

```vim
let g:ale_linters = {
\   'python': ['ty', 'ruff'],
\}

let g:ale_python_ty_executable = '.venv/bin/ty'
let g:ale_python_ty_options = '--strict'
```

### Troubleshooting

**ty not found:**

```bash
# Verify installation
which ty
ty --version

# Reinstall if needed
uv pip install --force-reinstall ty

# Check PATH
echo $PATH | grep .venv
```

**ty reports different errors than mypy:**

- Expected behavior - ty has different type inference
- Review each error case-by-case
- May catch real issues mypy missed
- May be more or less strict in certain areas
- Document significant discrepancies

**ty LSP not working in IDE:**

```bash
# Test LSP manually
ty lsp --version

# Check LSP logs
tail -f ~/.ty/lsp.log

# Verify IDE configuration
# Check LSP client settings
```

**ty slower than expected:**

- Check if running on network drive
- Verify ty cache is enabled
- Check file exclusion patterns
- Try: `ty check --profile` for diagnostics

### Future Enhancements

After initial integration:

- **ty-specific optimizations**: Fine-tune config for project
- **Custom type stubs**: Add project-specific stubs if needed
- **CI matrix**: Different strictness levels per environment
- **Performance monitoring**: Track type check times over time
- **Error trending**: Monitor type error counts as metric
- **Team training**: ty-specific workshops for developers

### Breaking Changes

**None (Initial Supplement Approach)**

- ty runs alongside mypy
- Both must pass
- No changes to existing workflow
- Can revert easily

**If Replacing MyPy:**

- Remove mypy from dependencies
- Remove mypy hooks
- Remove mypy tox environments
- Update CI configuration
- Update IDE configurations
- Update documentation

### Migration Notes

**First Run:**

```bash
# Install ty
uv pip install -e ".[dev]"

# Run ty for first time
ty check src/ tests/

# Compare with mypy
mypy src/ tests/

# Fix any new errors
# Update type annotations
```

**Rollback Plan:**

If ty doesn't work out:

```bash
# Remove ty from pyproject.toml
# Remove ty from .pre-commit-config.yaml
# Remove ty from tox.ini
# Remove ty from CI
# Keep mypy as-is
```

### Success Metrics

**Quantitative:**

- [ ] ty runs ≥10x faster than mypy
- [ ] CI time reduced by ≥15%
- [ ] Pre-commit faster by ≥50%
- [ ] LSP response time \<100ms
- [ ] Zero false positive rate increase
- [ ] Same or better error detection

**Qualitative:**

- [ ] Developer satisfaction improves
- [ ] Error messages more actionable
- [ ] IDE experience smoother
- [ ] Easier configuration to maintain
- [ ] Better ecosystem alignment
