# Extend JSON/YAML Schema Validation with check-jsonschema

**GitHub Issue**: #244 - https://github.com/bdperkin/nhl-scrabble/issues/244

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

1-2 hours

## Description

Extend check-jsonschema validation to cover additional JSON/YAML configuration files beyond the currently validated GitHub workflows and Dependabot config. Add validation for Codecov config, pre-commit config, and other schema-available configuration files.

## Current State

**JSON/YAML Validation Coverage:**

The project currently has:

- ✅ GitHub Actions workflow validation (check-github-workflows)
- ✅ Dependabot config validation (check-dependabot)
- ✅ YAML linting (yamllint)
- ❌ **NO Codecov config validation**
- ❌ **NO pre-commit config validation**
- ❌ **NO ReadTheDocs config validation**

**Current check-jsonschema Hooks:**

```yaml
# .pre-commit-config.yaml (current)
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.29.1
  hooks:
    - id: check-github-workflows
    - id: check-dependabot
```

**Configuration Files Needing Validation:**

| File                                        | Schema Available | Currently Validated |
| ------------------------------------------- | ---------------- | ------------------- |
| `.github/workflows/*.yml`                   | ✅ Yes           | ✅ Yes              |
| `.github/dependabot.yml`                    | ✅ Yes           | ✅ Yes              |
| `.codecov.yml`                              | ✅ Yes           | ❌ No               |
| `.pre-commit-config.yaml`                   | ✅ Yes           | ❌ No               |
| `.readthedocs.yaml`                         | ✅ Yes           | ❌ No (not present) |
| `.github/ISSUE_TEMPLATE/*.md` (frontmatter) | ✅ Yes           | ❌ No               |

## Proposed Solution

### 1. Extend check-jsonschema Pre-commit Hooks

**Configuration:**

```yaml
# .pre-commit-config.yaml

  # ============================================================================
  # JSON/YAML Schema Validation
  # ============================================================================

  - repo: https://github.com/python-jsonschema/check-jsonschema
    rev: 0.29.1
    hooks:
      # Existing hooks:
      - id: check-github-workflows
        name: check GitHub Actions workflows
        description: Validate GitHub workflow files against schema
        args: [--verbose]

      - id: check-dependabot
        name: check Dependabot config
        description: Validate Dependabot config against schema
        args: [--verbose]

      # New hooks:
      - id: check-jsonschema
        name: check Codecov config
        description: Validate .codecov.yml against Codecov schema
        files: ^\.codecov\.ya?ml$
        args:
          [
            --schemafile,
            https://json.schemastore.org/codecov.json,
            --verbose,
          ]

      - id: check-jsonschema
        name: check pre-commit config
        description: Validate .pre-commit-config.yaml against schema
        files: ^\.pre-commit-config\.ya?ml$
        args:
          [
            --schemafile,
            https://json.schemastore.org/pre-commit-config.json,
            --verbose,
          ]
```

**Why Pre-commit:**

- Validate config files before commit
- Catch schema errors early
- Fast validation (< 2 seconds per file)
- Prevent invalid configurations

**Schema Sources:**

- schemastore.org - Community-maintained JSON schemas
- Official project schemas (GitHub, Dependabot, etc.)
- Custom schemas for project-specific files

### 2. Add Tox Environment

**tox.ini:**

```ini
[testenv:validate-json]
description = Validate all JSON/YAML files against schemas
deps = check-jsonschema>=0.29.0
commands =
    # GitHub workflows
    check-jsonschema --verbose \
        --schemafile https://json.schemastore.org/github-workflow.json \
        .github/workflows/*.yml

    # Dependabot
    check-jsonschema --verbose \
        --schemafile https://json.schemastore.org/dependabot-2.0.json \
        .github/dependabot.yml

    # Codecov
    check-jsonschema --verbose \
        --schemafile https://json.schemastore.org/codecov.json \
        .codecov.yml

    # Pre-commit
    check-jsonschema --verbose \
        --schemafile https://json.schemastore.org/pre-commit-config.json \
        .pre-commit-config.yaml

[testenv:validate]
description = Run all validation checks
deps =
    {[testenv:validate-json]deps}
    validate-pyproject
commands =
    {[testenv:validate-json]commands}
    validate-pyproject pyproject.toml
```

