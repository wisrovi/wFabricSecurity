"""
Tests for Rate Limiting and Retry Logic modules
Part of Integrity Validation Matrix: Rate Limiting, Retry Logic
"""

import pytest
import sys
import os
import time
from unittest.mock import Mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestRateLimiter:
    """Tests for RateLimiter."""

    def test_rate_limiter_init(self):
        from wFabricSecurity.fabric_security.security.rate_limiter import RateLimiter

        limiter = RateLimiter(requests_per_second=100, burst=50)
        assert limiter is not None

    def test_try_acquire(self):
        from wFabricSecurity.fabric_security.security.rate_limiter import RateLimiter

        limiter = RateLimiter(requests_per_second=1000, burst=100)
        result = limiter.try_acquire()
        assert result is True

    def test_acquire(self):
        from wFabricSecurity.fabric_security.security.rate_limiter import RateLimiter

        limiter = RateLimiter(requests_per_second=1000, burst=100)
        limiter.acquire()
        assert True

    def test_get_stats(self):
        from wFabricSecurity.fabric_security.security.rate_limiter import RateLimiter

        limiter = RateLimiter(requests_per_second=100, burst=50)
        stats = limiter.get_stats()
        assert isinstance(stats, dict)


class TestRetryLogic:
    """Tests for Retry Logic."""

    def test_with_retry_success(self):
        from wFabricSecurity.fabric_security.security.retry import with_retry

        call_count = 0

        @with_retry(max_attempts=3, initial_delay=0.01)
        def success_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = success_func()
        assert result == "success"
        assert call_count == 1

    def test_with_retry_eventual_success(self):
        from wFabricSecurity.fabric_security.security.retry import with_retry

        call_count = 0

        @with_retry(max_attempts=3, initial_delay=0.01)
        def eventually_success():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("fail")
            return "success"

        result = eventually_success()
        assert result == "success"
        assert call_count == 2

    def test_with_retry_exhausted(self):
        from wFabricSecurity.fabric_security.security.retry import with_retry

        call_count = 0

        @with_retry(max_attempts=2, initial_delay=0.01)
        def always_fail():
            nonlocal call_count
            call_count += 1
            raise ValueError("always fail")

        with pytest.raises(ValueError):
            always_fail()
        assert call_count == 2

    def test_with_retry_specific_exception(self):
        from wFabricSecurity.fabric_security.security.retry import with_retry

        call_count = 0

        @with_retry(max_attempts=3, initial_delay=0.01, exceptions=(ValueError,))
        def fail_on_value():
            nonlocal call_count
            call_count += 1
            raise ValueError("fail")
            raise TypeError("should not retry")

        with pytest.raises(ValueError):
            fail_on_value()

    def test_with_retry_callback(self):
        from wFabricSecurity.fabric_security.security.retry import with_retry

        callback_results = []

        def my_callback(exc, attempt):
            callback_results.append((exc, attempt))

        @with_retry(max_attempts=2, initial_delay=0.01, on_retry=my_callback)
        def fail_func():
            raise ValueError("fail")

        with pytest.raises(ValueError):
            fail_func()
        assert len(callback_results) > 0

    def test_retry_context_init(self):
        from wFabricSecurity.fabric_security.security.retry import RetryContext

        ctx = RetryContext(max_attempts=3, initial_delay=0.5)
        assert ctx.max_attempts == 3
        assert ctx.delay == 0.5
        assert ctx.attempt == 0

    def test_retry_context_success(self):
        from wFabricSecurity.fabric_security.security.retry import RetryContext

        ctx = RetryContext(max_attempts=1, initial_delay=0.01)
        with ctx:
            pass
        assert ctx.succeeded is True
        assert ctx.exhausted is False

    def test_retry_context_failure(self):
        from wFabricSecurity.fabric_security.security.retry import RetryContext

        ctx = RetryContext(max_attempts=1, initial_delay=0.01)
        with pytest.raises(ValueError):
            with ctx:
                raise ValueError("test")
        assert ctx.exhausted is True

    def test_retry_context_backoff(self):
        from wFabricSecurity.fabric_security.security.retry import RetryContext

        ctx = RetryContext(max_attempts=3, initial_delay=0.05, backoff_factor=2.0)
        assert ctx.delay == 0.05

        with ctx:
            raise ValueError("first")
        assert ctx.delay == pytest.approx(0.1)

        with ctx:
            raise ValueError("second")
        assert ctx.delay == pytest.approx(0.2)

    def test_retry_context_multiple_attempts(self):
        from wFabricSecurity.fabric_security.security.retry import RetryContext

        ctx = RetryContext(max_attempts=1, initial_delay=0.01)
        assert ctx.attempt == 0

        with pytest.raises(ValueError):
            with ctx:
                raise ValueError("test")

        assert ctx.attempt == 1
        assert ctx.last_exception is not None


