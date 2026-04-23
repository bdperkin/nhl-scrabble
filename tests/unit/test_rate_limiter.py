"""Unit tests for the rate limiter module."""

import threading
import time

import pytest

from nhl_scrabble.rate_limiter import RateLimiter


class TestRateLimiter:
    """Tests for RateLimiter class."""

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_basic_rate_limiting(self) -> None:
        """Test basic rate limiting behavior."""
        limiter = RateLimiter(max_requests=2, time_window=1.0)

        # First 2 requests should be instant
        start = time.monotonic()
        assert limiter.acquire()
        assert limiter.acquire()
        elapsed = time.monotonic() - start
        assert elapsed < 0.1, f"First 2 requests took {elapsed}s, expected < 0.1s"

        # Third request should wait for token refill
        start = time.monotonic()
        assert limiter.acquire()
        elapsed = time.monotonic() - start
        # Should wait approximately 0.5s (one token refills in 0.5s)
        assert elapsed >= 0.4, f"Third request waited {elapsed}s, expected >= 0.4s"
        assert elapsed < 0.7, f"Third request waited {elapsed}s, expected < 0.7s"

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_burst_size(self) -> None:
        """Test burst size allows initial burst."""
        limiter = RateLimiter(max_requests=10, time_window=10.0, burst_size=5)

        # Can make 5 requests immediately (burst)
        start = time.monotonic()
        for _ in range(5):
            assert limiter.acquire()
        elapsed = time.monotonic() - start
        assert elapsed < 0.1, f"Burst of 5 took {elapsed}s, expected < 0.1s"

        # 6th request waits for refill (1 token refills in 1 second)
        start = time.monotonic()
        assert limiter.acquire()
        elapsed = time.monotonic() - start
        assert elapsed >= 0.9, f"6th request waited {elapsed}s, expected >= 0.9s"

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_non_blocking_mode(self) -> None:
        """Test non-blocking acquire mode."""
        limiter = RateLimiter(max_requests=1, time_window=10.0)

        # First request succeeds
        assert limiter.acquire(block=False) is True

        # Second request fails (no tokens)
        assert limiter.acquire(block=False) is False

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_thread_safety(self) -> None:
        """Test rate limiter is thread-safe."""
        limiter = RateLimiter(max_requests=20, time_window=1.0)
        results: list[int] = []
        lock = threading.Lock()

        def make_requests() -> None:
            """Make requests in a thread."""
            for _ in range(5):
                limiter.acquire()
                with lock:
                    results.append(1)

        # Create multiple threads
        threads = [threading.Thread(target=make_requests) for _ in range(3)]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # All requests should succeed
        assert len(results) == 15
        assert limiter.total_requests == 15

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_stats_tracking(self) -> None:
        """Test statistics tracking."""
        limiter = RateLimiter(max_requests=2, time_window=1.0)

        # Make requests
        limiter.acquire()
        limiter.acquire()
        limiter.acquire()  # This one waits

        stats = limiter.get_stats()
        assert stats["total_requests"] == 3
        assert stats["total_waits"] == 1
        assert stats["total_wait_time"] > 0
        assert stats["average_wait"] > 0
        assert stats["current_tokens"] >= 0
        assert stats["max_tokens"] == 2

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_reset(self) -> None:
        """Test resetting rate limiter."""
        limiter = RateLimiter(max_requests=1, time_window=10.0)

        # Use up token
        limiter.acquire()

        # Verify token is consumed
        assert limiter.acquire(block=False) is False

        # Reset
        limiter.reset()

        # Should have token again
        assert limiter.acquire(block=False) is True

        # Stats should also be reset
        stats = limiter.get_stats()
        assert stats["total_requests"] == 1  # One request after reset
        assert stats["total_waits"] == 0
        assert stats["total_wait_time"] == 0.0

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_refill_rate_property(self) -> None:
        """Test refill_rate property calculation."""
        limiter = RateLimiter(max_requests=30, time_window=60.0)

        # 30 requests per 60 seconds = 0.5 requests/second
        assert limiter.refill_rate == 0.5

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_multiple_tokens_acquire(self) -> None:
        """Test acquiring multiple tokens at once."""
        limiter = RateLimiter(max_requests=10, time_window=10.0)

        # Acquire 3 tokens at once
        start = time.monotonic()
        assert limiter.acquire(tokens=3)
        elapsed = time.monotonic() - start
        assert elapsed < 0.1  # Should be instant

        # Verify 3 tokens were consumed
        stats = limiter.get_stats()
        assert stats["current_tokens"] < 10  # Less than max

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_token_refill_over_time(self) -> None:
        """Test that tokens refill over time."""
        limiter = RateLimiter(max_requests=10, time_window=10.0)

        # Use up all tokens
        for _ in range(10):
            limiter.acquire(block=False)

        # No tokens left
        assert limiter.acquire(block=False) is False

        # Wait for 1 second (should refill 1 token)
        time.sleep(1.1)

        # Should have 1 token now
        assert limiter.acquire(block=False) is True

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_wait_time_calculation(self) -> None:
        """Test that wait time is calculated correctly."""
        limiter = RateLimiter(max_requests=2, time_window=2.0)

        # Use up both tokens
        limiter.acquire()
        limiter.acquire()

        # Third request should wait approximately 1 second
        start = time.monotonic()
        limiter.acquire()
        elapsed = time.monotonic() - start

        # Should wait for 1 token to refill (1 second for 1 token)
        assert 0.9 <= elapsed <= 1.2, f"Expected wait ~1s, got {elapsed}s"

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_burst_size_default(self) -> None:
        """Test that burst size defaults to max_requests."""
        limiter = RateLimiter(max_requests=30, time_window=60.0)

        # Burst size should equal max_requests by default
        assert limiter.burst_size == 30

        # Should be able to make max_requests immediately
        start = time.monotonic()
        for _ in range(30):
            assert limiter.acquire(block=False)
        elapsed = time.monotonic() - start
        assert elapsed < 0.1

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_concurrent_acquires(self) -> None:
        """Test concurrent token acquisition."""
        limiter = RateLimiter(max_requests=100, time_window=10.0)
        success_count = 0
        lock = threading.Lock()

        def try_acquire() -> None:
            """Try to acquire a token."""
            nonlocal success_count
            if limiter.acquire(block=False):
                with lock:
                    success_count += 1

        # Start many threads simultaneously
        threads = [threading.Thread(target=try_acquire) for _ in range(200)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should acquire at most max_requests tokens
        assert success_count <= 100
        assert success_count > 0  # But should acquire some

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_zero_tokens_available(self) -> None:
        """Test behavior when zero tokens are available."""
        limiter = RateLimiter(max_requests=1, time_window=10.0)

        # Use the only token
        limiter.acquire()

        # Non-blocking acquire should fail
        assert limiter.acquire(block=False) is False

        # Verify stats show (approximately) zero tokens
        stats = limiter.get_stats()
        assert stats["current_tokens"] < 0.01, f"Expected ~0 tokens, got {stats['current_tokens']}"

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_tokens_dont_exceed_burst_size(self) -> None:
        """Test that tokens never exceed burst size even after long wait."""
        limiter = RateLimiter(max_requests=10, time_window=1.0, burst_size=5)

        # Wait a long time
        time.sleep(2.0)

        # Should only have burst_size tokens, not more
        # Try to acquire more than burst_size
        count = 0
        while limiter.acquire(block=False):
            count += 1
            if count > 10:  # Safety limit
                break

        assert count == 5, f"Expected 5 tokens (burst_size), got {count}"


class TestRateLimiterEdgeCases:
    """Edge case tests for RateLimiter."""

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_very_high_rate_limit(self) -> None:
        """Test with very high rate limit."""
        limiter = RateLimiter(max_requests=1000, time_window=1.0)

        # Should be able to make many requests quickly
        start = time.monotonic()
        for _ in range(100):
            assert limiter.acquire(block=False)
        elapsed = time.monotonic() - start
        assert elapsed < 0.1

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_very_low_rate_limit(self) -> None:
        """Test with very low rate limit."""
        limiter = RateLimiter(max_requests=1, time_window=2.0)

        # First request instant
        assert limiter.acquire(block=False)

        # Second request should fail (no tokens)
        assert limiter.acquire(block=False) is False

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_fractional_tokens(self) -> None:
        """Test that fractional token refills work correctly."""
        # 3 requests per 2 seconds = 1.5 requests/second
        limiter = RateLimiter(max_requests=3, time_window=2.0)

        # Use up all tokens
        for _ in range(3):
            limiter.acquire()

        # Wait for partial refill (0.5 seconds = 0.75 tokens)
        time.sleep(0.6)

        # Should not have a full token yet
        assert limiter.acquire(block=False) is False

        # Wait a bit more (total ~1.2 seconds = ~1.8 tokens)
        time.sleep(0.7)

        # Should have at least 1 token now
        assert limiter.acquire(block=False) is True
