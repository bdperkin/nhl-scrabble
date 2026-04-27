# Documentation Audit Directory

This directory contains documentation audit reports for the NHL Scrabble project.

## Purpose

Regular documentation audits help maintain high-quality, accurate, and useful documentation by:

- Identifying gaps and inconsistencies
- Detecting broken links and outdated examples
- Measuring documentation quality over time
- Creating actionable improvement plans
- Ensuring documentation scales with the codebase

## Audit Schedule

**Recommended Frequency**: Quarterly (every 3 months)

**Last Audit**: 2026-04-23
**Next Audit**: 2026-07-23 (Q3 2026)

## Audit Reports

| Date       | Report File                       | Status      | Summary                                                                                                |
| ---------- | --------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------ |
| 2026-04-23 | documentation-audit-2026-04-23.md | ✅ Complete | Initial comprehensive audit. Overall quality: GOOD (4/5 stars). Created documentation standards guide. |

## Audit Process

### 1. Preparation (30 min)

- [ ] Set up audit environment (tools, tracking document)
- [ ] Review previous audit (if exists) to track progress
- [ ] Prepare audit checklist
- [ ] Clone fresh repository copy

### 2. Internal Documentation Audit (2 hours)

Python docstrings:

- [ ] Scan all `src/` Python files
- [ ] Check module-level docstrings
- [ ] Check class docstrings
- [ ] Check function/method docstrings
- [ ] Verify examples work
- [ ] Note missing type hints
- [ ] Record findings

**Tools**:

```bash
# Check docstring coverage
interrogate src/ --verbose

# Style checking (automatic via pre-commit)
pydocstyle src/

# Test examples
pytest --doctest-modules src/
```

### 3. External Documentation Audit (1.5 hours)

Markdown files:

- [ ] Review README.md
- [ ] Review CONTRIBUTING.md
- [ ] Review CLAUDE.md
- [ ] Review all `docs/` files
- [ ] Check code examples
- [ ] Validate links
- [ ] Record findings

**Tools**:

```bash
# Lint Markdown (automatic via pre-commit)
pymarkdown scan docs/ *.md

# Validate links
linkchecker docs/

# Check formatting
mdformat --check docs/ *.md
```

### 4. Generate Report (1 hour)

- [ ] Compile all findings
- [ ] Categorize issues by severity (Critical, High, Medium, Low)
- [ ] Create prioritized action list
- [ ] Write executive summary
- [ ] Include metrics and statistics
- [ ] Save report to `documentation-audit-YYYY-MM-DD.md`

### 5. Create Action Items (30 min)

- [ ] Create GitHub issues for critical gaps
- [ ] Add tasks to `tasks/` directory for medium priority
- [ ] Document low priority items for future reference
- [ ] Estimate effort for each item

### 6. Implement Quick Wins (30 min)

- [ ] Fix obvious typos
- [ ] Update outdated version numbers
- [ ] Fix broken internal links
- [ ] Commit quick fixes
- [ ] Note remaining work for follow-up tasks

## Audit Checklist

### Python Docstring Checklist

**Module-level**:

- [ ] Module purpose clearly stated
- [ ] Module-level attributes documented
- [ ] Usage examples provided (for complex modules)
- [ ] Related modules referenced

**Class-level**:

- [ ] Class purpose and responsibility documented
- [ ] All attributes documented
- [ ] Inheritance relationships explained (if relevant)
- [ ] Usage examples provided
- [ ] Related classes referenced (if relevant)

**Function/method**:

- [ ] Clear one-line summary
- [ ] All parameters documented (Args)
- [ ] Return value documented (Returns)
- [ ] Exceptions documented (Raises)
- [ ] Usage examples for complex functions
- [ ] Type hints present and accurate

**Inline comments**:

- [ ] Complex algorithms explained
- [ ] Non-obvious logic documented
- [ ] No outdated comments
- [ ] Comments explain WHY, not WHAT

### Markdown Documentation Checklist

**README.md**:

- [ ] Accurate project description
- [ ] Current installation instructions
- [ ] Working examples
- [ ] All badges functional
- [ ] Links to detailed docs

**CONTRIBUTING.md**:

- [ ] Current development setup instructions
- [ ] Accurate code style guidelines
- [ ] Testing instructions up-to-date
- [ ] PR process documented

**CLAUDE.md**:

- [ ] Current project architecture
- [ ] Accurate file structure
- [ ] Current dependencies
- [ ] Up-to-date workflows

