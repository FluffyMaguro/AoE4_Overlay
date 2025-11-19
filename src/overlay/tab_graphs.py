from typing import Any, Dict, List

from PyQt6 import QtGui, QtWidgets

from overlay.api_checking import get_rating_history
from overlay.graph_widget import GraphWidget
from overlay.logging_func import get_logger
from overlay.settings import settings
from overlay.worker import scheldule

logger = get_logger(__name__)


class GraphTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        self.plot_visibility: Dict[int, bool] = dict()

        # Graph
        self.graph = GraphWidget()
        self.graph.title = "Rating history"
        self.graph.x_label = "Date"
        self.graph.y_label = "Rating"
        self.graph.x_is_timestamp = True
        layout.addWidget(self.graph)

    def run_update(self):
        """ Gets new data and updates graphs"""
        scheldule(self.plot_data, self.get_all_rating_history)

    def change_plot_visibility(self, index: int, action: QtGui.QAction):
        """ Updates plot visibility for given `index`"""
        # Save plot visibility (needed to correctly update after new data is obtained)
        self.plot_visibility[index + 1] = action.isChecked()
        self.graph.set_plot_visibility(index + 1, action.isChecked())
        self.graph.update()

    def limit_to_day(self, action: QtGui.QAction):
        """ Limits the graph x-axis to 1 day if `action` is checked"""
        self.graph.max_x_diff = 24 * 60 * 60 if action.isChecked() else -1
        self.graph.update()

    @staticmethod
    def get_all_rating_history() -> Dict[int, List[Any]]:
        """ Gets rating history for all game modes"""
        result = dict()
        for id in range(17, 21):
            result[id] = get_rating_history(id, amount=150)
        return result

    def plot_data(self, data: Dict[int, List[Any]]):
        if data is None:
            logger.warning("No graph data")
            return
        self.graph.title = f"Rating history ({settings.player_name})"
        self.graph.clear_data()
        for id, values in data.items():
            if not values:
                continue
            index = id - 16
            label = f"{index}v{index}"
            y = [i['rating'] for i in values]
            x = [i['timestamp'] for i in values]
            self.graph.plot(x,
                            y,
                            label=label,
                            index=index,
                            show=self.plot_visibility.get(index, True))

        self.graph.update()
