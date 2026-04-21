#!/usr/bin/env bash
# Task Documentation Validation Script
# Validates consistency between tasks/README.md, tasks/IMPLEMENTATION_SEQUENCE.md,
# and tasks/TOOLING_ANALYSIS.md
#
# Usage: ./tasks/scripts/validate-task-docs.sh

set -e

echo "=========================================="
echo "  Task Documentation Validation Script"
echo "=========================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track validation failures
FAILURES=0

# Count actual task files on filesystem
echo "📊 Counting task files on filesystem..."
echo ""

ACTIVE_BUG_FIXES=$(find tasks/bug-fixes -maxdepth 1 -name "[0-9]*.md" 2>/dev/null | wc -l || echo 0)
ACTIVE_SECURITY=$(find tasks/security -maxdepth 1 -name "[0-9]*.md" 2>/dev/null | wc -l || echo 0)
ACTIVE_OPTIMIZATION=$(find tasks/optimization -maxdepth 1 -name "[0-9]*.md" 2>/dev/null | wc -l || echo 0)
ACTIVE_ENHANCEMENT=$(find tasks/enhancement -maxdepth 1 -name "[0-9]*.md" 2>/dev/null | wc -l || echo 0)
ACTIVE_TESTING=$(find tasks/testing -maxdepth 1 -name "[0-9]*.md" 2>/dev/null | wc -l || echo 0)
ACTIVE_NEW_FEATURES=$(find tasks/new-features -maxdepth 1 -name "[0-9]*.md" 2>/dev/null | wc -l || echo 0)
ACTIVE_REFACTORING=$(find tasks/refactoring -maxdepth 1 -name "[0-9]*.md" 2>/dev/null | wc -l || echo 0)

ACTIVE_FILES=$((ACTIVE_BUG_FIXES + ACTIVE_SECURITY + ACTIVE_OPTIMIZATION + ACTIVE_ENHANCEMENT + ACTIVE_TESTING + ACTIVE_NEW_FEATURES + ACTIVE_REFACTORING))
COMPLETED_FILES=$(find tasks/completed -name "[0-9]*.md" 2>/dev/null | wc -l || echo 0)
TOTAL_FILES=$((ACTIVE_FILES + COMPLETED_FILES))

echo "Filesystem Counts:"
echo "  Active Tasks:"
echo "    - bug-fixes: $ACTIVE_BUG_FIXES"
echo "    - security: $ACTIVE_SECURITY"
echo "    - optimization: $ACTIVE_OPTIMIZATION"
echo "    - enhancement: $ACTIVE_ENHANCEMENT"
echo "    - testing: $ACTIVE_TESTING"
echo "    - new-features: $ACTIVE_NEW_FEATURES"
echo "    - refactoring: $ACTIVE_REFACTORING"
echo "    - TOTAL: $ACTIVE_FILES"
echo "  Completed: $COMPLETED_FILES"
echo "  Grand Total: $TOTAL_FILES"
echo ""

# Extract counts from README.md
echo "📖 Reading tasks/README.md..."
echo ""

# Extract active and completed counts from "Total Tasks" line
README_TOTAL_LINE=$(grep "^\*\*Total Tasks\*\*:" tasks/README.md | head -1)
README_TOTAL=$(echo "$README_TOTAL_LINE" | grep -oP '\d+(?= tasks)' | head -1)
README_ACTIVE=$(echo "$README_TOTAL_LINE" | grep -oP '\d+(?= active)' | head -1)
README_COMPLETED=$(echo "$README_TOTAL_LINE" | grep -oP '\d+(?= completed)' | head -1)

echo "README.md Totals:"
echo "  Total: $README_TOTAL"
echo "  Active: $README_ACTIVE"
echo "  Completed: $README_COMPLETED"
echo ""

# Extract count from IMPLEMENTATION_SEQUENCE.md if it exists
if [ -f "tasks/IMPLEMENTATION_SEQUENCE.md" ]; then
    echo "📋 Reading tasks/IMPLEMENTATION_SEQUENCE.md..."
    echo ""

    SEQ_TOTAL_LINE=$(grep "^\*\*Total Tasks\*\*:" tasks/IMPLEMENTATION_SEQUENCE.md | head -1)
    if [ -n "$SEQ_TOTAL_LINE" ]; then
        SEQ_ACTIVE=$(echo "$SEQ_TOTAL_LINE" | grep -oP '\d+(?= active)' | head -1)
        echo "IMPLEMENTATION_SEQUENCE.md:"
        echo "  Active: $SEQ_ACTIVE"
        echo ""
    else
        echo "⚠️  Could not find '**Total Tasks**:' in IMPLEMENTATION_SEQUENCE.md"
        echo ""
    fi
