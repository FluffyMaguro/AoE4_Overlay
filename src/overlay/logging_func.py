import functools
import logging
import os
import time
from typing import Any, Dict

import appdirs

CONFIG_FOLDER = os.path.join(appdirs.user_data_dir(), "AoE4_Overlay")
LOG_FILE = os.path.join(CONFIG_FOLDER, 'overlay.log')
MATCH_LOG_FILE = os.path.join(CONFIG_FOLDER, 'matches.log')

if not os.path.isdir(CONFIG_FOLDER):
    os.mkdir(CONFIG_FOLDER)


def get_logger(name: str):
    logger = logging.getLogger(name)
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    logger.setLevel(logging.INFO)
    logger.setLevel(logging.INFO)

    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    format = logging.Formatter(
        '%(asctime)s|%(levelname)-7s|%(name)-21s: %(message)s [%(funcName)s|%(thread)d]',
        datefmt='%Y-%m-%d %H:%M:%S')
    c_handler.setFormatter(format)
    f_handler.setFormatter(format)

    return logger


def log_match(match: Dict[str, Any]):
    try:
        now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        with open(MATCH_LOG_FILE, 'a') as f:
            f.write(f"{now} | {match}\n")
    except Exception:
        ...


def catch_exceptions(logger: logging.Logger):
    """ Catches exceptions for given function and writes a log"""

    # Outer function is here to provide argument for the decorator
    def inner_function(job_func):

        @functools.wraps(job_func)  # passes useful info to decorators
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except Exception:
                logger.exception("")

        return wrapper

    return inner_function
