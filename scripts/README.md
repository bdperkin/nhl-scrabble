# Playwright Docker Wrappers for Fedora

Playwright does not officially support Fedora as a host OS. Browser engines like WebKit require system dependencies (`libjpeg-turbo8` and others) that are not available or compatible with Fedora's package management.

These wrapper scripts execute Playwright commands inside a custom Docker container hosted on GitHub Container Registry (GHCR), bypassing local dependency issues while maintaining full functionality.

## Custom Docker Image

The project maintains a custom Playwright Docker image at `ghcr.io/bdperkin/nhl-scrabble-playwright:latest`. This image:

- **Base**: Python 3.12 on Debian Bookworm
- **Pre-installed Browsers**: Chromium, Firefox, WebKit with all system dependencies
- **Pre-installed QA Dependencies**: pytest, pytest-playwright, httpx, locust, pillow, pixelmatch, pytest-benchmark, pytest-html, pytest-xdist, axe-playwright-python
- **User**: Runs as `pwuser` (non-root) for security
- **Size**: ~3.2 GB (all dependencies included)
- **Updates**: Rebuilt weekly via GitHub Actions to get latest Playwright and dependency versions
- **Source**: `.docker/Dockerfile` in repository

The image is automatically built and pushed to GHCR on:

- Pushes to main branch affecting `.docker/Dockerfile`
- Weekly schedule (Mondays at 6 AM UTC) for Playwright updates
- Manual workflow dispatch for custom builds

## Quick Start

```bash
# Install Playwright browsers in Docker container
./scripts/playwright install --with-deps chromium firefox webkit

# Run visual regression tests in Docker
./scripts/pytest-playwright qa/web/tests/visual/ --browser=chromium

# Generate baseline snapshots in Docker
./scripts/pytest-playwright qa/web/tests/visual/ --update-snapshots --browser=firefox
```

## Available Scripts

### 1. `build-playwright-image` - Build Custom Docker Image

Builds the custom Playwright Docker image for local testing or pushes to GHCR.

**Usage:**

```bash
# Build locally
./scripts/build-playwright-image

# Build and test
./scripts/build-playwright-image --test

# Build and push to GHCR (requires GITHUB_TOKEN)
GITHUB_TOKEN=$GH_TOKEN ./scripts/build-playwright-image --push
```

**Environment Variables:**

- `GITHUB_TOKEN` - GitHub Personal Access Token with `write:packages` scope (required for `--push`)
- `IMAGE_TAG` - Custom tag for the image (default: `latest`)

**Examples:**

```bash
# Build with custom tag
IMAGE_TAG=dev ./scripts/build-playwright-image

# Build, test, and push
GITHUB_TOKEN=$GH_TOKEN ./scripts/build-playwright-image --test --push
```

### 2. `playwright` - Playwright CLI Wrapper

Runs any Playwright CLI command in a Docker container.

**Usage:**

```bash
./scripts/playwright [playwright-args...]
```

**Examples:**

```bash
# Install all browsers with system dependencies
./scripts/playwright install --with-deps chromium firefox webkit

# Install specific browser
./scripts/playwright install chromium

# Check Playwright version
./scripts/playwright --version

# Run Playwright codegen
./scripts/playwright codegen http://localhost:5000
```

**Environment Variables:**

- `PLAYWRIGHT_IMAGE` - Docker image to use (default: `ghcr.io/bdperkin/nhl-scrabble-playwright:latest`)
- `PLAYWRIGHT_NO_PULL` - Skip pulling image if set to `true`

### 3. `pytest-playwright` - Pytest Wrapper for Playwright Tests

Runs pytest with Playwright tests in a Docker container.

**Usage:**

```bash
./scripts/pytest-playwright [pytest-args...]
```

**Examples:**

```bash
# Run all visual tests
./scripts/pytest-playwright qa/web/tests/visual/

# Run tests for specific browser
./scripts/pytest-playwright qa/web/tests/visual/ --browser=firefox

# Generate baseline snapshots
./scripts/pytest-playwright qa/web/tests/visual/ --update-snapshots

# Run with verbose output
./scripts/pytest-playwright qa/web/tests/visual/ -vv

# Run specific test file
./scripts/pytest-playwright qa/web/tests/visual/test_page_screenshots.py

# Run with maximum failures limit
./scripts/pytest-playwright qa/web/tests/visual/ --maxfail=3
```

**Prerequisites:**

- Web server must be running on `localhost:5000`
- Start server: `nhl-scrabble serve --host 0.0.0.0 --port 5000`

**Environment Variables:**

