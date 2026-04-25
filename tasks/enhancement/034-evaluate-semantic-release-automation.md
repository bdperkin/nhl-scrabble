# Evaluate semantic-release for Fully Automated Releases

**GitHub Issue**: [#383](https://github.com/bdperkin/nhl-scrabble/issues/383)

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

6-10 hours (comprehensive evaluation + POC + recommendation)

## Description

Research and evaluate **semantic-release** as a comprehensive alternative to the current piecemeal release automation approach. Semantic-release is an industry-standard tool that automates the entire release workflow based on conventional commits.

This is a **research and evaluation task**, not an immediate implementation. The goal is to:
1. Understand semantic-release capabilities
2. Compare with current workflow (tasks #010, #030, #031, #032)
3. Evaluate trade-offs (automation vs control, complexity vs simplicity)
4. Make informed recommendation (adopt, reject, or partial adoption)
5. Document findings for future reference

## Current State

**Piecemeal Release Automation (4 separate tasks):**

1. **Task #010** (completed): Dynamic versioning from git tags (hatch-vcs)
   - Version determined from git tags
   - Build-time version injection
   - No manual version bumps

2. **Task #030** (active): CHANGELOG automation (git-cliff)
   - Generate CHANGELOG from conventional commits
   - Keep a Changelog format
   - Requires manual trigger

3. **Task #031** (active): Version validation pre-commit hooks
   - Validates version consistency
   - Prevents configuration errors
   - Custom Python script

4. **Task #032** (active): GitHub release automation
   - Create releases from tag annotations
   - Extract release notes from git tags
   - GitHub Actions workflow

**Current Workflow:**
```bash
# 1. Developer creates tag with annotation
git tag -a v2.1.0 -m "Release notes..."
git push origin v2.1.0

# 2. GitHub Actions creates release (task #032)
# 3. git-cliff generates CHANGELOG (task #030 - manual or workflow)
# 4. Version detected from tag (task #010 - hatch-vcs)
# 5. Pre-commit validates consistency (task #031)
```

**Advantages:**
- ✅ Modular approach (can replace parts independently)
- ✅ Python-native tools where possible
- ✅ Full control over each step
- ✅ Already partially implemented
- ✅ No JavaScript dependency (except git-cliff is Rust)

**Disadvantages:**
- ❌ Multiple tools to maintain
- ❌ Manual coordination required
- ❌ Potential for inconsistencies
- ❌ More complex CI/CD configuration
- ❌ Developer must remember workflow steps

## semantic-release Overview

**What is semantic-release?**

semantic-release is a fully automated version management and package publishing tool that:
- Analyzes commits (conventional commits format)
- Determines next version (semantic versioning)
- Generates release notes and CHANGELOG
- Creates git tags
- Creates GitHub releases
- Publishes to npm, PyPI, etc.
- All triggered automatically on merge to main

**Example Workflow:**
```bash
# 1. Developer commits with conventional format
git commit -m "feat: add new feature X"
git commit -m "fix: correct bug Y"
git push origin feature-branch

# 2. PR merged to main

# 3. semantic-release (in CI) automatically:
#    - Analyzes commits (feat = minor, fix = patch)
#    - Determines version (v2.0.0 → v2.1.0)
#    - Generates CHANGELOG entry
#    - Creates git tag v2.1.0
#    - Creates GitHub release with notes
#    - Publishes to PyPI (optional)
#    - All without manual intervention!
```

**Key Features:**
- 🤖 **Fully automated** - No manual tagging or versioning
- 📊 **Commit analysis** - Determines version from commit messages
- 📝 **CHANGELOG generation** - Automatic release notes
- 🏷️ **Git tagging** - Creates tags automatically
- 🚀 **Publishing** - Can publish to npm, PyPI, etc.
- 🔌 **Plugin ecosystem** - Extensible with plugins
- 🛡️ **Dry-run mode** - Test releases without publishing

**Supported Platforms:**
- npm (native)
- PyPI (via @semantic-release/exec or python-semantic-release)
- GitHub Releases
- GitLab Releases
- Docker registries
- Custom platforms via plugins

## Evaluation Criteria

### 1. Functionality Comparison

| Feature | Current Approach | semantic-release | Winner |
|---------|------------------|------------------|--------|
| **Version Detection** | hatch-vcs (build-time) | Commit analysis (CI-time) | Tie |
| **CHANGELOG** | git-cliff (manual/workflow) | Automatic | semantic-release |
| **Git Tagging** | Manual | Automatic | semantic-release |
| **GitHub Releases** | GitHub Actions (task #032) | Built-in | Tie |
| **PyPI Publishing** | Manual | Automatic (plugin) | semantic-release |
| **Validation** | Pre-commit hooks (task #031) | Commit message linting | Current |
| **Control** | Full control each step | Opinionated workflow | Current |
| **Setup Complexity** | Multiple tools | Single tool | semantic-release |

### 2. Python Ecosystem Fit

**semantic-release Python Options:**

**Option A: python-semantic-release**
```yaml
# .github/workflows/release.yml
- uses: python-semantic-release/python-semantic-release@v8
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
```

- Python-native implementation
- Good PyPI integration
- Active development
- Poetry/setuptools/hatchling support

**Option B: semantic-release with exec plugin**
```yaml
# .releaserc.js
module.exports = {
  plugins: [
    '@semantic-release/commit-analyzer',
    '@semantic-release/release-notes-generator',
    ['@semantic-release/exec', {
      publishCmd: 'python -m build && twine upload dist/*'
    }],
    '@semantic-release/github'
  ]
}
```

- Node.js semantic-release (original)
- More plugins available
- Requires Node.js in CI

### 3. Integration with Current Workflow

**What would change:**

| Component | Current | With semantic-release | Impact |
|-----------|---------|----------------------|--------|
| **pyproject.toml** | `dynamic = ["version"]` | `version = "0.0.0"` (placeholder) | Moderate |
| **hatch-vcs** | Active | Replace with semantic-release | High |
| **git-cliff** | Planned (task #030) | Replace with semantic-release | Low (not yet implemented) |
| **Pre-commit hooks** | Keep (validation still useful) | Keep | None |
| **GitHub Actions** | Release workflow (task #032) | Replace with semantic-release | Moderate |
| **Developer workflow** | Manual tagging | Automatic on merge | **Significant** |

### 4. Trade-offs Analysis

**Advantages of semantic-release:**

✅ **Full automation**
- Zero manual intervention
- No forgetting steps
- Consistent process

✅ **Single tool**
- One configuration file
- Unified workflow
- Less maintenance

✅ **Industry standard**
- Well-tested
- Large community
- Good documentation

✅ **Commit-driven**
- Version from commits, not tags
- Forces good commit messages
- Self-documenting

✅ **PyPI publishing**
- Can auto-publish to PyPI
- Integrated with release process

**Disadvantages of semantic-release:**

❌ **Loss of control**
- Can't manually decide version
- Opinionated workflow
- Less flexibility

❌ **Dependency**
- Node.js in CI (if using original)
- Or Python version lock (if using python-semantic-release)
- External dependency

❌ **Learning curve**
- New tool to learn
- Configuration complexity
- Plugin ecosystem

❌ **Migration effort**
- Replace hatch-vcs
- Reconfigure CI/CD
- Update documentation
- Team training

❌ **Commit discipline**
- Requires strict conventional commits
- Mistakes can cause wrong versions
- No easy way to override

❌ **Incompatible with current approach**
- Can't use hatch-vcs + semantic-release
- All-or-nothing decision
- Would abandon task #010 work

### 5. Python-Specific Considerations

**python-semantic-release Compatibility:**

```toml
# pyproject.toml
[tool.semantic_release]
version_variable = "src/nhl_scrabble/__init__.py:__version__"
branch = "main"
upload_to_repository = true
upload_to_release = true
build_command = "python -m build"
```

**Concerns:**
- Must abandon hatch-vcs dynamic versioning
- Version would be written to `__init__.py` (not ideal)
- Less "Pythonic" than hatch-vcs
- Two sources of truth (git tag and file)

## Proposed Evaluation Plan

### Phase 1: Research (2-3 hours)

1. **Read Documentation**
   - python-semantic-release docs
   - semantic-release (Node) docs
   - Compare plugin ecosystems

2. **Review Existing Implementations**
   - Find Python projects using semantic-release
   - Study their configurations
   - Learn from their issues/PRs

3. **Analyze Compatibility**
   - Check hatch/hatchling compatibility
   - Review PyPI publishing integration
   - Understand CI/CD requirements

### Phase 2: Proof of Concept (2-3 hours)

1. **Test Branch Setup**
   ```bash
   git checkout -b experiment/semantic-release
   ```

2. **Configure python-semantic-release**
   - Install: `pip install python-semantic-release`
   - Configure in `pyproject.toml`
   - Test locally: `semantic-release version --dry-run`

3. **Test Version Detection**
   - Create test commits
   - Run semantic-release
   - Verify version bumps

4. **Test CHANGELOG Generation**
   - Review generated CHANGELOG
   - Compare to git-cliff output
   - Evaluate quality

5. **Test GitHub Release**
   - Dry-run GitHub release creation
   - Review release notes format
   - Compare to current approach

### Phase 3: Comparison (1-2 hours)

1. **Feature Comparison**
   - Create comparison table
   - List pros/cons
   - Identify gaps

2. **Effort Estimation**
   - Migration effort (current → semantic-release)
   - Maintenance effort (current vs semantic-release)
   - Learning curve

3. **Risk Assessment**
   - Breaking changes
   - Rollback difficulty
   - Vendor lock-in

### Phase 4: Recommendation (1-2 hours)

1. **Decision Matrix**
   - Weight criteria
   - Score each approach
   - Calculate recommendation

2. **Documentation**
   - Write findings report
   - Include examples
   - Provide recommendations

3. **Presentation**
   - Summarize for stakeholders
   - Include concrete examples
   - Propose next steps

## Testing Strategy

### POC Testing

```bash
# 1. Install python-semantic-release
pip install python-semantic-release

# 2. Configure
cat > pyproject.toml << 'EOF'
[tool.semantic_release]
version_variable = "src/nhl_scrabble/__init__.py:__version__"
branch = "main"
build_command = "python -m build"
EOF

# 3. Create test commits
git commit -m "feat: test feature for semantic-release POC"
git commit -m "fix: test bug fix for semantic-release POC"

# 4. Dry-run
semantic-release version --dry-run --verbose

# 5. Check what would happen
# - New version number
# - CHANGELOG entries
# - Git tag
# - GitHub release

# 6. Clean up
git checkout main
git branch -D experiment/semantic-release
```

### Comparison Testing

```bash
# Test current approach
git tag -a v2.1.0-test -m "Test release"
# Run task #032 workflow
# Generate CHANGELOG with git-cliff (task #030)

# vs

# Test semantic-release
semantic-release publish --dry-run
# Compare outputs
```

## Acceptance Criteria

- [ ] python-semantic-release documentation reviewed
- [ ] POC created on test branch
- [ ] Version detection tested and compared
- [ ] CHANGELOG generation tested and compared
- [ ] GitHub release creation tested and compared
- [ ] Compatibility analysis completed
- [ ] Trade-offs documented in comparison table
- [ ] Migration effort estimated
- [ ] Recommendation documented with rationale
- [ ] Findings report created
- [ ] Decision recorded (adopt/reject/defer)
- [ ] If adopt: Implementation task created
- [ ] If reject: Rationale documented for future reference

## Related Files

- `pyproject.toml` - Would require semantic-release configuration
- `src/nhl_scrabble/__init__.py` - Version variable location
- `.github/workflows/release.yml` - Release workflow (would be replaced)
- `CHANGELOG.md` - Generated by semantic-release (vs git-cliff)
- `.releaserc.json` or `pyproject.toml` - semantic-release config (new file)

## Dependencies

**Related Tasks:**
- **Task #010** (refactoring/010-dynamic-versioning.md) - Dynamic versioning (completed)
  - Would be **replaced** by semantic-release
  - Incompatible approaches
- **Task #030** (enhancement/030-automate-changelog-generation.md) - CHANGELOG automation (active)
  - Would be **replaced** by semantic-release
  - git-cliff vs semantic-release
- **Task #031** (enhancement/031-add-version-validation-pre-commit-hook.md) - Version validation (active)
  - Could **coexist** with semantic-release
  - Complementary validation
- **Task #032** (enhancement/032-github-release-notes-from-tag-annotations.md) - GitHub releases (active)
  - Would be **replaced** by semantic-release
  - Built-in feature

**External Tools:**
- **python-semantic-release** - Python implementation
  - https://github.com/python-semantic-release/python-semantic-release
  - https://python-semantic-release.readthedocs.io/
- **semantic-release** - Node.js original
  - https://github.com/semantic-release/semantic-release
  - https://semantic-release.gitbook.io/

**Decision Impact:**
- **If Adopt**: Significant changes to release workflow, abandon current tasks
- **If Reject**: Continue with current piecemeal approach (tasks #030, #031, #032)
- **If Defer**: Keep current approach, revisit after gaining more experience

## Additional Notes

### Decision Factors

**Favor semantic-release if:**
- ✅ Team wants full automation
- ✅ PyPI publishing is planned
- ✅ Willing to change current workflow
- ✅ Comfortable with opinionated tools
- ✅ Want industry-standard solution

**Favor current approach if:**
- ✅ Want flexibility and control
- ✅ Prefer modular tools
- ✅ Python-native tools preferred
- ✅ Already invested in hatch-vcs
- ✅ Like current manual tag workflow

### Migration Considerations

**If adopting semantic-release:**

**Breaking Changes:**
1. Replace hatch-vcs with semantic-release
2. Change version source (tag → file)
3. Update CI/CD workflows
4. Retrain team on new workflow

**Migration Steps:**
1. Disable hatch-vcs
2. Install python-semantic-release
3. Configure in pyproject.toml
4. Update GitHub Actions
5. Test on separate repository
6. Migrate production repository
7. Update documentation
8. Train team

**Rollback Plan:**
- Keep hatch-vcs configuration commented
- Document rollback procedure
- Test rollback before migrating

### Alternative: Hybrid Approach

**Could we use both?**

**Possible (but complex):**
- Keep hatch-vcs for version detection (task #010)
- Use semantic-release for CHANGELOG + GitHub releases
- Configure semantic-release to not manage version

**Configuration:**
```toml
[tool.semantic_release]
version_source = "tag"  # Use git tags, don't write to file
version_variable = null  # Don't update any file
build_command = "python -m build"
```

**Trade-offs:**
- 🤔 More complex (two tools)
- 🤔 Defeats purpose of semantic-release (simplification)
- 🤔 May confuse team
- ✅ Keeps hatch-vcs benefits
- ✅ Adds CHANGELOG automation

### Community Adoption

**Projects using python-semantic-release:**
- Many Python projects
- Check GitHub: `filename:pyproject.toml python-semantic-release`

**Projects using hatch-vcs:**
- Many Hatch-based projects
- Common in modern Python packaging

**Industry trend:**
- semantic-release popular in Node.js ecosystem
- Python ecosystem more fragmented (many tools)
- No clear winner in Python

### Performance Impact

**semantic-release CI Overhead:**
- Commit analysis: ~5-10s
- CHANGELOG generation: ~5-10s
- Git operations: ~5-10s
- PyPI upload: ~30-60s
- **Total**: ~1-2 minutes

**Current Approach Overhead:**
- Manual tagging: developer time
- git-cliff: ~5-10s (when implemented)
- GitHub release: ~10-20s
- **Total**: ~30s (plus developer time)

### Documentation Impact

**Would need to update:**
- CONTRIBUTING.md (new release process)
- CLAUDE.md (remove hatch-vcs, add semantic-release)
- README.md (possibly update badges)
- All task files (#010, #030, #031, #032) - mark as superseded

### Recommendation Timeline

**Immediate (after evaluation):**
- Document findings
- Make recommendation
- Get team feedback

**If Adopt:**
- **Short-term** (Q2 2026): POC on test repository
- **Medium-term** (Q3 2026): Migrate if POC successful
- **Long-term** (Q4 2026): Full team adoption

**If Reject:**
- **Immediate**: Document rationale
- **Short-term**: Continue with tasks #030, #031, #032
- **Long-term**: Revisit in 1 year

## Implementation Notes

*To be filled during evaluation:*
- POC results and observations
- Actual time spent on evaluation
- Tools/versions tested
- Comparison table completed
- Recommendation made (adopt/reject/defer)
- Rationale documented
- Next steps identified
- Team feedback incorporated
- Decision recorded
