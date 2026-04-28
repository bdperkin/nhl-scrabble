#!/usr/bin/env bash
# Visual regression test runner script
#
# Provides convenient commands for running visual tests and managing baselines.

set -euo pipefail

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Print usage
usage() {
    cat <<EOF
Usage: $(basename "$0") [COMMAND] [OPTIONS]

Visual regression test runner for NHL Scrabble web application.

COMMANDS:
    run                 Run all visual regression tests
    update              Update all baseline screenshots
    clean               Clean generated screenshots and diffs
    page                Run page screenshot tests only
    component           Run component screenshot tests only
    browser             Run cross-browser tests only
    help                Show this help message

OPTIONS:
    --headed            Run tests in headed mode (show browser)
    --browser NAME      Run tests on specific browser (chromium|firefox|webkit)
    --verbose           Run with verbose output
    --update-snapshots  Update baselines during test run

EXAMPLES:
    # Run all visual tests
    $(basename "$0") run

    # Update all baselines
    $(basename "$0") update

    # Run page tests only
    $(basename "$0") page

    # Run cross-browser tests in headed mode
    $(basename "$0") browser --headed

    # Run specific browser
    $(basename "$0") run --browser chromium

    # Run with verbose output
    $(basename "$0") run --verbose

EOF
}

# Check if application is running
check_app_running() {
    print_message "${BLUE}" "Checking if application is running..."
    if ! curl -s http://localhost:5000 >/dev/null; then
        print_message "${RED}" "ERROR: Application is not running on http://localhost:5000"
        print_message "${YELLOW}" "Please start the application first:"
        print_message "${YELLOW}" "  nhl-scrabble serve"
        exit 1
    fi
    print_message "${GREEN}" "✓ Application is running"
}

# Run all visual tests
run_all_tests() {
    local args=("$@")
    print_message "${BLUE}" "Running all visual regression tests..."
    cd "${SCRIPT_DIR}"
    pytest . "${args[@]}"
}

# Update all baselines
update_baselines() {
    local args=("$@")
    print_message "${YELLOW}" "⚠️  Updating all baseline screenshots..."
    print_message "${YELLOW}" "This will overwrite existing baselines!"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "${SCRIPT_DIR}"
        pytest . --update-snapshots "${args[@]}"
        print_message "${GREEN}" "✓ Baselines updated successfully"
        print_message "${YELLOW}" "Remember to review and commit the changes:"
        print_message "${YELLOW}" "  git diff qa/web/tests/visual/snapshots/"
        print_message "${YELLOW}" "  git add qa/web/tests/visual/snapshots/"
        print_message "${YELLOW}" "  git commit -m 'test(visual): Update baselines for <reason>'"
    else
        print_message "${YELLOW}" "Cancelled."
    fi
}

# Clean generated files
clean_files() {
    print_message "${BLUE}" "Cleaning generated files..."
    cd "${SCRIPT_DIR}"

    # Remove test results
    if [ -d "test-results" ]; then
        rm -rf test-results
        print_message "${GREEN}" "✓ Removed test-results/"
    fi

    # Remove pytest cache
    if [ -d ".pytest_cache" ]; then
        rm -rf .pytest_cache
        print_message "${GREEN}" "✓ Removed .pytest_cache/"
    fi

    # Remove __pycache__
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    print_message "${GREEN}" "✓ Removed __pycache__ directories"

    print_message "${GREEN}" "✓ Cleanup complete"
}

# Run page screenshot tests
run_page_tests() {
    local args=("$@")
    print_message "${BLUE}" "Running page screenshot tests..."
    cd "${SCRIPT_DIR}"
    pytest test_page_screenshots.py "${args[@]}"
}

# Run component screenshot tests
run_component_tests() {
    local args=("$@")
    print_message "${BLUE}" "Running component screenshot tests..."
    cd "${SCRIPT_DIR}"
    pytest test_component_screenshots.py "${args[@]}"
}

# Run cross-browser tests
run_browser_tests() {
    local args=("$@")
    print_message "${BLUE}" "Running cross-browser tests..."
    cd "${SCRIPT_DIR}"
    pytest test_cross_browser_visual.py "${args[@]}"
}

# Main command handling
main() {
    if [ $# -eq 0 ]; then
        usage
        exit 0
    fi

    # Check prerequisites
    check_app_running

    local command=$1
    shift

    case "${command}" in
        run)
            run_all_tests "$@"
            ;;
        update)
            update_baselines "$@"
            ;;
        clean)
            clean_files
            ;;
        page)
            run_page_tests "$@"
            ;;
        component)
            run_component_tests "$@"
            ;;
        browser)
            run_browser_tests "$@"
            ;;
        help|--help|-h)
            usage
            exit 0
            ;;
        *)
            print_message "${RED}" "ERROR: Unknown command: ${command}"
            echo
            usage
            exit 1
            ;;
    esac
}

main "$@"
