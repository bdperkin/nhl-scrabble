#!/usr/bin/env python3
"""Generate branding assets from source SVG.

This script converts the source SVG logo into all required formats and sizes
for use across the project: favicons, documentation logos, and social media images.

Requirements:
    pip install Pillow cairosvg

Usage:
    python scripts/generate_branding.py
    python scripts/generate_branding.py --source assets/branding/source/custom-logo.svg

The script will:
    1. Generate all favicon sizes (16x16, 32x32, ICO, Apple Touch, Android Chrome)
    2. Generate documentation logos (64px, 128px, 256px, 512px, SVG)
    3. Generate social media images (400x400 square, placeholder for 1200x630)
    4. Copy assets to appropriate locations (docs/_static/, .github/)
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

try:
    import cairosvg
    from PIL import Image
except ImportError as e:
    print(f"Error: {e}")
    print("\nRequired packages not installed. Install with:")
    print("  pip install Pillow cairosvg")
    print("  # or")
    print("  pip install -e '.[branding]'")
    sys.exit(1)


# Directory paths
REPO_ROOT = Path(__file__).parent.parent
SOURCE_DIR = REPO_ROOT / "assets" / "branding" / "source"
FAVICONS_DIR = REPO_ROOT / "assets" / "branding" / "favicons"
LOGOS_DIR = REPO_ROOT / "assets" / "branding" / "logos"
SOCIAL_DIR = REPO_ROOT / "assets" / "branding" / "social"
DOCS_STATIC = REPO_ROOT / "docs" / "_static"
GITHUB_DIR = REPO_ROOT / ".github"


def generate_png(svg_path: Path, output_path: Path, size: int) -> None:
    """Generate PNG from SVG at specified size.

    Args:
        svg_path: Path to source SVG file
        output_path: Path to output PNG file
        size: Output size in pixels (square)
    """
    print(f"  Generating {output_path.name} ({size}x{size}px)...")
    png_data = cairosvg.svg2png(
        url=str(svg_path),
        output_width=size,
        output_height=size,
    )
    output_path.write_bytes(png_data)


def generate_ico(png_paths: list[Path], output_path: Path) -> None:
    """Generate multi-resolution ICO file from PNG files.

    Args:
        png_paths: List of PNG file paths to include
        output_path: Path to output ICO file
    """
    print(f"  Generating {output_path.name} (multi-resolution ICO)...")
    images = [Image.open(p) for p in png_paths]
    images[0].save(
        output_path,
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48)],
    )


def generate_social_preview(source_svg: Path, output_path: Path) -> None:
    """Generate social preview image (1200x630).

    Note: This creates a centered version. For best results, manually create
    a version optimized for the 1200x630 aspect ratio.

    Args:
        source_svg: Path to source SVG file
        output_path: Path to output PNG file
    """
    print(f"  Generating {output_path.name} (1200x630px - centered)...")

    # Generate a large square version first
    temp_square = output_path.parent / "temp_square.png"
    generate_png(source_svg, temp_square, 630)

    # Create rectangular canvas and center the logo
    img = Image.open(temp_square)
    canvas = Image.new("RGBA", (1200, 630), (255, 255, 255, 255))

    # Center horizontally
    x_offset = (1200 - 630) // 2
    canvas.paste(img, (x_offset, 0))

    # Save
    canvas.save(output_path, "PNG")
    temp_square.unlink()

    print("    NOTE: For best results, manually optimize this image")
    print("          for the 1200x630 aspect ratio")


def copy_to_docs(logos_dir: Path, favicons_dir: Path, docs_static: Path) -> None:
    """Copy logo and favicon to Sphinx _static directory.

    Args:
        logos_dir: Path to logos directory
        favicons_dir: Path to favicons directory
        docs_static: Path to Sphinx _static directory
    """
    print("\nCopying assets to Sphinx documentation...")

    # Ensure docs/_static exists
    docs_static.mkdir(parents=True, exist_ok=True)

    # Copy logo SVG
    logo_svg = logos_dir / "logo.svg"
    if logo_svg.exists():
        shutil.copy2(logo_svg, docs_static / "logo.svg")
        print(f"  ✓ Copied {logo_svg.name} to docs/_static/")

    # Copy favicon
    favicon = favicons_dir / "favicon.ico"
    if favicon.exists():
        shutil.copy2(favicon, docs_static / "favicon.ico")
        print(f"  ✓ Copied {favicon.name} to docs/_static/")


def copy_to_github(logos_dir: Path, github_dir: Path) -> None:
    """Copy logo to .github directory for README.

    Args:
        logos_dir: Path to logos directory
        github_dir: Path to .github directory
    """
    print("\nCopying assets to .github directory...")

    # Ensure .github exists
    github_dir.mkdir(parents=True, exist_ok=True)

    # Copy 256px logo for README
    logo_256 = logos_dir / "logo-256.png"
    if logo_256.exists():
        shutil.copy2(logo_256, github_dir / "logo.png")
        print(f"  ✓ Copied {logo_256.name} to .github/logo.png")


def main() -> None:
    """Generate all branding assets from source SVG."""
    parser = argparse.ArgumentParser(description="Generate branding assets from SVG")
    parser.add_argument(
        "--source",
        type=Path,
        default=SOURCE_DIR / "logo.svg",
        help="Path to source SVG file (default: assets/branding/source/logo.svg)",
    )
    parser.add_argument(
        "--skip-social",
        action="store_true",
        help="Skip generating social preview image",
    )
    args = parser.parse_args()

    source_svg = args.source

    # Validate source SVG exists
    if not source_svg.exists():
        print(f"Error: Source SVG not found: {source_svg}")
        print("\nPlease create your logo SVG file first:")
        print(f"  {source_svg}")
        print("\nOr use --source to specify a different file:")
        print("  python scripts/generate_branding.py --source path/to/logo.svg")
        sys.exit(1)

    print(f"🎨 Generating branding assets from: {source_svg}")
    print("=" * 70)

    # Create directories
    print("\nCreating directories...")
    FAVICONS_DIR.mkdir(parents=True, exist_ok=True)
    LOGOS_DIR.mkdir(parents=True, exist_ok=True)
    SOCIAL_DIR.mkdir(parents=True, exist_ok=True)
    print("  ✓ Directories created")

    # Generate favicons
    print("\nGenerating favicons...")
    generate_png(source_svg, FAVICONS_DIR / "favicon-16x16.png", 16)
    generate_png(source_svg, FAVICONS_DIR / "favicon-32x32.png", 32)
    generate_png(source_svg, FAVICONS_DIR / "apple-touch-icon.png", 180)
    generate_png(source_svg, FAVICONS_DIR / "android-chrome-192x192.png", 192)
    generate_png(source_svg, FAVICONS_DIR / "android-chrome-512x512.png", 512)

    # Generate ICO
    generate_ico(
        [
            FAVICONS_DIR / "favicon-16x16.png",
            FAVICONS_DIR / "favicon-32x32.png",
        ],
        FAVICONS_DIR / "favicon.ico",
    )

    # Generate logos
    print("\nGenerating documentation logos...")
    # Copy source SVG
    shutil.copy2(source_svg, LOGOS_DIR / "logo.svg")
    print(f"  Copied {source_svg.name} to logos/")

    # Generate PNG sizes
    generate_png(source_svg, LOGOS_DIR / "logo-64.png", 64)
    generate_png(source_svg, LOGOS_DIR / "logo-128.png", 128)
    generate_png(source_svg, LOGOS_DIR / "logo-256.png", 256)
    generate_png(source_svg, LOGOS_DIR / "logo-512.png", 512)

    # Generate social media images
    print("\nGenerating social media images...")
    generate_png(source_svg, SOCIAL_DIR / "logo-square.png", 400)

    if not args.skip_social:
        generate_social_preview(source_svg, SOCIAL_DIR / "social-preview.png")

    # Copy to documentation and GitHub
    copy_to_docs(LOGOS_DIR, FAVICONS_DIR, DOCS_STATIC)
    copy_to_github(LOGOS_DIR, GITHUB_DIR)

    # Summary
    print("\n" + "=" * 70)
    print("✅ All branding assets generated successfully!")
    print("\nGenerated files:")
    print(f"  📁 Favicons: {FAVICONS_DIR.relative_to(REPO_ROOT)} (7 files)")
    print(f"  📁 Logos: {LOGOS_DIR.relative_to(REPO_ROOT)} (5 files)")
    print(f"  📁 Social: {SOCIAL_DIR.relative_to(REPO_ROOT)} (2 files)")
    print(f"  📁 Docs: {DOCS_STATIC.relative_to(REPO_ROOT)} (2 files)")
    print(f"  📁 GitHub: {GITHUB_DIR.relative_to(REPO_ROOT)} (1 file)")

    print("\nNext steps:")
    print("  1. Review generated files")
    print("  2. Test favicon at different sizes")
    print("  3. Update README.md to use logo")
    print("  4. Update docs/conf.py to configure logo")
    print("  5. Upload social-preview.png to GitHub repository settings")
    print("\nFor usage guidelines, see:")
    print("  assets/branding/README.md")


if __name__ == "__main__":
    main()
