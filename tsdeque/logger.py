import logging
import sys


def init_logger() -> None:
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(lineno)d - %(message)s"
    )
    stream_hdlr = logging.StreamHandler(sys.stdout)
    stream_hdlr.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    root_logger.addHandler(stream_hdlr)
