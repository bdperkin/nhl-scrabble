# Extend Sphinx Builder Functionality

**GitHub Issue**: [#331](https://github.com/bdperkin/nhl-scrabble/issues/331)

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

4-6 hours

## Description

Extend the NHL Scrabble documentation build system to support additional Sphinx builders beyond the currently implemented 6 formats (HTML, man pages, Texinfo, PDF/LaTeX, plain text, and AsciiDoc). Add support for additional Sphinx builders including EPUB, single-page HTML, directory-based HTML, JSON/pickle serialization, XML output, and gettext for internationalization.

This enhancement builds upon task enhancement/018 which added initial multi-format support.

## Current State

**Currently Implemented Documentation Formats** (from enhancement/018):

1. **HTML** (`html` builder) - Multi-page web documentation
1. **Man Pages** (`man` builder) - Unix man page format
1. **Texinfo** (`texinfo` builder) - GNU Info format
1. **PDF** (`latex` builder) - PDF via LaTeX compilation
1. **Plain Text** (`text` builder) - Simple text output
1. **AsciiDoc** (via pandoc) - AsciiDoc conversion (not a Sphinx builder)

**Current Makefile Structure**:

```makefile
docs-html: check-venv ## Build HTML documentation
	@cd docs && $(BIN)/sphinx-build -b html . _build/html

docs-man: check-venv ## Build man pages
	@cd docs && $(BIN)/sphinx-build -b man . _build/man

docs-texinfo: check-venv ## Build Texinfo documentation
	@cd docs && $(BIN)/sphinx-build -b texinfo . _build/texinfo

docs-pdf: check-venv ## Build PDF documentation (requires pdflatex)
	@cd docs && $(BIN)/sphinx-build -b latex . _build/latex
	@cd docs/_build/latex && $(MAKE) all-pdf

docs-text: check-venv ## Build plain text documentation
	@cd docs && $(BIN)/sphinx-build -b text . _build/text

docs-asciidoc: check-venv ## Build AsciiDoc documentation (requires pandoc)
	@cd docs && find . -name "*.rst" -type f ! -path "./_build/*" -exec sh -c 'pandoc -f rst -t asciidoc "{}" -o "_build/asciidoc/$$(basename {} .rst).adoc"' \;

docs-all: docs-html docs-man docs-texinfo docs-pdf docs-text docs-asciidoc
	@echo "All documentation formats built successfully!"
```

**Limitations**:

- No EPUB format for e-readers
- No single-page HTML for offline viewing
- No serialized formats (JSON/pickle) for programmatic access
- No XML output for integration with other tools
- No gettext support for internationalization
- No directory-based HTML (dirhtml) for cleaner URLs

## Proposed Solution

### Add 6 Additional Sphinx Builders

Implement support for the following additional Sphinx builders:

#### 1. EPUB Builder (`epub`)

E-book format for e-readers and mobile devices.

```python
# docs/conf.py additions
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright
epub_exclude_files = ['search.html']
epub_tocdepth = 3
```

```makefile
docs-epub: check-venv ## Build EPUB e-book documentation
	@printf "$(BLUE)Building EPUB documentation...$(NC)\n"
	@cd docs && $(BIN)/sphinx-build -b epub . _build/epub
	@printf "$(GREEN)✓ EPUB: docs/_build/epub/nhl-scrabble.epub$(NC)\n"
```

#### 2. Single-Page HTML Builder (`singlehtml`)

Single HTML file for offline viewing or printing.

```makefile
docs-singlehtml: check-venv ## Build single-page HTML documentation
	@printf "$(BLUE)Building single-page HTML documentation...$(NC)\n"
	@cd docs && $(BIN)/sphinx-build -b singlehtml . _build/singlehtml
	@printf "$(GREEN)✓ Single HTML: docs/_build/singlehtml/index.html$(NC)\n"
```

#### 3. Directory HTML Builder (`dirhtml`)

HTML output with directories for cleaner URLs (e.g., `/page/` instead of `/page.html`).

```makefile
docs-dirhtml: check-venv ## Build directory-based HTML documentation
	@printf "$(BLUE)Building directory HTML documentation...$(NC)\n"
	@cd docs && $(BIN)/sphinx-build -b dirhtml . _build/dirhtml
	@printf "$(GREEN)✓ Directory HTML: docs/_build/dirhtml/$(NC)\n"
```

#### 4. JSON Builder (`json`)

Serialized JSON format for programmatic access to documentation.

```makefile
docs-json: check-venv ## Build JSON documentation
	@printf "$(BLUE)Building JSON documentation...$(NC)\n"
	@cd docs && $(BIN)/sphinx-build -b json . _build/json
	@printf "$(GREEN)✓ JSON: docs/_build/json/$(NC)\n"
```

#### 5. XML Builder (`xml`)

XML output for integration with other documentation tools.

```makefile
docs-xml: check-venv ## Build XML documentation
	@printf "$(BLUE)Building XML documentation...$(NC)\n"
	@cd docs && $(BIN)/sphinx-build -b xml . _build/xml
	@printf "$(GREEN)✓ XML: docs/_build/xml/$(NC)\n"
```

#### 6. Gettext Builder (`gettext`)

Extract translatable messages for internationalization.

```makefile
docs-gettext: check-venv ## Extract translatable messages (i18n)
	@printf "$(BLUE)Extracting translatable messages...$(NC)\n"
	@cd docs && $(BIN)/sphinx-build -b gettext . _build/gettext
	@printf "$(GREEN)✓ Gettext: docs/_build/gettext/$(NC)\n"
```

### Update Configuration

```python
# docs/conf.py additions

# EPUB configuration
epub_title = project
epub_author = author
epub_publisher = "Brandon Perkins"
epub_copyright = copyright
epub_exclude_files = ['search.html']
epub_tocdepth = 3
epub_tocdup = True
epub_show_urls = 'footnote'
epub_use_index = True

# Gettext configuration (for i18n)
gettext_compact = False
gettext_uuid = True
gettext_location = True
gettext_auto_build = True
```

### Update .gitignore

```gitignore
# docs/.gitignore additions

# EPUB build artifacts
*.epub

# JSON/XML artifacts
*.json
*.xml

# Gettext artifacts
*.pot
*.po
*.mo
```

### Update Documentation

Add section to `docs/how-to/build-documentation.md`:

````markdown
### EPUB E-Book

Build EPUB format for e-readers:

```bash
make docs-epub
````

Output: `docs/_build/epub/nhl-scrabble.epub`

**Compatible with:**

- Amazon Kindle (via conversion)
- Apple Books
- Google Play Books
- Adobe Digital Editions
- Most e-reader apps

### Single-Page HTML

Build entire documentation as single HTML file:

```bash
make docs-singlehtml
```

Output: `docs/_build/singlehtml/index.html`

**Use cases:**

- Offline viewing
- Printing entire documentation
- PDF conversion via browser
- Email distribution

### Directory HTML

Build HTML with directory structure for cleaner URLs:

```bash
make docs-dirhtml
```

Output: `docs/_build/dirhtml/`

**Benefits:**

- URLs like `/installation/` instead of `/installation.html`
- Better for web servers
- Cleaner URL structure

### JSON Documentation

Build serialized JSON format:

```bash
make docs-json
```

Output: `docs/_build/json/`

**Use cases:**

- Programmatic documentation access
- Search index generation
- Documentation analysis tools

### XML Documentation

Build XML format:

```bash
make docs-xml
```

Output: `docs/_build/xml/`

**Use cases:**

- Integration with other tools
- XSLT transformations
- Documentation processing pipelines

### Gettext (i18n)

Extract translatable messages for internationalization:

```bash
make docs-gettext
```

Output: `docs/_build/gettext/`

**Use cases:**

- Preparing documentation for translation
- Multi-language documentation
- Localization workflows

````

## Implementation Steps

1. **Update docs/conf.py** (30 min)
   - Add EPUB configuration section
   - Add gettext configuration section
   - Verify all builders have necessary settings

2. **Add Makefile Targets** (30 min)
   - Add `docs-epub` target
   - Add `docs-singlehtml` target
   - Add `docs-dirhtml` target
   - Add `docs-json` target
   - Add `docs-xml` target
   - Add `docs-gettext` target
   - Update `docs-all` target to include new builders
   - Update `.PHONY` declaration

3. **Update docs/.gitignore** (10 min)
   - Add `*.epub` exclusion
   - Add `*.json` exclusion (if not already present)
   - Add `*.xml` exclusion (if not already present)
   - Add `*.pot`, `*.po`, `*.mo` exclusions

4. **Test Each Builder** (90 min)
   - Test EPUB build and verify output opens in e-reader
   - Test singlehtml build and verify completeness
   - Test dirhtml build and verify directory structure
   - Test JSON build and verify format
   - Test XML build and verify validity
   - Test gettext build and verify message extraction

5. **Add Tests** (60 min)
   - Add test for EPUB build in `tests/test_docs_builds.py`
   - Add test for singlehtml build
   - Add test for dirhtml build
   - Add test for JSON build
   - Add test for XML build
   - Add test for gettext build
   - Update Makefile target verification test
   - Update .gitignore verification test

6. **Update Documentation** (60 min)
   - Update `docs/how-to/build-documentation.md` with new formats
   - Add installation instructions if needed
   - Add usage examples for each format
   - Add troubleshooting section
   - Update `CLAUDE.md` with new builders

7. **Update docs-all Target** (10 min)
   - Update to include all new builders
   - Update total time estimate
   - Document build order

## Testing Strategy

### Unit Tests

Add tests to `tests/test_docs_builds.py`:

```python
@pytest.mark.skipif(
    shutil.which("sphinx-build") is None,
    reason="sphinx-build not found (docs dependencies not installed)",
)
def test_epub_build(self):
    """Test EPUB documentation build."""
    result = subprocess.run(  # noqa: S603
        [  # noqa: S607
            "sphinx-build",
            "-b",
            "epub",
            str(PROJECT_ROOT / "docs"),
            str(PROJECT_ROOT / "docs" / "_build" / "epub"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, f"EPUB build failed: {result.stderr}"

    # Verify EPUB file exists
    epub_file = PROJECT_ROOT / "docs" / "_build" / "epub" / "nhl-scrabble.epub"
    assert epub_file.exists(), "nhl-scrabble.epub not created"
    assert epub_file.stat().st_size > 0, "nhl-scrabble.epub is empty"

def test_singlehtml_build(self):
    """Test single-page HTML documentation build."""
    result = subprocess.run(  # noqa: S603
        [  # noqa: S607
            "sphinx-build",
            "-b",
            "singlehtml",
            str(PROJECT_ROOT / "docs"),
            str(PROJECT_ROOT / "docs" / "_build" / "singlehtml"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, f"Singlehtml build failed: {result.stderr}"

    # Verify index.html exists and is substantial
    index_html = PROJECT_ROOT / "docs" / "_build" / "singlehtml" / "index.html"
    assert index_html.exists(), "index.html not created"
    assert index_html.stat().st_size > 100000, "index.html too small (expected single-page)"

def test_dirhtml_build(self):
    """Test directory HTML documentation build."""
    result = subprocess.run(  # noqa: S603
        [  # noqa: S607
            "sphinx-build",
            "-b",
            "dirhtml",
            str(PROJECT_ROOT / "docs"),
            str(PROJECT_ROOT / "docs" / "_build" / "dirhtml"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, f"Dirhtml build failed: {result.stderr}"

    # Verify directory structure exists
    dirhtml_dir = PROJECT_ROOT / "docs" / "_build" / "dirhtml"
    assert dirhtml_dir.exists(), "dirhtml directory not created"
    assert (dirhtml_dir / "index.html").exists(), "index.html not created"

def test_json_build(self):
    """Test JSON documentation build."""
    result = subprocess.run(  # noqa: S603
        [  # noqa: S607
            "sphinx-build",
            "-b",
            "json",
            str(PROJECT_ROOT / "docs"),
            str(PROJECT_ROOT / "docs" / "_build" / "json"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, f"JSON build failed: {result.stderr}"

    # Verify JSON files exist
    json_dir = PROJECT_ROOT / "docs" / "_build" / "json"
    assert json_dir.exists(), "json directory not created"
    json_files = list(json_dir.glob("*.fjson"))
    assert len(json_files) > 0, "No JSON files created"

def test_xml_build(self):
    """Test XML documentation build."""
    result = subprocess.run(  # noqa: S603
        [  # noqa: S607
            "sphinx-build",
            "-b",
            "xml",
            str(PROJECT_ROOT / "docs"),
            str(PROJECT_ROOT / "docs" / "_build" / "xml"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, f"XML build failed: {result.stderr}"

    # Verify XML files exist
    xml_dir = PROJECT_ROOT / "docs" / "_build" / "xml"
    assert xml_dir.exists(), "xml directory not created"
    xml_files = list(xml_dir.glob("*.xml"))
    assert len(xml_files) > 0, "No XML files created"

def test_gettext_build(self):
    """Test gettext message extraction."""
    result = subprocess.run(  # noqa: S603
        [  # noqa: S607
            "sphinx-build",
            "-b",
            "gettext",
            str(PROJECT_ROOT / "docs"),
            str(PROJECT_ROOT / "docs" / "_build" / "gettext"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, f"Gettext build failed: {result.stderr}"

    # Verify .pot files exist
    gettext_dir = PROJECT_ROOT / "docs" / "_build" / "gettext"
    assert gettext_dir.exists(), "gettext directory not created"
    pot_files = list(gettext_dir.glob("*.pot"))
    assert len(pot_files) > 0, "No .pot files created"
````

### Manual Testing

```bash
# Test each format manually
make docs-epub
# Open docs/_build/epub/nhl-scrabble.epub in an e-reader

make docs-singlehtml
# Open docs/_build/singlehtml/index.html in browser and verify all content present

make docs-dirhtml
# Verify directory structure and navigation works

make docs-json
# Verify JSON files are valid: cat docs/_build/json/index.fjson | jq .

make docs-xml
# Verify XML is valid: xmllint docs/_build/xml/index.xml

make docs-gettext
# Verify .pot files extracted: ls docs/_build/gettext/

# Test all formats together
make docs-all
```

## Acceptance Criteria

- [x] EPUB builder configured in docs/conf.py
- [x] `docs-epub` Makefile target builds EPUB format
- [x] `docs-singlehtml` Makefile target builds single-page HTML
- [x] `docs-dirhtml` Makefile target builds directory HTML
- [x] `docs-json` Makefile target builds JSON format
- [x] `docs-xml` Makefile target builds XML format
- [x] `docs-gettext` Makefile target extracts messages
- [x] `docs-all` target includes all 12 builders
- [x] Tests added for all 6 new builders
- [x] .gitignore excludes all build artifacts
- [x] Documentation updated in build-documentation.md
- [x] CLAUDE.md updated with new builders
- [x] All tests pass locally
- [x] EPUB file opens in e-reader apps
- [x] Single-page HTML contains all documentation
- [x] Directory HTML has proper structure
- [x] JSON files are valid JSON
- [x] XML files are valid XML
- [x] Gettext extracts translatable messages

## Related Files

**Modified Files:**

- `docs/conf.py` - Add EPUB and gettext configuration
- `Makefile` - Add 6 new docs-\* targets, update docs-all
- `docs/.gitignore` - Add EPUB, JSON, XML, gettext exclusions
- `docs/how-to/build-documentation.md` - Document new builders
- `CLAUDE.md` - Update documentation formats section
- `tests/test_docs_builds.py` - Add tests for 6 new builders

**No New Files Required**

## Dependencies

**Python Dependencies** (already installed):

- `sphinx>=7.0` - All builders are built-in to Sphinx
- No additional packages needed

**System Dependencies**:

- None - all builders are pure Python

**Task Dependencies**:

- enhancement/018-sphinx-additional-formats.md (COMPLETE ✅) - Initial multi-format support

**Builds Upon**:

- enhancement/018 established the multi-format pattern
- This task extends it with additional Sphinx builders

## Additional Notes

### Format Use Cases

**EPUB**:

- E-reader distribution (Kindle, Kobo, etc.)
- Mobile documentation apps
- Offline reading on tablets
- Professional e-book publishing

**Single-Page HTML**:

- Offline documentation archives
- PDF conversion via browser print
- Email-friendly distribution
- Self-contained documentation

**Directory HTML**:

- Better SEO with clean URLs
- Web server deployment
- Consistent URL structure
- No .html extensions

**JSON**:

- Search engine indexing
- Documentation analysis tools
- Programmatic access to content
- API documentation generation

**XML**:

- XSLT transformations
- Integration with DocBook
- Documentation pipelines
- Other tool consumption

**Gettext**:

- Internationalization preparation
- Multi-language documentation
- Translation workflows
- Localization projects

### Performance Considerations

**Build Times** (estimated):

- EPUB: ~10-15s (needs to package files)
- Singlehtml: ~15-20s (generates large file)
- Dirhtml: ~10s (similar to HTML)
- JSON: ~8s (fast, simple format)
- XML: ~8s (fast, simple format)
- Gettext: ~5s (fast, message extraction only)
- Total additional time: ~60s

**With all 12 builders** (6 existing + 6 new):

- Sequential: ~2 minutes total
- Could be parallelized to ~30-40s

**Artifact Sizes** (estimated):

- EPUB: ~1-2 MB (compressed)
- Singlehtml: ~500 KB - 1 MB (large HTML file)
- Dirhtml: ~5-10 MB (similar to HTML)
- JSON: ~2-3 MB (verbose format)
- XML: ~3-4 MB (verbose format)
- Gettext: ~100-200 KB (message catalogs)

### Breaking Changes

**None** - All changes are additive:

- No changes to existing builders
- No changes to existing documentation
- New targets are optional
- Fully backwards compatible

### Comparison to Enhancement/018

Enhancement/018 added 5 Sphinx builders + 1 pandoc conversion:

- HTML, man, texinfo, PDF/LaTeX, text (Sphinx builders)
- AsciiDoc (pandoc conversion)

This task adds 6 more Sphinx builders:

- EPUB, singlehtml, dirhtml, JSON, XML, gettext

**Total after both tasks**: 11 Sphinx builders + 1 pandoc conversion = 12 formats

### Why These Builders?

**EPUB** - Most requested e-book format, supported by all major platforms

**Singlehtml** - Common request for offline/printable documentation

**Dirhtml** - Modern web best practice for clean URLs

**JSON** - Enables programmatic documentation access and tooling

**XML** - Industry standard for documentation interchange

**Gettext** - Standard i18n tool, enables future localization

### Not Included

**Excluded Builders** (can be added in future tasks if needed):

- `pickle` - Python-specific serialization, similar to JSON
- `pseudoxml` - Debugging tool, not user-facing
- `linkcheck` - We already have this as `docs-linkcheck`
- `coverage` - We already have this as `docs-coverage`
- `changes` - Requires changelog directives in RST files
- `dummy` - No output, testing only

### Future Enhancements

After this task:

- Task for EPUB styling/theming
- Task for multi-language documentation using gettext
- Task for parallel documentation builds
- Task for documentation deployment automation

### Documentation Best Practices

**EPUB**:

- Keep image sizes reasonable
- Test on multiple e-readers
- Validate with epubcheck
- Provide table of contents

**Singlehtml**:

- Monitor file size
- Test load time in browsers
- Consider split if too large
- Include navigation aids

**Dirhtml**:

- Test with web server
- Verify URL structure
- Check cross-references
- Test 404 handling

### Success Metrics

**Quantitative**:

- [ ] 6 new builders successfully building
- [ ] 12 total formats supported
- [ ] All tests passing (16 builder tests total)
- [ ] Build time under 2 minutes for docs-all
- [ ] Zero build errors or warnings

**Qualitative**:

- [ ] EPUB readable on Kindle/Apple Books
- [ ] Singlehtml contains all content
- [ ] Dirhtml URLs are clean and logical
- [ ] JSON is valid and parseable
- [ ] XML is valid and well-formed
- [ ] Gettext extracts all translatable strings

## Implementation Notes

*To be filled during implementation:*

- Actual build times for each format
- EPUB file size and compatibility testing results
- JSON/XML structure analysis
- Gettext message count and coverage
- Challenges encountered
- Deviations from plan
- Actual effort vs estimated
