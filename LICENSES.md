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

| Name                             | Version         | License                                                                                          |
| -------------------------------- | --------------- | ------------------------------------------------------------------------------------------------ |
| Authlib                          | 1.6.11          | BSD License                                                                                      |
| Authlib                          | 1.6.11          | BSD License                                                                                      |
| CacheControl                     | 0.14.4          | Apache-2.0                                                                                       |
| CacheControl                     | 0.14.4          | Apache-2.0                                                                                       |
| CairoSVG                         | 2.9.0           | LGPL-3.0-or-later                                                                                |
| CairoSVG                         | 2.9.0           | LGPL-3.0-or-later                                                                                |
| Jinja2                           | 3.1.6           | BSD License                                                                                      |
| Jinja2                           | 3.1.6           | BSD License                                                                                      |
| MarkupSafe                       | 3.0.3           | BSD-3-Clause                                                                                     |
| MarkupSafe                       | 3.0.3           | BSD-3-Clause                                                                                     |
| PyYAML                           | 6.0.3           | MIT License                                                                                      |
| PyYAML                           | 6.0.3           | MIT License                                                                                      |
| Pygments                         | 2.20.0          | BSD-2-Clause                                                                                     |
| Pygments                         | 2.20.0          | BSD-2-Clause                                                                                     |
| SecretStorage                    | 3.5.0           | BSD-3-Clause                                                                                     |
| SecretStorage                    | 3.5.0           | BSD-3-Clause                                                                                     |
| Sphinx                           | 8.1.3           | BSD License                                                                                      |
| Sphinx                           | 8.1.3           | BSD License                                                                                      |
| alabaster                        | 1.0.0           | BSD License                                                                                      |
| alabaster                        | 1.0.0           | BSD License                                                                                      |
| annotated-doc                    | 0.0.4           | MIT                                                                                              |
| annotated-doc                    | 0.0.4           | MIT                                                                                              |
| annotated-types                  | 0.7.0           | MIT License                                                                                      |
| annotated-types                  | 0.7.0           | MIT License                                                                                      |
| anyio                            | 4.13.0          | MIT                                                                                              |
| anyio                            | 4.13.0          | MIT                                                                                              |
| arrow                            | 1.2.3           | Apache Software License                                                                          |
| arrow                            | 1.2.3           | Apache Software License                                                                          |
| attrs                            | 26.1.0          | MIT                                                                                              |
| attrs                            | 26.1.0          | MIT                                                                                              |
| babel                            | 2.18.0          | BSD License                                                                                      |
| babel                            | 2.18.0          | BSD License                                                                                      |
| backports-datetime-fromisoformat | 2.0.3           | MIT License                                                                                      |
| backports-datetime-fromisoformat | 2.0.3           | MIT License                                                                                      |
| backports.tarfile                | 1.2.0           | MIT License                                                                                      |
| backports.tarfile                | 1.2.0           | MIT License                                                                                      |
| bandit                           | 1.9.4           | Apache-2.0                                                                                       |
| bandit                           | 1.9.4           | Apache-2.0                                                                                       |
| beautifulsoup4                   | 4.14.3          | MIT License                                                                                      |
| beautifulsoup4                   | 4.14.3          | MIT License                                                                                      |
| black                            | 26.3.1          | MIT                                                                                              |
| black                            | 26.3.1          | MIT                                                                                              |
| blacken-docs                     | 1.20.0          | MIT                                                                                              |
| blacken-docs                     | 1.20.0          | MIT                                                                                              |
| blocklint                        | 0.3.0           | UNKNOWN                                                                                          |
| blocklint                        | 0.3.0           | UNKNOWN                                                                                          |
| boolean.py                       | 5.0             | BSD-2-Clause                                                                                     |
| boolean.py                       | 5.0             | BSD-2-Clause                                                                                     |
| build                            | 1.4.3           | MIT                                                                                              |
| build                            | 1.4.3           | MIT                                                                                              |
| cachetools                       | 7.0.5           | MIT                                                                                              |
| cachetools                       | 7.0.5           | MIT                                                                                              |
| cairocffi                        | 1.7.1           | BSD License                                                                                      |
| cairocffi                        | 1.7.1           | BSD License                                                                                      |
| cattrs                           | 26.1.0          | MIT License                                                                                      |
| cattrs                           | 26.1.0          | MIT License                                                                                      |
| certifi                          | 2026.2.25       | Mozilla Public License 2.0 (MPL 2.0)                                                             |
| certifi                          | 2026.2.25       | Mozilla Public License 2.0 (MPL 2.0)                                                             |
| cffi                             | 2.0.0           | MIT                                                                                              |
| cffi                             | 2.0.0           | MIT                                                                                              |
| cfgv                             | 3.5.0           | MIT                                                                                              |
| cfgv                             | 3.5.0           | MIT                                                                                              |
| charset-normalizer               | 3.4.7           | MIT                                                                                              |
| charset-normalizer               | 3.4.7           | MIT                                                                                              |
| click                            | 8.1.3           | BSD License                                                                                      |
| click                            | 8.1.3           | BSD License                                                                                      |
| colorama                         | 0.4.6           | BSD License                                                                                      |
| colorama                         | 0.4.6           | BSD License                                                                                      |
| coverage                         | 7.13.5          | Apache-2.0                                                                                       |
| coverage                         | 7.13.5          | Apache-2.0                                                                                       |
| cryptography                     | 46.0.7          | Apache-2.0 OR BSD-3-Clause                                                                       |
| cryptography                     | 46.0.7          | Apache-2.0 OR BSD-3-Clause                                                                       |
| cssselect2                       | 0.9.0           | BSD License                                                                                      |
| cssselect2                       | 0.9.0           | BSD License                                                                                      |
| cyclonedx-python-lib             | 11.7.0          | Apache Software License                                                                          |
| cyclonedx-python-lib             | 11.7.0          | Apache Software License                                                                          |
| defusedxml                       | 0.7.1           | Python Software Foundation License                                                               |
| defusedxml                       | 0.7.1           | Python Software Foundation License                                                               |
| deptry                           | 0.25.1          | MIT                                                                                              |
| deptry                           | 0.25.1          | MIT                                                                                              |
| distlib                          | 0.4.0           | Python Software Foundation License                                                               |
| distlib                          | 0.4.0           | Python Software Foundation License                                                               |
| docformatter                     | 1.7.7           | MIT License; Other/Proprietary License                                                           |
| docformatter                     | 1.7.7           | MIT License; Other/Proprietary License                                                           |
| docopt                           | 0.6.2           | MIT License                                                                                      |
| docopt                           | 0.6.2           | MIT License                                                                                      |
| docutils                         | 0.21.2          | BSD License; GNU General Public License (GPL); Public Domain; Python Software Foundation License |
| docutils                         | 0.21.2          | BSD License; GNU General Public License (GPL); Public Domain; Python Software Foundation License |
| dparse                           | 0.6.4           | MIT License                                                                                      |
| dparse                           | 0.6.4           | MIT License                                                                                      |
| exceptiongroup                   | 1.3.1           | MIT License                                                                                      |
| exceptiongroup                   | 1.3.1           | MIT License                                                                                      |
| filelock                         | 3.28.0          | MIT                                                                                              |
| filelock                         | 3.28.0          | MIT                                                                                              |
| gitlint                          | 0.19.1          | MIT                                                                                              |
| gitlint                          | 0.19.1          | MIT                                                                                              |
| gitlint-core                     | 0.19.1          | MIT                                                                                              |
| gitlint-core                     | 0.19.1          | MIT                                                                                              |
| h11                              | 0.16.0          | MIT License                                                                                      |
| h11                              | 0.16.0          | MIT License                                                                                      |
| httpcore                         | 1.0.9           | BSD-3-Clause                                                                                     |
| httpcore                         | 1.0.9           | BSD-3-Clause                                                                                     |
| httpx                            | 0.28.1          | BSD License                                                                                      |
| httpx                            | 0.28.1          | BSD License                                                                                      |
| id                               | 1.6.1           | Apache Software License                                                                          |
| id                               | 1.6.1           | Apache Software License                                                                          |
| identify                         | 2.6.18          | MIT                                                                                              |
| identify                         | 2.6.18          | MIT                                                                                              |
| idna                             | 3.11            | BSD-3-Clause                                                                                     |
| idna                             | 3.11            | BSD-3-Clause                                                                                     |
| imagesize                        | 2.0.0           | MIT License                                                                                      |
| imagesize                        | 2.0.0           | MIT License                                                                                      |
| importlib_metadata               | 9.0.0           | Apache-2.0                                                                                       |
| importlib_metadata               | 9.0.0           | Apache-2.0                                                                                       |
| iniconfig                        | 2.3.0           | MIT                                                                                              |
| iniconfig                        | 2.3.0           | MIT                                                                                              |
| interrogate                      | 1.7.0           | MIT License                                                                                      |
| interrogate                      | 1.7.0           | MIT License                                                                                      |
| isort                            | 8.0.1           | MIT                                                                                              |
| isort                            | 8.0.1           | MIT                                                                                              |
| jaraco.classes                   | 3.4.0           | MIT License                                                                                      |
| jaraco.classes                   | 3.4.0           | MIT License                                                                                      |
| jaraco.context                   | 6.1.2           | MIT                                                                                              |
| jaraco.context                   | 6.1.2           | MIT                                                                                              |
| jaraco.functools                 | 4.4.0           | MIT                                                                                              |
| jaraco.functools                 | 4.4.0           | MIT                                                                                              |
| jeepney                          | 0.9.0           | MIT                                                                                              |
| jeepney                          | 0.9.0           | MIT                                                                                              |
| joblib                           | 1.5.3           | BSD-3-Clause                                                                                     |
| joblib                           | 1.5.3           | BSD-3-Clause                                                                                     |
| keyring                          | 25.7.0          | MIT                                                                                              |
| keyring                          | 25.7.0          | MIT                                                                                              |
| libcst                           | 1.8.2           | MIT License                                                                                      |
| libcst                           | 1.8.2           | MIT License                                                                                      |
| librt                            | 0.9.0           | MIT                                                                                              |
| librt                            | 0.9.0           | MIT                                                                                              |
| license-expression               | 30.4.4          | Apache-2.0                                                                                       |
| license-expression               | 30.4.4          | Apache-2.0                                                                                       |
| markdown-it-py                   | 3.0.0           | MIT License                                                                                      |
| markdown-it-py                   | 3.0.0           | MIT License                                                                                      |
| markdown2                        | 2.5.5           | MIT                                                                                              |
| markdown2                        | 2.5.5           | MIT                                                                                              |
| marshmallow                      | 4.3.0           | MIT                                                                                              |
| marshmallow                      | 4.3.0           | MIT                                                                                              |
| mdit-py-plugins                  | 0.5.0           | MIT License                                                                                      |
| mdit-py-plugins                  | 0.5.0           | MIT License                                                                                      |
| mdurl                            | 0.1.2           | MIT License                                                                                      |
| mdurl                            | 0.1.2           | MIT License                                                                                      |
| more-itertools                   | 11.0.2          | MIT                                                                                              |
| more-itertools                   | 11.0.2          | MIT                                                                                              |
| msgpack                          | 1.1.2           | Apache-2.0                                                                                       |
| msgpack                          | 1.1.2           | Apache-2.0                                                                                       |
| mypy                             | 1.20.1          | MIT                                                                                              |
| mypy                             | 1.20.1          | MIT                                                                                              |
| mypy_extensions                  | 1.1.0           | MIT                                                                                              |
| mypy_extensions                  | 1.1.0           | MIT                                                                                              |
| myst-parser                      | 4.0.1           | MIT License                                                                                      |
| myst-parser                      | 4.0.1           | MIT License                                                                                      |
| nh3                              | 0.3.4           | MIT                                                                                              |
| nh3                              | 0.3.4           | MIT                                                                                              |
| nhl-scrabble                     | 2.0.0           | MIT License                                                                                      |
| nhl-scrabble                     | 2.0.0           | MIT License                                                                                      |
| nltk                             | 3.9.4           | Apache Software License                                                                          |
| nltk                             | 3.9.4           | Apache Software License                                                                          |
| nodeenv                          | 1.10.0          | BSD License                                                                                      |
| nodeenv                          | 1.10.0          | BSD License                                                                                      |
| packageurl-python                | 0.17.6          | MIT License                                                                                      |
| packageurl-python                | 0.17.6          | MIT License                                                                                      |
| packaging                        | 26.1            | Apache-2.0 OR BSD-2-Clause                                                                       |
| packaging                        | 26.1            | Apache-2.0 OR BSD-2-Clause                                                                       |
| pathspec                         | 1.0.4           | Mozilla Public License 2.0 (MPL 2.0)                                                             |
| pathspec                         | 1.0.4           | Mozilla Public License 2.0 (MPL 2.0)                                                             |
| pdoc                             | 16.0.0          | Public Domain                                                                                    |
| pdoc                             | 16.0.0          | Public Domain                                                                                    |
| pillow                           | 12.2.0          | MIT-CMU                                                                                          |
| pillow                           | 12.2.0          | MIT-CMU                                                                                          |
| pip-api                          | 0.0.34          | Apache Software License                                                                          |
| pip-api                          | 0.0.34          | Apache Software License                                                                          |
| pip-requirements-parser          | 32.0.1          | MIT                                                                                              |
| pip-requirements-parser          | 32.0.1          | MIT                                                                                              |
| pip_audit                        | 2.10.0          | Apache Software License                                                                          |
| pip_audit                        | 2.10.0          | Apache Software License                                                                          |
| platformdirs                     | 4.9.6           | MIT                                                                                              |
| platformdirs                     | 4.9.6           | MIT                                                                                              |
| pluggy                           | 1.6.0           | MIT License                                                                                      |
| pluggy                           | 1.6.0           | MIT License                                                                                      |
| pre_commit                       | 4.5.1           | MIT                                                                                              |
| pre_commit                       | 4.5.1           | MIT                                                                                              |
| py                               | 1.11.0          | MIT License                                                                                      |
| py                               | 1.11.0          | MIT License                                                                                      |
| py-serializable                  | 2.1.0           | Apache Software License                                                                          |
| py-serializable                  | 2.1.0           | Apache Software License                                                                          |
| pycparser                        | 3.0             | BSD-3-Clause                                                                                     |
| pycparser                        | 3.0             | BSD-3-Clause                                                                                     |
| pydantic                         | 2.13.0          | MIT                                                                                              |
| pydantic                         | 2.13.0          | MIT                                                                                              |
| pydantic_core                    | 2.46.0          | MIT                                                                                              |
| pydantic_core                    | 2.46.0          | MIT                                                                                              |
| pydocstyle                       | 6.3.0           | MIT License                                                                                      |
| pydocstyle                       | 6.3.0           | MIT License                                                                                      |
| pyenchant                        | 3.3.0           | LGPL                                                                                             |
| pyenchant                        | 3.3.0           | LGPL                                                                                             |
| pyparsing                        | 3.3.2           | MIT                                                                                              |
| pyparsing                        | 3.3.2           | MIT                                                                                              |
| pyproject-api                    | 1.10.0          | MIT                                                                                              |
| pyproject-api                    | 1.10.0          | MIT                                                                                              |
| pyproject-fmt                    | 2.21.1          | MIT License                                                                                      |
| pyproject-fmt                    | 2.21.1          | MIT License                                                                                      |
| pyproject_hooks                  | 1.2.0           | MIT License                                                                                      |
| pyproject_hooks                  | 1.2.0           | MIT License                                                                                      |
| pyroma                           | 5.0.1           | MIT License                                                                                      |
| pyroma                           | 5.0.1           | MIT License                                                                                      |
| pytest                           | 9.0.3           | MIT                                                                                              |
| pytest                           | 9.0.3           | MIT                                                                                              |
| pytest-cov                       | 7.1.0           | MIT                                                                                              |
| pytest-cov                       | 7.1.0           | MIT                                                                                              |
| pytest-mock                      | 3.15.1          | MIT License                                                                                      |
| pytest-mock                      | 3.15.1          | MIT License                                                                                      |
| pytest-sphinx                    | 0.7.1           | BSD License                                                                                      |
| pytest-sphinx                    | 0.7.1           | BSD License                                                                                      |
| pytest-watch                     | 4.2.0           | MIT                                                                                              |
| pytest-watch                     | 4.2.0           | MIT                                                                                              |
| python-dateutil                  | 2.9.0.post0     | Apache Software License; BSD License                                                             |
| python-dateutil                  | 2.9.0.post0     | Apache Software License; BSD License                                                             |
| python-discovery                 | 1.2.2           | MIT License                                                                                      |
| python-discovery                 | 1.2.2           | MIT License                                                                                      |
| python-dotenv                    | 1.2.2           | BSD-3-Clause                                                                                     |
| python-dotenv                    | 1.2.2           | BSD-3-Clause                                                                                     |
| pytokens                         | 0.4.1           | MIT License                                                                                      |
| pytokens                         | 0.4.1           | MIT License                                                                                      |
| readme_renderer                  | 44.0            | Apache Software License                                                                          |
| readme_renderer                  | 44.0            | Apache Software License                                                                          |
| regex                            | 2026.4.4        | Apache-2.0 AND CNRI-Python                                                                       |
| regex                            | 2026.4.4        | Apache-2.0 AND CNRI-Python                                                                       |
| requests                         | 2.33.1          | Apache Software License                                                                          |
| requests                         | 2.33.1          | Apache Software License                                                                          |
| requests-cache                   | 1.3.1           | BSD-2-Clause                                                                                     |
| requests-cache                   | 1.3.1           | BSD-2-Clause                                                                                     |
| requests-toolbelt                | 1.0.0           | Apache Software License                                                                          |
| requests-toolbelt                | 1.0.0           | Apache Software License                                                                          |
| requirements-parser              | 0.13.0          | Apache Software License                                                                          |
| requirements-parser              | 0.13.0          | Apache Software License                                                                          |
| rfc3986                          | 2.0.0           | Apache Software License                                                                          |
| rfc3986                          | 2.0.0           | Apache Software License                                                                          |
| rich                             | 15.0.0          | MIT License                                                                                      |
| rich                             | 15.0.0          | MIT License                                                                                      |
| ruamel.yaml                      | 0.19.1          | MIT License                                                                                      |
| ruamel.yaml                      | 0.19.1          | MIT License                                                                                      |
| ruff                             | 0.15.10         | MIT                                                                                              |
| ruff                             | 0.15.10         | MIT                                                                                              |
| safety                           | 3.7.0           | MIT                                                                                              |
| safety                           | 3.7.0           | MIT                                                                                              |
| safety-schemas                   | 0.0.16          | MIT License                                                                                      |
| safety-schemas                   | 0.0.16          | MIT License                                                                                      |
| sh                               | 1.14.3          | MIT License                                                                                      |
| sh                               | 1.14.3          | MIT License                                                                                      |
| shellingham                      | 1.5.4           | ISC License (ISCL)                                                                               |
| shellingham                      | 1.5.4           | ISC License (ISCL)                                                                               |
| six                              | 1.17.0          | MIT License                                                                                      |
| six                              | 1.17.0          | MIT License                                                                                      |
| snowballstemmer                  | 3.0.1           | BSD License                                                                                      |
| snowballstemmer                  | 3.0.1           | BSD License                                                                                      |
| sortedcontainers                 | 2.4.0           | Apache Software License                                                                          |
| sortedcontainers                 | 2.4.0           | Apache Software License                                                                          |
| soupsieve                        | 2.8.3           | MIT                                                                                              |
| soupsieve                        | 2.8.3           | MIT                                                                                              |
| sphinx-autobuild                 | 2024.10.3       | MIT License                                                                                      |
| sphinx-autobuild                 | 2024.10.3       | MIT License                                                                                      |
| sphinx-autodoc-typehints         | 3.0.1           | MIT                                                                                              |
| sphinx-autodoc-typehints         | 3.0.1           | MIT                                                                                              |
| sphinx-click                     | 6.2.0           | MIT License                                                                                      |
| sphinx-click                     | 6.2.0           | MIT License                                                                                      |
| sphinx-copybutton                | 0.5.2           | MIT License                                                                                      |
| sphinx-copybutton                | 0.5.2           | MIT License                                                                                      |
| sphinx-last-updated-by-git       | 0.3.8           | BSD License                                                                                      |
| sphinx-last-updated-by-git       | 0.3.8           | BSD License                                                                                      |
| sphinx-sitemap                   | 2.9.0           | MIT                                                                                              |
| sphinx-sitemap                   | 2.9.0           | MIT                                                                                              |
| sphinx_design                    | 0.6.1           | MIT License                                                                                      |
| sphinx_design                    | 0.6.1           | MIT License                                                                                      |
| sphinx_rtd_theme                 | 3.1.0           | MIT License                                                                                      |
| sphinx_rtd_theme                 | 3.1.0           | MIT License                                                                                      |
| sphinxcontrib-applehelp          | 2.0.0           | BSD License                                                                                      |
| sphinxcontrib-applehelp          | 2.0.0           | BSD License                                                                                      |
| sphinxcontrib-devhelp            | 2.0.0           | BSD License                                                                                      |
| sphinxcontrib-devhelp            | 2.0.0           | BSD License                                                                                      |
| sphinxcontrib-htmlhelp           | 2.1.0           | BSD License                                                                                      |
| sphinxcontrib-htmlhelp           | 2.1.0           | BSD License                                                                                      |
| sphinxcontrib-jquery             | 4.1             | BSD License                                                                                      |
| sphinxcontrib-jquery             | 4.1             | BSD License                                                                                      |
| sphinxcontrib-jsmath             | 1.0.1           | BSD License                                                                                      |
| sphinxcontrib-jsmath             | 1.0.1           | BSD License                                                                                      |
| sphinxcontrib-programoutput      | 0.19            | BSD License                                                                                      |
| sphinxcontrib-programoutput      | 0.19            | BSD License                                                                                      |
| sphinxcontrib-qthelp             | 2.0.0           | BSD License                                                                                      |
| sphinxcontrib-qthelp             | 2.0.0           | BSD License                                                                                      |
| sphinxcontrib-serializinghtml    | 2.0.0           | BSD License                                                                                      |
| sphinxcontrib-serializinghtml    | 2.0.0           | BSD License                                                                                      |
| sphinxcontrib-spelling           | 8.0.2           | BSD License                                                                                      |
| sphinxcontrib-spelling           | 8.0.2           | BSD License                                                                                      |
| sphinxext-opengraph              | 0.13.0          | BSD-3-Clause                                                                                     |
| sphinxext-opengraph              | 0.13.0          | BSD-3-Clause                                                                                     |
| starlette                        | 1.0.0           | BSD-3-Clause                                                                                     |
| starlette                        | 1.0.0           | BSD-3-Clause                                                                                     |
| stevedore                        | 5.7.0           | Apache Software License                                                                          |
| stevedore                        | 5.7.0           | Apache Software License                                                                          |
| tabulate                         | 0.10.0          | MIT                                                                                              |
| tabulate                         | 0.10.0          | MIT                                                                                              |
| tenacity                         | 9.1.4           | Apache Software License                                                                          |
| tenacity                         | 9.1.4           | Apache Software License                                                                          |
| tinycss2                         | 1.5.1           | BSD License                                                                                      |
| tinycss2                         | 1.5.1           | BSD License                                                                                      |
| toml                             | 0.10.2          | MIT License                                                                                      |
| toml                             | 0.10.2          | MIT License                                                                                      |
| toml-fmt-common                  | 1.3.2           | MIT                                                                                              |
| toml-fmt-common                  | 1.3.2           | MIT                                                                                              |
| tomli_w                          | 1.2.0           | MIT License                                                                                      |
| tomli_w                          | 1.2.0           | MIT License                                                                                      |
| tomlkit                          | 0.14.0          | MIT License                                                                                      |
| tomlkit                          | 0.14.0          | MIT License                                                                                      |
| tox                              | 4.53.0          | MIT                                                                                              |
| tox                              | 4.53.0          | MIT                                                                                              |
| tox-uv                           | 1.35.1          | MIT                                                                                              |
| tox-uv                           | 1.35.1          | MIT                                                                                              |
| tox-uv-bare                      | 1.35.1          | MIT                                                                                              |
| tox-uv-bare                      | 1.35.1          | MIT                                                                                              |
| tqdm                             | 4.67.3          | MPL-2.0 AND MIT                                                                                  |
| tqdm                             | 4.67.3          | MPL-2.0 AND MIT                                                                                  |
| trove-classifiers                | 2026.1.14.14    | Apache Software License                                                                          |
| trove-classifiers                | 2026.1.14.14    | Apache Software License                                                                          |
| twine                            | 6.2.0           | Apache-2.0                                                                                       |
| twine                            | 6.2.0           | Apache-2.0                                                                                       |
| typer                            | 0.23.1          | MIT                                                                                              |
| typer                            | 0.23.1          | MIT                                                                                              |
| types-requests                   | 2.33.0.20260408 | Apache-2.0                                                                                       |
| types-requests                   | 2.33.0.20260408 | Apache-2.0                                                                                       |
| typing-inspection                | 0.4.2           | MIT                                                                                              |
| typing-inspection                | 0.4.2           | MIT                                                                                              |
| typing_extensions                | 4.15.0          | PSF-2.0                                                                                          |
| typing_extensions                | 4.15.0          | PSF-2.0                                                                                          |
| unimport                         | 1.3.1           | MIT License                                                                                      |
| unimport                         | 1.3.1           | MIT License                                                                                      |
| untokenize                       | 0.1.1           | MIT License                                                                                      |
| untokenize                       | 0.1.1           | MIT License                                                                                      |
| url-normalize                    | 2.2.1           | MIT                                                                                              |
| url-normalize                    | 2.2.1           | MIT                                                                                              |
| urllib3                          | 2.6.3           | MIT                                                                                              |
| urllib3                          | 2.6.3           | MIT                                                                                              |
| uv                               | 0.11.6          | MIT OR Apache-2.0                                                                                |
| uv                               | 0.11.6          | MIT OR Apache-2.0                                                                                |
| uvicorn                          | 0.44.0          | BSD-3-Clause                                                                                     |
| uvicorn                          | 0.44.0          | BSD-3-Clause                                                                                     |
| virtualenv                       | 21.2.4          | MIT                                                                                              |
| virtualenv                       | 21.2.4          | MIT                                                                                              |
| vulture                          | 2.16            | MIT License                                                                                      |
| vulture                          | 2.16            | MIT License                                                                                      |
| watchdog                         | 6.0.0           | Apache Software License                                                                          |
| watchdog                         | 6.0.0           | Apache Software License                                                                          |
| watchfiles                       | 1.1.1           | MIT License                                                                                      |
| watchfiles                       | 1.1.1           | MIT License                                                                                      |
| webencodings                     | 0.5.1           | BSD License                                                                                      |
| webencodings                     | 0.5.1           | BSD License                                                                                      |
| websockets                       | 16.0            | BSD-3-Clause                                                                                     |
| websockets                       | 16.0            | BSD-3-Clause                                                                                     |
| zipp                             | 3.23.1          | MIT                                                                                              |
| zipp                             | 3.23.1          | MIT                                                                                              |
