# How-to Guides

Practical, goal-oriented guides for solving specific problems with NHL Scrabble.

## What are how-to guides?

How-to guides are **problem-oriented** recipes that guide you through solving specific, real-world tasks. Unlike tutorials (which teach), how-to guides assume you have basic knowledge and need to accomplish a specific goal.

## Available Guides

### Installation & Setup

- **[Installation Variations](installation.md)** - Different ways to install NHL Scrabble
  - Install from PyPI (when available)
  - Install from source
  - Install with UV (10x faster)
  - Install for development
  - Docker installation
  - Offline installation

### Development

- **[Add a Report Type](add-report-type.md)** - Create custom report generators

  - Inherit from BaseReport
  - Implement generation logic
  - Register with CLI
  - Write tests

- **[Run Tests](run-tests.md)** - Execute different test configurations

  - Run all tests
  - Run specific tests
  - Run with coverage
  - Run with tox (multi-Python)
  - Parallel testing

- **[Setup Pre-commit Hooks](setup-pre-commit-hooks.md)** - Configure automated quality checks

  - Install hooks
  - Run manually
  - Customize hook configuration
  - Skip specific hooks
  - Update hook versions

- **[Use UV Package Manager](use-uv.md)** - Leverage UV for 10-100x speedup

  - Install UV
  - Use UV with tox
  - Manage dependencies
  - Lock file management

- **[Contribute Code](contribute-code.md)** - Submit code contributions

  - Fork and clone
  - Create feature branch
  - Make changes
  - Submit PR
  - Address review

### Configuration & Usage

- **[Configure API Settings](configure-api-settings.md)** - Customize NHL API behavior

  - Set timeout values
  - Configure retries
  - Adjust rate limits
  - Enable/disable caching
  - Environment variables

- **[Customize Output Format](customize-output-format.md)** - Control report formatting

  - Change output format (text/JSON)
  - Customize player counts
  - Filter teams/divisions
  - Save to file
  - Redirect output

- **[Export to JSON](export-to-json.md)** - Export data in JSON format

  - Generate JSON reports
  - Understand JSON structure
  - Import into Excel/Sheets
  - Use with Python/JavaScript
  - Query JSON with jq

### Web Interface

- **[Use the Web Interface](use-web-interface.md)** - Access NHL Scrabble via browser

  - Start the web server
  - Use the interactive form
  - Configure analysis parameters
  - View API documentation
  - Mobile usage

- **[Deploy the Web Interface](deploy-web-interface.md)** - Production deployment

  - Production server setup (Uvicorn, Gunicorn)
  - Reverse proxy configuration (Nginx, Caddy, Traefik)
  - Process management (Systemd, Docker)
  - Security configuration
  - Environment variables
  - Performance tuning

### Troubleshooting

- **[Debug API Issues](debug-api-issues.md)** - Diagnose NHL API problems

  - Connection timeouts
  - 404 errors
  - Rate limiting
  - Invalid responses
  - Network debugging

- **[Web Interface Troubleshooting](troubleshooting-web.md)** - Fix web interface issues

  - Server won't start
  - Static files not loading
  - API endpoint errors
  - Performance issues
  - Browser compatibility
  - Docker issues

## How to use these guides

- **Jump to what you need**: Guides are independent - start anywhere
- **Follow the steps**: Each guide has clear, actionable steps
- **Adapt to your needs**: Guides show the general approach - customize for your situation
- **Combine guides**: Use multiple guides together to solve complex problems

## Not finding what you need?

- **Learning the basics?** Start with [Tutorials](../tutorials/)
- **Looking up syntax?** Check the [Reference](../reference/) documentation
- **Want to understand why?** Read [Explanations](../explanation/)
- **Have a question?** See our [Support Guide](../../SUPPORT.md)
- **Found a gap?** [Suggest a new guide](https://github.com/bdperkin/nhl-scrabble/issues)

## Contributing guides

Know how to solve a problem? Share your knowledge!

See [How to Contribute Code](contribute-code.md) to add new how-to guides.
