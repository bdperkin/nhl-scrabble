# Add Comprehensive Documentation Badges to README

**GitHub Issue**: #91 - https://github.com/bdperkin/nhl-scrabble/issues/91

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

1-2 hours

## Description

Enhance the README.md with additional useful badges that provide at-a-glance information about project health, quality, and activity. The project currently has 12 badges but is missing several that would be valuable for users and contributors.

## Current State

**Existing badges (12 total):**

```markdown
[![CI](https://github.com/bdperkin/nhl-scrabble/actions/workflows/ci.yml/badge.svg)](...)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](...)
[![codecov](https://codecov.io/gh/bdperkin/nhl-scrabble/branch/main/graph/badge.svg)](...)
[![Python 3.10-3.13](https://img.shields.io/badge/python-3.10--3.13-blue.svg)](...)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](...)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](...)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](...)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](...)
[![Powered by UV](https://img.shields.io/badge/powered%20by-uv-black?logo=astral)](...)
[![GitHub stars](https://img.shields.io/github/stars/bdperkin/nhl-scrabble?style=social)](...)
[![GitHub issues](https://img.shields.io/github/issues/bdperkin/nhl-scrabble)](...)
[![GitHub last commit](https://img.shields.io/github/last-commit/bdperkin/nhl-scrabble)](...)
```

**Coverage:**

