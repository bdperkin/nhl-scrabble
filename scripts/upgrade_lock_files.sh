#!/usr/bin/env bash
# ============================================================================
# Upgrade UV Lock Files
# ============================================================================
# Purpose: Upgrades all uv.lock files in the project when dependencies change.
#
# Exit Codes:
#   0 - Success (lock files upgraded or already up-to-date)
#   1 - Lock files out of date (only with --check mode)
#   2 - Error during upgrade or invalid option
#
# Dependencies:
#   uv, bash 4.0+, diff, grep, make (via pip), pip
#
# Usage: ./scripts/upgrade_lock_files.sh [--check|--upgrade|--check-outdated]
#
# Description:
#   Handles both main project and QA web app lock files atomically. Used by
#   pre-commit hooks, make targets, and GitHub Actions workflows to keep
#   dependencies current and secure.
# ============================================================================

set -euo pipefail

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Script configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Lock file locations
readonly MAIN_LOCK="${PROJECT_ROOT}/uv.lock"
readonly QA_WEB_LOCK="${PROJECT_ROOT}/qa/web/uv.lock"

# Parse command line arguments
MODE="${1:-upgrade}"

# Functions
function log_info {
  printf "${BLUE}ℹ ${NC}%s\n" "$1" >&2
}

function log_success {
  printf "${GREEN}✅ ${NC}%s\n" "$1" >&2
}

function log_warning {
  printf "${YELLOW}⚠️  ${NC}%s\n" "$1" >&2
}

function log_error {
  printf "${RED}❌ ${NC}%s\n" "$1" >&2
}

# Check if uv is installed
function check_uv_installed {
  if ! command -v uv &>/dev/null; then
    log_error "uv not found. Install with: pip install uv"
    exit 2
  fi
}

# Upgrade a single lock file
function upgrade_lock_file {
  local lock_file="$1"
  local lock_dir
  lock_dir="$(dirname "${lock_file}")"

  log_info "Upgrading: ${lock_file}"

  # Change to the directory containing the lock file
  cd "${lock_dir}"

  # Run uv lock --upgrade
  if [[ -n "${UV_VERBOSE:-}" ]]; then
    uv lock --upgrade -v
  else
    uv lock --upgrade
  fi

  log_success "Upgraded: ${lock_file}"
}

# Check if lock file is up-to-date
function check_lock_file {
  local lock_file="$1"
  local lock_dir
  lock_dir="$(dirname "${lock_file}")"

  log_info "Checking: ${lock_file}"

  # Change to the directory containing the lock file
  cd "${lock_dir}"

  # Create a backup of the current lock file
  local backup="${lock_file}.backup"
  cp "${lock_file}" "${backup}"

  # Run uv lock (no --upgrade, just verify)
  if uv lock --locked 2>/dev/null; then
    log_success "Up-to-date: ${lock_file}"
    rm -f "${backup}"
    return 0
  else
    log_warning "Out-of-date: ${lock_file}"
    # Restore the original lock file
    mv "${backup}" "${lock_file}"
    return 1
  fi
}

# Show outdated packages
function check_outdated {
  local lock_file="$1"
  local lock_dir
  lock_dir="$(dirname "${lock_file}")"

  log_info "Checking outdated packages in: ${lock_file}"

  # Change to the directory containing the lock file
  cd "${lock_dir}"

  # Use uv tree --outdated (if available) or parse uv.lock
  # This is a placeholder - uv doesn't have a built-in outdated command yet
  # We can use the upgrade preview feature
  log_info "Running upgrade preview..."

  # Create a backup
  local backup="${lock_file}.backup"
  cp "${lock_file}" "${backup}"

  # Run upgrade and capture output
  if uv lock --upgrade 2>&1; then
    # Show what changed
    if ! diff -q "${backup}" "${lock_file}" &>/dev/null; then
      log_info "Packages would be updated:"
      diff -u "${backup}" "${lock_file}" | grep "^[-+]" | grep -v "^[-+][-+][-+]" || true
    else
      log_success "All packages are up-to-date"
    fi
    # Restore the original
    mv "${backup}" "${lock_file}"
  else
    mv "${backup}" "${lock_file}"
    return 1
  fi
}

# Main function
function main {
  local exit_code=0

  check_uv_installed

  case "${MODE}" in
    --check)
      log_info "Checking lock files are up-to-date..."

      if ! check_lock_file "${MAIN_LOCK}"; then
        exit_code=1
      fi

      if ! check_lock_file "${QA_WEB_LOCK}"; then
        exit_code=1
      fi

      if [[ ${exit_code} -eq 0 ]]; then
        log_success "All lock files are up-to-date"
      else
        log_error "Some lock files are out-of-date. Run: make lock-upgrade"
        exit ${exit_code}
      fi
      ;;

    --check-outdated)
      log_info "Checking for outdated packages..."

      check_outdated "${MAIN_LOCK}" || exit_code=1
      check_outdated "${QA_WEB_LOCK}" || exit_code=1

      exit ${exit_code}
      ;;

    --upgrade|upgrade)
      log_info "Upgrading all lock files to latest compatible versions..."

      upgrade_lock_file "${MAIN_LOCK}" || exit_code=2
      upgrade_lock_file "${QA_WEB_LOCK}" || exit_code=2

      if [[ ${exit_code} -eq 0 ]]; then
        log_success "All lock files upgraded successfully"
      else
        log_error "Failed to upgrade lock files"
        exit ${exit_code}
      fi
      ;;

    *)
      log_error "Invalid option: ${MODE}"
      log_info "Usage: $0 [--check|--upgrade|--check-outdated]"
      exit 2
      ;;
  esac
}

# Run main function
main
