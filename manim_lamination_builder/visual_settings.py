from manim.utils.color.core import ManimColor
from manim import RED, BLACK, BLUE_C, GREEN, BLUE, YELLOW, PURPLE, WHITE
from pydantic import BaseModel, ConfigDict

colors_list = [RED, GREEN, BLUE, YELLOW, PURPLE]


def get_color(i: int):
    if i >= len(colors_list):
        # TODO: test if dark theme
        return WHITE
    return colors_list[i]


class VisualSettings(BaseModel):
    point_color: ManimColor = RED
    stroke_color: ManimColor = BLACK
    polygon_color: ManimColor = BLUE_C
    point_size: float = 0.04
    stroke_width: float = 2
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @staticmethod
    def default():
        return VisualSettings()
