# Git Tag

______________________________________________________________________

## title: 'Git Tag Management' read_only: true type: 'command'

Create, list, and manage tags for marking specific points in repository history (releases, versions).

## Process

1. Determine tag operation:

   - List existing tags
   - Create new tag (lightweight or annotated)
   - Delete tag (local or remote)
   - Show tag information
   - Push tags to remote

1. Execute appropriate command:

   - Use `git tag` to list tags
   - Use `git tag <name>` for lightweight tag
   - Use `git tag -a <name>` for annotated tag
   - Use `git tag -d <name>` to delete
   - Use `git push --tags` to push tags

1. Verify operation:

   - Confirm tag created/deleted
   - Check tag points to correct commit
   - Verify tag pushed to remote if needed

## Tag Types

**Lightweight Tags:**

- Simple pointer to commit
- Just a name
- No metadata
- Use for temporary/private marks

**Annotated Tags:**

- Full objects in Git
- Contains tagger name, email, date
- Can have message
- Can be signed/verified
- Recommended for releases

## Examples

```bash
# List all tags
git tag
git tag -l
git tag --list

# List tags matching pattern
git tag -l "v1.*"

# Create lightweight tag
git tag v1.0.0

# Create annotated tag
git tag -a v1.0.0 -m "Release version 1.0.0"

# Create annotated tag (opens editor)
git tag -a v1.0.0

# Tag specific commit
git tag v1.0.0 abc123
git tag -a v1.0.0 abc123 -m "message"

# Show tag information
git show v1.0.0

# Delete local tag
git tag -d v1.0.0

# Delete remote tag
git push origin --delete v1.0.0
git push origin :refs/tags/v1.0.0  # Alternative

# Push single tag
git push origin v1.0.0

# Push all tags
git push --tags
git push origin --tags

# Fetch tags from remote
git fetch --tags

# Checkout tag (creates detached HEAD)
git checkout v1.0.0

# Create branch from tag
git checkout -b hotfix-v1 v1.0.0
```

## Common Use Cases

**Create release tag:**

```bash
git checkout main
git pull
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin v1.2.0
# Or push all tags:
git push --tags
```

**List releases:**

```bash
git tag                    # All tags
git tag -l "v*"           # Tags starting with v
git tag -l "v1.*"         # v1 series
git tag -n                # With first line of message
```

**Delete tag:**

```bash
# Local
git tag -d v1.0.0-beta

# Remote
git push origin --delete v1.0.0-beta
```

**Rename tag:**

```bash
# Tags can't be renamed, must delete and recreate
git tag new-name old-name
git tag -d old-name
git push origin :refs/tags/old-name
git push origin new-name
```

**Tag old commit:**

```bash
git log --oneline          # Find commit
git tag -a v0.9.0 abc123 -m "Beta release"
git push origin v0.9.0
```

## Tag Naming Conventions

**Semantic Versioning:**

```bash
git tag -a v1.2.3 -m "message"
# v = prefix (common)
# 1 = major (breaking changes)
# 2 = minor (new features)
# 3 = patch (bug fixes)
```

**Common Patterns:**

- `v1.0.0` - Version 1.0.0
- `v1.0.0-beta.1` - Pre-release
- `v1.0.0-rc.1` - Release candidate
- `v1.0.0-alpha.1` - Alpha release
- `release-2024.01` - Date-based

**Examples:**

```bash
git tag -a v1.0.0 -m "Initial release"
git tag -a v1.1.0 -m "Add user authentication"
git tag -a v1.1.1 -m "Fix login bug"
git tag -a v2.0.0 -m "Breaking: New API"
git tag -a v2.0.0-beta.1 -m "Beta release"
```

## Viewing Tags

**List tags:**

```bash
git tag                # Simple list
git tag -l "v1.*"     # Pattern match
git tag -n            # With message (1 line)
git tag -n5           # With 5 lines of message
```

**Show tag details:**

```bash
git show v1.0.0       # Full tag info
git tag -v v1.0.0     # Verify signed tag
```

**Sort tags:**

```bash
git tag --sort=version:refname     # Version sort
git tag --sort=-version:refname    # Reverse
git tag --sort=creatordate         # By date
```

## Pushing Tags

**Push single tag:**

```bash
git push origin v1.0.0
```

**Push all tags:**

```bash
git push --tags
git push origin --tags
```

**Push with atomic:**

```bash
git push --atomic origin main v1.0.0
# Both or neither
```

