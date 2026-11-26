import functools
import logging
import time

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def perf_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Starting '{func.__name__}' | args={args}, kwargs={kwargs}")
        start = time.perf_counter()

        try:
            resultado = func(*args, **kwargs)
            duration = time.perf_counter() - start
            logger.info(
                f"Finished '{func.__name__}' in {duration:.4f}s | return={resultado}"
            )
            return resultado
        except Exception:
            logger.exception(f"Error occurred while executing '{func.__name__}'")
            raise

    return wrapper
