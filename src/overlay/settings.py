import json
import os
from typing import List, Optional

from overlay.logging_func import get_logger

logger = get_logger(__name__)


def get_config_folder() -> str:
    return os.path.join(os.getenv('APPDATA'), "AoE4_Overlay")


class _Settings:
    def __init__(self):
        self.steam_id: Optional[int] = None
        self.profile_id: Optional[int] = None
        self.overlay_hotkey: str = ""
        self.overlay_geometry: Optional[List[int]] = None
        self.font_size: int = 12
        self.load()

    def load(self):
        """ Loads configuration from app data"""
        config_file = os.path.join(get_config_folder(), "config.json")

        if not os.path.isfile(config_file):
            return

        try:
            with open(config_file, 'r') as f:
                data = json.loads(f.read())
        except Exception:
            logger.warning("Failed to parse config file")
            return

        for key in self.__dict__:
            if key in data:
                setattr(self, key, data[key])

    def save(self):
        """ Saves configuration to app data"""
        config_folder = get_config_folder()
        if not os.path.isdir(config_folder):
            os.mkdir(config_folder)
        config_file = os.path.join(config_folder, "config.json")

        with open(config_file, 'w') as f:
            f.write(json.dumps(self.__dict__))


settings = _Settings()
