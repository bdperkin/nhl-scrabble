# How to Use UV Package Manager

Leverage UV for 10-100x faster package management.

## Problem

You want faster installation and dependency management.

## Solution

### Install UV

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Use UV for installation

```bash
# Clone repository
git clone https://github.com/bdperkin/nhl-scrabble.git
cd nhl-scrabble

# Install with UV (10x faster than pip)
make uv-init
source .venv/bin/activate
```

### UV with tox (automatic)

UV acceleration is automatic when using tox:

```bash
# Tox automatically uses UV via tox-uv plugin
make tox           # Fast with UV
make tox-parallel  # Even faster (10x speedup)
```

### Direct UV commands

```bash
# Install dependencies
uv pip install -r requirements.txt

# Install in editable mode
uv pip install -e .

# Sync dependencies from lock file
uv pip sync

# Update dependencies
uv pip install --upgrade -r requirements.txt
```

## Benefits

- **10-100x faster**: Installation and dependency resolution
- **Deterministic**: Lock file ensures reproducible installs
- **Compatible**: Drop-in replacement for pip
- **Reliable**: Better dependency resolution

## Related

- [Installation Guide](installation.md) - Installation methods
- [UV Ecosystem Explanation](../../docs/UV-ECOSYSTEM.md) - Why we use UV
- [Tox Reference](../../docs/TOX.md) - Tox with UV
