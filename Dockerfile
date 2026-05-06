# syntax=docker/dockerfile:1

# Build stage
FROM python:3.12-slim AS builder

# Accept version as build argument (provided by workflow or default to 0.0.0+dev)
ARG VERSION=0.0.0+dev

WORKDIR /build

# Install UV for fast dependency installation
RUN pip install --no-cache-dir uv

# Copy source code and dependency files
COPY . .

# Install package with all dependencies
# Set version for hatch-vcs (which expects git history) inline
RUN SETUPTOOLS_SCM_PRETEND_VERSION=${VERSION} \
    uv pip install --system --no-cache .

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

# Copy installed packages from builder (including nhl-scrabble)
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app

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