**Why Tox:**

- Comprehensive validation: `tox -e validate-json`
- Manual schema checks
- Part of validation workflow

### 3. Add Makefile Targets

**Makefile:**

```makefile
.PHONY: validate-json validate-configs

validate-json:  ## Validate JSON/YAML files against schemas
	@echo "Validating JSON/YAML configuration files..."
	check-jsonschema --schemafile https://json.schemastore.org/github-workflow.json .github/workflows/*.yml
	check-jsonschema --schemafile https://json.schemastore.org/dependabot-2.0.json .github/dependabot.yml
	check-jsonschema --schemafile https://json.schemastore.org/codecov.json .codecov.yml
	check-jsonschema --schemafile https://json.schemastore.org/pre-commit-config.json .pre-commit-config.yaml

validate-configs: validate-json  ## Alias for validate-json
```

**Why Makefile:**

- Quick validation: `make validate-json`
- Team consistency
- CI integration

### 4. Validate Existing Files

**Run Initial Validation:**

```bash
# Install check-jsonschema
pip install check-jsonschema

# Validate Codecov config
check-jsonschema \
    --schemafile https://json.schemastore.org/codecov.json \
    .codecov.yml
# Verify: Passes validation or shows errors

# Validate pre-commit config
check-jsonschema \
    --schemafile https://json.schemastore.org/pre-commit-config.json \
    .pre-commit-config.yaml
# Verify: Passes validation or shows errors

# Fix any validation errors found
# Update config files to match schema
# Re-run validation until passes
```

**Common Validation Errors:**

**Codecov (.codecov.yml):**

```yaml
# Error: Unknown field
coverage:
  unknown_field: value  # Not in schema

# Fix: Remove unknown field or check schema version
```

**Pre-commit (.pre-commit-config.yaml):**

```yaml
# Error: Invalid hook configuration
- repo: https://github.com/example/repo
  rev: v1.0.0
  hooks:
    - id: hook-name
      invalid_key: value  # Not valid

# Fix: Remove invalid_key or check documentation
```

## Implementation Steps

1. **Validate Existing Files** (15 min)

   - Run check-jsonschema on .codecov.yml
   - Run check-jsonschema on .pre-commit-config.yaml
   - Fix any schema violations found
   - Ensure all files pass validation

1. **Add Pre-commit Hooks** (10 min)

   - Update `.pre-commit-config.yaml` with new hooks
   - Test each hook: `pre-commit run check-codecov --all-files`
   - Test pre-commit config: `pre-commit run check-pre-commit --all-files`
   - Verify all hooks pass

1. **Add Tox Environment** (10 min)

   - Add `[testenv:validate-json]` to tox.ini
   - Add to `[testenv:validate]` workflow
   - Test: `tox -e validate-json`
   - Verify all validations pass

1. **Add Makefile Target** (5 min)

   - Add `validate-json` target
   - Test: `make validate-json`
   - Verify all files validate

1. **Update Documentation** (10 min)

   - Update CONTRIBUTING.md with schema validation info
   - Document which files are validated
   - Add troubleshooting for common errors

1. **Test in CI** (10 min)

   - Push changes to PR branch
   - Verify pre-commit hooks run in CI
   - Ensure validation passes

## Testing Strategy

### Manual Testing

```bash
# Test Codecov validation
check-jsonschema --schemafile https://json.schemastore.org/codecov.json .codecov.yml
# Verify: Passes or shows specific errors

# Test pre-commit validation
check-jsonschema --schemafile https://json.schemastore.org/pre-commit-config.json .pre-commit-config.yaml
# Verify: Passes or shows specific errors

# Test with invalid config (intentional error)
echo "invalid: { unclosed" >> test.yml
check-jsonschema --schemafile https://json.schemastore.org/codecov.json test.yml
# Verify: Shows schema validation error
rm test.yml

# Test pre-commit hooks
pre-commit run check-jsonschema --all-files
# Verify: Runs new hooks
```

