"""Retry logic for wFabricSecurity."""

import functools
import logging
import time
from typing import Any, Callable, Optional, Tuple, Type

logger = logging.getLogger("FabricSecurity.Retry")


def with_retry(
    max_attempts: int = 3,
    backoff_factor: float = 1.5,
    initial_delay: float = 0.5,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None,
):
    """Decorator to retry a function on failure with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts
        backoff_factor: Multiplier for delay between retries
        initial_delay: Initial delay in seconds
        exceptions: Tuple of exception types to catch
        on_retry: Optional callback called on each retry (exception, attempt_number)

    Returns:
        Decorated function

    Example:
        @with_retry(max_attempts=3, exceptions=(ConnectionError, TimeoutError))
        def call_fabric():
            ...
    """

    def decorator(func: Callable) -> Callable:
        is_async = (
            hasattr(func, "__code__")
            and func.__code__.co_flags & 0x80
            or hasattr(func, "__await__")
        )

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        logger.error(
                            f"[Retry] All {max_attempts} attempts failed for {func.__name__}"
                        )
                        raise

                    logger.warning(
                        f"[Retry] Attempt {attempt}/{max_attempts} failed: {e}. Retrying in {delay:.2f}s..."
                    )

                    if on_retry:
                        on_retry(e, attempt)

                    time.sleep(delay)
                    delay *= backoff_factor

            raise last_exception

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            import asyncio

            delay = initial_delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        logger.error(
                            f"[Retry] All {max_attempts} attempts failed for {func.__name__}"
                        )
                        raise

                    logger.warning(
                        f"[Retry] Attempt {attempt}/{max_attempts} failed: {e}. Retrying in {delay:.2f}s..."
                    )

                    if on_retry:
                        on_retry(e, attempt)

                    await asyncio.sleep(delay)
                    delay *= backoff_factor

            raise last_exception

        return async_wrapper if is_async else wrapper

    return decorator


class RetryContext:
    """Context manager for retry operations."""

    def __init__(
        self,
        max_attempts: int = 3,
        backoff_factor: float = 1.5,
        initial_delay: float = 0.5,
        exceptions: Tuple[Type[Exception], ...] = (Exception,),
    ):
        """Initialize retry context.

        Args:
            max_attempts: Maximum number of attempts
            backoff_factor: Multiplier for delay between retries
            initial_delay: Initial delay in seconds
            exceptions: Tuple of exception types to catch
        """
        self.max_attempts = max_attempts
        self.backoff_factor = backoff_factor
        self.initial_delay = initial_delay
        self.exceptions = exceptions
        self.attempt = 0
        self.last_exception = None
        self.delay = initial_delay

    def __enter__(self) -> "RetryContext":
        self.attempt += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is None:
            return True

        if issubclass(exc_type, self.exceptions):
            self.last_exception = exc_val
            if self.attempt < self.max_attempts:
                logger.warning(
                    f"[Retry] Attempt {self.attempt} failed: {exc_val}. Retrying in {self.delay:.2f}s..."
                )
                time.sleep(self.delay)
                self.delay *= self.backoff_factor
                return True

        if exc_val is not None:
            logger.error(
                f"[Retry] All {self.max_attempts} attempts failed or non-retryable exception"
            )
        return False

    @property
    def succeeded(self) -> bool:
        """Check if operation succeeded."""
        return self.last_exception is None

    @property
    def exhausted(self) -> bool:
        """Check if all attempts were exhausted."""
        return self.attempt >= self.max_attempts
