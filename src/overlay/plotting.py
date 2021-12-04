"""
Basic plotting built upon Pillow library.
I don't want to include matplotlib or pyqtchart as they require numpy,
and the installation size gets big.

"""

from typing import Any, Dict, Iterable, List, Optional, Union, Tuple

from PIL import Image, ImageDraw, ImageFont
from PyQt5 import QtGui

from overlay.helper_func import file_path

FONT_TITLE = ImageFont.truetype(file_path("src/font/arial.ttf"), 24)


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
    """ Figure of a graph """
    def __init__(self, title: str, width: int, height: int):
        self.title = title
        self.width = width
        self.height = height
        self.background_color = (222, 222, 222)

        self.data = []

    def plot(self,
             x: Iterable[Union[float, int]],
             y: Iterable[Union[float, int]],
             label: str = "",
             linewidth: float = 1.0):
        """ Simple line chart"""
        self.data.append({
            "x": x,
            "y": y,
            "label": label,
            "linewidth": linewidth
        })

    def calculate_limits(self) -> Tuple[float, float, float, float]:
        """ Calculates figure limits

        Returns:
            (x_min, x_max, y_min, y_max) """

        x_min = min([min(i['x']) for i in self.data])
        x_max = max([max(i['x']) for i in self.data])
        y_min = min([min(i['y']) for i in self.data])
        y_max = max([max(i['y']) for i in self.data])
        return x_min, x_max, y_min, y_max

    def get_image(self) -> Image.Image:
        im = Image.new("RGB", (self.width, self.height), self.background_color)

        # Title
        draw = ImageDraw.Draw(im)
        draw.text((self.width / 2, self.height * 0.01),
                  self.title,
                  align='center',
                  font=FONT_TITLE,
                  fill="black",
                  anchor="ma")

        # Bounding box
        x_offset = self.width * 0.02
        draw.rectangle(
            (x_offset, 40, self.width - x_offset, self.height - 100),
            outline=0,
            width=1)

        # Calculate xlim, ylim
        x_min, x_max, y_min, y_max = self.calculate_limits()
        x_box = self.width - 2 * x_offset
        y_box = self.height - 140
        x_scaling = 0
        y_scaling = 0

        def transform(x: float, y: float) -> Tuple[float, float]:
            """ Transforms a point from data to coordinates on image"""
            x - x_min

        # Scale
        # Draw plots
        # Place Legend
        # Actually draw image here

        return im

    def get_pixmap(self) -> QtGui.QPixmap:
        return pil2pixmap(self.get_image())
