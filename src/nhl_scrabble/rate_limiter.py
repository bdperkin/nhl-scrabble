"""Rate limiting for API requests.

This module provides a token bucket rate limiter for controlling API request rates. The rate limiter
is thread-safe and supports both blocking and non-blocking modes.
"""

import threading
import time
from typing import Any


class RateLimiter:
    """Token bucket rate limiter for API requests.

    Limits requests to a maximum rate while allowing bursts.
    Thread-safe for concurrent use.

    The token bucket algorithm works by:
    1. Maintaining a bucket of tokens (max: burst_size)
    2. Refilling tokens at a fixed rate (max_requests / time_window per second)
    3. Each request consumes 1 token
    4. Blocking when bucket is empty

    Args:
        max_requests: Maximum requests allowed per time window
        time_window: Time window in seconds (default: 60s = 1 minute)
        burst_size: Maximum burst size (default: max_requests)

    Examples:
        >>> limiter = RateLimiter(max_requests=30, time_window=60.0)
        >>> limiter.acquire()  # Blocks until token available
        True
        >>> limiter.acquire(block=False)  # Non-blocking mode
        True
    """

    def __init__(
        self,
        max_requests: int = 30,
        time_window: float = 60.0,
        burst_size: int | None = None,
    ) -> None:
        """Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed per time window
            time_window: Time window in seconds (default: 60s = 1 minute)
            burst_size: Max burst size (default: max_requests)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.burst_size = burst_size if burst_size is not None else max_requests

        # Token bucket state
        self.tokens = float(self.burst_size)
        self.last_update = time.monotonic()

        # Thread safety
        self.lock = threading.Lock()

        # Metrics
        self.total_requests = 0
        self.total_waits = 0
        self.total_wait_time = 0.0

    @property
    def refill_rate(self) -> float:
        """Calculate token refill rate (tokens per second).

        Returns:
            Number of tokens that refill per second.
        """
        return self.max_requests / self.time_window

    def _refill_tokens(self) -> None:
        """Refill tokens based on time elapsed since last update.

        This method should only be called while holding self.lock.
        """
        now = time.monotonic()
        elapsed = now - self.last_update

        # Add tokens based on elapsed time
        self.tokens = min(self.burst_size, self.tokens + (elapsed * self.refill_rate))

        self.last_update = now

    def acquire(self, tokens: int = 1, block: bool = True) -> bool:
        """Acquire tokens from bucket.

        Args:
            tokens: Number of tokens to acquire (default: 1)
            block: Whether to block until tokens available (default: True)

        Returns:
            True if tokens acquired, False if not available (non-blocking only)

        Examples:
            >>> limiter = RateLimiter(max_requests=10, time_window=60.0)
            >>> limiter.acquire()  # Blocking acquire
            True
            >>> limiter.acquire(block=False)  # Non-blocking acquire
            True
        """
        with self.lock:
            self._refill_tokens()

            # Check if tokens available
            if self.tokens >= tokens:
                self.tokens -= tokens
                self.total_requests += 1
                return True

            # Non-blocking mode
            if not block:
                return False

            # Calculate wait time
            deficit = tokens - self.tokens
            wait_time = deficit / self.refill_rate

            # Update metrics
            self.total_waits += 1
            self.total_wait_time += wait_time

        # Wait outside lock to allow other threads to proceed
        time.sleep(wait_time)

        # Try again after waiting
        with self.lock:
            self._refill_tokens()
            self.tokens -= tokens
            self.total_requests += 1
            return True

    def get_stats(self) -> dict[str, Any]:
        """Get rate limiter statistics.

        Returns:
            Dictionary with statistics:
                - total_requests: Total requests made
                - total_waits: Total times waited for tokens
                - total_wait_time: Total time spent waiting
                - average_wait: Average wait time per wait
                - current_tokens: Current token count
                - max_tokens: Maximum token capacity

        Examples:
            >>> limiter = RateLimiter(max_requests=30, time_window=60.0)
            >>> limiter.acquire()
            True
            >>> stats = limiter.get_stats()
            >>> stats["total_requests"]
            1
        """
        with self.lock:
            return {
                "total_requests": self.total_requests,
                "total_waits": self.total_waits,
                "total_wait_time": self.total_wait_time,
                "average_wait": (
                    self.total_wait_time / self.total_waits if self.total_waits > 0 else 0.0
                ),
                "current_tokens": self.tokens,
                "max_tokens": self.burst_size,
            }

    def reset(self) -> None:  # noqa: vulture
        """Reset rate limiter to initial state.

        Useful for testing or resetting quota usage.

        Examples:
            >>> limiter = RateLimiter(max_requests=1, time_window=60.0)
            >>> limiter.acquire()
            True
            >>> limiter.acquire(block=False)  # No tokens left
            False
            >>> limiter.reset()
            >>> limiter.acquire(block=False)  # Tokens restored
            True
        """
        with self.lock:
            self.tokens = float(self.burst_size)
            self.last_update = time.monotonic()
            self.total_requests = 0
            self.total_waits = 0
            self.total_wait_time = 0.0
