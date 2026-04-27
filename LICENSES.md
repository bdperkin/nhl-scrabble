# Dependency License Report

This file lists all Python package dependencies and their licenses for the NHL Scrabble project.

## License Policy

**NHL Scrabble** is licensed under the **MIT License**, a permissive open-source license.

### Runtime Dependencies

All runtime dependencies (packages distributed with the application) MUST use permissive licenses compatible with MIT:

- ✅ **Allowed**: MIT, Apache 2.0, BSD (2-clause, 3-clause), ISC, PSF, MPL-2.0, Unlicense, Public Domain
- ❌ **Prohibited**: GPL, LGPL, AGPL (copyleft licenses), Proprietary licenses

### Development Dependencies

Development and build tools (not distributed with the application) may use different licenses with justification:

- **blocklint** (UNKNOWN): Inclusive language checker, dev-only pre-commit hook
- **CairoSVG** (LGPL-3.0-or-later): SVG to PNG converter, optional branding tool
- **pyenchant** (LGPL): Spell checker for documentation, optional docs tool
- **docutils** (mixed BSD/GPL/Public Domain/PSF): Sphinx dependency for documentation generation

These exceptions are acceptable because:

1. They are optional dependencies (not required for core functionality)
1. They are build/development tools (not distributed with the package)
1. They do not affect the licensing of the NHL Scrabble codebase or distributed binaries

## Verification

To verify license compliance:

```bash
# Check all licenses
tox -e licenses

# View summary
tox -e licenses-summary

# Direct pip-licenses usage
pip-licenses --format=plain --order=license
```

## Complete License List

The following table shows all dependencies (including development and optional packages):