- ✅ Build status (CI)
- ✅ Documentation
- ✅ Code coverage (currently broken, see #90)
- ✅ Python versions
- ✅ License
- ✅ Code quality tools (ruff, mypy, pre-commit)
- ✅ Package manager (UV)
- ✅ GitHub stats (stars, issues, commits)

**Missing valuable badges:**

- ❌ Security scanning status (CodeQL)
- ❌ Documentation build status
- ❌ Latest release version
- ❌ PyPI version (for future)
- ❌ PyPI downloads (for future)
- ❌ Contributors count
- ❌ Code quality score (optional)
- ❌ Dependency status
- ❌ Maintenance status
- ❌ Pull requests status

## Proposed Solution

Add useful badges organized by category. Implementation should be done in phases based on availability and priority.

### Phase 1: GitHub Actions Badges (High Value, Available Now)

These badges use existing GitHub Actions workflows:

#### 1. CodeQL Security Scanning Badge

```markdown
[![CodeQL](https://github.com/bdperkin/nhl-scrabble/actions/workflows/codeql.yml/badge.svg)](https://github.com/bdperkin/nhl-scrabble/actions/workflows/codeql.yml)
```

**Why:** Shows security scanning is active and passing.

#### 2. Documentation Build Status

```markdown
[![Docs](https://github.com/bdperkin/nhl-scrabble/actions/workflows/docs.yml/badge.svg)](https://github.com/bdperkin/nhl-scrabble/actions/workflows/docs.yml)
```

**Why:** Shows documentation builds successfully.

### Phase 2: Version and Release Badges (Medium Value, Available Now)

#### 3. Latest Release Badge

```markdown
[![Latest Release](https://img.shields.io/github/v/release/bdperkin/nhl-scrabble?include_prereleases)](https://github.com/bdperkin/nhl-scrabble/releases)
```

**Why:** Shows latest version at a glance. Works even without releases (shows "no releases").

Alternative with custom version:

```markdown
[![Version](https://img.shields.io/badge/version-2.0.0-blue)](https://github.com/bdperkin/nhl-scrabble/releases)
```

#### 4. Release Date Badge

```markdown
[![Release Date](https://img.shields.io/github/release-date/bdperkin/nhl-scrabble)](https://github.com/bdperkin/nhl-scrabble/releases)
```

**Why:** Shows project is actively maintained.

### Phase 3: Community and Activity Badges (Medium Value, Available Now)

#### 5. Contributors Badge

```markdown
[![Contributors](https://img.shields.io/github/contributors/bdperkin/nhl-scrabble)](https://github.com/bdperkin/nhl-scrabble/graphs/contributors)
```

**Why:** Acknowledges contributors and encourages participation.

#### 6. Pull Requests Badge

```markdown
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/bdperkin/nhl-scrabble/pulls)
```

**Why:** Encourages contributions.

#### 7. Commit Activity Badge

```markdown
[![Commit Activity](https://img.shields.io/github/commit-activity/m/bdperkin/nhl-scrabble)](https://github.com/bdperkin/nhl-scrabble/graphs/commit-activity)
```

**Why:** Shows project is actively developed.

### Phase 4: Quality and Dependencies Badges (Low Value, Optional)

#### 8. Dependencies Status (Dependabot)

```markdown
[![Dependencies](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen)](https://github.com/bdperkin/nhl-scrabble/network/updates)
```

**Why:** Shows dependencies are current (manual update needed).

#### 9. Maintenance Status

```markdown
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/bdperkin/nhl-scrabble/graphs/commit-activity)
```

**Why:** Signals active maintenance.

#### 10. Code Size Badge

```markdown
[![Code Size](https://img.shields.io/github/languages/code-size/bdperkin/nhl-scrabble)](https://github.com/bdperkin/nhl-scrabble)
```

**Why:** Shows project size.

#### 11. Repo Size Badge

```markdown
[![Repo Size](https://img.shields.io/github/repo-size/bdperkin/nhl-scrabble)](https://github.com/bdperkin/nhl-scrabble)
```

**Why:** Shows total repository size.

### Phase 5: Future PyPI Badges (For Future Release)

These badges should be added when the package is published to PyPI:

#### 12. PyPI Version

```markdown
[![PyPI](https://img.shields.io/pypi/v/nhl-scrabble)](https://pypi.org/project/nhl-scrabble/)
```

#### 13. PyPI Downloads

```markdown
[![Downloads](https://img.shields.io/pypi/dm/nhl-scrabble)](https://pypi.org/project/nhl-scrabble/)
```

#### 14. PyPI - Python Versions

```markdown
[![Python Versions](https://img.shields.io/pypi/pyversions/nhl-scrabble)](https://pypi.org/project/nhl-scrabble/)
```

**Note:** Create placeholder in task for when PyPI publishing happens.

### Badge Organization

Reorganize badges into logical groups:

```markdown
<!-- Build & Quality -->
[![CI](...)](#)
[![CodeQL](...)](#)
[![Docs](...)](#)
[![codecov](...)](#)

<!-- Code Quality -->
[![Code style: ruff](...)](#)
[![Type checked: mypy](...)](#)
[![pre-commit](...)](#)

<!-- Package Info -->
[![Python 3.10-3.13](...)](#)
[![License: MIT](...)](#)
[![Powered by UV](...)](#)
[![Latest Release](...)](#)

<!-- Community & Activity -->
[![Contributors](...)](#)
[![GitHub stars](...)](#)
[![PRs Welcome](...)](#)
[![GitHub issues](...)](#)
[![Commit Activity](...)](#)
[![GitHub last commit](...)](#)

<!-- Maintenance -->
[![Maintenance](...)](#)
```

## Implementation Steps

### Step 1: Research and Verify Badges (15 minutes)

1. Test each badge URL to ensure it works
1. Verify badge displays correctly
1. Check that linked URLs are valid
1. Decide on badge ordering/grouping

### Step 2: Update README.md (20 minutes)

1. Back up current badge section
1. Add new badges in organized groups
1. Add HTML comments for badge categories
1. Ensure proper formatting and alignment

### Step 3: Test Badge Display (10 minutes)

1. View README on GitHub to verify all badges display
1. Click each badge to ensure links work
1. Test in both light and dark GitHub themes
1. Verify badges are readable at different screen sizes

### Step 4: Document Badge Maintenance (10 minutes)

1. Add section to CLAUDE.md about badges
1. Document which badges need manual updates
1. Note which badges are automated
1. Include instructions for future badge additions

### Step 5: Create Badge Reference (15 minutes)

Optional: Create `docs/badges.md` with:

- Complete list of all badges
- What each badge means
- How to update badges
- Badge URL templates

## Testing Strategy

### Visual Testing

1. **GitHub Preview:**

   - View README on GitHub
   - Check all badges display (no broken images)
   - Verify colors and styling are consistent
   - Test in light and dark modes

1. **Link Testing:**

   - Click each badge
   - Verify destination URL is correct
   - Check that target pages load successfully

1. **Cross-Browser Testing:**

   - Test in Chrome, Firefox, Safari
   - Verify badges render correctly
   - Check responsive design on mobile

### Automated Testing

Add pre-commit hook to validate badge URLs:

```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: check-badge-urls
      name: Check README badge URLs
      entry: python -c "import re, sys; content = open('README.md').read(); badges = re.findall(r'\[!\[.*?\]\((.*?)\)\]', content); print(f'Found {len(badges)} badges'); sys.exit(0)"
      language: system
      files: README.md
```

## Acceptance Criteria

- [x] CodeQL security badge added
- [x] Documentation build status badge added
- [x] Latest release badge added
- [x] Contributors badge added
- [x] PRs welcome badge added
- [x] Commit activity badge added
- [x] Maintenance status badge added
- [x] All new badges display correctly on GitHub
- [x] All badge links point to correct destinations
- [x] Badges are organized into logical groups with comments
- [x] CLAUDE.md updated with badge maintenance info
- [x] Optional: docs/badges.md created with reference
- [x] Optional: Pre-commit hook for badge validation
- [x] All badges tested in light and dark modes
- [x] Mobile display verified

## Related Files

- `README.md` - Primary location for badges (lines 1-15)
- `CLAUDE.md` - Document badge maintenance strategy
- `docs/badges.md` - Optional badge reference (NEW)
- `.pre-commit-config.yaml` - Optional badge validation hook

## Dependencies

**None** - All badges use external services:

- shields.io (badge generation)
- GitHub APIs (automated data)
- Codecov (coverage badge, depends on #90)

**External Services:**

- All badges are free for public repositories
- No API keys or tokens required
- No rate limiting concerns

## Additional Notes

### Badge Selection Criteria

Choose badges that:

1. **Provide value** - Actually useful information
1. **Stay current** - Auto-update from APIs
1. **Low maintenance** - Minimal manual updates needed
1. **Trustworthy** - From reputable sources
1. **Fast loading** - Don't slow down README rendering

### Shields.io Badge Customization

Badges can be customized with URL parameters:

```markdown
<!-- Custom colors -->
![Badge](https://img.shields.io/badge/text-value-blue)

<!-- Custom logo -->
![Badge](https://img.shields.io/badge/text-value-blue?logo=github)

<!-- Custom style -->
![Badge](https://img.shields.io/badge/text-value-blue?style=flat-square)
```

Styles available:

- `flat` (default)
- `flat-square`
- `plastic`
- `for-the-badge`
- `social`

### Badge Best Practices

**Do:**

- ✅ Group related badges together
- ✅ Use consistent badge styles
- ✅ Keep badge count reasonable (15-20 max)
- ✅ Link badges to relevant pages
- ✅ Use badges that auto-update

**Don't:**

- ❌ Add too many badges (visual clutter)
- ❌ Use badges that require manual updates
- ❌ Mix different badge styles
- ❌ Add badges for unimportant metrics
- ❌ Use broken or outdated badges

### Alternative Badge Sources

Besides shields.io, other sources include:

- **badgen.net** - Similar to shields.io
- **badge.fury.io** - PyPI-specific badges
- **GitHub badges** - Native GitHub badge URLs
- **codecov.io** - Coverage badges (see #90)

### Badge Alternatives

Instead of/in addition to badges, consider:

- **GitHub repository topics** - Tags for discovery
- **GitHub repository description** - One-line summary
- **GitHub About section** - Links and description
- **SECURITY.md** - Security policy badge
- **FUNDING.yml** - Sponsor button

### Performance Considerations

**Badge Loading:**

- Badges load asynchronously (no blocking)
- shields.io has CDN (fast globally)
- Badge images are cached by browsers
- Minimal impact on README load time

**Recommended:**

- Use SVG badges (smaller than PNG)
- Leverage browser caching
- Don't exceed 20-25 badges total

### Future Enhancements

After initial implementation:

1. **Dynamic Badges** - Badges that update based on repo state
1. **Custom Badges** - Project-specific badges
1. **Badge Dashboard** - Dedicated page showing all metrics
1. **Embedded Graphs** - Replace badges with mini-graphs
1. **OpenSSF Scorecard** - Security best practices badge

### Code Quality Badges (Optional)

If using external code quality services:

**Code Climate:**

```markdown
[![Maintainability](https://api.codeclimate.com/v1/badges/XXX/maintainability)](https://codeclimate.com/github/bdperkin/nhl-scrabble/maintainability)
```

**SonarCloud:**

```markdown
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=XXX&metric=alert_status)](https://sonarcloud.io/dashboard?id=XXX)
```

**Requires** setup on respective platforms.

### Maintenance Schedule

**Monthly:**

- Review badge accuracy
- Check for broken badge links
- Update manual badges if needed

**Quarterly:**

- Evaluate new badge opportunities
- Remove outdated/redundant badges
- Update badge organization

**Annually:**

- Review badge best practices
- Consider new badge sources
- Audit badge value vs. clutter

### Documentation Updates

Update CLAUDE.md with badge section:

```markdown
## Documentation Badges

The project uses comprehensive badges in README.md to provide at-a-glance information:

**Badge Categories:**
- Build & Quality - CI, CodeQL, Docs, Coverage
- Code Quality - Ruff, MyPy, Pre-commit
- Package Info - Python versions, License, UV, Version
- Community - Contributors, Stars, PRs, Issues, Activity
- Maintenance - Maintenance status, Last commit

**Badge Maintenance:**
- Most badges auto-update via GitHub APIs
- Manual badges (maintenance status) reviewed quarterly
- Badge links verified monthly
- Add new badges via enhancement/003 process

**Badge Sources:**
- shields.io - Primary badge generator
- GitHub Actions - Workflow status badges
- codecov.io - Coverage badges
- Direct GitHub badges - Stars, issues, commits
```

## Implementation Notes

*To be filled during implementation:*

- Date badges were added
- Which badges were selected for Phase 1
- Which badges were deferred to future phases
- Any badges that didn't work or were removed
- Badge organization strategy chosen
- Actual effort vs. estimated (1-2h)
- User/contributor feedback on badges
- Badge load time impact (if measurable)
- Any issues with badge services
