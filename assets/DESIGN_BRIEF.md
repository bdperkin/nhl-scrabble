# NHL Scrabble Logo Design Brief

**Project**: NHL Roster Scrabble Score Analyzer
**Date**: 2026-04-17
**Budget**: $50-200 (if hiring) or DIY with free tools
**Timeline**: 2-4 hours design time

______________________________________________________________________

## Project Overview

### What is NHL Scrabble?

NHL Scrabble is a Python command-line tool that fetches NHL roster data and calculates "Scrabble scores" for player names using standard Scrabble letter values. It's a fun, analytical project that combines:

- **NHL Hockey**: Professional ice hockey statistics and rosters
- **Scrabble Scoring**: Letter values (A=1, Q=10, Z=10, etc.)
- **Data Analysis**: Team rankings, playoff brackets, statistical reports

**Target Audience**: Hockey fans, Python developers, data enthusiasts, open-source contributors

### Brand Personality

- **Analytical** but approachable
- **Professional** but fun
- **Technical** but accessible
- **Sports-oriented** but inclusive

Think: "Nerd meets sports fan"

______________________________________________________________________

## Design Requirements

### Must-Have Features

1. **Combines Two Concepts**

   - NHL/Hockey imagery (stick, puck, rink, net, etc.)
   - Scrabble elements (tiles, letters, point values, board grid)

1. **Scalability**

   - Must be recognizable at 16x16px (favicon size)
   - Must look professional at 512x512px
   - Should be simple enough for small sizes

1. **Versatility**

   - Works on light backgrounds (white/cream)
   - Works on dark backgrounds (black/dark gray)
   - Can be used in grayscale/monochrome
   - No color dependency for recognition

1. **File Format**

   - **Primary deliverable**: SVG (Scalable Vector Graphics)
   - Editable paths (no embedded rasters)
   - Clean, optimized code (\<10KB file size)
   - No external dependencies or fonts (convert text to paths)

### Visual Style

- **Clean and modern** (not retro/vintage)
- **Bold and distinctive** (memorable)
- **Professional** (suitable for GitHub README)
- **Simple** (easy to reproduce, trace, remember)

### Colors

**Suggested Palette** (but designer has creative freedom):

```
Option 1: NHL-inspired
- Navy Blue: #003087 (NHL official blue)
- Red: #C60C30 (NHL official red)
- White: #FFFFFF
- Black: #000000

Option 2: Scrabble-inspired
- Tile Beige: #F4E4C1
- Letter Black: #2B2B2B
- Accent Blue: #4A90E2

Option 3: Combination
- Primary: #003087 (NHL blue)
- Secondary: #F4E4C1 (Scrabble tile)
- Accent: #C60C30 (NHL red)
- Text: #000000
```

**Important**: Logo should work in single color (black or white) for versatility.

______________________________________________________________________

## Concept Ideas

Here are some starting points (designer should feel free to explore beyond these):

### Concept A: Letter Tile Hockey Puck

```
┌─────────────┐
│             │
│   🏒  H     │  ← Hockey stick + Letter "H"
│      10     │  ← Point value
│             │
└─────────────┘
```

- Hockey puck shaped like a Scrabble tile
- Contains letter "H" (for Hockey) or "N" (for NHL)
- Shows point value (4 for H, 1 for N)
- Simple, iconic, scalable

### Concept B: Hockey Stick Word

```
  ╔═══╗ ╔═══╗ ╔═══╗
  ║ N ║ ║ H ║ ║ L ║
  ║ 1 ║ ║ 4 ║ ║ 1 ║
  ╚═══╝ ╚═══╝ ╚═══╝
     └──🏒──┘
```

- Three Scrabble tiles spelling "NHL"
- Hockey stick underlining or connecting them
- Classic and immediately recognizable

### Concept C: Rink Grid Pattern

```
╔══════════════╗
║ ╔═╗ ╔═╗ ╔═╗ ║
║ ║N║ ║H║ ║L║ ║  ← Ice rink outline
║ ╚═╝ ╚═╝ ╚═╝ ║    with tile grid inside
╚══════════════╝
```

- Ice rink outline
- Scrabble board grid pattern inside
- Letters or score in center

### Concept D: Hockey Net + Board

