# NHL Scrabble - Implementation Tasks

This directory contains detailed task specifications for future improvements to the NHL Scrabble project. Each task is a self-contained document with clear requirements, implementation guidance, and acceptance criteria.

## Task Organization

Tasks are organized by category:

```
tasks/
├── bug-fixes/          # Bug fixes and corrections
├── security/           # Security improvements
├── optimization/       # Performance optimizations
├── enhancement/        # Feature enhancements
├── testing/            # Test coverage improvements
├── new-features/       # Major new features
└── refactoring/        # Code refactoring
```

## Priority Levels

Each task is assigned a priority:

- **CRITICAL** - Must Do (Immediately)
- **HIGH** - Must Do (Next Sprint)
- **MEDIUM** - Should Do (Next Month)
- **LOW** - Nice to Have (Next Quarter)

## Task Index

### Bug Fixes (0 tasks)

| ID  | Title | Priority | Effort | Issue |
| --- | ----- | -------- | ------ | ----- |
|     |       |          |        |       |

**Total Effort**: 0 hours

### Security (7 tasks, 7 documented)

| ID  | Title                            | Priority | Effort | Issue |
| --- | -------------------------------- | -------- | ------ | ----- |
| 002 | Comprehensive Input Validation   | MEDIUM   | 3-4h   | #129  |
| 003 | SSRF Protection                  | MEDIUM   | 2-3h   | #130  |
| 004 | Rate Limit Enforcement           | MEDIUM   | 3-4h   | #131  |
| 005 | DoS Prevention                   | LOW      | 2-3h   | #134  |
| 006 | SSL/TLS Certificate Verification | LOW      | 1-2h   | #135  |
| 007 | PII Logging Prevention           | LOW      | 2-3h   | #136  |
| 008 | Config Injection Protection      | LOW      | 2-3h   | #137  |

**Documented Effort**: 17-22.5 hours

### Optimization (11 tasks, 11 documented)

| ID  | Title                                    | Priority | Effort   | Issue |
| --- | ---------------------------------------- | -------- | -------- | ----- |
| 001 | Optimize Report String Concatenation     | HIGH     | 1-2h     | #112  |
| 002 | Implement Concurrent API Fetching        | HIGH     | 3-4h     | #113  |
| 003 | Use heapq.nlargest() for Top-N Queries   | MEDIUM   | 1-2h     | #114  |
| 004 | Single-Pass Aggregations in Stats Report | MEDIUM   | 1-2h     | #115  |
| 005 | Move Imports to Module Level             | LOW      | 15-30min | #116  |
| 006 | Add to_dict() Methods to Dataclasses     | MEDIUM   | 2-3h     | #117  |
| 007 | Lazy Report Generation                   | LOW      | 2-3h     | #138  |
| 008 | Memoized Scoring                         | LOW      | 1-2h     | #139  |
| 009 | Memory Optimization (__slots__)          | LOW      | 2-3h     | #140  |
| 010 | Rate Limiting on Cache Hits              | LOW      | 1-2h     | #141  |
| 011 | Log Level Optimization                   | LOW      | 1-2h     | #142  |

**Documented Effort**: 16-24.5 hours
**Expected Speedup**: 5-10x overall performance improvement (report generation: 3-5x, API fetching: 5-8x)

### Enhancements (9 tasks, 9 documented)

| ID  | Title                            | Priority | Effort | Issue |
| --- | -------------------------------- | -------- | ------ | ----- |
| 001 | Progress Bars                    | MEDIUM   | 2-3h   | #132  |
| 002 | Interactive Mode                 | MEDIUM   | 4-6h   | #133  |
| 003 | Historical Data                  | LOW      | 8-12h  | #143  |
| 004 | CSV/Excel Export                 | LOW      | 3-4h   | #144  |
| 005 | Advanced Filtering Options       | LOW      | 4-5h   | #145  |
| 006 | Custom Scoring Rules             | LOW      | 3-4h   | #146  |
| 007 | Interactive Statistics Dashboard | LOW      | 6-8h   | #147  |
| 008 | Watch Mode Auto-Refresh          | LOW      | 2-3h   | #148  |
| 009 | Player Search                    | LOW      | 3-4h   | #149  |

**Documented Effort**: 35-49 hours

### Testing (2 tasks, 2 documented)

| ID  | Title                                  | Priority | Effort   | Issue |
| --- | -------------------------------------- | -------- | -------- | ----- |
| 007 | Add pytest-benchmark Performance Tests | MEDIUM   | 1-2h     | #125  |
| 008 | Add check-jsonschema Validation        | LOW      | 30-60min | #128  |

