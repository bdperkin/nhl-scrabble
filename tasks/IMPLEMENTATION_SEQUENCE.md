# NHL Scrabble - Priority-Ordered Implementation Sequence

**Generated**: 2026-04-22 (fully synchronized)
**Total Tasks**: 70 active tasks
**Estimated Effort**: 529.0 hours
**Strategy**: Priority-first with dependency awareness

## How to Use This File

Each task is listed as a `/implement-task` command ready to execute. Tasks are ordered by:

1. **Priority** (CRITICAL → HIGH → MEDIUM → LOW)
1. **Dependencies** (prerequisites before dependents)
1. **Strategic Value** (foundation before features)
1. **Effort** (quick wins within same priority)

**Execute tasks in order** for optimal results. Dependencies are clearly marked.

______________________________________________________________________

## Phase 1: High Priority - GitHub Workflows & Deployment

**Total Effort**: 24-32 hours
**Focus**: Critical deployment infrastructure and release automation
**Dependencies**: Parent task before sub-tasks

```bash
# Comprehensive GitHub Workflows Parent Task
/implement-task enhancement/022-comprehensive-github-workflows.md  # 24-32h, Issue #298

# PyPI Publishing (Critical for releases)
/implement-task new-features/032-pypi-publish-workflow.md         # 4-6h, Issue #299
```

**Rationale**: Enhancement/022 is the parent coordinating task for 12 workflow sub-tasks. PyPI publishing (sub-task 1) is HIGH priority for automated releases.

______________________________________________________________________

## Phase 2: Medium Priority Workflows - Deployment & Security

**Total Effort**: 12-18 hours
**Focus**: Release automation, security, and quality workflows
**Dependencies**: Sub-tasks of enhancement/022, GitHub releases depends on PyPI

```bash
# Deployment Workflows
/implement-task new-features/033-github-release-workflow.md       # 2-3h, Issue #300

# Security & Quality Workflows
/implement-task new-features/039-benchmark-workflow.md            # 3-4h, Issue #306
/implement-task new-features/040-sbom-workflow.md                 # 2-3h, Issue #307
/implement-task new-features/041-provenance-workflow.md           # 2-3h, Issue #308
/implement-task new-features/042-dependency-review-workflow.md    # 1-2h, Issue #309
```

**Rationale**: GitHub releases depend on PyPI publishing. Security workflows (SBOM, provenance, dependency review) and quality workflows (benchmarking) are MEDIUM priority for supply chain security.

______________________________________________________________________

## Phase 3: QA Automation Framework - Infrastructure

**Total Effort**: 30-40 hours
**Focus**: Establish QA automation foundation for web testing
**Dependencies**: Parent task before framework setup, framework before specific tests

```bash
# QA Framework Parent Task
/implement-task testing/012-qa-automation-framework.md            # 30-40h, Issue #311

# Playwright Framework Setup (Foundation)
/implement-task testing/014-playwright-framework-setup.md         # 6-8h, Issue #313
```

**Rationale**: testing/012 is the parent task documenting full QA framework. testing/014 (Playwright setup) is the foundation that all other QA tests depend on.

______________________________________________________________________

## Phase 4: QA Test Implementation - Specific Test Types

**Total Effort**: 16-24 hours
**Focus**: Implement specific QA test suites
**Dependencies**: Requires Playwright framework (testing/014) completed

```bash
# Specific QA Test Types (Can be done in parallel after framework ready)
/implement-task testing/015-functional-web-tests.md               # 6-8h, Issue #316
/implement-task testing/017-performance-load-tests.md             # 4-6h, Issue #314
/implement-task testing/016-visual-regression-tests.md            # 4-6h, Issue #317
/implement-task testing/018-accessibility-tests.md                # 2-4h, Issue #318
```

**Rationale**: All specific test types depend on Playwright framework being set up. Ordered by priority: functional (critical user flows) → performance → visual → accessibility.

______________________________________________________________________

## Phase 5: QA CI/CD Integration

**Total Effort**: 2-4 hours
**Focus**: Integrate QA tests into CI/CD pipeline
**Dependencies**: Requires test suites to exist (testing/015-018)

```bash
# QA CI/CD Integration (After tests exist)
/implement-task testing/019-qa-cicd-integration.md                # 2-4h, Issue #315
```

**Rationale**: CI/CD integration must come after test suites are implemented. This makes QA tests run automatically on PRs and pushes.

______________________________________________________________________

