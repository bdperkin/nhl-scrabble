# Add Local CodeQL Scanning Integration

**GitHub Issue**: [#389](https://github.com/bdperkin/nhl-scrabble/issues/389)

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

4-6 hours

## Description

Enable developers to run CodeQL security scanning locally before pushing code to GitHub. Currently, CodeQL only runs in GitHub Actions (weekly + on PRs), which means security issues are discovered late in the development cycle. Running CodeQL locally allows developers to catch and fix security vulnerabilities before committing code.

## Current State

**CodeQL in GitHub Actions:**

- Runs weekly on Monday at 6 AM UTC via scheduled workflow
- Runs on all pushes to main and pull requests
- Uses `security-and-quality` query suite
- Custom configuration in `.github/codeql/codeql-config.yml`
- Suppresses known false positives (Protocol docstrings, pytest unreachable code)

**Current workflow** (`.github/workflows/codeql.yml`):

```yaml
- name: Initialize CodeQL
  uses: github/codeql-action/init@v4
  with:
    languages: python
    queries: security-and-quality
    config-file: ./.github/codeql/codeql-config.yml

- name: Autobuild
  uses: github/codeql-action/autobuild@v4

- name: Perform CodeQL Analysis
  uses: github/codeql-action/analyze@v4
```

**No local CodeQL capability:**

- Developers cannot run CodeQL before pushing
- Security feedback only after CI runs (10-15 minute delay)
- No integration with pre-commit, tox, or make
- Must wait for GitHub Actions to detect issues

## Proposed Solution

Add local CodeQL scanning using the CodeQL CLI with integration into existing development workflows.

### 1. CodeQL CLI Installation

**Option A: System-wide installation** (recommended for active development):

```bash
# Download CodeQL CLI bundle
wget https://github.com/github/codeql-cli-binaries/releases/latest/download/codeql-linux64.zip
unzip codeql-linux64.zip -d ~/tools/
export PATH="$HOME/tools/codeql:$PATH"

# Download Python CodeQL queries
git clone https://github.com/github/codeql ~/tools/codeql-repo
```

**Option B: Project-local installation** (for consistency across team):

```bash
# Install via Makefile target
make install-codeql

# Installs to .codeql/ directory in project root
# Adds to .gitignore
```

### 2. Pre-commit Hook (Manual Run)

Add CodeQL as a **manual** pre-commit hook (not auto-run due to performance):

**.pre-commit-config.yaml**:

```yaml
# Security scanning hooks (manual run only - performance intensive)
- repo: local
  hooks:
    - id: codeql-analyze
      name: CodeQL Security Analysis
      entry: bash -c 'make codeql-check'
      language: system
      pass_filenames: false
      stages: [manual]  # Only run when explicitly requested
      verbose: true
```

**Usage**:

```bash
# Run CodeQL manually via pre-commit
pre-commit run codeql-analyze --hook-stage manual

# Or via make
make codeql-check
```

### 3. Tox Environment

Add dedicated tox environment for CodeQL analysis:

**tox.ini**:

```ini
[testenv:codeql]
description = Run CodeQL security analysis locally
skip_install = true
allowlist_externals =
    codeql
    bash
commands =
    bash -c 'if ! command -v codeql &> /dev/null; then echo "CodeQL CLI not installed. Run: make install-codeql"; exit 1; fi'
    bash scripts/codeql_local.sh {posargs}

[testenv:codeql-check]
description = Run CodeQL and fail on findings (CI mode)
skip_install = true
allowlist_externals =
    codeql
    bash
commands =
    bash -c 'if ! command -v codeql &> /dev/null; then echo "CodeQL CLI not installed"; exit 1; fi'
    bash scripts/codeql_local.sh --fail-on-findings {posargs}
```

**Usage**:

```bash
tox -e codeql              # Run analysis, show results
tox -e codeql-check        # Run analysis, fail if findings
```

### 4. Makefile Targets

Add comprehensive Makefile targets:

**Makefile**:

```makefile
# CodeQL Security Scanning
.PHONY: codeql codeql-check codeql-clean install-codeql

codeql: ## Run CodeQL security analysis locally
	@echo "Running CodeQL security analysis..."
	@bash scripts/codeql_local.sh

codeql-check: ## Run CodeQL and fail on security findings (CI mode)
	@echo "Running CodeQL security analysis (strict mode)..."
	@bash scripts/codeql_local.sh --fail-on-findings

codeql-clean: ## Clean CodeQL database and results
	@echo "Cleaning CodeQL database and results..."
	@rm -rf .codeql-db/ .codeql-results/
	@echo "✅ CodeQL artifacts cleaned"

install-codeql: ## Install CodeQL CLI locally (Linux/macOS)
	@bash scripts/install_codeql.sh
```

### 5. CodeQL Analysis Script

**scripts/codeql_local.sh**:

```bash
#!/usr/bin/env bash
# Local CodeQL security analysis script
# Mirrors GitHub Actions CodeQL workflow for local development

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CODEQL_DB="$PROJECT_ROOT/.codeql-db"
RESULTS_DIR="$PROJECT_ROOT/.codeql-results"
CONFIG_FILE="$PROJECT_ROOT/.github/codeql/codeql-config.yml"

# Parse arguments
FAIL_ON_FINDINGS=false
if [[ "${1:-}" == "--fail-on-findings" ]]; then
    FAIL_ON_FINDINGS=true
fi

# Check CodeQL CLI is installed
if ! command -v codeql &> /dev/null; then
    echo "❌ CodeQL CLI not found"
    echo "Install with: make install-codeql"
    echo "Or download from: https://github.com/github/codeql-cli-binaries/releases"
    exit 1
fi

# Clean previous results
echo "🧹 Cleaning previous CodeQL database..."
rm -rf "$CODEQL_DB" "$RESULTS_DIR"
mkdir -p "$RESULTS_DIR"

# Create CodeQL database
echo "📦 Creating CodeQL database for Python..."
codeql database create "$CODEQL_DB" \
    --language=python \
    --source-root="$PROJECT_ROOT" \
    --overwrite

# Run CodeQL analysis with security-and-quality suite
echo "🔍 Running CodeQL security analysis..."
codeql database analyze "$CODEQL_DB" \
    --format=sarif-latest \
    --output="$RESULTS_DIR/results.sarif" \
    --sarif-category=python \
    --sarif-add-query-help \
    --threads=0 \
    -- security-and-quality

# Convert SARIF to human-readable format
echo ""
echo "📊 CodeQL Analysis Results:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Parse SARIF results and display
python3 << 'PYTHON_SCRIPT'
import json
import sys
from pathlib import Path

sarif_file = Path("$RESULTS_DIR/results.sarif")
if not sarif_file.exists():
    print("❌ No results file found")
    sys.exit(1)

with open(sarif_file) as f:
    sarif = json.load(f)

results = sarif.get("runs", [{}])[0].get("results", [])

if not results:
    print("✅ No security findings detected!")
    sys.exit(0)

print(f"⚠️  Found {len(results)} security finding(s):\n")

for i, result in enumerate(results, 1):
    rule_id = result.get("ruleId", "unknown")
    level = result.get("level", "note").upper()
    message = result.get("message", {}).get("text", "No description")

    locations = result.get("locations", [])
    if locations:
        loc = locations[0].get("physicalLocation", {})
        file_path = loc.get("artifactLocation", {}).get("uri", "unknown")
        region = loc.get("region", {})
        line = region.get("startLine", "?")

        print(f"{i}. [{level}] {rule_id}")
        print(f"   File: {file_path}:{line}")
        print(f"   {message}\n")

if "$FAIL_ON_FINDINGS" == "true":
    print("❌ CodeQL found security issues (failing build)")
    sys.exit(1)
else:
    print(f"⚠️  Review and fix {len(results)} finding(s)")
    sys.exit(0)
PYTHON_SCRIPT

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📁 Full results: $RESULTS_DIR/results.sarif"
echo "🔍 View in VS Code: codeql sarif-viewer $RESULTS_DIR/results.sarif"
```

### 6. CodeQL Installation Script

**scripts/install_codeql.sh**:

```bash
#!/usr/bin/env bash
# Install CodeQL CLI locally for development
set -euo pipefail

INSTALL_DIR="${HOME}/tools"
CODEQL_VERSION="latest"

echo "📦 Installing CodeQL CLI to ${INSTALL_DIR}..."
mkdir -p "$INSTALL_DIR"

# Detect platform
OS="$(uname -s)"
case "$OS" in
    Linux*)  PLATFORM="linux64";;
    Darwin*) PLATFORM="osx64";;
    *)       echo "❌ Unsupported OS: $OS"; exit 1;;
esac

# Download CodeQL CLI
echo "⬇️  Downloading CodeQL CLI ($PLATFORM)..."
cd "$INSTALL_DIR"
wget -q "https://github.com/github/codeql-cli-binaries/releases/latest/download/codeql-${PLATFORM}.zip"
unzip -q "codeql-${PLATFORM}.zip"
rm "codeql-${PLATFORM}.zip"

# Download CodeQL queries
echo "⬇️  Downloading CodeQL query packs..."
if [ ! -d "$INSTALL_DIR/codeql-repo" ]; then
    git clone --depth 1 https://github.com/github/codeql.git "$INSTALL_DIR/codeql-repo"
fi

# Add to PATH instructions
echo ""
echo "✅ CodeQL CLI installed to: $INSTALL_DIR/codeql"
echo ""
echo "Add to your PATH by running:"
echo "  export PATH=\"$INSTALL_DIR/codeql:\$PATH\""
echo ""
echo "Or add to ~/.bashrc or ~/.zshrc:"
echo "  echo 'export PATH=\"$INSTALL_DIR/codeql:\$PATH\"' >> ~/.bashrc"
```

## Implementation Steps

1. **Create CodeQL analysis script** (`scripts/codeql_local.sh`)
   - Database creation logic
   - Analysis execution
   - SARIF result parsing
   - Human-readable output formatting

2. **Create CodeQL installation script** (`scripts/install_codeql.sh`)
   - Platform detection (Linux/macOS)
   - Download CodeQL CLI
   - Download query packs
   - PATH setup instructions

3. **Add Makefile targets**
   - `make codeql` - Run analysis
   - `make codeql-check` - Run with fail-on-findings
   - `make codeql-clean` - Clean artifacts
   - `make install-codeql` - Install CLI

4. **Add tox environments**
   - `tox -e codeql` - Run analysis
   - `tox -e codeql-check` - CI mode

5. **Add pre-commit hook** (manual stage)
   - Integrate with existing hooks
   - Document usage

6. **Update .gitignore**
   - Exclude `.codeql-db/`
   - Exclude `.codeql-results/`

7. **Update CONTRIBUTING.md**
   - Document CodeQL installation
   - Document usage (make, tox, pre-commit)
   - Add to development workflow

8. **Update Makefile help**
   - Add CodeQL targets to help output
   - Update security scanning section

## Testing Strategy

### Functional Testing

1. **Installation verification**:
   ```bash
   make install-codeql
   codeql version
   ```

2. **Database creation**:
   ```bash
   make codeql
   # Should create .codeql-db/ directory
   ```

3. **Analysis execution**:
   ```bash
   make codeql
   # Should complete without errors
   # Should match GitHub Actions results
   ```

4. **Result parsing**:
   ```bash
   make codeql-check
   # Should display human-readable findings
   # Should fail if findings exist (or pass if none)
   ```

5. **Tox integration**:
   ```bash
   tox -e codeql
   # Should run analysis via tox
   ```

6. **Pre-commit integration**:
   ```bash
   pre-commit run codeql-analyze --hook-stage manual
   # Should run analysis via pre-commit
   ```

### Validation Testing

1. **Introduce known vulnerability**:
   ```python
   # In test file
   exec(user_input)  # Should be flagged by CodeQL
   ```

2. **Run local analysis**:
   ```bash
   make codeql-check
   # Should detect and report vulnerability
   ```

3. **Compare with GitHub Actions**:
   - Push code with vulnerability
   - Compare local results vs GitHub Actions results
   - Verify findings match

4. **Performance testing**:
   - Measure analysis time (should be < 2 minutes for codebase)
   - Compare with GitHub Actions timing

## Acceptance Criteria

- [ ] CodeQL CLI installation script works on Linux and macOS
- [ ] `make codeql` runs full CodeQL analysis locally
- [ ] `make codeql-check` fails build if security findings exist
- [ ] `make codeql-clean` removes all CodeQL artifacts
- [ ] `make install-codeql` installs CodeQL CLI to ~/tools/
- [ ] `tox -e codeql` runs CodeQL analysis
- [ ] `tox -e codeql-check` runs in strict CI mode
- [ ] Pre-commit hook available for manual execution
- [ ] Results displayed in human-readable format
- [ ] SARIF results saved to `.codeql-results/results.sarif`
- [ ] Local results match GitHub Actions CodeQL results
- [ ] `.codeql-db/` and `.codeql-results/` added to .gitignore
- [ ] CONTRIBUTING.md documents CodeQL usage
- [ ] Makefile help includes CodeQL targets
- [ ] Analysis completes in < 2 minutes
- [ ] Uses same config as GitHub Actions (`.github/codeql/codeql-config.yml`)
- [ ] Respects query filters for false positives
- [ ] All tests pass
- [ ] Documentation updated

## Related Files

- `.github/workflows/codeql.yml` - Current GitHub Actions workflow
- `.github/codeql/codeql-config.yml` - CodeQL configuration
- `Makefile` - Add CodeQL targets
- `tox.ini` - Add CodeQL environments
- `.pre-commit-config.yaml` - Add CodeQL hook
- `.gitignore` - Add CodeQL artifacts
- `CONTRIBUTING.md` - Document CodeQL usage
- `scripts/codeql_local.sh` - Analysis script (new)
- `scripts/install_codeql.sh` - Installation script (new)

## Dependencies

**Required:**
- CodeQL CLI (installed via `make install-codeql`)
- Git (for cloning query packs)
- Python 3.12+ (for result parsing)
- Bash (for scripts)

**Optional:**
- VS Code with CodeQL extension (for SARIF viewing)

**No additional Python packages required** - uses stdlib only

## Additional Notes

### Performance Considerations

- **Analysis time**: ~1-2 minutes for nhl-scrabble codebase
- **Database size**: ~50-100 MB
- **Not suitable for auto-run**: Too slow for every commit
- **Manual hook stage**: Only run when needed

### Why Manual Pre-commit Hook?

CodeQL analysis is **too slow** for automatic pre-commit execution:

- Database creation: 30-60 seconds
- Query execution: 30-90 seconds
- Total: 1-2 minutes per run

**Instead**: Run manually before pushing:

```bash
# Before pushing important changes
pre-commit run codeql-analyze --hook-stage manual

# Or via make
make codeql-check
```

### CI Integration

**Not recommended** to add to CI:

- GitHub Actions already runs CodeQL (free for public repos)
- Local CodeQL is for **developer feedback**, not CI enforcement
- CI should continue using GitHub's CodeQL action (optimized, cached)

### Security Benefits

1. **Earlier detection**: Catch vulnerabilities before pushing
2. **Faster feedback**: No waiting for CI (1-2 min local vs 10-15 min CI)
3. **Offline development**: Run security scans without internet
4. **Learning tool**: See exactly what CodeQL detects
5. **Pre-PR validation**: Ensure clean CodeQL scan before opening PR

### Limitations

- Requires CodeQL CLI installation (~200 MB)
- Analysis is slower than other linters
- SARIF output is verbose (need parsing)
- Not all CodeQL features available locally (some GitHub-specific)

### Alternative: CodeQL in VS Code

For real-time security feedback, consider **CodeQL VS Code extension**:

```bash
# Install extension
code --install-extension GitHub.vscode-codeql

# Provides inline security warnings as you code
# More developer-friendly than CLI for active development
```

**Recommendation**: Use both:
- **VS Code extension**: Real-time feedback while coding
- **Local CLI**: Pre-push validation via `make codeql-check`

### Configuration Sync

The local analysis uses the **same configuration** as GitHub Actions:

- `.github/codeql/codeql-config.yml` for query filters
- `security-and-quality` query suite
- Same Python version and dependencies
- Same false positive suppressions

This ensures **consistent results** between local and CI scanning.

## Implementation Notes

*To be filled during implementation:*
- Actual approach taken
- Challenges encountered
- Deviations from plan
- Actual effort vs estimated
- Performance measurements
- Comparison with GitHub Actions results
