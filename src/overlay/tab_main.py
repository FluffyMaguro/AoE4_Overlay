import importlib
import platform
import time
import webbrowser
from functools import partial
from typing import Any, Dict, List, Optional

import keyboard
from PyQt5 import QtWidgets

import overlay.helper_func as hf
from overlay.api_checking import Api_checker, get_full_match_history
from overlay.logging_func import get_logger, log_match
from overlay.settings import settings
from overlay.tab_build_orders import BoTab
from overlay.tab_games import MatchHistoryTab
from overlay.tab_graphs import GraphTab
from overlay.tab_override import OverrideTab
from overlay.tab_random import RandomTab
from overlay.tab_settings import SettingsTab
from overlay.tab_stats import StatsTab
from overlay.tab_production import ProductionTab
from overlay.websocket import Websocket_manager
from overlay.worker import scheldule

logger = get_logger(__name__)


class TabWidget(QtWidgets.QTabWidget):

    def __init__(self, parent, version: str):
        super().__init__(parent)
        self.version = version
        self.api_checker = Api_checker()
        self.websocket_manager = Websocket_manager(settings.websocket_port)
        self.force_stop: bool = False
        self.prevent_overlay_update: bool = False

        self.games_tab = MatchHistoryTab(self)
        # self.graph_tab = GraphTab(self)
        self.random_tab = RandomTab(self)
        # self.stats_tab = StatsTab(self)
        self.build_order_tab = BoTab(self)
        self.override_tab = OverrideTab(self)
        self.override_tab.data_override.connect(self.override_event)
        self.override_tab.update_override.connect(self.override_update_event)
        self.settigns_tab = SettingsTab(self)
        self.settigns_tab.new_profile.connect(self.new_profile_found)
        self.production_tab = ProductionTab(self)

        self.addTab(self.settigns_tab, "Settings")
        self.addTab(self.games_tab, "Games")
        # self.addTab(self.graph_tab, "Rating")
        # self.addTab(self.stats_tab, "Stats")
        self.addTab(self.build_order_tab, "Build orders")
        self.addTab(self.random_tab, "Randomize")
        self.addTab(self.override_tab, "Override")
        self.addTab(self.production_tab, "Production")

    def start(self):
        logger.info(
            f"Starting (v{self.version}) (compiled:{hf.is_compiled()}) [{platform.platform()}]"
        )
        self.check_for_new_version()
        hf.create_custom_files()
        self.settigns_tab.start()
        self.run_new_game_check()
        self.websocket_manager.run()
        self.send_ws_colors()
        self.check_waking()

    def closeEvent(self, _):
        """Function called when closing the widget."""
        self.build_order_tab.close()

    def new_profile_found(self):
        self.api_checker.reset()
        # self.graph_tab.run_update()
        # self.stats_tab.run_mode_update()
        # self.stats_tab.clear_match_data()
        self.games_tab.clear_games()
        self.update_with_match_history_data(10000)
        self.parent().update_title(settings.player_name)

    def update_with_match_history_data(self, amount: int):
        """ Gets match history and updates games tab and passes data to stats tab"""
        scheldule(self.got_match_history, get_full_match_history, amount)

    def got_match_history(self, match_history: List[Any]):
        if match_history is None:
            self.settigns_tab.aoe4net_error_msg()
            logger.warning("No match history data")
            return
        self.settigns_tab.message("")
        # self.stats_tab.update_other_stats(match_history)
        self.games_tab.update_widgets(match_history)

    def run_new_game_check(self, delayed_seconds: int = 0):
        """ Creates a new thread for a new api check"""
        scheldule(self.new_game, self.api_checker.check_for_new_game,
                  delayed_seconds)

    def new_game(self, game_data: Optional[Dict[str, Any]]):
        """Received new data from api check, passes data along and reruns the check"""
        if self.force_stop:
            return

        if game_data is None:
            pass
        elif "new_rating" in game_data:
            logger.info(
                f"Game finished (rating_timestamp: {game_data['timestamp']})")
            # self.graph_tab.run_update()
            # self.stats_tab.run_mode_update()
            self.update_with_match_history_data(2)

        elif 'server_down' in game_data:
            self.settigns_tab.aoe4net_error_msg()
        else:
            if settings.log_matches:
                log_match(game_data)
            processed = hf.process_game(game_data)
            logger.info(
                f"New live game (game_id: {game_data['game_id']} | mode: {game_data['kind']} | started: {game_data['started_at']})"
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
        self.settigns_tab.update_button.clicked.connect(
            partial(webbrowser.open, link))
        self.settigns_tab.update_button.show()

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

    ### Functionality dedicated to checking for PC waking, and resetting keyboard threads

    def check_waking(self):
        """ Manages all checks and keyboard resets"""
        scheldule(self.pc_waken_from_sleep, self.wait_for_wake)

    def wait_for_wake(self):
        """ Function that checks for a interruption"""
        interval = 10  # Seconds
        while True:
            start = time.time()
            # Wait 5s
            for _ in range(interval * 2):
                time.sleep(0.5)
                if self.force_stop:
                    return None
            # Check the difference
            diff = time.time() - start
            if diff > interval + 5:
                time.sleep(4)
                return diff - interval

    def pc_waken_from_sleep(self, diff: Optional[float]):
        """ This function is run when the PC is awoken """
        if diff is None:
            return

        logger.info(f'PC awoke! ({hf.strtime(diff, show_seconds=True)})')
        self.check_waking()

        # Check for new updates & reset keyboard threads
        self.check_for_new_version()
        self.reset_keyboard_threads()

    def reset_keyboard_threads(self):
        """ Resets keyboard thread"""
        global keyboard
        try:
            logger.info(f'Resetting keyboard thread')
            keyboard.unhook_all()
            keyboard = importlib.reload(keyboard)
            self.settigns_tab.init_hotkeys()
            self.build_order_tab.init_hotkeys()
        except Exception:
            logger.exception(f"Failed to reset keyboard")