**Auto-push tags:**

```bash
git config --global push.followTags true
# Auto-pushes annotated tags with commits
```

## Checking Out Tags

**Detached HEAD (read-only):**

```bash
git checkout v1.0.0
# Warning: detached HEAD state
# View code at this tag, but can't commit
```

**Create branch from tag:**

```bash
git checkout -b hotfix-v1.0 v1.0.0
# Now can make commits on new branch
```

## Signed Tags

**Create signed tag (GPG):**

```bash
git tag -s v1.0.0 -m "Signed release v1.0.0"
# Requires GPG key configured
```

**Verify signed tag:**

```bash
git tag -v v1.0.0
# Checks GPG signature
```

**Setup GPG:**

```bash
git config user.signingkey <key-id>
git config tag.gpgSign true  # Auto-sign tags
```

## Tag Information

**Show tag:**

```bash
git show v1.0.0
# Shows tag object and commit
```

**Tag points to:**

```bash
git rev-parse v1.0.0
# Shows commit hash
```

**Tags containing commit:**

```bash
git tag --contains abc123
# Lists all tags containing commit
```

**Describe from tag:**

```bash
git describe
# Output: v1.0.0-14-gabc123
# 14 commits since v1.0.0
```

## Best Practices

**1. Use annotated tags for releases:**

```bash
# ✅ Good: Annotated
git tag -a v1.0.0 -m "Release version 1.0.0"

# ❌ Avoid: Lightweight for releases
git tag v1.0.0
```

**2. Follow semantic versioning:**

- MAJOR.MINOR.PATCH (1.2.3)
- Increment MAJOR for breaking changes
- Increment MINOR for new features
- Increment PATCH for bug fixes

**3. Tag from main/master:**

```bash
git checkout main
git pull
git tag -a v1.0.0 -m "message"
git push origin v1.0.0
```

**4. Write descriptive messages:**

```bash
git tag -a v1.2.0 -m "$(cat <<'EOF'
Release version 1.2.0

New features:
- User authentication
- Profile management
- Email notifications

Bug fixes:
- Fixed login timeout
- Resolved memory leak

Breaking changes:
- API endpoints now require authentication
EOF
)"
```

**5. Don't re-tag:**

- Tags should be immutable
- Delete and recreate if needed
- Coordinate with team

## Troubleshooting

**Tag already exists:**

```bash
# Delete old tag
git tag -d v1.0.0
git push origin --delete v1.0.0

# Create new tag
git tag -a v1.0.0 -m "message"
git push origin v1.0.0
```

**Tag not pushed:**

```bash
# git push doesn't push tags by default
git push origin v1.0.0
# Or push all tags:
git push --tags
```

**Can't delete remote tag:**

```bash
# Try both syntaxes:
git push origin --delete v1.0.0
git push origin :refs/tags/v1.0.0
```

**Detached HEAD after checkout:**

```bash
# Expected behavior with tags
# Create branch if you need to commit:
git checkout -b hotfix-v1 v1.0.0
```

## Advanced Operations

**Find tags by pattern:**

```bash
git tag -l "v1.*.*"        # v1 series
git tag -l "*-beta*"       # Beta releases
```

**Move tag to different commit:**

```bash
# Delete old tag
git tag -d v1.0.0
git push origin --delete v1.0.0

# Create new tag
git tag -a v1.0.0 abc123 -m "message"
git push origin v1.0.0
```

**Export tags:**

```bash
git tag > tags.txt
```

**Clone with specific tag:**

```bash
git clone --branch v1.0.0 <url>
```

## Lightweight vs Annotated

**Lightweight:**

```bash
git tag v1.0.0
# Just a pointer, no metadata
# Use for temporary/local marks
```

**Annotated:**

```bash
git tag -a v1.0.0 -m "Release v1.0.0"
# Full Git object with metadata
# Use for releases/public tags
```

**Show difference:**

```bash
# Lightweight - just shows commit
git show v1.0.0-light

# Annotated - shows tag object then commit
git show v1.0.0-annotated
```

## Tips

- Use annotated tags (`-a`) for releases
- Follow semantic versioning (vMAJOR.MINOR.PATCH)
- Write descriptive tag messages
- Push tags separately (`git push --tags`)
- Tag from stable branch (main/master)
- Don't move tags after pushing
- Sign important releases (`-s`)
- Use tags for release points, not branches
- List tags with `git tag -l "pattern"`
- Checkout tag creates detached HEAD (expected)
