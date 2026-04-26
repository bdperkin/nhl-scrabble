# NHL Scrabble Task Management

This directory contains all tasks for the NHL Scrabble project, organized by category and implementation status.

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

| ID  | Title                                                     | Priority | Effort    | Status    | GitHub Issue                                              | Notes |
| --- | --------------------------------------------------------- | -------- | --------- | --------- | --------------------------------------------------------- | ----- |
| 001 | Fix Config Validation in Config.from_env()                | MEDIUM   | 2-4 hours | Completed | [#38](https://github.com/bdperkin/nhl-scrabble/issues/38) | -     |
| 002 | Implement NHLApiNotFoundError Properly                    | MEDIUM   | 1-2 hours | Completed | [#40](https://github.com/bdperkin/nhl-scrabble/issues/40) | -     |
| 003 | Add Session Cleanup Safety Net                            | MEDIUM   | 1-2 hours | Completed | [#44](https://github.com/bdperkin/nhl-scrabble/issues/44) | -     |
| 004 | Fix Rate Limiting to Only Apply After Successful Requests | MEDIUM   | 1 hour    | Completed | [#47](https://github.com/bdperkin/nhl-scrabble/issues/47) | -     |
| 005 | Implement Exponential Backoff for Retries                 | MEDIUM   | 2-3 hours | Completed | [#48](https://github.com/bdperkin/nhl-scrabble/issues/48) | -     |
| 006 | Validate CLI Output Paths                                 | MEDIUM   | 1-2 hours | Completed | [#49](https://github.com/bdperkin/nhl-scrabble/issues/49) | -     |
| 007 | Fix Branch Protection Hook Failures in CI                 | MEDIUM   | 1-2 hours | Completed | [#58](https://github.com/bdperkin/nhl-scrabble/issues/58)   | -     |
| 008 | Fix NHLApiClient Session Cleanup Warning                  | MEDIUM   | 1-2 hours | Completed | [#362](https://github.com/bdperkin/nhl-scrabble/issues/362) | PR [#367](https://github.com/bdperkin/nhl-scrabble/pull/367), completed 2026-04-25, actual effort: 1.5h |
| 009 | Verify and Validate Caching is Enabled by Default        | MEDIUM   | 2-3 hours | Completed | [#365](https://github.com/bdperkin/nhl-scrabble/issues/365) | PR [#368](https://github.com/bdperkin/nhl-scrabble/pull/368), completed 2026-04-24 |
| 010 | Fix Output Format Validation Mismatch Between CLI and Config | HIGH     | 30min-1h  | Completed | [#366](https://github.com/bdperkin/nhl-scrabble/issues/366) | PR [#385](https://github.com/bdperkin/nhl-scrabble/pull/385), completed 2026-04-25, actual effort: 1h 15min |
| 011 | Use Platform-Specific Cache Directory with Permission Checking | MEDIUM   | 3-4 hours | Completed | [#369](https://github.com/bdperkin/nhl-scrabble/issues/369) | PR [#373](https://github.com/bdperkin/nhl-scrabble/pull/373), completed 2026-04-25, actual effort: 3.5h |

### Security

| ID  | Title                                                                    | Priority | Effort        | Status    | GitHub Issue                                                | Notes |
| --- | ------------------------------------------------------------------------ | -------- | ------------- | --------- | ----------------------------------------------------------- | ----- |
| 001 | Add GitHub Dependabot Configuration                                      | MEDIUM   | 30 minutes    | Completed | [#39](https://github.com/bdperkin/nhl-scrabble/issues/39)   | -     |
| 001 | Add pip-licenses for Dependency License Compliance                       | MEDIUM   | 30-60 minutes | Completed | [#126](https://github.com/bdperkin/nhl-scrabble/issues/126) | -     |
| 002 | Create SECURITY.md Policy                                                | MEDIUM   | 1 hour        | Completed | [#41](https://github.com/bdperkin/nhl-scrabble/issues/41)   | -     |
| 002 | Add Comprehensive Input Validation                                       | MEDIUM   | 3-4 hours     | Completed | [#129](https://github.com/bdperkin/nhl-scrabble/issues/129) | -     |
| 003 | Implement Log Sanitization for Secrets                                   | MEDIUM   | 2-3 hours     | Completed | [#45](https://github.com/bdperkin/nhl-scrabble/issues/45)   | -     |
| 003 | Add SSRF Protection for API Requests                                     | MEDIUM   | 2-3 hours     | Completed | [#130](https://github.com/bdperkin/nhl-scrabble/issues/130) | -     |
| 004 | Implement Comprehensive GitHub Repository Settings Security Improvements | MEDIUM   | 2-3 hours     | Completed | [#62](https://github.com/bdperkin/nhl-scrabble/issues/62)   | -     |
| 004 | Implement API Rate Limit Enforcement                                     | MEDIUM   | 3-4 hours     | Completed | [#131](https://github.com/bdperkin/nhl-scrabble/issues/131) | -     |
| 005 | Add DoS Prevention Mechanisms                                            | MEDIUM   | 2-3 hours     | Completed | [#134](https://github.com/bdperkin/nhl-scrabble/issues/134) | -     |
| 006 | Enforce SSL/TLS Certificate Verification                                 | MEDIUM   | 1-2 hours     | Completed | [#135](https://github.com/bdperkin/nhl-scrabble/issues/135) | -     |
| 007 | Prevent PII Logging                                                      | MEDIUM   | 2-3 hours     | Completed | [#136](https://github.com/bdperkin/nhl-scrabble/issues/136) | -     |
| 008 | Protect Against Config Injection                                         | MEDIUM   | 2-3 hours     | Completed | [#137](https://github.com/bdperkin/nhl-scrabble/issues/137) | -     |
| 009 | Add Bandit Security Linting for Python Code                              | MEDIUM   | 1-2 hours     | Completed | [#239](https://github.com/bdperkin/nhl-scrabble/issues/239) | -     |
| 010 | Add Safety Dependency Vulnerability Scanning                             | MEDIUM   | 1-2 hours     | Completed | [#240](https://github.com/bdperkin/nhl-scrabble/issues/240) | -     |
| 011 | Monitor and Fix CVE-2026-3219 When pip Patch is Available                | MEDIUM   | 30min-1h      | Active    | [#375](https://github.com/bdperkin/nhl-scrabble/issues/375) | Security monitoring for pip vulnerability |

### Optimization

| ID  | Title                                                            | Priority | Effort        | Status    | GitHub Issue                                                | Notes |
| --- | ---------------------------------------------------------------- | -------- | ------------- | --------- | ----------------------------------------------------------- | ----- |
| 001 | Implement API Response Caching                                   | MEDIUM   | 3-4 hours     | Completed | [#42](https://github.com/bdperkin/nhl-scrabble/issues/42)   | -     |
| 001 | Optimize Report String Concatenation Performance                 | MEDIUM   | 1-2 hours     | Completed | [#112](https://github.com/bdperkin/nhl-scrabble/issues/112) | -     |
| 002 | Implement CI, Tox, Pre-commit, and Related Tools Caching         | MEDIUM   | 3-5 hours     | Completed | [#60](https://github.com/bdperkin/nhl-scrabble/issues/60)   | -     |
| 002 | Implement Concurrent API Fetching for Team Rosters               | MEDIUM   | 3-4 hours     | Completed | [#113](https://github.com/bdperkin/nhl-scrabble/issues/113) | -     |
| 003 | Use heapq.nlargest() for Top-N Player Queries                    | MEDIUM   | 1-2 hours     | Completed | [#114](https://github.com/bdperkin/nhl-scrabble/issues/114) | -     |
| 004 | Optimize Stats Report with Single-Pass Aggregations              | MEDIUM   | 1-2 hours     | Completed | [#115](https://github.com/bdperkin/nhl-scrabble/issues/115) | -     |
| 005 | Move Imports to Module Level in CLI                              | MEDIUM   | 15-30 minutes | Completed | [#116](https://github.com/bdperkin/nhl-scrabble/issues/116) | -     |
| 006 | Add to_dict() Methods to Dataclasses for Fast JSON Serialization | MEDIUM   | 2-3 hours     | Completed | [#117](https://github.com/bdperkin/nhl-scrabble/issues/117) | -     |
| 007 | Implement Lazy Report Generation                                 | MEDIUM   | 2-3 hours     | Completed | [#138](https://github.com/bdperkin/nhl-scrabble/issues/138) | -     |
| 008 | Add Memoization to Scrabble Scoring                              | MEDIUM   | 1-2 hours     | Completed | [#139](https://github.com/bdperkin/nhl-scrabble/issues/139) | -     |
| 009 | Memory Optimization with __slots__                               | MEDIUM   | 2-3 hours     | Completed | [#140](https://github.com/bdperkin/nhl-scrabble/issues/140) | -     |
| 010 | Skip Rate Limiting on Cache Hits                                 | MEDIUM   | 1-2 hours     | Completed | [#141](https://github.com/bdperkin/nhl-scrabble/issues/141) | -     |
| 011 | Optimize Logging with Level Guards                               | MEDIUM   | 1-2 hours     | Completed | [#142](https://github.com/bdperkin/nhl-scrabble/issues/142) | -     |

### Enhancement

| ID  | Title                                                         | Priority | Effort                                                     | Status    | GitHub Issue                                                | Notes                                                                    |
| --- | ------------------------------------------------------------- | -------- | ---------------------------------------------------------- | --------- | ----------------------------------------------------------- | ------------------------------------------------------------------------ |
| 001 | Implement HTML Output Format                                  | MEDIUM   | 4-6 hours                                                  | Completed | [#46](https://github.com/bdperkin/nhl-scrabble/issues/46)   | -                                                                        |
| 001 | Add Progress Bars for Long Operations                         | MEDIUM   | 2-3 hours                                                  | Completed | [#132](https://github.com/bdperkin/nhl-scrabble/issues/132) | -                                                                        |
| 002 | Link Existing GitHub Issues to Task Files                     | MEDIUM   | 2-3 hours                                                  | Completed | [#55](https://github.com/bdperkin/nhl-scrabble/issues/55)   | -                                                                        |
| 002 | Implement Procida's Documentation Model (Diátaxis Framework)  | MEDIUM   | 8-12 hours                                                 | Completed | [#63](https://github.com/bdperkin/nhl-scrabble/issues/63)   | -                                                                        |
| 002 | Create Project Logo and Branding Assets                       | MEDIUM   | 4-8 hours                                                  | Completed | [#89](https://github.com/bdperkin/nhl-scrabble/issues/89)   | -                                                                        |
| 002 | Add Interactive Mode (REPL)                                   | MEDIUM   | 4-6 hours                                                  | Completed | [#133](https://github.com/bdperkin/nhl-scrabble/issues/133) | -                                                                        |
| 003 | Build Comprehensive Sphinx Documentation with GitHub Pages    | MEDIUM   | 12-16 hours                                                | Completed | [#64](https://github.com/bdperkin/nhl-scrabble/issues/64)   | -                                                                        |
| 003 | Add Comprehensive Documentation Badges to README              | MEDIUM   | 1-2 hours                                                  | Completed | [#91](https://github.com/bdperkin/nhl-scrabble/issues/91)   | -                                                                        |
| 003 | Add Historical Data Support                                   | MEDIUM   | 8-12 hours                                                 | Completed | [#143](https://github.com/bdperkin/nhl-scrabble/issues/143) | -                                                                        |
| 004 | Implement Automated API and CLI Documentation Generation      | MEDIUM   | 4-6 hours                                                  | Completed | [#81](https://github.com/bdperkin/nhl-scrabble/issues/81)   | -                                                                        |
| 004 | Add Python 3.14 Support and Testing                           | MEDIUM   | 2-3 hours                                                  | Completed | [#97](https://github.com/bdperkin/nhl-scrabble/issues/97)   | -                                                                        |
| 004 | Add CSV and Excel Export                                      | MEDIUM   | 3-4 hours                                                  | Completed | [#144](https://github.com/bdperkin/nhl-scrabble/issues/144) | -                                                                        |
| 005 | Enhance Sphinx Documentation with Quality Plugins             | MEDIUM   | 2-4 hours                                                  | Completed | [#82](https://github.com/bdperkin/nhl-scrabble/issues/82)   | -                                                                        |
| 005 | Add Python 3.15-dev Development Support                       | MEDIUM   | 1-2 hours                                                  | Completed | [#98](https://github.com/bdperkin/nhl-scrabble/issues/98)   | -                                                                        |
| 005 | Add Advanced Filtering Options                                | MEDIUM   | 4-5 hours                                                  | Completed | [#145](https://github.com/bdperkin/nhl-scrabble/issues/145) | -                                                                        |
| 006 | Skill Optimizations: Pre-Flight Validation and CI Diagnostics | MEDIUM   | 0.5-1 hours (implementation complete, commit and document) | Completed | [#88](https://github.com/bdperkin/nhl-scrabble/issues/88)   | -                                                                        |
| 006 | Add Custom Scoring Rules                                      | MEDIUM   | 3-4 hours                                                  | Completed | [#146](https://github.com/bdperkin/nhl-scrabble/issues/146) | -                                                                        |
| 007 | Add Interactive Statistics Dashboard                          | MEDIUM   | 6-8 hours                                                  | Completed | [#147](https://github.com/bdperkin/nhl-scrabble/issues/147) | -                                                                        |
| 008 | Add Watch Mode for Auto-Refresh                               | MEDIUM   | 2-3 hours                                                  | Completed | [#148](https://github.com/bdperkin/nhl-scrabble/issues/148) | -                                                                        |
| 009 | Add Player Search Functionality                               | MEDIUM   | 3-4 hours                                                  | Completed | [#149](https://github.com/bdperkin/nhl-scrabble/issues/149) | -                                                                        |
| 010 | Python 3.14 and 3.15-dev Support                              | MEDIUM   | 3-5 hours                                                  | Completed | [#217](https://github.com/bdperkin/nhl-scrabble/issues/217) | -                                                                        |
| 011 | Hyperlink Documentation to External Resources                 | LOW      | 2-4 hours                                                  | Completed | [#223](https://github.com/bdperkin/nhl-scrabble/issues/223) | PR [#327](https://github.com/bdperkin/nhl-scrabble/pull/327), 2026-04-22 |
| 012 | Enhance Implement-Task Skill with Pre-Flight Validation       | MEDIUM   | 1-2 hours                                                  | Completed | [#225](https://github.com/bdperkin/nhl-scrabble/issues/225) | -                                                                        |
| 015 | Add Standard Short Options to CLI Commands                    | MEDIUM   | 30-60 minutes                                              | Completed | [#229](https://github.com/bdperkin/nhl-scrabble/issues/229) | PR [#320](https://github.com/bdperkin/nhl-scrabble/pull/320), 2026-04-21 |
| 016 | Format CLI Help Examples with Comments                        | LOW      | 15-30 minutes                                              | Completed | [#230](https://github.com/bdperkin/nhl-scrabble/issues/230) | PR #319, completed 2026-04-21                                            |
| 017 | Expand CLI Output Formats                                     | MEDIUM   | 3-4 hours                                                  | Completed | [#231](https://github.com/bdperkin/nhl-scrabble/issues/231) | PR [#328](https://github.com/bdperkin/nhl-scrabble/pull/328), 2026-04-22 |
| 018 | Support Additional Sphinx Output Formats                      | MEDIUM   | 2-3 hours                                                  | Completed | [#232](https://github.com/bdperkin/nhl-scrabble/issues/232) | PR [#330](https://github.com/bdperkin/nhl-scrabble/pull/330), 2026-04-22 |
| 019 | Integrate Sphinx Doctest and Linkcheck into Build Process     | MEDIUM   | 1-2 hours                                                  | Completed | [#233](https://github.com/bdperkin/nhl-scrabble/issues/233) | PR [#333](https://github.com/bdperkin/nhl-scrabble/pull/333), 2026-04-22 |
| 020 | Enable Colorized Log Output Formatting                        | LOW      | 45 minutes                                                 | Completed | [#234](https://github.com/bdperkin/nhl-scrabble/issues/234) | PR [#321](https://github.com/bdperkin/nhl-scrabble/pull/321), 2026-04-21 |
| 021 | Optimize Tox Execution with Parallel and Fail-Fast Behavior   | MEDIUM   | 3-5 hours                                                  | Completed | [#283](https://github.com/bdperkin/nhl-scrabble/issues/283) | PR [#326](https://github.com/bdperkin/nhl-scrabble/pull/326), 2026-04-22 |
| 022 | Comprehensive GitHub Workflows Enhancement                    | MEDIUM   | 24-32 hours (main task coordination + sub-tasks)           | Active    | [#298](https://github.com/bdperkin/nhl-scrabble/issues/298) | -                                                                        |
| 023 | Extend Sphinx Builder Functionality                           | LOW      | 4-6 hours                                                  | Active    | [#331](https://github.com/bdperkin/nhl-scrabble/issues/331) | -                                                                        |
| 024 | Extend Sphinx Extension Functionality                         | LOW      | 3-5 hours                                                  | Active    | [#332](https://github.com/bdperkin/nhl-scrabble/issues/332) | -                                                                        |
| 025 | Add Automated Documentation Link Validation to CI             | MEDIUM   | 1 hour                                                     | Active    | [#351](https://github.com/bdperkin/nhl-scrabble/issues/351) | From documentation audit (task 013), gap #2                              |
| 026 | Add Automated Code Example Testing to CI                      | MEDIUM   | 2 hours                                                    | Active    | [#352](https://github.com/bdperkin/nhl-scrabble/issues/352) | From documentation audit (task 013), gap #3                              |
| 027 | Improve Function Example Coverage in Docstrings               | MEDIUM   | 3-4 hours                                                  | Active    | [#353](https://github.com/bdperkin/nhl-scrabble/issues/353) | From documentation audit (task 013), gap #4                              |
| 028 | Add Unicode Normalization for Player Names                    | MEDIUM   | 2-3 hours                                                  | Completed | [#363](https://github.com/bdperkin/nhl-scrabble/issues/363) | PR [#374](https://github.com/bdperkin/nhl-scrabble/pull/374), completed 2026-04-25, actual effort: 2.5h |
| 029 | Track ty Type Checker Validation Period (1-2 weeks)          | MEDIUM   | 1-2 weeks                                                  | Active    | [#325](https://github.com/bdperkin/nhl-scrabble/issues/325) | Validation tracking for ty integration (PR #324)                         |
| 030 | Automate CHANGELOG Generation from Git Tags and Commits       | MEDIUM   | 4-6 hours                                                  | Active    | [#379](https://github.com/bdperkin/nhl-scrabble/issues/379) | -                                                                        |
| 031 | Add Version Validation in Pre-commit Hooks                    | MEDIUM   | 1-2 hours                                                  | Active    | [#380](https://github.com/bdperkin/nhl-scrabble/issues/380) | -                                                                        |
| 032 | Create GitHub Release Notes from Tag Annotations              | MEDIUM   | 2-3 hours                                                  | Active    | [#381](https://github.com/bdperkin/nhl-scrabble/issues/381) | -                                                                        |
| 033 | Enhance Version Badge Display in README                       | LOW      | 30min-1h                                                   | Active    | [#382](https://github.com/bdperkin/nhl-scrabble/issues/382) | -                                                                        |
| 034 | Evaluate semantic-release for Fully Automated Releases        | LOW      | 6-10 hours                                                 | Active    | [#383](https://github.com/bdperkin/nhl-scrabble/issues/383) | Research task - evaluate comprehensive release automation alternative    |

### Testing

| ID  | Title                                                   | Priority | Effort                                           | Status    | GitHub Issue                                                | Notes                                                                    |
| --- | ------------------------------------------------------- | -------- | ------------------------------------------------ | --------- | ----------------------------------------------------------- | ------------------------------------------------------------------------ |
| 001 | Increase Test Coverage from 49% to 80%+                 | MEDIUM   | 8-12 hours                                       | Completed | [#43](https://github.com/bdperkin/nhl-scrabble/issues/43)   | -                                                                        |
| 001 | Enable Codecov Integration for Code Coverage Tracking   | MEDIUM   | 1-2 hours                                        | Completed | [#90](https://github.com/bdperkin/nhl-scrabble/issues/90)   | -                                                                        |
| 001 | Add pytest-timeout to Prevent Hanging Tests             | MEDIUM   | 30-60 minutes                                    | Completed | [#119](https://github.com/bdperkin/nhl-scrabble/issues/119) | -                                                                        |
| 001 | Implement Codecov Test Analytics in CI                  | MEDIUM   | 2-3 hours                                        | Completed | [#211](https://github.com/bdperkin/nhl-scrabble/issues/211) | -                                                                        |
| 002 | Add pytest-xdist for Parallel Test Execution            | MEDIUM   | 30-60 minutes                                    | Completed | [#120](https://github.com/bdperkin/nhl-scrabble/issues/120) | -                                                                        |
| 002 | Comprehensive Test Coverage Improvement (90-100%)       | MEDIUM   | 12-20 hours                                      | Completed | [#221](https://github.com/bdperkin/nhl-scrabble/issues/221) | -                                                                        |
| 003 | Add pytest-randomly to Randomize Test Execution Order   | MEDIUM   | 15-30 minutes                                    | Completed | [#121](https://github.com/bdperkin/nhl-scrabble/issues/121) | -                                                                        |
| 003 | Add Unit and Integration Tests for Caching Layer        | MEDIUM   | 2-4 hours                                        | Completed | [#235](https://github.com/bdperkin/nhl-scrabble/issues/235) | -                                                                        |
| 004 | Add pytest-sugar for Enhanced Test Output               | MEDIUM   | 15-30 minutes                                    | Completed | [#122](https://github.com/bdperkin/nhl-scrabble/issues/122) | -                                                                        |
| 004 | CLI Module Test Coverage (70% → 90%)                    | MEDIUM   | 2-3 hours                                        | Completed | [#253](https://github.com/bdperkin/nhl-scrabble/issues/253) | -                                                                        |
| 005 | Add pytest-clarity for Improved Assertion Diffs         | MEDIUM   | 15-30 minutes                                    | Completed | [#123](https://github.com/bdperkin/nhl-scrabble/issues/123) | -                                                                        |
| 005 | Web Interface Test Coverage (30% → 85%)                 | MEDIUM   | 3-4 hours                                        | Completed | [#254](https://github.com/bdperkin/nhl-scrabble/issues/254) | -                                                                        |
| 006 | Add diff-cover for PR Coverage Reporting                | MEDIUM   | 30-60 minutes                                    | Completed | [#124](https://github.com/bdperkin/nhl-scrabble/issues/124) | -                                                                        |
| 006 | Interactive Mode Test Coverage (73.59% → 91.07%)        | MEDIUM   | 2-3 hours                                        | Completed | [#255](https://github.com/bdperkin/nhl-scrabble/issues/255) | -                                                                        |
| 007 | Add pytest-benchmark for Performance Regression Testing | MEDIUM   | 1-2 hours                                        | Completed | [#125](https://github.com/bdperkin/nhl-scrabble/issues/125) | -                                                                        |
| 007 | Configuration and Logging Test Coverage (55% → 90%)     | MEDIUM   | 1-2 hours                                        | Completed | [#256](https://github.com/bdperkin/nhl-scrabble/issues/256) | -                                                                        |
| 008 | Add check-jsonschema for JSON/YAML File Validation      | MEDIUM   | 30-60 minutes                                    | Completed | [#128](https://github.com/bdperkin/nhl-scrabble/issues/128) | -                                                                        |
| 008 | Reports Module Test Coverage (40% → 90%)                | MEDIUM   | 2-3 hours                                        | Completed | [#257](https://github.com/bdperkin/nhl-scrabble/issues/257) | -                                                                        |
| 009 | Edge Cases and Error Path Testing                       | MEDIUM   | 2-3 hours                                        | Completed | [#258](https://github.com/bdperkin/nhl-scrabble/issues/258) | -                                                                        |
| 010 | Integration and End-to-End Testing                      | MEDIUM   | 2-3 hours                                        | Completed | [#259](https://github.com/bdperkin/nhl-scrabble/issues/259) | -                                                                        |
| 011 | Coverage Audit and Finalization                         | MEDIUM   | 2-3 hours                                        | Completed | [#260](https://github.com/bdperkin/nhl-scrabble/issues/260) | -                                                                        |
| 012 | QA Automation Framework                                 | MEDIUM   | 30-40 hours (main task coordination + sub-tasks) | Active    | [#311](https://github.com/bdperkin/nhl-scrabble/issues/311) | -                                                                        |
| 013 | QA Infrastructure Setup                                 | MEDIUM   | 4-6 hours                                        | Completed | [#312](https://github.com/bdperkin/nhl-scrabble/issues/312) | Closed by commit 0a99ee5, 2026-04-21                                     |
| 014 | Playwright Framework Setup                              | MEDIUM   | 6-8 hours                                        | Active    | [#313](https://github.com/bdperkin/nhl-scrabble/issues/313) | -                                                                        |
| 015 | Functional Web Tests                                    | MEDIUM   | 6-8 hours                                        | Active    | [#316](https://github.com/bdperkin/nhl-scrabble/issues/316) | -                                                                        |
| 016 | Visual Regression Tests                                 | MEDIUM   | 4-6 hours                                        | Active    | [#317](https://github.com/bdperkin/nhl-scrabble/issues/317) | -                                                                        |
| 017 | Performance and Load Tests                              | MEDIUM   | 4-6 hours                                        | Active    | [#314](https://github.com/bdperkin/nhl-scrabble/issues/314) | -                                                                        |
| 018 | Accessibility Tests                                     | MEDIUM   | 2-4 hours                                        | Active    | [#318](https://github.com/bdperkin/nhl-scrabble/issues/318) | -                                                                        |
| 019 | QA CI/CD Integration                                    | MEDIUM   | 2-4 hours                                        | Active    | [#315](https://github.com/bdperkin/nhl-scrabble/issues/315) | -                                                                        |
| 020 | Implement Flaky Test Retry Mechanisms                   | MEDIUM   | 6-10 hours                                       | Completed | [#322](https://github.com/bdperkin/nhl-scrabble/issues/322) | PR [#323](https://github.com/bdperkin/nhl-scrabble/pull/323), 2026-04-22 |
| 021 | Test Analytics and Coverage Analysis Tool               | MEDIUM   | 4-6 hours                                        | Active    | [#359](https://github.com/bdperkin/nhl-scrabble/issues/359) | -                                                                        |

### New Features

| ID  | Title                                                 | Priority | Effort              | Status    | GitHub Issue                                                | Notes |
| --- | ----------------------------------------------------- | -------- | ------------------- | --------- | ----------------------------------------------------------- | ----- |
| 001 | Build Web Interface with FastAPI                      | MEDIUM   | 16-24 hours         | Active    | [#50](https://github.com/bdperkin/nhl-scrabble/issues/50)   | -     |
| 002 | Add FastAPI Infrastructure and Web Server Foundation  | MEDIUM   | 3-4 hours           | Completed | [#103](https://github.com/bdperkin/nhl-scrabble/issues/103) | -     |
| 003 | Implement Web API Endpoints for NHL Scrabble Analysis | MEDIUM   | 4-6 hours           | Completed | [#104](https://github.com/bdperkin/nhl-scrabble/issues/104) | -     |
| 004 | Build Frontend Templates and CSS for Web Interface    | MEDIUM   | 4-6 hours           | Completed | [#105](https://github.com/bdperkin/nhl-scrabble/issues/105) | -     |
| 005 | Add JavaScript Interactivity and Data Visualizations  | MEDIUM   | 8-12 hours          | Completed | [#106](https://github.com/bdperkin/nhl-scrabble/issues/106) | -     |
| 006 | Web Interface Testing and Polish                      | MEDIUM   | 2-3 hours           | Completed | [#111](https://github.com/bdperkin/nhl-scrabble/issues/111) | -     |
| 007 | Add Standalone REST API Server                        | MEDIUM   | 8-12 hours          | Completed | [#150](https://github.com/bdperkin/nhl-scrabble/issues/150) | -     |
| 008 | Add Database Backend for Data Persistence             | MEDIUM   | 12-16 hours         | Active    | [#151](https://github.com/bdperkin/nhl-scrabble/issues/151) | -     |
| 009 | Add Notification System                               | MEDIUM   | 6-8 hours           | Active    | [#152](https://github.com/bdperkin/nhl-scrabble/issues/152) | -     |
| 010 | Add Player Comparison Tool                            | MEDIUM   | 4-6 hours           | Active    | [#153](https://github.com/bdperkin/nhl-scrabble/issues/153) | -     |
| 011 | Add Offline Mode Support                              | MEDIUM   | 4-5 hours           | Active    | [#154](https://github.com/bdperkin/nhl-scrabble/issues/154) | -     |
| 012 | Add Configuration Profiles                            | MEDIUM   | 3-4 hours           | Active    | [#155](https://github.com/bdperkin/nhl-scrabble/issues/155) | -     |
| 013 | Add Plugin System                                     | MEDIUM   | 10-14 hours         | Active    | [#156](https://github.com/bdperkin/nhl-scrabble/issues/156) | -     |
| 014 | Add Docker Support                                    | MEDIUM   | 4-6 hours           | Active    | [#157](https://github.com/bdperkin/nhl-scrabble/issues/157) | -     |
| 015 | Add Data Export/Import Functionality                  | MEDIUM   | 4-5 hours           | Active    | [#158](https://github.com/bdperkin/nhl-scrabble/issues/158) | -     |
| 016 | Internationalization and Localization (i18n/l10n)     | MEDIUM   | 32-48 hours         | Active    | [#218](https://github.com/bdperkin/nhl-scrabble/issues/218) | -     |
| 017 | Free Python Hosting and Deployment Infrastructure     | MEDIUM   | 8-12 hours          | Active    | [#219](https://github.com/bdperkin/nhl-scrabble/issues/219) | -     |
| 018 | Automated Python Package Building and Publishing      | MEDIUM   | 4-6 hours           | Active    | [#224](https://github.com/bdperkin/nhl-scrabble/issues/224) | -     |
| 019 | Create Comprehensive Release Automation Skill         | MEDIUM   | 8-12 hours          | Active    | [#247](https://github.com/bdperkin/nhl-scrabble/issues/247) | -     |
| 020 | CLI Internationalization Implementation               | MEDIUM   | 4-6 hours           | Active    | [#248](https://github.com/bdperkin/nhl-scrabble/issues/248) | -     |
| 021 | Web Interface Internationalization Implementation     | MEDIUM   | 6-8 hours           | Active    | [#249](https://github.com/bdperkin/nhl-scrabble/issues/249) | -     |
| 022 | TUI/Interactive Mode Internationalization             | MEDIUM   | 3-4 hours           | Active    | [#250](https://github.com/bdperkin/nhl-scrabble/issues/250) | -     |
| 023 | Create Initial Translation File Structure             | MEDIUM   | 2-3 hours           | Active    | [#251](https://github.com/bdperkin/nhl-scrabble/issues/251) | -     |
| 024 | Translate to Priority Languages                       | MEDIUM   | 8-12 hours          | Active    | [#252](https://github.com/bdperkin/nhl-scrabble/issues/252) | -     |
| 025 | Release Automation: Pre-Release Validation Phase      | MEDIUM   | 1-2 hours           | Active    | [#261](https://github.com/bdperkin/nhl-scrabble/issues/261) | -     |
| 026 | Release Automation: Version Bumping Phase             | MEDIUM   | 1-2 hours           | Active    | [#262](https://github.com/bdperkin/nhl-scrabble/issues/262) | -     |
| 027 | Release Automation: Build and Validate Phase          | MEDIUM   | 1-2 hours           | Active    | [#263](https://github.com/bdperkin/nhl-scrabble/issues/263) | -     |
| 028 | Release Automation: Publish Phase                     | MEDIUM   | 1-2 hours           | Active    | [#264](https://github.com/bdperkin/nhl-scrabble/issues/264) | -     |
| 029 | Release Automation: Post-Release Phase                | MEDIUM   | 1-2 hours           | Active    | [#265](https://github.com/bdperkin/nhl-scrabble/issues/265) | -     |
| 030 | Release Automation: Verification and Reporting Phase  | MEDIUM   | 1-2 hours           | Active    | [#266](https://github.com/bdperkin/nhl-scrabble/issues/266) | -     |
| 031 | Release Automation: Orchestration and CLI Interface   | MEDIUM   | 2-3 hours           | Active    | [#267](https://github.com/bdperkin/nhl-scrabble/issues/267) | -     |
| 032 | PyPI Package Publishing Workflow                      | MEDIUM   | 4-6 hours           | Active    | [#299](https://github.com/bdperkin/nhl-scrabble/issues/299) | -     |
| 033 | GitHub Release Automation Workflow                    | MEDIUM   | 2-3 hours           | Active    | [#300](https://github.com/bdperkin/nhl-scrabble/issues/300) | -     |
| 034 | Docker Container Build and Publish Workflow           | MEDIUM   | 3-4 hours           | Active    | [#301](https://github.com/bdperkin/nhl-scrabble/issues/301) | -     |
| 035 | PR Auto-Labeling Workflow                             | MEDIUM   | 1-2 hours           | Active    | [#302](https://github.com/bdperkin/nhl-scrabble/issues/302) | -     |
| 036 | PR Size Checker Workflow                              | MEDIUM   | 1-2 hours           | Active    | [#303](https://github.com/bdperkin/nhl-scrabble/issues/303) | -     |
| 037 | Stale Issue and PR Management Workflow                | MEDIUM   | 1 hour              | Active    | [#304](https://github.com/bdperkin/nhl-scrabble/issues/304) | -     |
| 038 | First-Time Contributor Welcome Workflow               | MEDIUM   | 30 minutes - 1 hour | Active    | [#305](https://github.com/bdperkin/nhl-scrabble/issues/305) | -     |
| 039 | Performance Benchmark Testing Workflow                | MEDIUM   | 3-4 hours           | Active    | [#306](https://github.com/bdperkin/nhl-scrabble/issues/306) | -     |
| 040 | Software Bill of Materials (SBOM) Generation Workflow | MEDIUM   | 2-3 hours           | Active    | [#307](https://github.com/bdperkin/nhl-scrabble/issues/307) | -     |
| 041 | SLSA Provenance Generation Workflow                   | MEDIUM   | 2-3 hours           | Active    | [#308](https://github.com/bdperkin/nhl-scrabble/issues/308) | -     |
| 042 | Enhanced Dependency Review Workflow                   | MEDIUM   | 1-2 hours           | Active    | [#309](https://github.com/bdperkin/nhl-scrabble/issues/309) | -     |
| 043 | Nightly Comprehensive Testing Workflow                | MEDIUM   | 2-3 hours           | Active    | [#310](https://github.com/bdperkin/nhl-scrabble/issues/310) | -     |

### Refactoring

| ID  | Title                                                                         | Priority | Effort              | Status    | GitHub Issue                                                | Notes                                                                                  |
| --- | ----------------------------------------------------------------------------- | -------- | ------------------- | --------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| 001 | Extract Retry Logic to Reusable Decorator                                     | MEDIUM   | 2-3 hours           | Completed | [#51](https://github.com/bdperkin/nhl-scrabble/issues/51)   | -                                                                                      |
| 001 | Consolidate Report Classes                                                    | MEDIUM   | 6-8 hours           | Completed | [#159](https://github.com/bdperkin/nhl-scrabble/issues/159) | -                                                                                      |
| 002 | Improve Type Safety                                                           | LOW      | 8-10 hours          | Completed | [#160](https://github.com/bdperkin/nhl-scrabble/issues/160) | PR [#354](https://github.com/bdperkin/nhl-scrabble/pull/354), 2026-04-24, 6h actual    |
| 002 | Port check_docs.sh Shell Script to Python                                     | MEDIUM   | 2-3 hours           | Completed | [#100](https://github.com/bdperkin/nhl-scrabble/issues/100) | -                                                                                      |
| 003 | Unified Configuration Management                                              | MEDIUM   | 5-6 hours           | Completed | [#161](https://github.com/bdperkin/nhl-scrabble/issues/161) | PR [#358](https://github.com/bdperkin/nhl-scrabble/pull/358), 2026-04-24, 5h actual    |
| 003 | Port check-branch-protection.sh Git Hook to Python                            | MEDIUM   | 1-2 hours           | Completed | [#101](https://github.com/bdperkin/nhl-scrabble/issues/101) | -                                                                                      |
| 004 | Add pyupgrade for Automatic Python Syntax Modernization                       | MEDIUM   | 1.5 hours           | Completed | [#118](https://github.com/bdperkin/nhl-scrabble/issues/118) | [PR #336](https://github.com/bdperkin/nhl-scrabble/pull/336)                           |
| 005 | Add djlint for HTML and Jinja2 Template Linting                               | MEDIUM   | 30-60 minutes       | Completed | [#127](https://github.com/bdperkin/nhl-scrabble/issues/127) | PR [#388](https://github.com/bdperkin/nhl-scrabble/pull/388), 2026-04-26, ~50min actual |
| 006 | Implement Consistent Error Handling Strategy                                  | MEDIUM   | 6-8 hours           | Completed | [#162](https://github.com/bdperkin/nhl-scrabble/issues/162) | PR [#361](https://github.com/bdperkin/nhl-scrabble/pull/361), 2026-04-24, 6h actual    |
| 007 | Add Dependency Injection                                                      | LOW      | 8-10 hours          | Completed | [#163](https://github.com/bdperkin/nhl-scrabble/issues/163) | PR [#360](https://github.com/bdperkin/nhl-scrabble/pull/360), 2026-04-24, 6h actual    |
| 008 | Repository Cleanup and Consolidation                                          | MEDIUM   | 4-6 hours           | Completed | [#216](https://github.com/bdperkin/nhl-scrabble/issues/216) | -                                                                                      |
| 009 | Git Branch Pruning Automation                                                 | MEDIUM   | 30-60 minutes       | Completed | [#220](https://github.com/bdperkin/nhl-scrabble/issues/220) | -                                                                                      |
| 010 | Dynamic Versioning from Git Tags                                              | MEDIUM   | 2-4 hours           | Completed | [#222](https://github.com/bdperkin/nhl-scrabble/issues/222) | PR [#378](https://github.com/bdperkin/nhl-scrabble/pull/378), 2026-04-25, 3.5h actual |
| 011 | Dependency Synchronization and Automation                                     | MEDIUM   | 3-4 hours           | Completed | [#226](https://github.com/bdperkin/nhl-scrabble/issues/226) | PR [#341](https://github.com/bdperkin/nhl-scrabble/pull/341), 2026-04-23, 4.5h actual  |
| 012 | Audit and Standardize Command-Line Options for Consistency                    | MEDIUM   | 2-4 hours           | Completed | [#236](https://github.com/bdperkin/nhl-scrabble/issues/236) | PR [#349](https://github.com/bdperkin/nhl-scrabble/pull/349), 2026-04-23, 5h actual    |
| 013 | Perform Project-Wide Documentation Audit                                      | MEDIUM   | 4-6 hours           | Completed | [#237](https://github.com/bdperkin/nhl-scrabble/issues/237) | PR [#350](https://github.com/bdperkin/nhl-scrabble/pull/350), 2026-04-24, 4h actual    |
| 014 | Add Refurb Python Code Modernization Linter                                   | MEDIUM   | 2-3 hours           | Completed | [#241](https://github.com/bdperkin/nhl-scrabble/issues/241) | PR [#337](https://github.com/bdperkin/nhl-scrabble/pull/337), 2026-04-22, 2.5h actual  |
| 015 | Add pyproject-fmt Configuration Formatter                                     | MEDIUM   | 45 minutes          | Completed | [#242](https://github.com/bdperkin/nhl-scrabble/issues/242) | PR [#386](https://github.com/bdperkin/nhl-scrabble/pull/386), 2026-04-25, 45min actual |
| 016 | Add Trailing Comma Python Formatter                                           | MEDIUM   | 30 minutes - 1 hour | Completed | [#243](https://github.com/bdperkin/nhl-scrabble/issues/243) | PR [#387](https://github.com/bdperkin/nhl-scrabble/pull/387), 2026-04-26, 1.5h actual |
| 017 | Extend JSON/YAML Schema Validation with check-jsonschema                      | MEDIUM   | 1-2 hours           | Completed | [#244](https://github.com/bdperkin/nhl-scrabble/issues/244) | PR [#338](https://github.com/bdperkin/nhl-scrabble/pull/338), 2026-04-23, 45min actual |
| 018 | Add check-wheel-contents Package Validator                                    | MEDIUM   | 1-2 hours           | Completed | [#245](https://github.com/bdperkin/nhl-scrabble/issues/245) | PR [#339](https://github.com/bdperkin/nhl-scrabble/pull/339), 2026-04-23, 1.5h actual  |
| 019 | Add ssort Python Statement Sorter                                             | MEDIUM   | 2-3 hours           | Completed | [#246](https://github.com/bdperkin/nhl-scrabble/issues/246) | PR [#340](https://github.com/bdperkin/nhl-scrabble/pull/340), 2026-04-23, 2.5h actual  |
| 020 | Migrate from Deprecated codecov/test-results-action to codecov/codecov-action | MEDIUM   | 30min-1h            | Completed | [#285](https://github.com/bdperkin/nhl-scrabble/issues/285) | PR [#372](https://github.com/bdperkin/nhl-scrabble/pull/372), 2026-04-24, 30min actual |
| 021 | Comprehensive Task Documentation Synchronization and Validation               | MEDIUM   | 3-5 hours           | Completed | [#286](https://github.com/bdperkin/nhl-scrabble/issues/286) | -                                                                                      |
| 022 | Remove Backward Compatibility Code Before First Release                       | MEDIUM   | 2-4 hours           | Completed | [#329](https://github.com/bdperkin/nhl-scrabble/issues/329) | PR [#335](https://github.com/bdperkin/nhl-scrabble/pull/335), 2026-04-22, 3.5h actual  |
| 023 | Consolidate Exporters and Formatters Architecture                             | LOW      | 3-5 hours           | Completed | [#377](https://github.com/bdperkin/nhl-scrabble/pull/377)  | PR [#377](https://github.com/bdperkin/nhl-scrabble/pull/377), 2026-04-25, 2.5h actual |
| 024 | Make 'ty' Blocking After Validation Period                                    | LOW      | 30min-1h            | Active    | [#355](https://github.com/bdperkin/nhl-scrabble/issues/355) | -                                                                                      |
| 025 | Make 'refurb' Blocking After Validation Period                                | LOW      | 30min-1h            | Completed | [#356](https://github.com/bdperkin/nhl-scrabble/issues/356) | PR [#370](https://github.com/bdperkin/nhl-scrabble/pull/370), 2026-04-24, 1.5h actual |
| 026 | Make 'gitlint' Blocking (Except GitHub CI Workflows) After Validation Period  | LOW      | 30min-1h            | Completed | [#357](https://github.com/bdperkin/nhl-scrabble/issues/357) | PR [#371](https://github.com/bdperkin/nhl-scrabble/pull/371), 2026-04-24, 45min actual |
| 027 | Audit and Adjust Logging Levels                                               | LOW      | 2-3 hours           | Completed | [#364](https://github.com/bdperkin/nhl-scrabble/issues/364) | PR [#376](https://github.com/bdperkin/nhl-scrabble/pull/376), 2026-04-25, 3h actual    |

## Statistics

### Task Counts by Category

| Category     | Active | Completed | Total   |
| ------------ | ------ | --------- | ------- |
| Bug Fixes    | 0      | 11        | 11      |
| Security     | 1      | 14        | 15      |
| Optimization | 0      | 13        | 13      |
| Enhancement  | 12     | 33        | 45      |
| Testing      | 8      | 23        | 31      |
| New Features | 37     | 6         | 43      |
| Refactoring  | 1      | 29        | 30      |
| **TOTAL**    | **59** | **129**   | **188** |

### Effort Estimates by Category

| Category     | Estimated Effort |
| ------------ | ---------------- |
| Bug Fixes    | 12.25 hours      |
| Security     | 82.75 hours      |
| Optimization | 36.0 hours       |
| Enhancement  | 219.25 hours     |
| Testing      | 265.0 hours      |
| New Features | 227.0 hours      |
| Refactoring  | 219.0 hours      |
| **TOTAL**    | **1061.25 hours**|

### Completion Progress

| Category     | Completion Rate |
| ------------ | --------------- |
| Bug Fixes    | 90.9%           |
| Security     | 93.3%           |
| Optimization | 100.0%          |
| Enhancement  | 73.3%           |
| Testing      | 74.2%           |
| New Features | 14.0%           |
| Refactoring  | 83.3%           |
| **OVERALL**  | **66.5%**       |

### Priority Distribution (Active Tasks)

| Priority | Count |
| -------- | ----- |
| CRITICAL | 0     |
| HIGH     | 1     |
| MEDIUM   | 58    |
| LOW      | 5     |

## Recommended Implementation Order

### Critical Priority (Immediate)

_No critical priority tasks_

### High Priority (Current Sprint)

1. **Bug Fix**: [#010 Fix Output Format Validation Mismatch](bug-fixes/010-fix-output-format-validation-mismatch.md) - 30min-1h - CLI crashes with confusing pydantic error for valid format options like markdown

## Total Project Roadmap

**Total Tasks**: 188 tasks (59 active, 129 completed)

- **Total Estimated Effort**: 1061.25 hours
  - Active Tasks: ~517 hours
  - Completed Tasks: ~544.25 hours
- **Overall Completion**: 67.0%

## Task Management Guidelines

1. **Creating Tasks**: Use the `create-task` skill or manually create in appropriate category directory
1. **Updating Status**: Move completed tasks to `completed/<category>/` directory
1. **GitHub Integration**: Link all tasks to GitHub issues for tracking
1. **Priority Assignment**: Follow priority guidelines for consistent task ordering
1. **Effort Estimation**: Use realistic estimates to plan sprints effectively

## Directory Structure

```
tasks/
├── README.md                    # This file
├── IMPLEMENTATION_SEQUENCE.md   # Recommended implementation order
├── TOOLING_ANALYSIS.md         # Tooling recommendations
├── bug-fixes/                   # Active bug fix tasks
├── security/                    # Active security tasks
├── optimization/                # Active optimization tasks
├── enhancement/                 # Active enhancement tasks
├── testing/                     # Active testing tasks
├── new-features/                # Active new feature tasks
├── refactoring/                 # Active refactoring tasks
└── completed/                   # Completed tasks (all categories)
    ├── bug-fixes/
    ├── security/
    ├── optimization/
    ├── enhancement/
    ├── testing/
    ├── new-features/
    └── refactoring/
```

## Related Documentation

- [CLAUDE.md](../CLAUDE.md) - Project overview and development guide
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- [GitHub Issues](https://github.com/bdperkin/nhl-scrabble/issues) - Issue tracker

______________________________________________________________________

**Last Updated**: 2026-04-25
**Total Tasks**: 188
**Completion Rate**: 66.5%
