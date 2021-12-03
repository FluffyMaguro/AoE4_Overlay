import json
import os
from typing import Optional


def get_config_folder() -> str:
    return os.path.join(os.getenv('APPDATA'), "AoE4_Overlay")


class _Settings:
    def __init__(self):
        self.steam_id: Optional[int] = None
        self.overlay_hotkey: str = ""
        self.load()

    def load(self):
        """ Loads configuration from app data"""
        config_file = os.path.join(get_config_folder(), "config.json")

        if not os.path.isfile(config_file):
            return

        with open(config_file, 'r') as f:
            data = json.loads(f.read())

        self.steam_id = data.get('steam_id', None)
        self.overlay_hotkey = data.get('overlay_hotkey', "")

    def save(self):
        """ Saves configuration to app data"""
        config_folder = get_config_folder()
        if not os.path.isdir(config_folder):
            os.mkdir(config_folder)
        config_file = os.path.join(config_folder, "config.json")

        with open(config_file, 'w') as f:
            f.write(
                json.dumps({
                    "steam_id": self.steam_id,
                    "overlay_hotkey": self.overlay_hotkey
                }))


settings = _Settings()