- `PLAYWRIGHT_IMAGE` - Docker image to use (default: `ghcr.io/bdperkin/nhl-scrabble-playwright:latest`)
- `PLAYWRIGHT_NO_PULL` - Skip pulling image if set to `true`
- `WEB_SERVER_URL` - Override web server URL (default: `http://localhost:5000`)

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Host (Fedora)                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Wrapper Script (scripts/playwright)            │   │
│  │  - Validates Docker is available                │   │
│  │  - Pulls GHCR Playwright image if needed        │   │
│  │  - Mounts repository (SELinux :z label)         │   │
│  │  - Forwards arguments to container              │   │
│  └──────────────────┬──────────────────────────────┘   │
│                     │                                   │
│  ┌──────────────────▼──────────────────────────────┐   │
│  │  Docker Container (Debian Bookworm)             │   │
│  │  ┌────────────────────────────────────────────┐ │   │
│  │  │  GHCR Image (pre-installed)                │ │   │
│  │  │  - Chromium, Firefox, WebKit               │ │   │
│  │  │  - System dependencies                     │ │   │
│  │  │  - All QA dependencies (pytest, etc.)      │ │   │
│  │  │  - Runs as root for Firefox compatibility  │ │   │
│  │  └────────────────────────────────────────────┘ │   │
│  │                                                  │   │
│  │  Volumes:                                        │   │
│  │  - /work ← Repository (read-write)              │   │
│  │  - Browser cache in image (/home/pwuser/.cache) │   │
│  │                                                  │   │
│  │  Network: host (access localhost:5000)          │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Key Features

**1. No Root-Owned Files**

- Container runs as your user ID (`--user $(id -u):$(id -g)`)
- Generated files (screenshots, reports) are owned by you
- No permission issues when accessing files

**2. Browser Cache Persistence**

- Browsers cached in `~/.cache/ms-playwright` on host
- Shared across container runs
- No need to re-download browsers

**3. Host Network Access**

- Container uses `--network host`
- Can access web server on `localhost:5000`
- No port mapping needed

**4. Working Directory Preservation**

- Script detects your current directory
- Maintains same relative path inside container
- Works seamlessly from any subdirectory

## Prerequisites

### System Requirements

**1. Docker**

Install Docker on Fedora:

```bash
# Install Docker
sudo dnf -y install dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
sudo dnf install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group (avoid sudo for docker commands)
sudo usermod -aG docker $USER
newgrp docker  # Or log out and back in
```

Verify Docker:

```bash
docker --version
docker run hello-world
```

**2. Disk Space**

- Playwright Docker image: ~2 GB
- Browser binaries: ~500 MB
- Total: ~2.5 GB minimum

### First-Time Setup

**1. Pull Playwright Python Image**

```bash
./scripts/playwright install --with-deps chromium firefox webkit
```

This will:

- Pull the official Playwright Python Docker image (~2 GB)
- Install Python Playwright package
- Install Chromium, Firefox, and WebKit browsers
- Install all system dependencies
- Cache browsers in `~/.cache/ms-playwright`

**2. Verify Installation**

```bash
# Check Playwright version
./scripts/playwright --version

# List installed browsers
ls -lh ~/.cache/ms-playwright/
```

## Usage Examples

### Visual Regression Testing Workflow

**1. Start Web Server**

```bash
# Terminal 1: Start web server
nhl-scrabble serve --host 0.0.0.0 --port 5000
```

**2. Run Visual Tests**

```bash
# Terminal 2: Run visual tests

# Run all visual tests (all browsers)
./scripts/pytest-playwright qa/web/tests/visual/

# Run tests for specific browser
./scripts/pytest-playwright qa/web/tests/visual/ --browser=chromium
./scripts/pytest-playwright qa/web/tests/visual/ --browser=firefox
./scripts/pytest-playwright qa/web/tests/visual/ --browser=webkit

# Generate baseline snapshots
./scripts/pytest-playwright qa/web/tests/visual/ --update-snapshots --browser=chromium

# Run with debugging
DEBUG=pw:api ./scripts/pytest-playwright qa/web/tests/visual/ --browser=firefox
```

### Playwright CLI Commands

**Browser Management:**

```bash
# Install specific browser
./scripts/playwright install chromium

# Install with system dependencies
./scripts/playwright install --with-deps webkit

# Install all browsers
./scripts/playwright install --with-deps chromium firefox webkit
```

**Code Generation:**

```bash
# Generate test code by recording interactions
./scripts/playwright codegen http://localhost:5000

# Generate test code for specific browser
./scripts/playwright codegen --browser=firefox http://localhost:5000
```

**Screenshots:**

```bash
# Capture screenshot (from inside container)
./scripts/playwright screenshot http://localhost:5000 screenshot.png
```

## Troubleshooting

### Docker Not Running

**Error:**

```
ERROR: Docker daemon is not running
```

**Solution:**

```bash
sudo systemctl start docker
sudo systemctl status docker
```

### Permission Denied

**Error:**

```
permission denied while trying to connect to the Docker daemon socket
```

