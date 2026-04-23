# UV Quick Reference Card

Quick reference for using UV with the NHL Scrabble project.

## Installation

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version

# Or check via Makefile
make uv-check
```

## Common Commands

| Task               | Make Command                       | Direct UV Command                           |
| ------------------ | ---------------------------------- | ------------------------------------------- |
| **Setup**          |                                    |                                             |
| Check uv installed | `make uv-check`                    | `uv --version`                              |
| Create venv        | `make uv-venv`                     | `uv venv .venv --python python3.12`         |
| Full init          | `make uv-init`                     | (multiple steps)                            |
| **Install**        |                                    |                                             |
| Install package    | `make uv-install`                  | `uv pip install -e .`                       |
| Install dev deps   | `make uv-install-dev`              | `uv pip install -e ".[dev,docs]"`           |
| **Update**         |                                    |                                             |
| Update all         | `make uv-update`                   | `uv pip install --upgrade -e ".[dev,docs]"` |
| Update specific    | -                                  | `uv pip install --upgrade <package>`        |
| **Run**            |                                    |                                             |
| Run app            | `make uv-run`                      | `uv run nhl-scrabble analyze`               |
| Run script         | -                                  | `uv run python script.py`                   |
| **Info**           |                                    |                                             |
| List packages      | `make uv-pip ARGS="list"`          | `uv pip list`                               |
| Show package       | `make uv-pip ARGS="show requests"` | `uv pip show requests`                      |
| Freeze deps        | -                                  | `uv pip freeze`                             |

## Speed Comparison

| Operation        | pip  | uv    | Speedup |
| ---------------- | ---- | ----- | ------- |
| Create venv      | ~3s  | ~0.5s | **6x**  |
| Install (cold)   | ~45s | ~5s   | **9x**  |
| Install (cached) | ~25s | ~1s   | **25x** |
| Resolve deps     | ~10s | ~0.3s | **33x** |

## Workflow Examples

### First Time Setup

```bash
# Clone repo
git clone https://github.com/bdperkin/nhl-scrabble.git
cd nhl-scrabble

# Setup with uv (fast!)
make uv-init
source .venv/bin/activate
```

### Daily Development

```bash
# Activate environment
source .venv/bin/activate

# Install new dependency
uv pip install httpx

# Run tests
pytest

# Run application
make uv-run
```

### Update Dependencies

```bash
# Update all to latest compatible versions
make uv-update

# Commit changes
git add pyproject.toml
git commit -m "Update dependencies"
```

### CI/CD Usage

```yaml
# GitHub Actions
  - name: Install uv
    uses: astral-sh/setup-uv@v4

  - name: Install dependencies
    run: uv pip install -e ".[dev]" --system
```

## Tips & Tricks

### 1. Global Cache

UV uses a global cache for packages:

```bash
# View cache location
uv cache dir

# Clean cache
uv cache clean

# Check cache size
uv cache clean --dry-run
```

### 2. Parallel Installation

UV automatically parallelizes package downloads - no configuration needed!

### 3. Offline Mode

```bash
# After cache is populated
uv pip install -e . --offline
```

### 4. Custom Index

```bash
# Use custom PyPI mirror
uv pip install -e . --index-url https://your-mirror.com/simple
```

### 5. Compile for Different Platforms

```bash
# Compile for specific platform
uv pip compile pyproject.toml --python-platform linux
```

## Troubleshooting

### UV Not Found

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
export PATH="$HOME/.cargo/bin:$PATH"
```

### Permission Errors

```bash
# Use --system flag for system Python
uv pip install -e . --system

# Or ensure you're in a venv
source .venv/bin/activate
```

### Cache Issues

```bash
# Clear cache and retry
uv cache clean
make uv-install-dev
```

### Compatibility Issues

```bash
# Fall back to pip for problematic packages
pip install problematic-package

# Continue with uv for everything else
make uv-install-dev
```

## Configuration Files

| File              | Purpose                                                          |
| ----------------- | ---------------------------------------------------------------- |
| `pyproject.toml`  | UV config in `[tool.uv]` section, dependencies, project metadata |
| `.python-version` | Python version (3.12-3.15) - read by UV, pyenv, and asdf         |

**Example [tool.uv] configuration:**

```toml
[tool.uv]
managed = true          # Enable UV dependency management
package = true          # This is a Python package
compile-bytecode = true # Compile .pyc files for faster imports
link-mode = "copy"      # Copy files instead of linking
```

## Resources

- Full docs: [docs/UV.md](UV.md)
- UV GitHub: https://github.com/astral-sh/uv
- Makefile: [../Makefile](../Makefile)
- pyproject.toml: [../pyproject.toml](../pyproject.toml)
- .python-version: [../.python-version](../.python-version)

## Quick Decision Tree

```
Need to install dependencies?
├─ First time? → make uv-init
├─ Just deps? → make uv-install-dev
└─ Update all? → make uv-update

Need to run something?
├─ Tests → pytest (after install)
├─ App → make uv-run
└─ Script → uv run python script.py

Having issues?
├─ Check install → make uv-check
├─ Clear cache → uv cache clean
└─ Fall back → make install-dev (use pip)
```

______________________________________________________________________

**Remember**: UV is a drop-in replacement for pip. Most pip commands work with `uv pip` prefix!
