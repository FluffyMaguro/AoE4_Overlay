import bisect
import math
import time
from typing import Iterable, List, Optional, Tuple, Union

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt

from overlay.logging_func import get_logger

logger = get_logger(__name__)

# Basic color palette as used in matplotlib
COLORS = ((51, 120, 182), (246, 126, 0), (65, 160, 33), (205, 35, 33),
          (145, 103, 191), (136, 86, 74), (220, 119, 195), (127, 127, 127),
          (187, 189, 0), (68, 190, 208))


def mmin(i: Iterable):
    return min(i) if i else 0


def mmax(i: Iterable):
    return max(i) if i else 1


def best_tick(span: float, most_ticks: float) -> float:
    """ Calculates a decent tick value given these parameters"""
    minimum = span / most_ticks
    magnitude = 10**math.floor(math.log(minimum, 10))
    residual = minimum / magnitude
    # This table must begin with 1 and end with 10
    table = [1, 1.5, 2, 3, 5, 7, 10]
    tick = table[bisect.bisect_right(table, residual)] if residual < 10 else 10
    return tick * magnitude


def get_ticks(vmin: float, vmax: float, tick_number: int = 10) -> List[float]:
    """ Calculates good tick values for data values `vmin` and `vmax`"""
    # Find the correct difference between ticks
    diff = best_tick(vmax - vmin, tick_number * 1.5)
    new_min = vmin - (vmin % diff)

    # Calculate the rest of the ticks
    ticks = []
    tick = new_min
    while tick <= vmax:
        if tick >= vmin:
            ticks.append(tick)
        tick += diff

    return ticks


class Box:
    """ Box used as a bounding box for a chart"""
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.padding = 10

    # A bunch of properties for inner box (this box minus padding)
    @property
    def inner_width(self) -> int:
        """ Inner box property"""
        return self.width - 2 * self.padding

    @property
    def inner_heigth(self) -> int:
        """ Inner box property"""
        return self.height - 2 * self.padding

    @property
    def x_start(self) -> int:
        """ Inner box property"""
        return self.x + self.padding

    @property
    def x_end(self) -> int:
        """ Inner box property"""
        return self.x + self.width - self.padding

    @property
    def y_start(self) -> int:
        """ Inner box property"""
        return self.y + self.padding

    @property
    def y_end(self) -> int:
        """ Inner box property"""
        return self.y + self.height - self.padding

    def draw(self,
             qp: QtGui.QPainter,
             edge_color: Union[str, Tuple[int, int, int, int],
                               Tuple[int, int, int]] = "#000",
             fill_color: Optional[Union[str, Tuple[int, int, int, int],
                                        Tuple[int, int, int]]] = None):
        """ Draws a chart bounding box"""

        if isinstance(edge_color, tuple):
            qp.setPen(QtGui.QColor(*edge_color))
        else:
            qp.setPen(QtGui.QColor(edge_color))

        if fill_color is None:
            qp.setBrush(QtGui.QBrush())
        else:
            if isinstance(fill_color, tuple):
                qp.setBrush(QtGui.QColor(*fill_color))
            else:
                qp.setBrush(QtGui.QColor(fill_color))

        qp.drawRect(self.x, self.y, self.width, self.height)


