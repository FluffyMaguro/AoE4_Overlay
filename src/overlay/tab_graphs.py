from typing import Any, Dict, List

from PyQt5 import QtWidgets

from overlay.api_checking import get_rating_history
from overlay.graph_widget import GraphWidget
from overlay.logging_func import get_logger
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

        self.get_new_data()

    def get_new_data(self):
        """ Gets new data and updates graphs"""
        scheldule(self.plot_data, self.get_all_rating_history)

    def change_plot_visibility(self, index: int, action: QtWidgets.QAction):
        """ Updates plot visibility for given `index`"""
        # Save plot visibility (needed to correctly update after new data is obtained)
        self.plot_visibility[index + 1] = action.isChecked()
        self.graph.set_plot_visibility(index + 1, action.isChecked())
        self.graph.update()

    @staticmethod
    def get_all_rating_history() -> Dict[int, List[Any]]:
        """ Gets rating history for all game modes"""
        result = dict()
        for id in range(17, 21):
            result[id] = get_rating_history(id, amount=50)
        return result

    def plot_data(self, data: Dict[int, List[Any]]):
        self.graph.clear_data()
        for id, values in data.items():
            if not values:
                continue
            index = id - 16
            label = f"{index}v{index} rating"

            y = [i['rating'] for i in values]
            x = [i['timestamp'] for i in values]
            self.graph.plot(x,
                            y,
                            label=label,
                            index=index,
                            show=self.plot_visibility.get(index, True))

        self.graph.update()
