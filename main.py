#!/usr/bin/env python3
from typing import Type
from manim import (
    BLACK,
    RED,
    WHITE,
    Arc,
    Dot,
    Mobject2D,
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


def cord_builder(a: NaryFraction, b: NaryFraction) -> Mobject2D:
    theta1 = min(a.to_angle(), b.to_angle())
    theta2 = max(a.to_angle(), b.to_angle())
    kapa1 = pi/2 + theta2
    delta_angle = pi - abs(theta1 - theta2)
    alpha = (theta1 + theta2) / 2
    r = tan(alpha - theta1)
    centerToCenter = sqrt(1 + r**2)
    center = [cos(alpha) * centerToCenter, sin(alpha) * centerToCenter, 0]
    return Arc(r, kapa1, delta_angle, arc_center=np.array(center))


class RenderLamination(Scene):
    def __init__(self, lamination: Lamination):
        self.lamination = lamination
        super().__init__()

    def construct(self):
        circle = Circle()  # create a circle
        circle.set_stroke(WHITE, opacity=1)
        circle.set_fill(BLACK, opacity=0)
        self.add(circle)  # show the circle on screen

        for cord in self.lamination.chords:
            for point in cord: 
                if not point in self.lamination.points:
                    self.lamination.points.append(point)
            a = NaryFraction.from_string(lamination.radix, cord[0])
            b = NaryFraction.from_string(lamination.radix, cord[1])
            self.add(cord_builder(a, b))

        for point in self.lamination.points:
            coordinates = NaryFraction.from_string(
                lamination.radix, point
            ).to_cartesian()
            self.add(Dot(np.array([coordinates[0], coordinates[1], 0]), color=RED))


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
