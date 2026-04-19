"""Tests for circuit breaker DoS protection."""

import time

import pytest

from nhl_scrabble.security.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitState,
)


class TestCircuitBreakerInitialization:
    """Test circuit breaker initialization and configuration."""

    def test_default_initialization(self) -> None:
        """Test circuit breaker with default parameters."""
        cb = CircuitBreaker()
        assert cb.failure_threshold == 5
        assert cb.timeout == 60.0
        assert cb.expected_exception is Exception
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
        assert cb.last_failure_time is None

    def test_custom_initialization(self) -> None:
        """Test circuit breaker with custom parameters."""
        cb = CircuitBreaker(
            failure_threshold=3,
            timeout=30.0,
            expected_exception=ValueError,
        )
        assert cb.failure_threshold == 3
        assert cb.timeout == 30.0
        assert cb.expected_exception is ValueError

    def test_invalid_threshold(self) -> None:
        """Test that invalid failure threshold raises ValueError."""
        with pytest.raises(ValueError, match="failure_threshold must be >= 1"):
            CircuitBreaker(failure_threshold=0)

    def test_invalid_timeout(self) -> None:
        """Test that negative timeout raises ValueError."""
        with pytest.raises(ValueError, match="timeout must be >= 0"):
            CircuitBreaker(timeout=-1.0)


class TestCircuitBreakerStates:
    """Test circuit breaker state transitions."""

    def test_initial_state_closed(self) -> None:
        """Test circuit breaker starts in CLOSED state."""
        cb = CircuitBreaker()
        assert cb.state == CircuitState.CLOSED
        assert cb.is_closed
        assert not cb.is_open

    def test_successful_call_stays_closed(self) -> None:
        """Test successful calls keep circuit CLOSED."""
        cb = CircuitBreaker()

        def success() -> str:
            return "OK"

        for _ in range(10):
            result = cb.call(success)
            assert result == "OK"
            assert cb.state == CircuitState.CLOSED
            assert cb.failure_count == 0

    def test_opens_after_threshold_failures(self) -> None:
        """Test circuit opens after reaching failure threshold."""
        cb = CircuitBreaker(failure_threshold=3)

        def failing() -> None:
            raise ValueError("Simulated failure")

        # First 3 failures should open circuit
        for i in range(3):
            with pytest.raises(ValueError, match=r"(Fail|Simulated failure)"):
                cb.call(failing)
            assert cb.failure_count == i + 1

        # Circuit should now be OPEN
        assert cb.state == CircuitState.OPEN
        assert cb.is_open
        assert not cb.is_closed

    def test_rejects_requests_when_open(self) -> None:
        """Test circuit breaker rejects requests when OPEN."""
        cb = CircuitBreaker(failure_threshold=2)

        def failing() -> None:
            raise ValueError("Fail")

        # Cause circuit to open
        for _ in range(2):
            with pytest.raises(ValueError, match=r"(Fail|Simulated failure)"):
                cb.call(failing)

        assert cb.state == CircuitState.OPEN

        # Now circuit should reject requests immediately
        with pytest.raises(CircuitBreakerOpenError, match="Circuit breaker is OPEN"):
            cb.call(lambda: "OK")

    def test_transitions_to_half_open_after_timeout(self) -> None:
        """Test circuit transitions to HALF_OPEN after timeout expires."""
        cb = CircuitBreaker(failure_threshold=2, timeout=0.1)

        def failing() -> None:
            raise ValueError("Fail")

        # Open the circuit
        for _ in range(2):
            with pytest.raises(ValueError, match=r"(Fail|Simulated failure)"):
                cb.call(failing)

        assert cb.state == CircuitState.OPEN

        # Wait for timeout
        time.sleep(0.15)

        # Next call should transition to HALF_OPEN
        # We need to actually make a call to trigger the transition
        def success() -> str:
            return "OK"

        result = cb.call(success)
        assert result == "OK"
        assert cb.state == CircuitState.CLOSED  # type: ignore[comparison-overlap]  # Success in HALF_OPEN closes circuit

    def test_half_open_success_closes_circuit(self) -> None:
        """Test successful request in HALF_OPEN state closes circuit."""
        cb = CircuitBreaker(failure_threshold=2, timeout=0.1)

        def failing() -> None:
            raise ValueError("Fail")

        # Open the circuit
        for _ in range(2):
            with pytest.raises(ValueError, match=r"(Fail|Simulated failure)"):
                cb.call(failing)

        # Wait for timeout
        time.sleep(0.15)

        # Successful call should close circuit
        def success() -> str:
            return "OK"

        result = cb.call(success)
        assert result == "OK"
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0

    def test_half_open_failure_reopens_circuit(self) -> None:
        """Test failure in HALF_OPEN state reopens circuit."""
        cb = CircuitBreaker(failure_threshold=2, timeout=0.1)

        def failing() -> None:
            raise ValueError("Fail")

        # Open the circuit
        for _ in range(2):
            with pytest.raises(ValueError, match=r"(Fail|Simulated failure)"):
                cb.call(failing)

        # Wait for timeout
        time.sleep(0.15)

        # Failed call should reopen circuit
        with pytest.raises(ValueError, match=r"(Fail|Simulated failure)"):
            cb.call(failing)

        assert cb.state == CircuitState.OPEN