class GraphWidget(QtWidgets.QWidget):
    """ Main widget supporting graphs """
    def __init__(self):
        super().__init__()

        self.title: str = "title"
        self.background_color = (222, 222, 222)
        self.x_label: str = ""
        self.y_label: str = ""
        self._data = []
        self.x_is_timestamp: bool = False
        # Used for limiting x-axis. Max difference in x shown from the max value.
        self.max_x_diff: int = -1

    def paintEvent(self, event):
        """ Override for draw event"""
        try:
            self._draw_plot()
        except:
            logger.exception("Failed to plot")

    def plot(self,
             x: Iterable[float],
             y: Iterable[float],
             label: str = "",
             linewidth: float = 3,
             show: bool = True,
             index: int = -1):
        """ Simple line chart"""
        self._data.append({
            "type": "lineplot",
            "x": x,
            "y": y,
            "label": label,
            "linewidth": linewidth,
            "index": index,
            "show": show
        })

    def text(self, text: str, x: float, y: float, color: str = "black"):
        """ Add a text to the chart"""
        self._data.append({
            "type": "text",
            "text": text,
            "x": (x, ),
            "y": (y, ),
            "color": color,
            "show": True
        })

    def clear_data(self):
        """ Clears all current data"""
        self._data = []

    def set_plot_visibility(self, index: int, visible: bool):
        """ Changes the visibility of the plot 
        Args:
            `index` : index of the plot (given manually)
            `visible` : whether to show or hide
        """
        for item in self._data:
            if index == item.get("index", -1):
                item["show"] = visible
                return

    def calculate_limits(self) -> Tuple[float, float, float, float]:
        """ Calculates figure limits

        Returns:
            (x_min, x_max, y_min, y_max) """

        x_min = mmin([min(i['x']) for i in self._data if i["show"]])
        x_max = mmax([max(i['x']) for i in self._data if i["show"]])

        if self.max_x_diff > 0:
            # In case we are limiting maximum diff from x_max
            if x_max - x_min > self.max_x_diff:
                x_min = x_max - self.max_x_diff

            y_mins = []
            y_maxs = []
            for plot in self._data:
                if not plot['show']:
                    continue
                y = [
                    y for x, y in zip(plot['x'], plot['y'])
                    if x_max - x < self.max_x_diff
                ]
                y_mins.append(mmin(y))
                y_maxs.append(mmax(y))
            y_min = mmin(y_mins)
            y_max = mmax(y_maxs)
        else:
            y_min = mmin([min(i['y']) for i in self._data if i["show"]])
            y_max = mmax([max(i['y']) for i in self._data if i["show"]])

        return x_min, x_max, y_min, y_max

    @staticmethod
    def _set_font(qp: QtGui.QPainter,
                  size: int,
                  bold: bool = False,
                  italic: bool = False,
                  underline: bool = False,
                  color: Union[QtGui.QColor,
                               Qt.GlobalColor] = Qt.GlobalColor.black):
        pen = qp.pen()
        pen.setColor(color)
        qp.setPen(pen)

        font = qp.font()
        font.setItalic(italic)
        font.setBold(bold)
        font.setUnderline(underline)
        font.setPointSize(size)
        qp.setFont(font)

    def _format_ticks(self,
                      value,
                      percent: bool = False,
                      timestamp: bool = False) -> str:
        if timestamp and self.max_x_diff > 0:
            return time.strftime("%b %d, %I:%M%p", time.localtime(value))
        if timestamp:
            return time.strftime("%b %d, %y", time.localtime(value))
        elif percent:
            return f"{value:.1%}"
        elif -1 < value < 1 and value != 0:
            return f"{value:.2f}"
        elif value > 10000:
            return f"{value:.2E}"
        return f"{value:.0f}"

    def _draw_line(self,
                   qp: QtGui.QPainter,
                   points: List[Tuple[int, int]],
                   linewidth: int = 2,
                   linestyle: Qt.PenStyle = Qt.PenStyle.SolidLine,
                   color: Union[QtGui.QColor,
                                Qt.GlobalColor] = Qt.GlobalColor.black):
        qp.setPen(QtGui.QPen(color, linewidth, linestyle))
        for idx, point in enumerate(points):
            # Skip the first one
            if not idx:
                continue
            qp.drawLine(*points[idx - 1], *point)

    def _draw_plot(self):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setPen(QtGui.QColor(0, 0, 0))

        # Bounding box
        x_offset_left = 80
        x_offset_right = 20
        y_offset_top = 25
        y_offset_bottom = 50
        box_width = self.width() - x_offset_left - x_offset_right
        box_height = self.height() - y_offset_top - y_offset_bottom

        box = Box(x_offset_left, y_offset_top, box_width, box_height)
        box.draw(qp, edge_color="#000", fill_color=self.background_color)

        # Calculate xlim, ylim
        x_min, x_max, y_min, y_max = self.calculate_limits()

        # Transforming into image coordinates
        x_scaling = box.inner_width / (x_max - x_min)
        y_diff = y_max - y_min
        y_diff = y_diff if y_diff else 1
        y_scaling = box.inner_heigth / y_diff

        def trans(x: float, y: float) -> Tuple[int, int]:
            """ Transforms a point from data to coordinates on image"""
            x_new = (x - x_min) * x_scaling + box.x_start
            y_new = box.y_end - (y - y_min) * y_scaling
            return int(x_new), int(y_new)

        # X-ticks
        x_ticks = get_ticks(x_min, x_max, 5)
        self._set_font(qp, 10)
        for x in x_ticks:
            xn, _ = trans(x, y_min)
            xn1 = (xn, box.y_end + box.padding + 1)
            xn2 = (xn, int(xn1[1] + self.height() / 100))
            self._draw_line(qp, [xn1, xn2], linewidth=1)
            rect = QtCore.QRect(xn - 100, box.y + box.height, 200, 30)
            qp.drawText(rect, Qt.AlignmentFlag.AlignCenter,
                        self._format_ticks(x, timestamp=self.x_is_timestamp))

            # Grid
            self._draw_line(qp, [(xn, box.y + 1),
                                 (xn, box.y + box.height - 1)],
                            linewidth=1,
                            color=QtGui.QColor("#c9c9c9"))

        # Y-ticks
        y_ticks = get_ticks(y_min, y_max, 5)
        for y in y_ticks:
            _, yn = trans(x_min, y)
            yn1 = (box.x, yn)
            yn2 = (int(box.x - self.height() / 100), yn)
            self._draw_line(qp, [yn1, yn2], linewidth=1)
            rect = QtCore.QRect(box.x - 110, yn - 16, 100, 30)
            qp.drawText(rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                        self._format_ticks(y))

            # Grid
            self._draw_line(qp, [(box.x + 1, yn), (box.x + box.width - 1, yn)],
                            linewidth=1,
                            color=QtGui.QColor("#c9c9c9"))

        # Draw data
        used_colors = []
        self._set_font(qp, 10)
        for idx, data in enumerate(self._data):
            if not data["show"]:
                continue
            elif data["type"] == "lineplot":
                points = [
                    trans(x, y) for x, y in zip(data['x'], data['y'])
                    if self.max_x_diff <= 0 or x_max - x < self.max_x_diff
                ]
                used_colors.append(QtGui.QColor(*COLORS[idx % len(COLORS)]))
                self._draw_line(qp,
                                points,
                                color=used_colors[-1],
                                linewidth=data['linewidth'])

                # For limited range draw points as well
                if self.max_x_diff > 0:
                    qp.setPen(QtGui.QPen(Qt.GlobalColor.black, 3))
                    [qp.drawEllipse(x - 2, y - 2, 4, 4) for x, y in points]

            elif data["type"] == "text":
                point = trans(data['x'][0], data['y'][0])
                rect = QtCore.QRect(*point, 200, 20)
                qp.setPen(QtGui.QColor(data['color']))
                qp.drawText(rect, Qt.AlignmentFlag.AlignCenter, data['text'])

        # Legend
        labels = [
            len(i['label']) for i in self._data
            if i['type'] != "text" and i["show"]
        ]
        item_num = len(labels)
        text_len = max(labels) if labels else 0
        qp.setBrush(QtGui.QColor("#fff"))
        qp.setPen(QtGui.QColor("black"))
        textbox = QtCore.QRect(box.x_start + box.width // 200,
                               box.y_start + box.width // 200,
                               35 + text_len * 7, 27 * item_num)
        qp.drawRect(textbox)
        textbox.setLeft(textbox.left() + 30)
        textbox.setTop(textbox.top() + 5)

        i = 0
        for item in self._data:
            if not item["show"] or item["type"] == "text":
                continue
            points = [(textbox.x() - 20, textbox.y() + 10),
                      (textbox.x() + -5, textbox.y() + 10)]
            self._draw_line(qp, points, color=used_colors[i], linewidth=4)
            self._set_font(qp, 10)
            qp.drawText(textbox, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                        item["label"])
            textbox.setTop(textbox.top() + 25)
            i += 1

        # Change font for axis labels
        self._set_font(qp, 12)

        # X-label
        qp.setPen(QtGui.QColor("black"))
        rect = QtCore.QRect(box.x + box.width // 2 - 100,
                            self.height() - 25, 200, 25)
        qp.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.x_label)

        # Y-label
        qp.rotate(-90)
        rect = QtCore.QRect(-box.y - box.height // 2 - 100, 5, 200, 25)
        qp.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.y_label)
        qp.rotate(90)

        # Title
        self._set_font(qp, 14)
        rect = QtCore.QRect(box.x + box.width // 2 - 500, -2, 1000, 30)
        qp.drawText(rect, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter,
                    self.title)

        qp.end()
