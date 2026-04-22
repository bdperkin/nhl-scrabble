# Documentation Link Reference

Common links for use in project documentation.

## Python

- **Python**: <https://www.python.org/>
- **Python Docs**: <https://docs.python.org/3/>
- **PEP Index**: <https://peps.python.org/>
- **PEP 8**: <https://peps.python.org/pep-0008/>
- **PEP 257**: <https://peps.python.org/pep-0257/>
- **PEP 440**: <https://peps.python.org/pep-0440/>
- **PEP 517**: <https://peps.python.org/pep-0517/>
- **PEP 518**: <https://peps.python.org/pep-0518/>
- **PEP 621**: <https://peps.python.org/pep-0621/>
- **PEP 631**: <https://peps.python.org/pep-0631/>
- **PyPI**: <https://pypi.org/>

## Development Tools

- **ruff**: <https://docs.astral.sh/ruff/>
- **mypy**: <https://mypy-lang.org/>
- **pytest**: <https://docs.pytest.org/>
- **pytest-xdist**: <https://pytest-xdist.readthedocs.io/>
- **pytest-cov**: <https://pytest-cov.readthedocs.io/>
- **tox**: <https://tox.wiki/>
- **pre-commit**: <https://pre-commit.com/>
- **UV**: <https://docs.astral.sh/uv/>
- **hatchling**: <https://hatch.pypa.io/latest/>
- **black**: <https://black.readthedocs.io/>
- **isort**: <https://pycqa.github.io/isort/>
- **flake8**: <https://flake8.pycqa.org/>
- **interrogate**: <https://interrogate.readthedocs.io/>
- **deptry**: <https://deptry.com/>
- **pydocstyle**: <http://www.pydocstyle.org/>
- **vulture**: <https://github.com/jendrikseipp/vulture>
- **bandit**: <https://bandit.readthedocs.io/>
- **safety**: <https://pyup.io/safety/>
- **ty**: <https://docs.astral.sh/ty/>
- **diff-cover**: <https://github.com/Bachmann1234/diff_cover>
- **sphinx**: <https://www.sphinx-doc.org/>
- **sphinx-rtd-theme**: <https://sphinx-rtd-theme.readthedocs.io/>
- **myst-parser**: <https://myst-parser.readthedocs.io/>

## Python Libraries

- **requests**: <https://requests.readthedocs.io/>
- **click**: <https://click.palletsprojects.com/>
- **pydantic**: <https://docs.pydantic.dev/>
- **rich**: <https://rich.readthedocs.io/>
- **typing-extensions**: <https://typing-extensions.readthedocs.io/>

## Build and Package Tools

- **pip**: <https://pip.pypa.io/>
- **setuptools**: <https://setuptools.pypa.io/>
- **wheel**: <https://wheel.readthedocs.io/>
- **twine**: <https://twine.readthedocs.io/>

## Standards

- **Semantic Versioning**: <https://semver.org/>
- **Conventional Commits**: <https://www.conventionalcommits.org/>
- **Keep a Changelog**: <https://keepachangelog.com/>
- **CommonMark**: <https://commonmark.org/>
- **Diátaxis**: <https://diataxis.fr/>

## Platforms and Services

- **GitHub**: <https://github.com/>
- **GitHub Actions**: <https://docs.github.com/en/actions>
- **GitHub Pages**: <https://pages.github.com/>
- **Codecov**: <https://about.codecov.io/>
- **CodeQL**: <https://codeql.github.com/>
- **Dependabot**: <https://docs.github.com/en/code-security/dependabot>

## Methodologies

- **Test-driven development**: <https://en.wikipedia.org/wiki/Test-driven_development>
- **Continuous integration**: <https://www.atlassian.com/continuous-delivery/continuous-integration>
- **Continuous delivery**: <https://www.atlassian.com/continuous-delivery>

## NHL API

- **NHL API Documentation**: <https://gitlab.com/dword4/nhlapi>
- **NHL Stats API**: <https://api-web.nhle.com/>

## Usage

When adding links to documentation:

1. **First mention**: Link the first occurrence of a term in each document
1. **Important mentions**: Link subsequent occurrences if particularly relevant
1. **Official sources**: Always link to official documentation
1. **HTTPS**: Use HTTPS links exclusively
1. **Stable URLs**: Prefer stable, canonical URLs

## Link Format

```markdown
# Inline links (preferred)
[Tool Name](https://official-site.com/)

# Reference-style links (for repeated or long URLs)
[Tool Name][tool-link]
...
[tool-link]: https://very-long-url.com/path/to/docs
```

## Checking Links

```bash
# Install markdown-link-check
npm install -g markdown-link-check

# Check all markdown files
find . -name "*.md" -not -path "./node_modules/*" -exec markdown-link-check {} \;

# Check specific file
markdown-link-check README.md
```
