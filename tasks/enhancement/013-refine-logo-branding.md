# Refine Project Logo Tiles and Hockey Stick Overlap

**GitHub Issue**: #227 - https://github.com/bdperkin/nhl-scrabble/issues/227

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

1-2 hours

## Description

Refine the visual design of the project logo by improving the tile layout and hockey stick overlap, then regenerate all branding assets using the automated generation script. This enhances the professional appearance of the project's visual identity across documentation, README, and other materials.

## Current State

**Existing Branding Assets:**

The project has branding assets including:

- Project logo with hockey stick and NHL theme
- Logo tiles/components
- Hockey stick graphic element
- Generation script: `scripts/generate_branding.py`

**Current Issues:**

1. **Logo Tiles**: Tile arrangement or sizing may need visual refinement
1. **Hockey Stick Overlap**: Hockey stick element overlap with other logo components needs adjustment
1. **Visual Cohesion**: Overall logo composition could be more polished

**Current Branding Structure:**

```
project/
├── docs/
│   └── _static/
│       └── logo.png          # Project logo
├── scripts/
│   └── generate_branding.py  # Branding generation script
└── assets/                    # (if exists) Source design files
    ├── logo_tiles/
    └── hockey_stick/
```

## Proposed Solution

### Design Refinements

**1. Logo Tiles Refinement:**

- Adjust tile spacing for better visual balance
- Ensure consistent sizing across all tile elements
- Optimize tile colors for contrast and readability
- Align tiles with overall logo composition

**2. Hockey Stick Overlap Refinement:**

- Adjust hockey stick positioning relative to other elements
- Ensure overlap doesn't obscure important logo details
- Create smooth visual integration with background
- Maintain NHL/hockey theme while improving clarity

**3. Overall Composition:**

- Ensure logo works at multiple sizes (favicon, README banner, docs)
- Maintain consistency across all generated variants
- Verify logo readability on light and dark backgrounds

### Generation Workflow

**scripts/generate_branding.py:**

```python
#!/usr/bin/env python3
"""Generate all project branding assets from source designs.

This script automates the creation of various logo formats and sizes
for use across documentation, README, favicons, and other materials.

Usage:
    python scripts/generate_branding.py

Outputs:
    - docs/_static/logo.png (main documentation logo)
    - docs/_static/favicon.ico (website favicon)
    - README_banner.png (README header image)
    - logo_variants/ (multiple sizes and formats)
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw

def refine_logo_tiles():
    """Refine logo tile positioning and sizing."""
    # Load tile components
    # Apply spacing adjustments
    # Ensure consistent sizing
    # Return refined tile composition
    pass

def refine_hockey_stick_overlap():
    """Adjust hockey stick overlap with other elements."""
    # Load hockey stick graphic
    # Adjust positioning
    # Blend with background/tiles
    # Return refined composition
    pass

def generate_logo_variants(base_logo):
    """Generate logo in multiple sizes and formats."""
    sizes = {
        'favicon': (32, 32),
        'small': (128, 128),
        'medium': (256, 256),
        'large': (512, 512),
        'banner': (1200, 400),
    }

    variants = {}
    for name, size in sizes.items():
        resized = base_logo.resize(size, Image.Resampling.LANCZOS)
        variants[name] = resized

    return variants

def save_branding_assets(variants):
    """Save all branding assets to appropriate locations."""
    output_paths = {
        'favicon': 'docs/_static/favicon.ico',
        'logo': 'docs/_static/logo.png',
        'banner': 'README_banner.png',
    }

    for name, path in output_paths.items():
        if name in variants:
            variants[name].save(path)

def main():
    """Main branding generation workflow."""
    print("🎨 Refining logo tiles...")
    tiles = refine_logo_tiles()

    print("🏒 Refining hockey stick overlap...")
    logo = refine_hockey_stick_overlap()

    print("📐 Generating logo variants...")
    variants = generate_logo_variants(logo)

    print("💾 Saving branding assets...")
    save_branding_assets(variants)

    print("✅ Branding generation complete!")
    print("\nGenerated assets:")
    print("  - docs/_static/logo.png")
    print("  - docs/_static/favicon.ico")
    print("  - README_banner.png")

if __name__ == "__main__":
    main()
```

## Implementation Steps

