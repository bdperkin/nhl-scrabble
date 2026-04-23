# Comprehensive GitHub Workflows Enhancement

**GitHub Issue**: #298 - https://github.com/bdperkin/nhl-scrabble/issues/298

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

24-32 hours (main task coordination + sub-tasks)

## Description

Enhance the project's CI/CD infrastructure by implementing additional useful and logical GitHub workflows across all categories: Deployment, Security, Continuous Integration, Automation, and Pages. This comprehensive enhancement will improve code quality, security posture, release management, and developer experience through automated workflows.

## Current State

**Existing Workflows (4):**

1. **`.github/workflows/ci.yml`** - Comprehensive CI testing

   - Python 3.12-3.15 matrix testing
   - Tox environments (31 configurations)
   - Pre-commit hooks (58 hooks)
   - Codecov integration
   - Test results upload

1. **`.github/workflows/codeql.yml`** - Security scanning

   - Weekly CodeQL analysis
   - Python security patterns
   - PR security checks

1. **`.github/workflows/security.yml`** - Dependency auditing

   - pip-audit vulnerability scanning
   - Bandit security linting
   - Safety vulnerability database checks
   - PR security comments

1. **`.github/workflows/docs.yml`** - Documentation deployment

   - Sphinx documentation builds
   - GitHub Pages deployment
   - Documentation quality checks
   - Sitemap generation

**Additional Infrastructure:**

- ✅ `.github/dependabot.yml` - Automated dependency updates
- ✅ `.github/CODEOWNERS` - Code review assignments
- ✅ `.github/PULL_REQUEST_TEMPLATE.md` - PR templates
- ✅ Branch protection rules configured
- ❌ **No deployment/release automation**
- ❌ **No PR automation** (labels, size checks, welcomes)
- ❌ **No stale issue/PR management**
- ❌ **No performance regression testing**
- ❌ **No supply chain security** (SBOM, provenance)
- ❌ **No container workflows**

## Proposed Solution

### Workflow Organization

Implement 12 new workflows organized into 5 categories, each as a separate sub-task:

```
.github/workflows/
├── ci.yml                    # ✅ Existing - Comprehensive testing
├── codeql.yml                # ✅ Existing - Security scanning
├── security.yml              # ✅ Existing - Dependency auditing
├── docs.yml                  # ✅ Existing - Documentation
├── publish.yml               # 🆕 Sub-task 1: PyPI package publishing
├── release.yml               # 🆕 Sub-task 2: GitHub release automation
├── docker.yml                # 🆕 Sub-task 3: Container image builds
├── pr-labels.yml             # 🆕 Sub-task 4: Auto-label PRs
├── pr-size.yml               # 🆕 Sub-task 5: PR size checking
├── stale.yml                 # 🆕 Sub-task 6: Stale issue management
├── welcome.yml               # 🆕 Sub-task 7: First-time contributor welcome
├── benchmark.yml             # 🆕 Sub-task 8: Performance regression testing
├── sbom.yml                  # 🆕 Sub-task 9: Software Bill of Materials
├── provenance.yml            # 🆕 Sub-task 10: SLSA provenance
├── dependency-review.yml     # 🆕 Sub-task 11: Enhanced dependency checks
└── nightly.yml               # 🆕 Sub-task 12: Nightly comprehensive testing
```

### Sub-Task Breakdown

Each workflow will be implemented as a separate sub-task in the `new-features` category:

#### **Sub-task 1: PyPI Package Publishing Workflow** (4-6h)

- **File**: `new-features/032-pypi-publish-workflow.md`
- **Priority**: HIGH
- **Triggers**: Version tags (`v*`)
- **Actions**:
  - Build source distribution (sdist)
  - Build wheel distribution
  - Verify with twine check
  - Test installation on multiple platforms
  - Publish to TestPyPI
  - Publish to PyPI
  - Create GitHub Release
- **Benefits**: Automated releases, no manual steps
- **Related**: Already documented in task #018, needs implementation

#### **Sub-task 2: GitHub Release Automation** (2-3h)

- **File**: `new-features/033-github-release-workflow.md`
- **Priority**: MEDIUM
- **Triggers**: Version tags (`v*`)
- **Actions**:
  - Extract release notes from CHANGELOG.md
  - Create GitHub Release
  - Attach build artifacts
  - Generate release summary
- **Benefits**: Consistent release documentation

#### **Sub-task 3: Docker Container Workflow** (3-4h)

- **File**: `new-features/034-docker-build-publish-workflow.md`
- **Priority**: LOW
- **Triggers**: Push to main, version tags, PRs
- **Actions**:
  - Build multi-platform images (amd64, arm64)
  - Run security scans (Trivy)
  - Push to GitHub Container Registry (GHCR)
  - Tag with version and latest
