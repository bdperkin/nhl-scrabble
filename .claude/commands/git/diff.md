# Git Diff

______________________________________________________________________

## title: 'Git Diff Changes' read_only: true type: 'command'

Show differences between commits, working tree, staging area, and branches.

## Process

1. Determine what to compare:

   - Working directory vs staging area (unstaged changes)
   - Staging area vs last commit (staged changes)
   - Between commits or branches
   - Specific files or directories

1. Execute appropriate diff command:

   - Use `git diff` for unstaged changes
   - Use `git diff --cached` for staged changes
   - Use `git diff HEAD` for all uncommitted changes
   - Use `git diff branch1..branch2` for branch comparison
   - Use `git diff commit1 commit2` for commit comparison

1. Analyze and present results:

   - Show added/removed lines
   - Highlight changed sections
   - Identify file modifications
   - Review before committing
   - Compare implementations

## Diff Types

**Working Tree Diffs:**

- `git diff` - Unstaged changes (working vs staging)
- `git diff HEAD` - All changes (working vs last commit)
- `git diff --staged` or `--cached` - Staged changes

**Commit Diffs:**

- `git diff commit1 commit2` - Between two commits
- `git diff branch1..branch2` - Between branch tips
- `git diff branch1...branch2` - Since branches diverged

**File-Specific:**

- `git diff -- file.py` - Specific file changes
- `git diff --name-only` - Just file names
- `git diff --stat` - Statistics only

## Examples

```bash
# Unstaged changes (working vs staging)
git diff

# Staged changes (staging vs last commit)
git diff --staged
git diff --cached  # Same as --staged

# All uncommitted changes
git diff HEAD

# Specific file
git diff src/module.py
git diff --cached src/module.py

# Between commits
git diff abc123 def456
git diff HEAD~2 HEAD

# Between branches
git diff main feature-branch
git diff main..feature-branch  # Same

# Since branches diverged
git diff main...feature-branch

# File names only
git diff --name-only
git diff --name-status  # With status (M, A, D)

# Statistics
git diff --stat
git diff --shortstat

# Ignore whitespace
git diff -w
git diff --ignore-all-space

# Word diff (better for prose)
git diff --word-diff

# Show function context
git diff --function-context

# Highlight moved code
git diff --color-moved
```

## Common Use Cases

**Review before staging:**

```bash
git diff                    # See what changed
git diff src/module.py      # Specific file
git add src/module.py       # Stage if good
```

**Review before committing:**

```bash
git diff --cached           # See what will be committed
git commit -m "message"     # Commit if satisfied
```

**Compare branches:**

```bash
git diff main..feature      # All differences
git diff main...feature     # Since divergence
```

**Find what changed:**

```bash
git diff HEAD~1             # Last commit
git diff HEAD~5 HEAD        # Last 5 commits
git diff --stat origin/main..HEAD  # Unpushed changes
```

**Review specific changes:**

```bash
git diff -p                 # Show full patches
git diff --stat             # Summary only
git diff --name-only        # Just file names
```

## Output Format

**Diff Header:**

```diff
diff --git a/file.py b/file.py
index abc123..def456 100644
--- a/file.py
+++ b/file.py
```

**Change Markers:**

- `---` - Old file
- `+++` - New file
- `@@` - Hunk header (location)
- `-` - Removed line (red)
- `+` - Added line (green)
- (space) - Context line (unchanged)

**Example Output:**

```diff
@@ -10,7 +10,8 @@ def calculate_score(name):
     total = 0
-    for char in name:
+    # Calculate score for each character
+    for char in name.upper():
         if char.isalpha():
             total += LETTER_VALUES.get(char, 0)
     return total
```

## Useful Options

**Format Options:**

- `--color` - Colorize output
- `--no-color` - Disable colors
- `--color-words` - Word-level diff
- `--unified=N` - N lines of context (default 3)
- `--minimal` - Spend more time for smaller diff

**Filter Options:**

- `--diff-filter=A` - Only added files
- `--diff-filter=M` - Only modified files
- `--diff-filter=D` - Only deleted files
- `--diff-filter=R` - Only renamed files

**Whitespace Options:**

- `-w` or `--ignore-all-space` - Ignore whitespace
- `-b` or `--ignore-space-change` - Ignore whitespace changes
- `--ignore-blank-lines` - Ignore blank line changes

## Comparing Specific Items

**Files:**

```bash
git diff HEAD -- file1.py file2.py
git diff branch1 branch2 -- src/
```

**Commits:**

```bash
git diff abc123 def456
git diff HEAD~3 HEAD~1
```

**Branches:**

```bash
git diff main feature
git diff origin/main main
```

## Advanced Usage

**Show differences in staged files:**

```bash
git diff --cached --name-only  # List staged files
git diff --cached --stat       # Staged file stats
```

**Ignore specific files:**

```bash
git diff -- . ':!package-lock.json'
git diff -- . ':!*.lock'
```

**Compare with remote:**

```bash
git fetch
git diff origin/main
git diff HEAD origin/main
```

**Visual diff tools:**

```bash
git difftool              # Use configured diff tool
git difftool --tool=vimdiff
git difftool --tool=meld
```

## Tips

- Use `git diff` before `git add` to review changes
- Use `git diff --cached` before `git commit` to review staged
- Add `-w` to ignore whitespace noise
- Use `--stat` for quick overview
- Use `--name-only` to see just file list
- Configure a visual diff tool for complex diffs
- Press `q` to quit diff viewer
- Use `git diff HEAD` to see all uncommitted changes at once
