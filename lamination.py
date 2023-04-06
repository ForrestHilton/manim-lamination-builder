# Licensed under the The AGPLv3 License (AGPLv3)
# Copyright (c) 2023 Forrest M. Hilton <forrestmhilton@gmail.com>
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from typing import List
from manim import (
    BLUE,
    RED,
    BLACK,
    Dot,
    Mobject,
    VMobject,
    Circle,
)

from points import NaryFraction
from chord import Chord, make_and_append_bezier


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
        unit_circle = Circle(color=BLACK)  # create a circle
        ret.add(unit_circle)  # show the circle on screen

        for polygon in self.polygons:
            # TODO: check if pollygon is valid
            shape = VMobject(BLUE, 1)
            for i in range(len(polygon)):
                a = polygon[i]
                b = polygon[(i + 1) % len(polygon)]
                chord = Chord(a, b)
                make_and_append_bezier(shape, a, b)

                if not (chord in self.chords):
                    self.chords.append(chord)

            if len(polygon) > 2:
                ret.add(shape)

        for chord in self.chords:
            for point in [chord.min, chord.max]:
                if point not in self.points:
                    self.points.append(point)
            ret.add(chord.build())

        for point in self.points:
            ret.add(
                Dot(
                    point.to_cartesian(),
                    color=RED,
                    radius=0.04,
                )
            )

        return ret
