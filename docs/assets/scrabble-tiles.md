# Scrabble Tile Image Assets

## Overview

This document describes the Scrabble tile image asset pipeline for the NHL Scrabble Score Analyzer project, including source file management, optimization, and deployment to the web application.

## Asset Structure

```
assets/branding/source/scrabble-tiles/
├── scrabble_tiles.svg          # Source SVG (Git LFS tracked, optimized)
└── png/                        # Exported PNG tiles
    ├── scrabble_tiles_A1.png   # Letter A tile (1 point)
    ├── scrabble_tiles_B1.png   # Letter B tile (3 points)
    └── ...                     # All 26 letters + blank

src/nhl_scrabble/web/static/img/scrabble-tiles/
├── README.md                   # Naming convention and usage docs
├── A-1.png                     # Letter A tile (deployed)
├── B-3.png                     # Letter B tile (deployed)
├── ...                         # All 26 letters
└── BLANK-0.png                 # Blank tile (deployed)
```

## Git LFS Configuration

### Why Git LFS?

The source SVG file (`scrabble_tiles.svg`) is 4.7 MB after optimization. Git LFS (Large File Storage) is used to:

1. Keep the repository size manageable
1. Store large binary files efficiently
1. Track file changes without bloating git history
1. Allow fast cloning without downloading all versions of large assets

### Setup Process

Git LFS was configured for this project with the following steps:

1. **Install Git LFS** (version 3.7.1):

   ```bash
   # Already installed on system
   git lfs version
   # git-lfs/3.7.1 (GitHub; linux amd64; go 1.23.5)
   ```

1. **Initialize Git LFS in repository**:

   ```bash
   git lfs install
   # Updated Git hooks
   # Git LFS initialized.
   ```

1. **Configure tracking for Scrabble tile SVGs**:

   ```bash
   git lfs track "assets/branding/source/scrabble-tiles/*.svg"
   # Tracking "assets/branding/source/scrabble-tiles/*.svg"
   ```

   This creates/updates `.gitattributes`:

   ```
   assets/branding/source/scrabble-tiles/*.svg filter=lfs diff=lfs merge=lfs -text
   ```

### Verification

Check LFS tracking status:

```bash
git lfs ls-files
# Lists all files tracked by LFS

git lfs track
# Listing tracked patterns
#     assets/branding/source/scrabble-tiles/*.svg (.gitattributes)
```

## SVG Optimization

### Original File

- **Size**: 5,267,595 bytes (5.1 MB)
- **Format**: Inkscape SVG with editor metadata

### Optimization Process

Used `scour` tool to optimize the SVG:

```bash
scour \
  --enable-viewboxing \
  --enable-id-stripping \
  --enable-comment-stripping \
  --shorten-ids \
  --indent=none \
  -i assets/branding/source/scrabble-tiles/scrabble_tiles.svg \
  -o assets/branding/source/scrabble-tiles/scrabble_tiles.svg
```

**Optimization techniques:**

- `--enable-viewboxing`: Convert absolute positioning to viewBox
- `--enable-id-stripping`: Remove unused IDs
- `--enable-comment-stripping`: Remove XML comments
- `--shorten-ids`: Use shorter ID names
- `--indent=none`: Remove whitespace/indentation

### Results

- **Optimized Size**: 4,895,535 bytes (4.7 MB)
- **Reduction**: 372,060 bytes (7.1%)
- **Percentage of Original**: 92.9%

The SVG remains fully functional while being more efficient for version control and storage.

## PNG Export and Deployment

### Export Process

Individual tiles were exported from the source SVG using Inkscape or similar tool:

- **Format**: PNG with transparency
- **Source naming**: `scrabble_tiles_X1.png` (where X is the letter)
- **Count**: 130 files exported (26 letters × 5 variants + blank variants)

### Deployment Automation

The `scripts/copy-scrabble-tiles.sh` script automates deployment from source to web:

**Script functionality:**

