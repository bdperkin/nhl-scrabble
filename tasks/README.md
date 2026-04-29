# NHL Scrabble Task Management

This directory contains all tasks for the NHL Scrabble project, organized by category and implementation status.

**Total Tasks**: 198 tasks (39 active, 159 completed)

## Overview

Tasks are organized into seven categories based on their nature:

1. **Bug Fixes**: Critical and high-priority bug resolutions
1. **Security**: Security enhancements and vulnerability fixes
1. **Optimization**: Performance improvements and optimizations
1. **Enhancement**: Feature improvements and refinements
1. **Testing**: Test coverage and quality improvements
1. **New Features**: Major new functionality
1. **Refactoring**: Code quality and maintainability improvements

Each task includes:

- Unique identifier (ID)
- Title and description
- Priority level (CRITICAL, HIGH, MEDIUM, LOW)
- Estimated effort
- GitHub issue reference
- Implementation status

## Priority Levels

- **CRITICAL**: Blocking issues, security vulnerabilities, data corruption - immediate action required
- **HIGH**: Important features, significant improvements, major bugs - prioritize in current sprint
- **MEDIUM**: Standard enhancements, minor bugs, nice-to-have features - schedule in upcoming sprints
- **LOW**: Future enhancements, optimizations, technical debt - backlog items

## Task Index

### Bug Fixes