- **Benefits**: Containerized deployments, easier testing

#### **Sub-task 4: PR Auto-Labeling** (1-2h)

- **File**: `new-features/035-pr-auto-label-workflow.md`
- **Priority**: LOW
- **Triggers**: PR opened/synchronized
- **Actions**:
  - Label based on changed files
  - Label based on PR title
  - Label by size (S/M/L/XL)
- **Benefits**: Better PR organization and filtering

#### **Sub-task 5: PR Size Checker** (1-2h)

- **File**: `new-features/036-pr-size-check-workflow.md`
- **Priority**: LOW
- **Triggers**: PR opened/synchronized
- **Actions**:
  - Calculate lines changed
  - Comment on large PRs
  - Suggest splitting if > 500 lines
- **Benefits**: Encourages smaller, reviewable PRs

#### **Sub-task 6: Stale Issue/PR Management** (1h)

- **File**: `new-features/037-stale-management-workflow.md`
- **Priority**: LOW
- **Triggers**: Schedule (daily)
- **Actions**:
  - Mark stale issues (60 days inactive)
  - Mark stale PRs (30 days inactive)
  - Close after 7 days if still stale
  - Skip labeled items
- **Benefits**: Keep issue tracker clean and relevant

#### **Sub-task 7: First-Time Contributor Welcome** (30min-1h)

- **File**: `new-features/038-welcome-contributor-workflow.md`
- **Priority**: LOW
- **Triggers**: PR/issue from first-time contributor
- **Actions**:
  - Post welcome message
  - Link to CONTRIBUTING.md
  - Thank contributor
- **Benefits**: Better contributor experience

#### **Sub-task 8: Performance Benchmark Testing** (3-4h)

- **File**: `new-features/039-benchmark-workflow.md`
- **Priority**: MEDIUM
- **Triggers**: Push to main, PRs
- **Actions**:
  - Run pytest-benchmark
  - Compare against main branch
  - Comment on PRs with results
  - Fail if > 10% regression
- **Benefits**: Catch performance regressions early

#### **Sub-task 9: SBOM Generation** (2-3h)

- **File**: `new-features/040-sbom-workflow.md`
- **Priority**: MEDIUM
- **Triggers**: Release, schedule (weekly)
- **Actions**:
  - Generate CycloneDX SBOM
  - Generate SPDX SBOM
  - Upload as release artifact
  - Archive for compliance
- **Benefits**: Supply chain transparency, compliance

#### **Sub-task 10: SLSA Provenance** (2-3h)

- **File**: `new-features/041-provenance-workflow.md`
- **Priority**: MEDIUM
- **Triggers**: Release builds
- **Actions**:
  - Generate SLSA provenance
  - Sign build artifacts
  - Verify build reproducibility
- **Benefits**: Build integrity verification

#### **Sub-task 11: Enhanced Dependency Review** (1-2h)

- **File**: `new-features/042-dependency-review-workflow.md`
- **Priority**: MEDIUM
- **Triggers**: PRs that change dependencies
- **Actions**:
  - Check for known vulnerabilities
  - Check license compatibility
  - Comment on PR with summary
  - Block incompatible licenses
- **Benefits**: Proactive dependency safety

#### **Sub-task 12: Nightly Comprehensive Testing** (2-3h)

- **File**: `new-features/043-nightly-testing-workflow.md`
- **Priority**: LOW
- **Triggers**: Schedule (nightly at 2 AM UTC)
- **Actions**:
  - Full test suite on all Python versions
  - Extended integration tests
  - Performance benchmarks
  - Coverage reports
  - Summary notification on failure
- **Benefits**: Catch environment-specific issues

### Implementation Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  GitHub Workflows                       │
└───────────────┬────────────────────────────────────────┘
                │
      ┌─────────┴─────────────────────┐
      │                               │
┌─────▼──────┐              ┌────────▼──────┐
│ On PR      │              │ On Push/Tag   │
├────────────┤              ├───────────────┤
│ • CI Tests │              │ • CI Tests    │
│ • Security │              │ • Security    │
│ • PR Labels│              │ • Docs Build  │
│ • PR Size  │              │ • Release     │
│ • Benchmark│              │ • Publish     │
│ • Dep Review│             │ • Docker      │
└────────────┘              │ • SBOM        │
                            │ • Provenance  │
                            └───────────────┘
      │
      └─────────┬──────────────────────┐
                │                      │
      ┌─────────▼────┐      ┌─────────▼────────┐
      │ Schedule     │      │ Manual Trigger   │
      ├──────────────┤      ├──────────────────┤
      │ • Nightly    │      │ • All workflows  │
      │ • CodeQL     │      │   (via dispatch) │
      │ • Security   │      └──────────────────┘
      │ • Stale      │
      │ • SBOM       │
      └──────────────┘
