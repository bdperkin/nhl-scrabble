# Your First Contribution to NHL Scrabble

Ready to contribute to NHL Scrabble? This tutorial walks you through making your first code contribution, from setup to pull request.

## What you'll learn

By the end of this tutorial, you'll have:

- ✅ Set up a complete development environment
- ✅ Run the test suite
- ✅ Made a small code change
- ✅ Run quality checks
- ✅ Created and submitted a pull request

**Time required**: ~30 minutes

## Prerequisites

- Completed the [Getting Started Tutorial](01-getting-started.md)
- GitHub account
- Git installed and configured
- Basic Python knowledge

## Step 1: Fork the repository

First, create your own copy of NHL Scrabble:

1. Go to https://github.com/bdperkin/nhl-scrabble
1. Click the **Fork** button in the top right
1. Wait for GitHub to create your fork

You now have your own copy at `https://github.com/YOUR-USERNAME/nhl-scrabble`

## Step 2: Clone your fork

Clone your fork (not the original repository):

```bash
git clone https://github.com/YOUR-USERNAME/nhl-scrabble.git
cd nhl-scrabble
```

Add the original repository as "upstream":

```bash
git remote add upstream https://github.com/bdperkin/nhl-scrabble.git
```

Verify your remotes:

```bash
git remote -v
```

You should see:

```
origin    https://github.com/YOUR-USERNAME/nhl-scrabble.git (fetch)
origin    https://github.com/YOUR-USERNAME/nhl-scrabble.git (push)
upstream  https://github.com/bdperkin/nhl-scrabble.git (fetch)
upstream  https://github.com/bdperkin/nhl-scrabble.git (push)
```

## Step 3: Set up development environment

Initialize the development environment:

```bash
make init
source .venv/bin/activate
```

This installs:

- All project dependencies
- Development tools (pytest, ruff, mypy)
- Pre-commit hooks
- Testing frameworks

**What are pre-commit hooks?**

Pre-commit hooks automatically check your code before each commit. They:

- Format code (black, ruff-format)
- Check for errors (ruff, mypy)
- Fix common issues (trailing whitespace, imports)
- Ensure quality standards

## Step 4: Run the test suite

Before making changes, verify everything works:

```bash
pytest
```

You should see:

```
================================ test session starts =================================
platform linux -- Python 3.12.19, pytest-9.0.3, pluggy-1.6.0
collected 131 items

tests/unit/test_scrabble.py ............                                      [  9%]
tests/unit/test_team_processor.py ..........                                  [ 17%]
tests/integration/test_cli.py ....................                            [ 32%]
...

======================== 131 passed in 23.45s ===========================
```

**All tests passing?** ✅ Great! You're ready to make changes.

**Tests failing?** ⚠️ Don't worry - pull the latest changes:

```bash
git pull upstream main
make install-dev
```

## Step 5: Create a feature branch

Never work directly on `main`. Create a feature branch:

```bash
git checkout -b add-my-feature
```

Branch naming conventions:

- `fix/description` - Bug fixes
- `feat/description` - New features
- `docs/description` - Documentation
- `refactor/description` - Code improvements

For this tutorial, let's add a simple feature - a new Scrabble letter value utility function.

## Step 6: Make a small change

Let's add a utility function to get individual letter values. Open `src/nhl_scrabble/scoring/scrabble.py`:

```bash
# Open in your editor
vim src/nhl_scrabble/scoring/scrabble.py
# or
code src/nhl_scrabble/scoring/scrabble.py
```

Add this new method to the `ScrabbleScorer` class (around line 40):

```python
def get_letter_value(self, letter: str) -> int:
    """Get the Scrabble value for a single letter.

    Args:
        letter: Single character to score (case-insensitive).

    Returns:
        Scrabble point value for the letter (0 if not a letter).

    Example:
        scorer = ScrabbleScorer()
        value = scorer.get_letter_value('Z')  # Returns 10
    """
    if not letter or not letter.isalpha():
        return 0
    return self.scrabble_values.get(letter.upper(), 0)
```

Save the file.

## Step 7: Write a test

Good code comes with tests. Open `tests/unit/test_scrabble.py` and add:

```python
def test_get_letter_value():
    """Test getting individual letter values."""
    scorer = ScrabbleScorer()

    # Test high-value letters
    assert scorer.get_letter_value("Z") == 10
    assert scorer.get_letter_value("Q") == 10
    assert scorer.get_letter_value("X") == 8
    assert scorer.get_letter_value("K") == 5

    # Test low-value letters
    assert scorer.get_letter_value("A") == 1
    assert scorer.get_letter_value("E") == 1

    # Test case insensitivity
    assert scorer.get_letter_value("z") == 10
    assert scorer.get_letter_value("Z") == 10

    # Test invalid input
    assert scorer.get_letter_value("") == 0
    assert scorer.get_letter_value("1") == 0
    assert scorer.get_letter_value(" ") == 0
```

Save the file.

## Step 8: Run tests

Run the test suite to verify your changes:

```bash
pytest tests/unit/test_scrabble.py::test_get_letter_value -v
```

You should see:

```
tests/unit/test_scrabble.py::test_get_letter_value PASSED                [100%]

======================== 1 passed in 0.12s ===========================
```

Run all tests to ensure nothing broke:

```bash
pytest
```

All 132 tests should pass (131 existing + 1 new).

