# NHL Scrabble Branding Assets

This directory contains all branding assets for the NHL Scrabble project, including logos, favicons, and social media images.

## 🎨 Design Brief

**See**: `../DESIGN_BRIEF.md` for complete design specifications and requirements.

## 📁 Directory Structure

```
assets/branding/
├── source/              # Source SVG files
│   ├── logo.svg         # Final logo (PUT YOUR LOGO HERE)
│   └── placeholder-logo.svg  # Temporary placeholder
├── favicons/            # Generated favicons (auto-generated)
│   ├── favicon-16x16.png
│   ├── favicon-32x32.png
│   ├── favicon.ico
│   ├── apple-touch-icon.png
│   ├── android-chrome-192x192.png
│   └── android-chrome-512x512.png
├── logos/               # Generated logos (auto-generated)
│   ├── logo.svg
│   ├── logo-64.png
│   ├── logo-128.png
│   ├── logo-256.png
│   └── logo-512.png
└── social/              # Social media images (auto-generated)
    ├── logo-square.png  # 400x400 for social media
    └── social-preview.png  # 1200x630 for Open Graph/Twitter Cards
```

## 🚀 Quick Start

### Option 1: You Have a Logo

If you already have a logo SVG file:

```bash
# 1. Place your logo in the source directory
cp /path/to/your-logo.svg assets/branding/source/logo.svg

# 2. Install dependencies
pip install Pillow cairosvg
# OR
pip install -e '.[branding]'

# 3. Generate all formats
python scripts/generate_branding.py

# Done! All formats generated automatically.
```

### Option 2: Design a Logo

If you need to design the logo:

**Using Inkscape (Free, Recommended)**:

```bash
# 1. Install Inkscape
# Download from: https://inkscape.org/

# 2. Create new document (512x512px)
# 3. Design your logo following the design brief
# 4. Save as SVG: File → Save As → Plain SVG
# 5. Save to: assets/branding/source/logo.svg

# 6. Generate all formats
pip install Pillow cairosvg
python scripts/generate_branding.py
```

**Using Figma (Free Tier)**:

```bash
# 1. Go to https://www.figma.com/
# 2. Create new file, add 512x512 frame
# 3. Design your logo following the design brief
# 4. Export as SVG: Select frame → Export → SVG
# 5. Save to: assets/branding/source/logo.svg

# 6. Generate all formats
pip install Pillow cairosvg
python scripts/generate_branding.py
```

### Option 3: Hire a Designer

If you want to hire a professional:

```bash
# 1. Go to Fiverr or 99designs
# 2. Search for "svg logo design minimal"
# 3. Share the design brief: assets/DESIGN_BRIEF.md
# 4. Request deliverable: logo.svg (512x512px, optimized)

# 5. Once received, save to: assets/branding/source/logo.svg

# 6. Generate all formats
pip install Pillow cairosvg
python scripts/generate_branding.py
```

## 🔧 Generation Script

The `scripts/generate_branding.py` script automatically generates all required formats from your source SVG.

### Usage

```bash
# Basic usage (uses assets/branding/source/logo.svg)
python scripts/generate_branding.py

# Use custom source file
python scripts/generate_branding.py --source path/to/custom.svg

# Skip social preview generation (create manually)
python scripts/generate_branding.py --skip-social

# Help
python scripts/generate_branding.py --help
```

### What It Does

1. **Generates Favicons**:

   - 16x16px, 32x32px PNG
   - Multi-resolution favicon.ico
   - Apple Touch Icon (180x180px)
   - Android Chrome icons (192x192px, 512x512px)

1. **Generates Logos**:

   - PNG: 64px, 128px, 256px, 512px
   - SVG: Copy of source (optimized)

1. **Generates Social Media**:

   - Square logo (400x400px)
   - Social preview (1200x630px) - centered on white background

1. **Copies to Destinations**:

   - `docs/_static/logo.svg` - Sphinx documentation logo
   - `docs/_static/favicon.ico` - Sphinx documentation favicon
   - `.github/logo.png` - README logo (256px)

### Requirements

```bash
# Python packages
pip install Pillow cairosvg

# Or add to pyproject.toml
[project.optional-dependencies]
branding = [
    "Pillow>=10.0.0",
    "cairosvg>=2.7.0",
]

# Then install with
pip install -e '.[branding]'
```

