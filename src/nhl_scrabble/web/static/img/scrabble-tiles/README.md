# Scrabble Tile Images

This directory contains Scrabble tile images for displaying letter values in the web interface.

## File Naming Convention

Images should be named according to the letter and point value:

- `A-1.png` - Letter A, worth 1 point
- `B-3.png` - Letter B, worth 3 points
- `Z-10.png` - Letter Z, worth 10 points
- `blank.png` - Blank tile (optional)

## Expected Format

- **Format**: PNG with transparency
- **Recommended Size**: 64x64px or 128x128px (will be scaled by CSS)
- **Style**: Match standard Scrabble tile design (cream/beige background, black letter, small point value in corner)

## Letter Point Values

Standard Scrabble letter values:

- **1 point**: A, E, I, O, U, L, N, S, T, R
- **2 points**: D, G
- **3 points**: B, C, M, P
- **4 points**: F, H, V, W, Y
- **5 points**: K
- **8 points**: J, X
- **10 points**: Q, Z

## Usage in Templates

Images will be referenced in Jinja2 templates as:

```html
<img alt="Letter A worth 1 point" class="scrabble-tile" src="{{ url_for('static', filename='img/scrabble-tiles/A-1.png') }}"/>
```

## TODO

- [ ] Add all 26 letter tiles (A-Z)
- [ ] Optional: Add blank tile
- [ ] Update players.html template to use tile images in legend
- [ ] Add CSS styling for tile display
