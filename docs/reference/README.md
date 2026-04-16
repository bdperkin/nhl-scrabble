# Reference Documentation

Technical specifications and complete API documentation for NHL Scrabble.

## What is reference documentation?

Reference documentation is **information-oriented** material that describes the machinery - the technical specifications, APIs, commands, and configuration options. It's for looking up facts, not for learning or problem-solving.

## Available References

### Command-Line Interface

- **[CLI Reference (Auto-Generated)](cli-generated.md)** - Complete CLI documentation

  - ⚡ Auto-generated from Click decorators
  - Always up-to-date with code
  - All commands and options
  - Usage examples
  - Exit codes

- **[CLI Reference (Manual)](cli.md)** - Curated command-line guide

  - Usage patterns
  - Best practices
  - Advanced examples

### Configuration

- **[Configuration Reference](configuration.md)** - All configuration options

  - Environment variables
  - Configuration file format
  - Default values
  - Validation rules
  - Examples

- **[Environment Variables](environment-variables.md)** - Complete environment variable reference

  - API configuration
  - Logging configuration
  - Output configuration
  - Development settings

### Build & Development Tools

- **[Makefile Reference](makefile.md)** - All Makefile targets

  - Setup targets
  - Testing targets
  - Quality check targets
  - Build targets
  - 55 documented targets

- **[Tox Reference](tox.md)** - Tox environment reference

  - Python version environments
  - Quality check environments
  - Coverage environments
  - Configuration options

### APIs & Data Formats

- **[Python API Reference (Auto-Generated)](api/index.md)** - Complete API documentation

  - ⚡ Auto-generated from docstrings
  - 100% coverage (interrogate enforced)
  - All modules, classes, and functions
  - Type hints and signatures
  - Interactive HTML documentation

- **[Python API Reference (Manual)](code-api.md)** - Using NHL Scrabble as a library

  - Getting started with the API
  - Common usage patterns
  - Integration examples
  - Best practices

- **[NHL API Reference](nhl-api.md)** - NHL API endpoints used

  - Standings endpoint
  - Roster endpoint
  - Response formats
  - Rate limits

- **[Scrabble Values](scrabble-values.md)** - Letter values and scoring rules

  - Letter point values
  - Scoring algorithm
  - Edge cases
  - Examples

### Output Formats

- **[JSON Schema Reference](json-schema.md)** - JSON output structure

  - Complete schema
  - Field descriptions
  - Examples
  - Validation

- **[Text Report Format](text-report-format.md)** - Text output structure

  - Report sections
  - Formatting rules
  - Indicators and symbols

## How to use reference documentation

- **Look up facts**: Find specific information quickly
- **Check syntax**: Verify exact command syntax
- **Validate values**: Check allowed values and formats
- **Copy examples**: Use examples as starting points
- **Link from code**: Reference docs from docstrings

## Not finding what you need?

- **Learning the basics?** Start with [Tutorials](../tutorials/)
- **Solving a problem?** Check [How-to Guides](../how-to/)
- **Understanding concepts?** Read [Explanations](../explanation/)
- **Have a question?** See our [Support Guide](../../SUPPORT.md)
- **Missing reference?** [Request it](https://github.com/bdperkin/nhl-scrabble/issues)

## Contributing

Found an error in the reference docs? Please [open an issue](https://github.com/bdperkin/nhl-scrabble/issues).

Want to add missing reference documentation? See [How to Contribute](../how-to/contribute-code.md).
