# Git Add

______________________________________________________________________

## title: 'Git Add Files' read_only: true type: 'command'

Add file contents to the index (staging area) for the next commit.

## Process

1. Check current repository status:

   - Use `git status` to see which files are modified, untracked, or already staged
   - Identify which files need to be added to the staging area

2. Add files to staging area:

   - Use `git add <file>` to stage specific files
   - Use `git add .` to stage all changes in current directory
   - Use `git add -A` to stage all changes in the entire repository
   - Use `git add -u` to stage only modified and deleted files (not new files)

3. Verify staging:

   - Run `git status` again to confirm files are properly staged
   - Use `git diff --cached` to review what will be committed
   - Files should now appear under "Changes to be committed"
