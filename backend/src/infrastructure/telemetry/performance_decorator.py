import functools
import inspect
import logging
import time
from collections.abc import Callable
from typing import Any, TypeVar, cast

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def perf_decorator(func: F) -> F:
    operation = func.__qualname__
    if inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
            except Exception as error:
                logger.error(
                    "Operation failed: %s (%s)",
                    operation,
                    type(error).__name__,
                )
                raise
            duration = time.perf_counter() - start
            logger.info("Operation %s completed in %.4fs", operation, duration)
            return result

        return cast(F, async_wrapper)

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
        except Exception as error:
            logger.error(
                "Operation failed: %s (%s)",
                operation,
                type(error).__name__,
            )
            raise
        duration = time.perf_counter() - start
        logger.info("Operation %s completed in %.4fs", operation, duration)
        return result

    return cast(F, wrapper)
