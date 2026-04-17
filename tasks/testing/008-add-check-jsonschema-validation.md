# Add check-jsonschema for JSON/YAML File Validation

**GitHub Issue**: #128 - https://github.com/bdperkin/nhl-scrabble/issues/128

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

30-60 minutes

## Description

Add check-jsonschema for automated validation of JSON and YAML files against JSON Schema definitions to catch structural errors, type mismatches, and invalid configurations before runtime.

Currently, the project has JSON files (test fixtures in `tests/fixtures/*.json`) and YAML files (GitHub workflows in `.github/workflows/*.yml`) with no automated schema validation. Invalid JSON structure or GitHub workflow syntax errors only surface when tests run or workflows execute, making debugging slower and potentially breaking CI.

check-jsonschema provides:

- Validation against JSON Schema definitions
- Built-in schemas for common files (GitHub Actions, Renovate, Azure Pipelines, etc.)
- Custom schema support for project-specific files
- Pre-commit hook integration
- CI integration to block invalid configs

**Impact**: Catch JSON/YAML structure errors early, prevent invalid GitHub workflow syntax, validate test fixtures, improved configuration file quality

**ROI**: Moderate - low setup effort (30-60 min), prevents CI failures from invalid YAML/JSON

## Current State

Project has JSON and YAML files with no schema validation:

**Test fixtures** (`tests/fixtures/`):

```bash
$ ls tests/fixtures/
sample_roster.json
sample_standings.json
```

Example fixture structure:

```json
{
  "forwards": [...],
  "defensemen": [...],
  "goalies": [...]
}
```

**GitHub workflows** (`.github/workflows/`):

```bash
$ ls .github/workflows/
ci.yml
docs.yml
security.yml
```

**Problems**:

- Invalid JSON/YAML only caught when used
- GitHub workflow syntax errors only caught in CI
- Test fixture schema drift undetected
- Manual validation required

**Missing tool**:

- No check-jsonschema in dependencies
- No schema validation in pre-commit
- No JSON/YAML checks in CI
- Could have invalid configs and not know

## Proposed Solution

Add check-jsonschema with validation for GitHub workflows and test fixtures:

**Step 1: Add check-jsonschema to dependencies**:

```toml
# pyproject.toml
[project.optional-dependencies]
dev = [
    "ruff>=0.3.0",
    "mypy>=1.8.0",
    "pre-commit>=3.6.0",
    "check-jsonschema>=0.28.0",  # Add JSON/YAML schema validation
    # ... other dev dependencies
]
```

**Step 2: Add pre-commit hooks**:

```yaml
# .pre-commit-config.yaml
# Add after check-json, check-yaml
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.28.0
  hooks:
    # Validate GitHub workflows against schema
    - id: check-github-workflows
      name: Validate GitHub workflows
      files: ^\.github/workflows/.*\.ya?ml$

    # Validate GitHub Actions against schema
    - id: check-github-actions
      name: Validate GitHub actions
      files: ^\.github/actions/.*\.ya?ml$

    # Validate Dependabot config (if exists)
    - id: check-dependabot
      name: Validate Dependabot config
      files: ^\.github/dependabot\.ya?ml$

    # Custom: Validate test fixtures (if schema created)
    - id: check-jsonschema
      name: Validate test fixture JSON
      files: ^tests/fixtures/.*\.json$
      args:
        - --schemafile
        - tests/schemas/fixture-schema.json  # Custom schema
```

**Step 3: Add tox environment**:

```ini
# tox.ini
[testenv:check-jsonschema]
description = Validate JSON and YAML files against schemas
skip_install = true
deps =
    check-jsonschema>=0.28.0
commands_pre =
    check-jsonschema --version
commands =
    # Validate GitHub workflows
    check-jsonschema --schemafile "https://json.schemastore.org/github-workflow.json" \
        .github/workflows/*.yml

    # Validate GitHub Actions (if any)
    check-jsonschema --schemafile "https://json.schemastore.org/github-action.json" \
        .github/actions/*/action.yml || true

    # Validate Dependabot config (if exists)
    check-jsonschema --schemafile "https://json.schemastore.org/dependabot-2.0.json" \
        .github/dependabot.yml || true

    # Validate test fixtures (if schema created)
    check-jsonschema --schemafile tests/schemas/fixture-schema.json \
        tests/fixtures/*.json || true
allowlist_externals =
    check-jsonschema
labels = quality, validation
```

