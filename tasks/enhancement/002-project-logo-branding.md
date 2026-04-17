# Create Project Logo and Branding Assets

**GitHub Issue**: #89 - https://github.com/bdperkin/nhl-scrabble/issues/89

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

4-8 hours

## Description

Create a professional logo/icon/avatar for the NHL Scrabble project that combines NHL hockey imagery with Scrabble scoring concepts. The logo should be available in multiple formats and sizes for use across documentation, GitHub, social media, and other platforms.

## Current State

The project currently has no logo or branding assets:

- No logo in README.md
- No favicon for documentation site
- No social media preview images
- No GitHub social preview image
- No branding in Sphinx documentation
- Generic GitHub avatar/icon

This makes the project look less professional and harder to recognize across different platforms.

## Proposed Solution

Create a comprehensive branding package with the following components:

### 1. Source SVG Design

Create a scalable vector graphic (SVG) that combines:

- **NHL elements**: Hockey stick, puck, ice rink, or team colors
- **Scrabble elements**: Letter tiles, point values, game board
- **Design principles**:
  - Simple and recognizable at small sizes (16x16px)
  - Works in both light and dark modes
  - Professional and polished appearance
  - Memorable and unique

**Example concept ideas:**

- Hockey puck with Scrabble tiles spelling "NHL"
- Hockey stick forming the letter "S" with point values
- Ice rink surface with Scrabble tile pattern
- Combination of hockey net and Scrabble board grid

### 2. Generated Formats

From the source SVG, generate multiple formats:

**Favicons:**

```bash
# Standard favicon
16x16px - favicon-16x16.png
32x32px - favicon-32x32.png
favicon.ico - Multi-resolution ICO file

# Apple Touch Icons
180x180px - apple-touch-icon.png

# Android Chrome Icons
192x192px - android-chrome-192x192.png
512x512px - android-chrome-512x512.png
```

**Documentation/README:**

```bash
64x64px   - logo-64.png
128x128px - logo-128.png
256x256px - logo-256.png
512x512px - logo-512.png
logo.svg  - Vector version
```

**Social Media:**

```bash
# Open Graph / Twitter Card (GitHub social preview)
1200x630px - social-preview.png

# GitHub profile
400x400px - logo-square.png
```

### 3. Repository Structure

Organize branding assets in a logical structure:

```
nhl-scrabble/
├── assets/                    # NEW: Branding assets directory
│   └── branding/
│       ├── source/
│       │   └── logo.svg       # Source SVG file
│       ├── favicons/
│       │   ├── favicon-16x16.png
│       │   ├── favicon-32x32.png
│       │   ├── favicon.ico
│       │   ├── apple-touch-icon.png
│       │   ├── android-chrome-192x192.png
│       │   └── android-chrome-512x512.png
│       ├── logos/
│       │   ├── logo.svg
│       │   ├── logo-64.png
│       │   ├── logo-128.png
│       │   ├── logo-256.png
│       │   └── logo-512.png
│       └── social/
│           ├── social-preview.png
│           └── logo-square.png
├── docs/
│   └── _static/              # Sphinx static assets
│       ├── logo.svg          # Symlink or copy from assets/
│       ├── favicon.ico       # Symlink or copy from assets/
│       └── ...
├── .github/
│   └── logo.png              # For README (symlink to assets/branding/logos/logo-256.png)
└── README.md                 # Updated to include logo
```

### 4. Integration Points

**README.md:**

```markdown
<p align="center">
  <img src=".github/logo.png" alt="NHL Scrabble Logo" width="200">
</p>

# NHL Scrabble Score Analyzer
```

**docs/conf.py (Sphinx):**

```python
# HTML theme options
html_theme_options = {
    "logo": {
        "image_light": "_static/logo.svg",
        "image_dark": "_static/logo.svg",
    }
}

html_favicon = "_static/favicon.ico"
```

**docs/index.rst:**

```rst
.. image:: _static/logo.svg
   :width: 200
   :align: center
   :alt: NHL Scrabble Logo
```

**GitHub Repository Settings:**

- Upload `assets/branding/social/social-preview.png` as social preview image
- Use `assets/branding/logos/logo-square.png` for repository avatar (if applicable)

**pyproject.toml (optional):**

```toml
[project.urls]
"Logo" = "https://raw.githubusercontent.com/bdperkin/nhl-scrabble/main/assets/branding/logos/logo.svg"
```

## Implementation Steps

### Step 1: Design Logo (2-4 hours)

1. Brainstorm concepts combining NHL + Scrabble themes
1. Sketch initial ideas
1. Create SVG using design tool:
   - **Inkscape** (free, open-source)
   - **Figma** (free tier available)
   - **Adobe Illustrator** (if available)
1. Ensure design works at multiple scales
1. Test in light and dark modes
1. Save source SVG to `assets/branding/source/logo.svg`

### Step 2: Generate Formats (1 hour)

Use ImageMagick or Python to generate all required formats:

```bash
# Install dependencies
pip install Pillow cairosvg

# Create generation script
cat > scripts/generate_branding.py << 'EOF'
#!/usr/bin/env python3
"""Generate branding assets from source SVG."""
import cairosvg
from pathlib import Path
from PIL import Image
import io

SOURCE_SVG = Path("assets/branding/source/logo.svg")
FAVICONS_DIR = Path("assets/branding/favicons")
LOGOS_DIR = Path("assets/branding/logos")
SOCIAL_DIR = Path("assets/branding/social")

def generate_png(svg_path, output_path, size):
    """Generate PNG from SVG at specified size."""
    png_data = cairosvg.svg2png(url=str(svg_path), output_width=size, output_height=size)
    with open(output_path, "wb") as f:
        f.write(png_data)

def generate_ico(png_paths, output_path):
    """Generate multi-resolution ICO file."""
    images = [Image.open(p) for p in png_paths]
    images[0].save(output_path, format="ICO", sizes=[(16,16), (32,32)])

def main():
    """Generate all branding assets."""
    # Create directories
    FAVICONS_DIR.mkdir(parents=True, exist_ok=True)
    LOGOS_DIR.mkdir(parents=True, exist_ok=True)
    SOCIAL_DIR.mkdir(parents=True, exist_ok=True)

    # Favicons
    generate_png(SOURCE_SVG, FAVICONS_DIR / "favicon-16x16.png", 16)
    generate_png(SOURCE_SVG, FAVICONS_DIR / "favicon-32x32.png", 32)
    generate_png(SOURCE_SVG, FAVICONS_DIR / "apple-touch-icon.png", 180)
    generate_png(SOURCE_SVG, FAVICONS_DIR / "android-chrome-192x192.png", 192)
    generate_png(SOURCE_SVG, FAVICONS_DIR / "android-chrome-512x512.png", 512)

    # Generate ICO
    generate_ico(
        [FAVICONS_DIR / "favicon-16x16.png", FAVICONS_DIR / "favicon-32x32.png"],
        FAVICONS_DIR / "favicon.ico"
    )

    # Logos
    (LOGOS_DIR / "logo.svg").write_text(SOURCE_SVG.read_text())
    generate_png(SOURCE_SVG, LOGOS_DIR / "logo-64.png", 64)
    generate_png(SOURCE_SVG, LOGOS_DIR / "logo-128.png", 128)
    generate_png(SOURCE_SVG, LOGOS_DIR / "logo-256.png", 256)
    generate_png(SOURCE_SVG, LOGOS_DIR / "logo-512.png", 512)

    # Social media (rectangular for Open Graph)
    # Note: May need manual adjustment for 1200x630 aspect ratio
    generate_png(SOURCE_SVG, SOCIAL_DIR / "logo-square.png", 400)
    print("Note: social-preview.png (1200x630) may need manual creation")
    print("      to properly fit the rectangular aspect ratio")

    print("✅ All branding assets generated successfully!")

if __name__ == "__main__":
    main()
EOF

chmod +x scripts/generate_branding.py

# Generate all assets
python scripts/generate_branding.py
```

### Step 3: Add to Repository (30 minutes)

1. Create directory structure:

   ```bash
   mkdir -p assets/branding/{source,favicons,logos,social}
   mkdir -p scripts
   ```

1. Add logo source SVG to `assets/branding/source/logo.svg`

1. Run generation script

1. Create symlinks/copies for documentation:

   ```bash
   # Copy to Sphinx static directory
   cp assets/branding/logos/logo.svg docs/_static/
   cp assets/branding/favicons/favicon.ico docs/_static/

   # Copy to GitHub directory
   mkdir -p .github
   cp assets/branding/logos/logo-256.png .github/logo.png
   ```

### Step 4: Update Documentation (1 hour)

1. **README.md**: Add logo at top
1. **docs/conf.py**: Configure Sphinx logo and favicon
1. **docs/index.rst**: Add logo to documentation homepage
1. **CLAUDE.md**: Update project branding section
1. **CONTRIBUTING.md**: Add note about logo usage

### Step 5: Configure GitHub (30 minutes)

1. Upload `social-preview.png` to GitHub repository settings:
   - Settings → General → Social preview
1. Update repository description if needed
1. Consider adding logo to GitHub Pages deployment

### Step 6: Create Usage Guidelines (30 minutes)

Create `assets/branding/README.md`:

````markdown
# NHL Scrabble Branding Assets

## Logo Usage

The NHL Scrabble logo is available in multiple formats and sizes.

### Source Files

- **SVG**: `source/logo.svg` - Original vector source (use for new exports)

### When to Use

- **Favicons**: Website/documentation favicons
- **Logos**: README, documentation, presentations
- **Social**: Open Graph previews, social media

### Guidelines

1. **Minimum Size**: Do not display smaller than 16x16px
1. **Clear Space**: Maintain minimum padding equal to logo height/4
1. **Colors**: Do not recolor or modify the logo
1. **Distortion**: Do not stretch, skew, or rotate the logo
1. **Backgrounds**: Logo should work on both light and dark backgrounds

## Generation

To regenerate all assets from source SVG:

