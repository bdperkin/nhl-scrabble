# Track ty Type Checker Validation Period (1-2 weeks)

**Category**: Enhancement
**Priority**: **MEDIUM** - Type Checking Validation
**Estimated Effort**: 1-2 weeks (ongoing monitoring + final decision)
**Status**: Active
**GitHub Issue**: [#325](https://github.com/bdperkin/nhl-scrabble/issues/325) - Track ty Type Checker Validation Period (1-2 weeks)

## Overview

Track validation period for Astral ty type checker integration (completed in #324). Monitor ty vs mypy for 1-2 weeks to assess performance, error detection quality, false positive rate, and developer experience before making final integration decision.

## Problem Description

ty v0.0.32 was integrated in PR #324 as a **non-blocking supplement to mypy** during a validation period. This task tracks validation metrics to determine whether to:
- Replace mypy with ty
- Keep both type checkers
- Remove ty
- Extend validation period

**Background:**
- **Implementation Task**: tasks/completed/enhancement/014-integrate-astral-ty-type-checker.md
- **Merged**: 2026-04-22 (commit 5abb17e via PR #324)
- **Parent Issue**: #228
- **Follow-up Task**: tasks/refactoring/024-make-ty-blocking.md (issue #355)

**Current Configuration:**
- ✅ ty runs in parallel with mypy (non-blocking)
- ✅ Integrated in: pre-commit, tox, CI, Makefile
- ✅ Validation mode enabled (continues on error)

**Initial Metrics (2026-04-22):**
- **Codebase**: ~1,866 LOC
- **ty**: 0.21s, 27 diagnostics (6 categories)
- **mypy**: 0.27s, 0 errors
- **Performance**: ty 1.3x faster than mypy

## Validation Goals

### Quantitative Metrics

Track and assess:
- [ ] **Performance**: Confirm ty speed advantage in CI/pre-commit
- [ ] **Error Detection**: Evaluate quality of 27 ty diagnostics
- [ ] **False Positive Rate**: Determine which diagnostics are legitimate vs noise
- [ ] **CI Performance**: Measure impact on overall pipeline duration
- [ ] **Pre-commit Speed**: Assess developer experience impact

### Qualitative Assessment

Evaluate:
- [ ] **Error Messages**: Are ty messages more actionable than mypy?
- [ ] **LSP Integration**: Test in VS Code, PyCharm, Neovim
- [ ] **Developer Satisfaction**: Overall experience during development
- [ ] **Maintenance Burden**: Configuration complexity vs mypy
- [ ] **Ecosystem Fit**: Benefits of unified Astral tooling (ruff, uv, ty)

## Weekly Checkpoints

### Week 1 (2026-04-22 to 2026-04-29)

- [ ] Run both type checkers daily
- [ ] Test LSP integration in at least one IDE
- [ ] Assess 10-15 diagnostics for validity
- [ ] Monitor CI performance metrics
- [ ] Document findings in issue #325

### Week 2 (2026-04-29 to 2026-05-06)

- [ ] Complete diagnostic assessment (all 27 diagnostics)
- [ ] Test LSP in additional IDEs if available
- [ ] Collect final performance metrics
- [ ] Make recommendation on integration decision
- [ ] Document final assessment in issue #325

## Decision Options

After validation period, choose one:

1. **Replace mypy** - ty superior quality, low false positives
   - Update task 024 (make-ty-blocking) to remove mypy
   - Close issue #355

2. **Keep both** - Complementary coverage justifies dual type checking
   - Update configuration to use both long-term
   - Close task 024 and issue #355

3. **Remove ty** - High false positives, not adding value
   - Revert ty integration from pre-commit/CI
   - Close task 024 and issue #355

4. **Keep ty non-blocking** - Extend validation period for more data
   - Continue validation for another 1-2 weeks
   - Update issue #325 with extended timeline

## Acceptance Criteria

- [ ] Week 1 checkpoint completed with findings documented
- [ ] Week 2 checkpoint completed with findings documented
- [ ] All 27 ty diagnostics categorized (valid/false positive)
- [ ] LSP integration tested in at least one IDE
- [ ] CI performance impact assessed
- [ ] Final recommendation made and documented
- [ ] Decision implemented (via task 024 or direct action)
- [ ] Issue #325 updated with final decision
- [ ] Issue #325 closed

## Implementation Plan

### Phase 1: Week 1 Monitoring (2026-04-22 to 2026-04-29)

1. **Daily Monitoring**:
   - Run both type checkers during development
   - Note any differences in error detection
   - Track pre-commit performance feel

2. **Diagnostic Assessment** (10-15 diagnostics):
   - Review ty diagnostic output
   - Categorize each: valid error / false positive / informational
   - Compare against mypy findings

3. **LSP Testing**:
   - Install ty LSP in primary IDE (if available)
   - Test autocomplete, hover, diagnostics
   - Compare with mypy/Pylance LSP experience

4. **Performance Metrics**:
   - Check CI logs for ty vs mypy timing
   - Monitor pre-commit hook timing
   - Note any slowdowns or improvements

5. **Document Findings**:
   - Update issue #325 with Week 1 summary
   - Flag any major concerns early

### Phase 2: Week 2 Completion (2026-04-29 to 2026-05-06)

1. **Complete Diagnostic Assessment** (remaining ~17 diagnostics):
   - Review all remaining ty diagnostics
   - Final categorization: valid/false positive/informational
   - Calculate false positive rate

2. **Additional LSP Testing** (if applicable):
   - Test in secondary IDE if available
   - Document LSP feature completeness

3. **Final Performance Assessment**:
   - Aggregate CI timing data
   - Calculate average speedup/slowdown
   - Assess overall pipeline impact

4. **Make Recommendation**:
   - Weigh all metrics and qualitative feedback
   - Consider maintenance burden
   - Align with project goals (speed, accuracy, Astral ecosystem)

5. **Document Decision**:
   - Update issue #325 with comprehensive findings
   - Clear recommendation with rationale
   - Next steps identified

### Phase 3: Implementation (2026-05-06+)

Based on decision:

**If Replace mypy:**
- Execute task 024 (make-ty-blocking)
- Remove mypy configuration
- Update documentation

**If Keep both:**
- Document long-term dual-checker strategy
- Update CLAUDE.md if needed
- Close task 024

**If Remove ty:**
- Revert ty from pre-commit/CI/tox
- Document reasons in issue #325
- Close task 024

**If Extend validation:**
- Update issue #325 timeline
- Continue monitoring for another period
- Repeat assessment phases

## Timeline

- **Start**: 2026-04-22
- **Week 1 Checkpoint**: 2026-04-29
- **Week 2 Checkpoint**: 2026-05-06
- **Final Decision**: 2026-05-06 (or later if extended)
- **Implementation**: TBD based on decision

## Current Status (Week 0: 2026-04-22)

**Initial Configuration:**
- ty v0.0.32 integrated as non-blocking
- Runs in parallel with mypy in all checks
- Validation mode: continues on error

**Initial Diagnostics:**
- ty: 27 diagnostics across 6 categories
- mypy: 0 errors
- Assessment: TBD

**Initial Performance:**
- ty: 0.21s
- mypy: 0.27s
- Speedup: 1.3x faster

## Related Tasks

- ✅ **task 014**: Integrate Astral ty Type Checker (completed, PR #324)
- 🔄 **task 024**: Make ty Blocking After Validation (issue #355, pending this decision)

## Related Files

**Type Checking Configuration:**
- `pyproject.toml` - ty and mypy settings
- `.pre-commit-config.yaml` - Pre-commit hooks
- `tox.ini` - Tox environments

**CI/CD:**
- `.github/workflows/ci.yml` - CI type checking

**Makefile:**
- `make mypy` - Run mypy
- `make ty` - Run ty
- `make type-check` - Run both

## References

- **Issue**: https://github.com/bdperkin/nhl-scrabble/issues/325
- **PR**: #324 - https://github.com/bdperkin/nhl-scrabble/pull/324
- **Commit**: 5abb17e
- **ty Documentation**: https://docs.astral.sh/ty/
- **Parent Issue**: #228

## Notes

- This is a **tracking task**, not an implementation task
- Focus is on data collection and decision making
- Implementation will occur via task 024 or direct action based on decision
- Week 1 checkpoint is approaching (2026-04-29, 4 days from now)
