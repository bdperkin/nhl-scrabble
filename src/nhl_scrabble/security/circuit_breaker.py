"""Circuit breaker pattern for DoS prevention.

This module implements the circuit breaker pattern to prevent cascading failures
and protect against degraded services. The circuit breaker has three states:

- CLOSED: Normal operation, requests pass through
- OPEN: Failing, requests are rejected immediately
- HALF_OPEN: Testing recovery, limited requests allowed
"""

import logging
import time
from collections.abc import Callable
from enum import Enum
from typing import Any, TypeVar

from nhl_scrabble.exceptions import CircuitBreakerOpenError

logger = logging.getLogger(__name__)

T = TypeVar("T")

__all__ = [
    "CircuitBreaker",
    "CircuitBreakerOpenError",
    "CircuitState",
]


class CircuitState(Enum):
    """Circuit breaker states.

    Attributes:
        CLOSED: Normal operation - requests pass through
        OPEN: Failure mode - requests are rejected immediately
        HALF_OPEN: Recovery testing - limited requests allowed to test if service recovered
    """

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker for preventing cascading failures.

    The circuit breaker monitors failures and transitions between states:
    - CLOSED → OPEN: After failure_threshold consecutive failures
    - OPEN → HALF_OPEN: After timeout period expires
    - HALF_OPEN → CLOSED: After a successful request
    - HALF_OPEN → OPEN: After any failure

    Attributes:
        failure_threshold: Number of failures before opening circuit
        timeout: Seconds to wait before attempting recovery (OPEN → HALF_OPEN)
        expected_exception: Exception type(s) to catch and count as failures
        failure_count: Current count of consecutive failures
        last_failure_time: Timestamp of last failure (for timeout calculation)
        state: Current circuit state
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        expected_exception: type[Exception] | tuple[type[Exception], ...] = Exception,
    ) -> None:
        """Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before circuit opens (default: 5)
            timeout: Seconds to wait before testing recovery (default: 60.0)
            expected_exception: Exception type(s) to catch as failures (default: Exception)

        Examples:
            >>> from requests import RequestException
            >>> cb = CircuitBreaker(failure_threshold=3, timeout=30.0)
            >>> cb.state
            <CircuitState.CLOSED: 'closed'>
        """
        if failure_threshold < 1:
            msg = f"failure_threshold must be >= 1, got {failure_threshold}"
            raise ValueError(msg)
        if timeout < 0:
            msg = f"timeout must be >= 0, got {timeout}"
            raise ValueError(msg)

        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time: float | None = None
        self.state = CircuitState.CLOSED

    def _on_success(self) -> None:
        """Handle successful request - reset failure count and close circuit."""
        if self.state == CircuitState.HALF_OPEN:
            logger.info("Circuit breaker transitioning from HALF_OPEN to CLOSED after success")

        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self) -> None:
        """Handle failed request - increment failure count and potentially open circuit."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            # Any failure in HALF_OPEN state immediately opens circuit
            logger.warning(
                f"Circuit breaker transitioning from HALF_OPEN to OPEN "
                f"after failure (total: {self.failure_count})"
            )
            self.state = CircuitState.OPEN

        elif self.failure_count >= self.failure_threshold:
            # Threshold reached in CLOSED state
            logger.warning(
                f"Circuit breaker transitioning from CLOSED to OPEN "
                f"after {self.failure_count} failures (threshold: {self.failure_threshold})"
            )
            self.state = CircuitState.OPEN

    def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Positional arguments to pass to function
            **kwargs: Keyword arguments to pass to function

        Returns:
            Function result if successful

        Raises:
            CircuitBreakerOpenError: If circuit is OPEN and rejecting requests
            Any exception raised by func: If function fails

        Examples:
            >>> cb = CircuitBreaker(failure_threshold=3)
            >>> result = cb.call(lambda x: x * 2, 5)
            >>> result
            10
        """
        # Check if circuit should transition from OPEN to HALF_OPEN
        if self.state == CircuitState.OPEN:
            if self.last_failure_time is not None:
                time_since_failure = time.time() - self.last_failure_time
                if time_since_failure >= self.timeout:
                    logger.info(
                        f"Circuit breaker transitioning from OPEN to HALF_OPEN "
                        f"after {time_since_failure:.1f}s timeout"
                    )
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker is OPEN (failed {self.failure_count} times, "
                        f"retry in {self.timeout - time_since_failure:.1f}s)"
                    )
            else:
                # Should not happen, but handle gracefully
                logger.warning("Circuit breaker OPEN but no last_failure_time set")
                self.state = CircuitState.HALF_OPEN

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception:
            self._on_failure()
            raise

    def reset(self) -> None:
        """Manually reset circuit breaker to CLOSED state.

        Useful for testing or manual intervention.
        """
        logger.info(
            f"Circuit breaker manually reset from {self.state.value} "
            f"(had {self.failure_count} failures)"
        )
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    @property
    def is_open(self) -> bool:
        """Check if circuit is currently OPEN.

        Returns:
            True if circuit is OPEN, False otherwise
        """
        return self.state == CircuitState.OPEN

    @property
    def is_closed(self) -> bool:
        """Check if circuit is currently CLOSED.

        Returns:
            True if circuit is CLOSED, False otherwise
        """
        return self.state == CircuitState.CLOSED

    def __repr__(self) -> str:
        """Return string representation of circuit breaker state."""
        return (
            f"CircuitBreaker(state={self.state.value}, "
            f"failures={self.failure_count}/{self.failure_threshold}, "
            f"timeout={self.timeout}s)"
        )
