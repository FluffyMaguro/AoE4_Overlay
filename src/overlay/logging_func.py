import logging


def get_logger(name: str):
    logger = logging.getLogger(name)
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler('file.log')
    logger.setLevel(logging.INFO)
    logger.setLevel(logging.INFO)

    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    format = logging.Formatter(
        '%(asctime)s %(levelname)s - %(name)s (%(funcName)s): %(message)s',
        datefmt='%Y-%M-%d %H:%M:%S')
    c_handler.setFormatter(format)
    f_handler.setFormatter(format)

    return logger