```

## Implementation Steps

### Phase 1: Planning and Setup (2-3h)

1. **Create Sub-Task Files** (1h)

   - Create 12 new task files in `new-features/` (032-043)
   - Follow task template structure
   - Include detailed implementation specs
   - Create corresponding GitHub issues

1. **Review Existing Workflows** (30min)

   - Audit current workflows for duplication
   - Identify integration points
   - Document dependencies

1. **Create Workflow Templates** (1h)

   - Set up reusable workflow templates
   - Create composite actions for common patterns
   - Document workflow standards

### Phase 2: High-Priority Workflows (8-12h)

4. **Implement Sub-task 1: PyPI Publishing** (4-6h)

   - Most critical for release automation
   - Follow task #018 specification
   - Test with pre-release version

1. **Implement Sub-task 8: Benchmarking** (3-4h)

   - Important for performance tracking
   - Integrate with existing pytest infrastructure

1. **Implement Sub-task 11: Dependency Review** (1-2h)

   - Security-focused
   - Complements existing security workflows

### Phase 3: Medium-Priority Workflows (7-10h)

7. **Implement Sub-task 2: Release Automation** (2-3h)

1. **Implement Sub-task 9: SBOM Generation** (2-3h)

1. **Implement Sub-task 10: SLSA Provenance** (2-3h)

### Phase 4: Low-Priority Automation (7-9h)

10. **Implement Sub-task 3: Docker Workflow** (3-4h)

01. **Implement Sub-task 4: PR Auto-Labeling** (1-2h)

01. **Implement Sub-task 5: PR Size Checker** (1-2h)

01. **Implement Sub-task 6: Stale Management** (1h)

01. **Implement Sub-task 7: Welcome Messages** (30min-1h)

01. **Implement Sub-task 12: Nightly Testing** (2-3h)

### Phase 5: Documentation and Testing (2-4h)

16. **Update Documentation** (1-2h)

    - Update CLAUDE.md with workflow descriptions
    - Create .github/workflows/README.md
    - Document workflow triggers and purposes
    - Add workflow badges to README.md

01. **Test All Workflows** (1-2h)

    - Create test branches/PRs
    - Verify triggers work correctly
    - Test failure scenarios
    - Verify notifications work

01. **Final Integration** (30min-1h)

    - Verify workflow interactions
    - Check for conflicts/duplication
    - Optimize workflow execution order
    - Monitor resource usage

## Testing Strategy

### Per-Workflow Testing

Each sub-task includes specific testing instructions:

```bash
# Test PR-triggered workflows
git checkout -b test/workflow-pr
# Make changes to trigger workflow
git push origin test/workflow-pr
gh pr create --title "Test: Workflow validation"

# Test tag-triggered workflows
git tag v0.0.1-test
git push origin v0.0.1-test

# Monitor workflow execution
gh run list --workflow=<workflow-name>
gh run watch

# Clean up test artifacts
git tag -d v0.0.1-test
git push origin :refs/tags/v0.0.1-test
gh pr close <pr-number> --delete-branch
```

### Integration Testing

```bash
# Test workflow combinations
# 1. Create PR (triggers: ci, pr-labels, pr-size, dependency-review)
gh pr create --title "feat: Test feature"

# 2. Add dependency (triggers: dependency-review)
# Edit pyproject.toml

# 3. Create release (triggers: publish, release, docker, sbom, provenance)
git tag v2.1.0
git push --tags

# 4. Verify all workflows pass
gh run list --limit 20
```

### Monitoring and Validation

```bash
# Check workflow status
gh workflow list

# View recent runs
gh run list --limit 50

# Check for failures
gh run list --status failure

