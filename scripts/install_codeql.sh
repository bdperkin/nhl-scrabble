#!/usr/bin/env bash
#
# Install CodeQL CLI locally for development
#
# Purpose: Download and install CodeQL CLI and query packs to ~/tools directory.
#          Provides local CodeQL analysis capability without GitHub Actions.
#
# Usage: ./install_codeql.sh
#
# Exit Codes:
#   0 - Success (CodeQL CLI installed successfully)
#   1 - Error (unsupported OS, download failed, extraction failed)
#
# Dependencies:
#   - wget: Download CodeQL CLI archive
#   - unzip: Extract CodeQL CLI archive
#   - git: Clone CodeQL query pack repository
#   - Standard tools: mkdir, rm, uname
#
# Installation Location: ${HOME}/tools/codeql
#
# Post-Install: Add to PATH with: export PATH="${HOME}/tools/codeql:$PATH"

set -euo pipefail

INSTALL_DIR="${HOME}/tools"
CODEQL_VERSION="latest"

echo "📦 Installing CodeQL CLI to ${INSTALL_DIR}..."
mkdir -p "$INSTALL_DIR"

# Detect platform
OS="$(uname -s)"
case "$OS" in
  Linux*)  PLATFORM="linux64" ;;
  Darwin*) PLATFORM="osx64" ;;
  *)       echo "❌ Unsupported OS: $OS"; exit 1 ;;
esac

# Download CodeQL CLI
echo "⬇️  Downloading CodeQL CLI ($PLATFORM)..."
cd "$INSTALL_DIR"
wget -q "https://github.com/github/codeql-cli-binaries/releases/latest/download/codeql-${PLATFORM}.zip"
unzip -q "codeql-${PLATFORM}.zip"
rm "codeql-${PLATFORM}.zip"

# Download CodeQL queries
echo "⬇️  Downloading CodeQL query packs..."
if [[ ! -d "$INSTALL_DIR/codeql-repo" ]]; then
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