## Phase 6: Low Priority Workflows - Automation & Nice-to-Haves

**Total Effort**: 9-13 hours
**Focus**: Developer experience and repository automation
**Dependencies**: Sub-tasks of enhancement/022, can be done in any order

```bash
# Container Workflow
/implement-task new-features/034-docker-build-publish-workflow.md  # 3-4h, Issue #301

# PR Automation
/implement-task new-features/035-pr-auto-label-workflow.md        # 1-2h, Issue #302
/implement-task new-features/036-pr-size-check-workflow.md        # 1-2h, Issue #303

# Repository Maintenance
/implement-task new-features/037-stale-management-workflow.md     # 1h, Issue #304
/implement-task new-features/038-welcome-contributor-workflow.md  # 30min-1h, Issue #305

# Comprehensive Testing
/implement-task new-features/043-nightly-testing-workflow.md      # 2-3h, Issue #310
```

**Rationale**: These are LOW priority quality-of-life improvements. Docker enables containerized deploys. PR automation improves contributor experience. Nightly testing catches environment-specific issues.

______________________________________________________________________

## Phase 7: Web Interface Completion (MEDIUM Priority)

**Total Effort**: 26-39 hours
**Focus**: Complete the web interface feature
**Dependencies**: Parent task documenting scope, sub-tasks already complete

```bash
# Web Interface Parent Task (documenting full scope)
/implement-task new-features/001-web-interface.md                 # 16-24h, Issue #50
```

**Rationale**: Task 001 is the parent task documenting the full web interface scope. Sub-tasks 002-006 are already complete (FastAPI infrastructure, API endpoints, templates, interactivity, testing/polish). This task provides comprehensive documentation and finalization.

______________________________________________________________________

## Phase 8: Developer Experience (MEDIUM Priority)

**Total Effort**: 5-9.5 hours
**Focus**: Improve developer workflow and tooling
**Dependencies**: None (independent enhancements)

```bash
# CLI Improvements (Quick wins first)
/implement-task enhancement/016-format-cli-help-examples.md       # 15-30min, Issue #230
/implement-task enhancement/015-add-cli-short-options.md          # 30-60min, Issue #229
/implement-task enhancement/020-colorized-log-output.md           # 30-60min, Issue #234

# Advanced Tooling
/implement-task enhancement/014-integrate-astral-ty-type-checker.md  # 2-3h, Issue #228
/implement-task enhancement/021-tox-parallel-failfast.md          # 3-5h, Issue #283
```

**Rationale**: CLI improvements enhance UX. Ordered by effort (quick wins first). Type checker (ty) complements mypy. Tox optimization speeds up local development and CI.

______________________________________________________________________

## Phase 9: Documentation & Output (MEDIUM Priority)

**Total Effort**: 8-13 hours
**Focus**: Enhanced documentation and output formats
**Dependencies**: None

```bash
# Documentation & Output
/implement-task enhancement/011-hyperlink-documentation.md         # 2-4h, Issue #223
/implement-task enhancement/017-expand-output-formats.md          # 3-4h, Issue #231
/implement-task enhancement/018-sphinx-additional-formats.md      # 2-3h, Issue #232
/implement-task enhancement/019-sphinx-doctest-linkcheck.md       # 1-2h, Issue #233
```

**Rationale**: Hyperlinks improve docs navigation. Output formats (YAML, XML) serve different use cases. Sphinx formats (PDF, EPUB) enhance documentation. Doctest/linkcheck ensure quality. Logical progression: navigation → output → formats → validation.

______________________________________________________________________

## Phase 10: Visual Polish (MEDIUM Priority)

**Total Effort**: 1-2 hours
**Focus**: Refine branding and visual elements
**Dependencies**: None

```bash
# Branding Refinement
/implement-task enhancement/013-refine-logo-branding.md           # 1-2h, Issue #227
```

**Rationale**: Logo tiles and hockey stick overlap need adjustment. Independent task, visual quality improvement.

______________________________________________________________________

## Phase 11: Repository Modernization (MEDIUM Priority)

**Total Effort**: 8.25-13.5 hours
**Focus**: Code modernization, formatting tools, and CI/CD maintenance
**Dependencies**: None (all independent tools)

