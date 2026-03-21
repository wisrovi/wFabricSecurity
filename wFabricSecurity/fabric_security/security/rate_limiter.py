"""Rate limiting for wFabricSecurity."""

import logging
import threading
import time
from collections import deque
from typing import Optional

from ..core.exceptions import RateLimitError

logger = logging.getLogger("FabricSecurity.RateLimiter")


class RateLimiter:
    """Token bucket rate limiter for preventing DoS attacks."""

    def __init__(
        self,
        requests_per_second: float = 100,
        burst: int = 200,
    ):
        """Initialize rate limiter.

        Args:
            requests_per_second: Maximum sustained request rate
            burst: Maximum burst size
        """
        self._rps = requests_per_second
        self._burst = burst
        self._tokens = float(burst)
        self._last_update = time.monotonic()
        self._lock = threading.Lock()
        self._request_times: deque = deque(maxlen=burst)
        self._blocked_until: Optional[float] = None

    @property
    def requests_per_second(self) -> float:
        """Get requests per second limit."""
        return self._rps

    @property
    def burst_size(self) -> int:
        """Get burst size limit."""
        return self._burst

    def _refill_tokens(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self._last_update
        tokens_to_add = elapsed * self._rps
        self._tokens = min(self._burst, self._tokens + tokens_to_add)
        self._last_update = now

    def acquire(
        self, tokens: int = 1, blocking: bool = True, timeout: Optional[float] = None
    ) -> bool:
        """Acquire tokens from the bucket.

        Args:
            tokens: Number of tokens to acquire
            blocking: Whether to block until tokens are available
            timeout: Maximum time to wait (None = wait forever)

        Returns:
            True if tokens were acquired

        Raises:
            RateLimitError: If rate limit is exceeded (non-blocking)
        """
        start_time = time.monotonic()

        while True:
            with self._lock:
                self._refill_tokens()

                if self._tokens >= tokens:
                    self._tokens -= tokens
                    self._request_times.append(time.monotonic())
                    return True

                if not blocking:
                    raise RateLimitError(
                        message=f"Rate limit exceeded. Need {tokens} tokens, have {self._tokens:.2f}",
                        details={
                            "requested": tokens,
                            "available": self._tokens,
                            "rps": self._rps,
                        },
                    )

                if timeout is not None:
                    elapsed = time.monotonic() - start_time
                    if elapsed >= timeout:
                        return False

                wait_time = (tokens - self._tokens) / self._rps
                if timeout is not None:
                    remaining = timeout - elapsed
                    wait_time = min(wait_time, remaining)

            time.sleep(min(wait_time, 0.1))

    def try_acquire(self, tokens: int = 1) -> bool:
        """Try to acquire tokens without blocking.

        Args:
            tokens: Number of tokens to acquire

        Returns:
            True if tokens were acquired
        """
        try:
            return self.acquire(tokens, blocking=False)
        except RateLimitError:
            return False

    def get_available_tokens(self) -> float:
        """Get current number of available tokens.

        Returns:
            Number of available tokens
        """
        with self._lock:
            self._refill_tokens()
            return self._tokens

    def get_recent_requests(self, seconds: float = 1.0) -> int:
        """Get number of requests in the last N seconds.

        Args:
            seconds: Time window

        Returns:
            Number of requests
        """
        cutoff = time.monotonic() - seconds
        with self._lock:
            count = sum(1 for t in self._request_times if t > cutoff)
        return count

    def is_over_limit(self, threshold: float = 1.0) -> bool:
        """Check if current rate exceeds threshold.

        Args:
            threshold: Threshold multiplier (1.0 = at limit)

        Returns:
            True if over limit
        """
        recent = self.get_recent_requests(1.0)
        return recent > (self._rps * threshold)

    def reset(self) -> None:
        """Reset the rate limiter."""
        with self._lock:
            self._tokens = float(self._burst)
            self._last_update = time.monotonic()
            self._request_times.clear()
            self._blocked_until = None

    def block_for(self, seconds: float) -> None:
        """Block all requests for a duration.

        Args:
            seconds: Duration to block
        """
        with self._lock:
            self._blocked_until = time.monotonic() + seconds
            self._tokens = 0

    def unblock(self) -> None:
        """Unblock the rate limiter."""
        with self._lock:
            self._blocked_until = None

    @property
    def is_blocked(self) -> bool:
        """Check if currently blocked."""
        if self._blocked_until is None:
            return False
        if time.monotonic() > self._blocked_until:
            self._blocked_until = None
            return False
        return True

    def get_stats(self) -> dict:
        """Get rate limiter statistics.

        Returns:
            Statistics dictionary
        """
        cutoff_1s = time.monotonic() - 1.0
        cutoff_10s = time.monotonic() - 10.0

        with self._lock:
            recent_1s = sum(1 for t in self._request_times if t > cutoff_1s)
            recent_10s = sum(1 for t in self._request_times if t > cutoff_10s)

            return {
                "available_tokens": self._tokens,
                "burst_size": self._burst,
                "requests_per_second": self._rps,
                "recent_requests_1s": recent_1s,
                "recent_requests_10s": recent_10s,
                "is_blocked": self.is_blocked,
                "blocked_until": self._blocked_until,
            }
