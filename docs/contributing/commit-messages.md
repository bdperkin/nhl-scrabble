# Commit Message Guidelines

Write clear, descriptive commit messages following the [Conventional Commits](https://www.conventionalcommits.org/) format.

## Format

```
type(scope): Short description

Longer explanation of the change. Explain WHY the change was made,
not just WHAT changed. Include motivation, context, and implementation
details.

Closes #123
```

## Requirements

Enforced by [gitlint](https://jorisroovers.com/gitlint/) in pre-commit hooks and CI.

**Title:**

- Length: 5-100 characters
- Format: `type(scope): description`
- Types: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `build`, `ci`, `chore`
- Scope: Optional module/component (e.g., `api`, `cli`, `reports`)
- Description: Clear summary of the change
- Use present tense: "Add feature" not "Added feature"

**Body:**

- Minimum 10 characters total
- Maximum 100 characters per line
- Explain WHY the change was made, not just WHAT changed
- Include motivation, context, and implementation details
- Reference related issues with `Closes #123` or `Fixes #456`

## Good Examples

```
✅ feat(api): Add caching to NHL API client

Implement request-level caching with 1-hour TTL to reduce API calls
and improve performance. Cache is stored in memory and cleared on
process restart.

Closes #42
```

```
✅ fix(cli): Validate output path before writing

Check that output directory exists and is writable before attempting
to write report files. Prevents cryptic IOError messages.

Fixes #87
```

```
✅ docs: Update installation instructions

Add UV installation instructions and update Python version requirements
to reflect 3.12+ support.
```

## Bad Examples

```
❌ "fix" - Title too short (< 5 characters)

❌ "Add support for multiple output formats including JSON, CSV, Excel, HTML, and XML with comprehensive formatting options"
   - Title too long (> 100 characters)

❌ "feat: Add feature" - Body missing (non-trivial change needs explanation)
```

## Special Cases

**Bot Commits:**

Bot commits may need `SKIP=gitlint git commit` if gitlint conflicts with automated formats.

**Trivial Changes:**

Small changes (typo fixes, formatting) still need properly formatted messages but may have shorter bodies.

## Automated Changelog Generation

This project uses conventional commits to **automatically generate CHANGELOG.md** via [git-cliff](https://git-cliff.org/).

### How It Works

1. **Commits** are written following conventional commit format
2. **git-cliff** parses commit history between version tags
3. **CHANGELOG.md** is automatically updated on release
4. **GitHub releases** include generated changelog notes

### Commit Type to Changelog Mapping

Commit types are mapped to [Keep a Changelog](https://keepachangelog.com/) categories:

| Commit Type | Changelog Section | Description |
|-------------|-------------------|-------------|
| `feat:` | **Added** | New features |
| `fix:` | **Fixed** | Bug fixes |
| `refactor:` | **Changed** | Code refactoring |
| `perf:` | **Performance** | Performance improvements |
| `docs:` | **Documentation** | Documentation changes |
| `deprecate:` | **Deprecated** | Deprecation warnings |
| `remove:` | **Removed** | Removed features |
| `security:` | **Security** | Security fixes |
| `style:` | *(skipped)* | Code style changes (not in changelog) |
| `test:` | *(skipped)* | Test changes (not in changelog) |
| `chore:` | *(skipped)* | Chore tasks (not in changelog) |
| `ci:` | *(skipped)* | CI/CD changes (not in changelog) |
| `build:` | *(skipped)* | Build system changes (not in changelog) |

### Writing Good Changelog Entries

Since commit messages become changelog entries, write them with **end users in mind**:

**Good (user-focused):**
```
✅ feat(api): Add caching to improve performance

Implement request-level caching with 1-hour TTL to reduce API calls
and improve performance by up to 80% for repeated queries.
```

**Bad (developer-focused):**
```
❌ refactor: Extract helper function

Move duplicate code into a helper function to reduce duplication.
```

**Guidance:**

- ✅ Focus on **what changed for users**, not internal implementation
- ✅ Highlight **benefits** (performance, usability, new capabilities)
- ✅ Use **clear, non-technical language** when possible
- ✅ Be **specific** about what was added/fixed/changed
- ❌ Don't describe internal refactoring unless it impacts users
- ❌ Don't use jargon or abbreviations without explanation

### Testing Changelog Output

Preview how your commits will appear in the changelog:

```bash
# Preview unreleased changes
make changelog-preview

# Generate full changelog locally
make changelog-update

# Preview specific tag
make changelog-tag TAG=v1.0.0
```

### Configuration

Changelog generation is configured in `.cliff.toml`. See the configuration for:

- Commit type mappings
- Changelog template
- Commit filtering rules
- Version detection patterns

### CI/CD Integration

On every release (version tag push):

1. GitHub Actions workflow runs
2. `git-cliff` generates updated CHANGELOG.md
3. Changelog is committed back to repository
4. GitHub release is created with changelog notes

See `.github/workflows/publish.yml` for the workflow definition.
