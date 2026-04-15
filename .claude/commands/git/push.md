# Git Push

______________________________________________________________________

## title: 'Git Push Changes' read_only: true type: 'command'

Analyze local commits and update remote refs along with associated objects.

## Process

1. Analyze local state and remote relationship:

   - Use `git status` to check current branch and tracking information
   - Use `git log --oneline origin/<branch>..HEAD` to see commits that will be pushed
   - Use `git remote -v` to verify remote repository URLs
   - Check if current branch has an upstream branch set

2. Assess push requirements and provide recommendations:

   - Determine if this is a first-time push (needs `git push -u origin <branch>`)
   - Check for potential conflicts with `git fetch` and `git status`
   - Analyze commit history to recommend appropriate push strategy
   - Identify if force push might be needed (and warn about dangers)
   - Suggest branch protection considerations for main branch

3. Execute push operation:

   - Use `git push` for standard pushes to tracked branches
   - Use `git push -u origin <branch>` to set upstream and push new branches
   - Use `git push origin <branch>` for explicit branch pushing
   - Consider `git push --force-with-lease` for safer force pushes when needed
   - Verify push success and provide confirmation of what was pushed
