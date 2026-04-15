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

2. Craft commit message recommendations:

   - Analyze the nature of the changes (e.g., "add", "fix", "update", "refactor", "docs")
   - Suggest a concise subject line (50 characters or less) that summarizes the changes
   - Recommend additional details for the commit body if needed
   - Follow conventional commit format if the project uses it
   - Ensure the message focuses on "why" rather than "what"
   - Do NOT add Claude co-authorship footers to commit messages

3. Execute commit:

   - Use `git commit -m "message"` for simple commits
   - Use `git commit` to open editor for multi-line messages
   - Consider `git commit --amend` if modifying the last commit
   - Verify commit was created successfully with `git log --oneline -1`