1. Maps source naming (`scrabble_tiles_A1.png`) to web naming (`A-1.png`)
1. Uses letter-to-points lookup table for filenames
1. Copies first variant of each letter (26 letters)
1. Copies blank tile if available
1. Provides visual feedback of copy operations

**Usage:**

```bash
./scripts/copy-scrabble-tiles.sh
```

**Output:**

```
Copying Scrabble tile images...
Source: assets/branding/source/scrabble-tiles/png
Destination: src/nhl_scrabble/web/static/img/scrabble-tiles

  ✓ A -> A-1.png (1 points)
  ✓ B -> B-3.png (3 points)
  ...
  ✓ Z -> Z-10.png (10 points)
  ✓ BLANK -> BLANK-0.png (0 points)

Done! Copied 27 tiles.
```

### Scrabble Point Values

Standard Scrabble letter point values used for naming:

| Points | Letters                      |
| ------ | ---------------------------- |
| 1      | A, E, I, O, U, L, N, S, T, R |
| 2      | D, G                         |
| 3      | B, C, M, P                   |
| 4      | F, H, V, W, Y                |
| 5      | K                            |
| 8      | J, X                         |
| 10     | Q, Z                         |
| 0      | BLANK                        |

## Web Application Usage

### Naming Convention

Deployed tiles follow the pattern: `{LETTER}-{POINTS}.png`

Examples:

- `A-1.png` - Letter A (1 point)
- `Q-10.png` - Letter Q (10 points)
- `BLANK-0.png` - Blank tile (0 points)

### Template Usage

Reference tiles in Jinja2 templates:

```html
<img alt="Letter A worth 1 point" class="scrabble-tile" src="{{ url_for('static', filename='img/scrabble-tiles/A-1.png') }}"/>
```

### CSS Styling

Tiles can be styled consistently:

```css
.scrabble-tile {
    width: 32px;
    height: 32px;
    margin: 2px;
    display: inline-block;
}
```

## Maintenance

### Updating Source SVG

If the source SVG needs to be updated:

1. Edit `assets/branding/source/scrabble-tiles/scrabble_tiles.svg`
1. Re-optimize if file size increases significantly:
   ```bash
   scour --enable-viewboxing --enable-id-stripping \
     --enable-comment-stripping --shorten-ids --indent=none \
     -i assets/branding/source/scrabble-tiles/scrabble_tiles.svg \
     -o assets/branding/source/scrabble-tiles/scrabble_tiles.svg
   ```
1. Commit changes (Git LFS will handle the large file)

### Re-exporting Tiles

If tiles need to be re-exported:

1. Export PNGs from the source SVG to `assets/branding/source/scrabble-tiles/png/`
1. Run deployment script:
   ```bash
   ./scripts/copy-scrabble-tiles.sh
   ```
1. Commit updated PNG files in `src/nhl_scrabble/web/static/img/scrabble-tiles/`

### Adding New Tile Variants

To add additional tile designs:

1. Update source SVG with new variant
1. Export new PNGs (e.g., `scrabble_tiles_A2.png` for second variant)
1. Update `copy-scrabble-tiles.sh` if different variant needed
1. Run deployment script

## File Inventory

### Git LFS Tracked Files

- `assets/branding/source/scrabble-tiles/scrabble_tiles.svg` (4.7 MB)

### Source PNG Exports (130 files)

- `assets/branding/source/scrabble-tiles/png/scrabble_tiles_*.png`

### Deployed Web Tiles (27 files)

- A-1.png through Z-10.png (26 letter tiles)
- BLANK-0.png (1 blank tile)

## References

- Git LFS: https://git-lfs.github.com/
- Scour SVG Optimizer: https://github.com/scour-project/scour
- Scrabble Letter Distribution: https://en.wikipedia.org/wiki/Scrabble_letter_distributions
- Web tile documentation: `src/nhl_scrabble/web/static/img/scrabble-tiles/README.md`
