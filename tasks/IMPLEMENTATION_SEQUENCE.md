# Task Implementation Sequence

**Generated**: 2026-05-08
**Updated**: 2026-05-14 (tasks 023, 024, 028, 037, 038, 039, 040, 041, 042, 043, 044, 045, 046, 051 completed)
**Total Tasks**: 15 active tasks
**Total Estimated Effort**: 80-113 hours

This document provides the optimal implementation sequence for all active tasks, organized by priority, dependencies, and strategic value. Tasks are grouped into logical phases with clear rationales.

## Usage

Use the `/implement-task` skill to work on tasks in this order:

```bash
# /implement-task category/ID-slug.md  # Example usage
```

Each task entry shows:
- Path to task file
- Estimated effort range
- GitHub issue number
- Dependencies (if any)

---

## Phase 1: HIGH Priority - Critical Test Coverage (COMPLETED)

**Rationale**: HIGH priority test coverage tasks addressing critical untested modules completed.

~~**Task 035 (business logic)**: Completed 2026-05-12 - Coverage analysis revealed task based on outdated data. All modules exceed targets (95.79% average). See PR #595.~~

~~**Task 037 (security)**: Completed 2026-05-12 - Enhanced SSRF protection tests. Coverage: 25%→97.5% (+72.5pp). Actual effort: ~2h (vs 12-16h estimate). Most modules already had excellent coverage from prior work. PR #596.~~

**Phase Total**: 0 hours (all tasks completed)

---

## Phase 2: MEDIUM Priority - Comprehensive Test Coverage (78-104 hours)

**Rationale**: Four MEDIUM priority test coverage tasks completing the comprehensive 7-task coverage initiative (033-039). These cover all remaining untested modules. Order by strategic foundation: infrastructure → application → final modules → interactive → web.

**Coverage Goal**: Increase overall coverage from ~92.5% to 97%+ by addressing ~3,623 untested statements across remaining 4 tasks.

~~**Task 033 (core infrastructure)**: Completed 2026-05-12 - Core infrastructure modules tested. Coverage: 90.21%→~92.5% (+2.3pp). 6 modules at 100%, 4 at 95%+. Actual effort: 4-5h (vs 16-24h estimate). Most modules already had excellent coverage. PR #597.~~

~~**Task 034 (application modules)**: Completed 2026-05-12 - Enhanced test coverage for validators and logging_config. Coverage: validators 12.30%→98.36% (+86pp), logging_config 0%→~95%. Added 42 comprehensive tests. Actual effort: ~3h (vs 24-32h estimate). Other modules already had excellent coverage. PR #598.~~

