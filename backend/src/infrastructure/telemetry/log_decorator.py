import functools
import inspect
import logging
from collections.abc import Callable
from typing import Any, TypeVar, cast

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def logger_decorator(func: F) -> F:
    operation = func.__qualname__
    if inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            logger.info("Starting persistence operation: %s", operation)
            try:
                result = await func(*args, **kwargs)
            except Exception as error:
                logger.error(
                    "Persistence operation failed: %s (%s)",
                    operation,
                    type(error).__name__,
                )
                raise
            logger.info("Completed persistence operation: %s", operation)
            return result

        return cast(F, async_wrapper)

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.info("Starting persistence operation: %s", operation)
        try:
            result = func(*args, **kwargs)
        except Exception as error:
            logger.error(
                "Persistence operation failed: %s (%s)",
                operation,
                type(error).__name__,
            )
            raise
        logger.info("Completed persistence operation: %s", operation)
        return result

    return cast(F, wrapper)
