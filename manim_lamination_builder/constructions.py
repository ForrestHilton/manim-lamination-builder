"""
This file brings together methods that would be needed for describing certain finite laminations. Its methods are particularly un-trustworthy.
"""
from manim_lamination_builder.chord import Chord
from manim_lamination_builder.custom_json import custom_dump
from manim_lamination_builder.lamination import AbstractLamination, LeafLamination
from manim_lamination_builder.points import UnitPoint, NaryFraction
from manim_lamination_builder import Lamination
from typing import Iterable, List, Union
from manim_lamination_builder.visual_settings import get_color, VisualSettings
import scipy


def uniquely_color(list: List[UnitPoint]) -> List[UnitPoint]:
    "mutates and returns mutation"
    for i, p in enumerate(list):
        p.visual_settings = VisualSettings(point_color=get_color(i))
    return list


def unicritical_polygon(d, q) -> List[NaryFraction]:
    """gives the polygon rotational that has rotation number 1/q in degree d"""
    starting_point = NaryFraction.from_string(d, "_" + "0" * (q - 1) + "1")
    original_shape = [starting_point]
    # generate original shape
    for i in range(q - 1):
        point = original_shape[i]
        original_shape.append(point.after_sigma())

    return uniquely_color(original_shape)


def inverted_rotational_polygon(degree, order) -> List[NaryFraction]:
    """similar to unicritical_polygon, but returns a polygon whose rotation number is -1/q"""
    starting_point = NaryFraction.from_string(degree, "_" + "0" + "1" * (order - 1))
    original_shape = [starting_point]
    # generate original shape
    for i in range(order - 1):
        point = original_shape[i]
        original_shape.append(point.after_sigma())

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


def add_points_preimages(lam: Lamination) -> Lamination:
    "mutates and returns mutation"
    for i in range(len(lam.points)):
        lam.points += lam.points[i].pre_images()
    return lam


add_points_preimages(double_orbit)


def fussCatalan(i, n):
    """
    formula that appears in my poster
    """
    return scipy.special.binom(n * i, i) / ((n - 1) * i + 1)


def sigma(input: Union[UnitPoint, Chord, Iterable[UnitPoint], AbstractLamination]):
    if isinstance(input, UnitPoint):
        return input.after_sigma()
    elif isinstance(input, Chord):
        return Chord(input.min.after_sigma(), input.max.after_sigma())
    elif isinstance(input, AbstractLamination):
        return input.apply_function(sigma)
    else:
        return [p.after_sigma() for p in input]


def pollygons_are_one_to_one(lam: AbstractLamination) -> bool:
    "tests weather all the polygons in a lamination map one to one"
    _lam = lam if isinstance(lam, Lamination) else lam.to_polygons()
    return all(
        [len(set(pollygon)) == len(set(sigma(pollygon))) for pollygon in _lam.polygons]
    )
