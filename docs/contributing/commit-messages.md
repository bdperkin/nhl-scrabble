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
