"""
Basic plotting built upon Pillow library.
Useful when you don't want to include matplotlib or pyqtchart as they require numpy,
and the installation size gets big.

"""

import itertools
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from PIL import Image, ImageDraw, ImageFont
from PyQt5 import QtGui

from overlay.helper_func import file_path

FONT_TITLE = ImageFont.truetype(file_path("src/font/arial.ttf"), 72)
FONT_LABEL = ImageFont.truetype(file_path("src/font/arial.ttf"), 60)

COLORS = ((51, 120, 182), (246, 126, 0), (65, 160, 33), (205, 35, 33),
          (145, 103, 191), (136, 86, 74), (220, 119, 195), (127, 127, 127),
          (187, 189, 0), (68, 190, 208))


def pil2pixmap(im: Image.Image) -> QtGui.QPixmap:
    """ Coverts PIL Image to a PyQt pixmap"""
    if im.mode == "RGB":
        r, g, b = im.split()
        im = Image.merge("RGB", (b, g, r))
    elif im.mode == "RGBA":
        r, g, b, a = im.split()
        im = Image.merge("RGBA", (b, g, r, a))
    elif im.mode == "L":
        im = im.convert("RGBA")
    im2 = im.convert("RGBA")
    data = im2.tobytes("raw", "RGBA")
    qim = QtGui.QImage(data, im.size[0], im.size[1],
                       QtGui.QImage.Format_ARGB32)
    pixmap = QtGui.QPixmap.fromImage(qim)
    return pixmap


class Figure:
    """ Figure of a graph.

    It renders at a higher resolution and then downscales at the end.
    """
    def __init__(self, title: str, width: int, height: int):
        self.title: str = title
        self.width = width * 4
        self.height = height * 4

        self.background_color = (222, 222, 222)
        self.x_label: str = ""
        self.y_label: str = ""
        self._data = []

    def plot(self,
             x: Iterable[float],
             y: Iterable[float],
             label: str = "",
             linewidth: float = 1.0):
        """ Simple line chart"""
        self._data.append({
            "type": "lineplot",
            "x": x,
            "y": y,
            "label": label,
            "linewidth": linewidth
        })

    def text(self, text: str, x: float, y: float):
        """ Add a text to the chart"""
        self._data.append({
            "type": "text",
            "text": text,
            "x": (x, ),
            "y": (y, )
        })

    def calculate_limits(self) -> Tuple[float, float, float, float]:
        """ Calculates figure limits

        Returns:
            (x_min, x_max, y_min, y_max) """

        x_min = min([min(i['x']) for i in self._data])
        x_max = max([max(i['x']) for i in self._data])
        y_min = min([min(i['y']) for i in self._data])
        y_max = max([max(i['y']) for i in self._data])
        return x_min, x_max, y_min, y_max

    def get_image(self) -> Image.Image:
        im = Image.new("RGB", (self.width, self.height), self.background_color)
        draw = ImageDraw.Draw(im)

        # Title
        draw.text((self.width / 2, self.height * 0.015),
                  self.title,
                  align='center',
                  font=FONT_TITLE,
                  fill="black",
                  anchor="ma")

        # Bounding box
        x_offset_left = self.width * 0.06
        x_offset_right = self.width * 0.02
        y_offset = 150
        y_end_offset = 170

        draw.rectangle((x_offset_left, y_offset, self.width - x_offset_right,
                        self.height - y_end_offset),
                       outline=(0, 0, 0),
                       width=3)

        padding = 30  # Padding inside the box
        box_width = self.width - (x_offset_left + x_offset_right) - 2 * padding
        box_height = self.height - y_offset - y_end_offset - 2 * padding

        # Calculate xlim, ylim
        x_min, x_max, y_min, y_max = self.calculate_limits()

        # Transforming into image coordinates
        x_scaling = box_width / (x_max - x_min)
        y_scaling = box_height / (y_max - y_min)

        def transform(x: float, y: float) -> Tuple[float, float]:
            """ Transforms a point from data to coordinates on image"""
            x_new = (x - x_min) * x_scaling + x_offset_left + padding
            y_new = y_offset + padding + box_height - (y - y_min) * y_scaling
            return x_new, y_new

        # Draw data
        for idx, data in enumerate(self._data):
            if data["type"] == "lineplot":
                points = (transform(x, y)
                          for x, y in zip(data['x'], data['y']))
                points = tuple(itertools.chain(*points))
                draw.line(points, fill=COLORS[idx % len(COLORS)], width=8)
            elif data["type"] == "text":
                point = transform(data['x'][0], data['y'][0])
                draw.text(point, data['text'], font=FONT_LABEL, fill=0)

        # !!!!Ticks
        # !!!!Grid
        # !!!!Legend

        # X-label
        draw.text((self.width / 2, self.height - y_end_offset + 20),
                  self.x_label,
                  align='center',
                  font=FONT_LABEL,
                  fill="black",
                  anchor="ma")

        # Y-label
        im = im.rotate(-90, expand=True)
        ImageDraw.Draw(im).text((self.height / 2, x_offset_left / 2),
                                self.y_label,
                                align='center',
                                font=FONT_LABEL,
                                fill="black",
                                anchor="md")
        im = im.rotate(90, expand=True)
        return im.resize((int(im.size[0] / 4), int(im.size[1] / 4)))

    def get_pixmap(self) -> QtGui.QPixmap:
        return pil2pixmap(self.get_image())
