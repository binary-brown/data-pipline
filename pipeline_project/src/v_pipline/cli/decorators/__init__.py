import logging
from functools import wraps
from logging import Logger
from typing import Callable

from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
	level="NOTSET",
	format=FORMAT,
	datefmt="[%X]",
	handlers=[RichHandler()],
)

logger = logging.getLogger("vp")


def log(logger: Logger = logger) -> Callable:
	def decorator(func: Callable) -> Callable:
		@wraps(func)
		def wrapper(*args, **kwargs):
			logger.info(f"Running {func.__name__}")
			try:
				return func(*args, **kwargs)
			except Exception as e:
				logger.exception(f"Error running {func.__name__}: {e}")
				raise e

		return wrapper

	return decorator
