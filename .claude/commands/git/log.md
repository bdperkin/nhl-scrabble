# Git Log

______________________________________________________________________

## title: 'Git Log History' read_only: true type: 'command'

Show commit history with various formatting and filtering options.

## Process

1. Determine information needed:

   - Recent commits (default behavior)
   - Specific file or directory history
   - Commits by author or date range
   - Branch comparison
   - Graphical representation

1. Execute appropriate log command:

   - Use `git log` for standard output
   - Use `git log --oneline` for compact view
   - Use `git log --graph` for branch visualization
   - Use `git log -p` to show patches (diffs)
   - Use `git log --stat` for file statistics

1. Analyze and present results:

   - Identify recent changes
   - Find specific commits
   - Understand branch history
   - Track file changes
   - Find commits by author or message

## Common Formats

**One-line format:**

- `--oneline` - Compact format (hash + message)
- `--graph` - ASCII graph showing branches
- `--decorate` - Show branch and tag names
- `--all` - Show all branches

**Detailed format:**

- `-p` or `--patch` - Show diff for each commit
- `--stat` - Show file change statistics
- `--shortstat` - Condensed statistics
- `--name-only` - Only show changed file names
- `--name-status` - Show file names with status

## Examples

```bash
# Recent commits (default)
git log

# Compact one-line format
git log --oneline

# Last 10 commits
git log -10
git log --oneline -10

# With graph and all branches
git log --oneline --graph --all --decorate

# Show diffs
git log -p
git log -p -2  # Last 2 commits with diffs

# Show file statistics
git log --stat

# Pretty format
git log --pretty=format:"%h - %an, %ar : %s"

# Commits in date range
git log --since="2 weeks ago"
git log --after="2024-01-01" --before="2024-12-31"

# Commits by author
git log --author="John Doe"

# Commits mentioning specific text
git log --grep="fix bug"

# File history
git log -- path/to/file.py
git log -p -- path/to/file.py  # With diffs

# Commits affecting function
git log -L :function_name:path/to/file.py

# Commits on branch not on main
git log main..feature-branch
git log --oneline main..HEAD

# Commits in branch A but not branch B
git log branch-B..branch-A
```

## Common Use Cases

**Review recent work:**

```bash
git log --oneline -10          # Last 10 commits
git log --oneline --graph -20  # Last 20 with graph
```

**Find specific commit:**

```bash
git log --grep="authentication"  # Search commit messages
git log --author="Alice"        # By author
git log -S "function_name"      # By code content
```

**Compare branches:**

```bash
git log main..feature           # What's in feature but not main
git log --oneline origin/main..HEAD  # Unpushed commits
```

**File history:**

```bash
git log -- src/module.py        # All commits affecting file
git log -p -- src/module.py     # With diffs
git log --follow -- src/new.py  # Follow through renames
```

**Beautiful output:**

```bash
git log --graph --oneline --decorate --all
git log --pretty=format:"%C(yellow)%h%Creset %C(blue)%ad%Creset | %s%C(green)%d%Creset %C(bold red)[%an]%Creset" --date=short
```

## Useful Aliases

Add to `~/.gitconfig`:

```ini
[alias]
    lg = log --oneline --graph --decorate --all
    ll = log --pretty=format:'%C(yellow)%h%Creset %C(blue)%ad%Creset | %s%C(green)%d%Creset %C(bold red)[%an]%Creset' --date=short
    ls = log --stat
    lp = log -p
    last = log -1 HEAD
```

Then use:

```bash
git lg        # Nice graph
git ll        # Pretty format
git last      # Last commit
```

## Format Placeholders

For `--pretty=format:`:

- `%H` - Commit hash (full)
- `%h` - Commit hash (abbreviated)
- `%an` - Author name
- `%ae` - Author email
- `%ad` - Author date
- `%ar` - Author date (relative)
- `%cn` - Committer name
- `%cd` - Commit date
- `%cr` - Commit date (relative)
- `%s` - Subject (commit message)
- `%b` - Body
- `%d` - Ref names (branches, tags)

## Filtering Options

**By date:**

```bash
git log --since="2 weeks ago"
git log --after="2024-01-01"
git log --before="yesterday"
```

**By author:**

```bash
git log --author="Alice"
git log --committer="Bob"
```

**By message:**

```bash
git log --grep="bug fix"
git log --grep="feat:" --grep="fix:"  # OR
git log --grep="feat:" --grep="fix:" --all-match  # AND
```

**By content:**

```bash
git log -S "function_name"    # Added or removed
git log -G "regex_pattern"    # Matches regex
```

**By file:**

```bash
git log -- path/to/file
git log --follow -- file      # Follow renames
```

## Tips

- Use `--oneline` for quick overview
- Add `--graph` to visualize branches
- Use `-p` to see what actually changed
- Use `--stat` for file-level overview
- Combine options for powerful queries
- Create aliases for frequent commands
- Press `q` to quit log viewer
