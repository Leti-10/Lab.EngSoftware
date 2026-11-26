import functools
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def logger_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Starting '{func.__name__}' | args={args}, kwargs={kwargs}")

        try:
            resultado = func(*args, **kwargs)
            logger.info(f"Finished '{func.__name__}' | return={resultado}")
            return resultado
        except Exception:
            logger.exception(f"Error occurred while executing '{func.__name__}'")
            raise

    return wrapper