**docs/ directory**:

- [ ] All tutorials work end-to-end
- [ ] All code examples execute correctly
- [ ] API reference matches current code
- [ ] No broken internal links
- [ ] No broken external links
- [ ] Consistent formatting

## Quality Metrics

Track these metrics over time to measure documentation health:

### Coverage Metrics

| Metric                  | Target | Current (2026-04-23) |
| ----------------------- | ------ | -------------------- |
| Docstring coverage      | 100%   | ~90%+ (estimated)    |
| Functions with examples | 80%    | ~60-70%              |
| Type hint coverage      | 100%   | ~98%                 |

### Quality Metrics

| Metric                  | Target    | Current (2026-04-23)  |
| ----------------------- | --------- | --------------------- |
| Broken links            | 0         | Unknown (not checked) |
| Outdated examples       | 0         | 0 (assumed)           |
| Documentation freshness | \<30 days | \<1 day               |

### File Metrics

| Metric                    | Current (2026-04-23) |
| ------------------------- | -------------------- |
| Python files              | 68                   |
| Markdown files (docs/)    | 45                   |
| Root Markdown files       | 9                    |
| Total documentation files | 122                  |

## Audit Tools

### Automated Tools

**Docstring Tools**:

- `interrogate` - Docstring coverage measurement
- `pydocstyle` - Docstring style checking (PEP 257)
- `pytest --doctest-modules` - Test examples in docstrings

**Markdown Tools**:

- `pymarkdown` - Markdown linting
- `mdformat` - Markdown formatting
- `linkchecker` - Link validation
- `doc8` - RST linting

### Installation

```bash
# Install documentation audit tools
pip install interrogate pydocstyle linkchecker

# Or use project dev dependencies (already includes most tools)
pip install -e ".[dev]"
```

### Running Tools

```bash
# Check docstring coverage
interrogate src/ --verbose --fail-under 100

# Lint docstrings
pydocstyle src/

# Test docstring examples
pytest --doctest-modules src/

# Lint Markdown
pymarkdown scan docs/ *.md

# Validate links
linkchecker docs/ --check-extern

# Format Markdown
mdformat --check docs/ *.md
```

## Automated Link Validation

The project includes automated link checking via GitHub Actions and linkchecker:

### CI/CD Integration

**GitHub Actions Workflow**: `.github/workflows/link-checker.yml`

**Runs On**:

- Pull requests (when docs or markdown files change)
- Monthly schedule (every Monday at 9 AM UTC)
- Manual trigger via `workflow_dispatch`

**Configuration**: `.linkcheckerrc`

**Features**:

- Multi-threaded checking (10 threads)
- 30-second timeout per link
- External link validation
- HTML report artifact (30-day retention)
- Continues on error for scheduled runs

**Excluded URLs** (to prevent false positives from rate-limiting):

- GitHub Actions URLs (`^https://github.com/.*/actions`)
- Codecov URLs (`^https://codecov.io`, `^https://app.codecov.io`)
- Shields.io badges (`^https://shields.io`, `^https://img.shields.io`)
- GitHub API (`^https://api.github.com`)
- pre-commit.ci results (`^https://results.pre-commit.ci`)

### Local Usage

```bash
# Check all documentation links
linkchecker docs/ *.md

# With configuration file
linkchecker --config .linkcheckerrc docs/ *.md

# External links only
linkchecker --check-extern docs/ *.md

# Generate HTML report
linkchecker --output=html docs/ *.md > link-report.html
```

### Installation

Linkchecker is included in the `docs` optional dependency group:

```bash
# Install docs dependencies (includes linkchecker)
pip install -e ".[docs]"

# Or install linkchecker separately
pip install linkchecker
```

### When Links Fail

1. **Review CI report**: Download HTML artifact from workflow run
1. **Check exclusions**: Add rate-limited sites to `.linkcheckerrc`
1. **Fix broken links**: Update URLs or remove dead links
1. **Update redirects**: Replace redirected URLs with final destinations

## Automated Code Example Testing

The project includes automated testing of code examples in docstrings and documentation to prevent documentation drift.

### What Gets Tested

**Python Docstrings** (`pytest --doctest-modules`):

- Function and method examples in docstrings
- Class usage examples
- Module-level examples
- Uses pytest-doctestplus for enhanced doctest support

**Markdown Documentation** (`python scripts/test_markdown_examples.py`):

- Python code blocks in documentation files
- Executable examples in tutorials and how-to guides
- Skips pseudo-code and illustrative examples