| Name                          | Version                         | License                                                      |
| ----------------------------- | ------------------------------- | ------------------------------------------------------------ |
| Authlib                       | 1.7.0                           | BSD License                                                  |
| CacheControl                  | 0.14.4                          | Apache-2.0                                                   |
| EditorConfig                  | 0.17.1                          | Python Software Foundation License                           |
| Jinja2                        | 3.1.6                           | BSD License                                                  |
| LinkChecker                   | 10.6.0                          | GNU General Public License v2 or later (GPLv2+)              |
| MarkupSafe                    | 3.0.3                           | BSD-3-Clause                                                 |
| PyYAML                        | 6.0.3                           | MIT License                                                  |
| Pygments                      | 2.20.0                          | BSD-2-Clause                                                 |
| SecretStorage                 | 3.5.0                           | BSD-3-Clause                                                 |
| Sphinx                        | 9.1.0                           | BSD-2-Clause                                                 |
| Unidecode                     | 1.4.0                           | GNU General Public License v2 or later (GPLv2+)              |
| add_trailing_comma            | 4.0.0                           | MIT                                                          |
| alabaster                     | 1.0.0                           | BSD License                                                  |
| annotated-doc                 | 0.0.4                           | MIT                                                          |
| annotated-types               | 0.7.0                           | MIT License                                                  |
| anyio                         | 4.13.0                          | MIT                                                          |
| attrs                         | 26.1.0                          | MIT                                                          |
| babel                         | 2.18.0                          | BSD License                                                  |
| bandit                        | 1.9.4                           | Apache-2.0                                                   |
| beautifulsoup4                | 4.14.3                          | MIT License                                                  |
| black                         | 26.3.1                          | MIT                                                          |
| blacken-docs                  | 1.20.0                          | MIT                                                          |
| boolean.py                    | 5.0                             | BSD-2-Clause                                                 |
| build                         | 1.4.3                           | MIT                                                          |
| cachetools                    | 7.0.5                           | MIT                                                          |
| cattrs                        | 26.1.0                          | MIT License                                                  |
| certifi                       | 2026.2.25                       | Mozilla Public License 2.0 (MPL 2.0)                         |
| cffi                          | 2.0.0                           | MIT                                                          |
| cfgv                          | 3.5.0                           | MIT                                                          |
| chardet                       | 7.4.2                           | 0BSD                                                         |
| charset-normalizer            | 3.4.7                           | MIT                                                          |
| check-jsonschema              | 0.37.1                          | Apache Software License                                      |
| clang-format                  | 22.1.4                          | Apache Software License                                      |
| click                         | 8.3.2                           | BSD-3-Clause                                                 |
| colorama                      | 0.4.6                           | BSD License                                                  |
| colorlog                      | 6.10.1                          | MIT License                                                  |
| coverage                      | 7.13.5                          | Apache-2.0                                                   |
| cryptography                  | 46.0.7                          | Apache-2.0 OR BSD-3-Clause                                   |
| cssbeautifier                 | 1.15.4                          | MIT                                                          |
| cyclonedx-python-lib          | 11.7.0                          | Apache Software License                                      |
| defusedxml                    | 0.7.1                           | Python Software Foundation License                           |
| dicttoxml                     | 1.7.16                          | GNU GENERAL PUBLIC LICENSE                                   |
| diff_cover                    | 10.2.0                          | Apache Software License                                      |
| distlib                       | 0.4.0                           | Python Software Foundation License                           |
| djlint                        | 1.36.4                          | GNU General Public License v3 or later (GPLv3+)              |
| dnspython                     | 2.8.0                           | ISC License (ISCL)                                           |
| docformatter                  | 1.7.7                           | MIT License; Other/Proprietary License                       |
| docopt                        | 0.6.2                           | MIT License                                                  |
| docutils                      | 0.22.4                          | BSD License; GNU General Public License (GPL); Public Domain |
| dparse                        | 0.6.4                           | MIT License                                                  |
| et_xmlfile                    | 2.0.0                           | MIT License                                                  |
| execnet                       | 2.1.2                           | MIT                                                          |
| fastapi                       | 0.136.0                         | MIT                                                          |
| fastjsonschema                | 2.21.2                          | BSD License                                                  |
| filelock                      | 3.25.2                          | MIT                                                          |
| h11                           | 0.16.0                          | MIT License                                                  |
| httpcore                      | 1.0.9                           | BSD-3-Clause                                                 |
| httptools                     | 0.7.1                           | MIT                                                          |
| httpx                         | 0.28.1                          | BSD License                                                  |
| id                            | 1.6.1                           | Apache Software License                                      |
| identify                      | 2.6.18                          | MIT                                                          |
| idna                          | 3.11                            | BSD-3-Clause                                                 |
| imagesize                     | 2.0.0                           | MIT License                                                  |
| iniconfig                     | 2.3.0                           | MIT                                                          |
| interrogate                   | 1.7.0                           | MIT License                                                  |
| isort                         | 8.0.1                           | MIT                                                          |
| jaraco.classes                | 3.4.0                           | MIT License                                                  |
| jaraco.context                | 6.1.2                           | MIT                                                          |
| jaraco.functools              | 4.4.0                           | MIT                                                          |
| jeepney                       | 0.9.0                           | MIT                                                          |
| joblib                        | 1.5.3                           | BSD-3-Clause                                                 |
| joserfc                       | 1.6.4                           | BSD License                                                  |
| jsbeautifier                  | 1.15.4                          | MIT                                                          |
| json5                         | 0.14.0                          | Apache Software License                                      |
| jsonschema                    | 4.26.0                          | MIT                                                          |
| jsonschema-specifications     | 2025.9.1                        | MIT                                                          |
| keyring                       | 25.7.0                          | MIT                                                          |
| librt                         | 0.9.0                           | MIT                                                          |
| license-expression            | 30.4.4                          | Apache-2.0                                                   |
| markdown-it-py                | 4.0.0                           | MIT License                                                  |
| marshmallow                   | 4.3.0                           | MIT                                                          |
| mdit-py-plugins               | 0.5.0                           | MIT License                                                  |
| mdurl                         | 0.1.2                           | MIT License                                                  |
| more-itertools                | 11.0.2                          | MIT                                                          |
| msgpack                       | 1.1.2                           | Apache-2.0                                                   |
| mypy                          | 1.20.1                          | MIT                                                          |
| mypy_extensions               | 1.1.0                           | MIT                                                          |
| myst-parser                   | 5.0.0                           | MIT License                                                  |
| nh3                           | 0.3.4                           | MIT                                                          |
| nhl-scrabble                  | 0.0.3.dev4+g833b70562.d20260427 | MIT License                                                  |
| nltk                          | 3.9.4                           | Apache Software License                                      |
| nodeenv                       | 1.10.0                          | BSD License                                                  |
| openpyxl                      | 3.1.5                           | MIT License                                                  |
| packageurl-python             | 0.17.6                          | MIT License                                                  |
| packaging                     | 26.0                            | Apache-2.0 OR BSD-2-Clause                                   |
| pathspec                      | 1.0.4                           | Mozilla Public License 2.0 (MPL 2.0)                         |
| pip-api                       | 0.0.34                          | Apache Software License                                      |
| pip-requirements-parser       | 32.0.1                          | MIT                                                          |
| pip_audit                     | 2.10.0                          | Apache Software License                                      |
| platformdirs                  | 4.9.6                           | MIT                                                          |
| pluggy                        | 1.6.0                           | MIT License                                                  |
| pprintpp                      | 0.4.0                           | BSD License                                                  |
| pre_commit                    | 4.5.1                           | MIT                                                          |
| prompt_toolkit                | 3.0.52                          | BSD License                                                  |
| py                            | 1.11.0                          | MIT License                                                  |
| py-cpuinfo                    | 9.0.0                           | MIT License                                                  |
| py-serializable               | 2.1.0                           | Apache Software License                                      |
| pycparser                     | 3.0                             | BSD-3-Clause                                                 |
| pydantic                      | 2.13.0                          | MIT                                                          |
| pydantic-settings             | 2.14.0                          | MIT                                                          |
| pydantic_core                 | 2.46.0                          | MIT                                                          |
| pyenchant                     | 3.3.0                           | LGPL                                                         |
| pyparsing                     | 3.3.2                           | MIT                                                          |
| pyproject-api                 | 1.10.0                          | MIT                                                          |
| pyproject-fmt                 | 2.21.1                          | MIT License                                                  |
| pyproject_hooks               | 1.2.0                           | MIT License                                                  |
| pyroma                        | 5.0.1                           | MIT License                                                  |
| pytest                        | 9.0.3                           | MIT                                                          |
| pytest-benchmark              | 5.2.3                           | BSD-2-Clause                                                 |
| pytest-clarity                | 1.0.1                           | MIT License                                                  |
| pytest-cov                    | 7.1.0                           | MIT                                                          |
| pytest-mock                   | 3.15.1                          | MIT License                                                  |
| pytest-randomly               | 4.1.0                           | MIT                                                          |
| pytest-rerunfailures          | 16.1                            | MPL-2.0                                                      |
| pytest-sphinx                 | 0.7.1                           | BSD License                                                  |
| pytest-sugar                  | 1.1.1                           | BSD License                                                  |
| pytest-timeout                | 2.4.0                           | DFSG approved; MIT License                                   |
| pytest-watch                  | 4.2.0                           | MIT                                                          |
| pytest-xdist                  | 3.8.0                           | MIT                                                          |
| python-discovery              | 1.2.2                           | MIT License                                                  |
| python-dotenv                 | 1.2.2                           | BSD-3-Clause                                                 |
| pytokens                      | 0.4.1                           | MIT License                                                  |
| readme_renderer               | 44.0                            | Apache Software License                                      |
| referencing                   | 0.37.0                          | MIT                                                          |
| refurb                        | 2.3.1                           | GNU General Public License v3 (GPLv3)                        |
| regex                         | 2026.4.4                        | Apache-2.0 AND CNRI-Python                                   |
| regress                       | 2025.10.1                       | MIT License                                                  |
| requests                      | 2.33.1                          | Apache Software License                                      |
| requests-cache                | 1.3.1                           | BSD-2-Clause                                                 |
| requests-toolbelt             | 1.0.0                           | Apache Software License                                      |
| rfc3986                       | 2.0.0                           | Apache Software License                                      |
| rich                          | 15.0.0                          | MIT License                                                  |
| roman-numerals                | 4.1.0                           | 0BSD OR CC0-1.0                                              |
| rpds-py                       | 0.30.0                          | MIT                                                          |
| ruamel.yaml                   | 0.19.1                          | MIT License                                                  |
| ruff                          | 0.15.10                         | MIT                                                          |
| safety                        | 3.7.0                           | MIT                                                          |
| safety-schemas                | 0.0.16                          | MIT License                                                  |
| shellingham                   | 1.5.4                           | ISC License (ISCL)                                           |
| six                           | 1.17.0                          | MIT License                                                  |
| snowballstemmer               | 3.0.1                           | BSD License                                                  |
| sortedcontainers              | 2.4.0                           | Apache Software License                                      |
| soupsieve                     | 2.8.3                           | MIT                                                          |
| sphinx-autobuild              | 2025.8.25                       | MIT License                                                  |
| sphinx-autodoc-typehints      | 3.10.2                          | MIT                                                          |
| sphinx-copybutton             | 0.5.2                           | MIT License                                                  |
| sphinx-last-updated-by-git    | 0.3.8                           | BSD License                                                  |
| sphinx-sitemap                | 2.9.0                           | MIT                                                          |
| sphinx_design                 | 0.7.0                           | MIT License                                                  |
| sphinx_rtd_theme              | 3.1.0                           | MIT License                                                  |
| sphinxcontrib-applehelp       | 2.0.0                           | BSD License                                                  |
| sphinxcontrib-devhelp         | 2.0.0                           | BSD License                                                  |
| sphinxcontrib-htmlhelp        | 2.1.0                           | BSD License                                                  |
| sphinxcontrib-jquery          | 4.1                             | BSD License                                                  |
| sphinxcontrib-jsmath          | 1.0.1                           | BSD License                                                  |
| sphinxcontrib-programoutput   | 0.19                            | BSD License                                                  |
| sphinxcontrib-qthelp          | 2.0.0                           | BSD License                                                  |
| sphinxcontrib-serializinghtml | 2.0.0                           | BSD License                                                  |
| sphinxcontrib-spelling        | 8.0.2                           | BSD License                                                  |
| sphinxext-opengraph           | 0.13.0                          | BSD-3-Clause                                                 |
| starlette                     | 1.0.0                           | BSD-3-Clause                                                 |
| stevedore                     | 5.7.0                           | Apache Software License                                      |
| tabulate                      | 0.10.0                          | MIT                                                          |
| tenacity                      | 9.1.4                           | Apache Software License                                      |
| termcolor                     | 3.3.0                           | MIT                                                          |
| tokenize_rt                   | 6.2.0                           | MIT                                                          |
| toml-fmt-common               | 1.3.2                           | MIT                                                          |
| tomli                         | 2.4.1                           | MIT                                                          |
| tomli_w                       | 1.2.0                           | MIT License                                                  |
| tomlkit                       | 0.14.0                          | MIT License                                                  |
| tox                           | 4.52.1                          | MIT                                                          |
| tox-ini-fmt                   | 1.7.1                           | MIT                                                          |
| tox-uv                        | 1.35.1                          | MIT                                                          |
| tox-uv-bare                   | 1.35.1                          | MIT                                                          |
| tqdm                          | 4.67.3                          | MPL-2.0 AND MIT                                              |
| trove-classifiers             | 2026.1.14.14                    | Apache Software License                                      |
| twine                         | 6.2.0                           | Apache-2.0                                                   |
| ty                            | 0.0.29                          | MIT License                                                  |
| typer                         | 0.24.1                          | MIT                                                          |
| types-PyYAML                  | 6.0.12.20260408                 | Apache-2.0                                                   |
| types-requests                | 2.33.0.20260408                 | Apache-2.0                                                   |
| typing-inspection             | 0.4.2                           | MIT                                                          |
| typing_extensions             | 4.15.0                          | PSF-2.0                                                      |
| untokenize                    | 0.1.1                           | MIT License                                                  |
| url-normalize                 | 2.2.1                           | MIT                                                          |
| urllib3                       | 2.6.3                           | MIT                                                          |
| uv                            | 0.11.6                          | MIT OR Apache-2.0                                            |
| uvicorn                       | 0.46.0                          | BSD-3-Clause                                                 |
| uvloop                        | 0.22.1                          | Apache Software License; MIT License                         |
| validate-pyproject            | 0.25                            | MPL-2.0 and MIT and BSD-3-Clause                             |
| virtualenv                    | 21.2.1                          | MIT                                                          |
| watchdog                      | 6.0.0                           | Apache Software License                                      |
| watchfiles                    | 1.1.1                           | MIT License                                                  |
| websockets                    | 16.0                            | BSD-3-Clause                                                 |
