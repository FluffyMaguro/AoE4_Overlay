import logging
import os

import appdirs

CONFIG_FOLDER = os.path.join(appdirs.user_data_dir(), "AoE4_Overlay")
LOG_FILE = os.path.join(CONFIG_FOLDER, 'overlay.log')

if not os.path.isdir(CONFIG_FOLDER):
    os.mkdir(CONFIG_FOLDER)


def get_logger(name: str):
    logger = logging.getLogger(name)
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(LOG_FILE)
    logger.setLevel(logging.INFO)
    logger.setLevel(logging.INFO)

    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    format = logging.Formatter(
        '%(asctime)s|%(levelname)-7s|%(name)-21s: %(message)s [%(funcName)s|%(thread)d]',
        datefmt='%Y-%M-%d %H:%M:%S')
    c_handler.setFormatter(format)
    f_handler.setFormatter(format)

    return logger