1. **Review Current Logo** (15 min)

   - Open existing logo assets
   - Identify specific tile spacing/sizing issues
   - Note hockey stick overlap problems
   - Document desired improvements

1. **Refine Logo Tiles** (20 min)

   - Adjust tile positioning in design software or code
   - Ensure consistent spacing and alignment
   - Optimize colors for better contrast
   - Test at multiple sizes

1. **Refine Hockey Stick Overlap** (20 min)

   - Adjust hockey stick positioning
   - Blend edges for smoother integration
   - Ensure overlap enhances rather than obscures
   - Test visual clarity

1. **Update Generation Script** (10 min)

   - Ensure `scripts/generate_branding.py` includes refinements
   - Add any new generation logic if needed
   - Verify script dependencies are installed
   - Test script locally

1. **Generate All Assets** (5 min)

   - Run: `python scripts/generate_branding.py`
   - Verify all output files created
   - Check multiple size variants
   - Test favicon rendering

1. **Visual QA** (10 min)

   - View logo at multiple sizes
   - Test on light and dark backgrounds
   - Verify favicon in browser
   - Check README banner appearance
   - Ensure docs logo displays correctly

1. **Commit Updated Branding** (5 min)

   - Add all generated assets
   - Commit with descriptive message
   - Include before/after comparison in PR

## Testing Strategy

### Visual Testing

**Size Variants:**

```bash
# Generate all variants
python scripts/generate_branding.py

# Verify outputs exist
ls -lh docs/_static/logo.png
ls -lh docs/_static/favicon.ico
ls -lh README_banner.png

# Test logo at different sizes
for size in 32 64 128 256 512; do
    convert docs/_static/logo.png -resize ${size}x${size} test_${size}.png
done
```

**Background Testing:**

- Test logo on white background (README)
- Test logo on dark background (GitHub dark mode)
- Test favicon in browser tabs
- Test docs logo in Sphinx documentation

### Automated Checks

```bash
# Verify script runs without errors
python scripts/generate_branding.py

# Check output file formats
file docs/_static/logo.png  # Should be PNG
file docs/_static/favicon.ico  # Should be ICO

# Verify image dimensions
identify docs/_static/logo.png
identify README_banner.png
```

### Manual Review Checklist

- [ ] Logo tiles are evenly spaced
- [ ] Hockey stick overlap looks natural
- [ ] Logo is crisp at small sizes (32x32 favicon)
- [ ] Logo is clear at large sizes (banner)
- [ ] Colors have good contrast
- [ ] Design matches NHL/hockey theme
- [ ] Logo works on light backgrounds
- [ ] Logo works on dark backgrounds

## Acceptance Criteria

- [ ] Logo tiles are refined with improved spacing/sizing
- [ ] Hockey stick overlap is adjusted for better visual integration
- [ ] `scripts/generate_branding.py` script runs successfully
- [ ] All branding assets are generated:
  - [ ] `docs/_static/logo.png` (updated)
  - [ ] `docs/_static/favicon.ico` (updated)
  - [ ] `README_banner.png` (if used)
  - [ ] Additional variants as needed
- [ ] Logo displays correctly at multiple sizes
- [ ] Logo works on light and dark backgrounds
- [ ] Favicon renders properly in browsers
- [ ] Visual QA passes for all variants
- [ ] Updated branding assets committed to repository
- [ ] Before/after comparison documented

## Related Files

**Modified Files:**

- `scripts/generate_branding.py` - Branding generation script (if updates needed)
- `docs/_static/logo.png` - Main project logo
- `docs/_static/favicon.ico` - Website favicon
- `README_banner.png` - README header image (if exists)

**Source Files (if separate):**

- `assets/logo_tiles/` - Source tile designs
- `assets/hockey_stick/` - Hockey stick graphic
- `assets/logo_source.svg` - Vector source file (if exists)

**Documentation:**

- `README.md` - May display logo banner
- `docs/conf.py` - Sphinx logo configuration
- `docs/index.rst` - Documentation homepage with logo

## Dependencies

**Python Dependencies:**

- `Pillow` (PIL) - Image manipulation (likely already installed for docs)
- Python 3.10+ (already required)

**Optional Design Tools:**

- Image editing software (GIMP, Photoshop, Inkscape)
- Vector graphics editor for source files
- Color picker for consistency

**No Task Dependencies** - Standalone visual enhancement

