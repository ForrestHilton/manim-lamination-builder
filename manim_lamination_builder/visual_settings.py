from manim.utils.color import Colors
from pydantic import BaseModel

colors_list = [
    Colors.pure_red,
    Colors.pure_green,
    Colors.pure_blue,
    Colors.yellow,
    Colors.purple,
]


def get_color(i: int):
    if i >= len(colors_list):
        # TODO: test if dark theme
        return Colors.white
    return colors_list[i]


class VisualSettings(BaseModel):
    point_color: Colors = Colors.red
    stroke_color: Colors = Colors.black
    polygon_color: Colors = Colors.blue_c
    point_size: float = 0.04
    stroke_width: float = 2

    @staticmethod
    def default():
        return VisualSettings()
