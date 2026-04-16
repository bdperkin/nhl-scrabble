# Support

## Getting Help

Thank you for using NHL Scrabble Score Analyzer! This document provides guidance on how to get help with the project.

## Documentation

Before asking for help, please check the available documentation:

- **[README.md](README.md)** - Quick start guide and basic usage
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development setup and contribution guidelines
- **[CLAUDE.md](CLAUDE.md)** - Comprehensive project overview and architecture
- **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Detailed development workflows
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and release notes

## How to Get Help

### 1. Check Existing Issues

Search through [existing issues](https://github.com/bdperkin/nhl-scrabble/issues) to see if your question has already been answered.

### 2. GitHub Discussions (if enabled)

For general questions, ideas, or discussions, use GitHub Discussions (if available).

### 3. Create an Issue

If you can't find an answer, create a new issue:

- **Bug reports**: Use the bug report template
- **Feature requests**: Use the feature request template
- **Questions**: Use the question template or create a regular issue

**Issue Guidelines**:

- Use a clear, descriptive title
- Provide as much context as possible
- Include steps to reproduce (for bugs)
- Include your environment details (Python version, OS, etc.)
- Be respectful and patient

### 4. Stack Overflow

For general Python or programming questions, [Stack Overflow](https://stackoverflow.com) is a great resource. Use tags:

- `python`
- `nhl-api`
- `click` (for CLI questions)

## Common Issues

### Installation Problems

**Issue**: `pip install` fails

**Solutions**:

- Ensure you have Python 3.10+ installed: `python --version`
- Upgrade pip: `pip install --upgrade pip`
- Try using uv for faster installation: `uv pip install -e .`
- Check [CONTRIBUTING.md](CONTRIBUTING.md) for detailed setup instructions

### API Errors

**Issue**: "Failed to fetch NHL data"

**Solutions**:

- Check your internet connection
- Verify the NHL API is accessible: https://api-web.nhle.com/v1/standings/now
- Check if you're being rate-limited (wait a few minutes)
- Try increasing timeout: `NHL_SCRABBLE_API_TIMEOUT=30 nhl-scrabble analyze`

### Import Errors

**Issue**: `ModuleNotFoundError: No module named 'nhl_scrabble'`

**Solutions**:

- Ensure you installed in development mode: `pip install -e .`
- Activate your virtual environment: `source .venv/bin/activate`
- Reinstall: `make install-dev`

### Test Failures

**Issue**: Tests failing locally

**Solutions**:

- Ensure all dependencies installed: `make install-dev`
- Run with verbose output: `pytest -vv`
- Check specific failed test: `pytest tests/path/to/test_file.py::test_name -vv`
- See [CONTRIBUTING.md](CONTRIBUTING.md) for testing guidelines

## Reporting Bugs

When reporting bugs, please include:

1. **Description**: Clear description of the bug
1. **Steps to Reproduce**: Detailed steps to reproduce the issue
1. **Expected Behavior**: What you expected to happen
1. **Actual Behavior**: What actually happened
1. **Environment**:
   - OS: (e.g., Ubuntu 22.04, macOS 13, Windows 11)
   - Python version: `python --version`
   - Package version: `nhl-scrabble --version` or check `pyproject.toml`
1. **Error Messages**: Complete error messages and stack traces
1. **Additional Context**: Screenshots, logs, or any other helpful information

## Feature Requests

We welcome feature requests! When suggesting new features:

1. **Search First**: Check if someone already suggested it
1. **Describe Use Case**: Explain why this feature would be useful
1. **Provide Examples**: Show how it would work
1. **Consider Scope**: Be realistic about complexity and fit

## Security Issues

**Do not report security vulnerabilities in public issues!**

See [SECURITY.md](SECURITY.md) for instructions on reporting security vulnerabilities privately.

## Development Help

For help with development:

1. Read [CONTRIBUTING.md](CONTRIBUTING.md) for development setup
1. Check [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for workflows
1. Review [CLAUDE.md](CLAUDE.md) for project architecture
1. Use `make help` to see all available Makefile targets

## What to Expect

- **Response Time**: We aim to respond to issues within 2-3 business days
- **Bug Fixes**: Critical bugs addressed in next release; minor bugs as time permits
- **Feature Requests**: Evaluated based on fit, complexity, and maintainability
- **Questions**: Usually answered within a few days

## Code of Conduct

This project follows standard open-source community guidelines. Please be:

- **Respectful**: Treat everyone with respect
- **Constructive**: Provide helpful feedback
- **Patient**: Remember maintainers are often volunteers
- **Inclusive**: Welcome contributors of all backgrounds

## Additional Resources

- **NHL API**: https://api-web.nhle.com/
- **Python Documentation**: https://docs.python.org/3/
- **Click Documentation**: https://click.palletsprojects.com/
- **Pydantic Documentation**: https://docs.pydantic.dev/

## Contact

- **GitHub Issues**: https://github.com/bdperkin/nhl-scrabble/issues (preferred)
- **Maintainer**: See GitHub profile for contact information

## Thank You

Thank you for using NHL Scrabble Score Analyzer! Your questions, bug reports, and contributions help make this project better for everyone.
