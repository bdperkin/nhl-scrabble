"""Unit tests for retry decorator."""

import time

import pytest

from nhl_scrabble.utils.retry import _calculate_backoff_delay, retry


class TestRetryDecorator:
    """Tests for retry decorator."""

    def test_retry_success_on_first_attempt(self) -> None:
        """Test that successful operation doesn't retry."""
        attempts = []

        @retry(max_attempts=3)
        def operation() -> str:
            attempts.append(1)
            return "success"

        result = operation()

        assert result == "success"
        assert len(attempts) == 1

    def test_retry_success_on_second_attempt(self) -> None:
        """Test that operation retries and succeeds."""
        attempts = []

        @retry(max_attempts=3, exceptions=(ValueError,))
        def operation() -> str:
            attempts.append(1)
            if len(attempts) < 2:
                raise ValueError("Temporary error")
            return "success"

        result = operation()

        assert result == "success"
        assert len(attempts) == 2

    def test_retry_exhausts_attempts(self) -> None:
        """Test that operation fails after max attempts."""

        @retry(max_attempts=3, exceptions=(ValueError,))
        def operation() -> str:
            raise ValueError("Persistent error")

        with pytest.raises(ValueError, match="Persistent error"):
            operation()

    def test_retry_backoff_timing(self) -> None:
        """Test that retry uses exponential backoff."""
        attempts = []

        @retry(max_attempts=3, backoff_factor=2.0, exceptions=(ValueError,))
        def operation() -> str:
            attempts.append(time.time())
            if len(attempts) < 3:
                raise ValueError("Error")
            return "success"

        operation()

        # Check delays (approximately 1s, 2s)
        delay1 = attempts[1] - attempts[0]
        delay2 = attempts[2] - attempts[1]

        # Allow tolerance for jitter (±25%)
        assert 0.7 < delay1 < 1.3  # ~1s ±jitter
        assert 1.4 < delay2 < 2.6  # ~2s ±jitter

    @pytest.mark.slow
    @pytest.mark.timeout(60)  # Test can take ~45 seconds due to retry delays
    def test_retry_respects_max_backoff(self) -> None:
        """Test that backoff is capped at max_backoff."""

        @retry(max_attempts=10, backoff_factor=2.0, max_backoff=5.0, exceptions=(ValueError,))
        def operation() -> str:
            raise ValueError("Error")

        start = time.time()
        with pytest.raises(ValueError, match="Error"):
            operation()
        duration = time.time() - start

        # With uncapped backoff, would be 1+2+4+8+16+... > 500s
        # With 5s cap, should be less (capped delays)
        # 9 retries with max 5s each + jitter = ~45s max
        assert duration < 60  # Allow some overhead

    def test_retry_on_retry_callback(self) -> None:
        """Test that on_retry callback is called."""
        callback_calls = []

        def on_retry_callback(exc: Exception, attempt: int) -> None:
            callback_calls.append((str(exc), attempt))

        @retry(max_attempts=3, on_retry=on_retry_callback, exceptions=(ValueError,))
        def operation() -> str:
            raise ValueError("Error")

        with pytest.raises(ValueError, match="Error"):
            operation()

        assert len(callback_calls) == 2  # Called on attempt 1 and 2 (not on last)
        assert callback_calls[0] == ("Error", 1)
        assert callback_calls[1] == ("Error", 2)

    def test_retry_specific_exceptions(self) -> None:
        """Test that retry only catches specified exceptions."""

        @retry(max_attempts=3, exceptions=(ValueError,))
        def operation() -> str:
            raise TypeError("Wrong exception type")

        # TypeError should not be caught, should raise immediately
        with pytest.raises(TypeError, match="Wrong exception type"):
            operation()

    def test_retry_with_return_value(self) -> None:
        """Test that retry preserves return value."""

        @retry(max_attempts=3)
        def operation() -> dict[str, int]:
            return {"result": 42}

        result = operation()

        assert result == {"result": 42}

    def test_retry_with_args_and_kwargs(self) -> None:
        """Test that retry works with function arguments."""

        @retry(max_attempts=3)
        def operation(x: int, y: int, multiplier: int = 1) -> int:
            return (x + y) * multiplier

        result = operation(3, 4, multiplier=2)

        assert result == 14

    def test_retry_preserves_function_metadata(self) -> None:
        """Test that retry decorator preserves function metadata."""

        @retry(max_attempts=3)
        def operation() -> str:
            """Operation docstring."""
            return "result"

        assert operation.__name__ == "operation"
        assert operation.__doc__ == "Operation docstring."

    def test_retry_multiple_exception_types(self) -> None:
        """Test retry with multiple exception types."""
        attempts = []

        @retry(max_attempts=5, exceptions=(ValueError, TypeError))
        def operation() -> str:
            attempts.append(1)
            if len(attempts) == 1:
                raise ValueError("First error")
            if len(attempts) == 2:
                raise TypeError("Second error")
            return "success"

        result = operation()

        assert result == "success"
        assert len(attempts) == 3