class TestRateLimiterCoverage:
    """Additional tests for RateLimiter to increase coverage."""

    def test_acquire_multiple_tokens(self):
        from wFabricSecurity.fabric_security.security.rate_limiter import RateLimiter

        limiter = RateLimiter(requests_per_second=100, burst=10)
        result = limiter.acquire(tokens=5, blocking=False)
        assert result is True

    def test_acquire_with_timeout_insufficient_tokens(self):
        from wFabricSecurity.fabric_security.security.rate_limiter import RateLimiter

        limiter = RateLimiter(requests_per_second=1, burst=1)
        limiter.acquire(tokens=1, blocking=False)
        result = limiter.acquire(tokens=1, blocking=True, timeout=0.01)
        assert result is False

    def test_get_recent_requests(self):
        from wFabricSecurity.fabric_security.security.rate_limiter import RateLimiter

        limiter = RateLimiter(requests_per_second=100, burst=10)
        limiter.acquire(tokens=3, blocking=False)
        recent = limiter.get_recent_requests(1.0)
        assert recent >= 0

    def test_is_over_limit(self):
        from wFabricSecurity.fabric_security.security.rate_limiter import RateLimiter

        limiter = RateLimiter(requests_per_second=10, burst=5)
        limiter.acquire(tokens=3, blocking=False)
        is_over = limiter.is_over_limit()
        assert isinstance(is_over, bool)

    def test_block_for(self):
        from wFabricSecurity.fabric_security.security.rate_limiter import RateLimiter

        limiter = RateLimiter(requests_per_second=100, burst=10)
        limiter.block_for(0.5)
        assert limiter.try_acquire() is False

    def test_unblock(self):
        from wFabricSecurity.fabric_security.security.rate_limiter import RateLimiter

        limiter = RateLimiter(requests_per_second=100, burst=10)
        limiter.block_for(0.1)
        time.sleep(0.2)
        limiter.unblock()
        result = limiter.try_acquire()
        assert result is True

    def test_is_blocked_property(self):
        from wFabricSecurity.fabric_security.security.rate_limiter import RateLimiter

        limiter = RateLimiter(requests_per_second=100, burst=10)
        assert limiter.is_blocked is False
        limiter.block_for(0.1)
        assert limiter.is_blocked is True

    def test_get_stats_includes_blocked_until(self):
        from wFabricSecurity.fabric_security.security.rate_limiter import RateLimiter

        limiter = RateLimiter(requests_per_second=100, burst=10)
        limiter.block_for(1.0)
        stats = limiter.get_stats()
        assert "blocked_until" in stats

    def test_acquire_0_tokens(self):
        from wFabricSecurity.fabric_security.security.rate_limiter import RateLimiter

        limiter = RateLimiter(requests_per_second=100, burst=10)
        result = limiter.acquire(tokens=0, blocking=False)
        assert result is True

    def test_reset_clears_tokens(self):
        from wFabricSecurity.fabric_security.security.rate_limiter import RateLimiter

        limiter = RateLimiter(requests_per_second=100, burst=5)
        limiter.acquire(tokens=3, blocking=False)
        limiter.reset()
        tokens = limiter.get_available_tokens()
        assert tokens == 5.0

    def test_rate_limit_exceeded_error(self):
        from wFabricSecurity.fabric_security.security.rate_limiter import RateLimiter
        from wFabricSecurity.fabric_security.core.exceptions import RateLimitError

        limiter = RateLimiter(requests_per_second=100, burst=2)
        limiter.acquire(tokens=2, blocking=False)
        with pytest.raises(RateLimitError):
            limiter.acquire(tokens=1, blocking=False)