class TestCircuitBreakerExceptionHandling:
    """Test circuit breaker exception handling."""

    def test_only_counts_expected_exceptions(self) -> None:
        """Test circuit only counts expected exception types."""
        cb = CircuitBreaker(failure_threshold=3, expected_exception=ValueError)

        def value_error() -> None:
            raise ValueError("Expected")

        def type_error() -> None:
            raise TypeError("Unexpected")

        # ValueError should be counted
        with pytest.raises(ValueError, match="Expected"):
            cb.call(value_error)
        assert cb.failure_count == 1

        # TypeError should not be counted (unexpected exception)
        with pytest.raises(TypeError):
            cb.call(type_error)
        assert cb.failure_count == 1  # Should not increment

    def test_multiple_exception_types(self) -> None:
        """Test circuit breaker with multiple expected exception types."""
        cb = CircuitBreaker(
            failure_threshold=3,
            expected_exception=(ValueError, TypeError),
        )

        def value_error() -> None:
            raise ValueError("First type")

        def type_error() -> None:
            raise TypeError("Second type")

        # Both should be counted
        with pytest.raises(ValueError, match="First type"):
            cb.call(value_error)
        assert cb.failure_count == 1

        with pytest.raises(TypeError):
            cb.call(type_error)
        assert cb.failure_count == 2


class TestCircuitBreakerReset:
    """Test circuit breaker manual reset."""

    def test_reset_from_open(self) -> None:
        """Test manual reset from OPEN state."""
        cb = CircuitBreaker(failure_threshold=2)

        def failing() -> None:
            raise ValueError("Fail")

        # Open the circuit
        for _ in range(2):
            with pytest.raises(ValueError, match=r"(Fail|Simulated failure)"):
                cb.call(failing)

        assert cb.state == CircuitState.OPEN
        assert cb.failure_count == 2

        # Reset
        cb.reset()
        assert cb.state == CircuitState.CLOSED  # type: ignore[comparison-overlap]
        assert cb.failure_count == 0  # type: ignore[unreachable]
        assert cb.last_failure_time is None

    def test_reset_from_closed(self) -> None:
        """Test reset when already closed."""
        cb = CircuitBreaker()
        cb.reset()
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0


class TestCircuitBreakerCallWithArguments:
    """Test circuit breaker call with function arguments."""

    def test_call_with_positional_args(self) -> None:
        """Test calling function with positional arguments."""
        cb = CircuitBreaker()

        def add(a: int, b: int) -> int:
            return a + b

        result = cb.call(add, 5, 3)
        assert result == 8

    def test_call_with_keyword_args(self) -> None:
        """Test calling function with keyword arguments."""
        cb = CircuitBreaker()

        def greet(name: str, greeting: str = "Hello") -> str:
            return f"{greeting}, {name}!"

        result = cb.call(greet, name="World", greeting="Hi")
        assert result == "Hi, World!"

    def test_call_with_mixed_args(self) -> None:
        """Test calling function with mixed positional and keyword arguments."""
        cb = CircuitBreaker()

        def compute(a: int, b: int, operation: str = "add") -> int:
            if operation == "add":
                return a + b
            return a * b

        result = cb.call(compute, 5, 3, operation="multiply")
        assert result == 15


class TestCircuitBreakerRepresentation:
    """Test circuit breaker string representation."""

    def test_repr_closed(self) -> None:
        """Test __repr__ in CLOSED state."""
        cb = CircuitBreaker(failure_threshold=5, timeout=60.0)
        repr_str = repr(cb)
        assert "state=closed" in repr_str
        assert "failures=0/5" in repr_str
        assert "timeout=60.0s" in repr_str

    def test_repr_open(self) -> None:
        """Test __repr__ in OPEN state."""
        cb = CircuitBreaker(failure_threshold=2, timeout=30.0)

        def failing() -> None:
            raise ValueError("Fail")

        # Open the circuit
        for _ in range(2):
            with pytest.raises(ValueError, match=r"(Fail|Simulated failure)"):
                cb.call(failing)

        repr_str = repr(cb)
        assert "state=open" in repr_str
        assert "failures=2/2" in repr_str


class TestCircuitBreakerEdgeCases:
    """Test circuit breaker edge cases and boundary conditions."""

    def test_threshold_of_one(self) -> None:
        """Test circuit breaker with failure threshold of 1."""
        cb = CircuitBreaker(failure_threshold=1)

        def failing() -> None:
            raise ValueError("Fail")

        # Single failure should open circuit
        with pytest.raises(ValueError, match=r"(Fail|Simulated failure)"):
            cb.call(failing)

        assert cb.state == CircuitState.OPEN

    def test_zero_timeout(self) -> None:
        """Test circuit breaker with zero timeout (immediate recovery)."""
        cb = CircuitBreaker(failure_threshold=2, timeout=0.0)

        def failing() -> None:
            raise ValueError("Fail")

        # Open the circuit
        for _ in range(2):
            with pytest.raises(ValueError, match=r"(Fail|Simulated failure)"):
                cb.call(failing)

        assert cb.state == CircuitState.OPEN

        # Should immediately allow retry (timeout=0)
        def success() -> str:
            return "OK"

        result = cb.call(success)
        assert result == "OK"
        assert cb.state == CircuitState.CLOSED  # type: ignore[comparison-overlap]

    def test_successive_failures_and_successes(self) -> None:
        """Test alternating failures and successes."""
        cb = CircuitBreaker(failure_threshold=3)

        def failing() -> None:
            raise ValueError("Fail")

        def success() -> str:
            return "OK"

        # Failure
        with pytest.raises(ValueError, match=r"(Fail|Simulated failure)"):
            cb.call(failing)
        assert cb.failure_count == 1

        # Success resets count
        cb.call(success)
        assert cb.failure_count == 0

        # Failure
        with pytest.raises(ValueError, match=r"(Fail|Simulated failure)"):
            cb.call(failing)
        assert cb.failure_count == 1

        # Circuit should still be closed (threshold not reached)
        assert cb.state == CircuitState.CLOSED
