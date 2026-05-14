#!/usr/bin/env bash
# Complete all remaining translations in sequence
# Each translation will create its own branch and PR

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