class TestCalculateBackoffDelay:
    """Tests for _calculate_backoff_delay helper function."""

    def test_calculate_backoff_delay_exponential(self) -> None:
        """Test that backoff delay increases exponentially."""
        delay_0 = _calculate_backoff_delay(0, backoff_factor=2.0)
        delay_1 = _calculate_backoff_delay(1, backoff_factor=2.0)
        delay_2 = _calculate_backoff_delay(2, backoff_factor=2.0)
        delay_3 = _calculate_backoff_delay(3, backoff_factor=2.0)

        # Attempt 0: 1.0 * (2.0 ** 0) = 1.0 ± 25%
        assert 0.75 <= delay_0 <= 1.25

        # Attempt 1: 1.0 * (2.0 ** 1) = 2.0 ± 25%
        assert 1.5 <= delay_1 <= 2.5

        # Attempt 2: 1.0 * (2.0 ** 2) = 4.0 ± 25%
        assert 3.0 <= delay_2 <= 5.0

        # Attempt 3: 1.0 * (2.0 ** 3) = 8.0 ± 25%
        assert 6.0 <= delay_3 <= 10.0

        # Verify exponential growth
        assert delay_0 < delay_1 < delay_2 < delay_3

    def test_calculate_backoff_delay_respects_max(self) -> None:
        """Test that backoff delay respects max_backoff limit."""
        # High attempt number would normally give huge delay
        # 1.0 * (2.0 ** 10) = 1024.0, but max_backoff = 5.0
        delay = _calculate_backoff_delay(10, backoff_factor=2.0, max_backoff=5.0)

        # Should be capped at max_backoff ± jitter (25% of 5.0 = 1.25)
        assert 0.0 <= delay <= 6.25  # max_backoff + jitter

    def test_calculate_backoff_delay_respects_retry_after(self) -> None:
        """Test that backoff delay respects Retry-After header."""
        # Retry-After value should override exponential backoff
        delay = _calculate_backoff_delay(0, retry_after=10)
        assert delay == 10.0

        # Retry-After should still respect max_backoff
        delay_capped = _calculate_backoff_delay(0, retry_after=50, max_backoff=30.0)
        assert delay_capped == 30.0  # Capped at max_backoff

    def test_calculate_backoff_delay_never_negative(self) -> None:
        """Test that backoff delay is never negative."""
        # Even with jitter, delay should be >= 0
        for attempt in range(10):
            delay = _calculate_backoff_delay(attempt)
            assert delay >= 0.0

    def test_calculate_backoff_delay_custom_backoff_factor(self) -> None:
        """Test backoff with custom backoff factor."""
        delay_0 = _calculate_backoff_delay(0, backoff_factor=3.0)
        delay_1 = _calculate_backoff_delay(1, backoff_factor=3.0)

        # Attempt 0: 1.0 * (3.0 ** 0) = 1.0 ± 25%
        assert 0.75 <= delay_0 <= 1.25

        # Attempt 1: 1.0 * (3.0 ** 1) = 3.0 ± 25%
        assert 2.25 <= delay_1 <= 3.75


class TestRetryEdgeCases:
    """Tests for retry decorator edge cases."""

    def test_retry_with_zero_max_attempts_raises_immediately(self) -> None:
        """Test that max_attempts=0 raises immediately."""

        @retry(max_attempts=0, exceptions=(ValueError,))
        def operation() -> str:
            raise ValueError("Error")

        # Should raise RuntimeError for invalid max_attempts
        with pytest.raises(RuntimeError, match="max_attempts=0 < 1"):
            operation()

    def test_retry_with_one_max_attempt_no_retry(self) -> None:
        """Test that max_attempts=1 doesn't retry."""
        attempts = []

        @retry(max_attempts=1, exceptions=(ValueError,))
        def operation() -> str:
            attempts.append(1)
            raise ValueError("Error")

        with pytest.raises(ValueError, match="Error"):
            operation()

        # Should only attempt once
        assert len(attempts) == 1

    def test_retry_callback_receives_correct_attempt_number(self) -> None:
        """Test that callback receives correct attempt numbers."""
        callback_attempts = []

        def on_retry_callback(exc: Exception, attempt: int) -> None:
            callback_attempts.append(attempt)

        @retry(max_attempts=4, on_retry=on_retry_callback, exceptions=(ValueError,))
        def operation() -> str:
            raise ValueError("Error")

        with pytest.raises(ValueError, match="Error"):
            operation()

        # Should be called 3 times (attempts 1, 2, 3 - not on final attempt 4)
        assert callback_attempts == [1, 2, 3]