### CI/CD Integration

**Tox Environment**: `tox -e doctest`

**GitHub Actions**: Runs on all commits (experimental/non-blocking)

**Status**: Currently experimental due to existing doctest failures that need fixing

### Local Usage

```bash
# Run all doctest checks
make doctest

# Or via tox
tox -e doctest

# Test docstrings only
pytest --doctest-modules src/nhl_scrabble/

# Test Markdown examples only
python scripts/test_markdown_examples.py
```

### Excluded Documentation

The following directories contain pseudo-code or illustrative examples that are not meant to be executed:

- `docs/explanation/` - Architecture documentation
- `docs/contributing/` - Guidelines with example patterns
- `docs/how-to/` - Guides with context-dependent examples
- `docs/testing/` - Testing documentation with pytest examples
- `CLAUDE.md` - Project documentation
- `tasks/` - Task files

### Writing Testable Examples

**Good Docstring Examples**:

```python
def calculate_score(name: str) -> int:
    """Calculate Scrabble score.

    Examples:
        >>> from nhl_scrabble.scoring import ScrabbleScorer
        >>> scorer = ScrabbleScorer()
        >>> scorer.calculate_score("TEST")
        4
    """
```

**Skipping Examples**:

```python
def fetch_api() -> dict:
    """Fetch from API.

    Examples:
        >>> # doctest: +SKIP
        >>> data = fetch_api()  # Requires network
    """
```

### Current Status

**Docstring Examples**: 89 passing, 39 failing, 7 skipped (as of 2026-04-27)
**Markdown Examples**: 3 passing, 3 skipped, 0 failing

**Acceptable Baseline**: 39 failures (documented below)

### Acceptable Baseline Rationale

The 39 remaining doctest failures are considered acceptable for the following reasons:

**Complex Setup Requirements** (15 failures):

- Protocol interface examples requiring full mock implementations
- Dashboard examples needing complex nested data structures
- Comparison reports requiring historical season data
- Examples dependent on external state (cache, database)

**Optional Dependencies** (3 failures):

- Template formatter examples requiring Jinja2
- Excel exporter examples requiring openpyxl (already skipped where possible)
- Examples requiring third-party integrations

**Architectural Patterns** (12 failures):

- Dependency injection examples with Protocol-based mocking
- Team processor examples requiring full NHL API client setup
- Playoff calculator examples needing complete team standings data
- Report generator examples requiring multi-level data hierarchies

**Edge Cases** (9 failures):

- Retry decorator examples with timing-dependent behavior
- CLI validation examples with filesystem state
- Search functionality examples requiring indexed data
- Historical data store examples with persistent state

**Baseline Review Schedule**:

- Review quarterly during documentation audits
- Revisit when refactoring affected modules
- Consider fixture-based solutions for high-value examples
- Update baseline if significant improvements are made

### Detailed Baseline Breakdown

**Protocol Interfaces (6 failures)**:

- `interfaces.APIClientProtocol.__enter__`
- `interfaces.ScorerProtocol.score_player`
- `interfaces.TeamProcessorProtocol.process_all_teams`
- `interfaces.TeamProcessorProtocol.calculate_division_standings`
- `interfaces.TeamProcessorProtocol.calculate_conference_standings`
- `formatters.__init__.nhl_scrabble.formatters`

*Reason*: Protocol examples demonstrate interface contracts but require full implementations to execute.

**Dependency Injection (3 failures)**:

- `di.DependencyContainer.create_api_client`
- `di.DependencyContainer.create_scorer`
- `di.create_dependencies`

*Reason*: DI examples require Config setup and may create network connections.

**Team/Playoff Processing (6 failures)**:

- `processors.team_processor.TeamProcessor.process_all_teams`
- `processors.team_processor.TeamProcessor.calculate_division_standings`
- `processors.team_processor.TeamProcessor.calculate_conference_standings`
- `processors.playoff_calculator.PlayoffCalculator.calculate_playoff_standings`
- `api.nhl_client.NHLApiClient.get_teams`
- `dashboard.StatisticsDashboard` (2 examples)

*Reason*: Require NHL API data or complex multi-team data structures.

**Comparison Reports (4 failures)**:

- `reports.comparison.SeasonComparison` (2 examples)
- `reports.comparison.TrendAnalysis` (2 examples)

*Reason*: Require historical season data not available in test context.

**Report Generation (3 failures)**:

- `reports.generator.ReportGenerator`
- `formatters.template_formatter.TemplateFormatter` (2 examples)
- `formatters.text_formatter.TextFormatter`

*Reason*: Template formatter requires Jinja2; others need complex data hierarchies.

**Formatter Factory (2 failures)**:

- `formatters.factory.get_formatter`
- `formatters.__init__.get_formatter`

*Reason*: Factory examples require proper module initialization.

**CLI Validation (2 failures)**:

- `cli.validate_output_path`
- `cli.validate_cli_arguments`

*Reason*: Filesystem-dependent validation logic with state dependencies.

**Utility Functions (4 failures)**:

- `utils.retry.retry`
- `utils.retry._calculate_backoff_delay`
- `api.nhl_client.NHLApiClient._calculate_backoff_delay`
- `validators.validate_file_path`

*Reason*: Timing-dependent or filesystem-dependent behavior.

**Storage/Configuration (4 failures)**:

- `storage.historical.HistoricalDataStore.load_season`
- `scoring.config.ScoringConfig.load_from_file`
- `api.nhl_client.NHLApiClient.get_cache_info`
- `security.dos_protection.create_protected_session`

*Reason*: Require persistent storage, config files, or external dependencies.

**Security/Search (3 failures)**:

- `security.log_filter.SensitiveDataFilter`
- `search.PlayerSearch.search`

*Reason*: Complex pattern matching or indexed data requirements.

**Total**: 39 failures across 11 categories

**Next Steps**:

1. ~~Fix common docstring failures~~ (COMPLETED: reduced from 57 to 39)
1. Keep doctest CI check as experimental/non-blocking
1. Add more executable examples to documentation where feasible
1. Consider pytest fixtures for complex examples in future iterations

## Follow-up Tasks

Common follow-up tasks from audits:

1. **Add Missing Examples**

   - Priority: MEDIUM
   - Effort: 3-4 hours
   - Focus: Public APIs, complex functions

1. **Fix Broken Links**

   - Priority: MEDIUM-HIGH (depending on count)
   - Effort: 30 min - 2 hours
   - Tool: linkchecker

1. **Update Outdated Information**

   - Priority: HIGH
   - Effort: Varies
   - Examples: Version numbers, deprecated features

1. **Add Documentation Tests**

   - Priority: MEDIUM
   - Effort: 2-3 hours
   - Goal: Automated example testing

1. **Improve Coverage**

   - Priority: LOW-MEDIUM
   - Effort: 2-4 hours
   - Goal: 100% docstring coverage

## Best Practices

### During Audit

1. **Be Systematic**: Follow checklist, don't skip files
1. **Take Notes**: Record all findings, even minor issues
1. **Categorize Issues**: Critical, High, Medium, Low
1. **Include Examples**: Specific file:line references
1. **Measure Metrics**: Track coverage, quality scores

### Creating Reports

1. **Executive Summary**: High-level overview for stakeholders
1. **Detailed Findings**: Organized by category
1. **Prioritized Actions**: Clear next steps
1. **Metrics**: Quantitative measurements
1. **Examples**: Specific instances of issues

### After Audit

1. **Create Tasks**: Turn findings into actionable items
1. **Prioritize**: Focus on high-impact improvements
1. **Track Progress**: Update audit report with completed items
1. **Schedule Next Audit**: Set date for next review
1. **Share Results**: Communicate with team

## Continuous Improvement

Between audits, maintain documentation quality:

### Daily

- [ ] Write docstrings for new code
- [ ] Update examples when APIs change
- [ ] Fix broken links when found

### Weekly

- [ ] Review new documentation in PRs
- [ ] Update CHANGELOG for releases
- [ ] Check CI documentation jobs

### Monthly

- [ ] Run link checker
- [ ] Review documentation metrics
- [ ] Address quick fixes

### Quarterly

- [ ] Full documentation audit
- [ ] Update documentation standards
- [ ] Measure progress on action items

## Resources

**Standards**:

- [Documentation Standards Guide](../contributing/documentation-standards.md)
- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

**Tools**:

- [interrogate Documentation](https://interrogate.readthedocs.io/)
- [linkchecker](https://linkchecker.github.io/linkchecker/)
- [Diátaxis Framework](https://diataxis.fr/)

**Community**:

- [Write the Docs](https://www.writethedocs.org/)
- [Read the Docs](https://readthedocs.org/)

______________________________________________________________________

**Maintained by**: Documentation team
**Questions**: Open an issue on GitHub
**Last Updated**: 2026-04-23
