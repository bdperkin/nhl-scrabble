# How to Install NHL Scrabble

Different installation methods for various use cases.

## Problem

You want to install NHL Scrabble using the best method for your situation.

## Solutions

Choose the installation method that fits your needs:

### Method 1: Install from source (Recommended for now)

**When to use**: Current primary installation method until package is published to PyPI.

**Steps**:

```bash
# Clone repository
git clone https://github.com/bdperkin/nhl-scrabble.git
cd nhl-scrabble

# Install with traditional tools
make init
source .venv/bin/activate

# Verify installation
nhl-scrabble --version
```

**What this does**:

- Creates Python virtual environment
- Installs all dependencies
- Installs NHL Scrabble in editable mode
- Sets up development tools

### Method 2: Install with UV (10x faster)

**When to use**: You want fastest possible installation.

**Steps**:

```bash
# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repository
git clone https://github.com/bdperkin/nhl-scrabble.git
cd nhl-scrabble

# Install with UV
make uv-init
source .venv/bin/activate

# Verify installation
nhl-scrabble --version
```

**Benefits**:

- 10-100x faster than pip
- Deterministic dependency resolution
- Built-in virtual environment management
- Compatible with all Python tools

See [How to Use UV](use-uv.md) for more details.

### Method 3: Install from PyPI (Future)

**When to use**: Once package is published to PyPI.

**Steps**:

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install from PyPI
pip install nhl-scrabble

# Verify installation
nhl-scrabble --version
```

**Status**: Not yet available. Watch the [releases page](https://github.com/bdperkin/nhl-scrabble/releases).

### Method 4: Development installation

**When to use**: You want to modify the code or contribute.

**Steps**:

```bash
# Fork the repository on GitHub first
git clone https://github.com/YOUR-USERNAME/nhl-scrabble.git
cd nhl-scrabble

# Add upstream remote
git remote add upstream https://github.com/bdperkin/nhl-scrabble.git

# Install development dependencies
make init

# Install pre-commit hooks
pre-commit install

# Verify installation
pytest
```

**What this includes**:

- All runtime dependencies
- Development tools (pytest, ruff, mypy)
- Pre-commit hooks (automatic quality checks)
- Testing frameworks (pytest, pytest-cov, pytest-mock)

See [First Contribution Tutorial](../tutorials/03-first-contribution.md) for complete guide.

### Method 5: Docker installation (Advanced)

**When to use**: You want containerized installation.

**Steps**:

Create a `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y git make

# Clone and install
RUN git clone https://github.com/bdperkin/nhl-scrabble.git .
RUN make init

# Activate venv in container
ENV PATH="/app/.venv/bin:$PATH"

# Default command
CMD ["nhl-scrabble", "analyze"]
```

Build and run:

```bash
# Build image
docker build -t nhl-scrabble .

# Run analysis
docker run nhl-scrabble

# Save output
docker run -v $(pwd):/output nhl-scrabble nhl-scrabble analyze --output /output/report.txt
```

### Method 6: Offline installation

**When to use**: Installing on a machine without internet access.

**Steps**:

On a machine with internet:

```bash
# Download dependencies
pip download -r requirements.txt -d ./packages

# Archive the packages
tar -czf nhl-scrabble-offline.tar.gz ./packages ./src ./pyproject.toml ./Makefile
```

On offline machine:

```bash
# Extract archive
tar -xzf nhl-scrabble-offline.tar.gz
cd nhl-scrabble-offline

# Create venv
python -m venv .venv
source .venv/bin/activate

# Install from local packages
pip install --no-index --find-links=./packages -e .

# Verify
nhl-scrabble --version
```

## Verification

After installation, verify it works:

```bash
# Check version
nhl-scrabble --version

# Run analysis (requires internet for NHL API)
nhl-scrabble analyze

# Run tests (development installation only)
pytest
```

## Troubleshooting

### Issue: "command not found: nhl-scrabble"

**Solution**: Activate the virtual environment:

```bash
source .venv/bin/activate
```

### Issue: "Python 3.12 or higher required"

**Solution**: Upgrade Python:

```bash
# macOS
brew install python@3.12

# Ubuntu/Debian
sudo apt install python3.12

# Windows
# Download from python.org
```

### Issue: "Permission denied"

**Solution**: Don't use sudo with pip/make:

```bash
# Wrong
sudo make init

# Correct
make init
```

### Issue: "Failed building wheel for..."

**Solution**: Install build dependencies:

```bash
# macOS
xcode-select --install

# Ubuntu/Debian
sudo apt install python3-dev build-essential

# Windows
# Install Visual Studio Build Tools
```

### Issue: "UV not found"

**Solution**: Install UV first:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH (if needed)
export PATH="$HOME/.cargo/bin:$PATH"
```

## Platform-specific notes

### macOS

- Requires Command Line Tools: `xcode-select --install`
- Use Homebrew for Python: `brew install python@3.12`
- May need to use `python3` instead of `python`

### Linux

- Most distributions include Python 3.12+
- May need python3-venv package: `sudo apt install python3-venv`
- Some distros use `python3` command

### Windows

- Install Python from [python.org](https://www.python.org/downloads/)
- Check "Add Python to PATH" during installation
- Use PowerShell or Git Bash, not CMD
- Activation command: `.venv\Scripts\activate`

## Uninstallation

To remove NHL Scrabble:

```bash
# Deactivate virtual environment
deactivate

# Remove directory
rm -rf nhl-scrabble

# If installed from PyPI
pip uninstall nhl-scrabble
```

## Related

- [Use UV Package Manager](use-uv.md) - For fastest installation
- [Getting Started Tutorial](../tutorials/01-getting-started.md) - After installation
- [Configure API Settings](configure-api-settings.md) - Customize behavior
- [Run Tests](run-tests.md) - Verify development installation