```
     ╔═════════╗
    ╱║ S  37  ║╲
   ╱ ║         ║ ╲  ← Hockey net shape
  ╱  ╚═════════╝  ╲   with Scrabble tile
 ╱_________________╲
```

- Hockey net silhouette
- Scrabble tile in center
- Shows example score

### Concept E: Minimalist Badge

```
  ◆────────◆
  │  NHL   │
  │   🏒   │  ← Simple badge with
  │   37   │    hockey stick + score
  ◆────────◆
```

- Badge/emblem shape
- Minimal elements (stick or puck)
- Score number as focal point
- Professional and clean

______________________________________________________________________

## Technical Specifications

### Canvas Size

- **Artboard**: 512x512px (1:1 square ratio)
- **Safe area**: Keep important elements within central 400x400px
- **Padding**: Minimum 32px margin on all sides

### SVG Requirements

```xml
<ns0:svg xmlns:ns0="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <ns0:title>NHL Scrabble Logo</ns0:title>
</ns0:svg>
```

**Technical checklist**:

- ✅ Use `viewBox="0 0 512 512"` for proper scaling
- ✅ Convert all text to paths (no font dependencies)
- ✅ Simplify paths (reduce anchor points)
- ✅ Use semantic layer names
- ✅ Remove invisible/hidden layers
- ✅ Optimize with SVGO or similar tool
- ✅ File size under 10KB

### Export Requirements

**Primary Deliverable**:

- `logo.svg` - Clean, optimized SVG source file

**Secondary (nice to have, but can be auto-generated)**:

- `logo-preview.png` - 512x512px preview
- `logo-light-bg.png` - On white background
- `logo-dark-bg.png` - On dark gray background

______________________________________________________________________

## Size Testing

Logo must be tested at these sizes:

| Size    | Context       | Requirement                           |
| ------- | ------------- | ------------------------------------- |
| 16x16px | Favicon       | Recognizable icon, main shape visible |
| 32x32px | Small favicon | Details start to appear               |
| 64px    | GitHub avatar | Clear and professional                |
| 128px   | Documentation | All details visible                   |
| 256px   | README header | Full quality, impressive              |
| 512px   | Social media  | Perfect quality                       |

**Critical**: At 16x16px, the logo should still communicate "hockey + scoring"

______________________________________________________________________

## Usage Contexts

Where the logo will appear:

### Web/Digital

- ✅ GitHub README (256px, light/dark mode)
- ✅ GitHub repository avatar (64px)
- ✅ GitHub social preview (1200x630px - will be cropped from square)
- ✅ Sphinx documentation header (128px)
- ✅ Browser favicon (16x16, 32x32)
- ✅ Mobile bookmark icon (180x180 Apple Touch Icon)
- ✅ PyPI package page (if published)

### Documentation

- ✅ PDF exports (vector, scalable)
- ✅ Presentations (PowerPoint/Google Slides)
- ✅ Terminal ASCII art (optional, for fun)

### Print (Future)

- ✅ Stickers (2-4 inches)
- ✅ T-shirts (chest logo)
- ✅ Business cards (optional)

______________________________________________________________________

## What to Avoid

❌ **Don't**:

