import json
import os
import pathlib

import requests
from PyQt5 import QtCore

from overlay.logging_func import get_logger

logger = get_logger(__name__)

# def isCompiled() -> bool:
#     """ Checks whether the app is compiled by Nuitka"""
#     return '__compiled__' in globals()

# def nuitka_exe_folder():
#     """ Returns the folder of the executable"""
#     return pathlib.Path(sys.argv[0]).parent.absolute()

ROOT = pathlib.Path(__file__).parent.parent.parent.absolute()


def pyqt_wait(miliseconds: int):
    """ Pause executing for `time` in miliseconds"""
    loop = QtCore.QEventLoop()
    QtCore.QTimer.singleShot(miliseconds, loop.quit)
    loop.exec_()


def file_path(file: str) -> str:
    """ Returns the path to the main directory regardless of the current working directory """
    return os.path.normpath(os.path.join(ROOT, file))


def version_to_int(version: str):
    """Convets `1.0.1` to an integer """
    return sum([
        int(i) * (1000**idx) for idx, i in enumerate(version.split('.')[::-1])
    ])


def version_check(version: str) -> str:
    """ Checks version. Returns either link for the new version or an empty string. """
    try:
        url = "https://raw.githubusercontent.com/FluffyMaguro/AoE4_Overlay/main/version.json"
        data = json.loads(requests.get(url).text)
        if version_to_int(version) < version_to_int(data['version']):
            return data['link']
    except Exception:
        logger.warning("Failed to check for a new version")
    return ""
