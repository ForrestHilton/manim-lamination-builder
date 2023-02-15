#!/usr/bin/env python3
from functools import reduce
from typing import Type
from manim import (
        Union,
    BLACK,
    BLUE,
    RED,
    WHITE,
    Arc,
    ArcPolygonFromArcs,
    Difference,
    Dot,
    Intersection,
    Mobject,
    Scene,
    Circle,
    Create,
    tempconfig,
    Point,
)
import sys
import os
import json

from points import NaryFraction
from Lamination import Lamination, laminations_from_dict
import numpy as np
from math import pi, tan, sqrt, cos, sin


background = BLACK


class RenderLamination(Scene):
    def __init__(self, lamination: Lamination):
        self.lamination = lamination
        super().__init__()

    def construct(self):
        circle = Circle()  # create a circle
        circle.set_stroke(WHITE, opacity=1)
        circle.set_fill(background, opacity=0)
        self.add(circle)  # show the circle on screen

        for polygon in self.lamination.polygons:
            # TODO: check if pollygon is valid
            boundaries = []
            cords = []
            for i in range(len(polygon)):
                cord = [polygon[i], polygon[(i + 1) % len(polygon)]]
                cords.append(cord)
                if not (
                    False  # TODO: reduce redundancy
                    # cord in self.lamination.polygons
                    # or [cord[0], cord[1]] in self.lamination.polygons
                ):
                    self.lamination.chords.append(cord)

                boundaries.append(self.cord_builder(cord, needs_circle=True))

            ccw_convex = []
            cw_convex = []
            for i, cord in enumerate(cords):
                # copies from cord builder function
                a = NaryFraction.from_string(lamination.radix, cord[0])
                b = NaryFraction.from_string(lamination.radix, cord[1])
                theta1 = a.to_angle()
                theta2 = b.to_angle()

                distance_ccw = (theta1 - theta2) % (2 * pi)
                distance_cw = (theta2 - theta1) % (2 * pi)
                if distance_cw > pi:
                    cw_convex.append(i)
                if distance_ccw > pi:
                    ccw_convex.append(i)

            difference_subject = Circle(1)
            if len(cw_convex) == 0 or len(ccw_convex) == 0:
                pass
            elif len(ccw_convex) == 1:
                difference_subject = Intersection(
                    difference_subject, boundaries.pop(ccw_convex[0])
                )
            else:
                assert len(cw_convex) == 1
                difference_subject = Intersection(
                    difference_subject, boundaries.pop(cw_convex[0])
                )
            clip = reduce(Union, boundaries)
            self.add(
                Difference(
                    difference_subject,
                    clip,
                    color=BLUE,
                    fill_opacity=1,
                )
            )

        for cord in self.lamination.chords:
            if len(cord) != 2:
                print("cords should have length two")
            for point in cord:
                if not point in self.lamination.points:
                    self.lamination.points.append(point)
            self.add(self.cord_builder(cord, needs_circle=False))

        for point in self.lamination.points:
            coordinates = NaryFraction.from_string(
                lamination.radix, point
            ).to_cartesian()
            self.add(Dot(np.array([coordinates[0], coordinates[1], 0]), color=RED))

    def cord_builder(self, cord, needs_circle) -> Mobject:
        a = NaryFraction.from_string(lamination.radix, cord[0])
        b = NaryFraction.from_string(lamination.radix, cord[1])
        theta1 = min(a.to_angle(), b.to_angle())
        theta2 = max(a.to_angle(), b.to_angle())
        kapa1 = pi / 2 + theta2
        delta_angle = pi - abs(theta1 - theta2)
        alpha = (theta1 + theta2) / 2
        r = tan(alpha - theta1)
        centerToCenter = sqrt(1 + r**2)
        center = [cos(alpha) * centerToCenter, sin(alpha) * centerToCenter, 0]
        # print(
        #     "Arc({}, {}, {}, arc_center=np.array({}))".format(
        #         r, kapa1, delta_angle, center
        #     )
        # )
        if needs_circle:
            c = Circle(r)
            c.move_to(center)
            return c
        return Arc(r, kapa1, delta_angle, arc_center=np.array(center))


if True:
    file = sys.argv[-1]
    if len(sys.argv) == 1:
        path = "/home/forrest/Desktop/MA498/python-lamination-builder/test.json"
    else:
        path = os.path.join(os.getcwd(), file)
    with open(path) as f:
        data = json.load(f)
    laminations = laminations_from_dict(data)

    with tempconfig({"quality": "medium_quality", "preview": True}):
        for lamination in laminations:
            scene = RenderLamination(lamination)
            scene.render()
