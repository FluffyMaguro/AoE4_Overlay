from typing import Any, Dict, List, Optional

from PyQt5 import QtCore, QtGui, QtWidgets

from overlay.logging_func import get_logger

logger = get_logger(__name__)


class StatsTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()

    # Map stats

    # Civ stats

    def update_data(self, match_history: List[Any]):
        print("NEW:", len(match_history))