```bash
# Modernization & Formatting Tools
/implement-task refactoring/004-add-pyupgrade-syntax-modernization.md    # 1-2h, Issue #118
/implement-task refactoring/014-add-refurb-modernization-linting.md      # 2-3h, Issue #241
/implement-task refactoring/015-add-pyproject-fmt-formatting.md          # 30-60min, Issue #242
/implement-task refactoring/016-add-trailing-comma-formatting.md         # 30-60min, Issue #243
/implement-task refactoring/017-extend-jsonschema-validation.md          # 1-2h, Issue #244
/implement-task refactoring/005-add-djlint-html-template-linting.md     # 30-60min, Issue #127
/implement-task refactoring/018-add-check-wheel-contents.md              # 1-2h, Issue #245
/implement-task refactoring/019-add-ssort-statement-sorting.md           # 2-3h, Issue #246
/implement-task refactoring/020-migrate-codecov-test-results-action.md   # 30-60min, Issue #285
```

**Rationale**: pyupgrade modernizes syntax. refurb finds improvements. pyproject-fmt standardizes config. Trailing-comma helps diffs. JSON schema validation catches errors. djlint improves HTML quality. Wheel validation ensures package quality. Statement sorting improves readability (requires consensus). Codecov migration from deprecated action. Order by impact.

______________________________________________________________________

## Phase 12: Repository Cleanup (MEDIUM Priority)

**Total Effort**: 13-20 hours
**Focus**: Organizational improvements and audits
**Dependencies**: Phase 11 modernization tools should run first

```bash
# Repository Organization
/implement-task refactoring/011-dependency-synchronization-automation.md  # 3-4h, Issue #226
/implement-task refactoring/012-cli-options-audit.md                 # 2-4h, Issue #236
/implement-task refactoring/013-documentation-audit.md               # 4-6h, Issue #237
```

**Rationale**: Dependency sync automates maintenance. CLI audit standardizes options. Docs audit ensures completeness. Sequential order for cumulative improvements.

______________________________________________________________________

## Phase 13: Package Automation (MEDIUM Priority)

**Total Effort**: 4-6 hours
**Focus**: Automated package building and publishing
**Dependencies**: Repository should be clean (Phase 12)

```bash
# Package Automation
/implement-task new-features/018-automated-python-package-building-publishing.md  # 4-6h, Issue #224
```

**Rationale**: Automates PyPI publishing workflow. Foundation for release automation. Should be implemented after repository cleanup.

______________________________________________________________________

## Phase 14: Release Automation (MEDIUM Priority, Sequential)

**Total Effort**: 17-26 hours
**Focus**: Complete release automation workflow
**Dependencies**: Sequential - each task depends on previous
**Prerequisite**: new-features/018 (package automation) from Phase 13
**Parent Task**: #247 - Create comprehensive release automation skill

```bash
# Release Automation Parent Task (documents full automation scope)
/implement-task new-features/019-comprehensive-release-automation-skill.md  # 8-12h, Issue #247

# Release Automation Pipeline Sub-tasks (MUST BE SEQUENTIAL)
/implement-task new-features/025-release-pre-release-validation.md   # 1-2h, Issue #261
/implement-task new-features/026-release-version-bumping.md          # 1-2h, Issue #262
/implement-task new-features/027-release-build-validate.md           # 1-2h, Issue #263
/implement-task new-features/028-release-publish.md                  # 1-2h, Issue #264
/implement-task new-features/029-release-post-release.md             # 1-2h, Issue #265
/implement-task new-features/030-release-verification.md             # 1-2h, Issue #266
/implement-task new-features/031-release-orchestration-cli.md        # 2-3h, Issue #267
```

**Rationale**: Task 019 is the parent task documenting comprehensive release automation. Sub-tasks 025-031 implement the sequential workflow: validate → version → build → publish → post-release → verify → orchestrate.

______________________________________________________________________

## Phase 15: Internationalization Infrastructure (MEDIUM Priority)

**Total Effort**: 36-54 hours
**Focus**: Full internationalization and localization (i18n/l10n) infrastructure
**Dependencies**: Infrastructure setup before component translation
**Parent Task**: #218 - Implement internationalization and localization

```bash
# i18n/l10n Parent Task (documents full i18n scope and infrastructure)
/implement-task new-features/016-internationalization-localization.md  # 32-48h, Issue #218
```

**Rationale**: Task 016 is the comprehensive parent task covering i18n infrastructure setup and overall l10n strategy. Infrastructure must be in place before internationalizing components (Phase 16).

______________________________________________________________________

## Phase 16: Internationalization Components (MEDIUM Priority, Semi-Sequential)

