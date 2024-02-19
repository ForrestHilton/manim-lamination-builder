from manim import PURE_RED, PURE_GREEN, PURE_BLUE, YELLOW, PURPLE, RED, BLACK, BLUE_C
from manim.utils.color.core import ManimColor
from pydantic import BaseModel

colors_list = [PURE_RED, PURE_GREEN, PURE_BLUE, YELLOW, PURPLE]


def get_color(i: int):
    if i >= len(colors_list):
        # TODO: test if dark theme
        return ManimColors.white
    return colors_list[i]


class VisualSettings(BaseModel):
    point_color: ManimColor = RED
    stroke_color: ManimColor = BLACK
    polygon_color: ManimColor = BLUE_C
    point_size: float = 0.04
    stroke_width: float = 2

    @staticmethod
    def default():
        return VisualSettings()