**Step 4: Create custom schema for test fixtures** (optional):

```json
// tests/schemas/fixture-schema.json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "NHL API Roster Response",
  "type": "object",
  "required": ["forwards", "defensemen", "goalies"],
  "properties": {
    "forwards": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "firstName", "lastName"],
        "properties": {
          "id": {"type": "integer"},
          "firstName": {"type": "object", "properties": {"default": {"type": "string"}}},
          "lastName": {"type": "object", "properties": {"default": {"type": "string"}}},
          "sweaterNumber": {"type": "integer"},
          "positionCode": {"type": "string"}
        }
      }
    },
    "defensemen": {
      "type": "array",
      "items": {"$ref": "#/properties/forwards/items"}
    },
    "goalies": {
      "type": "array",
      "items": {"$ref": "#/properties/forwards/items"}
    }
  }
}
```

**Step 5: CLI usage examples**:

```bash
# Validate GitHub workflows
check-jsonschema --schemafile "https://json.schemastore.org/github-workflow.json" \
    .github/workflows/ci.yml

# Validate all workflows
check-jsonschema --schemafile "https://json.schemastore.org/github-workflow.json" \
    .github/workflows/*.yml

# Validate with custom schema
check-jsonschema --schemafile tests/schemas/fixture-schema.json \
    tests/fixtures/sample_roster.json

# Via tox
tox -e check-jsonschema

# Via pre-commit
pre-commit run check-github-workflows --all-files
```

**Step 6: Example output**:

```bash
$ check-jsonschema --schemafile "https://json.schemastore.org/github-workflow.json" \
    .github/workflows/ci.yml

ok -- validation done, no errors

$ check-jsonschema --schemafile "https://json.schemastore.org/github-workflow.json" \
    .github/workflows/broken.yml

ValidationError: 'on' is a required property

Failed validating 'required' in schema:
    {'$schema': 'http://json-schema.org/draft-07/schema',
     'required': ['on', 'jobs'],
     ...}

On instance:
    {'jobs': {...}}
```

## Implementation Steps

1. **Add check-jsonschema to dependencies**:

   - Update `pyproject.toml` `[project.optional-dependencies.dev]`
   - Add `check-jsonschema>=0.28.0`

1. **Add pre-commit hooks**:

   - Add hooks for GitHub workflows validation
   - (Optional) Add hooks for GitHub actions validation
   - (Optional) Add hooks for Dependabot config
   - (Optional) Add hooks for test fixtures with custom schema

1. **Add tox environment**:

   - Create `[testenv:check-jsonschema]` in `tox.ini`
   - Configure to validate all JSON/YAML files

1. **Update lock file**:

   - Run `uv lock` to update dependencies

1. **Run initial validation**:

   - Run `check-jsonschema` on existing files
   - Identify any schema violations
   - Fix issues or document exceptions

1. **(Optional) Create custom schemas**:

   - Create `tests/schemas/` directory
   - Write JSON Schema for test fixtures
   - Validate fixtures against schema

1. **Test pre-commit integration**:

   - Modify a workflow file
   - Verify pre-commit catches invalid syntax
   - Verify valid changes pass

1. **Document usage**:

   - Add to CONTRIBUTING.md
   - Explain schema validation
   - Document how to update schemas

## Testing Strategy

**GitHub Workflow Validation**:

```bash
# Test valid workflow
check-jsonschema --schemafile "https://json.schemastore.org/github-workflow.json" \
    .github/workflows/ci.yml

# Expected: ok -- validation done, no errors

# Test invalid workflow (temporarily break one)
# Remove required 'on:' key from workflow
check-jsonschema --schemafile "https://json.schemastore.org/github-workflow.json" \
    .github/workflows/ci.yml

# Expected: ValidationError: 'on' is a required property
```

**Test Fixture Validation** (if custom schema created):

```bash
# Validate test fixtures
check-jsonschema --schemafile tests/schemas/fixture-schema.json \
    tests/fixtures/sample_roster.json

# Expected: Passes if fixtures match API structure
# Or: ValidationError if structure mismatch
```

**Pre-commit Integration**:

```bash
# Test pre-commit hook
pre-commit run check-github-workflows --all-files

# Make invalid change to workflow
echo "invalid: yaml: syntax:" >> .github/workflows/ci.yml

# Run pre-commit
pre-commit run check-github-workflows --files .github/workflows/ci.yml

# Expected: Hook catches invalid YAML
```

