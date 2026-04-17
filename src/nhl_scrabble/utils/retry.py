"""Retry decorator with exponential backoff and jitter."""

import logging
import random
import time
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


def retry(
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    max_backoff: float = 30.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    on_retry: Callable[[Exception, int], None] | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Retry a function with exponential backoff and jitter.

    Retries a function when it raises specified exceptions,
    using exponential backoff with jitter to space out retry attempts.

    Args:
        max_attempts: Maximum number of attempts (default: 3)
        backoff_factor: Multiplier for exponential backoff (default: 2.0)
        max_backoff: Maximum backoff delay in seconds (default: 30.0)
        exceptions: Tuple of exceptions to catch and retry (default: all)
        on_retry: Optional callback function called on retry (exception, attempt)

    Returns:
        Decorated function with retry logic

    Examples:
        Basic retry with default settings:
        >>> @retry(max_attempts=5)
        ... def fetch_data():
        ...     return requests.get("https://api.example.com")

        Retry specific exceptions only:
        >>> @retry(max_attempts=5, exceptions=(requests.RequestException,))
        ... def fetch_data():
        ...     return requests.get("https://api.example.com")

        Custom backoff and callback:
        >>> def log_retry(exc, attempt):
        ...     print(f"Retry {attempt}: {exc}")
        >>> @retry(max_attempts=3, backoff_factor=3.0, on_retry=log_retry)
        ... def operation():
        ...     return perform_operation()
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        """Wrap the target function with retry logic."""

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            """Execute function with retry logic on exceptions."""
            # Handle edge case: max_attempts < 1
            if max_attempts < 1:
                msg = f"{func.__name__} called with max_attempts={max_attempts} < 1"
                raise RuntimeError(msg)

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    # Last attempt - don't retry
                    if attempt == max_attempts - 1:
                        logger.error(f"{func.__name__} failed after {max_attempts} attempts: {e}")
                        raise

                    # Calculate backoff delay with jitter
                    delay = _calculate_backoff_delay(
                        attempt=attempt,
                        backoff_factor=backoff_factor,
                        max_backoff=max_backoff,
                    )

                    # Log retry
                    logger.warning(
                        f"{func.__name__} failed on attempt {attempt + 1}/{max_attempts}: {e}, "
                        f"retrying in {delay:.2f}s"
                    )

                    # Call callback if provided
                    if on_retry:
                        on_retry(e, attempt + 1)

                    # Wait before retry
                    time.sleep(delay)

            # Should never reach here due to raise in loop, but satisfy type checker
            msg = f"{func.__name__} exhausted all retries"
            raise RuntimeError(msg)

        return wrapper

    return decorator


def _calculate_backoff_delay(
    attempt: int,
    backoff_factor: float = 2.0,
    max_backoff: float = 30.0,
    retry_after: int | None = None,
) -> float:
    """Calculate backoff delay with exponential backoff and jitter.

    Args:
        attempt: Current attempt number (0-indexed)
        backoff_factor: Exponential backoff multiplier
        max_backoff: Maximum delay in seconds
        retry_after: Optional Retry-After header value from 429 response

    Returns:
        Delay in seconds with jitter applied

    Examples:
        >>> _calculate_backoff_delay(0)  # First retry
        0.75  # ~1.0 * (2.0 ** 0) with ±25% jitter
        >>> _calculate_backoff_delay(3)  # Fourth retry
        6.5   # ~8.0 * (2.0 ** 3) with ±25% jitter, capped at max_backoff
    """
    if retry_after is not None:
        # Respect Retry-After header from API (429 responses)
        return min(float(retry_after), max_backoff)

    # Exponential backoff: base_delay * (backoff_factor ** attempt)
    base_delay = 1.0
    delay = min(base_delay * (backoff_factor**attempt), max_backoff)

    # Add jitter: randomize ±25% to prevent thundering herd
    # Safe: Using random for jitter, not cryptography
    jitter = delay * 0.25
    delay = delay + random.uniform(-jitter, jitter)  # noqa: S311

    return max(0, delay)
