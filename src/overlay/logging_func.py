import logging
import os

CONFIG_FOLDER = os.path.join(os.getenv('APPDATA'), "AoE4_Overlay")
LOG_FILE = os.path.join(CONFIG_FOLDER, 'overlay.log')


def get_logger(name: str):
    logger = logging.getLogger(name)
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(LOG_FILE)
    logger.setLevel(logging.INFO)
    logger.setLevel(logging.INFO)

    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    format = logging.Formatter(
        '%(asctime)s|%(name)s|%(levelname)s: %(message)s [%(funcName)s|%(thread)d]',
        datefmt='%Y-%M-%d %H:%M:%S')
    c_handler.setFormatter(format)
    f_handler.setFormatter(format)

    return logger
