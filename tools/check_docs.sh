#!/usr/bin/env bash
# Check if generated documentation is up-to-date
# Works in both local development and CI environments

set -e  # Exit on error

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Checking generated documentation...${NC}"

# Generate API docs
echo -e "${BLUE}Generating API reference documentation...${NC}"
mkdir -p docs/reference/api
pdoc nhl_scrabble -o docs/reference/api -d markdown

# Generate CLI docs
echo -e "${BLUE}Generating CLI reference documentation...${NC}"
python tools/generate_cli_docs.py

# Check if any files were modified
if ! git diff --exit-code docs/reference/api/ docs/reference/cli-generated.md > /dev/null 2>&1; then
    echo -e "${RED}✗ Generated docs are out of date!${NC}"
    echo -e "${RED}Run 'make docs-gen' to regenerate documentation${NC}"
    echo ""
    echo "Modified files:"
    git diff --name-only docs/reference/api/ docs/reference/cli-generated.md
    exit 1
fi

echo -e "${GREEN}✓ Generated docs are up-to-date${NC}"
exit 0
