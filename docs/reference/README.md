# Reference Documentation

Technical specifications and complete API documentation for NHL Scrabble.

## What is reference documentation?

Reference documentation is **information-oriented** material that describes the machinery - the technical specifications, APIs, commands, and configuration options. It's for looking up facts, not for learning or problem-solving.

## Available References

### Command-Line Interface

- **[CLI Reference](cli.md)** - Complete command-line interface documentation
  - All commands and subcommands
  - All options and flags
  - Exit codes
  - Environment variables
  - Examples

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

- **[Python API Reference](code-api.md)** - Use NHL Scrabble as a library

  - Public classes and functions
  - Type signatures
  - Return values
  - Examples

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