**CI Integration Test**:

```bash
# Via tox (simulates CI)
tox -e check-jsonschema

# Expected: Exit 0 if all files valid
```

## Acceptance Criteria

- [ ] check-jsonschema added to `[project.optional-dependencies.dev]`
- [ ] Lock file updated with check-jsonschema
- [ ] Pre-commit hook added for GitHub workflows validation
- [ ] `[testenv:check-jsonschema]` added to `tox.ini`
- [ ] Running `check-jsonschema` on `.github/workflows/*.yml` passes
- [ ] All GitHub workflows validate successfully
- [ ] Pre-commit hook triggers on workflow file changes
- [ ] (Optional) Custom schema created for test fixtures in `tests/schemas/`
- [ ] (Optional) Test fixtures validate against custom schema
- [ ] (Optional) Pre-commit hook added for test fixture validation
- [ ] Documentation updated (CONTRIBUTING.md)

## Related Files

- `pyproject.toml` - Add check-jsonschema dependency
- `.pre-commit-config.yaml` - Add check-jsonschema hooks
- `tox.ini` - Add check-jsonschema tox environment
- `.github/workflows/*.yml` - GitHub workflow files to validate
- `tests/fixtures/*.json` - Test fixture JSON files
- `tests/schemas/` - Custom JSON schemas (new directory, optional)
- `tests/schemas/fixture-schema.json` - Custom schema for test fixtures (optional)
- `CONTRIBUTING.md` - Document schema validation
- `uv.lock` - Updated with check-jsonschema

## Dependencies

**Recommended implementation order**:

- Can be implemented independently
- Low priority (quality improvement, not critical)
- Higher value if more JSON/YAML files added

**No blocking dependencies** - Can be implemented standalone

**Works with**:

- Existing check-json, check-yaml hooks
- All pre-commit hooks
- Tox environments
- CI workflows

## Additional Notes

**Why check-jsonschema?**

- **Built-in schemas**: GitHub workflows, Renovate, many common formats
- **Custom schemas**: Support project-specific validation
- **Fast**: Written in Python, fast validation
- **Pre-commit ready**: Easy integration
- **Standards-based**: Uses JSON Schema specification
- **Active**: Well-maintained, 500+ stars

**How check-jsonschema Works**:

```
Validation process:
  1. Load JSON/YAML file
  2. Parse into data structure
  3. Load schema (URL or local file)
  4. Validate data against schema
  5. Check required fields, types, formats
  6. Report validation errors or success
```

**Built-in Schema URLs**:

| File Type           | Schema URL                                        |
| ------------------- | ------------------------------------------------- |
| **GitHub Workflow** | https://json.schemastore.org/github-workflow.json |
| **GitHub Action**   | https://json.schemastore.org/github-action.json   |
| **Dependabot**      | https://json.schemastore.org/dependabot-2.0.json  |
| **Renovate**        | https://json.schemastore.org/renovate.json        |
| **Azure Pipelines** | https://json.schemastore.org/azure-pipelines.json |
| **package.json**    | https://json.schemastore.org/package.json         |
| **tsconfig.json**   | https://json.schemastore.org/tsconfig.json        |

See full list: https://www.schemastore.org/json/

**Hook IDs Available**:

```yaml
# Pre-built hooks for common files
- id: check-github-workflows    # .github/workflows/*.yml
- id: check-github-actions       # .github/actions/*/action.yml
- id: check-dependabot          # .github/dependabot.yml
- id: check-renovate            # renovate.json
- id: check-azure-pipelines     # azure-pipelines.yml
- id: check-readthedocs         # .readthedocs.yml
- id: check-gitlab-ci           # .gitlab-ci.yml

# Generic hook for custom schemas
- id: check-jsonschema          # Any JSON/YAML with custom schema
```

**Custom Schema Example**:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "My Config File",
  "type": "object",
  "required": ["version", "settings"],
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
    },
    "settings": {
      "type": "object",
      "properties": {
        "enabled": {"type": "boolean"},
        "count": {"type": "integer", "minimum": 0}
      }
    }
  }
}
```

**CLI Options**:

```bash
# Basic validation
check-jsonschema --schemafile SCHEMA FILE

