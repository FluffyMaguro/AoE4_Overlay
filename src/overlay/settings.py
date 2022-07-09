import json
import os
from typing import Dict, List, Optional

from overlay.logging_func import CONFIG_FOLDER, get_logger

logger = get_logger(__name__)
CONFIG_FILE = os.path.join(CONFIG_FOLDER, "config.json")


class _Settings:

    def __init__(self):
        self.websocket_port: int = 7307
        self.send_email_logs: bool = True
        self.log_matches: bool = True
        self.interval: int = 15
        self.app_width: int = 900
        self.app_height: int = 600
        self.steam_id: Optional[int] = None
        self.profile_id: Optional[int] = None
        self.player_name: Optional[str] = None
        self.overlay_hotkey: str = ""
        self.overlay_geometry: Optional[List[int]] = None
        self.font_size: int = 12
        self.max_games_history: int = 100
        self.civ_stats_color: str = "#BC8AEA"
        self.show_graph = {"1": True, "2": True, "3": True, "4": True}
        self.team_colors = ((74, 255, 2, 0.35), (3, 179, 255, 0.35),
                            (255, 0, 0, 0.35), (255, 0, 255, 0.35),
                            (255, 255, 0, 0.35))
        # build order (BO) related parameters
        self.bo_show_title: bool = False  # True to show the title
        self.bo_title_color: list = [230, 159, 0]  # color for the title
        self.bo_overlay_hotkey_show: str = ""  # hotkey to show/hide the BO
        self.bo_overlay_hotkey_cycle: str = ""  # hotkey to cycle between the different BO available
        self.bo_overlay_hotkey_previous_step: str = ""  # hotkey to go to the previous step of the build order
        self.bo_overlay_hotkey_next_step: str = ""  # hotkey to go to the next step of the build order
        self.bo_font_size: int = 12  # font size
        self.bo_text_color: list = [255, 255, 255]  # text RGB color
        self.bo_color_background: list = [30, 30, 30]  # background RGB color
        self.bo_font_police: str = 'Arial'  # police font
        self.bo_opacity: float = 0.75  # opacity of the window
        self.bo_upper_right_position: list = [1870, 70]  # position for the upper right corner
        self.bo_image_height: int = 30  # height of the images
        self.bo_border_size: int = 15  # size of the borders
        self.bo_vertical_spacing: int = 10  # vertical space between the build order lines
        # store build orders
        self.build_orders: Dict[str, str] = {
            "Instructions": "Write your own build order.\n"
                            "You can also copy one from the https://age4builder.com website.\n\n"
                            "Two formats are accepted (both available on https://age4builder.com):\n"
                            "* Simple TXT format.\n"
                            "* JSON format compatible with CraftySalamander overlay."
        }

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