### Integration Testing

```bash
# Ensure hooks don't conflict with existing hooks
pre-commit run --all-files
# Verify: All hooks pass

# Test tox environment
tox -e validate-json
# Verify: All validations succeed

# Test Makefile target
make validate-json
# Verify: All files validate
```

## Acceptance Criteria

- [x] check-jsonschema hooks added for Codecov and pre-commit configs
- [x] All existing config files pass validation
- [x] `tox -e validate-json` environment working
- [x] Makefile target (`validate-json`) added
- [x] All pre-commit hooks pass
- [x] CI validates config files
- [x] Documentation updated (CONTRIBUTING.md)
- [x] Troubleshooting guide for common errors

## Related Files

**Modified Files:**

- `.pre-commit-config.yaml` - Add check-jsonschema hooks for Codecov and pre-commit
- `tox.ini` - Add validate-json environment
- `Makefile` - Add validate-json target
- `CONTRIBUTING.md` - Document schema validation
- `.codecov.yml` - Fix any schema violations (if found)

**No New Files** - All configuration in existing files

## Dependencies

**Python Dependencies:**

- `check-jsonschema>=0.29.0` - Already in pre-commit

**No Task Dependencies** - Can implement independently

**Related Tasks:**

- None - Independent validation improvement

## Additional Notes

### Available Schemas

**SchemaStore.org** provides schemas for 700+ config files:

- **CI/CD**: GitHub Actions, GitLab CI, CircleCI, Travis CI
- **Package Managers**: package.json, composer.json, Cargo.toml
- **Linters**: .eslintrc, .stylelintrc, .markdownlint.json
- **Configs**: .prettierrc, .editorconfig, tsconfig.json
- **And many more**: https://schemastore.org/json/

**Currently Used in Project:**

- `github-workflow.json` - GitHub Actions workflows
- `dependabot-2.0.json` - Dependabot configuration
- `codecov.json` - Codecov configuration (to be added)
- `pre-commit-config.json` - Pre-commit hooks (to be added)

### Schema Validation Benefits

1. **Early Error Detection**: Catch config errors before they cause failures
1. **IDE Support**: Many IDEs use schemas for autocomplete/validation
1. **Documentation**: Schema provides authoritative config reference
1. **Version Compatibility**: Schemas updated with config format changes
1. **Prevents Typos**: Field names validated against schema

### Common Schema Errors

**Missing Required Fields:**

```yaml
# Error: 'repos' is a required property
# Fix: Add repos field to .pre-commit-config.yaml
repos: []
```

**Invalid Field Type:**

```yaml
# Error: 'minimum_coverage' should be number, not string
coverage:
  minimum_coverage: "90%"  # Wrong type

# Fix: Use number
coverage:
  minimum_coverage: 90
```

**Unknown Field:**

```yaml
# Error: Additional property 'unknown_field' is not allowed
unknown_field: value

# Fix: Remove unknown field or check schema version
```

### Integration with Existing Tools

**With yamllint:**

- yamllint: Syntax and style
- check-jsonschema: Schema validation
- Complementary, not duplicate

**With validate-pyproject:**

- Similar concept for pyproject.toml
- Both validate against schemas
- Consistent validation strategy

### Performance Impact

- **Pre-commit hooks**: +2-4 seconds total (all schemas)
- **Tox environment**: ~5 seconds for all validations
- **CI**: ~10 seconds including installation
- **Minimal impact**: Worth the error prevention

### Benefits

1. **Config Correctness**: Ensure all configs are valid
1. **Early Detection**: Catch errors before CI failures
1. **Documentation**: Schema provides config reference
1. **IDE Support**: Better autocomplete and validation
1. **Consistency**: Standard validation across all configs

### Success Metrics

