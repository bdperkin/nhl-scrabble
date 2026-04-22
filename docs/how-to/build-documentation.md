# Build Documentation in Multiple Formats

This guide explains how to build NHL Scrabble documentation in various output formats.

## Overview

The project uses Sphinx to generate documentation in multiple formats:

- **HTML** - Web documentation (default, deployed to GitHub Pages)
- **Man Pages** - Unix man page format for terminal viewing
- **Texinfo** - GNU Info format for Emacs/Info readers
- **PDF** - Portable document format via LaTeX (requires additional tools)
- **Plain Text** - Simple text-only format

## Quick Start

```bash
# Build all formats
make docs-all

# Build specific format
make docs-html     # HTML only
make docs-man      # Man pages only
make docs-pdf      # PDF only (requires LaTeX)
```

## Building Each Format

### HTML Documentation

Build web-friendly HTML documentation:

```bash
make docs-html
```

Output: `docs/_build/html/index.html`

**View locally:**

```bash
# Open in browser
open docs/_build/html/index.html  # macOS
xdg-open docs/_build/html/index.html  # Linux
start docs/_build/html/index.html  # Windows

# Or serve with live reload
make serve-docs  # http://localhost:8000
```

### Man Pages

Build Unix man page documentation:

```bash
make docs-man
```

Output: `docs/_build/man/nhl-scrabble.1`

**View locally:**

```bash
# View directly
man docs/_build/man/nhl-scrabble.1

# Or install system-wide (requires sudo)
sudo cp docs/_build/man/nhl-scrabble.1 /usr/local/share/man/man1/
man nhl-scrabble
```

### Texinfo (GNU Info)

Build GNU Info format documentation:

```bash
make docs-texinfo
```

Output: `docs/_build/texinfo/nhl-scrabble.texi`

**View locally:**

```bash
# View Texinfo source
less docs/_build/texinfo/nhl-scrabble.texi

# Or compile to Info format and install (requires makeinfo)
cd docs/_build/texinfo
makeinfo nhl-scrabble.texi -o nhl-scrabble.info
sudo cp nhl-scrabble.info /usr/local/share/info/
sudo install-info /usr/local/share/info/nhl-scrabble.info /usr/local/share/info/dir
info nhl-scrabble
```

### PDF Documentation

Build PDF documentation via LaTeX:

```bash
make docs-pdf
```

Output: `docs/_build/latex/nhl-scrabble.pdf`

**Requirements:**

- `pdflatex` (from TeX Live or similar LaTeX distribution)
- LaTeX packages: `texlive-latex-base`, `texlive-latex-extra`

**Install LaTeX:**

```bash
# Ubuntu/Debian
sudo apt-get install texlive-latex-base texlive-latex-extra

# macOS
brew install --cask mactex

# Fedora/RHEL
sudo dnf install texlive-scheme-basic texlive-latex-extra
```

**Known Limitations:**

- PDF build may fail if documentation contains SVG images (LaTeX requires PNG/PDF)
- Requires ~500 MB disk space for LaTeX installation
- Compilation can be slow (~30-60 seconds)

**If PDF build fails:**

```bash
# Check LaTeX logs
cat docs/_build/latex/nhl-scrabble.log

# Common issues:
# - SVG images not supported: Convert to PNG or PDF
# - Missing packages: Install texlive-latex-extra
# - Compilation errors: Check .log file for details
```

### Plain Text

Build plain text documentation:

```bash
make docs-text
```

Output: `docs/_build/text/`

**View locally:**

```bash
# View index
less docs/_build/text/index.txt

# View specific page
less docs/_build/text/how-to/build-documentation.txt

# Or use any text editor
vim docs/_build/text/index.txt
```

## Building All Formats

Build all documentation formats at once:

```bash
make docs-all
```

This runs all individual build targets in sequence:

1. HTML documentation
1. Man pages
1. Texinfo
1. PDF (if LaTeX available)
1. Plain text

**Output locations:**

```
docs/_build/
├── html/              # HTML documentation
│   └── index.html
├── man/               # Man pages
│   └── nhl-scrabble.1
├── texinfo/           # Texinfo source
│   └── nhl-scrabble.texi
├── latex/             # LaTeX source & PDF
│   ├── nhl-scrabble.tex
│   └── nhl-scrabble.pdf
└── text/              # Plain text
    └── index.txt
```

## Advanced Usage

### Custom Sphinx Options

Pass custom options to sphinx-build:

```bash
# Build with specific Sphinx options
cd docs
sphinx-build -b html -W --keep-going . _build/html
```

**Useful options:**

- `-W` - Treat warnings as errors
- `-n` - Run in nit-picky mode (warn about all references)
- `-q` - Quiet mode (only errors)
- `-v` - Verbose mode (more output)
- `-j auto` - Parallel build (uses all CPU cores)

### Incremental Builds

Sphinx builds incrementally by default (only rebuilds changed files):

```bash
# Incremental build (fast)
make docs-html

# Force complete rebuild
rm -rf docs/_build/html
make docs-html
```

### Clean Build Artifacts

Clean all build artifacts:

```bash
# Clean all formats
rm -rf docs/_build

# Clean specific format
rm -rf docs/_build/html
rm -rf docs/_build/latex
```

