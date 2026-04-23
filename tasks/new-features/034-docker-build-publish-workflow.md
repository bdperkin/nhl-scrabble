# Docker Container Build and Publish Workflow

**GitHub Issue**: #301 - https://github.com/bdperkin/nhl-scrabble/issues/301

**Parent Task**: enhancement/022-comprehensive-github-workflows.md (#298)

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

3-4 hours

## Description

Implement automated Docker container build and publish workflow that creates multi-platform container images (amd64, arm64), runs security scans, and publishes to GitHub Container Registry (GHCR) on pushes and tags. Enables containerized deployments and easier testing.

## Current State

**No Container Support:**

Currently, the project has no Docker support:

```bash
# Users must install locally
pip install nhl-scrabble
nhl-scrabble analyze

# No containerized option available
```

**Problems:**

- ❌ No containerized deployment option
- ❌ Environment inconsistencies
- ❌ Harder to test in isolated environments
- ❌ No multi-platform support
- ❌ Missing modern deployment option

**Existing:**

- ✅ Python package works well
- ✅ Clear dependencies in pyproject.toml
- ❌ No Dockerfile
- ❌ No container workflow
- ❌ No container registry configured

## Proposed Solution

### Container Workflow

Create `.github/workflows/docker.yml`:

```yaml
name: Docker Build and Publish

on:
  push:
    branches:
      - main
    tags:
      - v*
    paths:
      - src/**
      - pyproject.toml
      - Dockerfile
      - .github/workflows/docker.yml
  pull_request:
    paths:
      - Dockerfile
      - .github/workflows/docker.yml
  workflow_dispatch:

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

permissions:
  contents: read
  packages: write  # For GHCR push

jobs:
  build-and-push:
    name: Build and Push Docker Image
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v6

      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GitHub Container Registry
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            # Tag as 'latest' on main branch
            type=raw,value=latest,enable={{is_default_branch}}
            # Tag with version on tags (v1.2.3 -> 1.2.3)
            type=semver,pattern={{version}}
            # Tag with major.minor on tags (v1.2.3 -> 1.2)
            type=semver,pattern={{major}}.{{minor}}
            # Tag with major on tags (v1.2.3 -> 1)
            type=semver,pattern={{major}}
            # Tag with SHA for traceability
            type=sha,prefix={{branch}}-

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          build-args: |
            VERSION=${{ steps.meta.outputs.version }}

      - name: Run Trivy security scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{
            steps.meta.outputs.version }}
          format: sarif
          output: trivy-results.sarif

      - name: Upload Trivy results to GitHub Security
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: trivy-results.sarif

      - name: Generate SBOM
        uses: anchore/sbom-action@v0
        with:
          image: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{
            steps.meta.outputs.version }}
          format: spdx-json
          output-file: sbom-spdx.json

      - name: Upload SBOM
        uses: actions/upload-artifact@v4
        with:
          name: docker-sbom
          path: sbom-spdx.json
          retention-days: 90
```

### Dockerfile

Create optimized multi-stage Dockerfile:

```dockerfile
# syntax=docker/dockerfile:1

# Build stage
FROM python:3.12-slim as builder

WORKDIR /build

# Install UV for fast dependency installation
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv pip install --system --no-cache .

# Runtime stage
FROM python:3.12-slim

# Set labels
LABEL org.opencontainers.image.source=https://github.com/bdperkin/nhl-scrabble
LABEL org.opencontainers.image.description="NHL Roster Scrabble Score Analyzer"
LABEL org.opencontainers.image.licenses=MIT

# Create non-root user
RUN useradd -m -u 1000 nhlscrabble && \
    mkdir -p /home/nhlscrabble/.cache && \
    chown -R nhlscrabble:nhlscrabble /home/nhlscrabble

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=nhlscrabble:nhlscrabble src/ /app/src/
COPY --chown=nhlscrabble:nhlscrabble pyproject.toml /app/

WORKDIR /app

# Install package in editable mode
RUN pip install --no-deps -e .

# Switch to non-root user
USER nhlscrabble

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV NHL_SCRABBLE_CACHE_DIR=/home/nhlscrabble/.cache/nhl-scrabble

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD nhl-scrabble --version || exit 1

# Default command
ENTRYPOINT ["nhl-scrabble"]
CMD ["--help"]
```

### .dockerignore

Create `.dockerignore` to optimize build:

```
# Git
.git
.gitignore
.gitattributes

# Python
__pycache__
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.tox/
.coverage
.coverage.*
.cache
.pytest_cache/
htmlcov/

# Documentation
docs/_build/
docs/.DS_Store

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# CI
.github/
.pre-commit-config.yaml

# Other
*.md
!README.md
LICENSE
CHANGELOG.md
```

## Implementation Steps

1. **Create Dockerfile** (1h)

   - Write multi-stage Dockerfile
   - Optimize for size and security
   - Add health check
   - Use non-root user
   - Test local build

1. **Create .dockerignore** (15min)

   - List files to exclude
   - Optimize build context size

1. **Create Workflow File** (1h)

   - Set up QEMU for multi-platform
   - Configure Buildx
   - Add metadata extraction
   - Configure caching

1. **Add Security Scanning** (30min)

   - Integrate Trivy scanner
   - Upload results to Security tab
   - Generate SBOM

1. **Test Workflow** (1-1.5h)

   - Test PR builds (no push)
   - Test main branch builds
   - Test tag builds
   - Verify multi-platform
   - Test security scan
   - Verify GHCR publication

1. **Create Documentation** (30min)

   - Add Docker usage to README
   - Document image tags
   - Add examples
   - Document GHCR location

## Testing Strategy

### Local Docker Testing

```bash
# Build locally
docker build -t nhl-scrabble:test .

# Check image size
docker images nhl-scrabble:test

# Run container
docker run --rm nhl-scrabble:test --version
docker run --rm nhl-scrabble:test --help
docker run --rm nhl-scrabble:test analyze

# Test with volume mount (for output)
docker run --rm -v $(pwd)/output:/output nhl-scrabble:test analyze --output /output/report.txt

# Test interactive
docker run -it --rm nhl-scrabble:test /bin/bash
```

### Multi-Platform Testing

```bash
# Build for specific platform
docker buildx build --platform linux/amd64 -t nhl-scrabble:amd64 .
docker buildx build --platform linux/arm64 -t nhl-scrabble:arm64 .

# Build for both platforms
docker buildx build --platform linux/amd64,linux/arm64 -t nhl-scrabble:multi .
```

### Security Scanning

```bash
# Run Trivy locally
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image nhl-scrabble:test

# Check for high/critical vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image --severity HIGH,CRITICAL nhl-scrabble:test
```

### GHCR Pull Testing

```bash
# Pull from GHCR
docker pull ghcr.io/bdperkin/nhl-scrabble:latest

# Run pulled image
docker run --rm ghcr.io/bdperkin/nhl-scrabble:latest --version

# Pull specific version
docker pull ghcr.io/bdperkin/nhl-scrabble:2.1.0
```

## Acceptance Criteria

- [ ] Dockerfile created and optimized
- [ ] .dockerignore created
- [ ] Workflow file created: `.github/workflows/docker.yml`
- [ ] Multi-platform support (amd64, arm64)
- [ ] Builds on pushes to main
- [ ] Builds on version tags
- [ ] Builds on PRs (test only, no push)
- [ ] Publishes to GHCR
- [ ] Image tagged with `latest` on main
- [ ] Image tagged with version on tags
- [ ] Security scanning with Trivy
- [ ] SBOM generation
- [ ] Non-root user configured
- [ ] Health check included
- [ ] Build caching working
- [ ] Documentation updated (README, Docker usage)
- [ ] Local testing completed
- [ ] GHCR publication verified
- [ ] Multi-platform images verified

## Related Files

**New Files:**

- `Dockerfile` - Container image definition
- `.dockerignore` - Build context exclusions
- `.github/workflows/docker.yml` - Container workflow

**Modified Files:**

- `README.md` - Add Docker usage section
- `CLAUDE.md` - Document container workflow
- `docs/tutorials/01-getting-started.md` - Add Docker option

## Dependencies

**Task Dependencies:**

- **Optional**: Can be implemented independently
- **Enhances**: Provides alternative deployment method

**Tool Dependencies:**

- Docker Buildx - Multi-platform builds
- QEMU - Cross-platform emulation
- Trivy - Security scanning
- GitHub Container Registry - Image hosting

**GitHub Actions:**

- `docker/setup-qemu-action@v3`
- `docker/setup-buildx-action@v3`
- `docker/login-action@v3`
- `docker/metadata-action@v5`
- `docker/build-push-action@v5`
- `aquasecurity/trivy-action@master`
- `anchore/sbom-action@v0`

## Additional Notes

### Image Tags

**On main branch:**

- `ghcr.io/bdperkin/nhl-scrabble:latest`
- `ghcr.io/bdperkin/nhl-scrabble:main-<sha>`

**On version tag (v2.1.0):**

- `ghcr.io/bdperkin/nhl-scrabble:2.1.0`
- `ghcr.io/bdperkin/nhl-scrabble:2.1`
- `ghcr.io/bdperkin/nhl-scrabble:2`
- `ghcr.io/bdperkin/nhl-scrabble:latest`

### Usage Examples

**Basic usage:**

```bash
docker run --rm ghcr.io/bdperkin/nhl-scrabble:latest analyze
```

**With output file:**

```bash
docker run --rm -v $(pwd):/output \
  ghcr.io/bdperkin/nhl-scrabble:latest \
  analyze --output /output/report.txt
```

**With environment variables:**

```bash
docker run --rm \
  -e NHL_SCRABBLE_VERBOSE=true \
  -e NHL_SCRABBLE_TOP_PLAYERS=50 \
  ghcr.io/bdperkin/nhl-scrabble:latest analyze
```

**Interactive mode:**

```bash
docker run -it --rm ghcr.io/bdperkin/nhl-scrabble:latest /bin/bash
```

### Image Optimization

**Size optimizations:**

- Multi-stage build (builder + runtime)
- Python slim base image (~150MB vs ~1GB full)
- UV for fast dependency installation
- .dockerignore to reduce context
- No cache directories included

**Expected image size:** ~200-250MB

### Security Features

- Non-root user (UID 1000)
- Minimal base image
- Regular security scans
- SBOM generation
- No secrets in image
- Read-only application code

### Performance

**Build times:**

- Initial build: ~3-5 minutes
- Cached build: ~30 seconds
- Multi-platform build: ~5-7 minutes

**Registry:**

- GHCR is free for public repositories
- Unlimited bandwidth
- Fast CDN-backed pulls
- Integrated with GitHub

### Future Enhancements

- Docker Compose for web interface
- ARM32 support (Raspberry Pi)
- Alpine-based variant (smaller)
- Distroless variant (more secure)
- Docker Hub publication
- Amazon ECR publication

## Implementation Notes

*To be filled during implementation:*

- Date started:
- Date completed:
- Actual effort:
- Final image size:
- Build time:
- Security scan results:
- Multi-platform test results:
