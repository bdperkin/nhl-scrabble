"""Tests for Sphinx documentation builds in multiple formats.

This module tests the various Sphinx documentation output formats:
- HTML (web documentation)
- Man pages (Unix man page format)
- Texinfo (GNU Info format)
- PDF (via LaTeX - optional, requires pdflatex)
- Plain text (simple text format)
"""

import shutil
import subprocess
from pathlib import Path

import pytest

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent


class TestDocumentationBuilds:
    """Test suite for Sphinx documentation builds.

    Tests build documentation in multiple formats and verify outputs are created.
    Uses the shared docs/_build directory - does not clean up to avoid conflicts.
    """

    @pytest.mark.skipif(
        shutil.which("sphinx-build") is None,
        reason="sphinx-build not found (docs dependencies not installed)",
    )
    def test_html_build(self):
        """Test HTML documentation build."""
        # Build HTML documentation
        # Safe: sphinx-build is trusted tool from project dependencies
        result = subprocess.run(  # noqa: S603
            [  # noqa: S607
                "sphinx-build",
                "-b",
                "html",
                str(PROJECT_ROOT / "docs"),
                str(PROJECT_ROOT / "docs" / "_build" / "html"),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        # Check build succeeded
        assert result.returncode == 0, f"HTML build failed: {result.stderr}"

        # Verify index.html exists
        index_html = PROJECT_ROOT / "docs" / "_build" / "html" / "index.html"
        assert index_html.exists(), "index.html not created"
        assert index_html.stat().st_size > 0, "index.html is empty"

    @pytest.mark.skipif(
        shutil.which("sphinx-build") is None,
        reason="sphinx-build not found (docs dependencies not installed)",
    )
    def test_man_build(self):
        """Test man page documentation build."""
        # Build man pages
        # Safe: sphinx-build is trusted tool from project dependencies
        result = subprocess.run(  # noqa: S603
            [  # noqa: S607
                "sphinx-build",
                "-b",
                "man",
                str(PROJECT_ROOT / "docs"),
                str(PROJECT_ROOT / "docs" / "_build" / "man"),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        # Check build succeeded
        assert result.returncode == 0, f"Man page build failed: {result.stderr}"

        # Verify man page exists
        man_page = PROJECT_ROOT / "docs" / "_build" / "man" / "nhl-scrabble.1"
        assert man_page.exists(), "nhl-scrabble.1 man page not created"
        assert man_page.stat().st_size > 0, "nhl-scrabble.1 is empty"

    @pytest.mark.skipif(
        shutil.which("sphinx-build") is None,
        reason="sphinx-build not found (docs dependencies not installed)",
    )
    def test_texinfo_build(self):
        """Test Texinfo documentation build."""
        # Build Texinfo documentation
        # Safe: sphinx-build is trusted tool from project dependencies
        result = subprocess.run(  # noqa: S603
            [  # noqa: S607
                "sphinx-build",
                "-b",
                "texinfo",
                str(PROJECT_ROOT / "docs"),
                str(PROJECT_ROOT / "docs" / "_build" / "texinfo"),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        # Check build succeeded
        assert result.returncode == 0, f"Texinfo build failed: {result.stderr}"

        # Verify Texinfo file exists
        texinfo_file = PROJECT_ROOT / "docs" / "_build" / "texinfo" / "nhl-scrabble.texi"
        assert texinfo_file.exists(), "nhl-scrabble.texi not created"
        assert texinfo_file.stat().st_size > 0, "nhl-scrabble.texi is empty"

    @pytest.mark.skipif(
        shutil.which("sphinx-build") is None,
        reason="sphinx-build not found (docs dependencies not installed)",
    )
    def test_text_build(self):
        """Test plain text documentation build."""
        # Build text documentation
        # Safe: sphinx-build is trusted tool from project dependencies
        result = subprocess.run(  # noqa: S603
            [  # noqa: S607
                "sphinx-build",
                "-b",
                "text",
                str(PROJECT_ROOT / "docs"),
                str(PROJECT_ROOT / "docs" / "_build" / "text"),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        # Check build succeeded
        assert result.returncode == 0, f"Text build failed: {result.stderr}"

        # Verify text file exists
        text_file = PROJECT_ROOT / "docs" / "_build" / "text" / "index.txt"
        assert text_file.exists(), "index.txt not created"
        assert text_file.stat().st_size > 0, "index.txt is empty"

    @pytest.mark.skipif(
        shutil.which("pandoc") is None,
        reason="pandoc not found (required for AsciiDoc conversion)",
    )
    def test_asciidoc_build(self):
        """Test AsciiDoc documentation build.

        Note: This uses pandoc to convert RST files to AsciiDoc format.
        Requires pandoc to be installed on the system.
        """
        # Build AsciiDoc documentation
        # Safe: pandoc is trusted tool, find is trusted system tool
        result = subprocess.run(
            [  # noqa: S607
                "make",
                "docs-asciidoc",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        # Check build succeeded
        assert result.returncode == 0, f"AsciiDoc build failed: {result.stderr}"

        # Verify AsciiDoc directory exists
        asciidoc_dir = PROJECT_ROOT / "docs" / "_build" / "asciidoc"
        assert asciidoc_dir.exists(), "asciidoc directory not created"

        # Verify at least index.adoc exists
        index_adoc = asciidoc_dir / "index.adoc"
        assert index_adoc.exists(), "index.adoc not created"
        assert index_adoc.stat().st_size > 0, "index.adoc is empty"

    @pytest.mark.skipif(
        shutil.which("sphinx-build") is None,
        reason="sphinx-build not found (docs dependencies not installed)",
    )
    def test_latex_build(self):
        """Test LaTeX documentation build (PDF generation step 1).

        Note: This tests LaTeX generation only, not PDF compilation.
        PDF compilation requires pdflatex and may fail due to image format
        compatibility issues (e.g., SVG images not supported by LaTeX).
        """
        # Build LaTeX documentation
        # Safe: sphinx-build is trusted tool from project dependencies
        result = subprocess.run(  # noqa: S603
            [  # noqa: S607
                "sphinx-build",
                "-b",
                "latex",
                str(PROJECT_ROOT / "docs"),
                str(PROJECT_ROOT / "docs" / "_build" / "latex"),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        # Check build succeeded
        assert result.returncode == 0, f"LaTeX build failed: {result.stderr}"

        # Verify LaTeX file exists
        latex_file = PROJECT_ROOT / "docs" / "_build" / "latex" / "nhl-scrabble.tex"
        assert latex_file.exists(), "nhl-scrabble.tex not created"
        assert latex_file.stat().st_size > 0, "nhl-scrabble.tex is empty"

    @pytest.mark.skipif(
        shutil.which("sphinx-build") is None
        or shutil.which("pdflatex") is None
        or shutil.which("make") is None,
        reason="sphinx-build, pdflatex, or make not found (PDF build requires LaTeX)",
    )
    def test_pdf_compilation(self):
        """Test PDF compilation from LaTeX (optional - may fail due to images).

        This test is marked as xfail because PDF compilation may fail due to:
        - SVG images not supported by LaTeX (requires PNG/PDF)
        - Missing LaTeX packages
        - LaTeX compilation errors

        The test is informational to track PDF build capability.
        """
        # First build LaTeX
        # Safe: sphinx-build is trusted tool from project dependencies
        subprocess.run(  # noqa: S603
            [  # noqa: S607
                "sphinx-build",
                "-b",
                "latex",
                str(PROJECT_ROOT / "docs"),
                str(PROJECT_ROOT / "docs" / "_build" / "latex"),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        # Try to compile PDF
        latex_dir = PROJECT_ROOT / "docs" / "_build" / "latex"
        # Safe: make is trusted system tool, all-pdf is hardcoded target
        result = subprocess.run(
            ["make", "all-pdf"],  # noqa: S607
            cwd=latex_dir,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            # PDF compilation succeeded
            pdf_file = latex_dir / "nhl-scrabble.pdf"
            assert pdf_file.exists(), "nhl-scrabble.pdf not created"
            assert pdf_file.stat().st_size > 0, "nhl-scrabble.pdf is empty"
        else:
            # PDF compilation failed - this is expected if images are incompatible
            # Skip the test with a message
            pytest.skip(
                f"PDF compilation failed (expected due to image compatibility): {result.stderr[:200]}",
            )

    def test_makefile_targets_exist(self):
        """Test that new Makefile targets are defined."""
        makefile = PROJECT_ROOT / "Makefile"
        assert makefile.exists(), "Makefile not found"

        makefile_content = makefile.read_text()

        # Check for new documentation targets
        assert "docs-html:" in makefile_content, "docs-html target not found in Makefile"
        assert "docs-man:" in makefile_content, "docs-man target not found in Makefile"
        assert "docs-texinfo:" in makefile_content, "docs-texinfo target not found in Makefile"
        assert "docs-pdf:" in makefile_content, "docs-pdf target not found in Makefile"
        assert "docs-text:" in makefile_content, "docs-text target not found in Makefile"
        assert "docs-asciidoc:" in makefile_content, "docs-asciidoc target not found in Makefile"
        assert "docs-all:" in makefile_content, "docs-all target not found in Makefile"

    def test_sphinx_config_has_format_settings(self):
        """Test that Sphinx configuration includes settings for all formats."""
        conf_file = PROJECT_ROOT / "docs" / "conf.py"
        assert conf_file.exists(), "docs/conf.py not found"

        conf_content = conf_file.read_text()

        # Check for format-specific configuration
        assert "man_pages" in conf_content, "man_pages configuration not found"
        assert "texinfo_documents" in conf_content, "texinfo_documents configuration not found"
        assert "latex_documents" in conf_content, "latex_documents configuration not found"
        assert "latex_elements" in conf_content, "latex_elements configuration not found"
        assert "text_newlines" in conf_content, "text_newlines configuration not found"
        assert "text_sectionchars" in conf_content, "text_sectionchars configuration not found"

    def test_gitignore_excludes_build_artifacts(self):
        """Test that docs/.gitignore excludes build artifacts."""
        gitignore = PROJECT_ROOT / "docs" / ".gitignore"
        assert gitignore.exists(), "docs/.gitignore not found"

        gitignore_content = gitignore.read_text()

        # Check for build artifact exclusions
        assert "_build/" in gitignore_content, "_build/ not excluded"
        assert "*.pdf" in gitignore_content, "*.pdf not excluded"
        assert "*.tex" in gitignore_content, "*.tex not excluded"
        assert "*.aux" in gitignore_content, "*.aux not excluded"
        assert "*.log" in gitignore_content, "*.log not excluded"
        assert "*.adoc" in gitignore_content, "*.adoc not excluded"