**Total Effort**: 23-33 hours
**Focus**: Multi-language support
**Dependencies**: Requires Phase 15 infrastructure
**Parent Task**: new-features/016 (#218)

```bash
# Component Internationalization (Can be parallel)
/implement-task new-features/020-i18n-cli-internationalization.md    # 4-6h, Issue #248
/implement-task new-features/021-i18n-web-internationalization.md    # 6-8h, Issue #249
/implement-task new-features/022-i18n-tui-internationalization.md    # 3-4h, Issue #250

# Translation Files (Requires 020-022 complete)
/implement-task new-features/023-i18n-create-translation-files.md    # 2-3h, Issue #251

# Actual Translations (Requires 023 complete)
/implement-task new-features/024-i18n-priority-language-translations.md  # 8-12h, Issue #252
```

**Rationale**: CLI, Web, TUI can be internationalized in parallel. Translation file creation requires code changes complete. Actual translations require translation files. Order: components → files → translations.

______________________________________________________________________

## Phase 17: Advanced Features - Data & Integration (MEDIUM Priority)

**Total Effort**: 28-40 hours
**Focus**: Database backend, plugins, notifications
**Dependencies**: None (independent features)

```bash
# Major Feature Additions
/implement-task new-features/008-database-backend.md                 # 12-16h, Issue #151
/implement-task new-features/013-plugin-system.md                    # 10-14h, Issue #156
/implement-task new-features/009-notification-system.md              # 6-8h, Issue #152
```

**Rationale**: Database enables persistence. Plugin system enables extensibility. Notifications enable monitoring. Order by complexity and impact: database → plugins → notifications.

______________________________________________________________________

## Phase 18: Advanced Features - Infrastructure (MEDIUM Priority)

**Total Effort**: 19-27 hours
**Focus**: Deployment and infrastructure
**Dependencies**: Docker benefits from database (Phase 17)

```bash
# Infrastructure & Deployment
/implement-task new-features/014-docker-support.md                   # 4-6h, Issue #157
/implement-task new-features/017-free-python-hosting-deployment.md   # 8-12h, Issue #219
/implement-task new-features/012-config-profiles.md                  # 3-4h, Issue #155
/implement-task new-features/015-data-export-import.md               # 4-5h, Issue #158
```

**Rationale**: Docker containerization. Free hosting deployment (Render, Railway, Fly.io). Config profiles for different environments. Data export/import for migrations. Order: docker → hosting → profiles → import/export.

______________________________________________________________________

## Phase 19: Advanced Features - User Tools (MEDIUM Priority)

**Total Effort**: 8-11 hours
**Focus**: User-facing tools and utilities
**Dependencies**: None

```bash
# User Utilities
/implement-task new-features/010-player-comparison-tool.md           # 4-6h, Issue #153
/implement-task new-features/011-offline-mode.md                     # 4-5h, Issue #154
```

**Rationale**: Player comparison adds analysis features. Offline mode enables usage without internet. Independent features, can be done in any order.

______________________________________________________________________

## Phase 20: Advanced Refactoring - Type Safety (MEDIUM Priority)

**Total Effort**: 13-16 hours
**Focus**: Comprehensive type safety improvements
**Dependencies**: Should come after modernization (Phase 11)

```bash
# Type Safety & Config
/implement-task refactoring/002-improve-type-safety.md               # 8-10h, Issue #160
/implement-task refactoring/003-unified-config-management.md         # 5-6h, Issue #161
```

**Rationale**: Type safety prevents runtime errors. Unified config simplifies management. Order: types → config (config benefits from better types).

______________________________________________________________________

## Phase 21: Advanced Refactoring - Architecture (MEDIUM Priority)

**Total Effort**: 16-20 hours
**Focus**: Architectural improvements
**Dependencies**: Should come after type safety (Phase 20)

```bash
# Architecture Improvements
/implement-task refactoring/007-dependency-injection.md              # 8-10h, Issue #163
/implement-task refactoring/006-error-handling-strategy.md           # 6-8h, Issue #162
/implement-task refactoring/010-dynamic-versioning-from-git-tags.md  # 2-4h, Issue #222
```

**Rationale**: Dependency injection improves testability. Error handling strategy ensures consistency. Dynamic versioning from git tags automates version management. Order: DI first (enables better error handling patterns), then versioning.

______________________________________________________________________

## Implementation Statistics

### By Priority

| Priority  | Tasks  | Effort       | Phases        |
| --------- | ------ | ------------ | ------------- |
| HIGH      | 1      | 4-6h         | Phase 1       |
| MEDIUM    | 71     | 525-723h     | Phase 2-21    |
| LOW       | 0      | 0h           | -             |
| **TOTAL** | **72** | **529-729h** | **21 Phases** |

### By Category

| Category     | Tasks  | Effort       |
| ------------ | ------ | ------------ |
| Enhancement  | 11     | 39.25-59.5h  |
| New Features | 44     | 420-585h     |
| Refactoring  | 10     | 21.75-32.5h  |
| Testing      | 7      | 48-52h       |
| **TOTAL**    | **72** | **529-729h** |

### Critical Path

**Foundation** (Phases 1-5): 88-117h

- GitHub workflows → QA framework → Test implementation

**Feature Completion** (Phases 7-10): 40-63.5h

- Web interface → Developer experience → Documentation → Branding

**Modernization** (Phases 11-13): 25.25-39.5h

- Code modernization → Repository cleanup → Package automation

**Automation** (Phase 14): 17-26h

- Release automation workflow (sequential)

**Internationalization** (Phases 15-16): 59-87h

- i18n infrastructure → Component translation

**Long-term** (Phases 17-21): 84-114h

- Advanced features, architectural refactoring

______________________________________________________________________

## Execution Guidelines

### Phase Sequencing

1. **Complete phases sequentially** where marked (especially Phase 14, 16)
1. **Within phases**, tasks can often be done in parallel unless noted
1. **Skip phases** that don't align with current goals
1. **Revisit** this file as priorities change

### Task Execution

```bash
# 1. Read the task file completely
cat tasks/<category>/<id>-<slug>.md

# 2. Create feature branch
git checkout -b <category>/<id>-<slug>

# 3. Implement using /implement-task
/implement-task <category>/<id>-<slug>.md

# 4. Follow the automated workflow:
#    - Pre-flight validation
#    - Implementation
#    - Testing
#    - Pre-commit hooks
#    - Create PR
#    - Wait for CI
#    - Merge
#    - Post-merge cleanup
```

### Progress Tracking

After completing each task:

1. Update task file with completion notes
1. Mark task complete in tasks/README.md
1. Move to tasks/completed/ (optional)
1. Update this file if priorities change

______________________________________________________________________

## Quick Reference

### Next 5 Tasks (Immediate Work)

```bash
/implement-task enhancement/022-comprehensive-github-workflows.md  # 24-32h, HIGH
/implement-task new-features/032-pypi-publish-workflow.md         # 4-6h, HIGH
/implement-task new-features/033-github-release-workflow.md       # 2-3h, MEDIUM
/implement-task new-features/039-benchmark-workflow.md            # 3-4h, MEDIUM
/implement-task new-features/040-sbom-workflow.md                 # 2-3h, MEDIUM
```

**Total**: 35-48 hours of high-value workflow automation

### Quick Wins (Under 1 hour each)

```bash
/implement-task enhancement/016-format-cli-help-examples.md          # 15-30min
/implement-task enhancement/015-add-cli-short-options.md             # 30-60min
/implement-task enhancement/020-colorized-log-output.md              # 30-60min
/implement-task refactoring/015-add-pyproject-fmt-formatting.md      # 30-60min
/implement-task refactoring/016-add-trailing-comma-formatting.md     # 30-60min
/implement-task refactoring/005-add-djlint-html-template-linting.md # 30-60min
/implement-task refactoring/020-migrate-codecov-test-results-action.md # 30-60min
/implement-task new-features/037-stale-management-workflow.md        # 1h
/implement-task new-features/038-welcome-contributor-workflow.md     # 30min-1h
```

**Total**: 3.5-7 hours of quick improvements

______________________________________________________________________

## Notes

**Last Updated**: 2026-04-22
**Active Tasks**: 72
**Completed Tasks**: 82
**Completion Rate**: 53.2% (82/154)

**Phase Distribution**:

- **Immediate** (Phases 1-5): 88-117h → Workflows + QA framework
- **Short-term** (Phases 7-13): 65.5-103h → Features + modernization + package automation
- **Mid-term** (Phase 14-16): 76-113h → Release automation + i18n
- **Long-term** (Phases 17-21): 84-114h → Advanced features + architecture

**Velocity Assumptions**:

- Conservative: 10h/sprint (2 weeks)
- Moderate: 15h/sprint
- Aggressive: 25h/sprint

See `tasks/README.md` for detailed task information and sprint planning.
