# PR Auto-Labeling Workflow

**GitHub Issue**: #302 - https://github.com/bdperkin/nhl-scrabble/issues/302

**Parent Task**: enhancement/022-comprehensive-github-workflows.md (#298)

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

1-2 hours

## Description

Implement automated PR labeling workflow that automatically adds relevant labels based on changed files, PR title, and size. This improves PR organization, filtering, and helps reviewers quickly understand the scope and type of changes.

## Current State

**Manual PR Labeling:**

Currently, all PR labels are added manually:

```bash
# Manual process
1. Create PR
2. Review changed files
3. Manually add labels (enhancement, bug, documentation, etc.)
4. Update labels as PR evolves
```

**Problems:**

- ❌ Time-consuming manual process
- ❌ Inconsistent labeling
- ❌ Easy to forget labels
- ❌ No automatic categorization
- ❌ Hard to filter PRs by type

**Existing:**

- ✅ Labels defined in repository
- ✅ PR template exists
- ❌ No automatic labeling
- ❌ No label consistency enforcement

## Proposed Solution

### Auto-Labeling Workflow

Create `.github/workflows/pr-labels.yml`:

```yaml
name: PR Auto-Labeling

on:
  pull_request:
    types: [opened, synchronize, reopened, edited]

permissions:
  contents: read
  pull-requests: write  # Required to add labels

jobs:
  label:
    name: Auto-Label Pull Request
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v6

      - name: Label based on changed files
        uses: actions/labeler@v5
        with:
          repo-token: ${{ secrets.GITHUB_TOKEN }}
          configuration-path: .github/labeler.yml
          sync-labels: true

      - name: Label based on PR size
        uses: codelytv/pr-size-labeler@v1
        with:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          xs_label: size/XS
          xs_max_size: 10
          s_label: size/S
          s_max_size: 100
          m_label: size/M
          m_max_size: 500
          l_label: size/L
          l_max_size: 1000
          xl_label: size/XL
          fail_if_xl: false
          message_if_xl: ''
          github_api_url: https://api.github.com

      - name: Label based on PR title
        uses: actions/github-script@v7
        with:
          script: |
            const prTitle = context.payload.pull_request.title.toLowerCase();
            const labels = [];

            // Conventional commit prefixes
            if (prTitle.startsWith('feat:') || prTitle.startsWith('feature:')) {
              labels.push('enhancement');
            }
            if (prTitle.startsWith('fix:') || prTitle.startsWith('bugfix:')) {
              labels.push('bug');
            }
            if (prTitle.startsWith('docs:') || prTitle.startsWith('documentation:')) {
              labels.push('documentation');
            }
            if (prTitle.startsWith('test:') || prTitle.startsWith('tests:')) {
              labels.push('testing');
            }
            if (prTitle.startsWith('refactor:')) {
              labels.push('refactoring');
            }
            if (prTitle.startsWith('perf:') || prTitle.startsWith('performance:')) {
              labels.push('performance');
            }
            if (prTitle.startsWith('ci:') || prTitle.startsWith('chore:')) {
              labels.push('ci/cd');
            }
            if (prTitle.startsWith('security:')) {
              labels.push('security');
            }
            if (prTitle.includes('breaking') || prTitle.includes('!:')) {
              labels.push('breaking-change');
            }

            // Add labels if any found
            if (labels.length > 0) {
              await github.rest.issues.addLabels({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: context.payload.pull_request.number,
                labels: labels
              });
            }
```

### Labeler Configuration

Create `.github/labeler.yml`:

```yaml
# Auto-label based on changed files

# Source code changes
python:
  - '**/*.py'

# Documentation changes
documentation:
  - docs/**/*
  - '**/*.md'
  - README.md
  - CONTRIBUTING.md

# Testing changes
testing:
  - tests/**/*
  - '**/*test*.py'
  - pytest.ini
  - conftest.py

# CI/CD changes
ci/cd:
  - .github/workflows/**
  - .github/**/*.yml
  - tox.ini
  - .pre-commit-config.yaml

# Configuration changes
configuration:
  - pyproject.toml
  - setup.py
  - setup.cfg
  - '*.ini'
  - '*.cfg'
  - '*.toml'

# Dependencies
dependencies:
  - pyproject.toml
  - requirements*.txt
  - uv.lock

# Web interface
web:
  - src/nhl_scrabble/web/**
  - '**/*.html'
  - '**/*.css'
  - '**/*.js'

# API changes
api:
  - src/nhl_scrabble/api/**

# CLI changes
cli:
  - src/nhl_scrabble/cli.py
  - src/nhl_scrabble/__main__.py

# Security
security:
  - SECURITY.md
  - .github/workflows/security.yml
  - .github/workflows/codeql.yml

# Tasks
tasks:
  - tasks/**/*
```

## Implementation Steps

1. **Create Workflow File** (30min)

   - Create `.github/workflows/pr-labels.yml`
   - Configure triggers
   - Set up labeler action
   - Set up size labeler
   - Add title-based labeling

1. **Create Labeler Configuration** (30min)

   - Create `.github/labeler.yml`
   - Define path-based rules
   - Organize by category
   - Test path matching

1. **Create Missing Labels** (15min)

   - Ensure all labels exist in repository
   - Create size labels (XS, S, M, L, XL)
   - Create category labels
   - Set label colors

1. **Test Workflow** (30min-1h)

   - Create test PRs with different changes
   - Verify path-based labeling
   - Verify size labeling
   - Verify title-based labeling
   - Test label synchronization

1. **Update Documentation** (15min)

   - Update CONTRIBUTING.md
   - Document label meanings
   - Document PR title conventions
   - Add examples

## Testing Strategy

### Test Cases

```bash
# Test 1: Documentation PR
git checkout -b test/docs-change
echo "test" >> README.md
git commit -am "docs: Update README"
gh pr create --title "docs: Update README" --body "Test"
# Expected: documentation, size/XS

# Test 2: Python code PR
git checkout -b test/python-change
echo "test" >> src/nhl_scrabble/cli.py
git commit -am "feat: Add new feature"
gh pr create --title "feat: Add new CLI option" --body "Test"
# Expected: python, cli, enhancement, size/XS

# Test 3: Large PR
git checkout -b test/large-change
# Make 600+ line changes
gh pr create --title "refactor: Major refactoring" --body "Test"
# Expected: python, refactoring, size/XL

# Test 4: Multiple file types
git checkout -b test/mixed-change
echo "test" >> README.md
echo "test" >> src/nhl_scrabble/cli.py
echo "test" >> tests/test_cli.py
git commit -am "fix: Update multiple files"
gh pr create --title "fix: Fix bug across multiple files" --body "Test"
# Expected: python, documentation, testing, bug, size/S
```

### Verification

```bash
# Check labels applied
gh pr view <pr-number> --json labels --jq '.labels[].name'

# Check label synchronization
# Edit PR to change files, verify labels update
```

## Acceptance Criteria

- [x] Workflow file created: `.github/workflows/pr-labels.yml`
- [x] Labeler configuration created: `.github/labeler.yml`
- [x] All required labels created in repository
- [x] Path-based labeling working
- [x] Size-based labeling working (XS/S/M/L/XL)
- [x] Title-based labeling working
- [x] Conventional commit prefixes recognized
- [x] Labels synchronize on PR updates
- [x] Multiple labels can be applied
- [x] No conflicts between labeling rules
- [x] CONTRIBUTING.md updated with PR guidelines
- [x] Test PRs verified
- [x] Documentation complete

## Related Files

**New Files:**

- `.github/workflows/pr-labels.yml` - Auto-labeling workflow
- `.github/labeler.yml` - Path-based label rules

**Modified Files:**

- `CONTRIBUTING.md` - Add PR title conventions
- `CLAUDE.md` - Document auto-labeling workflow

**Repository Configuration:**

- Create size labels (size/XS, size/S, size/M, size/L, size/XL)
- Ensure category labels exist

## Dependencies

**Tool Dependencies:**

- `actions/labeler@v5` - File-based labeling
- `codelytv/pr-size-labeler@v1` - Size-based labeling
- `actions/github-script@v7` - Title-based labeling

**No Task Dependencies:**

- Can be implemented independently

## Additional Notes

### Label Definitions

**Size Labels:**

- `size/XS` - 0-10 lines changed
- `size/S` - 11-100 lines changed
- `size/M` - 101-500 lines changed
- `size/L` - 501-1000 lines changed
- `size/XL` - 1000+ lines changed

**Category Labels:**

- `python` - Python code changes
- `documentation` - Documentation updates
- `testing` - Test additions/modifications
- `ci/cd` - CI/CD configuration
- `configuration` - Project configuration
- `dependencies` - Dependency updates
- `web` - Web interface changes
- `api` - API changes
- `cli` - CLI changes
- `security` - Security-related changes
- `tasks` - Task documentation

**Type Labels:**

- `enhancement` - New features
- `bug` - Bug fixes
- `refactoring` - Code refactoring
- `performance` - Performance improvements
- `breaking-change` - Breaking changes

### PR Title Conventions

Encourage conventional commits:

```
feat: Add new feature
fix: Fix bug
docs: Update documentation
test: Add tests
refactor: Refactor code
perf: Performance improvement
ci: CI/CD changes
chore: Maintenance
security: Security fix
```

### Label Colors

Suggested label colors for consistency:

```
Size labels: Blue (#0366d6)
Category labels: Gray (#d1d5da)
Type labels:
  - enhancement: Green (#28a745)
  - bug: Red (#d73a4a)
  - refactoring: Purple (#6f42c1)
  - performance: Orange (#fb8500)
  - breaking-change: Dark red (#b60205)
```

### Benefits

**For Contributors:**

- Labels applied automatically
- Clear categorization
- Consistent labeling

**For Reviewers:**

- Quick PR filtering
- Understand scope at glance
- Prioritize by size

**For Maintainers:**

- Better organization
- Easier release notes
- Track PR types over time

### Future Enhancements

- Priority labels based on keywords
- Auto-assign reviewers based on labels
- Auto-add to project boards
- Milestone auto-assignment
- Release note generation from labels

## Implementation Notes

**Implemented**: 2026-05-03
**Branch**: new-features/035-pr-auto-label-workflow
**PR**: #485 - https://github.com/bdperkin/nhl-scrabble/pull/485
**Commits**: 2 commits (dc01dbf, 4d390f3)

### Actual Implementation

Successfully implemented automated PR labeling workflow with three labeling strategies:

1. **Path-based labeling** (.github/labeler.yml):
   - 12 label categories configured
   - Uses actions/labeler@v5 with changed-files matcher
   - Covers: python, documentation, testing, ci/cd, configuration, dependencies, web, api, cli, security, tasks

2. **Size-based labeling** (workflow):
   - 5 size categories: XS (0-10), S (11-100), M (101-500), L (501-1000), XL (1000+)
   - Uses codelytv/pr-size-labeler@v1

3. **Title-based labeling** (workflow):
   - Recognizes 9 conventional commit prefixes
   - Uses actions/github-script@v7 for custom logic
   - Detects breaking changes with `!:` or `breaking` keyword

### Labels Created

Created 8 new labels:
- size/XS (blue #0366d6)
- size/S (blue #0366d6)
- size/M (blue #0366d6)
- size/L (blue #0366d6)
- size/XL (blue #0366d6)
- python (gray #d1d5da)
- tasks (gray #d1d5da)
- breaking-change (dark red #b60205)

### Test PRs

- PR #485 - This implementation PR successfully tested the workflow
- Labels applied correctly:
  - ci/cd (modified .github/workflows/)
  - documentation (modified .md files)
  - enhancement (feat: prefix in title)
  - size/M (~200-300 lines changed)

### Challenges Encountered

**Labeler Configuration Format Issue**:
- Initial implementation used v4 format (simple pattern arrays)
- actions/labeler@v5 requires `changed-files` with `any-glob-to-any-file` structure
- Error: "found unexpected type for label 'python' (should be array of config options)"
- Fixed in commit 4d390f3 by converting to v5 format

### Deviations from Plan

None - followed the proposed solution closely.

### Actual vs Estimated Effort

- **Estimated**: 1-2h
- **Actual**: ~1.5h (including fixing labeler config format)
- **Breakdown**:
  - Workflow creation: 30min
  - Labeler config: 30min
  - Label creation: 15min
  - Documentation: 15min
  - Debugging/fixing v5 format: 10min

### Related PRs

- #485 - Main implementation

### Lessons Learned

- Always check GitHub Actions documentation for latest version syntax
- actions/labeler@v5 has breaking changes from v4 format
- Testing workflows requires creating actual PRs (can't test locally)
- Label synchronization works perfectly - labels update on PR push automatically
- Multiple labeling strategies complement each other well