- Use official NHL team logos (trademark violation)
- Use Hasbro's Scrabble branding (trademark violation)
- Make it too complex (won't scale to 16px)
- Rely on color for recognition (must work in B&W)
- Use gradients (makes file size huge, doesn't scale well)
- Use text that must be read at small sizes
- Make it too "busy" or detailed

✅ **Do**:

- Suggest hockey through simple shapes (stick, puck, net)
- Suggest Scrabble through tile shape or point values
- Keep it simple and iconic
- Test at 16x16px frequently
- Use solid colors or simple patterns
- Make it memorable and unique

______________________________________________________________________

## Design Tools

### Free Options (Recommended for DIY)

**Inkscape** (Desktop, Free)

- Download: https://inkscape.org/
- Best for: Full SVG control, professional results
- Learning curve: Moderate
- Tutorial: "Inkscape for Beginners" on YouTube

**Figma** (Web, Free Tier)

- URL: https://www.figma.com/
- Best for: Modern interface, easy to learn
- Learning curve: Easy
- Can export to SVG

### Paid Options (If Hiring)

**Fiverr**

- Search: "svg logo design simple minimal"
- Budget: $50-150
- Timeline: 2-7 days
- Tip: Show this brief, request 2-3 concepts

**99designs**

- Run a contest: $299+
- Get 10-30 concepts from multiple designers
- Choose winner
- Higher quality but more expensive

______________________________________________________________________

## Deliverables Checklist

When complete, the designer should provide:

### Required Files

```
assets/branding/source/
├── logo.svg                 # Primary deliverable (clean, optimized)
├── logo-light-bg.png        # Preview on white background (512x512)
└── logo-dark-bg.png         # Preview on dark background (512x512)
```

### File Specifications

- **SVG**:

  - Optimized, \<10KB
  - All text converted to paths
  - Clean layer names
  - No external dependencies

- **PNG Previews**:

  - 512x512px
  - PNG-24 with transparency
  - Optimized with pngcrush/optipng

### Documentation

- **Design rationale** (2-3 sentences explaining the concept)
- **Color codes** (hex values used)
- **Usage notes** (any specific guidance)

______________________________________________________________________

## Success Criteria

A successful logo will:

✅ **Communicate concept** - Viewer immediately understands "hockey + scoring"
✅ **Scale perfectly** - Recognizable from 16px to 512px
✅ **Work everywhere** - Light, dark, color, grayscale
✅ **Be memorable** - Distinctive and unique
✅ **Look professional** - Suitable for GitHub, documentation, presentations
✅ **Be simple** - Easy to reproduce, trace, describe
✅ **Be versatile** - Works as icon, wordmark, or combination

______________________________________________________________________

## Inspiration & References

### Similar Projects (for style reference)

- **Pytest Logo**: Simple, iconic, professional
- **Python Logo**: Two elements combined (snakes)
- **GitHub Octopus**: Scalable, recognizable at any size
- **Rust Logo**: Clean geometric design
- **Docker Whale**: Combines two concepts (container + whale)

### Design Styles to Consider

**Flat Design**

- No shadows or gradients
- Clean lines
- Modern and professional

**Line Art**

- Outlined shapes
- Works great in single color
- Scalable and clean

**Badge/Emblem**

- Classic shape (circle, shield, diamond)
- Professional and authoritative
- Works for sports theme

**Minimalist**

- Absolute minimum elements
- Maximum impact
- Best for scaling

______________________________________________________________________

## Next Steps

### For Designer

1. **Review this brief** - Understand project and requirements
1. **Sketch 2-3 concepts** - Rough ideas on paper or digital
1. **Get feedback** - Share sketches before finalizing
1. **Create SVG** - Use Inkscape/Figma to create final logo
1. **Test scaling** - Export at 16px, 64px, 256px, 512px to verify
1. **Optimize** - Clean up SVG, reduce file size
1. **Deliver files** - SVG + PNG previews

### For Review/Approval

When designer provides concepts, evaluate on:

- Does it communicate "hockey + scoring"?
- Is it recognizable at 16x16px?
- Does it work in light and dark modes?
- Does it look professional?
- Is it unique and memorable?
- Is the SVG clean and optimized?

______________________________________________________________________

## Questions for Designer

Before starting, designer may ask:

**Q: Should it include the word "NHL Scrabble"?**
A: Optional. Icon-only is fine. If text included, must convert to paths.

**Q: Can I use color?**
A: Yes, but logo must also work in single color (black or white).

**Q: How literal should the hockey/Scrabble elements be?**
A: Suggestive is better than literal. Shapes that hint at the concept.

**Q: Can I add a tagline?**
A: Not in the primary logo. Keep it simple.

**Q: What if my design doesn't work at 16px?**
A: Create a simplified version for favicons (common practice).

______________________________________________________________________

## License

The final logo will be licensed under **MIT License** (same as the project).

Designer retains right to showcase in portfolio, but all usage rights transfer to project.

______________________________________________________________________

## Contact

For questions or to submit designs:

- **GitHub Issue**: #89 - https://github.com/bdperkin/nhl-scrabble/issues/89
- **Project**: https://github.com/bdperkin/nhl-scrabble

______________________________________________________________________

**Good luck! We're excited to see what you create! 🏒🔤**
