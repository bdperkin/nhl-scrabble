#!/usr/bin/env bash
# Copy and rename Scrabble tile images to web static directory
# Maps from source naming (scrabble_tiles_A1.png) to web naming (A-1.png)
#
# Purpose: Automate deployment of Scrabble tile images from source exports to web static directory.
#          Handles naming convention transformation and applies standard Scrabble point values.

set -euo pipefail

SOURCE_DIR="assets/branding/source/scrabble-tiles/png"
DEST_DIR="src/nhl_scrabble/web/static/img/scrabble-tiles"

# Scrabble point values for each letter
declare -A POINTS=(
  [A]=1 [B]=3 [C]=3 [D]=2 [E]=1 [F]=4 [G]=2 [H]=4 [I]=1 [J]=8
  [K]=5 [L]=1 [M]=3 [N]=1 [O]=1 [P]=3 [Q]=10 [R]=1 [S]=1 [T]=1
  [U]=1 [V]=4 [W]=4 [X]=8 [Y]=4 [Z]=10
)

echo "Copying Scrabble tile images..."
echo "Source: ${SOURCE_DIR}"
echo "Destination: ${DEST_DIR}"
echo ""

# Copy each letter tile (using the first variant of each letter)
for letter in {A..Z}; do
  source_file="${SOURCE_DIR}/scrabble_tiles_${letter}1.png"
  points="${POINTS[$letter]}"
  dest_file="${DEST_DIR}/${letter}-${points}.png"

  if [[ -f "$source_file" ]]; then
    cp "$source_file" "$dest_file"
    echo "  ✓ $letter -> ${letter}-${points}.png (${points} points)"
  else
    echo "  ✗ $letter: Source file not found: $source_file"
  fi
done

# Copy blank tiles if they exist
if [[ -f "${SOURCE_DIR}/scrabble_tiles_[BLANK1].png" ]]; then
  cp "${SOURCE_DIR}/scrabble_tiles_[BLANK1].png" "${DEST_DIR}/BLANK-0.png"
  echo "  ✓ BLANK -> BLANK-0.png (0 points)"
fi

echo ""
echo "Done! Copied $(ls -1 "${DEST_DIR}"/*.png 2>/dev/null | wc -l) tiles."
