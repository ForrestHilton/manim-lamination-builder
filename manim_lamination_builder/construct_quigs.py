import colorsys
import math
from operator import xor
from typing import Callable, Iterable, List

import numpy as np
from manim import *
from manim import ImageMobject, Scene, tempconfig
from PIL import Image

from manim_lamination_builder.chord import Chord
from manim_lamination_builder.lamination import LeafLamination
from manim_lamination_builder.main import Main
from manim_lamination_builder.malaugh import Psi, psi
from manim_lamination_builder.orbits import Orbit
from manim_lamination_builder.points import Angle, FloatWrapper, NaryFraction, sigma
from manim_lamination_builder.visual_settings import VisualSettings


def angle_to_color(angle_rotations: Angle):
    """
    Convert an angle (in rotations, 0 to 1) to an RGB tuple scaled 0–255.
    1 rotation = full hue sweep through the color wheel.
    """
    rgb = colorsys.hsv_to_rgb(angle_rotations.to_float(), 1, 1)
    return ManimColor(tuple(int(round(c * 255.0)) for c in rgb))


class ColorWheel(Scene):
    def construct(self):
        size = 400
        im = Image.new("RGB", (size, size))
        radius = size / 2
        cx, cy = radius, radius
        pix = im.load()

        for x in range(size):
            for y in range(size):
                rx = x - cx
                ry = y - cy
                s = (rx**2 + ry**2) ** 0.5 / radius
                if s < 0.95:
                    pix[x, y] = (0, 0, 0)
                elif s <= 1.0:
                    # Convert angle from atan2 to rotations in [0, 1)
                    angle_rotations = ((math.atan2(ry, rx) / math.pi) + 1.0) / 2.0
                    pix[x, y] = angle_to_color(FloatWrapper(angle_rotations, 2))

        wheel = ImageMobject(im).scale(2)
        self.add(wheel)


def color(v: Iterable[Angle]) -> List[Angle]:
    v = list(v)
    for p in v:
        color = angle_to_color(p)
        settings = VisualSettings(
            point_color=color, stroke_color=color, polygon_color=color
        )
        p.visual_settings = settings
    return v


class GenerateLams(Scene):
    "displays all the laminations in sorted order generated from the points using the function provided"

    def __init__(
        self, points: Iterable[Angle], quig_function: Callable[[Angle], LeafLamination]
    ):
        self.points = points
        self.quig_function = quig_function
        super().__init__()

    def construct(self):
        for point in sorted(self.points):
            self.add(self.quig_function(point).build(2))
            self.wait(0.1)
            self.clear()


def base_strings(length, radix):
    if radix < 2:
        raise ValueError("radix must be at least 2")
    for i in range(radix**length):
        n = i
        chars = []
        for _ in range(length):
            chars.append(n % radix)
            n //= radix
        yield tuple(reversed(chars))


def periodic_points(max_period=6):
    rets = cumulative_base_strings(max_period, 2)
    return set([NaryFraction(exact=(), repeating=tuple(str), degree=2) for str in rets])


def pre_iterates_of_zero(max_preperiod=6):
    strs = cumulative_base_strings(max_preperiod, 2)
    return set([NaryFraction(exact=tuple(str), repeating=(), degree=2) for str in strs])


def cumulative_base_strings(max_length, radix):
    for length in range(max_length):
        for string in base_strings(length, radix):
            yield string


def duplicate_by_fixed_points(lam: LeafLamination) -> LeafLamination:
    d = lam.degree
    leaves = []
    for i in range(lam.degree):
        for leaf in lam.leafs:
            leaves.append(Chord(leaf.min + i / (d - 1), leaf.max + i / (d - 1)))

    return LeafLamination(points=[], leafs=leaves, degree=lam.degree)


def _in_closed_hole_away_from_zero(lam: LeafLamination, x: Angle) -> bool:
    "returns true if x is under a leaf with respect to zero, on any leaf endpoint"
    for leaf in lam.leafs:
        if x in [leaf.min, leaf.max]:
            return True
        length = leaf.max.to_float() - leaf.min.to_float()
        if length == 0.5:
            if x < 0.5:
                return True
        if (leaf.min < x and x < leaf.max) ^ (length > 0.5):
            return True
    return False


def Psi_lam(
    lam: LeafLamination,
    insertion_point: Angle,
    additional_leaves=False,
    added_pullbacks=6,
) -> LeafLamination:
    assert insertion_point.degree == lam.degree
    leaves = []
    for leaf in lam.leafs:
        leaves.append(
            Chord(
                psi(leaf.min, insertion_point),
                psi(leaf.max, insertion_point, lesser=False),
            )
        )

    if additional_leaves:
        d = lam.degree
        eventual_preimages = []
        for exact in cumulative_base_strings(added_pullbacks, d):
            eventual_preimages.append(
                NaryFraction(
                    exact=exact + insertion_point.exact,
                    repeating=insertion_point.repeating,
                    degree=d,
                    visual_settings=insertion_point.visual_settings,
                )
            )
        eventual_preimages = filter(
            lambda x: not _in_closed_hole_away_from_zero(lam, x),
            eventual_preimages,
        )

        for p in eventual_preimages:
            leaves.append(Psi(p, insertion_point))
    return LeafLamination(points=[], leafs=leaves, degree=lam.degree + 1)


def build_quig(insertion_point: NaryFraction) -> LeafLamination:
    return Psi_lam(LeafLamination.empty(2), insertion_point, additional_leaves=True)


def cubic_co_majors(insertion_points: List[Angle]) -> LeafLamination:
    leaves = []
    for insertion_point in insertion_points:
        sibling = insertion_point.other_sibling()[0]
        leaves.append(Psi(sibling, insertion_point))
    return LeafLamination(points=[], leafs=leaves, degree=3)


