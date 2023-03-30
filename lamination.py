# Licensed under the The AGPLv3 License (AGPLv3)
# Copyright (c) 2023 Forrest M. Hilton <forrestmhilton@gmail.com>
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from functools import reduce
from typing import List
from manim import (
    BLUE,
    RED,
    WHITE,
    BLACK,
    Difference,
    Dot,
    Intersection,
    Mobject,
    Circle,
)

from points import NaryFraction
from chord import Chord
import numpy as np
from math import pi


background = BLACK


class Lamination:
    polygons: List[List[NaryFraction]]
    chords: List["Chord"]
    points: List[NaryFraction]
    radix: int

    def __init__(
        self,
        polygons: List[List[NaryFraction]],
        chords: List["Chord"],
        points: List[NaryFraction],
        radix: int,
    ) -> None:
        self.polygons = polygons
        self.chords = chords
        self.points = points
        self.radix = radix

    def build(self) -> Mobject:
        ret = Mobject()
        unit_circle = Circle()  # create a circle
        unit_circle.set_stroke(WHITE, opacity=1)
        unit_circle.set_fill(background, opacity=0)
        ret.add(unit_circle)  # show the circle on screen

        for polygon in self.polygons:
            # TODO: check if pollygon is valid
            boundaries = []
            chords = []
            for i in range(len(polygon)):
                chord = Chord(polygon[i], polygon[(i + 1) % len(polygon)])
                ordered_chord = [polygon[i], polygon[(i + 1) % len(polygon)]]
                chords.append(ordered_chord)
                if not (chord in self.chords):
                    self.chords.append(chord)

                boundaries.append(chord.circle())
            if len(polygon) < 3:
                continue

            ccw_convex = []
            cw_convex = []
            for i, ordered_chord in enumerate(chords):
                # copies from cord builder function
                theta1 = ordered_chord[0].to_angle()
                theta2 = ordered_chord[1].to_angle()

                distance_ccw = (theta1 - theta2) % (2 * pi)
                distance_cw = (theta2 - theta1) % (2 * pi)
                if distance_cw > pi:
                    cw_convex.append(i)
                if distance_ccw > pi:
                    ccw_convex.append(i)

            # using workaround documented here https://github.com/ManimCommunity/manim/issues/3167
            convex_boundary = None
            if len(cw_convex) == 0 or len(ccw_convex) == 0:
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

        for chord in self.chords:
            for point in [chord.min, chord.max]:
                if point not in self.points:
                    self.points.append(point)
            ret.add(chord.build())

        for point in self.points:
            coordinates = point.to_cartesian()
            ret.add(
                Dot(
                    np.array([coordinates[0], coordinates[1], 0]),
                    color=RED,
                    radius=0.04,
                )
            )

        return ret
