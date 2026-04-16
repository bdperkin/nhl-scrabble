# Git Add

______________________________________________________________________

## title: 'Git Add Files' read_only: true type: 'command'

Add file contents to the index (staging area) for the next commit.

## Process

1. Check current repository status:

   - Use `git status` to see which files are modified, untracked, or already staged
   - Identify which files need to be added to the staging area
   - Check for any files that should not be committed (.env, credentials, etc.)

1. Add files to staging area:

   - Use `git add <file>` to stage specific files (preferred for safety)
   - Use `git add <dir>` to stage all changes in a directory
   - Use `git add .` to stage all changes in current directory and subdirectories
   - Use `git add -A` to stage all changes in the entire repository
   - Use `git add -u` to stage only modified and deleted files (not new files)
   - Use `git add -p` for interactive staging (patch mode)

1. Verify staging:

   - Run `git status` again to confirm files are properly staged
   - Use `git diff --cached` to review what will be committed
   - Files should now appear under "Changes to be committed"
   - Use `git diff` to see unstaged changes still remaining

1. Make corrections if needed:

   - Use `git reset HEAD <file>` to unstage specific files
   - Use `git reset HEAD` to unstage all files
   - Re-add files as needed

## Safety Considerations

Before staging files, always verify:

- ✅ No sensitive data (.env, credentials, API keys, secrets)
- ✅ No large binary files (unless intended and using Git LFS)
- ✅ No build artifacts or generated files (.pyc, node_modules, dist)
- ✅ Files match what you intend to commit
- ✅ .gitignore is properly configured

## Examples

```bash
# Stage a specific file
git add src/module.py

# Stage multiple specific files
git add src/module.py tests/test_module.py

# Stage all Python files in current directory
git add *.py

# Stage all changes in src/ directory
git add src/

# Stage all changes (use with caution)
git add -A

# Interactive staging (choose which hunks to stage)
git add -p src/module.py

# Stage only tracked files (ignore new files)
git add -u

# Unstage a file
git reset HEAD src/module.py
```

## Common Use Cases

**Stage specific changes:**

```bash
git status              # See what changed
git add file1.py       # Stage one file
git add file2.py       # Stage another
git status             # Verify staging
```

**Stage everything safely:**

```bash
git status             # Review changes first
git add -A             # Stage all changes
git status             # Verify nothing unexpected
git diff --cached      # Review what will be committed
```

**Partial staging:**

```bash
git add -p file.py     # Interactive staging
# Choose 'y' to stage hunk, 'n' to skip, 's' to split, '?' for help
```