else
    echo "⚠️  tasks/IMPLEMENTATION_SEQUENCE.md not found"
    echo ""
    SEQ_ACTIVE=""
fi

# Validation checks
echo "=========================================="
echo "  Validation Results"
echo "=========================================="
echo ""

# Check 1: Active tasks match between filesystem and README.md
echo "Check 1: Active tasks (Filesystem vs README.md)"
if [ "$ACTIVE_FILES" -eq "$README_ACTIVE" ]; then
    echo -e "  ${GREEN}✅ PASS${NC}: Active count matches ($ACTIVE_FILES)"
else
    echo -e "  ${RED}❌ FAIL${NC}: Mismatch detected!"
    echo "    - Filesystem: $ACTIVE_FILES"
    echo "    - README.md: $README_ACTIVE"
    echo "    - Difference: $((README_ACTIVE - ACTIVE_FILES))"
    FAILURES=$((FAILURES + 1))
fi
echo ""

# Check 2: Completed tasks match
echo "Check 2: Completed tasks (Filesystem vs README.md)"
if [ "$COMPLETED_FILES" -eq "$README_COMPLETED" ]; then
    echo -e "  ${GREEN}✅ PASS${NC}: Completed count matches ($COMPLETED_FILES)"
else
    echo -e "  ${RED}❌ FAIL${NC}: Mismatch detected!"
    echo "    - Filesystem: $COMPLETED_FILES"
    echo "    - README.md: $README_COMPLETED"
    echo "    - Difference: $((README_COMPLETED - COMPLETED_FILES))"
    FAILURES=$((FAILURES + 1))
fi
echo ""

# Check 3: Total matches
echo "Check 3: Total tasks (Filesystem vs README.md)"
if [ "$TOTAL_FILES" -eq "$README_TOTAL" ]; then
    echo -e "  ${GREEN}✅ PASS${NC}: Total count matches ($TOTAL_FILES)"
else
    echo -e "  ${RED}❌ FAIL${NC}: Mismatch detected!"
    echo "    - Filesystem: $TOTAL_FILES"
    echo "    - README.md: $README_TOTAL"
    echo "    - Difference: $((README_TOTAL - TOTAL_FILES))"
    FAILURES=$((FAILURES + 1))
fi
echo ""

# Check 4: IMPLEMENTATION_SEQUENCE.md matches README.md
if [ -n "$SEQ_ACTIVE" ]; then
    echo "Check 4: Active tasks (IMPLEMENTATION_SEQUENCE.md vs README.md)"
    if [ "$SEQ_ACTIVE" -eq "$README_ACTIVE" ]; then
        echo -e "  ${GREEN}✅ PASS${NC}: Active count matches ($SEQ_ACTIVE)"
    else
        echo -e "  ${RED}❌ FAIL${NC}: Mismatch detected!"
        echo "    - IMPLEMENTATION_SEQUENCE.md: $SEQ_ACTIVE"
        echo "    - README.md: $README_ACTIVE"
        echo "    - Difference: $((README_ACTIVE - SEQ_ACTIVE))"
        FAILURES=$((FAILURES + 1))
    fi
    echo ""
fi

# Check 5: IMPLEMENTATION_SEQUENCE.md matches filesystem
if [ -n "$SEQ_ACTIVE" ]; then
    echo "Check 5: Active tasks (IMPLEMENTATION_SEQUENCE.md vs Filesystem)"
    if [ "$SEQ_ACTIVE" -eq "$ACTIVE_FILES" ]; then
        echo -e "  ${GREEN}✅ PASS${NC}: Active count matches ($SEQ_ACTIVE)"
    else
        echo -e "  ${RED}❌ FAIL${NC}: Mismatch detected!"
        echo "    - IMPLEMENTATION_SEQUENCE.md: $SEQ_ACTIVE"
        echo "    - Filesystem: $ACTIVE_FILES"
        echo "    - Difference: $((ACTIVE_FILES - SEQ_ACTIVE))"
        FAILURES=$((FAILURES + 1))
    fi
    echo ""
fi

# Summary
echo "=========================================="
echo "  Summary"
echo "=========================================="
echo ""

if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}✅ All validation checks passed!${NC}"
    echo ""
    echo "Task documentation is consistent across all files."
    exit 0
else
    echo -e "${RED}❌ $FAILURES validation check(s) failed!${NC}"
    echo ""
    echo "Task documentation has inconsistencies that need to be fixed."
    echo ""
    echo "Recommendations:"
    echo "1. Update README.md with accurate task counts from filesystem"
    echo "2. Update IMPLEMENTATION_SEQUENCE.md to match README.md"
    echo "3. Remove completed tasks from active task lists"
    echo "4. Add any missing new tasks"
    echo "5. Re-run this script to verify fixes"
    exit 1
fi
