# Playwright Docker Image for NHL Scrabble QA
#
# This image provides a consistent testing environment with Playwright browsers
# and all system dependencies pre-installed. It's specifically designed for
# visual regression testing and end-to-end testing of the NHL Scrabble web interface.
#
# Base: Python 3.12 on Debian Bookworm
# Includes: Playwright, all browsers (chromium, firefox, webkit), system dependencies
# User: pwuser (non-root) for security
#
# Build:
#   docker build -f Dockerfile.playwright -t ghcr.io/bdperkin/nhl-scrabble-playwright:latest .
#
# Run:
#   docker run --rm -it ghcr.io/bdperkin/nhl-scrabble-playwright:latest /bin/bash

FROM python:3.12-bookworm

LABEL org.opencontainers.image.source="https://github.com/bdperkin/nhl-scrabble"
LABEL org.opencontainers.image.description="Playwright testing environment for NHL Scrabble"
LABEL org.opencontainers.image.licenses="MIT"

# Install Playwright and QA test dependencies
# All test dependencies are pre-installed in the image to avoid
# reinstalling them on every CI run, making workflows faster and simpler.
RUN pip install --no-cache-dir \
    playwright \
    axe-playwright-python>=0.1.7 \
    httpx>=0.28 \
    locust>=2.43.4 \
    pillow>=12.2 \
    pixelmatch>=0.2.3 \
    pytest>=9.0.3 \
    pytest-benchmark>=5.2.3 \
    pytest-html>=4.2 \
    pytest-playwright>=0.7.2 \
    pytest-playwright-snapshot>=1 \
    pytest-xdist>=3.8

# Install system dependencies for browsers (requires root)
# This installs all OS packages needed for chromium, firefox, and webkit
RUN playwright install-deps chromium firefox webkit

# Create non-root user for running tests securely
# pwuser is the conventional Playwright user
RUN useradd -m -s /bin/bash pwuser && \
    mkdir -p /home/pwuser/.cache/ms-playwright && \
    chown -R pwuser:pwuser /home/pwuser

# Switch to non-root user
USER pwuser

# Install browsers as pwuser (system deps already installed above)
# This downloads and caches browsers in /home/pwuser/.cache/ms-playwright/
RUN playwright install chromium firefox webkit

# Set working directory
WORKDIR /home/pwuser

# Default command: show Playwright version
CMD ["playwright", "--version"]
