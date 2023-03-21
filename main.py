#!/usr/bin/env python3
# Licensed under the The AGPLv3 License (AGPLv3)
# Copyright (c) 2023 Forrest M. Hilton <forrestmhilton@gmail.com>
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from functools import reduce
from custom_json import CustomDecoder
from typing import List, Tuple
from manim import (
    Group,
    BLACK,
    BLUE,
    RED,
    WHITE,
    Arc,
    Difference,
    Dot,
    Intersection,
    Mobject,
    Scene,
    Circle,
    tempconfig,
)
import sys
import os
import json

from manim.utils.file_ops import config

from points import NaryFraction
from lamination import Lamination, Chord
import numpy as np
from math import pi, tan, sqrt, cos, sin


background = BLACK


def cord_builder(cord, needs_circle) -> Mobject:
    a = cord[0]
    b = cord[1]
    theta1 = min(a.to_angle(), b.to_angle())
    theta2 = max(a.to_angle(), b.to_angle())
    if abs(theta1 - theta2) - pi < 1e-8:
        # 2.2250738585072014e-308 is the smallest positive number
        theta1 += 1e-7
    kapa1 = pi / 2 + theta2
    # wraping edge case:
    if theta2 - theta1 > pi:
        theta1, theta2 = theta1 + pi, theta2 + pi
    delta_angle = pi - abs(theta1 - theta2)
    alpha = (theta1 + theta2) / 2
    r = tan(alpha - theta1)
    centerToCenter = sqrt(1 + r**2)
    center = [cos(alpha) * centerToCenter, sin(alpha) * centerToCenter, 0]
    # print("Circle({})".format(r))
    # print(".move_to({})".format(center))
    if needs_circle:
        c = Circle(r)
        c.move_to(center)
        return c
    return Arc(r, kapa1, delta_angle, arc_center=np.array(center))


def build_lamination(lamination: Lamination):
    ret = Mobject()
    unit_circle = Circle()  # create a circle
    unit_circle.set_stroke(WHITE, opacity=1)
    unit_circle.set_fill(background, opacity=0)
    ret.add(unit_circle)  # show the circle on screen

    for polygon in lamination.polygons:
        # TODO: check if pollygon is valid
        boundaries = []
        cords = []
        for i in range(len(polygon)):
            cord = [polygon[i], polygon[(i + 1) % len(polygon)]]
            cords.append(cord)
            if not (
                False  # TODO: reduce redundancy
                # cord in lamination.polygons
                # or [cord[0], cord[1]] in lamination.polygons
            ):
                lamination.chords.append(cord)

            boundaries.append(cord_builder(cord, needs_circle=True))
        if len(polygon) < 3:
            continue

        ccw_convex = []
        cw_convex = []
        for i, cord in enumerate(cords):
            # copies from cord builder function
            a = cord[0]
            b = cord[1]
            theta1 = a.to_angle()
            theta2 = b.to_angle()

            distance_ccw = (theta1 - theta2) % (2 * pi)
            distance_cw = (theta2 - theta1) % (2 * pi)
            if distance_cw > pi:
                cw_convex.append(i)
            if distance_ccw > pi:
                ccw_convex.append(i)

        # using workaround documented here https://github.com/ManimCommunity/manim/issues/3167
        convex_boundary = None
        if len(cw_convex) == 0 or len(cw_convex) == 0:
            pass
        elif len(ccw_convex) == 1:
            convex_boundary = boundaries.pop(ccw_convex[0])
        else:
            assert len(cw_convex) == 1
            convex_boundary = boundaries.pop(cw_convex[0])
        shape = reduce(
            lambda a, b: Difference(
                a,
                b,
                color=BLUE,
                fill_opacity=1,
            ),
            boundaries,
            unit_circle,
        )

        if convex_boundary is not None:
            shape = Intersection(shape, convex_boundary, color=BLUE, fill_opacity=1)
        ret.add(shape)

    for cord in lamination.chords:
        if len(cord) != 2:
            print("cords should have length two")
        for point in cord:
            if point not in lamination.points:
                lamination.points.append(point)
        ret.add(cord_builder(cord, needs_circle=False))

    for point in lamination.points:
        coordinates = point.to_cartesian()
        ret.add(
            Dot(np.array([coordinates[0], coordinates[1], 0]), color=RED, radius=0.03)
        )

    return ret


class Main(Scene):
    def __init__(self, laminations: List[Lamination]):
        self.laminations = laminations
        super().__init__()

    def construct(self):
        group = Group(
            *[build_lamination(lamination) for lamination in self.laminations]
        )
        group = group.arrange_in_grid()
        group.scale(
            1
            / max(group.width / config.frame_width, group.height / config.frame_height)
        )
        self.add(group)


if __name__ == "__main__":
    file = sys.argv[-1]
    if len(sys.argv) == 1:
        path = "/home/forrest/Desktop/manim_lamination_builder/test.json"
    else:
        path = os.path.join(os.getcwd(), file)
    with open(path) as f:
        data = json.load(f, cls=CustomDecoder)
    laminations = data

    with tempconfig({"quality": "medium_quality", "preview": True}):
        scene = Main(laminations)
        scene.render()
