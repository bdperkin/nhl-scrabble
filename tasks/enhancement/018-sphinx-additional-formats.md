# Support Additional Sphinx Output Formats

**GitHub Issue**: #232 - https://github.com/bdperkin/nhl-scrabble/issues/232

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

2-3 hours

## Description

Expand Sphinx documentation build system to support multiple output formats beyond HTML. Add support for Texinfo, man pages, PDF (via pdflatex), and plain text formats to provide comprehensive documentation distribution options for different use cases.

## Current State

**Current Sphinx Configuration:**

The project currently uses Sphinx to generate HTML documentation deployed to GitHub Pages:

```python
# docs/conf.py
project = "NHL Scrabble"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    # ... other extensions
]

html_theme = "sphinx_rtd_theme"
```

**Current Build Process:**

```bash
# Makefile
docs:
	sphinx-build -b html docs docs/_build/html

serve-docs:
	sphinx-autobuild docs docs/_build/html --port 8000
```

**Current Output:**

- HTML documentation only (deployed to GitHub Pages)
- Accessible at: https://bdperkin.github.io/nhl-scrabble/

**Limitations:**

1. **No Offline Documentation** - Users need internet access
1. **No System Integration** - Can't install as man pages
1. **No PDF Distribution** - Can't provide downloadable PDF manual
1. **No Info Pages** - No GNU Info format for Emacs/Info readers
1. **No Plain Text** - No simple text-only format

## Proposed Solution

### Add Multiple Sphinx Builders

Configure Sphinx to build documentation in 5 additional formats:

1. **HTML** (existing) - Web documentation
1. **Texinfo** (new) - GNU Info format for Emacs
1. **Man Pages** (new) - Unix man page format
1. **PDF** (new) - Portable document format via LaTeX
1. **Text** (new) - Plain text documentation

### Implementation Approach

**1. Update Sphinx Configuration (docs/conf.py)**

```python
# docs/conf.py

# Man page configuration
man_pages = [
    (
        "index",                    # Source document
        "nhl-scrabble",            # Man page name
        "NHL Scrabble Documentation",  # Description
        ["Brandon Perkins"],       # Authors
        1,                         # Section (1 = commands)
    ),
]

# Texinfo configuration
texinfo_documents = [
    (
        "index",                   # Source document
        "nhl-scrabble",           # Target name
        "NHL Scrabble Documentation",  # Title
        "Brandon Perkins",        # Author
        "nhl-scrabble",           # Dir menu entry
        "NHL player name Scrabble scoring system",  # Description
        "Miscellaneous",          # Category
    ),
]

# LaTeX/PDF configuration
latex_documents = [
    (
        "index",                   # Source document
        "nhl-scrabble.tex",       # Target name
        "NHL Scrabble Documentation",  # Title
        "Brandon Perkins",        # Author
        "manual",                 # Document class (manual or howto)
    ),
]

latex_elements = {
    "papersize": "letterpaper",
    "pointsize": "10pt",
    "preamble": "",
    "figure_align": "htbp",
}

# Text output configuration
text_newlines = "unix"
text_sectionchars = "*=-~\"+`"
```

**2. Add Makefile Targets**

```makefile
# Makefile

.PHONY: docs-html docs-man docs-texinfo docs-pdf docs-text docs-all

docs-html:  ## Build HTML documentation
	@echo "Building HTML documentation..."
	sphinx-build -b html docs docs/_build/html
	@echo "HTML docs: docs/_build/html/index.html"

docs-man:  ## Build man pages
	@echo "Building man pages..."
	sphinx-build -b man docs docs/_build/man
	@echo "Man pages: docs/_build/man/"

docs-texinfo:  ## Build Texinfo documentation
	@echo "Building Texinfo documentation..."
	sphinx-build -b texinfo docs docs/_build/texinfo
	@echo "Texinfo: docs/_build/texinfo/"

docs-pdf:  ## Build PDF documentation (requires pdflatex)
	@echo "Building PDF documentation..."
	sphinx-build -b latex docs docs/_build/latex
	@$(MAKE) -C docs/_build/latex all-pdf
	@echo "PDF: docs/_build/latex/nhl-scrabble.pdf"

docs-text:  ## Build plain text documentation
	@echo "Building text documentation..."
	sphinx-build -b text docs docs/_build/text
	@echo "Text docs: docs/_build/text/"

docs-all: docs-html docs-man docs-texinfo docs-pdf docs-text  ## Build all documentation formats
	@echo "All documentation formats built successfully!"
```

**3. Update .gitignore**

```gitignore
# docs/.gitignore
_build/
*.pdf
*.tex
*.aux
*.log
*.out
*.toc
```

**4. Add Dependencies (Optional)**

For PDF generation, users need LaTeX:

```bash
# Ubuntu/Debian
sudo apt-get install texlive-latex-base texlive-latex-extra

# macOS
brew install --cask mactex

# Fedora
sudo dnf install texlive-scheme-basic
```

**5. Update Documentation**

Add to `docs/contributing/building-docs.md`:

````markdown
## Building Documentation

### HTML (Default)

```bash
make docs-html
# Output: docs/_build/html/index.html
````

### Man Pages

```bash
make docs-man
# Install: sudo cp docs/_build/man/nhl-scrabble.1 /usr/local/share/man/man1/
# View: man nhl-scrabble
```

### PDF

```bash
make docs-pdf
# Requires: pdflatex (texlive)
# Output: docs/_build/latex/nhl-scrabble.pdf
```

### Texinfo (GNU Info)

```bash
make docs-texinfo
# Install: sudo cp docs/_build/texinfo/nhl-scrabble.info /usr/local/share/info/
# View: info nhl-scrabble
```

### Plain Text

```bash
make docs-text
# Output: docs/_build/text/
```

### All Formats

```bash
make docs-all
```

````

**6. GitHub Actions CI Integration**

```yaml
# .github/workflows/docs.yml

name: Documentation

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          pip install -e ".[docs]"
          sudo apt-get install -y texlive-latex-base texlive-latex-extra

      - name: Build HTML docs
        run: make docs-html

      - name: Build man pages
        run: make docs-man

      - name: Build Texinfo
        run: make docs-texinfo

      - name: Build PDF
        run: make docs-pdf

      - name: Build text
        run: make docs-text

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: documentation
          path: docs/_build/
````

## Implementation Steps

1. **Update Sphinx Configuration** (30 min)

   - Add man_pages configuration
   - Add texinfo_documents configuration
   - Add latex_documents configuration
   - Add latex_elements styling
   - Add text output configuration

1. **Add Makefile Targets** (15 min)

   - Create docs-man target
   - Create docs-texinfo target
   - Create docs-pdf target
   - Create docs-text target
   - Create docs-all target
   - Update docs target help text

1. **Test Each Format** (45 min)

   - Test HTML build (existing)
   - Test man page build
   - Test Texinfo build
   - Test PDF build (requires LaTeX)
   - Test text build
   - Verify output quality

1. **Update Documentation** (30 min)

   - Add format descriptions to README
   - Create building-docs.md guide
   - Document LaTeX requirements
   - Add installation instructions
   - Add troubleshooting section

1. **Update CI/CD** (15 min)

   - Add LaTeX installation to CI
   - Add build steps for each format
   - Upload artifacts
   - Test CI pipeline

1. **Update .gitignore** (5 min)

   - Add \_build/ exclusions
   - Add LaTeX intermediate files
   - Keep build outputs local

## Testing Strategy

### Manual Testing

```bash
# Test each format individually
make docs-html
# Verify: Open docs/_build/html/index.html in browser

make docs-man
# Verify: man docs/_build/man/nhl-scrabble.1

make docs-texinfo
# Verify: info docs/_build/texinfo/nhl-scrabble.info

make docs-pdf
# Verify: Open docs/_build/latex/nhl-scrabble.pdf

make docs-text
# Verify: cat docs/_build/text/index.txt

# Test all formats together
make docs-all
# Verify: All formats build without errors
```

### Quality Checks

1. **Man Pages**:

   - Section headings formatted correctly
   - Synopsis matches actual CLI
   - Examples render properly
   - Cross-references work

1. **PDF**:

   - Table of contents generated
   - Images render correctly
   - Code blocks formatted properly
   - Page breaks appropriate

1. **Texinfo**:

   - Navigation structure correct
   - Menus generated properly
   - Cross-references work
   - Info reader compatible

1. **Text**:

   - Line wrapping appropriate
   - Section hierarchy clear
   - Code blocks readable
   - Tables formatted reasonably

### CI Testing

```bash
# Local CI simulation
tox -e docs

