import json
import os
from typing import List, Optional

from overlay.logging_func import CONFIG_FOLDER, get_logger

logger = get_logger(__name__)
CONFIG_FILE = os.path.join(CONFIG_FOLDER, "config.json")


class _Settings:
    def __init__(self):
        self.app_width: int = 900
        self.app_height: int = 600
        self.steam_id: Optional[int] = None
        self.profile_id: Optional[int] = None
        self.player_name: Optional[str] = None
        self.overlay_hotkey: str = ""
        self.overlay_geometry: Optional[List[int]] = None
        self.font_size: int = 12
        self.show_graph = {"1": True, "2": True, "3": True, "4": True}
        self.team_colors = ((74, 255, 2, 0.35), (3, 179, 255, 0.35), (255, 0,
                                                                      0, 0.35))

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
        with open(CONFIG_FILE, 'w') as f:
            f.write(json.dumps(self.__dict__, indent=2))


settings = _Settings()