# Monitor resource usage
# GitHub Actions usage limits:
# - Free: 2,000 minutes/month
# - Pro: 3,000 minutes/month
```

## Acceptance Criteria

### Main Task

- [ ] All 12 sub-task files created in `new-features/` directory
- [ ] All sub-tasks have corresponding GitHub issues
- [ ] Main tracking issue created linking all sub-tasks
- [ ] Workflow documentation created (`.github/workflows/README.md`)
- [ ] CLAUDE.md updated with workflow descriptions
- [ ] README.md updated with workflow badges
- [ ] All workflows tested and verified working
- [ ] No conflicts or duplication between workflows
- [ ] Resource usage within GitHub Actions limits
- [ ] All workflows have proper error handling
- [ ] All workflows have status checks configured

### Individual Sub-Tasks

Each sub-task must meet:

- [ ] Workflow file created in `.github/workflows/`
- [ ] Workflow triggers correctly configured
- [ ] Workflow permissions set appropriately
- [ ] Error handling implemented
- [ ] Testing completed successfully
- [ ] Documentation updated
- [ ] GitHub issue closed

### Documentation

- [ ] `.github/workflows/README.md` created with workflow index
- [ ] Each workflow has description and trigger documentation
- [ ] Troubleshooting section added
- [ ] Badge URLs documented
- [ ] Workflow dependencies documented

### Quality Gates

- [ ] All workflows pass yamllint validation
- [ ] All workflows pass actionlint validation
- [ ] No security issues in workflows
- [ ] No hardcoded secrets
- [ ] Proper use of GitHub-provided secrets
- [ ] Workflow concurrency configured appropriately

## Related Files

**New Files:**

- `.github/workflows/publish.yml` (sub-task 1)
- `.github/workflows/release.yml` (sub-task 2)
- `.github/workflows/docker.yml` (sub-task 3)
- `.github/workflows/pr-labels.yml` (sub-task 4)
- `.github/workflows/pr-size.yml` (sub-task 5)
- `.github/workflows/stale.yml` (sub-task 6)
- `.github/workflows/welcome.yml` (sub-task 7)
- `.github/workflows/benchmark.yml` (sub-task 8)
- `.github/workflows/sbom.yml` (sub-task 9)
- `.github/workflows/provenance.yml` (sub-task 10)
- `.github/workflows/dependency-review.yml` (sub-task 11)
- `.github/workflows/nightly.yml` (sub-task 12)
- `.github/workflows/README.md` (documentation)
- `tasks/new-features/032-pypi-publish-workflow.md`
- `tasks/new-features/033-github-release-workflow.md`
- `tasks/new-features/034-docker-build-publish-workflow.md`
- `tasks/new-features/035-pr-auto-label-workflow.md`
- `tasks/new-features/036-pr-size-check-workflow.md`
- `tasks/new-features/037-stale-management-workflow.md`
- `tasks/new-features/038-welcome-contributor-workflow.md`
- `tasks/new-features/039-benchmark-workflow.md`
- `tasks/new-features/040-sbom-workflow.md`
- `tasks/new-features/041-provenance-workflow.md`
- `tasks/new-features/042-dependency-review-workflow.md`
- `tasks/new-features/043-nightly-testing-workflow.md`

**Modified Files:**

- `README.md` - Add workflow badges
- `CLAUDE.md` - Document workflow infrastructure
- `tasks/README.md` - Update task index with sub-tasks
- `.github/CODEOWNERS` (optional) - Add workflow owners
- `pyproject.toml` (optional) - Add workflow-related dependencies

**Configuration Files:**

- `.github/labeler.yml` - Label configuration for auto-labeler
- `.github/release.yml` - Release notes configuration

## Dependencies

**Task Dependencies:**

- **Complements**: `new-features/018-automated-python-package-building-publishing.md`

  - Sub-task 1 implements this specification

- **Depends on**: `refactoring/010-dynamic-versioning-from-git-tags.md` (#222)

  - Required for automated versioning in publishing workflow

**Tool Dependencies:**

- GitHub Actions (already available)
- GitHub CLI (`gh`) for testing
- `actionlint` for workflow validation (install for testing)
- `yamllint` for YAML validation (already in pre-commit)
- Docker (for container workflow testing)
- `pytest-benchmark` (for benchmark workflow)
- `cyclonedx-bom` (for SBOM generation)

**No Breaking Changes:**

- All workflows are additive
- Existing workflows remain unchanged
- Can be implemented incrementally
- Each workflow is independent

## Additional Notes

### Workflow Categories

**Deployment (3 workflows):**

- PyPI publishing (sub-task 1)
- Release automation (sub-task 2)
- Docker builds (sub-task 3)

**Security (4 workflows):**

- SBOM generation (sub-task 9)
- SLSA provenance (sub-task 10)
- Dependency review (sub-task 11)
- Already have: CodeQL, security audit

**Continuous Integration (2 workflows):**

- Benchmark testing (sub-task 8)
- Nightly testing (sub-task 12)
- Already have: CI, tox, pre-commit

**Automation (4 workflows):**

- PR auto-labeling (sub-task 4)
- PR size checking (sub-task 5)
- Stale management (sub-task 6)
- Welcome messages (sub-task 7)

**Pages (already implemented):**

- Documentation deployment (existing docs.yml)
- Sitemap generation (existing docs.yml)

### Resource Management

**GitHub Actions Limits:**

- Free tier: 2,000 minutes/month
- Current usage: ~500-800 minutes/month
- Estimated with new workflows: ~1,200-1,500 minutes/month
- Still within free tier limits

**Optimization Strategies:**

- Use workflow concurrency groups
- Skip workflows on documentation-only changes
- Use path filters to avoid unnecessary runs
- Cache aggressively
- Parallelize where possible

### Security Considerations

**Workflow Security:**

- ✅ Never commit secrets to workflows
- ✅ Use GitHub-provided secrets
- ✅ Minimal permissions (principle of least privilege)
- ✅ Pin action versions for security
- ✅ Regular Dependabot updates for actions
- ✅ Review workflow changes carefully

**Best Practices:**

- Use `permissions:` block in every workflow
- Avoid `workflow_dispatch` with user inputs unless validated
- Use environment protection rules for sensitive workflows
- Enable branch protection for workflow files
- Require code review for `.github/workflows/` changes

### Performance Considerations

**Workflow Execution:**

- Parallel execution where possible
- Smart triggers (path filters, branch filters)
- Caching for faster runs
- Artifact reuse between jobs
- Matrix strategies for comprehensive testing

**Monitoring:**

```yaml
# Add to workflows for monitoring
  - name: Workflow timing
    run: echo "::notice::Workflow completed in ${{ github.run_duration }}"