**Note:** `docs/_build/` is excluded from git via `docs/.gitignore`

## Troubleshooting

### Sphinx Not Found

**Error:** `sphinx-build: command not found`

**Solution:**

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Or with make
make install-dev
```

### PDF Build Fails

**Error:** `make: *** [Makefile:29: nhl-scrabble.pdf] Error 12`

**Common causes:**

1. **LaTeX not installed:**

   ```bash
   # Check if pdflatex is available
   which pdflatex

   # If not found, install LaTeX
   sudo apt-get install texlive-latex-base texlive-latex-extra
   ```

1. **SVG images not supported:**

   - LaTeX cannot process SVG images
   - Badges and logos must be PNG or PDF format
   - This is a known limitation
   - Alternative: Use `rst2pdf` (pure Python, limited features)

1. **Missing LaTeX packages:**

   ```bash
   # Check LaTeX log for missing packages
   cat docs/_build/latex/nhl-scrabble.log | grep "! LaTeX Error"

   # Install additional packages
   sudo apt-get install texlive-latex-extra
   ```

### Warnings During Build

Sphinx may show warnings for:

- Broken cross-references
- Missing documents
- Deprecated syntax

**View warnings:**

```bash
# Build with warnings visible
make docs-html 2>&1 | grep WARNING
```

**Common warnings:**

- `WARNING: unknown document` - Broken link to non-existent page
- `WARNING: duplicate object description` - Duplicate API documentation
- `WARNING: toctree contains reference to nonexisting document` - Missing page in table of contents

### Build Performance

**Slow builds:**

```bash
# Use parallel building
cd docs
sphinx-build -b html -j auto . _build/html

# Or clean build cache
rm -rf docs/_build/doctrees
```

**Large build artifacts:**

- HTML: ~5-10 MB
- Man: ~50-100 KB
- Texinfo: ~200-500 KB
- PDF: ~1-3 MB
- Text: ~100-200 KB

## CI/CD Integration

Documentation is built automatically in CI:

```yaml
# .github/workflows/docs.yml

- name: Build all formats
  run: |
    make docs-html
    make docs-man
    make docs-texinfo
    make docs-text
    # PDF build optional (may fail on CI)
```

**GitHub Pages:**

- Only HTML documentation is deployed to GitHub Pages
- Other formats are available as CI artifacts
- PDF can be attached to GitHub Releases

## Distribution

### Installing Man Pages

System-wide installation:

```bash
# Install man page
sudo cp docs/_build/man/nhl-scrabble.1 /usr/local/share/man/man1/

# Update man database
sudo mandb

# View
man nhl-scrabble
```

User-only installation:

```bash
# Create user man directory
mkdir -p ~/.local/share/man/man1

# Copy man page
cp docs/_build/man/nhl-scrabble.1 ~/.local/share/man/man1/

# Add to MANPATH
echo 'export MANPATH="$HOME/.local/share/man:$MANPATH"' >> ~/.bashrc
source ~/.bashrc

# View
man nhl-scrabble
```

### Installing Texinfo

System-wide installation:

```bash
# Compile and install
cd docs/_build/texinfo
makeinfo nhl-scrabble.texi -o nhl-scrabble.info
sudo cp nhl-scrabble.info /usr/local/share/info/

# Update info directory
sudo install-info /usr/local/share/info/nhl-scrabble.info /usr/local/share/info/dir

# View
info nhl-scrabble
```

### Distributing PDF

Include PDF in package distribution:

```bash
# Build PDF
make docs-pdf

# Copy to distribution
cp docs/_build/latex/nhl-scrabble.pdf dist/

# Or upload to GitHub Releases
gh release upload v2.0.0 docs/_build/latex/nhl-scrabble.pdf
```

## Configuration

Documentation format settings are in `docs/conf.py`:

```python
# Man page configuration
man_pages = [
    ("index", "nhl-scrabble", "NHL Scrabble Documentation", ["Brandon Perkins"], 1),
]

# Texinfo configuration
texinfo_documents = [
    (
        "index",
        "nhl-scrabble",
        "NHL Scrabble Documentation",
        "Brandon Perkins",
        "nhl-scrabble",
        "NHL player name Scrabble scoring system",
        "Miscellaneous",
    ),
]

# LaTeX/PDF configuration
latex_documents = [
    ("index", "nhl-scrabble.tex", "NHL Scrabble Documentation", "Brandon Perkins", "manual"),
]

# Text output configuration
text_newlines = "unix"
text_sectionchars = '*=-~"+`'
```

## Best Practices

1. **Always build HTML** - Primary documentation format
1. **Test man pages** - View with `man` before installing
1. **PDF is optional** - LaTeX dependency may not be available everywhere
1. **Use make targets** - Consistent build commands across environments
1. **Check warnings** - Fix broken links and missing documents
1. **Clean before release** - `rm -rf docs/_build && make docs-all`

## Related Documentation

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [Makefile Reference](../reference/makefile.md)
- [Contributing Guide](../../CONTRIBUTING.md)

## See Also

- `make help` - All available make targets
- `make docs-quality` - Documentation quality checks
- `make serve-docs` - Local documentation server
