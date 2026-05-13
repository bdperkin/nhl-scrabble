#!/bin/bash
# Purpose: Check that staged Python files do not exceed size limit
# Description: Pre-commit hook to enforce maximum file size for Python files
#              to maintain code modularity and prevent bloated files.
#
# Exit codes:
#   0 - All files within size limit
#   1 - One or more files exceed size limit
#
# Dependencies:
#   - git: Required for checking staged files
#   - wc: Required for calculating file sizes (standard utility)
#
# Usage: Called automatically by pre-commit hook
#
# Define limit in bytes (e.g., 50KB = 51200)
# 20KB = 20480
MAX_SIZE=20480
FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(py)$' | grep -v -E "(src/nhl_scrabble/api/nhl_client\.py|src/nhl_scrabble/analytics/formatters\.py|tests/unit/test_analytics_formatters\.py)$")

for FILE in ${FILES}; do
  if [[ -f "$FILE" ]]; then
    SIZE=$(wc -c <"$FILE")
    if [[ "$SIZE" -gt "$MAX_SIZE" ]]; then
      echo "File ${FILE} is too large (${SIZE} bytes). Limit is ${MAX_SIZE}."
      exit 1
    fi
  fi
done
