# Automate CHANGELOG Generation from Git Tags and Commits

**GitHub Issue**: [#379](https://github.com/bdperkin/nhl-scrabble/issues/379)

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

4-6 hours

## Description

Automate the generation and maintenance of CHANGELOG.md using git history (tags and conventional commits). Currently, CHANGELOG.md is manually updated for each release, which is error-prone, time-consuming, and can lead to missed changes or inconsistencies.

The project already uses:
- Conventional commit messages (feat, fix, docs, refactor, ci, etc.)
- Dynamic versioning from git tags via hatch-vcs (task #010)
- Keep a Changelog format

Automating changelog generation will:
- Reduce manual work during releases
- Ensure all changes are documented
- Maintain consistency with Keep a Changelog format
- Integrate with the existing CI/CD release process

## Current State

**Manual CHANGELOG.md Maintenance:**

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.1.0] - 2026-04-25

### Deprecated

- **CSVExporter Class** - Deprecated in favor of CSVFormatter...
```

**Current Process:**
1. Developer makes changes with conventional commits
2. Before release, manually review git log
3. Manually categorize changes into CHANGELOG.md sections
4. Manually format entries following Keep a Changelog guidelines
5. Commit CHANGELOG.md updates
6. Create git tag for release

**Issues:**
- Time-consuming manual process
- Easy to miss commits or categorize incorrectly
- Inconsistent formatting between releases
- Requires reviewing entire git log manually
- No validation that all changes are documented

**Existing Infrastructure:**
- ✅ Conventional commits used throughout codebase
- ✅ Dynamic versioning from git tags (hatch-vcs)
- ✅ Keep a Changelog format established
- ✅ Semantic versioning adopted
- ❌ No automated changelog generation
- ❌ No CI integration for changelog updates

## Proposed Solution

Implement automated CHANGELOG.md generation using **git-cliff** (Rust-based, fast, highly configurable):

### Why git-cliff?

**Advantages:**
- Native Keep a Changelog format support
- Conventional Commits parser built-in
- Highly configurable via TOML config
- Fast (written in Rust)
- Supports custom commit parsers and templates
- GitHub Actions integration available
- Active development and community
- Can update existing changelog or generate from scratch
- Supports version tag detection
- Filters out irrelevant commits (CI, chores, etc.)

**Alternatives Considered:**
- `auto-changelog`: JavaScript-based, less flexible
- `conventional-changelog`: JavaScript ecosystem, complex setup
- `git-chglog`: Go-based, less active
- Manual scripts: Reinventing the wheel

### Configuration (cliff.toml)

Create `.cliff.toml` with Keep a Changelog mapping:

```toml
[changelog]
# Keep a Changelog format
header = """
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

"""
# Template for each release section
body = """
{% if version %}\
    ## [{{ version | trim_start_matches(pat="v") }}] - {{ timestamp | date(format="%Y-%m-%d") }}
{% else %}\
    ## [Unreleased]
{% endif %}\
{% for group, commits in commits | group_by(attribute="group") %}
    ### {{ group | upper_first }}
    {% for commit in commits %}
        - {{ commit.message | upper_first }} ({{ commit.id | truncate(length=7, end="") }})
    {%- endfor %}
{% endfor %}\n
"""
# Remove trailing whitespace
trim = true

[git]
# Parse conventional commits
conventional_commits = true
# Filter out commits
filter_unconventional = true
# Split commits by type
split_commits = false
# Commit parsers (map types to changelog groups)
commit_parsers = [
  { message = "^feat", group = "Added" },
  { message = "^fix", group = "Fixed" },
  { message = "^doc", group = "Documentation" },
  { message = "^perf", group = "Performance" },
  { message = "^refactor", group = "Changed" },
  { message = "^style", skip = true },
  { message = "^test", skip = true },
  { message = "^chore", skip = true },
  { message = "^ci", skip = true },
  { message = "^build", skip = true },
]
# Protect against malformed commits
filter_commits = false
# Tag pattern
tag_pattern = "v[0-9]*"
# Skip tags
skip_tags = ""
# Ignore tags
ignore_tags = ""
# Sort commits oldest first
sort_commits = "oldest"
```

### Local Usage

```bash
# Generate changelog for unreleased commits
git cliff --unreleased

# Generate changelog and update CHANGELOG.md
git cliff --output CHANGELOG.md

# Generate changelog for specific version range
git cliff v0.0.1..v0.1.0

# Generate full changelog from all tags
git cliff --tag v0.1.0
```

### CI/CD Integration (GitHub Actions)

Add to release workflow (`.github/workflows/release.yml`):

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  changelog:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v6
        with:
          fetch-depth: 0  # Full history for git-cliff

      - name: Generate Changelog
        uses: orhun/git-cliff-action@v4
        with:
          config: cliff.toml
          args: --verbose --tag ${{ github.ref_name }}
        env:
          OUTPUT: CHANGELOG.md

      - name: Commit Changelog
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add CHANGELOG.md
          git commit -m "docs(changelog): Update CHANGELOG.md for ${{ github.ref_name }}"
          git push

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          body_path: CHANGELOG.md
          generate_release_notes: false
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Makefile Integration

Add convenience targets:

```makefile
# Generate changelog preview (unreleased)
changelog-preview:
	git-cliff --unreleased

# Update CHANGELOG.md
changelog-update:
	git-cliff --output CHANGELOG.md

# Generate changelog for specific tag
changelog-tag:
	git-cliff --tag $(TAG)
```

### Documentation Updates

Update documentation to explain:
- Conventional commit requirement
- How CHANGELOG.md is auto-generated
- Local testing with `git-cliff`
- CI/CD changelog integration

## Implementation Steps

1. **Install and Configure git-cliff** (1h)
   - Add git-cliff to development dependencies
   - Create `.cliff.toml` configuration
   - Test locally with existing git history
   - Validate Keep a Changelog format output
   - Fine-tune commit parsers for project needs

2. **Integrate with Makefile** (30min)
   - Add `changelog-preview` target
   - Add `changelog-update` target
   - Add `changelog-tag` target
   - Document in Makefile help

3. **CI/CD Integration** (1-2h)
   - Create/update `.github/workflows/release.yml`
   - Add git-cliff-action step
   - Add auto-commit step for CHANGELOG.md
   - Test with dummy tag/release
   - Ensure GitHub release includes changelog

4. **Documentation** (1h)
   - Update CONTRIBUTING.md with commit message guidelines
   - Document automated changelog process
   - Add Makefile reference entry
   - Update release process documentation
   - Add examples of conventional commits

5. **Testing and Validation** (1-1.5h)
   - Generate changelog from current history
   - Validate format matches Keep a Changelog
   - Test unreleased changes detection
   - Test version range generation
   - Verify CI/CD workflow (dry run)
   - Compare output to current manual CHANGELOG.md

## Testing Strategy

### Manual Testing

```bash
# 1. Install git-cliff
cargo install git-cliff
# or
brew install git-cliff

# 2. Test changelog generation (dry run)
git cliff --unreleased --output /dev/stdout

# 3. Test specific version range
git cliff v0.0.1..HEAD --output /dev/stdout

# 4. Test full changelog generation
git cliff --output test-changelog.md
diff CHANGELOG.md test-changelog.md

# 5. Validate Keep a Changelog format
# Check sections: Added, Changed, Deprecated, Removed, Fixed, Security
```

### CI/CD Testing

```bash
# 1. Create test tag
git tag v0.1.1-test
git push origin v0.1.1-test

# 2. Monitor GitHub Actions workflow
# Verify changelog is generated and committed

# 3. Check GitHub release
# Verify release notes include changelog

# 4. Clean up test tag
git tag -d v0.1.1-test
git push origin --delete v0.1.1-test
```

### Unit Tests

```python
# tests/unit/test_changelog.py
def test_cliff_config_exists():
    """Test that cliff.toml configuration exists."""
    assert Path(".cliff.toml").exists()

def test_cliff_config_valid():
    """Test that cliff.toml is valid TOML."""
    import tomli
    with open(".cliff.toml", "rb") as f:
        config = tomli.load(f)
    assert "changelog" in config
    assert "git" in config

def test_conventional_commits_enabled():
    """Test that conventional commits parsing is enabled."""
    import tomli
    with open(".cliff.toml", "rb") as f:
        config = tomli.load(f)
    assert config["git"]["conventional_commits"] is True
```

## Acceptance Criteria

- [ ] git-cliff installed and configured via `.cliff.toml`
- [ ] Configuration generates Keep a Changelog format
- [ ] Conventional commits correctly categorized:
  - `feat:` → Added
  - `fix:` → Fixed
  - `refactor:` → Changed
  - `perf:` → Performance
  - `docs:` → Documentation
  - CI commits filtered out (ci, chore, test, style)
- [ ] Makefile targets added:
  - `make changelog-preview`
  - `make changelog-update`
  - `make changelog-tag TAG=vX.Y.Z`
- [ ] CI/CD workflow generates and commits CHANGELOG.md on tag push
- [ ] GitHub releases include generated changelog
- [ ] Documentation updated:
  - CONTRIBUTING.md (conventional commits)
  - CLAUDE.md (changelog automation)
  - Makefile reference
- [ ] Tests pass (config validation, format checks)
- [ ] Existing CHANGELOG.md content preserved
- [ ] Manual verification: generated changelog matches Keep a Changelog format

## Related Files

- `CHANGELOG.md` - Changelog file to be auto-generated
- `.cliff.toml` - git-cliff configuration (to be created)
- `.github/workflows/release.yml` - Release workflow with changelog generation (to be created/updated)
- `Makefile` - Add changelog targets
- `CONTRIBUTING.md` - Document conventional commit requirement
- `CLAUDE.md` - Document changelog automation
- `docs/reference/makefile.md` - Document new Makefile targets
- `pyproject.toml` - Add git-cliff as dev dependency (optional)

## Dependencies

**External Tools:**
- **git-cliff** - Changelog generation tool
  - Install: `cargo install git-cliff` or `brew install git-cliff`
  - GitHub: https://github.com/orhun/git-cliff
  - Docs: https://git-cliff.org/

**GitHub Actions:**
- `orhun/git-cliff-action@v4` - Official git-cliff GitHub Action
- `softprops/action-gh-release@v2` - GitHub release creation

**Related Tasks:**
- Task #010 (refactoring/010-dynamic-versioning.md) - Dynamic versioning from git tags (completed)
  - CHANGELOG automation builds on tag-based versioning
  - Same git tags used for both version detection and changelog generation

**Project Requirements:**
- Conventional commits format (already in use)
- Git tags following `vX.Y.Z` pattern
- Keep a Changelog format (already adopted)

## Additional Notes

### Conventional Commit Enforcement

To ensure quality changelog generation, consider adding commit message validation:

**Pre-commit Hook** (`.pre-commit-config.yaml`):
```yaml
- repo: https://github.com/compilerla/conventional-pre-commit
  rev: v3.1.0
  hooks:
    - id: conventional-pre-commit
      stages: [commit-msg]
```

**Commitlint** (alternative):
```yaml
- repo: https://github.com/alessandrojcm/commitlint-pre-commit-hook
  rev: v9.13.0
  hooks:
    - id: commitlint
      stages: [commit-msg]
```

### Migration Strategy

**Phase 1**: Setup and Testing (this task)
- Install and configure git-cliff
- Test locally
- Add Makefile targets
- Validate output

**Phase 2**: CI Integration (follow-up)
- Add to GitHub Actions release workflow
- Test with release candidates
- Monitor and adjust configuration

**Phase 3**: Full Automation (future)
- Consider auto-generating release notes
- Consider version bump automation
- Consider changelog-based PR descriptions

### Keep a Changelog Categories

Standard Keep a Changelog categories mapped to conventional commits:

| Changelog Section | Conventional Type | Examples |
|-------------------|-------------------|----------|
| **Added** | `feat:` | New features, new endpoints, new commands |
| **Changed** | `refactor:`, `perf:` | Refactoring, performance improvements |
| **Deprecated** | `deprecate:` | Deprecation warnings, backward compat |
| **Removed** | `remove:` | Removed features, dropped support |
| **Fixed** | `fix:` | Bug fixes, error corrections |
| **Security** | `security:` | Security patches, vulnerability fixes |
| **Documentation** | `docs:` | Documentation updates (optional) |

### Performance Implications

git-cliff is very fast:
- Full changelog generation: <100ms
- Incremental updates: <50ms
- CI overhead: ~5-10 seconds (includes git-cliff-action setup)

### Breaking Changes

When implementing, ensure:
- Existing CHANGELOG.md content is preserved
- Manual entries (if any) are not overwritten
- First run generates full history correctly
- Subsequent runs append new releases only

### Trade-offs

**Advantages:**
- ✅ Eliminates manual changelog maintenance
- ✅ Ensures consistency and completeness
- ✅ Reduces release process time
- ✅ Professional, standard format
- ✅ Integrates with existing tooling (git tags, CI/CD)

**Disadvantages:**
- ⚠️ Requires conventional commit discipline
- ⚠️ Initial setup and configuration time
- ⚠️ Relies on commit message quality
- ⚠️ May need manual curation for major releases

**Mitigation:**
- Add pre-commit hooks for commit message validation
- Document conventional commit guidelines clearly
- Allow manual CHANGELOG.md edits before release
- Review generated changelog in PR process

## Implementation Notes

*To be filled during implementation:*
- Actual git-cliff configuration used
- CI/CD workflow integration details
- Challenges encountered (commit parsing, formatting, etc.)
- Configuration tweaks needed for project-specific needs
- Actual effort vs estimated
- Any deviations from proposed solution
