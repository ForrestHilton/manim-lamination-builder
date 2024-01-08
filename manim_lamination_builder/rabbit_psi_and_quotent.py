from manim import *
import numpy as np
import cmath

import functools

from manim_lamination_builder.points import CarryingFloatWrapper

c = -0.122561166876657 + 0.744861766619737j


def f(z):
    return z**2 + c


def f0(z):
    d = 2
    return z**d


def inversef(z, guess):
    ret = cmath.sqrt(z - c)
    if np.abs(ret - guess) < np.abs(-ret - guess):
        return ret
    else:
        return -ret


def psi(w):
    assert np.abs(w) > 1
    if np.abs(w) > 1e150:
        return w
    return inversef(psi(f0(w)), w)


# import time
# start = time.perf_counter_ns()
# ret = psi(1.025+1.2875j)
# end = time.perf_counter_ns()
# print(ret, end-start)
## old way gives  (0.831862910941456+1.1429005122387517j) 767689
## this way gives (0.831862910941456+1.1429005122387519j) 97113
if False:
    from multiprocessing import Pool

    def process_point(p,function):
        out = function(complex(p[0], p[1]))
        return out.real * RIGHT + out.imag * UP

    def apply_complex_function(mob: Mobject, function) -> Mobject:
        ret = mob.copy()

        with Pool() as pool:
            out_points = pool.map(functools.partial(process_point, function=function), mob.points)

        for i,p in enumerate(out_points):
            ret.points[i] = p
        
        for i, submob in enumerate(ret.submobjects):
            ret.submobjects[i] = apply_complex_function(submob, function)
        return ret
else:
    def apply_complex_function(mob: Mobject, function) -> Mobject:
        ret = mob.copy()
        for i, p in enumerate(mob.points):
            out = function(complex(p[0], p[1]))
            ret.points[i] = out.real * RIGHT + out.imag * UP

        for i, submob in enumerate(ret.submobjects):
            ret.submobjects[i] = apply_complex_function(submob, function)
        return ret
"""
This approach cheats in the sense that it looks at the actual Julia set.
"""
import functools
from math import atan2, tan
from typing import Optional, List
from manim import (
    BLUE,
    ORIGIN,
    RIGHT,
    TAU,
    UP,
    WHITE,
    Arc,
    Line,
    Scene,
    Transform,
    np,
    rate_functions,
    CubicBezier,
)
from manim.animation.animation import config
from manim.mobject.geometry.arc import itertools
from manim_lamination_builder import (
    Chord,
    FloatWrapper,
    GapLamination,
    Angle,
    parse_lamination,
    rabbit_nth_pullback,
)
from numpy import repeat
import cmath
from manim_lamination_builder import custom_dump


def get_convexity(in_list: List[Angle]) -> Optional[List[CarryingFloatWrapper]]:
    """
    Retruns a sorted list of vetesies in CCW order such that the first is the boundary
    of the convex region. Wraping is handeld correctly and all points are taken from the same sheet
    of the reamon serface.
    If the Polygon is not convex in some way, return None.
    """
    sorted_list = sorted([p.to_float() for p in in_list])

    for i, p in enumerate(sorted_list):
        next_p = sorted_list[(i + 1) % len(in_list)]
        distance_ccw = (next_p - p) % 1
        if distance_ccw > 0.5:
            sorted_list = sorted([1 + p2 if p2 < next_p else p2 for p2 in sorted_list])
            return list(map(lambda p: CarryingFloatWrapper(p), sorted_list))

    return None