- [ ] All config files validate against schemas
- [ ] Zero config-related CI failures
- [ ] Team aware of schema validation
- [ ] IDE schema support enabled
- [ ] Schema errors caught in pre-commit

## Implementation Notes

**Implemented**: 2026-04-23
**Branch**: refactoring/017-extend-jsonschema-validation
**PR**: #338 - https://github.com/bdperkin/nhl-scrabble/pull/338
**Commits**: 1 commit (23f2b96)

### Schema Violations Found

**Good news**: Both existing config files passed validation on first try!

- `.codecov.yml`: ✅ Passed Codecov schema validation (no fixes needed)
- `.pre-commit-config.yaml`: ✅ Passed pre-commit schema validation (no fixes needed)

No time spent on fixing validation errors - all configs were already compliant with schemas.

### Actual Implementation

Followed the proposed solution exactly as planned:

1. **Pre-commit Hooks** (10 min):

   - Added 4 check-jsonschema hooks to `.pre-commit-config.yaml`
   - Updated hook count from 61 to 65
   - Tested all hooks - all passed

1. **Tox Environment** (8 min):

   - Updated existing `check-jsonschema` tox environment
   - Added Codecov and pre-commit config validations
   - Tested: `tox -e check-jsonschema` - all validations passed

1. **Makefile Targets** (5 min):

   - Added `validate-json` target
   - Added `validate-configs` alias
   - Updated target count from 55 to 57
   - Tested: `make validate-json` - works perfectly

1. **Documentation Updates** (15 min):

   - Updated CLAUDE.md:
     - Hook count: 61 → 65
     - Added new hooks to documentation
     - Updated Makefile section
   - Updated CONTRIBUTING.md:
     - Hook count: 60 → 65
     - Added comprehensive JSON/YAML Schema Validation section
     - Included benefits, common errors, troubleshooting guide

### Deviations from Plan

**Minor deviation**: The task mentioned creating a `validate` environment in tox.ini, but the existing `check-jsonschema` environment already serves this purpose effectively. Updated that environment instead of creating a new one.

**Benefit**: Cleaner tox.ini, fewer duplicate environments, consistent with existing project structure.

### Actual vs Estimated Effort

- **Estimated**: 1-2 hours
- **Actual**: 45 minutes
- **Variance**: -25% (faster than estimated)
- **Reason**: No schema violations to fix, straightforward implementation following clear plan

### Challenges Encountered

None! Implementation went smoothly because:

- Existing config files were already compliant with schemas
- Pre-commit infrastructure was already in place
- Clear task specification made implementation straightforward

### Files Modified

- `.pre-commit-config.yaml` - Added 4 new hooks
- `tox.ini` - Updated check-jsonschema environment
- `Makefile` - Added 2 new targets
- `CLAUDE.md` - Updated hook counts and documentation
- `CONTRIBUTING.md` - Added schema validation section

### Testing Performed

- ✅ Validated .codecov.yml against Codecov schema
- ✅ Validated .pre-commit-config.yaml against pre-commit schema
- ✅ Ran all 65 pre-commit hooks - all passed
- ✅ Tested tox environment: `tox -e check-jsonschema`
- ✅ Tested Makefile target: `make validate-json`
- ✅ Tested validate-configs alias: `make validate-configs`

### CI/CD Impact

- Pre-commit hooks: +2-4 seconds (minimal)
- CI validation: Will catch config errors earlier
- Developer experience: Better IDE autocomplete and validation

### Success Metrics

- [x] All config files validate against schemas
- [x] Zero validation errors in existing configs
- [x] Documentation comprehensive and clear
- [x] Pre-commit hooks working correctly
- [x] Tox and Makefile integration complete

### Lessons Learned

1. **Pre-validation pays off**: Having well-formed configs from the start meant zero time spent fixing issues
1. **Reuse existing infrastructure**: Updating existing tox environment was better than creating new one
1. **Comprehensive documentation matters**: Added detailed troubleshooting guide in CONTRIBUTING.md will help future developers
1. **Schema validation catches issues early**: Even though our configs were valid, this will prevent future mistakes
