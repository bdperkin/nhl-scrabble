#!/usr/bin/env bash
#
# Local CodeQL security analysis script
# Mirrors GitHub Actions CodeQL workflow for local development
#
# Purpose: Run CodeQL static security analysis locally before pushing to GitHub.
#          Catches security vulnerabilities early in development cycle.
#
# Usage: ./codeql_local.sh [OPTIONS]
#
# Arguments:
#   --fail-on-findings    Exit with code 1 if security findings detected (CI mode)
#   (no arguments)        Run analysis and display results (default mode)
#
# Exit Codes:
#   0 - Success (no findings or informational mode)
#   1 - Error (CodeQL CLI not found, analysis failed, or findings in CI mode)
#
# Dependencies:
#   - codeql: CodeQL CLI (install with: make install-codeql)
#   - python: Python interpreter for SARIF processing
#   - Standard tools: rm, mkdir
#
# Examples:
#   ./codeql_local.sh                    # Run analysis, display results
#   ./codeql_local.sh --fail-on-findings # CI mode, fail on findings
#   make codeql-check                    # Makefile wrapper with --fail-on-findings

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
python3 << PYTHON_SCRIPT
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

EXIT_CODE=$?

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📁 Full results: $RESULTS_DIR/results.sarif"
echo "🔍 View in VS Code: codeql sarif-viewer $RESULTS_DIR/results.sarif"

exit $EXIT_CODE
