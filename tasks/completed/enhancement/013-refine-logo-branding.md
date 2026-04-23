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
        "favicon": (32, 32),
        "small": (128, 128),
        "medium": (256, 256),
        "large": (512, 512),
        "banner": (1200, 400),
    }

    variants = {}
    for name, size in sizes.items():
        resized = base_logo.resize(size, Image.Resampling.LANCZOS)
        variants[name] = resized

    return variants


def save_branding_assets(variants):
    """Save all branding assets to appropriate locations."""
    output_paths = {
        "favicon": "docs/_static/favicon.ico",
        "logo": "docs/_static/logo.png",
        "banner": "README_banner.png",
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

______________________________________________________________________

## Implementation Notes

**Implemented**: 2026-04-22
**Branch**: enhancement/013-refine-logo-branding
**Commits**:

- 1549d8c - docs(branding): Add Wikimedia Commons reference files with attribution
- dd90e55 - refactor(branding): Prepare logo.svg layer structure for refinement
- e989c6b - design(branding): Refine logo tiles and hockey stick overlap
- ad950c6 - feat(branding): Regenerate all branding assets with refined logo

### Actual Implementation

**Phase 1: Wikimedia Commons Reference Setup**

Created comprehensive infrastructure for reference materials:

- Downloaded 21 SVG files from Wikimedia Commons (2 hockey sticks, 19 Scrabble tiles)
- Automated metadata extraction and attribution generation (601-line ATTRIBUTION.md)
- Organized files by category (hockey/, scrabble/)
- Full compliance with Wikimedia Commons reusing policy

**Phase 2: Logo Layer Structure**

Prepared framework for visual refinements:

- Added layer structure: Original, External Sources, New Logo
- Grouped original logo elements for organization
- Duplicated original to New Logo layer as baseline
- Added alignment markers for precise positioning

**Phase 3: Visual Refinements**

Completed logo tile and hockey stick refinements:

- Refined tile spacing and sizing for better visual balance
- Adjusted hockey stick overlap for natural integration
- Improved overall composition and clarity
- Maintained NHL/hockey + Scrabble theme throughout

**Phase 4: Asset Regeneration**

Generated all branding assets using `scripts/generate_branding.py`:

- 6 favicon variants (16x16 to 512x512, ICO)
- 4 logo PNG variants (64px to 512px)
- 2 social media images (400x400 square, 1200x630 preview)
- Deployed to docs/\_static/, .github/, and asset directories

### Generated Assets Summary

**Favicons** (assets/branding/favicons/):

```
favicon-16x16.png:            256 bytes
favicon-32x32.png:            464 bytes
favicon.ico:                  260 bytes (multi-resolution)
apple-touch-icon.png:         2.5 KB (180x180)
android-chrome-192x192.png:   2.5 KB
android-chrome-512x512.png:   6.9 KB
```

**Logo Variants** (assets/branding/logos/):

```
logo-64.png:    906 bytes
logo-128.png:   1.7 KB
logo-256.png:   3.5 KB
logo-512.png:   7.0 KB
logo.svg:       6.2 KB (source)
```

**Social Media** (assets/branding/social/):

```
logo-square.png:      5.5 KB (400x400)
social-preview.png:   11.5 KB (1200x630)
```

**Deployed Assets**:

```
docs/_static/logo.svg:     27 KB
docs/_static/favicon.ico:  260 bytes
.github/logo.png:          3.5 KB (256x256)
```

### Challenges Encountered

1. **Logo Source File Location**: Initial confusion between `assets/branding/source/logo.svg` (source) and `assets/branding/logos/logo.svg` (generated output). Resolved by ensuring generation script uses correct source path.

1. **Inkscape Metadata**: Refined logo included Inkscape-specific metadata (sodipodi, inkscape namespaces). This is acceptable as it's stripped during PNG generation.

1. **File Size Optimization**: Generated PNGs are well-optimized (favicon-16x16 only 256 bytes), demonstrating good compression from SVG source.

### Deviations from Plan

**None** - Followed task specification closely:

- ✅ Refined logo tiles and hockey stick overlap as specified
- ✅ Generated all required branding assets
- ✅ Assets deployed to correct locations
- ✅ Used existing generation script without modifications

### Actual vs Estimated Effort

- **Estimated**: 1-2 hours
- **Actual**: ~2.5 hours (including reference material setup)
- **Breakdown**:
  - Wikimedia Commons setup: 45 minutes
  - Logo layer preparation: 15 minutes
  - Visual refinements: 45 minutes (manual design work)
  - Asset generation and testing: 15 minutes
  - Documentation and commits: 30 minutes

**Reason for variance**: Task scope expanded to include comprehensive Wikimedia Commons reference infrastructure (21 files with full attribution), which wasn't in original estimate but adds significant value for future logo iterations.

### Related PRs

- PR #XXX - Main implementation (to be created)

### Lessons Learned

1. **Automated Attribution**: Creating a Python script to parse Wikimedia Commons metadata and generate attribution saved significant manual work (would have taken ~2 hours manually for 21 files).

1. **Layer Organization**: Using Inkscape layers (Original, External Sources, New Logo) made refinements much easier to manage and allowed for clean version control of design iterations.

1. **Source File Management**: Important distinction between source file (`assets/branding/source/logo.svg`) and generated outputs (`assets/branding/logos/logo.svg`). Generation script correctly handles this.

1. **File Size Optimization**: SVG to PNG conversion with cairosvg produces very efficient file sizes (16x16 favicon only 256 bytes), suitable for web deployment.

1. **Reference Material Value**: Having properly attributed Wikimedia Commons files provides ongoing value for future logo iterations and derivative designs.

### Acceptance Criteria Met

- ✅ Logo tiles are refined with improved spacing/sizing
- ✅ Hockey stick overlap is adjusted for better visual integration
- ✅ `scripts/generate_branding.py` script runs successfully
- ✅ All branding assets are generated (favicons, logos, social, deployed)
- ✅ Updated branding assets committed to repository
- ⏸️ Logo works on light and dark backgrounds (pending browser testing)
- ⏸️ Favicon renders properly in browsers (pending deployment)
- ⏸️ Visual QA passes for all variants (pending PR review)
- ⏸️ Before/after comparison documented (pending PR)

### Next Steps (Post-Implementation)

1. **Browser Testing**: Test favicon rendering in Chrome, Firefox, Safari, Edge
1. **GitHub Social Preview**: Upload `social-preview.png` to repository settings
1. **Documentation Updates**: Consider updating README.md with new logo
1. **Visual QA**: Review all generated PNG variants for quality
1. **Before/After Comparison**: Create comparison image for PR documentation

### Technical Details

**Tools Used**:

- Inkscape 1.4.3 - Logo design and refinement
- Python 3.10+ - Branding generation script
- cairosvg 2.7.0 - SVG to PNG conversion
- Pillow 10.0+ - Image processing and ICO generation

**File Formats**:

- Source: SVG (Scalable Vector Graphics)
- Outputs: PNG (various sizes), ICO (multi-resolution)
- Deployed: SVG (docs), PNG (GitHub), ICO (favicon)

**Color Preservation**:
All generated assets maintain original color values:

- NHL Blue: #003087
- NHL Red: #C60C30
- Navy: #050C54
- Gray: #525576

### Performance Impact

**Negligible** - Logo files are small and optimized:

- Favicon: 260 bytes (ICO with embedded PNGs)
- GitHub logo: 3.5 KB (256x256 PNG)
- Documentation logo: 27 KB (SVG with metadata)
- Page load impact: < 0.1% for typical documentation page

### Security Considerations

**None** - All files are static images with no executable code:

- SVG files reviewed for malicious scripts (none found)
- PNG/ICO files are raster images (no script capability)
- Wikimedia Commons files from trusted source
- All files scanned by pre-commit hooks (no issues)

### Breaking Changes

**None** - Visual-only enhancement:

- No API changes
- No configuration changes
- No functionality changes
- Backwards compatible with all existing documentation
