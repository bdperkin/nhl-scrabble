# Docker Playwright Quick Reference

Fast reference for common Docker Playwright tasks.

______________________________________________________________________

## Daily Usage

```bash
# Run Playwright command
./scripts/playwright --version
./scripts/playwright install webkit

# Run visual tests
./scripts/pytest-playwright qa/web/tests/visual/

# Run with specific browser
./scripts/pytest-playwright qa/web/tests/visual/ --browser=firefox

# Generate baselines
./scripts/pytest-playwright qa/web/tests/visual/ --update-snapshots
```

______________________________________________________________________

## Local Development

```bash
# Build image locally
./scripts/build-playwright-image

# Build and test
./scripts/build-playwright-image --test

# Build and push to GHCR (requires GITHUB_TOKEN)
GITHUB_TOKEN=$GH_TOKEN ./scripts/build-playwright-image --push
```

______________________________________________________________________

## Troubleshooting

```bash
# Force pull latest image
docker pull ghcr.io/bdperkin/nhl-scrabble-playwright:latest

# Test with locally-built image
PLAYWRIGHT_IMAGE=nhl-scrabble-playwright:latest ./scripts/playwright --version

# Test with Microsoft's image (fallback)
PLAYWRIGHT_IMAGE=mcr.microsoft.com/playwright/python:latest ./scripts/playwright --version

# Check if Docker is running
docker info

# Check image size
docker images ghcr.io/bdperkin/nhl-scrabble-playwright

# Remove old images
docker rmi ghcr.io/bdperkin/nhl-scrabble-playwright:2026-04-20
```

______________________________________________________________________

## Environment Variables

```bash
# Use different image
PLAYWRIGHT_IMAGE=mcr.microsoft.com/playwright/python:latest

# Skip pulling image (faster if already cached)
PLAYWRIGHT_NO_PULL=true

# Override web server URL
WEB_SERVER_URL=http://localhost:8080
```

______________________________________________________________________

## Common Commands

### Install Browsers

```bash
# All browsers
./scripts/playwright install chromium firefox webkit

# Single browser
./scripts/playwright install webkit

# With system dependencies (not needed - already in image)
./scripts/playwright install --with-deps webkit
```

### Run Tests

```bash
# All tests, all browsers
./scripts/pytest-playwright qa/web/tests/visual/

# Specific browser
./scripts/pytest-playwright qa/web/tests/visual/ --browser=chromium

# With verbose output
./scripts/pytest-playwright qa/web/tests/visual/ -vv

# Stop on first failure
./scripts/pytest-playwright qa/web/tests/visual/ --maxfail=1

# Specific test file
./scripts/pytest-playwright qa/web/tests/visual/test_page_screenshots.py
```

### Generate Baselines

```bash
# All browsers
./scripts/pytest-playwright qa/web/tests/visual/ --update-snapshots

# Specific browser
./scripts/pytest-playwright qa/web/tests/visual/ \
  --update-snapshots \
  --browser=webkit

# Verify baselines
find qa/web/tests/visual/__snapshots__/ -name "*.png" | wc -l
```

______________________________________________________________________

## Image Information

- **Location**: `ghcr.io/bdperkin/nhl-scrabble-playwright:latest`
- **Base**: Python 3.12 on Debian Bookworm
- **Size**: ~2.5 GB
- **Updates**: Weekly (Mondays 6 AM UTC)
- **Browsers**: Chromium, Firefox, WebKit
- **User**: pwuser (UID/GID overridden at runtime)

______________________________________________________________________

## Key Files

- **Dockerfile**: `Dockerfile.playwright`
- **Build Workflow**: `.github/workflows/docker-playwright.yml`
- **Build Script**: `scripts/build-playwright-image`
- **Wrapper Scripts**: `scripts/playwright`, `scripts/pytest-playwright`
- **Documentation**: `scripts/README.md`, `DOCKER-IMAGE-APPROACH.md`

______________________________________________________________________

## Getting Help

```bash
# Wrapper script help
./scripts/build-playwright-image --help
./scripts/playwright --help
./scripts/pytest-playwright --help

# Playwright help
./scripts/playwright --version
./scripts/playwright --help

# Pytest help
./scripts/pytest-playwright --help
```

______________________________________________________________________

## Quick Diagnostics

```bash
# Check Docker status
docker info

# Check image exists
docker images ghcr.io/bdperkin/nhl-scrabble-playwright

# Test image
docker run --rm ghcr.io/bdperkin/nhl-scrabble-playwright:latest \
  playwright --version

# Check browsers in image
docker run --rm ghcr.io/bdperkin/nhl-scrabble-playwright:latest \
  bash -c "ls -la /home/pwuser/.cache/ms-playwright/"

# Check web server running
curl -I http://localhost:5000

# Check browser cache on host
ls -la ~/.cache/ms-playwright/
```

______________________________________________________________________

## Emergency Procedures

### Rollback to Microsoft Image

```bash
# Temporary (one command)
PLAYWRIGHT_IMAGE=mcr.microsoft.com/playwright/python:latest \
  ./scripts/playwright --version

# Permanent (revert wrapper scripts)
git checkout origin/main -- scripts/playwright scripts/pytest-playwright
```

### Rebuild Image (Emergency Update)

```bash
# Rebuild locally
./scripts/build-playwright-image

# Push to GHCR
GITHUB_TOKEN=$GH_TOKEN ./scripts/build-playwright-image --push

# Or trigger GitHub Actions manually
gh workflow run docker-playwright.yml
```

### Clear All Docker Cache

```bash
# Nuclear option - removes ALL Docker images/containers
docker system prune -a
docker volume prune

# Then rebuild
./scripts/build-playwright-image
```

______________________________________________________________________

## Performance Tips

1. **Keep image cached**: Don't prune GHCR image unless necessary
1. **Use `PLAYWRIGHT_NO_PULL=true`**: Skip pull check if image cached
1. **Parallel tests**: Use `pytest -n auto` for parallel execution
1. **Limit browsers**: Test one browser at a time during development
1. **Reuse containers**: Wrapper scripts already use `--rm`, but avoid manual `docker run` loops

______________________________________________________________________

## See Also

- **Full documentation**: `scripts/README.md`
- **Technical details**: `DOCKER-IMAGE-APPROACH.md`
- **Implementation summary**: `CUSTOM-DOCKER-IMAGE-SUMMARY.md`
- **Playwright docs**: https://playwright.dev/docs/docker
- **GHCR docs**: https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