```

### Maintenance Strategy

**Regular Reviews:**

- Quarterly workflow audit
- Update action versions via Dependabot
- Review and optimize slow workflows
- Check for deprecated actions
- Monitor GitHub Actions updates

**Documentation:**

- Keep `.github/workflows/README.md` updated
- Document workflow purposes
- Link to relevant task files
- Maintain troubleshooting guide

### Future Enhancements

After initial implementation, consider:

- Mobile app deployment workflows (if web interface expanded)
- Automated changelog generation
- Release announcement automation (Twitter, Discord, etc.)
- Conda-forge publishing workflow
- Homebrew formula updates
- Automated documentation translations
- Visual regression testing workflows
- Accessibility testing workflows

### Breaking Changes

**None** - All workflows are additive and optional:

- Existing CI/CD processes unchanged
- Manual processes still available
- Workflows can be disabled individually
- No impact on existing development workflow
- Can be adopted incrementally

### Migration Notes

**Implementation Order:**

1. **Phase 1**: High-priority workflows (publishing, benchmarks)
1. **Phase 2**: Security workflows (SBOM, provenance, dep review)
1. **Phase 3**: Automation workflows (labels, size, stale, welcome)
1. **Phase 4**: Nice-to-have workflows (Docker, nightly)

**Rollback Strategy:**

- Each workflow is in separate file
- Can disable by removing/renaming file
- Can disable triggers while keeping file
- No dependencies between workflows
- Easy to roll back individual workflows

### Expected Benefits

**Developer Experience:**

- ✅ Faster PR reviews (auto-labels, size checks)
- ✅ Better PR quality (size warnings, benchmarks)
- ✅ Welcoming community (welcome messages)
- ✅ Cleaner issue tracker (stale management)

**Release Management:**

- ✅ Automated releases (publishing workflow)
- ✅ Consistent release notes (release workflow)
- ✅ Container deployments (Docker workflow)
- ✅ Multiple distribution formats

**Security:**

- ✅ Supply chain transparency (SBOM)
- ✅ Build verification (provenance)
- ✅ Proactive dependency checks (review workflow)
- ✅ Comprehensive security scanning

**Quality:**

- ✅ Performance tracking (benchmarks)
- ✅ Comprehensive testing (nightly)
- ✅ Early regression detection
- ✅ Better coverage

### Success Metrics

**Quantitative:**

- Reduce release time from 30min to 5min
- Increase PR labeling accuracy to 95%+
- Reduce stale issues by 50%
- Catch performance regressions before merge
- 100% supply chain transparency

**Qualitative:**

- Better contributor experience
- Cleaner issue tracker
- More consistent releases
- Improved security posture
- Better documentation

## Implementation Notes

*To be filled during implementation:*

### Phase 1 Completion

- Date started:
- Date completed:
- Actual effort:
- Challenges encountered:
- Deviations from plan:

### Phase 2-4 Completion

- Sub-tasks completed:
- Workflows implemented:
- Workflows skipped/deferred:
- Reasons for changes:

### Final Notes

- Overall effort vs estimated:
- Unexpected challenges:
- Lessons learned:
- Recommendations for future workflow additions:
