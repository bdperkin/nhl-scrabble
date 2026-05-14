#!/usr/bin/env bash
# ============================================================================
# Translate All Remaining Locales
# ============================================================================
# Purpose: Automates translation of remaining NHL Scrabble locales using
#          AI-assisted translation with the translate-locale.py script.
#
# Dependencies:
#   - python3: Required for running translate-locale.py script
#   - translate-locale.py: Core translation automation script
#   - bash 4.0+: Required for array and advanced shell features
#   - git: Required for version control operations
#   - gh CLI: Required for creating pull requests
#
# Exit Codes:
#   0 - Success (all translations completed)
#   1 - Failure (translation failed and user aborted)
#
# Usage: ./scripts/translate-all-remaining.sh
#
# Status: ✅ ALL 12 SUPPORTED LOCALES NOW TRANSLATED (as of 2026-05-14)
#
# Supported Locales (12 total):
#   - North America: en_US (source), en_CA ✅, fr_CA ✅
#   - Nordic: sv_SE ✅, fi_FI ✅
#   - Central Europe: cs_CZ ✅, de_DE ✅, de_CH ✅, it_CH ✅, sk_SK ✅
#   - Eastern Europe: ru_RU ✅, lv_LV ✅
#
# This script completed: ru_RU, fi_FI, cs_CZ, de_DE, it_CH, sk_SK, lv_LV
# Manually completed earlier: en_CA, fr_CA, sv_SE, de_CH
#
# Description:
#   Sequentially translates specified locales using AI-assisted translation.
#   For each locale:
#   - Generates translations from built-in database (~30-50 core terms)
#   - Compiles .mo files
#   - Updates test configuration
#   - Updates TRANSLATING.md
#   - Runs i18n tests
#   - Creates git branch, commits, pushes, and creates PR
#
#   All translations are marked as DRAFT requiring native speaker review.
#
# Note: To translate additional locales, add them to the LOCALES array below.
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TRANSLATE_SCRIPT="$SCRIPT_DIR/translate-locale.py"

# Remaining locales to translate
LOCALES=(
  "ru_RU"
  "fi_FI"
  "cs_CZ"
  "de_DE"
  "it_CH"
  "sk_SK"
  "lv_LV"
)

echo "🌐 Translating ${#LOCALES[@]} remaining locales"
echo "============================================================"
echo ""

for locale in "${LOCALES[@]}"; do
  echo "📝 Starting $locale..."
  python3 "$TRANSLATE_SCRIPT" "$locale" || {
    echo "❌ Failed to translate $locale"
    echo "Continue with next locale? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
      exit 1
    fi
  }
  echo ""
  echo "✅ $locale complete!"
  echo "============================================================"
  echo ""
done

echo "🎉 All translations complete!"
echo ""
echo "Summary:"
for locale in "${LOCALES[@]}"; do
  echo "  ✅ $locale"
done
echo ""
echo "⚠️  IMPORTANT: All translations are AI-assisted DRAFTS"
echo "   They require review by native speakers before release"
