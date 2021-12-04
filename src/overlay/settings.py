import json
import os
from typing import List, Optional

from overlay.logging_func import get_logger

logger = get_logger(__name__)

CONFIG_FOLDER = os.path.join(os.getenv('APPDATA'), "AoE4_Overlay")
CONFIG_FILE = os.path.join(CONFIG_FOLDER, "config.json")


class _Settings:
    def __init__(self):
        self.steam_id: Optional[int] = None
        self.profile_id: Optional[int] = None
        self.player_name: Optional[str] = None
        self.overlay_hotkey: str = ""
        self.overlay_geometry: Optional[List[int]] = None
        self.font_size: int = 12
        self.load()

    def load(self):
        """ Loads configuration from app data"""
        if not os.path.isfile(CONFIG_FILE):
            return
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.loads(f.read())
        except Exception:
            logger.warning("Failed to parse config file")
            return

        for key in self.__dict__:
            if key in data:
                setattr(self, key, data[key])

    def save(self):
        """ Saves configuration to app data"""
        if not os.path.isdir(CONFIG_FOLDER):
            os.mkdir(CONFIG_FOLDER)

        with open(CONFIG_FILE, 'w') as f:
            f.write(json.dumps(self.__dict__))


settings = _Settings()
