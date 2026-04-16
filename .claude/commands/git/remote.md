# Git Remote

______________________________________________________________________

## title: 'Git Remote Management' read_only: true type: 'command'

Manage set of tracked repositories (remotes) for fetching and pushing changes.

## Process

1. Determine remote operation:

   - List existing remotes
   - Add new remote
   - Remove remote
   - Rename remote
   - Change remote URL
   - Show remote information

1. Execute appropriate command:

   - Use `git remote` to list remotes
   - Use `git remote add` to add remote
   - Use `git remote remove` to delete remote
   - Use `git remote rename` to rename
   - Use `git remote set-url` to change URL

1. Verify operation:

   - Confirm remote added/changed
   - Test with `git fetch <remote>`
   - Check with `git remote -v`

## Remote Basics

**Origin:**

- Default remote name
- Usually the repository you cloned from
- Convention, not requirement

**Upstream:**

- Common name for original repo when forking
- Tracks project you forked from
- Allows syncing with main project

## Examples

```bash
# List remotes
git remote
git remote -v  # With URLs

# Add remote
git remote add origin https://github.com/user/repo.git
git remote add upstream https://github.com/original/repo.git

# Remove remote
git remote remove origin
git remote rm origin  # Alias

# Rename remote
git remote rename origin old-origin

# Change URL
git remote set-url origin https://github.com/user/new-repo.git

# Show remote info
git remote show origin

# Get remote URL
git remote get-url origin

# Set different push URL
git remote set-url --push origin https://github.com/user/repo.git

# Prune stale branches
git remote prune origin
git remote prune origin --dry-run  # Preview
```

## Common Use Cases

**Clone and check remote:**

```bash
git clone https://github.com/user/repo.git
cd repo
git remote -v
# origin  https://github.com/user/repo.git (fetch)
# origin  https://github.com/user/repo.git (push)
```

**Add upstream for fork:**

```bash
# After forking on GitHub
git remote add upstream https://github.com/original/repo.git
git remote -v
# origin    https://github.com/you/repo.git (fetch)
# origin    https://github.com/you/repo.git (push)
# upstream  https://github.com/original/repo.git (fetch)
# upstream  https://github.com/original/repo.git (push)
```

**Change to SSH from HTTPS:**

```bash
git remote -v  # Check current URL
git remote set-url origin git@github.com:user/repo.git
git remote -v  # Verify change
```

**Add multiple remotes:**

```bash
git remote add origin https://github.com/user/repo.git
git remote add gitlab https://gitlab.com/user/repo.git
git remote add bitbucket https://bitbucket.org/user/repo.git
```

**Rename remote:**

```bash
git remote rename origin upstream
git remote rename upstream origin
```

## Remote URLs

**HTTPS format:**

```bash
https://github.com/user/repo.git
https://gitlab.com/user/repo.git
https://bitbucket.org/user/repo.git
```

**SSH format:**

```bash
git@github.com:user/repo.git
git@gitlab.com:user/repo.git
git@bitbucket.org:user/repo.git
```

**Change protocol:**

```bash
# HTTPS to SSH
git remote set-url origin git@github.com:user/repo.git

# SSH to HTTPS
git remote set-url origin https://github.com/user/repo.git
```

## Show Remote Information

**Basic info:**

```bash
git remote show origin
```

**Output shows:**

- Remote URL
- HEAD branch
- Remote branches
- Local branches configured for pull
- Local refs configured for push

**Example output:**

```
* remote origin
  Fetch URL: https://github.com/user/repo.git
  Push  URL: https://github.com/user/repo.git
  HEAD branch: main
  Remote branches:
    main      tracked
    feature-a tracked
    feature-b tracked
  Local branch configured for 'git pull':
    main merges with remote main
  Local ref configured for 'git push':
    main pushes to main (up to date)
```

## Working with Multiple Remotes

**Fork workflow:**

```bash
# 1. Add upstream
git remote add upstream https://github.com/original/repo.git

# 2. Fetch from upstream
git fetch upstream

# 3. Merge upstream changes
git checkout main
git merge upstream/main

# 4. Push to your fork
git push origin main
```

**Mirror to multiple remotes:**

```bash
git remote add origin https://github.com/user/repo.git
git remote add gitlab https://gitlab.com/user/repo.git

# Push to both
git push origin main
git push gitlab main

# Or configure push to multiple:
git config remote.all.url "https://github.com/user/repo.git"
git config --add remote.all.url "https://gitlab.com/user/repo.git"
git push all main  # Pushes to both
```

