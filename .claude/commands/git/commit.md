# Git Commit

______________________________________________________________________

## title: 'Git Commit Changes' read_only: true type: 'command'

Analyze staged changes and record them to the repository with an appropriate commit message.

## Process

1. Analyze staged changes:

   - Use `git status` to see what files are staged for commit
   - Use `git diff --cached` to review the actual changes that will be committed
   - Identify the type of changes (new features, bug fixes, refactoring, documentation, etc.)
   - Check for any sensitive information that shouldn't be committed
   - Verify all tests pass before committing

1. Craft commit message recommendations:

   - Analyze the nature of the changes (e.g., "add", "fix", "update", "refactor", "docs")
   - Suggest a concise subject line (50 characters or less) that summarizes the changes
   - Recommend additional details for the commit body if needed
   - Follow conventional commit format if the project uses it
   - Ensure the message focuses on "why" rather than "what"
   - Do NOT add Claude co-authorship footers to commit messages
   - Reference related issues/PRs (e.g., "Fixes #42", "Closes #123")

1. Execute commit:

   - Use `git commit -m "message"` for simple commits
   - Use `git commit` to open editor for multi-line messages
   - Use HEREDOC for multi-line messages in scripts
   - Consider `git commit --amend` if modifying the last commit
   - Use `git commit --no-verify` to skip hooks (only when necessary)
   - Verify commit was created successfully with `git log --oneline -1`

1. Handle commit failures:

   - If pre-commit hooks fail, fix the issues and create a NEW commit
   - NEVER use `--amend` after hook failure (would modify wrong commit)
   - Review hook output for specific errors to fix
   - Re-stage files after fixing issues

## Commit Message Guidelines

**Subject line:**

- Keep under 50 characters
- Use imperative mood ("Add feature" not "Added feature")
- Start with type prefix if using conventional commits
- Capitalize first letter
- No period at end

**Body (optional but recommended):**

- Wrap at 72 characters
- Explain "why" not "what"
- Separate from subject with blank line
- Use bullet points for multiple items
- Reference issues and PRs

**Conventional Commit Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style/formatting
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Test changes
- `build`: Build system changes
- `ci`: CI/CD changes
- `chore`: Maintenance tasks

## Safety Checks

Before committing, always verify:

- ✅ No sensitive data in staged files
- ✅ All tests pass
- ✅ Code follows project style guidelines
- ✅ Commit message is clear and descriptive
- ✅ Only related changes in single commit
- ✅ No debug code or console.log() statements

## Examples

```bash
# Simple commit
git commit -m "Fix login bug"

# Conventional commit
git commit -m "fix: resolve authentication timeout issue"

# Multi-line commit with HEREDOC
git commit -m "$(cat <<'EOF'
feat: Add user profile management

- Add profile editing interface
- Implement profile picture upload
- Add form validation

Closes #42
EOF
)"

# Commit with body in editor
git commit
# Opens editor for detailed message

# Amend last commit (local only!)
git commit --amend

# Amend without changing message
git commit --amend --no-edit

# Empty commit (for triggering CI)
git commit --allow-empty -m "Trigger CI rebuild"

# Skip pre-commit hooks (use sparingly)
git commit --no-verify -m "Emergency hotfix"
```

## Common Use Cases

**Standard commit workflow:**

```bash
git status                    # Check what's staged
git diff --cached             # Review changes
git commit -m "Add feature X" # Commit with message
git log --oneline -1          # Verify commit
```

**Conventional commit:**

```bash
git commit -m "feat: implement user authentication"
git commit -m "fix: resolve memory leak in data processor"
git commit -m "docs: update installation instructions"
```

**Multi-line commit:**

```bash
git commit  # Opens editor
# Write subject line
# Blank line
# Write detailed body
# Save and exit
```

**Fix last commit:**

```bash
# Forgot to add a file
git add forgotten_file.py
git commit --amend --no-edit

# Fix commit message
git commit --amend
# Edit message in editor
```

## IMPORTANT: Amend Safety

⚠️ **NEVER amend commits that have been pushed to shared branches!**

- Amending rewrites history
- Other developers may have pulled the original commit
- Use amend only for local, unpushed commits
- If you need to fix a pushed commit, create a new commit instead