| ID  | Title | Priority | Effort | Status | GitHub Issue | Notes |
| --- | ----- | -------- | ------ | ------ | ------------ | ----- |
| 001 | Fix Config Validation in Config.from_env() | CRITICAL | 2-4 hours (actual: ~3h) | Completed | [#38](https://github.com/bdperkin/nhl-scrabble/issues/38) | PR [#72](https://github.com/bdperkin/nhl-scrabble/pull/72), completed 2026-04-16 |
| 002 | Implement NHLApiNotFoundError Properly | HIGH | 1-2 hours (actual: ~1.5h) | Completed | [#40](https://github.com/bdperkin/nhl-scrabble/issues/40) | PR [#73](https://github.com/bdperkin/nhl-scrabble/pull/73), completed 2026-04-16 |
| 003 | Add Session Cleanup Safety Net | MEDIUM | 1-2 hours (actual: ~1.5h) | Completed | [#44](https://github.com/bdperkin/nhl-scrabble/issues/44) | PR [#76](https://github.com/bdperkin/nhl-scrabble/pull/76), completed 2026-04-16 |
| 004 | Fix Rate Limiting to Only Apply After Successful Requests | LOW | 1 hour (actual: ~45 minutes) | Completed | [#47](https://github.com/bdperkin/nhl-scrabble/issues/47) | completed 2026-04-16 |
| 005 | Implement Exponential Backoff for Retries | LOW | 2-3 hours (actual: ~2.5h) | Completed | [#48](https://github.com/bdperkin/nhl-scrabble/issues/48) | PR [#95](https://github.com/bdperkin/nhl-scrabble/pull/95), completed 2026-04-17 |
| 006 | Validate CLI Output Paths | LOW | 1-2 hours (actual: ~1.5 hours (middle of range)) | Completed | [#49](https://github.com/bdperkin/nhl-scrabble/issues/49) | PR [#79](https://github.com/bdperkin/nhl-scrabble/pull/79), completed 2026-04-16 |
| 007 | Fix Branch Protection Hook Failures in CI | HIGH | 1-2 hours (actual: ~1 hour) | Completed | [#58](https://github.com/bdperkin/nhl-scrabble/issues/58) | PR [#59](https://github.com/bdperkin/nhl-scrabble/pull/59), completed 2026-04-16 |
| 008 | Fix NHLApiClient Session Cleanup Warning | MEDIUM | 1-2 hours (actual: ~1.5h) | Completed | [#362](https://github.com/bdperkin/nhl-scrabble/issues/362) | PR [#367](https://github.com/bdperkin/nhl-scrabble/pull/367), completed 2026-04-24 |
| 009 | Verify and Validate Caching is Enabled by Default | MEDIUM | 2-3 hours (actual: ~2.5 hours) | Completed | [#365](https://github.com/bdperkin/nhl-scrabble/issues/365) | PR [#368](https://github.com/bdperkin/nhl-scrabble/pull/368), completed 2026-04-24 |
| 010 | Fix Output Format Validation Mismatch Between CLI and Config | HIGH | 30 minutes - 1 hour (actual: ~1 hour 15 minutes) | Completed | [#366](https://github.com/bdperkin/nhl-scrabble/issues/366) | PR [#385](https://github.com/bdperkin/nhl-scrabble/pull/385), completed 2026-04-25 |
| 011 | Use Platform-Specific Cache Directory with Permission Checking | MEDIUM | 3-4 hours (actual: ~3.5 hours) | Completed | [#369](https://github.com/bdperkin/nhl-scrabble/issues/369) | PR [#373](https://github.com/bdperkin/nhl-scrabble/pull/373), completed 2026-04-25 |
| 012 | Debug Functional Test Failures in QA Suite | MEDIUM | 1-2 hours (actual: ~1.5h) | Completed | [#438](https://github.com/bdperkin/nhl-scrabble/issues/438) | PR [#450](https://github.com/bdperkin/nhl-scrabble/pull/450), completed 2026-04-29 |
| 013 | Fix WCAG 2.1 AA Accessibility Violations in Web App | HIGH | 2-3 hours (actual: ~3.5h) | Completed | [#440](https://github.com/bdperkin/nhl-scrabble/issues/440) | PR [#449](https://github.com/bdperkin/nhl-scrabble/pull/449), completed 2026-04-29 |
| 014 | Fix QA Automation Test Failures (Functional and Accessibility) | HIGH | 4-6 hours | Active | [#454](https://github.com/bdperkin/nhl-scrabble/issues/454) | 2 functional test failures (CSP violations), 4-5 accessibility test failures |

### Security

| ID  | Title | Priority | Effort | Status | GitHub Issue | Notes |
| --- | ----- | -------- | ------ | ------ | ------------ | ----- |
| 011 | Monitor and Fix CVE-2026-3219 When pip Patch is Available | MEDIUM | Unknown | Active | [#375](https://github.com/bdperkin/nhl-scrabble/issues/375) | - |
| 012 | Add Local CodeQL Scanning Integration | MEDIUM | 4-6 hours (actual: ~1.5h) | Completed | [#389](https://github.com/bdperkin/nhl-scrabble/issues/389) | PR [#423](https://github.com/bdperkin/nhl-scrabble/pull/423), completed 2026-04-28 |
| 001 | Add pip-licenses for Dependency License Compliance | MEDIUM | 30-60 minutes (actual: 45 minutes) | Completed | [#126](https://github.com/bdperkin/nhl-scrabble/issues/126) | PR [#164](https://github.com/bdperkin/nhl-scrabble/pull/164), completed 2026-04-17 |
| 001 | Add GitHub Dependabot Configuration | CRITICAL | 30 minutes (actual: ~25 minutes) | Completed | [#39](https://github.com/bdperkin/nhl-scrabble/issues/39) | PR [#65](https://github.com/bdperkin/nhl-scrabble/pull/65), completed 2026-04-16 |
| 002 | Add Comprehensive Input Validation | MEDIUM | 3-4 hours (actual: ~3.5 hours) | Completed | [#129](https://github.com/bdperkin/nhl-scrabble/issues/129) | PR [#196](https://github.com/bdperkin/nhl-scrabble/pull/196), completed 2026-04-18 |
| 002 | Create SECURITY.md Policy | HIGH | 1 hour (actual: Part of PR #71 (total 1.5h for entire security settings)) | Completed | [#41](https://github.com/bdperkin/nhl-scrabble/issues/41) | PR [#71](https://github.com/bdperkin/nhl-scrabble/pull/71), completed 2026-04-16 |
| 003 | Implement Log Sanitization for Secrets | MEDIUM | 2-3 hours (actual: ~2.5h) | Completed | [#45](https://github.com/bdperkin/nhl-scrabble/issues/45) | PR [#78](https://github.com/bdperkin/nhl-scrabble/pull/78), completed 2026-04-16 |
| 003 | Add SSRF Protection for API Requests | MEDIUM | 2-3 hours (actual: ~45 minutes (implementation was already complete on branch from previous work)) | Completed | [#130](https://github.com/bdperkin/nhl-scrabble/issues/130) | PR [#181](https://github.com/bdperkin/nhl-scrabble/pull/181), completed 2026-04-18 |
| 004 | Implement Comprehensive GitHub Repository Settings Security Improvements | CRITICAL | 2-3 hours (actual: ~1.5 hours) | Completed | [#62](https://github.com/bdperkin/nhl-scrabble/issues/62) | PR [#71](https://github.com/bdperkin/nhl-scrabble/pull/71), completed 2026-04-16 |
| 004 | Implement API Rate Limit Enforcement | MEDIUM | 3-4 hours | Completed | [#131](https://github.com/bdperkin/nhl-scrabble/issues/131) | - |
| 005 | Add DoS Prevention Mechanisms | LOW | 2-3 hours (actual: ~2.5h) | Completed | [#134](https://github.com/bdperkin/nhl-scrabble/issues/134) | PR [#198](https://github.com/bdperkin/nhl-scrabble/pull/198), completed 2026-04-18 |
| 006 | Enforce SSL/TLS Certificate Verification | LOW | 1-2 hours (actual: ~1.5h) | Completed | [#135](https://github.com/bdperkin/nhl-scrabble/issues/135) | completed 2026-04-18 |
| 007 | Prevent PII Logging | LOW | 2-3 hours (actual: ~2.5 hours) | Completed | [#136](https://github.com/bdperkin/nhl-scrabble/issues/136) | PR [#200](https://github.com/bdperkin/nhl-scrabble/pull/200), completed 2026-04-18 |
| 008 | Protect Against Config Injection | LOW | 2-3 hours | Completed | [#137](https://github.com/bdperkin/nhl-scrabble/issues/137) | - |
| 009 | Add Bandit Security Linting for Python Code | HIGH | 1-2 hours (actual: ~1.5 hours) | Completed | [#239](https://github.com/bdperkin/nhl-scrabble/issues/239) | PR [#268](https://github.com/bdperkin/nhl-scrabble/pull/268), completed 2026-04-20 |
| 010 | Add Safety Dependency Vulnerability Scanning | HIGH | 1-2 hours (actual: 1.5 hours) | Completed | [#240](https://github.com/bdperkin/nhl-scrabble/issues/240) | PR [#269](https://github.com/bdperkin/nhl-scrabble/pull/269), completed 2026-04-20 |

### Optimization

| ID  | Title | Priority | Effort | Status | GitHub Issue | Notes |
| --- | ----- | -------- | ------ | ------ | ------------ | ----- |
| 001 | Implement API Response Caching | HIGH | 3-4 hours (actual: 3.5h) | Completed | [#42](https://github.com/bdperkin/nhl-scrabble/issues/42) | PR [#74](https://github.com/bdperkin/nhl-scrabble/pull/74), completed 2026-04-16 |
| 001 | Optimize Report String Concatenation Performance | HIGH | 1-2 hours | Completed | [#112](https://github.com/bdperkin/nhl-scrabble/issues/112) | - |
| 002 | Implement Concurrent API Fetching for Team Rosters | HIGH | 3-4 hours (actual: 3.5h) | Completed | [#113](https://github.com/bdperkin/nhl-scrabble/issues/113) | PR [#187](https://github.com/bdperkin/nhl-scrabble/pull/187), completed 2026-04-17 |
| 002 | Implement CI, Tox, Pre-commit, and Related Tools Caching | MEDIUM | 3-5 hours (actual: ~2.5 hours) | Completed | [#60](https://github.com/bdperkin/nhl-scrabble/issues/60) | PR [#61](https://github.com/bdperkin/nhl-scrabble/pull/61), completed 2026-04-16 |
| 003 | Use heapq.nlargest() for Top-N Player Queries | MEDIUM | 1-2 hours (actual: ~2.5h) | Completed | [#114](https://github.com/bdperkin/nhl-scrabble/issues/114) | PR [#188](https://github.com/bdperkin/nhl-scrabble/pull/188), completed 2026-04-17 |
| 004 | Optimize Stats Report with Single-Pass Aggregations | MEDIUM | 1-2 hours (actual: 1.5 hours) | Completed | [#115](https://github.com/bdperkin/nhl-scrabble/issues/115) | PR [#189](https://github.com/bdperkin/nhl-scrabble/pull/189), completed 2026-04-17 |
| 005 | Move Imports to Module Level in CLI | LOW | 15-30 minutes (actual: ~20 minutes) | Completed | [#116](https://github.com/bdperkin/nhl-scrabble/issues/116) | completed 2026-04-17 |
| 006 | Add to_dict() Methods to Dataclasses for Fast JSON Serialization | MEDIUM | 2-3 hours (actual: ~1.5h) | Completed | [#117](https://github.com/bdperkin/nhl-scrabble/issues/117) | PR [#191](https://github.com/bdperkin/nhl-scrabble/pull/191), completed 2026-04-17 |
| 007 | Implement Lazy Report Generation | LOW | 2-3 hours (actual: ~2.5h) | Completed | [#138](https://github.com/bdperkin/nhl-scrabble/issues/138) | PR [#192](https://github.com/bdperkin/nhl-scrabble/pull/192), completed 2026-04-17 |
| 008 | Add Memoization to Scrabble Scoring | LOW | 1-2 hours (actual: ~1.5h) | Completed | [#139](https://github.com/bdperkin/nhl-scrabble/issues/139) | PR [#193](https://github.com/bdperkin/nhl-scrabble/pull/193), completed 2026-04-17 |
| 009 | Memory Optimization with __slots__ | LOW | 2-3 hours (actual: ~1h) | Completed | [#140](https://github.com/bdperkin/nhl-scrabble/issues/140) | PR [#194](https://github.com/bdperkin/nhl-scrabble/pull/194), completed 2026-04-17 |
| 010 | Skip Rate Limiting on Cache Hits | LOW | 1-2 hours (actual: ~2 hours (based on commit timestamp and complexity)) | Completed | [#141](https://github.com/bdperkin/nhl-scrabble/issues/141) | PR [#182](https://github.com/bdperkin/nhl-scrabble/pull/182), completed 2026-04-17 |
| 011 | Optimize Logging with Level Guards | LOW | 1-2 hours (actual: 1.5h) | Completed | [#142](https://github.com/bdperkin/nhl-scrabble/issues/142) | PR [#195](https://github.com/bdperkin/nhl-scrabble/pull/195), completed 2026-04-17 |

### Enhancement

| ID  | Title | Priority | Effort | Status | GitHub Issue | Notes |
| --- | ----- | -------- | ------ | ------ | ------------ | ----- |
| 022 | Comprehensive GitHub Workflows Enhancement | MEDIUM | 24-32 hours (main task coordination + sub-tasks) | Completed | [#298](https://github.com/bdperkin/nhl-scrabble/issues/298) | - |
| 023 | Extend Sphinx Builder Functionality | LOW | 4-6 hours | Completed | [#331](https://github.com/bdperkin/nhl-scrabble/issues/331) | - |
| 024 | Extend Sphinx Extension Functionality | LOW | 3-5 hours | Completed | [#332](https://github.com/bdperkin/nhl-scrabble/issues/332) | - |
| 029 | Track ty Type Checker Validation Period (1-2 weeks) | MEDIUM | Unknown | Active | [#325](https://github.com/bdperkin/nhl-scrabble/issues/325) | - |
| 033 | Enhance Version Badge Display in README | LOW | 30 minutes - 1 hour | Completed | [#382](https://github.com/bdperkin/nhl-scrabble/issues/382) | - |
| 034 | Evaluate semantic-release for Fully Automated Releases | LOW | 6-10 hours (comprehensive evaluation + POC + recommendation) | Completed | [#383](https://github.com/bdperkin/nhl-scrabble/issues/383) | - |
| 035 | Add Comprehensive Bash Script Quality Tooling | MEDIUM | 6-8 hours (actual: ~7h) | Completed | [#424](https://github.com/bdperkin/nhl-scrabble/issues/424) | PR [#429](https://github.com/bdperkin/nhl-scrabble/pull/429), completed 2026-04-28 |
| 001 | Implement HTML Output Format | MEDIUM | 4-6 hours (actual: ~4h) | Completed | [#46](https://github.com/bdperkin/nhl-scrabble/issues/46) | PR [#92](https://github.com/bdperkin/nhl-scrabble/pull/92), completed 2026-04-16 |
| 001 | Add Progress Bars for Long Operations | MEDIUM | 2-3 hours (actual: ~3 hours) | Completed | [#132](https://github.com/bdperkin/nhl-scrabble/issues/132) | PR [#172](https://github.com/bdperkin/nhl-scrabble/pull/172), completed 2026-04-17 |
| 002 | Add Interactive Mode (REPL) | MEDIUM | 4-6 hours (actual: Implementation was already complete on this branch) | Completed | [#133](https://github.com/bdperkin/nhl-scrabble/issues/133) | completed 2026-04-17 |
| 002 | Link Existing GitHub Issues to Task Files | MEDIUM | 2-3 hours (actual: ~45 minutes) | Completed | [#55](https://github.com/bdperkin/nhl-scrabble/issues/55) | PR [#57](https://github.com/bdperkin/nhl-scrabble/pull/57), completed 2026-04-16 |
| 002 | Implement Procida's Documentation Model (Diátaxis Framework) | MEDIUM | 8-12 hours (actual: ~10 hours) | Completed | [#63](https://github.com/bdperkin/nhl-scrabble/issues/63) | PR [#80](https://github.com/bdperkin/nhl-scrabble/pull/80), completed 2026-04-16 |
| 002 | Create Project Logo and Branding Assets | MEDIUM | 4-8 hours (actual: ~3h) | Completed | [#89](https://github.com/bdperkin/nhl-scrabble/issues/89) | completed 2026-04-17 |
| 003 | Add Comprehensive Documentation Badges to README | LOW | 1-2 hours (actual: ~45 minutes) | Completed | [#91](https://github.com/bdperkin/nhl-scrabble/issues/91) | PR [#108](https://github.com/bdperkin/nhl-scrabble/pull/108), completed 2026-04-17 |
| 003 | Add Historical Data Support | LOW | 8-12 hours (actual: ~4h) | Completed | [#143](https://github.com/bdperkin/nhl-scrabble/issues/143) | PR [#202](https://github.com/bdperkin/nhl-scrabble/pull/202), completed 2026-04-18 |
| 003 | Build Comprehensive Sphinx Documentation with GitHub Pages | MEDIUM | 12-16 hours (actual: ~8 hours (including troubleshooting and CI fixes)) | Completed | [#64](https://github.com/bdperkin/nhl-scrabble/issues/64) | PR [#86](https://github.com/bdperkin/nhl-scrabble/pull/86), completed 2026-04-16 |
| 004 | Implement Automated API and CLI Documentation Generation | MEDIUM | 4-6 hours (actual: ~5.5h) | Completed | [#81](https://github.com/bdperkin/nhl-scrabble/issues/81) | PR [#85](https://github.com/bdperkin/nhl-scrabble/pull/85), completed 2026-04-16 |
| 004 | Add CSV and Excel Export | LOW | 3-4 hours (actual: ~3.5h) | Completed | [#144](https://github.com/bdperkin/nhl-scrabble/issues/144) | PR [#203](https://github.com/bdperkin/nhl-scrabble/pull/203), completed 2026-04-18 |
| 004 | Add Python 3.14 Support and Testing | MEDIUM | 2-3 hours (actual: ~45 minutes) | Completed | [#97](https://github.com/bdperkin/nhl-scrabble/issues/97) | PR [#99](https://github.com/bdperkin/nhl-scrabble/pull/99), completed 2026-04-17 |
| 005 | Add Advanced Filtering Options | LOW | 4-5 hours | Completed | [#145](https://github.com/bdperkin/nhl-scrabble/issues/145) | - |
| 005 | Add Python 3.15-dev Development Support | LOW | 1-2 hours (actual: ~1.5 hours (implementation, testing, documentation)) | Completed | [#98](https://github.com/bdperkin/nhl-scrabble/issues/98) | PR [#102](https://github.com/bdperkin/nhl-scrabble/pull/102), completed 2026-04-17 |
| 005 | Enhance Sphinx Documentation with Quality Plugins | LOW | 2-4 hours (actual: ~3.5h (including CI fixes)) | Completed | [#82](https://github.com/bdperkin/nhl-scrabble/issues/82) | PR [#87](https://github.com/bdperkin/nhl-scrabble/pull/87), completed 2026-04-16 |
| 006 | Add Custom Scoring Rules | LOW | 3-4 hours | Completed | [#146](https://github.com/bdperkin/nhl-scrabble/issues/146) | - |
| 006 | Skill Optimizations: Pre-Flight Validation and CI Diagnostics | HIGH | 0.5-1 hours (implementation complete, commit and document) (actual: ~0.5h) | Completed | [#88](https://github.com/bdperkin/nhl-scrabble/issues/88) | completed 2026-04-16 |
| 007 | Add Interactive Statistics Dashboard | LOW | 6-8 hours (actual: ~4 hours) | Completed | [#147](https://github.com/bdperkin/nhl-scrabble/issues/147) | completed 2026-04-18 |
| 008 | Add Watch Mode for Auto-Refresh | LOW | 2-3 hours (actual: ~2.5 hours) | Completed | [#148](https://github.com/bdperkin/nhl-scrabble/issues/148) | completed 2026-04-18 |
| 009 | Add Player Search Functionality | LOW | 3-4 hours | Completed | [#149](https://github.com/bdperkin/nhl-scrabble/issues/149) | - |
| 010 | Python 3.14 and 3.15-dev Support | MEDIUM | 3-5 hours (actual: ~2h) | Completed | [#217](https://github.com/bdperkin/nhl-scrabble/issues/217) | PR [#282](https://github.com/bdperkin/nhl-scrabble/pull/282), completed 2026-04-20 |
| 011 | Hyperlink Documentation to External Resources | LOW | 2-4 hours (actual: 3 hours) | Completed | [#223](https://github.com/bdperkin/nhl-scrabble/issues/223) | PR [#327](https://github.com/bdperkin/nhl-scrabble/pull/327), completed 2026-04-22 |
| 012 | Enhance Implement-Task Skill with Pre-Flight Validation | MEDIUM | 1-2 hours (actual: 1.5h) | Completed | [#225](https://github.com/bdperkin/nhl-scrabble/issues/225) | PR [#281](https://github.com/bdperkin/nhl-scrabble/pull/281), completed 2026-04-20 |
| 013 | Refine Project Logo Tiles and Hockey Stick Overlap | LOW | 1-2 hours (actual: ~2.5 hours (including reference material setup)) | Completed | [#227](https://github.com/bdperkin/nhl-scrabble/issues/227) | completed 2026-04-22 |
| 014 | Integrate Astral 'ty' Type Checker/LSP | LOW | 2-3 hours (actual: ~2.5 hours) | Completed | [#228](https://github.com/bdperkin/nhl-scrabble/issues/228) | completed 2026-04-21 |
| 015 | Add Standard Short Options to CLI Commands | LOW | 30-60 minutes (actual: ~45 minutes (within range)) | Completed | [#229](https://github.com/bdperkin/nhl-scrabble/issues/229) | PR [#320](https://github.com/bdperkin/nhl-scrabble/pull/320), completed 2026-04-21 |
| 016 | Format CLI Help Examples with Comments | LOW | 15-30 minutes (actual: ~25 minutes) | Completed | [#230](https://github.com/bdperkin/nhl-scrabble/issues/230) | completed 2026-04-21 |
| 017 | Expand CLI Output Formats | MEDIUM | 3.5-4.5 hours (actual: ~4 hours) | Completed | [#231](https://github.com/bdperkin/nhl-scrabble/issues/231) | PR [#328](https://github.com/bdperkin/nhl-scrabble/pull/328), completed 2026-04-22 |
| 018 | Support Additional Sphinx Output Formats | LOW | 2-3 hours (actual: ~3.5 hours) | Completed | [#232](https://github.com/bdperkin/nhl-scrabble/issues/232) | PR [#330](https://github.com/bdperkin/nhl-scrabble/pull/330), completed 2026-04-22 |
| 019 | Integrate Sphinx Doctest and Linkcheck into Build Process | LOW | 1-2 hours (actual: ~2.5 hours) | Completed | [#233](https://github.com/bdperkin/nhl-scrabble/issues/233) | PR [#333](https://github.com/bdperkin/nhl-scrabble/pull/333), completed 2026-04-22 |
| 020 | Enable Colorized Log Output Formatting | LOW | 30 minutes - 1 hour (actual: ~45 minutes) | Completed | [#234](https://github.com/bdperkin/nhl-scrabble/issues/234) | PR [#321](https://github.com/bdperkin/nhl-scrabble/pull/321), completed 2026-04-21 |
| 021 | Optimize Tox Execution with Parallel and Fail-Fast Behavior | LOW | 3-5 hours (actual: ~2 hours) | Completed | [#283](https://github.com/bdperkin/nhl-scrabble/issues/283) | PR [#326](https://github.com/bdperkin/nhl-scrabble/pull/326), completed 2026-04-22 |
| 025 | Add Automated Documentation Link Validation to CI | MEDIUM | 1 hour (actual: ~1.5 hours) | Completed | [#351](https://github.com/bdperkin/nhl-scrabble/issues/351) | PR [#394](https://github.com/bdperkin/nhl-scrabble/pull/394), completed 2026-04-26 |
| 026 | Add Automated Code Example Testing to CI | MEDIUM | 2 hours (actual: Fixed 18 common failures, documented 39 as acceptable baseline) | Completed | [#352](https://github.com/bdperkin/nhl-scrabble/issues/352) | PR [#408](https://github.com/bdperkin/nhl-scrabble/pull/408), completed 2026-04-27 |
| 027 | Improve Function Example Coverage in Docstrings | MEDIUM | 3-4 hours | Completed | [#353](https://github.com/bdperkin/nhl-scrabble/issues/353) | PR [#409](https://github.com/bdperkin/nhl-scrabble/pull/409), completed 2026-04-27 |
| 028 | Add Unicode Normalization for Player Names | MEDIUM | 2-3 hours (actual: ~2.5 hours) | Completed | [#363](https://github.com/bdperkin/nhl-scrabble/issues/363) | PR [#374](https://github.com/bdperkin/nhl-scrabble/pull/374), completed 2026-04-25 |
| 030 | Automate CHANGELOG Generation from Git Tags and Commits | MEDIUM | 4-6 hours (actual: ~4 hours) | Completed | - | PR [#410](https://github.com/bdperkin/nhl-scrabble/pull/410), completed 2026-04-27 |
| 031 | Add Version Validation in Pre-commit Hooks | MEDIUM | 1-2 hours (actual: ~1.5 hours) | Completed | - | PR [#411](https://github.com/bdperkin/nhl-scrabble/pull/411), completed 2026-04-27 |
| 032 | Create GitHub Release Notes from Tag Annotations | MEDIUM | 2-3 hours (actual: ~1.5 hours) | Completed | - | completed 2026-04-27 |
| 035 | Implement pre-commit.ci GitHub Automation | MEDIUM | 1-2 hours (actual: ~45 minutes) | Completed | [#391](https://github.com/bdperkin/nhl-scrabble/issues/391) | PR [#393](https://github.com/bdperkin/nhl-scrabble/pull/393), completed 2026-04-27 |
| 036 | Implement File-Based Logging for Uvicorn Web Server | MEDIUM | 3-5 hours (actual: ~3 hours) | Completed | - | PR [#413](https://github.com/bdperkin/nhl-scrabble/pull/413), completed 2026-04-27 |
| 037 | Documentation Refactoring and Web Interface Polish | MEDIUM | 16-24 hours (completed) | Completed | - | - |

### Testing

| ID  | Title | Priority | Effort | Status | GitHub Issue | Notes |
| --- | ----- | -------- | ------ | ------ | ------------ | ----- |
| 012 | QA Automation Framework | MEDIUM | 30-40 hours (actual: ~30h across 7 sub-tasks) | Completed | [#311](https://github.com/bdperkin/nhl-scrabble/issues/311) | All sub-tasks #013-#019 completed, final integration PR [#436](https://github.com/bdperkin/nhl-scrabble/pull/436), completed 2026-04-28 |
| 014 | Playwright Framework Setup | MEDIUM | 6-8 hours (actual: ~4h) | Completed | [#313](https://github.com/bdperkin/nhl-scrabble/issues/313) | PR [#430](https://github.com/bdperkin/nhl-scrabble/pull/430), completed 2026-04-28 |
| 015 | Functional Web Tests | MEDIUM | 6-8 hours (actual: ~4h) | Completed | [#316](https://github.com/bdperkin/nhl-scrabble/issues/316) | PR [#435](https://github.com/bdperkin/nhl-scrabble/pull/435), completed 2026-04-28 |
| 016 | Visual Regression Tests | MEDIUM | 4-6 hours (actual: ~3h) | Completed | [#317](https://github.com/bdperkin/nhl-scrabble/issues/317) | PR [#432](https://github.com/bdperkin/nhl-scrabble/pull/432), completed 2026-04-28 |
| 017 | Performance and Load Tests | MEDIUM | 4-6 hours (actual: ~6.5h) | Completed | [#314](https://github.com/bdperkin/nhl-scrabble/issues/314) | PR [#434](https://github.com/bdperkin/nhl-scrabble/pull/434), completed 2026-04-28 |
| 018 | Accessibility Tests | MEDIUM | 2-4 hours (actual: ~2.5h) | Completed | [#318](https://github.com/bdperkin/nhl-scrabble/issues/318) | PR [#431](https://github.com/bdperkin/nhl-scrabble/pull/431), completed 2026-04-28 |
| 019 | QA CI/CD Integration | MEDIUM | 2-4 hours (actual: ~2h) | Completed | [#315](https://github.com/bdperkin/nhl-scrabble/issues/315) | PR [#436](https://github.com/bdperkin/nhl-scrabble/pull/436), completed 2026-04-28 |
| 021 | Test Analytics and Coverage Analysis Tool | MEDIUM | 4-6 hours | Completed | [#359](https://github.com/bdperkin/nhl-scrabble/issues/359) | - |
| 001 | Add pytest-timeout to Prevent Hanging Tests | MEDIUM | 30-60 minutes (actual: ~45 minutes) | Completed | [#119](https://github.com/bdperkin/nhl-scrabble/issues/119) | PR [#168](https://github.com/bdperkin/nhl-scrabble/pull/168), completed 2026-04-17 |
| 001 | Implement Codecov Test Analytics in CI | MEDIUM | 2-3 hours (actual: ~2.5 hours) | Completed | [#211](https://github.com/bdperkin/nhl-scrabble/issues/211) | PR [#272](https://github.com/bdperkin/nhl-scrabble/pull/272), completed 2026-04-20 |
| 001 | Enable Codecov Integration for Code Coverage Tracking | MEDIUM | 1-2 hours (actual: ~35 minutes total) | Completed | [#90](https://github.com/bdperkin/nhl-scrabble/issues/90) | PR [#93](https://github.com/bdperkin/nhl-scrabble/pull/93), completed 2026-04-17 |
| 001 | Increase Test Coverage from 49% to 80%+ | HIGH | 8-12 hours (actual: ~4h) | Completed | [#43](https://github.com/bdperkin/nhl-scrabble/issues/43) | PR [#75](https://github.com/bdperkin/nhl-scrabble/pull/75), completed 2026-04-16 |
| 002 | Add pytest-xdist for Parallel Test Execution | MEDIUM | 30-60 minutes (actual: ~45 minutes) | Completed | [#120](https://github.com/bdperkin/nhl-scrabble/issues/120) | PR [#169](https://github.com/bdperkin/nhl-scrabble/pull/169), completed 2026-04-17 |
| 002 | Comprehensive Test Coverage Improvement (90-100%) | MEDIUM | 12-20 hours (actual: ~2 hours (audit + targeted improvements)) | Completed | [#221](https://github.com/bdperkin/nhl-scrabble/issues/221) | completed 2026-04-21 |
| 003 | Add pytest-randomly to Randomize Test Execution Order | MEDIUM | 15-30 minutes (actual: 25 minutes) | Completed | [#121](https://github.com/bdperkin/nhl-scrabble/issues/121) | PR [#165](https://github.com/bdperkin/nhl-scrabble/pull/165), completed 2026-04-17 |
| 003 | Add Unit and Integration Tests for Caching Layer | MEDIUM | 2-4 hours (actual: ~3h) | Completed | [#235](https://github.com/bdperkin/nhl-scrabble/issues/235) | PR [#284](https://github.com/bdperkin/nhl-scrabble/pull/284), completed 2026-04-20 |
| 004 | Add pytest-sugar for Enhanced Test Output | MEDIUM | 15-30 minutes (actual: ~20 minutes) | Completed | [#122](https://github.com/bdperkin/nhl-scrabble/issues/122) | PR [#166](https://github.com/bdperkin/nhl-scrabble/pull/166), completed 2026-04-17 |
| 004 | CLI Module Test Coverage (70% → 90%) | MEDIUM | 2-3 hours (actual: 2.5h) | Completed | [#253](https://github.com/bdperkin/nhl-scrabble/issues/253) | PR [#270](https://github.com/bdperkin/nhl-scrabble/pull/270), completed 2026-04-20 |
| 005 | Add pytest-clarity for Improved Assertion Diffs | MEDIUM | 15-30 minutes (actual: ~20 minutes) | Completed | [#123](https://github.com/bdperkin/nhl-scrabble/issues/123) | PR [#167](https://github.com/bdperkin/nhl-scrabble/pull/167), completed 2026-04-17 |
| 005 | Web Interface Test Coverage (30% → 85%) | MEDIUM | 3-4 hours (actual: ~6h total across 3 PRs) | Completed | [#254](https://github.com/bdperkin/nhl-scrabble/issues/254) | completed 2026-04-18 |
| 006 | Add diff-cover for PR Coverage Reporting | MEDIUM | 30-60 minutes (actual: ~45 minutes) | Completed | [#124](https://github.com/bdperkin/nhl-scrabble/issues/124) | PR [#170](https://github.com/bdperkin/nhl-scrabble/pull/170), completed 2026-04-17 |
| 006 | Interactive Mode Test Coverage (73.59% → 91.07%) | MEDIUM | 2-3 hours (actual: ~4h total) | Completed | [#255](https://github.com/bdperkin/nhl-scrabble/issues/255) | PR [#288](https://github.com/bdperkin/nhl-scrabble/pull/288), completed 2026-04-21 |
| 007 | Add pytest-benchmark for Performance Regression Testing | MEDIUM | 1-2 hours (actual: ~2.5h) | Completed | [#125](https://github.com/bdperkin/nhl-scrabble/issues/125) | PR [#178](https://github.com/bdperkin/nhl-scrabble/pull/178), completed 2026-04-17 |
| 007 | Configuration and Logging Test Coverage (55% → 90%) | MEDIUM | 1-2 hours (actual: ~1.5 hours) | Completed | [#256](https://github.com/bdperkin/nhl-scrabble/issues/256) | PR [#271](https://github.com/bdperkin/nhl-scrabble/pull/271), completed 2026-04-20 |
| 008 | Add check-jsonschema for JSON/YAML File Validation | LOW | 30-60 minutes (actual: ~45 minutes) | Completed | [#128](https://github.com/bdperkin/nhl-scrabble/issues/128) | completed 2026-04-17 |
| 008 | Reports Module Test Coverage (40% → 90%) | MEDIUM | 2-3 hours (actual: ~2.5h) | Completed | [#257](https://github.com/bdperkin/nhl-scrabble/issues/257) | PR [#289](https://github.com/bdperkin/nhl-scrabble/pull/289), completed 2026-04-21 |
| 009 | Edge Cases and Error Path Testing | MEDIUM | 2-3 hours (actual: 2.5 hours) | Completed | [#258](https://github.com/bdperkin/nhl-scrabble/issues/258) | completed 2026-04-21 |
| 010 | Integration and End-to-End Testing | MEDIUM | 2-3 hours | Completed | [#259](https://github.com/bdperkin/nhl-scrabble/issues/259) | completed 2026-04-21 |
| 011 | Coverage Audit and Finalization | MEDIUM | 2-3 hours | Completed | [#260](https://github.com/bdperkin/nhl-scrabble/issues/260) | completed 2026-04-21 |
| 013 | QA Infrastructure Setup | MEDIUM | 4-6 hours | Completed | [#312](https://github.com/bdperkin/nhl-scrabble/issues/312) | - |
| 020 | Implement Flaky Test Retry Mechanisms | MEDIUM | 6-10 hours (actual: ~4 hours) | Completed | [#322](https://github.com/bdperkin/nhl-scrabble/issues/322) | PR [#323](https://github.com/bdperkin/nhl-scrabble/pull/323), completed 2026-04-22 |
| 022 | Generate Visual Regression Test Baselines | MEDIUM | 30 minutes (actual: ~45 minutes) | Completed | [#437](https://github.com/bdperkin/nhl-scrabble/issues/437) | Chromium + Firefox baselines generated (28 snapshots), WebKit deferred to CI, completed 2026-04-29 |
| 023 | Make QA Workflow Blocking After All Tests Pass | LOW | 15 minutes | Active | [#439](https://github.com/bdperkin/nhl-scrabble/issues/439) | - |

### New Features

| ID  | Title | Priority | Effort | Status | GitHub Issue | Notes |
| --- | ----- | -------- | ------ | ------ | ------------ | ----- |
| 008 | Add Database Backend for Data Persistence | LOW | 12-16 hours | Completed | [#151](https://github.com/bdperkin/nhl-scrabble/issues/151) | - |
| 009 | Add Notification System | LOW | 6-8 hours | Completed | [#152](https://github.com/bdperkin/nhl-scrabble/issues/152) | - |
| 010 | Add Player Comparison Tool | LOW | 4-6 hours | Completed | [#153](https://github.com/bdperkin/nhl-scrabble/issues/153) | - |
| 011 | Add Offline Mode Support | LOW | 4-5 hours | Completed | [#154](https://github.com/bdperkin/nhl-scrabble/issues/154) | - |
| 012 | Add Configuration Profiles | LOW | 3-4 hours | Completed | [#155](https://github.com/bdperkin/nhl-scrabble/issues/155) | - |
| 013 | Add Plugin System | LOW | 10-14 hours | Completed | [#156](https://github.com/bdperkin/nhl-scrabble/issues/156) | - |
| 014 | Add Docker Support | LOW | 4-6 hours | Completed | [#157](https://github.com/bdperkin/nhl-scrabble/issues/157) | - |
| 015 | Add Data Export/Import Functionality | LOW | 4-5 hours | Completed | [#158](https://github.com/bdperkin/nhl-scrabble/issues/158) | - |
| 016 | Internationalization and Localization (i18n/l10n) | LOW | 32-48 hours | Active | [#218](https://github.com/bdperkin/nhl-scrabble/issues/218) | - |
| 017 | Free Python Hosting and Deployment Infrastructure | LOW | 8-12 hours | Active | [#219](https://github.com/bdperkin/nhl-scrabble/issues/219) | - |
| 018 | Automated Python Package Building and Publishing | MEDIUM | 4-6 hours (actual: ~8h total with enhancements) | Completed | [#224](https://github.com/bdperkin/nhl-scrabble/issues/224) | PR [#405](https://github.com/bdperkin/nhl-scrabble/pull/405), completed 2026-04-27 |
| 019 | Create Comprehensive Release Automation Skill | LOW | 8-12 hours | Completed | [#247](https://github.com/bdperkin/nhl-scrabble/issues/247) | - |
| 020 | CLI Internationalization Implementation | LOW | 4-6 hours | Completed | [#248](https://github.com/bdperkin/nhl-scrabble/issues/248) | - |
| 021 | Web Interface Internationalization Implementation | LOW | 6-8 hours | Completed | [#249](https://github.com/bdperkin/nhl-scrabble/issues/249) | - |
| 022 | TUI/Interactive Mode Internationalization | LOW | 3-4 hours | Completed | [#250](https://github.com/bdperkin/nhl-scrabble/issues/250) | - |
| 023 | Create Initial Translation File Structure | LOW | 2-3 hours | Completed | [#251](https://github.com/bdperkin/nhl-scrabble/issues/251) | - |
| 024 | Translate to Priority Languages | LOW | 8-12 hours | Completed | [#252](https://github.com/bdperkin/nhl-scrabble/issues/252) | - |
| 025 | Release Automation: Pre-Release Validation Phase | LOW | 1-2 hours | Completed | [#261](https://github.com/bdperkin/nhl-scrabble/issues/261) | - |
| 026 | Release Automation: Version Bumping Phase | LOW | 1-2 hours | Completed | [#262](https://github.com/bdperkin/nhl-scrabble/issues/262) | - |
| 027 | Release Automation: Build and Validate Phase | LOW | 1-2 hours | Completed | [#263](https://github.com/bdperkin/nhl-scrabble/issues/263) | - |
| 028 | Release Automation: Publish Phase | LOW | 1-2 hours | Completed | [#264](https://github.com/bdperkin/nhl-scrabble/issues/264) | - |
| 029 | Release Automation: Post-Release Phase | LOW | 1-2 hours | Completed | [#265](https://github.com/bdperkin/nhl-scrabble/issues/265) | - |
| 030 | Release Automation: Verification and Reporting Phase | LOW | 1-2 hours | Completed | [#266](https://github.com/bdperkin/nhl-scrabble/issues/266) | - |
| 031 | Release Automation: Orchestration and CLI Interface | LOW | 2-3 hours | Completed | [#267](https://github.com/bdperkin/nhl-scrabble/issues/267) | - |
| 034 | Docker Container Build and Publish Workflow | LOW | 3-4 hours | Completed | [#301](https://github.com/bdperkin/nhl-scrabble/issues/301) | - |
| 035 | PR Auto-Labeling Workflow | LOW | 1-2 hours | Completed | [#302](https://github.com/bdperkin/nhl-scrabble/issues/302) | - |
| 036 | PR Size Checker Workflow | LOW | 1-2 hours | Completed | [#303](https://github.com/bdperkin/nhl-scrabble/issues/303) | - |
| 043 | Nightly Comprehensive Testing Workflow | LOW | 2-3 hours | Completed | [#310](https://github.com/bdperkin/nhl-scrabble/issues/310) | - |
| 001 | Build Web Interface with FastAPI | MEDIUM | 16-24 hours (actual: <15 min (web interface already implemented, only needed task documentation)) | Completed | [#50](https://github.com/bdperkin/nhl-scrabble/issues/50) | completed 2026-04-26 |
| 002 | Add FastAPI Infrastructure and Web Server Foundation | MEDIUM | 3-4 hours (actual: ~3.5 hours) | Completed | [#103](https://github.com/bdperkin/nhl-scrabble/issues/103) | PR [#174](https://github.com/bdperkin/nhl-scrabble/pull/174), completed 2026-04-17 |
| 003 | Implement Web API Endpoints for NHL Scrabble Analysis | MEDIUM | 4-6 hours | Completed | [#104](https://github.com/bdperkin/nhl-scrabble/issues/104) | - |
| 004 | Build Frontend Templates and CSS for Web Interface | MEDIUM | 4-6 hours (actual: ~3.5 hours) | Completed | [#105](https://github.com/bdperkin/nhl-scrabble/issues/105) | PR [#176](https://github.com/bdperkin/nhl-scrabble/pull/176), completed 2026-04-17 |
| 005 | Add JavaScript Interactivity and Data Visualizations | MEDIUM | 8-12 hours (actual: GET endpoint with dual response (HTML for HTMX, JSON for API)) | Completed | [#106](https://github.com/bdperkin/nhl-scrabble/issues/106) | PR [#296](https://github.com/bdperkin/nhl-scrabble/pull/296), completed 2026-04-21 |
| 006 | Web Interface Testing and Polish | MEDIUM | 2-3 hours (actual: ~2.5 hours) | Completed | [#111](https://github.com/bdperkin/nhl-scrabble/issues/111) | PR [#297](https://github.com/bdperkin/nhl-scrabble/pull/297), completed 2026-04-21 |
| 007 | Add Standalone REST API Server | LOW | 8-12 hours | Completed | [#150](https://github.com/bdperkin/nhl-scrabble/issues/150) | - |
| 032 | PyPI Package Publishing Workflow | HIGH | 4-6 hours (actual: ~2.5 hours) | Completed | [#299](https://github.com/bdperkin/nhl-scrabble/issues/299) | PR [#405](https://github.com/bdperkin/nhl-scrabble/pull/405), completed 2026-04-27 |
| 033 | GitHub Release Automation Workflow | MEDIUM | 2-3 hours | Completed | [#300](https://github.com/bdperkin/nhl-scrabble/issues/300) | - |
| 037 | Stale Issue and PR Management Workflow | LOW | 1 hour (actual: ~45 minutes) | Completed | [#304](https://github.com/bdperkin/nhl-scrabble/issues/304) | PR [#395](https://github.com/bdperkin/nhl-scrabble/pull/395), completed 2026-04-26 |
| 038 | First-Time Contributor Welcome Workflow | LOW | 30 minutes - 1 hour (actual: ~45 minutes) | Completed | [#305](https://github.com/bdperkin/nhl-scrabble/issues/305) | PR [#397](https://github.com/bdperkin/nhl-scrabble/pull/397), completed 2026-04-27 |
| 039 | Performance Benchmark Testing Workflow | MEDIUM | 3-4 hours (actual: ~2.5h) | Completed | [#306](https://github.com/bdperkin/nhl-scrabble/issues/306) | PR [#421](https://github.com/bdperkin/nhl-scrabble/pull/421), completed 2026-04-28 |
| 040 | Software Bill of Materials (SBOM) Generation Workflow | MEDIUM | 2-3 hours (actual: ~2 hours) | Completed | [#307](https://github.com/bdperkin/nhl-scrabble/issues/307) | PR [#416](https://github.com/bdperkin/nhl-scrabble/pull/416), completed 2026-04-28 |
| 041 | SLSA Provenance Generation Workflow | MEDIUM | 2-3 hours (actual: ~2.5 hours) | Completed | [#308](https://github.com/bdperkin/nhl-scrabble/issues/308) | PR [#420](https://github.com/bdperkin/nhl-scrabble/pull/420), completed 2026-04-28 |
| 042 | Enhanced Dependency Review Workflow | MEDIUM | 1-2 hours (actual: ~1.5 hours) | Completed | [#309](https://github.com/bdperkin/nhl-scrabble/issues/309) | PR [#414](https://github.com/bdperkin/nhl-scrabble/pull/414), completed 2026-04-28 |

### Refactoring

| ID  | Title | Priority | Effort | Status | GitHub Issue | Notes |
| --- | ----- | -------- | ------ | ------ | ------------ | ----- |
| 024 | Make 'ty' Blocking After Validation Period | LOW | 30 minutes - 1 hour | Completed | [#355](https://github.com/bdperkin/nhl-scrabble/issues/355) | - |
| 001 | Consolidate Report Classes | LOW | 6-8 hours (actual: ~3 hours) | Completed | [#159](https://github.com/bdperkin/nhl-scrabble/issues/159) | PR [#184](https://github.com/bdperkin/nhl-scrabble/pull/184), completed 2026-04-17 |
| 001 | Extract Retry Logic to Reusable Decorator | LOW | 2-3 hours (actual: ~2.5h) | Completed | [#51](https://github.com/bdperkin/nhl-scrabble/issues/51) | PR [#96](https://github.com/bdperkin/nhl-scrabble/pull/96), completed 2026-04-17 |
| 002 | Improve Type Safety | LOW | 8-10 hours (actual: ~6 hours) | Completed | [#160](https://github.com/bdperkin/nhl-scrabble/issues/160) | PR [#354](https://github.com/bdperkin/nhl-scrabble/pull/354), completed 2026-04-24 |
| 002 | Port check_docs.sh Shell Script to Python | LOW | 2-3 hours (actual: ~2 hours) | Completed | [#100](https://github.com/bdperkin/nhl-scrabble/issues/100) | PR [#109](https://github.com/bdperkin/nhl-scrabble/pull/109), completed 2026-04-17 |
| 003 | Port check-branch-protection.sh Git Hook to Python | LOW | 1-2 hours (actual: ~1.5 hours) | Completed | [#101](https://github.com/bdperkin/nhl-scrabble/issues/101) | PR [#110](https://github.com/bdperkin/nhl-scrabble/pull/110), completed 2026-04-17 |
| 003 | Unified Configuration Management | LOW | 5-6 hours (actual: ~5h) | Completed | [#161](https://github.com/bdperkin/nhl-scrabble/issues/161) | PR [#358](https://github.com/bdperkin/nhl-scrabble/pull/358), completed 2026-04-24 |
| 004 | Add pyupgrade for Automatic Python Syntax Modernization | MEDIUM | 1-2 hours (actual: ~1.5h) | Completed | [#118](https://github.com/bdperkin/nhl-scrabble/issues/118) | PR [#336](https://github.com/bdperkin/nhl-scrabble/pull/336), completed 2026-04-22 |
| 005 | Add djlint for HTML and Jinja2 Template Linting | LOW | 30-60 minutes (actual: ~50 minutes) | Completed | [#127](https://github.com/bdperkin/nhl-scrabble/issues/127) | PR [#388](https://github.com/bdperkin/nhl-scrabble/pull/388), completed 2026-04-26 |
| 006 | Implement Consistent Error Handling Strategy | LOW | 6-8 hours (actual: ~4 hours) | Completed | [#162](https://github.com/bdperkin/nhl-scrabble/issues/162) | PR [#361](https://github.com/bdperkin/nhl-scrabble/pull/361), completed 2026-04-24 |
| 007 | Add Dependency Injection | LOW | 8-10 hours (actual: ~6 hours) | Completed | [#163](https://github.com/bdperkin/nhl-scrabble/issues/163) | completed 2026-04-24 |
| 008 | Repository Cleanup and Consolidation | MEDIUM | 4-6 hours (actual: 1.5h) | Completed | [#216](https://github.com/bdperkin/nhl-scrabble/issues/216) | PR [#278](https://github.com/bdperkin/nhl-scrabble/pull/278), completed 2026-04-20 |
| 009 | Git Branch Pruning Automation | LOW | 30-60 minutes (actual: 45 minutes) | Completed | [#220](https://github.com/bdperkin/nhl-scrabble/issues/220) | PR [#279](https://github.com/bdperkin/nhl-scrabble/pull/279), completed 2026-04-20 |
| 010 | Dynamic Versioning from Git Tags | LOW | 2-4 hours (actual: ~3.5 hours) | Completed | [#222](https://github.com/bdperkin/nhl-scrabble/issues/222) | PR [#378](https://github.com/bdperkin/nhl-scrabble/pull/378), completed 2026-04-25 |
| 011 | Dependency Synchronization and Automation | MEDIUM | 3-4 hours (actual: ~4.5 hours) | Completed | [#226](https://github.com/bdperkin/nhl-scrabble/issues/226) | PR [#341](https://github.com/bdperkin/nhl-scrabble/pull/341), completed 2026-04-23 |
| 012 | Audit and Standardize Command-Line Options for Consistency | MEDIUM | 2-4 hours (actual: ~5 hours) | Completed | [#236](https://github.com/bdperkin/nhl-scrabble/issues/236) | PR [#349](https://github.com/bdperkin/nhl-scrabble/pull/349), completed 2026-04-24 |
| 013 | Perform Project-Wide Documentation Audit | MEDIUM | 4-6 hours (actual: ~4 hours) | Completed | [#237](https://github.com/bdperkin/nhl-scrabble/issues/237) | completed 2026-04-23 |
| 014 | Add Refurb Python Code Modernization Linter | MEDIUM | 2-3 hours (actual: refurb reads pyproject.toml automatically, no flag needed) | Completed | [#241](https://github.com/bdperkin/nhl-scrabble/issues/241) | PR [#337](https://github.com/bdperkin/nhl-scrabble/pull/337), completed 2026-04-22 |
| 015 | Add pyproject-fmt Configuration Formatter | MEDIUM | 30 minutes - 1 hour (actual: ~45 minutes) | Completed | [#242](https://github.com/bdperkin/nhl-scrabble/issues/242) | PR [#386](https://github.com/bdperkin/nhl-scrabble/pull/386), completed 2026-04-25 |
| 016 | Add Trailing Comma Python Formatter | MEDIUM | 30 minutes - 1 hour (actual: 1.5 hours) | Completed | [#243](https://github.com/bdperkin/nhl-scrabble/issues/243) | PR [#387](https://github.com/bdperkin/nhl-scrabble/pull/387), completed 2026-04-26 |
| 017 | Extend JSON/YAML Schema Validation with check-jsonschema | MEDIUM | 1-2 hours (actual: 45 minutes) | Completed | [#244](https://github.com/bdperkin/nhl-scrabble/issues/244) | PR [#338](https://github.com/bdperkin/nhl-scrabble/pull/338), completed 2026-04-23 |
| 018 | Add check-wheel-contents Package Validator | LOW | 1-2 hours (actual: Implemented as local hook) | Completed | [#245](https://github.com/bdperkin/nhl-scrabble/issues/245) | PR [#339](https://github.com/bdperkin/nhl-scrabble/pull/339), completed 2026-04-23 |
| 019 | Add ssort Python Statement Sorter | LOW | 2-3 hours (actual: ~2.5 hours) | Completed | [#246](https://github.com/bdperkin/nhl-scrabble/issues/246) | PR [#340](https://github.com/bdperkin/nhl-scrabble/pull/340), completed 2026-04-23 |
| 020 | Migrate from Deprecated codecov/test-results-action to codecov/codecov-action | MEDIUM | 30min-1h (actual: ~30 minutes) | Completed | [#285](https://github.com/bdperkin/nhl-scrabble/issues/285) | PR [#372](https://github.com/bdperkin/nhl-scrabble/pull/372), completed 2026-04-24 |
| 021 | Comprehensive Task Documentation Synchronization and Validation | MEDIUM | 3-5 hours | Completed | [#286](https://github.com/bdperkin/nhl-scrabble/issues/286) | PR [#287](https://github.com/bdperkin/nhl-scrabble/pull/287), completed 2026-04-21 |
| 022 | Remove Backward Compatibility Code Before First Release | MEDIUM | 2-4 hours (actual: ~3.5h) | Completed | - | PR [#335](https://github.com/bdperkin/nhl-scrabble/pull/335), completed 2026-04-23 |
| 023 | Consolidate Exporters and Formatters Architecture | LOW | 3-5 hours (actual: ~2.5h) | Completed | - | PR [#377](https://github.com/bdperkin/nhl-scrabble/pull/377), completed 2026-04-25 |
| 025 | Make 'refurb' Blocking After Validation Period | LOW | 30 minutes - 1 hour (actual: ~1.5 hours) | Completed | - | PR [#370](https://github.com/bdperkin/nhl-scrabble/pull/370), completed 2026-04-24 |
| 026 | Make 'gitlint' Blocking (Everywhere Except GitHub CI Workflows) After Validation Period | LOW | 30 minutes - 1 hour (actual: ~45 minutes) | Completed | - | PR [#371](https://github.com/bdperkin/nhl-scrabble/pull/371), completed 2026-04-24 |
| 027 | Audit and Adjust Logging Levels | LOW | 2-3 hours (actual: 2.5 hours) | Completed | [#364](https://github.com/bdperkin/nhl-scrabble/issues/364) | completed 2026-04-25 |
