# How to Contribute Code

Submit code contributions to NHL Scrabble.

## Problem

You want to contribute a bug fix, feature, or improvement.

## Solution

See the [First Contribution Tutorial](../tutorials/03-first-contribution.md) for a complete walkthrough.

## Quick reference

### 1. Fork and clone

```bash
# Fork on GitHub, then:
git clone https://github.com/YOUR-USERNAME/nhl-scrabble.git
cd nhl-scrabble
git remote add upstream https://github.com/bdperkin/nhl-scrabble.git
```

### 2. Create feature branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Make changes

- Follow existing code style
- Add type hints
- Write docstrings
- Include tests

### 4. Run quality checks

```bash
make quality  # Run all checks
pytest        # Run tests
```

### 5. Commit

```bash
git add .
git commit -m "feat: add your feature

Detailed description of changes.

Closes #123"
```

### 6. Push and create PR

```bash
git push -u origin feature/your-feature-name
# Then create PR on GitHub
```

## PR checklist

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Added tests for new code
- [ ] Updated documentation
- [ ] Descriptive commit messages
- [ ] PR links to related issue

## Related

- [First Contribution Tutorial](../tutorials/03-first-contribution.md) - Detailed guide
- [Development Workflow](../explanation/development-workflow.md) - Our process
- [CONTRIBUTING.md](../../CONTRIBUTING.md) - Full contributing guide