```bash
python scripts/generate_branding.py
````

## License

The NHL Scrabble logo is © 2026 and licensed under MIT License (same as project).

````

## Testing Strategy

### Visual Testing

1. **Favicon testing**:
   - View in browser tab (16x16px)
   - View in bookmarks bar (32x32px)
   - Test on mobile devices (Apple Touch Icon)
1. **Logo testing**:
   - View in README on GitHub (light/dark mode)
   - View in Sphinx documentation (light/dark mode)
   - Test at different sizes (64px, 128px, 256px)
1. **Social preview testing**:
   - Share repository link on Twitter/Slack to see preview
   - Check GitHub repository social preview image

### Automated Testing

Add pre-commit hook to validate branding assets exist:

```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: check-branding-assets
      name: Check branding assets exist
      entry: python -c "import sys; from pathlib import Path; assets = ['assets/branding/logos/logo.svg', 'docs/_static/logo.svg', 'docs/_static/favicon.ico', '.github/logo.png']; missing = [a for a in assets if not Path(a).exists()]; sys.exit(1) if missing else sys.exit(0)"
      language: system
      pass_filenames: false
````

## Acceptance Criteria

- [x] Source SVG logo created in `assets/branding/source/logo.svg`
- [x] All favicon formats generated (16x16, 32x32, ICO, Apple Touch, Android Chrome)
- [x] All logo PNG sizes generated (64, 128, 256, 512)
- [x] Social preview image created (1200x630)
- [x] Logo added to README.md
- [x] Logo configured in Sphinx documentation (conf.py)
- [x] Favicon configured in Sphinx documentation
- [x] Logo added to docs/index.rst
- [x] Generation script created and tested
- [x] Branding README created with usage guidelines
- [x] GitHub social preview image uploaded
- [x] Logo works in both light and dark modes
- [x] Logo is recognizable at 16x16px (favicon size)
- [x] All generated files tracked in git
- [x] CLAUDE.md updated with branding information

## Related Files

- `assets/branding/` - All branding assets (NEW)
- `scripts/generate_branding.py` - Asset generation script (NEW)
- `README.md` - Add logo
- `docs/conf.py` - Configure Sphinx logo/favicon
- `docs/index.rst` - Add logo to docs homepage
- `docs/_static/logo.svg` - Sphinx logo (copy/symlink)
- `docs/_static/favicon.ico` - Sphinx favicon (copy/symlink)
- `.github/logo.png` - GitHub README logo (copy/symlink)
- `CLAUDE.md` - Update with branding section
- `.pre-commit-config.yaml` - Optional validation hook

## Dependencies

**Design Tools (choose one):**

- Inkscape (free, recommended)
- Figma (free tier)
- Adobe Illustrator (commercial)

**Generation Tools:**

```toml
# Add to pyproject.toml [project.optional-dependencies]
branding = [
    "Pillow>=10.0.0",      # Image processing
    "cairosvg>=2.7.0",     # SVG to PNG conversion
]
```

**External Dependencies:**

- None - all assets self-contained

## Additional Notes

### Design Considerations

**Color Palette:**

- Consider NHL team colors (red, blue, black, white)
- Scrabble tile colors (beige/tan, black text)
- Ensure high contrast for accessibility
- Test grayscale version for print

**Typography:**

- If including text, use clear, readable font
- Consider monospace font to echo Scrabble tile aesthetic
- Ensure legibility at small sizes

**Symbolism:**

- Combine hockey and word game elements
- Keep it simple (will be viewed at 16x16px)
- Make it memorable and unique

### Alternative Approaches

**Option 1: Text-based logo**

```
╔════╗  NHL
║ 37 ║  Scrabble
╚════╝
```

**Option 2: Icon-only logo**

- Simple hockey puck with "37" (example score)
- Works well as favicon
- Add text version for README

**Option 3: Combination mark**

- Icon + wordmark side-by-side
- Provides flexibility for different contexts

### Future Enhancements

Once base branding is established:

1. **Animated logo** - SVG animation for documentation
1. **Dark mode variant** - Separate logo for dark backgrounds
1. **Stickers/swag** - Physical branding materials
1. **Video intro** - Animated logo for presentations
1. **ASCII art** - Terminal-friendly version

### Legal Considerations

- **NHL trademark**: Ensure logo doesn't violate NHL trademarks
- **Fair use**: This is a transformative, non-commercial project
- **Attribution**: Include proper attribution if using third-party design elements
- **License**: Logo should be MIT licensed like the project

### Performance

- **SVG file size**: Keep under 10KB for fast loading
- **PNG optimization**: Use pngcrush/optipng to reduce file sizes
- **Lazy loading**: Consider lazy-loading logos in documentation
- **CDN**: For future, consider serving from CDN

### Accessibility

- **Alt text**: Provide meaningful alt text ("NHL Scrabble Logo")
- **Contrast**: Ensure logo meets WCAG contrast requirements
- **Scalability**: SVG ensures perfect scaling for screen readers

## Implementation Notes

*To be filled during implementation:*

- Actual design chosen and rationale
- Tool(s) used for design
- Any deviations from proposed directory structure
- Challenges encountered during generation
- Actual effort vs. estimated (4-8h)
- User feedback on logo design