~~**Task 036 (final modules)**: Completed 2026-05-12 - Investigation revealed all work already complete from prior PRs. Coverage: config.py 93.60% (PR #385), analytics 97-99% (PR #463), exporters/formatters 92-100% (PR #360). Task based on outdated snapshot. Actual effort: 1h investigation (vs 18-24h estimate). PR #600.~~

~~**Task 038 (interactive modules)**: Completed 2026-05-12 - Investigation revealed tests already existed with 91.11% coverage (not 0%). Added 18 edge case tests. Coverage: interactive/shell.py 91.11%→99.27% (+8.16%), interactive/__init__.py 100%. Only 3 lines remain uncovered (complex retry logic). Actual effort: ~2h (vs 16-20h estimate, 88% faster). Task based on outdated data. PR #602.~~

~~**Task 039 (web modules)**: Completed 2026-05-12 - Investigation revealed actual coverage was 54.94% (not 0% claimed). Created 34 unit tests (26 web_app + 8 auto_link). Coverage: auto_link.py 85.33%→97.33% ✅ (exceeds 95%!), web/app.py 49.95%→56.21% (+6.26pp), overall 54.94%→60.27% (+5.33pp). Created 6 follow-up tasks (040-045) for remaining web/app.py coverage (~12-16h). Actual effort: ~6h (vs 20-28h estimate, 70% time savings). Task based on incorrect data. PR #603.~~

**Phase Total**: 0 hours (all tasks completed)

**Dependencies**:
- Phase 1 should complete first (HIGH priority test coverage)
- Tasks within this phase are largely independent and can be parallelized
- All 7 tasks (033-039) form a comprehensive coverage initiative

---

## Phase 3: MEDIUM Priority - I18n Quality & Testing (3-4 hours)

**Rationale**: Improve internationalization quality and coverage. Translation reviews validate quality baseline for AI-assisted translations.

~~**Task 046 (fr_CA review)**: Completed 2026-05-14 - Native French Canadian speaker reviewed all 254 translations. Validated natural language, Quebec hockey terminology, and cultural appropriateness. Actual effort: ~3.5h (within 3-4h estimate). First fully reviewed translation! ✅~~

**Remaining Reviews**:
```bash
/implement-task enhancement/047-native-speaker-review-sv-se.md  # 3-4h, Issue #510
```

**Phase Total**: 3-4 hours

---

## Phase 4: LOW Priority - Documentation & Tooling (Quick Wins) (8-12 hours)

**Rationale**: Low-effort documentation and tooling improvements. These are quick wins that improve developer experience without blocking other work.

```bash
/implement-task testing/023-make-qa-workflow-blocking.md  # 15min, Issue #439
/implement-task refactoring/024-make-ty-blocking.md  # 30min-1h, Issue #355, [Dependency: #325 ty validation]
```

**Phase Total**: 0.75-1.25 hours

---

## Phase 5: LOW Priority - I18n Visual Enhancements (2-3 hours)

**Rationale**: Visual improvements to locale selection. Low priority but enhances user experience. Do after core i18n quality work.

```bash
~~**Task 045 (locale dropdown flags)**: Completed 2026-05-13 - Added Unicode flag emoji to locale selector. Created LOCALE_FLAGS & LOCALE_NAMES dicts, get_locale_display_name() function, updated web templates. 60+ tests (19 unit + 5 integration), 100% coverage on new code. Actual: ~2.5h (vs 2-3h estimate). PR #611.~~
```

**Phase Total**: 2-3 hours

---

## Phase 6: LOW Priority - Translation Locales (Simple) (COMPLETED)

**Rationale**: Simple locale with minimal differences from en_US. Quick win for expanding locale coverage.

~~**Task 037 (en_CA)**: Completed 2026-05-13 - English (Canada) translation. All 254 strings translated with Canadian spelling variants. Actual effort: ~1.5h (within 1-2h estimate). PR #622.~~

**Phase Total**: ~1.5 hours (actual)

---

## Phase 7: LOW Priority - Translation Locales (Complex Languages) (COMPLETED)

**Rationale**: Complex translations requiring professional translators. All 8 translation tasks completed (en_CA, ru_RU, fi_FI, cs_CZ, de_DE, de_CH, it_CH, sk_SK, lv_LV). Major i18n milestone: **All 12 supported locales now have complete translations!**

**Simpler Adaptations** (can leverage de_DE):
~~**Task 042 (de_CH)**: Completed 2026-05-13 - German (Switzerland) translation. All 254 strings translated with Swiss German conventions (ss instead of ß). Actual effort: ~4h (within 4-6h estimate). PR #623.~~

**Full Translations**:
~~**Task 038 (ru_RU)**: Completed 2026-05-13 - Russian (Russia) translation. All 254 strings translated with Cyrillic encoding. Actual effort: ~6h (within 6-8h estimate). PR #624.~~

~~**Task 039 (fi_FI)**: Completed 2026-05-13 - Finnish (Finland) translation. All 254 strings translated with complex Finnish grammar. Actual effort: ~6.5h (within 6-8h estimate). PR #625.~~

~~**Task 040 (cs_CZ)**: Completed 2026-05-13 - Czech (Czech Republic) translation. All 254 strings translated with complex declensions. Actual effort: ~7h (within 6-8h estimate). PR #626.~~

~~**Task 041 (de_DE)**: Completed 2026-05-13 - German (Germany) translation. All 254 strings translated with compound words and DEL terminology. Actual effort: ~7h (within 6-8h estimate). PR #627.~~

~~**Task 043 (it_CH)**: Completed 2026-05-13 - Italian (Switzerland) translation. All 254 strings translated with Swiss Italian NLA/NLB terminology. Actual effort: ~6.5h (within 6-8h estimate). PR #628.~~

~~**Task 044 (sk_SK)**: Completed 2026-05-14 - Slovak (Slovakia) translation. All 254 strings translated with Slovak Extraliga terminology. Actual effort: ~7h (within 6-8h estimate). PR #629.~~

~~**Task 045 (lv_LV)**: Completed 2026-05-14 - Latvian (Latvia) translation. All 254 strings translated with Latvian hockey terminology. Actual effort: ~7h (within 6-8h estimate). PR #630.~~

**Phase Total**: 0 hours (all tasks completed)

---

## Phase 8: LOW Priority - I18n Advanced Features (12-18 hours)

**Rationale**: Advanced i18n features that build on completed translations. Community platform enables collaborative translation. Locale-specific scoring adds fairness for international users.

```bash
/implement-task enhancement/049-community-translation-platform.md  # 4-6h, Issue #522
/implement-task enhancement/050-locale-specific-scrabble-letter-values.md  # 8-12h, Issue #523
```

**Phase Total**: 12-18 hours

---

## Phase 9: LOW Priority - Research & Evaluation (14-22 hours)

**Rationale**: Research tasks that inform future decisions. No immediate implementation required, but valuable for strategic planning.

```bash
/implement-task enhancement/034-evaluate-semantic-release-automation.md  # 6-10h, Issue #383
/implement-task new-features/017-free-python-hosting-deployment.md  # 8-12h, Issue #219
```

**Phase Total**: 14-22 hours

---

## Phase 10: LOW Priority - New Features (Infrastructure) (52-72 hours)

**Rationale**: Significant new features that add capabilities but aren't blocking current work. Group by complexity (simpler first).

**Simpler Features** (3-8 hours):
```bash
/implement-task new-features/012-config-profiles.md  # 3-4h, Issue #155
/implement-task new-features/011-offline-mode.md  # 4-5h, Issue #154
/implement-task new-features/015-data-export-import.md  # 4-5h, Issue #158
/implement-task new-features/010-player-comparison-tool.md  # 4-6h, Issue #153
/implement-task new-features/014-docker-support.md  # 4-6h, Issue #157
/implement-task new-features/009-notification-system.md  # 6-8h, Issue #152
```

**Complex Features** (10-16 hours):
```bash
/implement-task new-features/013-plugin-system.md  # 10-14h, Issue #156
/implement-task new-features/008-database-backend.md  # 12-16h, Issue #151
```

**Phase Total**: 52-72 hours

---

## Summary

**Total Active Tasks**: 15
**Total Estimated Effort**: 80-113 hours

### By Priority:
- **HIGH**: 0 tasks (0 hours) - All critical test coverage completed
- **MEDIUM**: 3 tasks (31-45 hours) - I18n quality (sv_SE review), test-analytics enhancement, code quality refactoring
- **LOW**: 12 tasks (49-68 hours) - Features, documentation, research (all translations complete!)

### By Category:
- **Testing**: 2 tasks (8.25-12.25 hours) - QA workflow + test-analytics
- **Enhancement**: 4 tasks (46-69 hours) - I18n review (sv_SE), Sphinx extensions, test-analytics, evaluation
- **New Features**: 10 tasks (12-21 hours) - Infrastructure features (all translations complete!)
- **Refactoring**: 1 task (20-29 hours) - Module split refactoring

### Strategic Focus:
1. **Phases 1-2** (0 hours): Test coverage completed - all coverage tasks done
   - All 7 coverage tasks (033-039) completed
   - Overall coverage improved to 90.21%+
   - Investigation pattern: Many tasks were based on outdated data
2. **Phases 3-7** (0 hours): All translation tasks completed - major i18n milestone! 🎉
   - **All 12 supported locales now have complete translations** (254/254 strings each)
   - 8 translation tasks completed (en_CA, ru_RU, fi_FI, cs_CZ, de_DE, de_CH, it_CH, sk_SK, lv_LV)
   - Total actual effort: ~51.5h (vs 52-66h estimated, 97% accurate)
   - **fr_CA now REVIEWED by native speaker** - first validated translation! ✅
   - Remaining locales marked as DRAFT requiring native speaker review
3. **Phase 3** (3-4 hours remaining): I18n quality review for sv_SE
4. **Phases 4-14** (77-109 hours): Test-analytics, refactoring, advanced i18n, research, infrastructure

### Implementation Notes:
- **Test Coverage Tasks** (033-039): All 7 tasks completed - comprehensive coverage initiative finished
- **Translation Tasks** (037-045): **ALL COMPLETE!** Major milestone - 12 locales, 254 strings each, 100% coverage
  - Actual total effort: ~51.5h (en_CA: 1.5h, de_CH: 4h, ru_RU: 6h, fi_FI: 6.5h, cs_CZ: 7h, de_DE: 7h, it_CH: 6.5h, sk_SK: 7h, lv_LV: 7h)
  - AI-assisted with systematic hockey terminology database
  - All marked as DRAFT requiring native speaker review
- **I18n Quality Review (046)**: **fr_CA REVIEWED!** First validated translation ✅
  - Native French Canadian speaker reviewed all 254 strings
  - Validated: natural language, Quebec hockey terminology, cultural appropriateness
  - Actual effort: ~3.5h (within 3-4h estimate)
  - Quality benchmark established for future reviews (sv_SE, de_CH, and remaining locales)
- **Quick Wins**: Task testing/023 (15min) and refactoring/024 (30min-1h) can be completed quickly
- **Major Refactoring**: Task 028 (20-29h) splits 4 large modules - significant code organization effort

---

**Last Updated**: 2026-05-14
**Next Review**: After completing Phase 1 (HIGH priority test coverage)