## Additional Notes

### Design Principles

**Logo Design Best Practices:**

1. **Scalability**: Logo should work from 16x16 (favicon) to 1200px (banner)
1. **Simplicity**: Avoid overly complex elements at small sizes
1. **Contrast**: Ensure readability on various backgrounds
1. **Consistency**: Maintain NHL/hockey theme throughout
1. **Professionalism**: Polish reflects project quality

### Branding Consistency

**Where Logo Appears:**

- **README.md**: Banner/header image
- **Documentation**: Sphinx theme logo
- **Favicon**: Browser tabs, bookmarks
- **GitHub**: Social preview image
- **PyPI**: Package listing logo (if supported)

**Color Palette:**

Maintain consistent colors across all branding:

- Primary: NHL-themed colors
- Secondary: Hockey stick accent
- Background: Transparent or white/dark variants

### Generation Script Benefits

**Automation Advantages:**

- **Consistency**: All variants generated from single source
- **Reproducibility**: Easy to regenerate if design changes
- **Efficiency**: One command creates all needed formats
- **Version Control**: Script in git ensures reproducible builds

**Script Workflow:**

```bash
# Make design refinements in source files
# or directly in scripts/generate_branding.py

# Generate all assets
python scripts/generate_branding.py

# Verify outputs
ls -lh docs/_static/
ls -lh README_banner.png

# Test in context
make docs
open docs/_build/html/index.html  # View logo in docs

# Commit updates
git add docs/_static/ README_banner.png scripts/generate_branding.py
git commit -m "design: Refine logo tiles and hockey stick overlap"
```

### Visual Quality Checklist

**Before Generation:**

- [ ] Source design files are high resolution
- [ ] Colors are defined in consistent palette
- [ ] Vector elements are clean (if SVG source)
- [ ] Tile alignment is mathematically precise

**After Generation:**

- [ ] No pixelation at any size
- [ ] Colors match source design
- [ ] No artifacts or compression issues
- [ ] Transparent backgrounds work correctly
- [ ] ICO favicon includes multiple sizes

### Future Enhancements

After initial refinement, consider:

- **Animated Logo**: Subtle animation for web use
- **Dark Mode Variant**: Optimized logo for dark themes
- **Social Media**: Twitter card, Open Graph images
- **Stickers/Swag**: Print-ready logo variants
- **Icon Set**: Complementary icons for UI elements

### Testing on GitHub

**GitHub Rendering:**

```markdown
# README.md
![NHL Scrabble](README_banner.png)
```

**Social Preview:**

- Repository Settings → Social Preview
- Upload: `README_banner.png` (1200x630px recommended)
- Verify in link previews (Twitter, Slack, etc.)

### Breaking Changes

**None** - This is purely visual enhancement:

- No API changes
- No functionality changes
- No configuration changes
- Backwards compatible

### Migration Notes

**First Run:**

- Backup existing logo assets before running script
- Review generated assets before committing
- Test documentation builds locally
- Verify favicon displays in browsers

**Rollback:**

If refinements aren't satisfactory:

```bash
# Restore previous assets
git checkout HEAD~1 -- docs/_static/
git checkout HEAD~1 -- README_banner.png

# Or restore from backup
cp backup/logo.png docs/_static/logo.png
```

### Troubleshooting

**Script Fails:**

```bash
# Check Python dependencies
pip list | grep -i pillow

# Install if missing
pip install Pillow

# Verify Python version
python --version  # Should be 3.10+
```

**Output Quality Issues:**

- Increase source resolution
- Use lossless formats (PNG, not JPG)
- Verify color profiles
- Check antialiasing settings

**Favicon Not Displaying:**

- Clear browser cache (Ctrl+Shift+Del)
- Verify ICO format (not PNG renamed to .ico)
- Check browser console for errors
- Verify path in HTML: `<link rel="icon" href="_static/favicon.ico">`

### Documentation Updates

After refinement, update:

- **README.md**: If logo placement changes
- **docs/conf.py**: If logo configuration changes
- **CONTRIBUTING.md**: Document how to regenerate branding
- **This task file**: Add implementation notes when complete

### Design Collaboration

If working with a designer:

1. Share current logo and pain points
1. Iterate on refinements
1. Export high-resolution source files
1. Update generation script to match new design
1. Document design decisions for future reference
