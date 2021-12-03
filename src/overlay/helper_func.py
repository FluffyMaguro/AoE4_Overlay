import json
import os
import pathlib
from typing import Any, Dict

# def isCompiled() -> bool:
#     """ Checks whether the app is compiled by Nuitka"""
#     return '__compiled__' in globals()

# def nuitka_exe_folder():
#     """ Returns the folder of the executable"""
#     return pathlib.Path(sys.argv[0]).parent.absolute()

ROOT = pathlib.Path(__file__).parent.parent.parent.absolute()


def file_path(file: str) -> str:
    """ Returns the path to the main directory regardless of the current working directory """
    return os.path.normpath(os.path.join(ROOT, file))


def get_config_folder() -> str:
    return os.path.join(os.getenv('APPDATA'), "AoE4_Overlay")


def load_config() -> Dict[str, Any]:
    """ Loads configuration from app data"""
    config_file = os.path.join(get_config_folder(), "config.json")

    if not os.path.isfile(config_file):
        return {}

    with open(config_file, 'r') as f:
        return json.loads(f.read())


def save_config(object: Dict[str, Any]):
    """ Saves configuration to app data"""
    config_folder = get_config_folder()
    if not os.path.isdir(config_folder):
        os.mkdir(config_folder)
    config_file = os.path.join(config_folder, "config.json")

    with open(config_file, 'w') as f:
        f.write(json.dumps(object))