**Solution:**

```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker  # Or log out and back in

# Verify
docker run hello-world
```

### Web Server Not Accessible

**Error:**

```
WARNING: Web server not detected on localhost:5000
```

**Solution:**

```bash
# Start web server with 0.0.0.0 binding (not 127.0.0.1)
nhl-scrabble serve --host 0.0.0.0 --port 5000

# Verify server is accessible
curl http://localhost:5000
```

### Image Pull Failures

**Error:**

```
ERROR: Failed to pull Docker image
```

**Solutions:**

```bash
# Check internet connection
curl -I https://mcr.microsoft.com

# Manually pull image
docker pull mcr.microsoft.com/playwright:v1.49.1-noble

# Check Docker Hub rate limits
docker system info | grep -i rate
```

### Browser Not Found

**Error:**

```
Browser not found
```

**Solution:**

```bash
# Reinstall browsers
./scripts/playwright install --with-deps chromium firefox webkit

# Verify browser cache
ls -lh ~/.cache/ms-playwright/
```

### File Permission Issues

**Symptoms:**

- Generated files owned by root
- Cannot modify snapshots

**Cause:**

- Container not running as current user

**Solution:**

- Wrapper scripts should automatically use `--user $(id -u):$(id -g)`
- If issue persists, check script has correct `--user` flag

### Snapshot Path Issues

**Error:**

```
Snapshot not found
```

**Cause:**

- Working directory mismatch between host and container

**Solution:**

```bash
# Run from qa/web directory (not repository root)
cd qa/web
../../scripts/pytest-playwright tests/visual/
```

## Advanced Usage

### Building Custom Docker Image Locally

For development or testing custom image changes:

```bash
# Build locally
docker build -f Dockerfile.playwright -t nhl-scrabble-playwright:local .

# Test locally-built image
PLAYWRIGHT_IMAGE=nhl-scrabble-playwright:local ./scripts/playwright --version

# Run tests with local image
PLAYWRIGHT_IMAGE=nhl-scrabble-playwright:local \
  ./scripts/pytest-playwright qa/web/tests/visual/
```

### Manually Pushing to GHCR

To manually build and push to GitHub Container Registry:

```bash
# Login to GHCR (use GitHub Personal Access Token with packages scope)
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Build and tag
docker build -f Dockerfile.playwright \
  -t ghcr.io/bdperkin/nhl-scrabble-playwright:latest \
  -t ghcr.io/bdperkin/nhl-scrabble-playwright:$(date +%Y-%m-%d) \
  .

# Push both tags
docker push ghcr.io/bdperkin/nhl-scrabble-playwright:latest
docker push ghcr.io/bdperkin/nhl-scrabble-playwright:$(date +%Y-%m-%d)
```

**Note**: GitHub Actions automatically builds and pushes the image. Manual pushes are only needed for emergency updates.

### Using Different Docker Images

Override the default GHCR image for testing:

```bash
# Use Microsoft's official image
PLAYWRIGHT_IMAGE=mcr.microsoft.com/playwright/python:latest \
  ./scripts/playwright --version

# Use specific version tag
PLAYWRIGHT_IMAGE=ghcr.io/bdperkin/nhl-scrabble-playwright:2026-04-29 \
  ./scripts/pytest-playwright qa/web/tests/visual/
```

### Skip Image Pull

Skip pulling image (faster if image already exists):

```bash
PLAYWRIGHT_NO_PULL=true ./scripts/playwright --version
```

### Override Web Server URL

Change web server URL for tests:

```bash
WEB_SERVER_URL=http://host.docker.internal:8080 \
  ./scripts/pytest-playwright qa/web/tests/visual/
```

### Debug Mode

Enable Playwright debugging:

```bash
# API debugging
DEBUG=pw:api ./scripts/pytest-playwright qa/web/tests/visual/

# Browser debugging
DEBUG=pw:browser ./scripts/pytest-playwright qa/web/tests/visual/

# Full debugging
DEBUG=pw:* ./scripts/pytest-playwright qa/web/tests/visual/
```

### Interactive Debugging

Use Playwright's inspector:

```bash
PWDEBUG=1 ./scripts/pytest-playwright qa/web/tests/visual/ \
  --browser=chromium \
  -k test_index_page_visual
```

## Comparison: Native vs Docker

