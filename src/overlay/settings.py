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
                            (255, 0, 0, 0.35), (255, 0, 255, 0.35), (255, 255,
                                                                     0, 0.35))
        # build order (BO) related parameters
        self.bo_show_title: bool = True  # True to show the title
        self.bo_title_color: list = [230, 159, 0]  # color for the title
        self.bo_overlay_hotkey_show: str = ""  # hotkey to show/hide the BO
        self.bo_overlay_hotkey_cycle: str = ""  # hotkey to cycle between the different BO available
        self.bo_overlay_hotkey_previous_step: str = ""  # hotkey to go to the previous step of the BO
        self.bo_overlay_hotkey_next_step: str = ""  # hotkey to go to the next step of the BO
        self.bo_font_size: int = 12  # font size
        self.bo_text_color: list = [255, 255, 255]  # text RGB color
        self.bo_color_background: list = [30, 30, 30]  # background RGB color
        self.bo_font_police: str = 'Arial'  # police font
        self.bo_opacity: float = 0.75  # opacity of the window
        self.bo_upper_right_position: list = [
            1870, 70
        ]  # position for the upper right corner
        self.bo_image_height: int = 30  # height of the images
        self.bo_border_size: int = 15  # size of the borders
        self.bo_vertical_spacing: int = 10  # vertical space between the BO lines
        # store build orders
        self.buildorders: Dict[str, str] = {
            "Instructions":
                "Write your own build order.\n"
                "You can also copy one from the https://age4builder.com website\n"
                "    (click on the salamander icon and paste it here).\n\n"
                "Two formats are accepted (both available on https://age4builder.com):\n"
                "* Simple TXT format.\n"
                "* JSON format compatible with CraftySalamander overlay."
        }
        self.unchecked_buildorders: list = []  # list of build orders which are not checked at launch
        # images
        self.image_wood: str = 'resource/resource_wood.png'  # wood resource
        self.image_food: str = 'resource/resource_food.png'  # food resource
        self.image_gold: str = 'resource/resource_gold.png'  # gold resource
        self.image_stone: str = 'resource/resource_stone.png'  # stone resource
        self.image_population: str = 'building_economy/house.png'  # population icon
        self.image_villager: str = 'unit_worker/villager.png'  # villager icon
        self.image_age_unknown: str = 'age/age_unknown.png'  # unknown age image
        self.image_age_1: str = 'age/age_1.png'  # first age image (Dark Age)
        self.image_age_2: str = 'age/age_2.png'  # second age image (Feudal Age)
        self.image_age_3: str = 'age/age_3.png'  # third age image (Castle Age)
        self.image_age_4: str = 'age/age_4.png'  # fourth age image (Imperial Age)
        self.image_time: str = 'time/time.png'  # time for build order

    def load(self):
        """ Loads configuration from app data"""
        if not os.path.isfile(CONFIG_FILE):
            return
        try:
            with open(CONFIG_FILE, 'rb') as f:
                data = json.loads(f.read())
        except Exception:
            logger.warning("Failed to parse config file")
            return

        for key in data:
            setattr(self, key, data[key])

    def save(self):
        """ Saves configuration to app data"""
        with open(CONFIG_FILE, 'w') as f:
            f.write(json.dumps(self.__dict__, indent=2))


settings = _Settings()
