# Pull Request Process

Follow this process when creating and reviewing pull requests.

## Before Submitting

Checklist before creating a PR:

1. ✅ All tests pass
1. ✅ Code coverage is maintained or improved
1. ✅ Code is formatted with ruff
1. ✅ No linting errors
1. ✅ Type checking passes
1. ✅ Documentation is updated
1. ✅ Commit messages are clear
1. ✅ Branch is up-to-date with main

## Submitting a Pull Request

### 1. Push Your Branch

```bash
git push origin feature/your-feature-name
```

### 2. Create Pull Request on GitHub

### 3. Fill Out the PR Template

Include:

- Description of changes
- Related issue numbers
- Testing performed
- Screenshots (if UI changes)

### 4. Address Review Feedback

- Make requested changes
- Push updates to your branch
- Respond to comments

## PR Review Criteria

Pull requests will be reviewed for:

- **Functionality**: Does it work as intended?
- **Tests**: Are there adequate tests?
- **Code Quality**: Is the code clean and maintainable?
- **Documentation**: Is it properly documented?
- **Style**: Does it follow project conventions?
- **Performance**: Are there any performance concerns?

## Reviewing Dependabot Pull Requests

This project uses [GitHub Dependabot](https://docs.github.com/en/code-security/dependabot) to automatically create PRs for dependency updates.

### For Security Updates (Immediate Action Required)

1. **Review the vulnerability**: Check the security advisory linked in the PR
1. **Verify the fix**: Ensure the updated version addresses the vulnerability
1. **Check compatibility**: Review changelog for breaking changes
1. **Run tests**: Ensure CI passes (automatic)
1. **Merge quickly**: Security updates should be merged promptly

**Example PR**: `deps(python): Bump requests from 2.31.0 to 2.31.1 [security]`

### For Regular Updates (Review Weekly)

Dependabot groups related updates to reduce noise:

- **Development dependencies**: Grouped minor/patch updates
- **Production dependencies**: Grouped patch updates
- **GitHub Actions**: Grouped workflow updates

**Review process**:

1. **Check the changelog**: Review what changed in each dependency
1. **Verify tests pass**: CI must be green
1. **Check for breaking changes**: Review major version bumps carefully
1. **Test locally if needed**: For significant updates, test locally
1. **Merge**: If tests pass and no issues, merge

**Automated checks**:

- ✅ All tests run automatically
- ✅ Pre-commit hooks verify code quality
- ✅ Type checking runs
- ✅ Coverage is maintained

**When to reject**:

- ❌ Tests fail
- ❌ Breaking changes without migration path
- ❌ Known issues with new version
- ❌ Requires significant refactoring

**Labels on Dependabot PRs**:

- `dependencies` - All dependency updates
- `python` - Python package updates
- `github-actions` - GitHub Actions updates
- `security` - Security-related updates (auto-added by GitHub)

**Commit message format**:

Dependabot PRs use [conventional commits](https://www.conventionalcommits.org/):

- `deps(python): Bump package from X to Y`
- `ci: Update GitHub Actions to v2`

## Stale Issue/PR Policy

To keep the issue tracker relevant and manageable:

- **Issues** inactive for 60 days are marked stale
- **Pull requests** inactive for 30 days are marked stale
- Items are closed 7 days after being marked stale

**To prevent closure:**

- Add a comment with an update
- Add the `keep-open` label
- Continue working on it

**Closed items can be reopened** at any time if still relevant.