| Feature                 | Native Install                  | Docker Wrapper (GHCR)         |
| ----------------------- | ------------------------------- | ----------------------------- |
| **Fedora Support**      | ❌ Not officially supported     | ✅ Works via Debian container |
| **System Dependencies** | ❌ Manual installation required | ✅ Pre-installed              |
| **WebKit Support**      | ❌ Requires libjpeg-turbo8      | ✅ Full support               |
| **Setup Complexity**    | ⚠️ High (dependency conflicts)  | ✅ Low (pull image)           |
| **Disk Space**          | ~500 MB (browsers only)         | ~2.5 GB (image + browsers)    |
| **Performance**         | ✅ Native speed                 | ⚠️ Slight overhead (~5%)      |
| **Isolation**           | ❌ System-wide installation     | ✅ Containerized              |
| **CI Consistency**      | ⚠️ Environment differences      | ✅ Identical environment      |
| **Image Source**        | N/A                             | Custom GHCR (auto-updated)    |
| **Playwright Updates**  | Manual pip install              | Weekly auto-rebuild           |

## Performance Considerations

**Docker Overhead:**

- Container startup: ~1-2 seconds
- Test execution: ~5% slower than native (negligible)
- Network: No overhead (host networking)
- Disk I/O: Minimal overhead (bind mounts)

**Optimization Tips:**

1. Keep Docker image pulled locally (`PLAYWRIGHT_NO_PULL=true`)
1. Use browser cache (automatically handled)
1. Run multiple tests in single pytest invocation
1. Use `--maxfail` to stop early on failures

**Benchmark (23 visual tests, chromium):**

- Native: ~15 seconds (if it worked)
- Docker wrapper: ~16 seconds (6.7% overhead)
- Acceptable tradeoff for compatibility

## CI/CD Integration

These wrapper scripts are designed for **local development on Fedora**. CI environments (GitHub Actions) use Ubuntu runners and can install Playwright natively:

**CI (GitHub Actions):**

```yaml
- name: Install Playwright browsers
  run: |
    playwright install --with-deps ${{ matrix.browser }}
```

**Local (Fedora):**

```bash
./scripts/playwright install --with-deps ${{ matrix.browser }}
```

## Maintenance

### Updating Playwright Version

**1. Check Latest Version**

```bash
# Check available images
docker search mcr.microsoft.com/playwright

# Check tags
# Visit: https://mcr.microsoft.com/v2/playwright/tags/list
```

**2. Update to Specific Version**

Use environment variable (no script changes needed):

```bash
# Use specific version
export PLAYWRIGHT_VERSION=1.50.0

# Pull and install
./scripts/playwright install --with-deps chromium firefox webkit
```

Or edit wrapper scripts for a permanent change:

```bash
# Edit scripts to change default version
vim scripts/playwright
vim scripts/pytest-playwright

# Change:
PLAYWRIGHT_VERSION="${PLAYWRIGHT_VERSION:-latest}"
# To:
PLAYWRIGHT_VERSION="${PLAYWRIGHT_VERSION:-1.50.0}"
```

**3. Pull New Image**

```bash
# Pull updated image
PLAYWRIGHT_VERSION=1.50.0 ./scripts/playwright --version

# Reinstall browsers
PLAYWRIGHT_VERSION=1.50.0 ./scripts/playwright install --with-deps chromium firefox webkit
```

**4. Test**

```bash
# Verify version
./scripts/playwright --version

# Run tests
./scripts/pytest-playwright qa/web/tests/visual/
```

### Cleaning Up

**Remove Old Docker Images:**

```bash
# List Playwright images
docker images | grep playwright

# Remove specific version
docker rmi mcr.microsoft.com/playwright:v1.48.0-noble

# Remove all unused images
docker image prune -a
```

**Clear Browser Cache:**

```bash
# Remove cached browsers
rm -rf ~/.cache/ms-playwright/

# Reinstall
./scripts/playwright install --with-deps chromium firefox webkit
```

**Full Cleanup:**

```bash
# Remove all Docker images
docker image prune -a

# Remove browser cache
rm -rf ~/.cache/ms-playwright/

# Restart fresh
./scripts/playwright install --with-deps chromium firefox webkit
```

## Resources

**Official Documentation:**

- [Playwright Docker Documentation](https://playwright.dev/docs/docker)
- [Playwright CLI](https://playwright.dev/docs/cli)
- [Microsoft Playwright Docker Images](https://mcr.microsoft.com/product/playwright/about)

**Docker Documentation:**

- [Docker Get Started](https://docs.docker.com/get-started/)
- [Docker on Fedora](https://docs.docker.com/engine/install/fedora/)
- [Docker Volumes](https://docs.docker.com/storage/volumes/)

**Troubleshooting:**

- [Playwright Troubleshooting](https://playwright.dev/docs/troubleshooting)
- [Docker Troubleshooting](https://docs.docker.com/config/daemon/troubleshoot/)

## Support

For issues with these wrapper scripts:

- Open an issue: https://github.com/bdperkin/nhl-scrabble/issues
- Tag with: `playwright`, `docker`, `fedora`

For Playwright issues:

- Playwright GitHub: https://github.com/microsoft/playwright
- Playwright Discord: https://aka.ms/playwright/discord