# Should build all formats and report any warnings/errors
```

## Acceptance Criteria

- [ ] Sphinx configured for 5 output formats (HTML, man, texinfo, PDF, text)
- [ ] Makefile targets for all formats
- [ ] `docs-html` builds HTML documentation
- [ ] `docs-man` builds Unix man pages
- [ ] `docs-texinfo` builds GNU Info format
- [ ] `docs-pdf` builds PDF via LaTeX
- [ ] `docs-text` builds plain text documentation
- [ ] `docs-all` builds all formats successfully
- [ ] Man pages install correctly (`sudo cp ... /usr/local/share/man/man1/`)
- [ ] PDF opens in PDF readers without errors
- [ ] Texinfo opens in Info readers without errors
- [ ] Text documentation is readable in terminal
- [ ] CI builds all formats successfully
- [ ] Documentation updated with build instructions
- [ ] LaTeX dependency documented (optional for PDF)
- [ ] All formats tested manually
- [ ] .gitignore excludes build artifacts

## Related Files

**Modified Files:**

- `docs/conf.py` - Add format-specific configurations
- `Makefile` - Add build targets for each format
- `docs/.gitignore` - Exclude build outputs
- `.github/workflows/docs.yml` - Build all formats in CI
- `docs/contributing/building-docs.md` - Document build process
- `README.md` - Mention multiple format support

**New Files:**

- None (build outputs are excluded from git)

## Dependencies

**Python Dependencies** (already installed):

- `sphinx>=7.0` - Documentation generator
- `sphinx-rtd-theme>=2.0` - Theme (HTML)

**System Dependencies** (optional, for PDF):

- `texlive-latex-base` - LaTeX base system
- `texlive-latex-extra` - Additional LaTeX packages
- `pdflatex` - PDF compiler

**No Python Task Dependencies** - Can implement independently

**Builds Upon**:

- enhancement/003-sphinx-documentation.md (COMPLETE ✅) - Sphinx infrastructure
- enhancement/005-sphinx-quality-plugins.md (COMPLETE ✅) - Quality checks

## Additional Notes

### Format Use Cases

**HTML** (existing):

- Primary web documentation
- GitHub Pages deployment
- Interactive navigation
- Search functionality

**Man Pages** (new):

- System documentation integration
- Terminal-based quick reference
- Unix/Linux user expectations
- Offline CLI help

**PDF** (new):

- Downloadable complete manual
- Offline reading
- Print-friendly format
- Professional appearance

**Texinfo** (new):

- Emacs documentation integration
- GNU Info system compatibility
- Hierarchical browsing
- Cross-reference navigation

**Plain Text** (new):

- Simplest offline format
- Terminal viewing without man
- Text editor compatible
- grep-able documentation

### LaTeX Dependency Considerations

**LaTeX is Optional**:

- Only needed for PDF generation
- HTML/man/texinfo/text work without LaTeX
- CI can build PDF (LaTeX installed)
- Local developers can skip PDF if needed

**LaTeX Installation Size**:

- Basic: ~200 MB (texlive-latex-base)
- Full: ~2-5 GB (texlive-full)
- Recommended: Basic + extra (~500 MB)

**Alternatives to LaTeX**:

- Could use `rinohtype` (pure Python PDF)
- Could use `rst2pdf` (simpler, limited features)
- LaTeX provides best quality and feature support

### Documentation Distribution

**Man Pages**:

```bash
# Install system-wide
sudo cp docs/_build/man/nhl-scrabble.1 /usr/local/share/man/man1/

# View
man nhl-scrabble
```

**Texinfo**:

```bash
# Install system-wide
sudo cp docs/_build/texinfo/nhl-scrabble.info /usr/local/share/info/

# Update info directory
sudo install-info /usr/local/share/info/nhl-scrabble.info /usr/local/share/info/dir

# View
info nhl-scrabble
```

**PDF**:

```bash
# Copy to standard location
cp docs/_build/latex/nhl-scrabble.pdf ~/Documents/

# Or include in package distribution
# Can upload to GitHub Releases
```

**Text**:

```bash
# View in terminal
less docs/_build/text/index.txt

