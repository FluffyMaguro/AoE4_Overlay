import platform
import webbrowser
from functools import partial
from typing import Any, Dict, List, Optional

from PyQt5 import QtWidgets

import overlay.helper_func as hf
from overlay.api_checking import Api_checker, get_full_match_history
from overlay.logging_func import get_logger
from overlay.settings import settings
from overlay.tab_games import MatchHistoryTab
from overlay.tab_graphs import GraphTab
from overlay.tab_override import OverrideTab
from overlay.tab_random import RandomTab
from overlay.tab_settings import SettingsTab
from overlay.tab_stats import StatsTab
from overlay.websocket import Websocket_manager
from overlay.worker import scheldule

logger = get_logger(__name__)


class TabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent, version: str):
        super().__init__(parent)
        self.version = version
        self.api_checker = Api_checker()
        self.websocket_manager = Websocket_manager(settings.websocket_port)
        self.force_stop = False
        self.prevent_overlay_update = False

        self.games_tab = MatchHistoryTab(self)
        self.graph_tab = GraphTab(self)
        self.random_tab = RandomTab(self)
        self.stats_tab = StatsTab(self)
        self.override_tab = OverrideTab(self)
        self.override_tab.data_override.connect(self.override_event)
        self.override_tab.update_override.connect(self.override_update_event)
        self.settigns_tab = SettingsTab(self)
        self.settigns_tab.new_profile.connect(self.new_profile_found)

        self.addTab(self.settigns_tab, "Settings")
        self.addTab(self.games_tab, "Games")
        self.addTab(self.graph_tab, "Rating")
        self.addTab(self.stats_tab, "Stats")
        self.addTab(self.override_tab, "Override")
        self.addTab(self.random_tab, "Randomize")

    def start(self):
        logger.info(
            f"Starting (v{self.version}) (c:{hf.is_compiled()}) [{platform.platform()}]"
        )
        self.check_for_new_version()
        hf.create_custom_files()
        self.settigns_tab.start()
        self.run_new_game_check()
        self.websocket_manager.run()
        self.send_ws_colors()

    def new_profile_found(self):
        self.api_checker.reset()
        self.graph_tab.run_update()
        self.stats_tab.run_mode_update()
        self.stats_tab.clear_match_data()
        self.games_tab.clear_games()
        self.update_with_match_history_data(10000)
        self.parent().update_title(settings.player_name)

    def update_with_match_history_data(self, amount: int):
        """ Gets match history and updates games tab and passes data to stats tab"""
        scheldule(self.got_match_history, get_full_match_history, amount)

    def got_match_history(self, match_history: List[Any]):
        if match_history is None:
            self.settigns_tab.message(
                "Failed to get match history! Possibly an issue with AoEIV.net",
                color='red')
            logger.warning("No match history data")
            return
        self.settigns_tab.message("")
        self.stats_tab.update_other_stats(match_history)
        self.games_tab.update_widgets(match_history)

    def run_new_game_check(self, delayed_seconds: int = 0):
        """ Creates a new thread for a new api check"""
        scheldule(self.new_game, self.api_checker.check_for_new_game,
                  delayed_seconds)

    def new_game(self, game_data: Optional[Dict[str, Any]]):
        """Received new data from api check, passes data along and reruns the check"""
        if self.force_stop:
            return
        if game_data is not None and "new_rating" in game_data:
            logger.info(
                f"Game finished (rating_timestamp: {game_data['timestamp']})")
            self.graph_tab.run_update()
            self.stats_tab.run_mode_update()
            self.update_with_match_history_data(2)
        elif game_data is not None:
            processed = hf.process_game(game_data)
            logger.info(
                f"New live game (match_id: {processed['match_id']} | mode: {processed['mode']-16})"
            )
            self.override_tab.update_data(processed)
            if not self.prevent_overlay_update:
                self.settigns_tab.overlay_widget.update_data(processed)
                self.websocket_manager.send({
                    "type": "player_data",
                    "data": processed
                })

        self.run_new_game_check(delayed_seconds=30)

    def stop_checking_api(self):
        """ The app is closing, we need to start shuttings things down"""
        self.force_stop = True
        self.api_checker.force_stop = True

    def check_for_new_version(self):
        """ Checks for a new version, creates a button if there is one """
        link = hf.version_check(self.version)
        if not link:
            return
        logger.info("New version available!")
        self.update_button.clicked.connect(partial(webbrowser.open, link))
        self.update_button.show()

    def override_event(self, data: Dict[str, Any]):
        self.settigns_tab.overlay_widget.update_data(data)
        self.websocket_manager.send({"type": "player_data", "data": data})

    def override_update_event(self, prevent: bool):
        self.prevent_overlay_update = prevent

    def send_ws_colors(self):
        self.websocket_manager.send({
            "type": "color",
            "data": settings.team_colors
        })
