# GitHub Maintainer Review Protocol

______________________________________________________________________

## title: 'GitHub Maintainer Review Protocol' read_only: true type: 'command'

Comprehensive workflow for maintainers reviewing pull requests, from initial triage through merging.

## Process

### 1. Initial Triage & Environment Sync

Before reviewing code, ensure your local environment matches the remote state and the contributor's work is accessible.

- **Fetch Remote Changes:** Update your local tracking branches to ensure you aren't reviewing against stale code.
  ```bash
  git fetch --all --prune
  ```

- **Check out the PR Branch:** Use the GitHub CLI to bring the contributor's code into your local environment for testing.
  ```bash
  gh pr checkout <pr-number>
  ```

- **Verify CI Status:** Confirm that all automated checks (GitHub Actions, unit tests, linting) have passed before manual review begins.
  ```bash
  gh pr checks <pr-number>
  ```

### 2. Technical Review & Code Analysis

The maintainer focuses on logic, architecture, and long-term sustainability.

- **Diff Analysis:** Review the files changed. Look for 'code smells,' breaking changes in APIs, or deviations from the project's design patterns.
  ```bash
  git diff main...HEAD
  gh pr diff <pr-number>
  ```

- **Security Audit:** Check for exposed secrets, unsafe dependencies, or vulnerable logic patterns (e.g., SQL injection or improper input sanitization).
  - Run security scanners (e.g., `pip-audit`, `bandit`)
  - Review dependency changes in `pyproject.toml` and lock files
  - Check for hardcoded credentials or API keys

- **Documentation Check:** Ensure that any new features or logic changes are reflected in the `README.md` or `/docs` folder.
  - Verify docstrings are complete (interrogate compliance)
  - Check that user-facing changes are documented
  - Ensure CHANGELOG.md will be updated (via conventional commits)

- **Run Local Tests:** Execute the full test suite to catch issues that CI might have missed.
  ```bash
  make test
  make tox
  make quality
  ```

### 3. Collaborative Feedback (The 'Review' Phase)

Interaction with the contributor happens through three primary actions:

- **Comment:** Ask for clarification on specific lines without blocking the PR.
  - Use for questions, suggestions, or non-critical observations
  - Helpful for mentoring or explaining project conventions

- **Request Changes:** Formally block the PR from merging until specific technical issues are addressed.
  - Use for bugs, security issues, or significant design problems
  - Be specific about what needs to change and why
  - Provide actionable feedback

- **Approve:** Signal that the code is ready for the main branch.
  - Only approve when all technical concerns are resolved
  - Ensure CI is green and tests pass locally

> **Maintainer Tip:** Use **Suggested Changes** in the GitHub UI. This allows you to provide a code snippet that the contributor can apply with a single click, reducing friction.

```bash
# Review via CLI
gh pr review <pr-number> --comment --body "Your feedback here"
gh pr review <pr-number> --request-changes --body "Issues to address"
gh pr review <pr-number> --approve
```

### 4. Final Validation & Merging

Once the contributor has addressed feedback and CI is green:

- **Final Pre-Merge Checks:**
  - Verify all conversations are resolved
  - Confirm CI is passing
  - Review the final commit message (especially for squash merges)
  - Check that the PR title follows Conventional Commits format

- **Choose Merge Strategy:**

  - **Squash and Merge** (Preferred): Combines all contributor commits into one clean commit on the main branch to keep history readable.
    - Best for feature branches with many small commits
    - Ensures clean, linear history
    - Preserves PR context in merge commit message

  - **Rebase and Merge**: Moves the contributor's commits to the tip of the main branch.
    - Best when commits are already well-structured
    - Maintains individual commit history
    - Creates linear history without merge commits

  - **Create a Merge Commit**: Creates a merge commit with all original commits.
    - Best for large features or when preserving exact commit history is important
    - Shows clear integration points in history

- **Merge the PR:**
  ```bash
  gh pr merge <pr-number> --squash --delete-branch
  gh pr merge <pr-number> --rebase --delete-branch
  gh pr merge <pr-number> --merge --delete-branch
  ```

- **Delete Branch:** Clean up the repository by deleting the feature branch post-merge.
  - Usually handled automatically with `--delete-branch` flag
  - Keeps repository tidy and prevents stale branch accumulation

- **Post-Merge Verification:**
  - Pull latest changes to main branch
  - Verify the merge appears correctly in history
  - Check that any related issues were automatically closed

## Notes

- This protocol assumes the project follows Conventional Commits for changelog generation
- All quality checks (pre-commit hooks, CI) must pass before merging
- For this project specifically, ensure UV-accelerated tox runs pass and coverage requirements are met
- Never bypass pre-commit hooks with `--no-verify` during review