def cubic_majors(insertion_points: List[Angle]) -> LeafLamination:
    leaves = []
    for insertion_point in insertion_points:
        leaves.append(Psi(insertion_point, insertion_point))
    return LeafLamination(points=[], leafs=leaves, degree=3)


def cubic_minors(insertion_points: List[Angle]) -> LeafLamination:
    leaves = []
    for insertion_point in insertion_points:
        leaves.append(sigma(Psi(insertion_point, insertion_point)))
    return LeafLamination(points=[], leafs=leaves, degree=3)


def short_quig(insertion_point: NaryFraction) -> LeafLamination:
    "takes a quadratic insertion point and performs two insertions"
    assert insertion_point.degree == 2
    cubic = build_quig(insertion_point)
    new_insertion_point = psi(insertion_point, insertion_point)
    return Psi_lam(cubic, new_insertion_point)


def short_co_majors(insertion_points: List[Angle]) -> LeafLamination:
    leaves = []
    for insertion_point in insertion_points:
        sibling = insertion_point.other_sibling()[0]
        cubic_comaj = Psi(sibling, insertion_point)
        new_insertion_point = psi(insertion_point, insertion_point)
        leaves.append(Psi(cubic_comaj, new_insertion_point))
    return LeafLamination(points=[], leafs=leaves, degree=3)


def short_majors(insertion_points: List[Angle]) -> LeafLamination:
    leaves = []
    for insertion_point in insertion_points:
        cub_maj = Psi(insertion_point, insertion_point)
        new_insertion_point = psi(insertion_point, insertion_point)
        leaves.append(Psi(cub_maj, new_insertion_point))
    return LeafLamination(points=[], leafs=leaves, degree=3)


def short_minors(insertion_points: List[Angle]) -> LeafLamination:
    leaves = []
    for insertion_point in insertion_points:
        cub_maj = Psi(insertion_point, insertion_point)
        new_insertion_point = psi(insertion_point, insertion_point)
        leaves.append(sigma(Psi(cub_maj, new_insertion_point)))
    return LeafLamination(points=[], leafs=leaves, degree=3)


def long_quig(insertion_point: NaryFraction) -> LeafLamination:
    "takes a quadratic insertion point and performs two insertions"
    assert insertion_point.degree == 2
    cubic = build_quig(insertion_point)
    new_insertion_point = psi(insertion_point.other_sibling()[0], insertion_point)
    return Psi_lam(cubic, new_insertion_point, additional_leaves=True)


def long_co_majors(insertion_points: List[Angle]) -> LeafLamination:
    leaves = []
    for insertion_point in insertion_points:
        sibling = insertion_point.other_sibling()[0]
        cubic_comaj = Psi(sibling, insertion_point)
        new_insertion_point = psi(sibling, insertion_point)
        leaves.append(Psi(cubic_comaj, new_insertion_point))
    return LeafLamination(points=[], leafs=leaves, degree=3)


def long_majors(insertion_points: List[Angle]) -> LeafLamination:
    leaves = []
    for insertion_point in insertion_points:
        sibling = insertion_point.other_sibling()[0]
        cub_maj = Psi(insertion_point, insertion_point)
        new_insertion_point = psi(sibling, insertion_point)
        leaves.append(Psi(cub_maj, new_insertion_point))
    return LeafLamination(points=[], leafs=leaves, degree=3)


def long_minors(insertion_points: List[Angle]) -> LeafLamination:
    leaves = []
    for insertion_point in insertion_points:
        sibling = insertion_point.other_sibling()[0]
        cub_maj = Psi(insertion_point, insertion_point)
        new_insertion_point = psi(sibling, insertion_point)
        leaves.append(sigma(Psi(cub_maj, new_insertion_point)))
    return LeafLamination(points=[], leafs=leaves, degree=3)


if __name__ == "__main__":
    with tempconfig({"quality": "high_quality", "preview": True}):
        # GenerateLams(color(periodic_points(6)), build_quig).render()
        # GenerateLams(color(periodic_points(6)), short_quig).render()
        # GenerateLams(
        #     color(filter(lambda x: x < 0.5, periodic_points(6))), long_quig
        # ).render()
        # GenerateLams(pre_iterates_of_zero(5), long_quig).render()
        pass
    with tempconfig(
        {"quality": "fourk_quality", "preview": True}  # , "background_color": WHITE
    ):
        # ColorWheel().render()
        # Main(
        #     [LeafLamination(points=color(periodic_points(7)), leafs=[], degree=2)]
        # ).render()
        # Main([build_quig(color([NaryFraction.from_string(2, "_01")])[0])]).render()
        # Main([cubic_co_majors(color(periodic_points(9)))]).render()
        # Main([cubic_majors(color(periodic_points(9)))]).render()
        # Main([short_co_majors(color(periodic_points(9)))]).render()
        # Main([short_majors(color(periodic_points(9)))]).render()
        # Main([short_minors(color(periodic_points(9)))]).render()
        # Main([long_co_majors(color(periodic_points(9)))]).render()
        # Main([long_majors(color(periodic_points(9)))]).render()
        # Main([long_minors(color(periodic_points(9)))]).render()
        reduced = color(
            filter(
                lambda x: x < 0.5,
                list(periodic_points(9))
                + [p.other_sibling()[0] for p in periodic_points(9)],
            )
        )
        # Main([long_co_majors(reduced)]).render()
        # Main([long_majors(reduced)]).render()
        Main([long_minors(reduced)]).render()
        # Quigs(pre_iterates_of_zero).render()
        # Main([short_quig(NaryFraction.from_string(2, "_01"))]).render()

        pass
