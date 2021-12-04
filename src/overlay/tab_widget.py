import webbrowser
from functools import partial

from PyQt5 import QtWidgets

from overlay.graph_tab import GraphTab
from overlay.helper_func import version_check
from overlay.logging_func import get_logger
from overlay.main_widget import MainTab
from overlay.match_history_tab import MatchHistoryTab

logger = get_logger(__name__)


class TabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.match_history_tab = MatchHistoryTab(self)
        self.graph_tab = GraphTab(self)
        # Need this one defined the last
        self.main_tab = MainTab(self)

        self.addTab(self.main_tab, "Setting")
        self.addTab(self.match_history_tab, "Games")
        self.addTab(self.graph_tab, "Graphs")

    def check_for_new_version(self, version: str):
        """ Checks for a new version, creates a button if there is one """
        link = version_check(version)
        if not link:
            return
        logger.info("New version available!")
        self.update_button.clicked.connect(partial(webbrowser.open, link))
        self.update_button.show()
