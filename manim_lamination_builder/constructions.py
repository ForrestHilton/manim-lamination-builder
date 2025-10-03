"""
This file brings together methods that would be needed for describing certain finite laminations. Its methods are particularly un-trustworthy.
"""

from typing import Iterable, List, TypeVar

import scipy

from manim_lamination_builder.chord import Chord
from manim_lamination_builder.custom_json import custom_dump
from manim_lamination_builder.lamination import (
    AbstractLamination,
    GapLamination,
    Polygon,
    sigma,
)
from manim_lamination_builder.points import Angle, NaryFraction
from manim_lamination_builder.visual_settings import VisualSettings, get_color


def uniquely_color(list: Polygon) -> Polygon:
    "mutates and returns mutation"
    for i, p in enumerate(list):
        p.visual_settings = VisualSettings(point_color=get_color(i))
    return list


def unicritical_polygon(d, q) -> tuple[NaryFraction, ...]:
    """gives the polygon rotational that has rotation number 1/q in degree d.
    Always uses NaryFraction"""
    starting_point = NaryFraction.from_string(d, "_" + "0" * (q - 1) + "1")
    original_shape: List[NaryFraction] = [starting_point]
    # generate original shape
    for i in range(q - 1):
        point: NaryFraction = original_shape[i]
        original_shape.append(point.after_sigma())

    return uniquely_color(tuple(original_shape))  # type: ignore


def inverted_rotational_polygon(degree, order) -> tuple[NaryFraction, ...]:
    """similar to unicritical_polygon, but returns a polygon whose rotation number is -1/q"""
    starting_point = NaryFraction.from_string(degree, "_" + "0" + "1" * (order - 1))
    original_shape = [starting_point]
    # generate original shape
    for i in range(order - 1):
        point = original_shape[i]
        original_shape.append(point.after_sigma())

    return uniquely_color(tuple(original_shape))  # type: ignore


def insert_criticality(x: GapLamination, at: NaryFraction) -> GapLamination:
    "probably broken method"  # TODO
    assert sum(at.repeating) == 0 and len(at.exact) == 1

    def shift(x: Angle) -> NaryFraction:
        assert isinstance(x, NaryFraction)  # TODO
        return NaryFraction(
            degree=x.degree + 1,
            exact=[i if i < at.to_float() * at.degree else i + 1 for i in x.exact],
            repeating=[
                i if i < at.to_float() * at.degree else i + 1 for i in x.repeating
            ],
        )

    ret = x.apply_function(shift)
    x.degree += 1
    return ret


start = GapLamination(
    polygons=[
        [NaryFraction.from_string(3, "_012"), NaryFraction.from_string(3, "_112")]
    ],
    points=[],
    degree=3,
)

insertion_points = [
    NaryFraction.from_string(3, "2011"),
    NaryFraction.from_string(3, "0"),
]

double_orbit = GapLamination(
    polygons=[
        uniquely_color(
            start.polygons[0]
            + start.apply_function(lambda x: x.after_sigma()).polygons[0]
            + start.apply_function(lambda x: x.after_sigma())
            .apply_function(lambda x: x.after_sigma())
            .polygons[0]
        )
    ],
    points=[],
    degree=3,
).auto_populated()


def add_points_preimages(lam: GapLamination) -> GapLamination:
    "Mutates and returns mutation"
    for i in range(len(lam.points)):
        lam.points += lam.points[i].pre_images()
    return lam


#
# add_points_preimages(double_orbit)


def fussCatalan(i, n):
    "Formula that appears in my poster."
    return scipy.special.binom(n * i, i) / ((n - 1) * i + 1)


def pollygons_are_one_to_one(lam: AbstractLamination) -> bool:
    "Tests weather all the polygons in a lamination map one to one"
    _lam = lam if isinstance(lam, GapLamination) else lam.to_polygons()
    return all(
        [len(set(pollygon)) == len(set(sigma(pollygon))) for pollygon in _lam.polygons]
    )