## 📋 Logo Requirements

Your logo SVG should meet these requirements:

### Technical Requirements

✅ **File Format**: SVG (Scalable Vector Graphics)
✅ **Dimensions**: 512x512px (1:1 square aspect ratio)
✅ **Text to Paths**: All text converted to paths (no font dependencies)
✅ **File Size**: Under 10KB (optimized)
✅ **ViewBox**: `viewBox="0 0 512 512"`
✅ **No External Dependencies**: No embedded images, external fonts, or linked files

### Visual Requirements

✅ **Recognizable at 16x16px**: Logo is clear even at favicon size
✅ **Works on Light Backgrounds**: Clear on white/cream
✅ **Works on Dark Backgrounds**: Clear on black/dark gray
✅ **Works in Grayscale**: Recognizable without color
✅ **Combines Concepts**: Shows both NHL/hockey and Scrabble/scoring elements
✅ **Professional**: Suitable for GitHub, documentation, presentations

### Quality Checklist

Before committing your logo, verify:

- [ ] SVG opens correctly in browser
- [ ] SVG is valid (check with https://validator.w3.org/)
- [ ] All text converted to paths (no fonts required)
- [ ] File size under 10KB
- [ ] Looks good at 16x16px (test favicon)
- [ ] Looks good at 512x512px (test full size)
- [ ] Works on white background
- [ ] Works on dark background (#1a1a1a)
- [ ] Recognizable in grayscale
- [ ] No trademark violations (NHL official logos, Hasbro Scrabble)

## 🎯 Usage Guidelines

### When to Use

- ✅ GitHub README header
- ✅ Documentation homepage
- ✅ Social media posts about the project
- ✅ Presentations/talks about the project
- ✅ PyPI package listing (if published)
- ✅ Stickers/swag (future)

### Size Guide

| Context              | Recommended Size | File to Use                 |
| -------------------- | ---------------- | --------------------------- |
| GitHub README        | 256px            | `.github/logo.png`          |
| Sphinx docs header   | 128px            | `docs/_static/logo.svg`     |
| Browser favicon      | 16-32px          | `docs/_static/favicon.ico`  |
| Social media profile | 400px            | `social/logo-square.png`    |
| Social preview       | 1200x630         | `social/social-preview.png` |
| Presentations        | Vector           | `logos/logo.svg`            |

### Design Guidelines

**Do**:

- ✅ Use official logo files from this directory
- ✅ Maintain aspect ratio when resizing
- ✅ Provide adequate padding/clear space
- ✅ Use on appropriate backgrounds

**Don't**:

- ❌ Modify or recolor the logo
- ❌ Stretch or distort the logo
- ❌ Add effects (shadows, glows, outlines)
- ❌ Display smaller than 16x16px
- ❌ Use on busy or low-contrast backgrounds

## 🔄 Updating the Logo

If you need to update the logo:

```bash
# 1. Update the source SVG
vim assets/branding/source/logo.svg

# 2. Regenerate all formats
python scripts/generate_branding.py

# 3. Test generated files
ls -lh assets/branding/favicons/
ls -lh assets/branding/logos/
ls -lh assets/branding/social/

# 4. Commit changes
git add assets/branding/ docs/_static/ .github/logo.png
git commit -m "feat(branding): Update logo design"
```

## 📦 Integration Points

The generated assets are automatically copied to these locations:

### Documentation (Sphinx)

**Files**:

- `docs/_static/logo.svg` - Logo for documentation header
- `docs/_static/favicon.ico` - Favicon for documentation

**Configuration** (`docs/conf.py`):

```python
html_logo = "_static/logo.svg"
html_favicon = "_static/favicon.ico"
```

### GitHub README

**File**:

- `.github/logo.png` - Logo for README (256px)

**Usage** (`README.md`):

```markdown
<p align="center">
  <img src=".github/logo.png" alt="NHL Scrabble Logo" width="200">
</p>
```

### GitHub Repository Settings

**Manual Upload Required**:

1. Go to: https://github.com/bdperkin/nhl-scrabble/settings
1. Scroll to "Social preview"
1. Upload: `assets/branding/social/social-preview.png`

This shows up when sharing the repository on Twitter, Slack, etc.

## 🧪 Testing Generated Assets

After generation, test your assets:

### Visual Testing

```bash
# 1. Test favicon (open in browser)
open assets/branding/favicons/favicon.ico

# 2. Test logos at different sizes
open assets/branding/logos/logo-64.png
open assets/branding/logos/logo-128.png
open assets/branding/logos/logo-256.png
open assets/branding/logos/logo-512.png

# 3. Test social preview
open assets/branding/social/social-preview.png
```

### Browser Testing

Create a test HTML file:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Logo Test</title>
    <link rel="icon" type="image/x-icon" href="assets/branding/favicons/favicon.ico">
    <style>
        body { font-family: sans-serif; padding: 40px; }
        .bg-light { background: #ffffff; padding: 20px; margin: 20px 0; }
        .bg-dark { background: #1a1a1a; padding: 20px; margin: 20px 0; }
    </style>
</head>
<body>
    <h1>NHL Scrabble Logo Test</h1>

    <h2>Light Background</h2>
    <div class="bg-light">
        <img src="assets/branding/logos/logo-64.png" alt="64px">
        <img src="assets/branding/logos/logo-128.png" alt="128px">
        <img src="assets/branding/logos/logo-256.png" alt="256px">
    </div>

    <h2>Dark Background</h2>
    <div class="bg-dark">
        <img src="assets/branding/logos/logo-64.png" alt="64px">
        <img src="assets/branding/logos/logo-128.png" alt="128px">
        <img src="assets/branding/logos/logo-256.png" alt="256px">
    </div>
</body>
</html>
```

## 🐛 Troubleshooting

### Script Errors

**Problem**: `ModuleNotFoundError: No module named 'cairosvg'`

**Solution**:

```bash
pip install Pillow cairosvg
```

**Problem**: `FileNotFoundError: logo.svg not found`

**Solution**: Create your logo first at `assets/branding/source/logo.svg`

### SVG Issues

**Problem**: Generated PNGs look pixelated or blurry

**Solution**: Check that source SVG uses `viewBox="0 0 512 512"` and is actual vector paths, not embedded raster images

**Problem**: SVG has missing fonts or symbols

**Solution**: Convert all text to paths in your design tool:

- Inkscape: Path → Object to Path
- Figma: Right-click text → Flatten Selection

### Quality Issues

**Problem**: Logo not recognizable at 16x16px

**Solution**: Simplify your design. Logo may be too complex. Consider creating a simplified icon-only version for favicons.

**Problem**: Logo doesn't work on dark backgrounds

**Solution**: Ensure logo has proper stroke/outline or use lighter colors. Test on `#1a1a1a` background.

## 📝 License

The NHL Scrabble logo and branding assets are:

**Copyright**: © 2026 Brandon Perkins
**License**: MIT License (same as project)

You are free to:

- ✅ Use the logo in presentations about the project
- ✅ Include in articles/blog posts about the project
- ✅ Use in derivative works (with attribution)

You must:

- ✅ Provide attribution to NHL Scrabble project
- ✅ Include copy of MIT License

You must not:

- ❌ Claim the logo as your own original work
- ❌ Use in a way that implies official NHL or Hasbro endorsement
- ❌ Use for commercial purposes unrelated to the project

## 🎨 Design Credits

Logo designed by: [Your Name / Designer Name]
Date: [Date]
Design tool: [Inkscape / Figma / etc.]

## 📚 Additional Resources

- **Design Brief**: `../DESIGN_BRIEF.md`
- **Inkscape Tutorials**: https://inkscape.org/learn/
- **Figma Tutorials**: https://www.youtube.com/c/Figma
- **SVG Optimization**: https://github.com/svg/svgo
- **Logo Design Tips**: https://www.smashingmagazine.com/logo-design/

## 🆘 Need Help?

- **GitHub Issue**: #89 - https://github.com/bdperkin/nhl-scrabble/issues/89
- **Discussion**: https://github.com/bdperkin/nhl-scrabble/discussions
- **Documentation**: https://bdperkin.github.io/nhl-scrabble/

______________________________________________________________________

**Status**: 🚧 Placeholder phase - Logo design needed
**Next Step**: Create `source/logo.svg` following the design brief