class CheatingPinch(Scene):
    def __init__(self, lamination:GapLamination):
        def change_color(p):
            p.visual_settings.stroke_width = 2
            return p
        self.lamination = lamination.apply_function(change_color)
        self.all_vertecies_sorted = sorted(
            itertools.chain.from_iterable(self.lamination.polygons),
            key=lambda p: p.to_float(),
        )
        #  corresponds to its first ccw edge in the sorted or convex list
        self.initial_curves = []
        self.destination_curves = []
        self.polygons_handled = repeat(False, len(lamination.polygons))
        super().__init__()

    def add_initial_curve(self, p: Angle, next_p: Angle):
        bigness = (next_p.to_float() - p.to_float()) % 1
        arc = Arc(
            start_angle=p.to_angle(),
            angle=bigness * TAU,
            stroke_width=2,
        )
        self.initial_curves.append(arc)

    def point_positioning_function(self, polygon: List[Angle]):
        points = []
        for angle in polygon:
            z = psi(1.000000001 * cmath.exp(angle.to_angle() * 1j))
            points.append(RIGHT * np.real(z) + UP * np.imag(z))
        return sum(points) / len(points)

    def angle_of_last_fatu_gap_rotaitions(self, polygon) -> float:
        """rotations"""
        first_ray = get_convexity(polygon)[0]
        z1 = psi(1.000000001 * cmath.exp(first_ray.to_angle() * 1j))
        z2 = psi(1.000005 * cmath.exp(first_ray.to_angle() * 1j))
        diff = z2 - z1
        angle_of_first_ray = np.angle(diff) / 2 / np.pi
        return angle_of_first_ray - 0.5 / len(polygon)

    def recursive_polygon_formation(self, polygon):
        cut_point_position = self.point_positioning_function(polygon)
        self.polygons_handled[self.lamination.polygons.index(polygon)] = True
        polygon_sorted = get_convexity(polygon)
        assert not polygon_sorted == None
        angle_of_final_fatue_gap = self.angle_of_last_fatu_gap_rotaitions(polygon)

        for i, p in enumerate(polygon_sorted):
            # test if recursion is needed
            angle_of_this_fatue_gap = angle_of_final_fatue_gap + (i + 1) / len(
                polygon_sorted
            )

            broad_index = self.all_vertecies_sorted.index(p.cleared())
            next_p = self.all_vertecies_sorted[
                (broad_index + 1) % len(self.all_vertecies_sorted)
            ]
            bigness = (next_p.to_float() - p.to_float()) % 1

            self.add_initial_curve(p, next_p)

            a = angle_of_this_fatue_gap + (-0.33) / len(polygon_sorted)
            A = FloatWrapper(a).to_cartesian() * bigness * 3
            if next_p in polygon:
                # repeated code
                b = a + 1 / len(polygon_sorted) * 0.66
                B = FloatWrapper(b).to_cartesian() * bigness * 3

                self.destination_curves += CubicBezier(
                    cut_point_position,
                    cut_point_position + A,
                    cut_point_position + B,
                    cut_point_position,
                    stroke_width=2,
                )
            else:
                adjacent_polygon = next(
                    filter(lambda poly: next_p in poly, self.lamination.polygons)
                )
                angle_of_this_cut_point_from_other = self.angle_of_last_fatu_gap_rotaitions(
                    adjacent_polygon
                ) + list(
                    map(lambda p: p.cleared(), get_convexity(adjacent_polygon))
                ).index(
                    next_p
                ) / len(
                    adjacent_polygon
                )

                b = angle_of_this_cut_point_from_other + (0.33) / len(polygon_sorted)
                B = FloatWrapper(b).to_cartesian() * bigness * 3

                # destination curve
                other_cut_point_position = self.point_positioning_function(
                    adjacent_polygon
                )
                # scailar = 8 * Line(cut_point_position,other_cut_point_position).get_length()
                scailar = 3
                self.destination_curves += CubicBezier(
                    cut_point_position,
                    cut_point_position + A * scailar,
                    other_cut_point_position + B * scailar,
                    other_cut_point_position,
                    stroke_width=2,
                )

                if not self.polygons_handled[
                    self.lamination.polygons.index(adjacent_polygon)
                ]:
                    self.recursive_polygon_formation(adjacent_polygon)

    def construct(self):
        polygon_mobs = []
        polygon_destinations = []
        for i, polygon in enumerate(self.lamination.polygons):
            polygon_mobs += self.lamination.build().submobjects[1 + i]

            cut_point_position = self.point_positioning_function(polygon)
            polygon_destinations += CubicBezier(
                cut_point_position,
                cut_point_position,
                cut_point_position,
                cut_point_position,
                stroke_color= WHITE,
                stroke_width = 2,
                color=BLUE,
            )

        # start procedure
        self.recursive_polygon_formation(self.lamination.polygons[0])

        self.add(*polygon_mobs)
        self.add(*self.initial_curves)
        self.wait(0.2)
        self.play(
            *[
                Transform(a, b)
                for a, b in zip(self.initial_curves, self.destination_curves)
            ],
            *[Transform(a, b) for a, b in zip(polygon_mobs, polygon_destinations)],
            run_time=1,
            rate_func=rate_functions.linear,
        )
        self.wait(0.2)


if __name__ == "__main__":
    config.frame_width /= 3.5
    config.frame_height /= 3.5
    config.preview = True
    lamination = rabbit_nth_pullback(6)
    CheatingPinch(lamination).render()
