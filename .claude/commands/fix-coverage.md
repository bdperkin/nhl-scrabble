# Fix Pytest Coverage Gap

______________________________________________________________________

## title: 'Fix Pytest Coverage Gap' read_only: true type: 'command'

Automates the end-to-end workflow for identifying, targeting, and fixing test coverage gaps in a specific Python file or module using `pytest` and `coverage.py`. The primary goal is to turn "red" (untested) lines into "green" (tested) lines, focusing on high-impact logic, error handlers, and edge cases to prevent future regressions.

**Usage:**

```bash
/fix-coverage <target_file_or_module>
```

## Process

1. **Create Implementation Branch**

   - Verify the current working directory is clean (`git status`)
   - Switch to the main branch and pull the latest changes
   - Generate a unique branch name based on the target: `test-coverage/<target_name>`
   - Create and switch to the new branch: `git checkout -b test-coverage/<target_name>`

1. **Implement Solution**

   - Locate the target file/module
   - Analyze the current source code to identify complex logic, `if/else` branches, or exception blocks
   - If the code contains unreachable "dead code", flag it for deletion rather than trying to write tests for it

1. **Implement Tests**

   - Locate or create the corresponding test file (e.g., `tests/test_<target_name>.py`)
   - Write explicit `pytest` unit tests designed to execute the untested paths
   - Focus heavily on edge cases, boundary inputs, and mocking external dependencies if needed

1. **Verify Acceptance Criteria**

   - Ensure tests assert actual behaviors, side effects, or return values
   - **Constraint**: Do not write shallow assertions just to pass lines; tests must validate correct execution logic

1. **Pre-Flight Validation**

   - Run the test suite using `pytest-cov` to measure the target's coverage locally
   - Execute: `pytest --cov=<target_module> --cov-report=term-missing tests/`
   - Verify that the target lines have been executed and the file's coverage percentage has increased

1. **Update Documentation**

   - If fixing this gap uncovered a non-obvious architecture quirk or requirement, document it inline via docstrings
   - Update any internal tracking or markdown testing notes if relevant to the project

1. **Commit Implementation**

   - Stage the modified target file and the new test file: `git add .`
   - Commit the changes with a clear descriptive message: `git commit -m "test(coverage): increase test coverage for <target_name>"`

1. **Automated Pre-Flight Validation**

   - Run the full project linting, type-checking, and test suite locally to guarantee no regressions were introduced
   - Command: `pytest && ruff check .` (or equivalent project lint tools)

1. **Push to Remote**

   - Push the branch to the origin repository: `git push origin test-coverage/<target_name>`

1. **Create Pull Request**

   - Generate a Pull Request link or use the GitHub/GitLab CLI to open a PR
   - Title: `test: fix coverage gaps in <target_name>`
   - Description: Include details on which specific branches, loops, or error handlers are now validated

1. **Wait for CI/CD**

   - Monitor remote pipeline execution
   - Ensure all remote testing, coverage checks, and status gates pass successfully

1. **Merge Pull Request**

   - Once CI/CD passes and peer approval is granted, squash and merge the PR into the main branch

1. **Return to Main Branch**

   - Switch back to your local environment's primary branch: `git checkout main` (or `master`)

1. **Update Local Main**

   - Pull down the newly merged remote changes to keep the local copy synchronized: `git pull origin main`

1. **Delete Task Branch**

   - Clean up the local workspace by removing the temporary feature branch: `git branch -d test-coverage/<target_name>`

1. **Report Completion**

   - Provide a final status summary detailing:
     - The baseline coverage vs. the new coverage percentage
     - Specific edge cases or code blocks successfully resolved
     - Confirmation of local branch cleanup
