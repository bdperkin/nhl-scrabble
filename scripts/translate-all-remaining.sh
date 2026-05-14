#!/usr/bin/env bash
# ============================================================================
# Translate All Remaining Locales
# ============================================================================
# Purpose: Automates translation of all remaining NHL Scrabble locales using
#          AI-assisted translation with the translate-locale.py script.
#
# Exit Codes:
#   0 - Success (all translations completed)
#   1 - Failure (translation failed and user aborted)
#
# Dependencies:
#   python3, translate-locale.py, bash 4.0+, git, gh CLI
#
# Usage: ./scripts/translate-all-remaining.sh
#
# Description:
#   Sequentially translates 7 remaining locales (ru_RU, fi_FI, cs_CZ, de_DE,
#   it_CH, sk_SK, lv_LV) using AI-assisted translation. For each locale:
#   - Generates translations from built-in database (~30-50 core terms)
#   - Compiles .mo files
#   - Updates test configuration
#   - Updates TRANSLATING.md
#   - Runs i18n tests
#   - Creates git branch, commits, pushes, and creates PR
#
#   All translations are marked as DRAFT requiring native speaker review.
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