# Multiple files
check-jsonschema --schemafile SCHEMA file1.json file2.json

# Glob pattern
check-jsonschema --schemafile SCHEMA *.json

# Schema from URL
check-jsonschema --schemafile "https://..." file.json

# Schema from local file
check-jsonschema --schemafile schema.json file.json

# Check format without validation
check-jsonschema --check-metaschema schema.json

# Default instance value
check-jsonschema --schemafile schema.json --default-filetype json file.txt

# Fill defaults (modify file)
check-jsonschema --schemafile schema.json --fill-defaults file.json
```

**Validation Error Example**:

```bash
$ check-jsonschema --schemafile schema.json data.json

Schema validation errors were encountered.
  data.json::$.settings.count: -5 is less than the minimum of 0

  Failed validating 'minimum' in schema['properties']['settings']['properties']['count']:
      {'minimum': 0, 'type': 'integer'}

  On instance['settings']['count']:
      -5
```

**Integration with GitHub Actions**:

Already built-in! GitHub workflow files automatically validated against official schema.

```yaml
# .github/workflows/ci.yml will be validated against:
# https://json.schemastore.org/github-workflow.json
```

Common errors caught:

- Missing required fields (`on:`, `jobs:`)
- Invalid job names (spaces, special chars)
- Unknown workflow keys
- Invalid step syntax
- Type mismatches (string vs array)

**Test Fixture Schema Benefits**:

For this project's test fixtures:

```json
// tests/fixtures/sample_roster.json
{
  "forwards": [...],
  "defensemen": [...],
  "goalies": [...]
}
```

Schema would catch:

- Missing player fields (firstName, lastName)
- Type mismatches (id as string instead of int)
- Invalid position codes
- Schema drift as API changes

**When check-jsonschema is Most Valuable**:

1. **Many config files**: More files = more value
1. **GitHub Actions heavy**: Lots of workflows/actions
1. **Test fixtures**: API response fixtures that can drift
1. **JSON/YAML configs**: Any structured config files
1. **Multi-developer teams**: Catches config mistakes in PRs

**Current Project Scope**:

- **~10 YAML files** (.github/workflows, configs)
- **2-3 JSON files** (test fixtures)
- **Value**: LOW to MODERATE

**Future Value** (if files grow):

- Add more GitHub workflows
- Add more test fixtures
- Add JSON API schemas
- Add config files
- Value increases significantly

**Alternative Tools Considered**:

| Tool         | Pros                      | Cons                 |
| ------------ | ------------------------- | -------------------- |
| **yamllint** | Fast YAML linting         | No schema validation |
| **jsonlint** | Simple JSON validation    | No schema validation |
| **ajv-cli**  | Fast JSON Schema          | Node.js dependency   |
| **yajsv**    | Fast YAML/JSON validation | Go binary            |

**Best Practices**:

```bash
# ✅ Good: Validate before committing
check-jsonschema --schemafile SCHEMA file.yml
git add file.yml
git commit

# ✅ Good: Use built-in schemas when available
check-jsonschema --schemafile "https://json.schemastore.org/github-workflow.json"

# ✅ Good: Create schemas for important fixtures
# Prevents schema drift as APIs change

# ✅ Good: Run in CI to catch issues in PRs
tox -e check-jsonschema

# ❌ Bad: Skipping validation errors
# Fix the file or update the schema

# ❌ Bad: Not versioning custom schemas
# Commit schemas to git

# ❌ Bad: Overly strict schemas
# Allow flexibility where appropriate
```

**Common Questions**:

**Q: Will this validate all YAML files?**
A: No, only files with schemas. Use yamllint for general YAML linting.

**Q: Does it work with YAML?**
A: Yes, validates both JSON and YAML against JSON Schema.

**Q: Can I validate against multiple schemas?**
A: No, one schema per validation. Run multiple checks for different file types.

**Q: Does it modify files?**
A: Only with `--fill-defaults` flag. Otherwise, read-only validation.

**Q: Is it slow?**
A: No, very fast. Validates 100 files in \<1 second.

**Q: Should I create schemas for test fixtures?**
A: Optional. Useful if fixtures are complex or API changes frequently.

## Implementation Notes

*To be filled during implementation:*

- Number of JSON/YAML files validated
- Any validation errors found initially
- Whether custom schemas created for test fixtures
- Whether added to CI or kept local-only
- Developer feedback on schema validation utility
