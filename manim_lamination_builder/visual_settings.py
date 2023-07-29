from copy import deepcopy
from typing import List
from manim.utils.color import Colors

from manim_lamination_builder.points import UnitPoint

colors_list = [
    Colors.pure_red,
    Colors.pure_green,
    Colors.pure_blue,
    Colors.yellow,
    Colors.purple,
]

def get_color(i:int):
    if i >= len(colors_list):
        return Colors.black
    return colors_list[i]


class VisualSettings:
    point_color: Colors
    stroke_color: Colors
    polygon_color: Colors
    point_size: float
    stroke_width: float

    def __init__(
        self, point_color = Colors.red, stroke_color = Colors.black, polygon_color = Colors.blue_c, point_size = 0.04, stroke_width = 4):
        self.point_color = point_color
        self.stroke_color = stroke_color # TODO
        self.polygon_color = polygon_color 
        self.point_size = point_size
        self.stroke_width = stroke_width# TODO

    @staticmethod
    def default():
        return VisualSettings()

def uniquely_color(list:List[UnitPoint]) -> List[UnitPoint]:
    ret = deepcopy(list)
    for i,p in enumerate(list):
        p.visual_settings.point_color = get_color(i)
    return ret
