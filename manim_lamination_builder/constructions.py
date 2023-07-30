"""
This file brings together methods that would be needed for describing certain finite laminations. Its methods are particularly un-trustworthy.
"""
from manim_lamination_builder.custom_json import custom_dump
from manim_lamination_builder.points import UnitPoint, NaryFraction
from manim_lamination_builder import Lamination
from typing import List
from manim_lamination_builder.visual_settings import get_color, VisualSettings


def uniquely_color(list: List[UnitPoint]) -> List[UnitPoint]:
    "mutates and returns mutation"
    for i, p in enumerate(list):
        p.visual_settings = VisualSettings(point_color=get_color(i))
    return list


def unicritical_polygon(degree, order) -> List[NaryFraction]:
    starting_point = NaryFraction.from_string(degree, "_" + "0" * (order - 1) + "1")
    original_shape = [starting_point]
    # generate original shape
    for i in range(order - 1):
        point = original_shape[i]
        original_shape.append(point.after_sigma().cleared())

    return uniquely_color(original_shape)


def insert_criticality(x: Lamination, at: NaryFraction) -> Lamination:
    "probably broken method"
    assert sum(at.repeating) == 0 and len(at.exact) == 1

    def shift(x: NaryFraction) -> NaryFraction:
        return NaryFraction(
            x.base + 1,
            [i if i < at.to_float() * at.base else i + 1 for i in x.exact],
            [i if i < at.to_float() * at.base else i + 1 for i in x.repeating],
        )

    ret = x.apply_function(shift)
    x.radix += 1
    return ret


start = Lamination(
    [[NaryFraction.from_string(3, "_012"), NaryFraction.from_string(3, "_112")]],
    [],
    3,
)

insertion_points = [
    NaryFraction.from_string(3, "2011"),
    NaryFraction.from_string(3, "0"),
]

double_orbit = Lamination(
    [
        uniquely_color(
            start.polygons[0]
            + start.apply_function(lambda x: x.after_sigma()).polygons[0]
            + start.apply_function(lambda x: x.after_sigma())
            .apply_function(lambda x: x.after_sigma())
            .polygons[0]
        )
    ],
    [],
    3,
)

double_orbit.auto_populate()

if __name__ == "__main__":
    from manim_lamination_builder import Main
    from manim_lamination_builder.main import config
    print(custom_dump(double_orbit))

    config.preview = True
    Main([double_orbit]).render()