**Documented Effort**: 1.5-3.0 hours

**Note**: Coverage target of 90.93% achieved. Codecov integration enabled for ongoing coverage tracking.

### New Features (13 tasks active, 15 documented, 2 completed)

| ID  | Title                        | Priority | Effort | Issue | Status      |
| --- | ---------------------------- | -------- | ------ | ----- | ----------- |
| 001 | Build Web Interface (Parent) | MEDIUM   | 16-24h | #50   | In Progress |
| 002 | FastAPI Infrastructure       | MEDIUM   | 3.5h   | #103  | ✅ Complete |
| 003 | Web API Endpoints            | MEDIUM   | 4-6h   | #104  |             |
| 004 | Web Frontend Templates       | MEDIUM   | 3.5h   | #105  | ✅ Complete |
| 005 | JavaScript Interactivity     | MEDIUM   | 8-12h  | #106  |             |
| 006 | Web Testing and Polish       | MEDIUM   | 2-3h   | #111  |             |
| 007 | Standalone REST API Server   | LOW      | 8-12h  | #150  |             |
| 008 | Database Backend             | LOW      | 12-16h | #151  |             |
| 009 | Notification System          | LOW      | 6-8h   | #152  |             |
| 010 | Player Comparison Tool       | LOW      | 4-6h   | #153  |             |
| 011 | Offline Mode                 | LOW      | 4-5h   | #154  |             |
| 012 | Config Profiles              | LOW      | 3-4h   | #155  |             |
| 013 | Plugin System                | LOW      | 10-14h | #156  |             |
| 014 | Docker Support               | LOW      | 4-6h   | #157  |             |
| 015 | Data Export/Import           | LOW      | 4-5h   | #158  |             |