## Prune Remote Branches

**Why prune:**

- Remove stale remote-tracking branches
- Clean up deleted branches
- Keep `git branch -r` output current

**How to prune:**

```bash
# Preview what will be pruned
git remote prune origin --dry-run

# Prune deleted branches
git remote prune origin

# Prune automatically on fetch
git config remote.origin.prune true

# Or globally
git config --global fetch.prune true
```

## Remote Branches

**List remote branches:**

```bash
git branch -r              # Remote branches
git branch -a              # All branches (local + remote)
```

**Fetch from remote:**

```bash
git fetch origin           # Fetch all branches
git fetch origin main      # Fetch specific branch
```

**Checkout remote branch:**

```bash
git checkout -b feature origin/feature
# Or (Git 2.23+):
git switch -c feature origin/feature
```

**Delete remote branch:**

```bash
git push origin --delete feature-branch
```

## Troubleshooting

**Remote already exists:**

```bash
# Remove and re-add
git remote remove origin
git remote add origin <url>

# Or just change URL
git remote set-url origin <new-url>
```

**Wrong URL:**

```bash
git remote -v              # Check current
git remote set-url origin <correct-url>
git remote -v              # Verify
```

**Can't fetch from remote:**

```bash
# Check URL is correct
git remote -v

# Test connection
ping github.com

# Try re-adding
git remote remove origin
git remote add origin <url>

# Check authentication
git ls-remote origin
```

**Multiple push URLs:**

```bash
# Set different push URL
git remote set-url --push origin <push-url>

# Check
git remote -v
# origin  <fetch-url> (fetch)
# origin  <push-url>  (push)
```

## Best Practices

**1. Use descriptive remote names:**

```bash
git remote add upstream <url>     # ✅ Clear purpose
git remote add backup <url>       # ✅ Clear purpose
git remote add fork <url>         # ✅ Clear purpose
```

**2. Verify remotes after adding:**

```bash
git remote add origin <url>
git remote -v                     # Verify
git fetch origin                  # Test connection
```

**3. Use SSH for private repos:**

```bash
# SSH (recommended for private)
git remote add origin git@github.com:user/repo.git

# HTTPS (works for public, needs credentials for private)
git remote add origin https://github.com/user/repo.git
```

**4. Prune regularly:**

```bash
git remote prune origin
# Or configure auto-prune
git config fetch.prune true
```

**5. Fork workflow:**

```bash
# origin = your fork
# upstream = original repo
git remote add origin <your-fork-url>
git remote add upstream <original-repo-url>
```

## Configuration

**Set default push remote:**

```bash
git config branch.main.remote origin
```

**Set default push ref:**

```bash
git config push.default current
```

**Auto-prune on fetch:**

```bash
git config remote.origin.prune true
git config --global fetch.prune true
```

## Advanced Operations

**Add remote with fetch:**

```bash
git remote add -f origin <url>
# Adds remote and fetches immediately
```

**Add remote with track:**

```bash
git remote add -t main origin <url>
# Only track specific branch
```

**Set HEAD for remote:**

```bash
git remote set-head origin main
```

**Get remote's HEAD:**

```bash
git remote show origin | grep "HEAD"
```

## Remote Naming Conventions

**Common names:**

- `origin` - Your primary remote (default)
- `upstream` - Original repo in fork workflow
- `fork` - Your fork of another project
- `backup` - Backup location
- `production` - Production deployment
- `staging` - Staging deployment

**Example setup:**

```bash
git remote add origin git@github.com:you/repo.git
git remote add upstream git@github.com:original/repo.git
git remote add production git@production-server:repo.git
```

## Migration

**Change from HTTPS to SSH:**

```bash
# Get current URL
git remote get-url origin

# Convert to SSH (GitHub)
git remote set-url origin git@github.com:user/repo.git

# Test
ssh -T git@github.com
```

**Move to different platform:**

```bash
# Add new remote
git remote add new-origin <new-url>

# Push all branches
git push new-origin --all
git push new-origin --tags

# Update origin
git remote remove origin
git remote rename new-origin origin
```

## Tips

- Use `git remote -v` to see all remotes with URLs
- Name remotes descriptively (origin, upstream, etc.)
- Use SSH for easier authentication
- Prune stale branches regularly
- Test new remotes with `git fetch`
- Keep origin for your main repository
- Use upstream for forked projects
- Verify URLs before adding
- Use `git remote show` for detailed info