# Or use any text editor
vim docs/_build/text/index.txt
```

### Sphinx Builder Details

**HTML Builder** (existing):

- Default Sphinx builder
- Feature-rich output
- Theme support (sphinx_rtd_theme)
- JavaScript interactivity

**Man Builder** (new):

- Generates groff man page source
- Section 1 (user commands)
- Standard man page formatting
- No installation required for build

**Texinfo Builder** (new):

- Generates GNU Texinfo source
- Compiles to .info format
- Used by Emacs Info mode
- Hierarchical documentation structure

**LaTeX/PDF Builder** (new):

- Generates LaTeX source (.tex)
- Requires pdflatex to compile to PDF
- High-quality typesetting
- Professional appearance

**Text Builder** (new):

- Simplest output format
- Plain text with basic formatting
- Line wrapping at 80 columns
- Section hierarchy with symbols

### CI/CD Considerations

**Build Time Impact**:

- HTML: ~10s (current)
- Man: ~5s (fast)
- Texinfo: ~5s (fast)
- PDF: ~30s (LaTeX compilation)
- Text: ~5s (fast)
- Total: ~55s (parallel possible)

**Artifact Storage**:

- HTML: ~5 MB
- Man: ~50 KB
- Texinfo: ~200 KB
- PDF: ~1-2 MB
- Text: ~100 KB
- Total: ~7-8 MB per build

**Recommendation**:

- Build all formats in CI for verification
- Only deploy HTML to GitHub Pages
- Provide other formats as release artifacts

### Performance Optimization

**Parallel Builds** (future enhancement):

```makefile
docs-all:
	$(MAKE) -j4 docs-html docs-man docs-texinfo docs-pdf docs-text
```

Benefits:

- 4x faster with parallel builds
- Total time: ~15s instead of ~55s
- CI runners have multiple cores

### Breaking Changes

**None** - This is purely additive:

- No changes to existing HTML documentation
- No changes to current build process
- New formats are optional
- Backwards compatible

### User Impact

**Positive**:

- More documentation distribution options
- Offline documentation access
- System-integrated man pages
- Professional PDF manual
- Flexible format choices

**Neutral**:

- No impact on users who only use HTML docs
- Optional LaTeX dependency for PDF
- Slightly larger artifact storage in CI

### Future Enhancements

After implementation:

- **EPUB Builder** - E-reader format
- **Singlehtml Builder** - One-page HTML
- **Linkcheck Builder** - Verify external links
- **Coverage Builder** - Docstring coverage report
- **Gettext Builder** - i18n/l10n support

### Documentation Best Practices

**Man Page Writing**:

- Keep synopsis accurate
- Include common examples
- Cross-reference related commands
- Follow man page conventions

**PDF Styling**:

- Consistent heading styles
- Appropriate page breaks
- Good table formatting
- Quality code syntax highlighting

**Texinfo Structure**:

- Clear menu hierarchy
- Meaningful node names
- Good cross-references
- Index entries

### Testing Checklist

- [ ] HTML builds without warnings
- [ ] Man page displays correctly with `man`
- [ ] Texinfo opens in `info` reader
- [ ] PDF compiles without LaTeX errors
- [ ] PDF opens in Adobe Reader/Evince/Preview
- [ ] Text documentation readable in terminal
- [ ] All formats contain complete content
- [ ] Code examples render correctly in all formats
- [ ] Tables format appropriately in each format
- [ ] Cross-references work in all formats
- [ ] Images display correctly (HTML/PDF)
- [ ] CI builds all formats successfully
- [ ] Artifacts upload to GitHub Actions
- [ ] No LaTeX warnings in PDF build
- [ ] Man page section numbering correct
- [ ] Texinfo menu structure logical

### Success Metrics

**Quantitative**:

- [ ] 5 output formats supported (HTML, man, texinfo, PDF, text)
- [ ] All formats build in \<60s total
- [ ] PDF under 3 MB
- [ ] Zero LaTeX errors
- [ ] CI passes with all formats

**Qualitative**:

- [ ] Man pages match Unix conventions
- [ ] PDF looks professional
- [ ] Texinfo navigation is intuitive
- [ ] Text documentation is readable
- [ ] Build process is documented

## Implementation Notes

*To be filled during implementation:*

- Actual LaTeX dependencies required
- PDF compilation time and optimization
- Man page section assignment decisions
- Texinfo menu structure choices
- Text formatting adjustments
- CI build time impact
- Artifact size measurements
- User feedback on formats
- Deviations from plan
- Actual effort vs estimated