## Step 9: Run quality checks

NHL Scrabble uses comprehensive quality checks. Run them all:

```bash
make quality
```

This runs:

- `ruff check` - Linting
- `ruff format --check` - Formatting check
- `mypy` - Type checking

Fix any issues that appear. For formatting issues, auto-fix with:

```bash
make ruff-format
```

## Step 10: Commit your changes

Stage your changes:

```bash
git add src/nhl_scrabble/scoring/scrabble.py tests/unit/test_scrabble.py
```

Commit with a descriptive message:

```bash
git commit -m "feat(scoring): add get_letter_value() method

Add utility method to get Scrabble value for individual letters.
Useful for debugging and custom scoring logic.

- Add get_letter_value() to ScrabbleScorer
- Add comprehensive tests
- Handle case insensitivity
- Return 0 for invalid input"
```

**What happens?**

Pre-commit hooks run automatically:

```
Check hooks apply to the repository..................Passed
trim trailing whitespace.............................Passed
fix end of files.....................................Passed
check yaml...........................................Passed
ruff check...........................................Passed
ruff format..........................................Passed
mypy.................................................Passed
...
[add-my-feature abc1234] feat(scoring): add get_letter_value() method
 2 files changed, 25 insertions(+)
```

If hooks fail, they'll auto-fix most issues. Review changes and commit again.

## Step 11: Push to your fork

Push your branch to your fork:

```bash
git push -u origin add-my-feature
```

## Step 12: Create a pull request

1. Go to your fork on GitHub: `https://github.com/YOUR-USERNAME/nhl-scrabble`
1. Click the **Compare & pull request** button
1. Fill in the PR template:

```markdown
## Summary

Add utility method to get Scrabble value for individual letters.

## Changes

- Add `get_letter_value()` method to `ScrabbleScorer`
- Add comprehensive unit tests
- Handle edge cases (empty string, numbers, case insensitivity)

## Testing

- ✅ All existing tests pass
- ✅ Added new test: `test_get_letter_value`
- ✅ Coverage: 100% on new code
- ✅ Quality checks pass (ruff, mypy)

## Motivation

Useful for debugging player scores and building custom scoring logic.
```

4. Click **Create pull request**

## Step 13: Wait for CI checks

GitHub Actions will automatically run:

- Tests on Python 3.12, 3.13, 3.14, 3.15
- All pre-commit hooks
- Code coverage checks
- Security scans

Watch the checks at the bottom of your PR. All should pass ✅.

## Step 14: Address review feedback

A maintainer will review your PR and may request changes:

- Add more tests
- Improve documentation
- Fix edge cases
- Adjust implementation

To make changes:

```bash
# Make your changes
vim src/nhl_scrabble/scoring/scrabble.py

# Commit and push
git add .
git commit -m "Address review feedback"
git push
```

The PR updates automatically!

## Step 15: Celebrate! 🎉

Once approved, a maintainer will merge your PR. Congratulations - you're now a contributor!

Your contribution will:

- Appear in the next release
- Be listed in the changelog
- Show on your GitHub profile

## What you've learned

You've successfully:

- ✅ Set up a development environment
- ✅ Run the test suite
- ✅ Made a code change
- ✅ Written tests
- ✅ Run quality checks
- ✅ Created a pull request
- ✅ Participated in code review

## Next steps

Ready for more?

1. **Find an issue**: Look for ["good first issue"](https://github.com/bdperkin/nhl-scrabble/labels/good%20first%20issue) labels
1. **Learn the codebase**: Read [Architecture Explanation](../explanation/architecture.md)
1. **Add a feature**: See [How to Add a Report Type](../how-to/add-report-type.md)
1. **Improve docs**: Documentation contributions are always welcome!

## Tips for success

**Do**:

- ✅ Start with small changes
- ✅ Write tests for all code
- ✅ Follow existing code style
- ✅ Keep PRs focused on one thing
- ✅ Respond to feedback promptly

**Don't**:

- ❌ Work directly on main branch
- ❌ Submit huge PRs
- ❌ Skip tests or quality checks
- ❌ Mix multiple unrelated changes
- ❌ Take feedback personally

## Common issues

### Issue: Pre-commit hooks failing

**Solution**: Let hooks auto-fix, then commit again:

```bash
git add -u
git commit
```

### Issue: Tests passing locally but failing in CI

**Solution**: Ensure you're testing with the same Python version:

```bash
tox -e py312  # Test with Python 3.12
tox -e py313  # Test with Python 3.13
tox -e py314  # Test with Python 3.14
tox -e py315  # Test with Python 3.15
```

### Issue: Merge conflicts

**Solution**: Update your branch from upstream:

```bash
git fetch upstream
git rebase upstream/main
# Resolve conflicts
git push --force-with-lease
```

### Issue: "Permission denied" when pushing

**Solution**: Check your remote is your fork, not upstream:

```bash
git remote -v
# origin should be YOUR-USERNAME, not bdperkin
```

## Getting help

- **Questions?** Ask in your PR or [open a discussion](https://github.com/bdperkin/nhl-scrabble/discussions)
- **Stuck?** See [Support Guide](../../SUPPORT.md)
- **Found a bug?** [Open an issue](https://github.com/bdperkin/nhl-scrabble/issues)

Thank you for contributing to NHL Scrabble! 🏒
