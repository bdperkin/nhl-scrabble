# QA Automation Framework

This directory contains standalone quality assurance automation tests that are separate from the main project's unit and integration tests.

## Directory Structure

```
qa/
├── web/          # Web automation tests (Playwright)
├── api/          # API automation tests (future)
├── cli/          # CLI automation tests (future)
├── tui/          # TUI automation tests (future)
└── sdk/          # SDK automation tests (future)
```

## Purpose

The QA automation framework provides comprehensive testing beyond traditional unit and integration tests:

- **Functional Testing**: End-to-end user workflows
- **Visual Regression Testing**: UI appearance verification
- **Performance Testing**: Load and stress testing
- **Accessibility Testing**: WCAG compliance verification
- **Cross-browser Testing**: Multi-browser compatibility

## Test Types

### Web Tests (`./web/`)

Automated web interface testing using Playwright:

- **Framework**: Playwright (Python)
- **Browsers**: Chromium, Firefox, WebKit
- **Test Types**: Functional, Visual, Performance, Accessibility
- **See**: [web/README.md](web/README.md)

### API Tests (`./api/`)

**Status**: Planned for future implementation

Automated API testing for RESTful endpoints.

### CLI Tests (`./cli/`)

**Status**: Planned for future implementation

Automated command-line interface testing.

### TUI Tests (`./tui/`)

**Status**: Planned for future implementation

Automated terminal UI testing.

### SDK Tests (`./sdk/`)

**Status**: Planned for future implementation

Automated SDK/library usage testing.

## Quick Start

### Web Tests

```bash
# Install dependencies
make qa-install

# Run all web tests
make qa-test

# Run specific test types
make qa-functional
make qa-visual
make qa-performance
make qa-accessibility
```

## Integration with CI/CD

QA tests are integrated into the CI/CD pipeline:

- **Pre-merge**: Functional and accessibility tests
- **Post-merge**: Full test suite including visual and performance
- **Nightly**: Comprehensive cross-browser testing

## Documentation

- [Web Testing Guide](web/README.md)
- [Makefile Reference](../docs/reference/makefile.md) (QA targets)
- [Contributing Guide](../CONTRIBUTING.md)

## Best Practices

1. **Isolation**: QA tests are independent of main project tests
1. **Page Object Model**: Use POM pattern for maintainability
1. **Test Data**: Use fixtures and factories for test data
1. **Idempotency**: Tests should be runnable in any order
1. **Stability**: Use auto-waiting and proper selectors
1. **Documentation**: Keep READMEs and comments up to date

## Makefile Targets

Run `make help` and look for the "QA Testing" section:

```bash
make qa-install           # Install QA dependencies
make qa-test              # Run all QA tests
make qa-functional        # Run functional tests only
make qa-visual            # Run visual regression tests
make qa-performance       # Run performance tests
make qa-accessibility     # Run accessibility tests
make qa-clean             # Clean QA artifacts
```

## Support

- **Issues**: [GitHub Issues](https://github.com/bdperkin/nhl-scrabble/issues)
- **Discussions**: [GitHub Discussions](https://github.com/bdperkin/nhl-scrabble/discussions)
- **Documentation**: [Online Docs](https://bdperkin.github.io/nhl-scrabble/)
