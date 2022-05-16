import sys

from loguru import logger


def setup_loguru():
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")
