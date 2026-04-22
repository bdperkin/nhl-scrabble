"""Playwright configuration for web automation tests."""

# Playwright configuration
config = {
    "base_url": "http://localhost:5000",
    "timeout": 30000,
    "screenshot_on_failure": True,
    "video_on_failure": True,
    "trace_on_failure": True,
}

BROWSERS = ["chromium", "firefox", "webkit"]
HEADLESS = True
SLOW_MO = 0  # Slow down by N ms for debugging