**Documented Effort**: 87.5-126 hours (web interface subtasks: 14.5-21h remaining, standalone features: 70-100h)
**Completed**: 7 hours (Task 002: FastAPI Infrastructure 3.5h - PR #174, Task 004: Web Frontend Templates 3.5h - PR #176)

### Refactoring (6 tasks active, 7 documented, 1 completed)

| ID  | Title                              | Priority | Effort   | Issue |
| --- | ---------------------------------- | -------- | -------- | ----- |
| 002 | Improve Type Safety                | LOW      | 8-10h    | #160  |
| 003 | Unified Config Management          | LOW      | 5-6h     | #161  |
| 004 | Add pyupgrade Syntax Modernization | MEDIUM   | 1-2h     | #118  |
| 005 | Add djlint HTML Template Linting   | LOW      | 30-60min | #127  |
| 006 | Error Handling Strategy            | LOW      | 6-8h     | #162  |
| 007 | Dependency Injection               | LOW      | 8-10h    | #163  |

**Documented Effort**: 29-37.5 hours remaining

**Completed**: 3 hours (Task 001: Consolidate Report Classes 3h - PR #184)

## Total Project Roadmap

**Total Tasks**: 52 tasks (49 active, 3 completed)
**Remaining Effort**: 184.5-261 hours (10 hours completed)

### By Category

- **Security**: 7 tasks, 17-22.5h
- **Optimization**: 11 tasks, 16-24.5h (5-10x performance improvement)
- **Enhancement**: 9 tasks, 35-49h
- **Testing**: 2 tasks, 1.5-3.0h
- **New Features**: 13 tasks active (2 completed), 87.5-126h remaining (completed: 7h)
  - Web interface: 14.5-21h remaining (2 of 6 subtasks completed)
  - Standalone features: 70-100h
- **Refactoring**: 6 tasks active (1 completed), 29-37.5h remaining (completed: 3h)

### By Priority

- **MEDIUM**: 5 tasks remaining, 41.25-63h (web interface 5 tasks)
- **LOW**: 46 tasks, 152.75-209.5h (long-term improvements and new capabilities)

### Completed Tasks

- **Task 002** (new-features): FastAPI Infrastructure - 3.5h (PR #174, 2026-04-17)

## How to Use These Tasks

### For Implementation

1. **Choose a task** based on priority and available time
1. **Read the task file** completely - it contains:
   - Problem description
   - Current state analysis
   - Proposed solution with code examples
   - Testing strategy
   - Acceptance criteria
   - Related files
   - Dependencies
1. **Create a branch** for the task:
   ```bash
   git checkout -b feature/001-config-validation
   ```
1. **Implement** following the task specification
1. **Test** according to the testing strategy
1. **Verify** all acceptance criteria are met
1. **Update** any documentation mentioned
1. **Create PR** referencing the task file

### For Planning

Tasks can be used for:

- **Sprint planning**: Pick tasks by priority and effort
- **Time estimation**: Effort estimates provided for each task
- **Backlog grooming**: Tasks are pre-analyzed and ready
- **Knowledge transfer**: New contributors can pick up tasks independently

### For Tracking Progress

As tasks are completed:

1. Update the task file with:
   - ✅ Completed acceptance criteria
   - 📝 Implementation notes
   - 🔗 Links to PRs/commits
   - 📊 Actual vs estimated effort
1. Move completed task to `tasks/completed/` (optional)
1. Update this README to reflect progress

## Task Template

Each task follows this structure:

```markdown
# Task Title

## Priority
**PRIORITY_LEVEL** - Time Frame

## Estimated Effort
X-Y hours

## Description
Brief description of the problem/enhancement

## Current State
Current implementation with code examples

## Proposed Solution
Detailed solution with code examples

## Testing Strategy
How to test the implementation

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Related Files
- file1.py
- file2.py

## Dependencies
Required dependencies or other tasks

## Additional Notes
Any extra context, trade-offs, or considerations
```

## Recommended Implementation Order

This section organizes all documented tasks into a recommended implementation sequence based on priority, effort, dependencies, and impact.

### Phase 1: Critical Foundation (Week 1-2)

**Focus**: Critical security and bug fixes
**Total Effort**: All critical tasks completed! ✅

1. **security/001-dependabot.md** (30min) - #39 - Complete ✅

   - CRITICAL priority, quick win
   - Enables automated dependency updates
   - Completed 2026-04-16

1. **security/004-github-settings-security.md** (2-3h) - #62 - Complete ✅

   - CRITICAL priority, major security improvements
   - Branch protection, Dependabot alerts, CodeQL scanning
   - Completed 2026-04-16

1. **bug-fixes/001-config-validation.md** (2-4h) - #38 - Complete ✅

   - CRITICAL priority, prevents runtime errors
   - Validates configuration before execution
   - Completed 2026-04-16

1. **security/002-security-policy.md** (1h) - Complete ✅

   - Already completed (SECURITY.md created)

### Phase 2: High-Impact Improvements (Week 2-3)

**Focus**: Testing, performance, and important bug fixes
**Total Effort**: All tasks complete! ✅

1. **bug-fixes/002-unused-exception.md** (1-2h) - #40 - Complete ✅

   - HIGH priority, clean up exception handling
   - Quick fix with good impact
   - Completed 2026-04-16

1. **optimization/001-api-caching.md** (3-4h) - #42 - Complete ✅

   - HIGH priority, major performance improvement
   - 30x speedup for cached runs (30s → \<1s)
   - Completed 2026-04-16

1. **testing/001-increase-coverage.md** (8-12h) - #43 - Complete ✅

   - HIGH priority, foundation for quality
   - Increased coverage from 55.70% to 90.93% (+35.23pp)
   - Exceeded 80% target by 10.93pp
   - Completed 2026-04-16

### Phase 3: Medium Priority - Quality & Security (Week 4-5)

**Focus**: Security hardening and code quality
**Total Effort**: ~1-2 hours (2 tasks complete)

1. **security/003-secrets-sanitization.md** (2-3h) - #45 - Complete ✅

   - MEDIUM priority, prevents credential leaks
   - Important for production security
   - Completed 2026-04-16

1. **bug-fixes/006-output-validation.md** (1-2h) - #49 - Complete ✅

   - LOW priority but related to security
   - Validates CLI output paths before API calls
   - Completed 2026-04-16

1. **bug-fixes/003-session-cleanup.md** (1-2h) - #44

   - MEDIUM priority, safety net for session management
   - Prevents resource leaks
   - No dependencies

### Phase 4: Documentation Excellence (Week 6-8)

**Focus**: Comprehensive documentation system
**Total Effort**: All tasks complete! ✅

**Recommended order** (flexible based on needs):

1. **enhancement/002-procida-documentation.md** (8-12h) - #63 - Complete ✅

   - MEDIUM priority, organize documentation structure
   - Implement Diátaxis framework (tutorials/how-to/reference/explanation)
   - Do this FIRST to organize content
   - No dependencies
   - Completed 2026-04-16 (10h actual)

1. **enhancement/003-sphinx-documentation.md** (12-16h) - #64 - Complete ✅

   - MEDIUM priority, comprehensive Sphinx documentation with GitHub Pages
   - 9 modern Sphinx extensions, full API reference, automated deployment
   - MyST parser for seamless Markdown integration
   - Completed 2026-04-16 (8h actual)

1. **enhancement/004-automated-api-cli-docs.md** (4-6h) - #81 - Complete ✅

   - MEDIUM priority, automated API/CLI documentation
   - Uses pdoc for HTML API reference + custom script for CLI docs
   - Fast builds (\<2s), minimal dependencies
   - Completed 2026-04-16 (5.5h actual)

1. **enhancement/005-sphinx-quality-plugins.md** (2-4h) - #82 - Complete ✅

   - LOW priority, enhance Sphinx documentation quality

   - Completed 2026-04-16 (3.5h actual)

   - Quality plugins: coverage, linkcheck, doctest, sitemap, pytest-sphinx, blacken-docs

   - Can now be implemented as enhancement

### Phase 5: Performance & Polish (Week 9-10) - Complete ✅

**Focus**: Performance optimizations, enhancements, and polish
**Planned Effort**: ~9-19 hours
**Actual Effort**: 9.83h

1. **enhancement/002-project-logo-branding.md** (4-8h) - #89 - Complete ✅

   - MEDIUM priority, project branding
   - Create logo, favicons, and social media assets
   - Improves project professionalism and recognition
   - Completed 2026-04-17 (3h actual)

1. **testing/001-enable-codecov.md** (1-2h) - #90 - Complete ✅

   - MEDIUM priority, coverage tracking infrastructure
   - Enable Codecov integration for coverage trends
   - Fix "unknown" badge and 404 errors
   - Completed 2026-04-17 (0.58h actual)

1. **bug-fixes/004-rate-limiting.md** (1h) - #47 - Complete ✅

   - LOW priority, minor fix
   - Improves API rate limiting logic
   - Completed 2026-04-17 (0.75h actual)

1. **bug-fixes/005-exponential-backoff.md** (2-3h) - #48 - Complete ✅

   - LOW priority, improve retry reliability
   - Implements exponential backoff with jitter
   - Completed 2026-04-17 (2.5h actual)

1. **refactoring/001-extract-retry-logic.md** (2-3h) - #51 - Complete ✅

   - LOW priority, code organization
   - Extracts retry logic to reusable module
   - Completed 2026-04-17 (2.5h actual)

### Phase 6: Testing Infrastructure (Month 3)

**Focus**: Pytest plugins and testing improvements
**Total Effort**: 3.75-7.5 hours

1. **testing/001-add-pytest-timeout.md** (30-60min) - #119

   - MEDIUM priority, prevent hanging tests
   - Add pytest-timeout plugin
   - Essential for CI reliability

1. **testing/002-add-pytest-xdist.md** (30-60min) - #120

   - MEDIUM priority, parallel test execution
   - 10x faster test runs
   - Better developer experience

1. **testing/004-add-pytest-sugar.md** (15-30min) - #122

   - MEDIUM priority, enhanced test output
   - Better visual feedback
   - Instant failure display

1. **testing/005-add-pytest-clarity.md** (15-30min) - #123

   - MEDIUM priority, improved diffs
   - Better assertion failure messages
   - Faster debugging

1. **testing/006-add-diff-cover.md** (30-60min) - #124

   - MEDIUM priority, PR coverage tracking
   - Enforce coverage on new code
   - Prevent coverage regression

1. **testing/007-add-pytest-benchmark.md** (1-2h) - #125

   - MEDIUM priority, performance testing
   - Track optimization impact
   - Regression detection

1. **testing/008-add-check-jsonschema.md** (30-60min) - #128

   - LOW priority, JSON validation
   - Schema validation for configs
   - Better error messages

### Phase 7: Web Interface (Month 4-5)

**Focus**: Build comprehensive web UI
**Total Effort**: 38-55 hours (parent + subtasks)

1. **new-features/001-web-interface.md** (16-24h) - #50

   - MEDIUM priority, parent tracking task
   - Coordinate all web interface work
   - Depends on: Good test coverage

1. **new-features/002-fastapi-infrastructure.md** (3-4h) - #103

   - MEDIUM priority, FastAPI setup
   - Project structure, routing, templates
   - Foundation for all web features

1. **new-features/003-web-api-endpoints.md** (4-6h) - #104

   - MEDIUM priority, REST API endpoints
   - JSON API for frontend consumption
   - OpenAPI documentation

1. **new-features/004-web-frontend-templates.md** (4-6h) - #105

   - MEDIUM priority, HTML templates
   - Jinja2 templates with Tailwind CSS
   - Responsive design

1. **new-features/005-javascript-interactivity.md** (8-12h) - #106

   - MEDIUM priority, Alpine.js interactivity
   - Dynamic filtering, sorting
   - Real-time updates

1. **new-features/006-web-testing-polish.md** (2-3h) - #111

   - MEDIUM priority, testing and polish
   - Selenium tests, accessibility
   - Production-ready quality

### Phase 8: Future Enhancements (Backlog)

**Total Effort**: ~140-200 hours across 43 LOW priority tasks

All tasks now fully documented with implementation plans, acceptance criteria, and GitHub issues!

**Quick Wins** (under 4h each):

- security/001-add-pip-licenses-compliance.md (30-60min) - #126
- enhancement/003-comprehensive-documentation-badges.md (1-2h) - #91
- optimization/008-memoized-scoring.md (1-2h) - #139
- optimization/010-rate-limiting-cache-hits.md (1-2h) - #141
- optimization/011-log-level-optimization.md (1-2h) - #142
- security/006-ssl-verification.md (1-2h) - #135
- enhancement/008-watch-mode.md (2-3h) - #148
- security/007-pii-logging-prevention.md (2-3h) - #136
- security/008-config-injection-protection.md (2-3h) - #137
- security/005-dos-prevention.md (2-3h) - #134
- optimization/009-memory-optimization-slots.md (2-3h) - #140
- optimization/007-lazy-report-generation.md (2-3h) - #138
- enhancement/006-custom-scoring-rules.md (3-4h) - #146
- enhancement/009-player-search.md (3-4h) - #149
- enhancement/004-csv-excel-export.md (3-4h) - #144
- new-features/012-config-profiles.md (3-4h) - #155

**Medium Efforts** (4-8h):

- enhancement/005-filtering-options.md (4-5h) - #145
- new-features/011-offline-mode.md (4-5h) - #154
- new-features/015-data-export-import.md (4-5h) - #158
- new-features/010-player-comparison-tool.md (4-6h) - #153
- new-features/014-docker-support.md (4-6h) - #157
- refactoring/003-unified-config-management.md (5-6h) - #161
- refactoring/001-consolidate-reports.md (6-8h) - #159
- refactoring/006-error-handling-strategy.md (6-8h) - #162
- new-features/009-notification-system.md (6-8h) - #152
- enhancement/007-statistics-dashboard.md (6-8h) - #147

**Major Features** (8+ hours):

- refactoring/002-improve-type-safety.md (8-10h) - #160
- refactoring/007-dependency-injection.md (8-10h) - #163
- enhancement/003-historical-data.md (8-12h) - #143
- new-features/007-rest-api-server.md (8-12h) - #150
- new-features/013-plugin-system.md (10-14h) - #156
- new-features/008-database-backend.md (12-16h) - #151

For detailed implementation plans, see individual task files in:

- `tasks/security/` (8 tasks, 18-23.5h)
- `tasks/optimization/` (11 tasks, 16-24.5h)
- `tasks/enhancement/` (9 tasks, 35-49h)
- `tasks/new-features/` (15 tasks, 92-131h)
- `tasks/refactoring/` (7 tasks, 35-45.5h)

## Implementation Strategy

### Quick Wins (Do First)

Tasks with high impact and low effort:

1. security/001-add-pip-licenses-compliance.md (30-60min) - #126
1. Testing plugins (15-60min each):
   - testing/004-add-pytest-sugar.md (15-30min) - #122
   - testing/005-add-pytest-clarity.md (15-30min) - #123
   - testing/001-add-pytest-timeout.md (30-60min) - #119
   - testing/002-add-pytest-xdist.md (30-60min) - #120
   - testing/006-add-diff-cover.md (30-60min) - #124
1. All completed ✅

### Foundation (Do Early)

Critical for future work:

1. security/004-github-settings-security.md (2-3h) - Complete ✅
1. bug-fixes/001-config-validation.md (2-4h) - Complete ✅
1. testing/001-increase-coverage.md (8-12h) - Complete ✅
1. testing/007-add-pytest-benchmark.md (1-2h) - #125

### High Impact (Prioritize)

Major improvements with significant value:

1. optimization/001-api-caching.md (3-4h) - Complete ✅
1. enhancement/002-procida-documentation.md (8-12h) - Complete ✅
1. enhancement/003-sphinx-documentation.md (12-16h) - Complete ✅
1. enhancement/001-progress-bars.md (2-3h) - #132
1. enhancement/002-interactive-mode.md (4-6h) - #133

### Web Interface (Large Feature)

Complete web UI implementation:

1. new-features/001-web-interface.md (16-24h parent) - #50
1. new-features/002-fastapi-infrastructure.md (3-4h) - #103
1. new-features/003-web-api-endpoints.md (4-6h) - #104
1. new-features/004-web-frontend-templates.md (4-6h) - #105
1. new-features/005-javascript-interactivity.md (8-12h) - #106
1. new-features/006-web-testing-polish.md (2-3h) - #111

**Total**: 38-55 hours for complete web interface

### Nice to Have (Do Later)

Valuable but not critical:

1. Most LOW priority tasks (security hardening, optimization, refactoring)
1. Large features (REST API, database backend, plugin system)
1. Advanced enhancements (historical data, notifications)

## Sprint Planning Guide

### Sprint 1 (2 weeks): Critical Foundation - Complete ✅

**Planned Effort**: 6-8.5 hours
**Actual Effort**: 5.42 hours

- security/001 ✅ (0.42h actual)
- security/004 ✅ (1.5h actual)
- bug-fixes/001 ✅ (3h actual)
- security/002 ✅ (already complete)

### Sprint 2 (2 weeks): High Impact - Complete ✅

**Planned Effort**: 13-18 hours
**Actual Effort**: 9h

- bug-fixes/002 ✅ (1.5h actual)
- optimization/001 ✅ (3.5h actual)
- testing/001 ✅ (4h actual)

### Sprint 3 (2 weeks): Security & Quality - In Progress

**Planned Effort**: 2-4 hours
**Actual Effort**: 2.5h

- bug-fixes/003 (Session cleanup) - Remaining
- bug-fixes/006 (Output validation) - Remaining
- security/003 ✅ (2.5h actual) - Completed

### Sprint 4 (2 weeks): Documentation Part 1 - Complete ✅

**Planned Effort**: 8-12 hours
**Actual Effort**: 10h

- enhancement/002 ✅ (10h actual) - Procida documentation

### Sprint 5 (2 weeks): Documentation Part 2 - Complete ✅

**Planned Effort**: 12-16 hours
**Actual Effort**: 8h

- enhancement/003 ✅ (8h actual) - Sphinx + GitHub Pages

### Sprint 6 (2 weeks): Testing Infrastructure

**Planned Effort**: 3.75-7.5 hours

- testing/001-add-pytest-timeout (30-60min) - #119
- testing/002-add-pytest-xdist (30-60min) - #120
- testing/004-add-pytest-sugar (15-30min) - #122
- testing/005-add-pytest-clarity (15-30min) - #123
- testing/006-add-diff-cover (30-60min) - #124
- testing/007-add-pytest-benchmark (1-2h) - #125
- testing/008-add-check-jsonschema (30-60min) - #128

### Sprint 7-9 (6 weeks): Web Interface

**Planned Effort**: 38-55 hours (spread across 3 sprints)

**Sprint 7** (2 weeks): Foundation (7-10h)

- new-features/001-web-interface (tracking) - #50
- new-features/002-fastapi-infrastructure (3-4h) - #103
- new-features/003-web-api-endpoints (4-6h) - #104

**Sprint 8** (2 weeks): Frontend (12-18h)

- new-features/004-web-frontend-templates (4-6h) - #105
- new-features/005-javascript-interactivity (8-12h) - #106

**Sprint 9** (2 weeks): Polish & Launch (2-3h)

- new-features/006-web-testing-polish (2-3h) - #111
- Bug fixes and refinement from user feedback

### Sprint 10+ (Ongoing): Features & Refactoring

**Backlog** (~140-200 hours of documented LOW priority tasks):

- Security hardening (002-008): 17-22.5h
- Optimization improvements (007-011): 7-10h
- Enhancement features (001-002, 003-009): 29-40h
- New features (007-015): 54-76h
- Refactoring (001-003, 006-007): 33-42h

Pick tasks based on priority and available capacity

## Dependencies Graph

### No Dependencies (Can start anytime)

**Quick Wins** (independent tasks):

- All security tasks (001-008) - No dependencies
- All testing plugin tasks (001-008) - No dependencies
- Most optimization tasks (001-011) - Independent
- Most enhancement tasks (001-002, 003-009) - Independent
- Most refactoring tasks (001-007) - Can start anytime

**Exception**: Tasks requiring API changes or database backend should wait for their dependencies.

### Sequential Dependencies

**Security Chain**:

```
security/002-input-validation (#129)
└── security/003-ssrf-protection (#130)
    └── Can benefit from validated inputs
```

**Optimization Chain**:

```
optimization/001-api-caching (#42) ✅
└── optimization/010-rate-limiting-cache-hits (#141)
    └── Builds on caching implementation
```

**Testing Chain**:

```
All testing plugins (001-008) can be implemented independently in any order:
- testing/001-add-pytest-timeout (#119) - 30-60min
- testing/002-add-pytest-xdist (#120) - 30-60min
- testing/003-add-pytest-randomly (#121) - 15-30min ✅ COMPLETE
- testing/004-add-pytest-sugar (#122) - 15-30min
- testing/005-add-pytest-clarity (#123) - 15-30min
- testing/006-add-diff-cover (#124) - 30-60min
- testing/007-add-pytest-benchmark (#125) - 1-2h
- testing/008-add-check-jsonschema (#128) - 30-60min

Recommended order: 004, 005 (quick UX wins), then 001, 002 (infrastructure), then 006, 007, 008
```

**Enhancement Chain**:

```
enhancement/002-procida-documentation (#63) ✅
└── enhancement/003-sphinx-documentation (#64) ✅
    └── enhancement/004-automated-api-cli-docs (#81) ✅
        └── enhancement/005-sphinx-quality-plugins (#82) ✅

enhancement/001-progress-bars (#132)
└── Can enhance enhancement/002-interactive-mode (#133)
```

**New Features Chain**:

```
new-features/007-rest-api-server (#150)
└── new-features/008-database-backend (#151)
    └── new-features/009-notification-system (#152)
        └── Notifications benefit from database

new-features/001-web-interface (#50)
├── new-features/002-fastapi-infrastructure (#103)
├── new-features/003-web-api-endpoints (#104)
├── new-features/004-web-frontend-templates (#105)
├── new-features/005-javascript-interactivity (#106)
└── new-features/006-web-testing-polish (#111)
```

**Refactoring Chain**:

```
refactoring/001-consolidate-reports (#159)
└── Enables better type safety work

refactoring/002-improve-type-safety (#160)
└── refactoring/007-dependency-injection (#163)
    └── Type safety helps DI implementation
```

### Recommended Order for Maximum Value

**Phase 1: Foundation** (Completed ✅)

- Testing, security hardening, documentation

**Phase 2: Performance** (Next recommended)

1. optimization/001-011 (16-24.5h) - Quick wins with major impact
1. enhancement/001-002 (6-9h) - Progress bars + Interactive mode

**Phase 3: Security Hardening**

1. security/002-008 (17-22.5h) - Complete security posture

**Phase 4: User Features**

1. enhancement/003-009 (29-40h) - Historical data, export, filtering, etc.

**Phase 5: Major Features**

1. new-features/007-015 (54-76h) - REST API, database, plugins, etc.

**Phase 6: Code Quality**

1. refactoring/001-007 (35-45.5h) - Long-term maintainability

## Contributing

When adding new tasks:

1. Use the task template above
1. Place in appropriate category directory
1. Number sequentially (001, 002, ...)
1. Update this README index
1. Include realistic effort estimates
1. Provide comprehensive acceptance criteria

## Questions or Issues?

- **Missing context?** Check the comprehensive analysis that generated these tasks
- **Disagree with priority?** Priorities can be adjusted based on business needs
- **Found a task unclear?** Open an issue or update the task file with clarifications
- **Completed a task?** Update the task file and this README

## Metrics to Track

As tasks are completed, track:

- **Test Coverage**: Target 80%+ (currently 49%)
- **Cyclomatic Complexity**: Target \<10 (check with `radon cc src/`)
- **Performance**: API calls, runtime, memory usage
- **Security**: Vulnerabilities (should be 0 critical/high)
- **User Experience**: GitHub stars, issue resolution time, PyPI downloads

## Related Documentation

- **CLAUDE.md** - Project overview and development guide
- **README.md** - User-facing documentation
- **CONTRIBUTING.md** - Contribution guidelines
- **docs/DEVELOPMENT.md** - Development environment setup

______________________________________________________________________

**Last Updated**: 2026-04-17
**Tasks Documented**: 58 tasks across 6 categories
**Completion Status**: 33 completed, 25 planned
**Total Documented Effort**: 199.75-280 hours
**Completed Effort**: ~76.83 hours
**Remaining Effort**: ~122.92-203.17 hours

## Completed Tasks

| ID  | Title                                      | Category     | Completed  | Actual Effort | PR   |
| --- | ------------------------------------------ | ------------ | ---------- | ------------- | ---- |
| 002 | Link GitHub Issues to Tasks                | Enhancement  | 2026-04-16 | 0.75h         | #57  |
| 007 | Fix Branch Protection Hook in CI           | Bug Fix      | 2026-04-16 | 1h            | #59  |
| 002 | Implement CI Caching                       | Optimization | 2026-04-16 | 2.5h          | #61  |
| 001 | Add GitHub Dependabot                      | Security     | 2026-04-16 | 0.42h         | #65  |
| 002 | Create SECURITY.md Policy                  | Security     | 2026-04-16 | 0.5h          | #71  |
| 004 | GitHub Settings Security Hardening         | Security     | 2026-04-16 | 1.5h          | #71  |
| 001 | Fix Config Validation                      | Bug Fix      | 2026-04-16 | 3h            | #72  |
| 002 | Implement NHLApiNotFoundError              | Bug Fix      | 2026-04-16 | 1.5h          | #73  |
| 001 | Implement API Response Caching             | Optimization | 2026-04-16 | 3.5h          | #74  |
| 001 | Increase Test Coverage to 90.93%           | Testing      | 2026-04-16 | 4h            | #75  |
| 003 | Add Session Cleanup Safety Net             | Bug Fix      | 2026-04-16 | 1.5h          | #76  |
| 003 | Implement Log Sanitization                 | Security     | 2026-04-16 | 2.5h          | #78  |
| 006 | Validate CLI Output Paths                  | Bug Fix      | 2026-04-16 | 1.5h          | #79  |
| 002 | Implement Procida Documentation            | Enhancement  | 2026-04-16 | 10h           | #80  |
| 004 | Automated API/CLI Documentation            | Enhancement  | 2026-04-16 | 5.5h          | #85  |
| 003 | Build Sphinx Docs + GitHub Pages           | Enhancement  | 2026-04-16 | 8h            | #86  |
| 001 | Implement HTML Output Format               | Enhancement  | 2026-04-16 | 4h            | #92  |
| 005 | Add Sphinx Quality Plugins                 | Enhancement  | 2026-04-16 | 3.5h          | #87  |
| 006 | Skill Optimizations                        | Enhancement  | 2026-04-16 | 0.5h          | N/A  |
| 002 | Create Project Logo and Branding           | Enhancement  | 2026-04-17 | 3h            | #89  |
| 001 | Enable Codecov Integration                 | Testing      | 2026-04-17 | 0.58h         | #93  |
| 004 | Fix Rate Limiting Logic                    | Bug Fix      | 2026-04-17 | 0.75h         | #94  |
| 005 | Implement Exponential Backoff              | Bug Fix      | 2026-04-17 | 2.5h          | #95  |
| 001 | Extract Retry Logic                        | Refactoring  | 2026-04-17 | 2.5h          | #96  |
| 004 | Add Python 3.14 Support and Testing        | Enhancement  | 2026-04-17 | 0.75h         | #99  |
| 005 | Add Python 3.15-dev Support (Non-Blocking) | Enhancement  | 2026-04-17 | 1.5h          | #102 |
| 002 | Port check_docs.sh to Python               | Refactoring  | 2026-04-17 | 2h            | #109 |
| 003 | Port branch protection hook to Python      | Refactoring  | 2026-04-17 | 1.5h          | #110 |
| 001 | Add pip-licenses Compliance                | Security     | 2026-04-17 | 0.75h         | #164 |
| 003 | Add pytest-randomly for test randomization | Testing      | 2026-04-17 | 0.42h         | #165 |
| 004 | Add pytest-sugar Enhanced Output           | Testing      | 2026-04-17 | 0.33h         | #166 |
| 005 | Add pytest-clarity Improved Diffs          | Testing      | 2026-04-17 | 0.33h         | #167 |
| 001 | Add pytest-timeout Plugin                  | Testing      | 2026-04-17 | 0.75h         | #168 |
| 002 | Add pytest-xdist Parallel Testing          | Testing      | 2026-04-17 | 0.75h         | #169 |
| 006 | Add diff-cover PR Coverage                 | Testing      | 2026-04-17 | 0.75h         | #170 |
