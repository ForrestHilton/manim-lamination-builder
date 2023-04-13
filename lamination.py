# Licensed under the The AGPLv3 License (AGPLv3)
# Copyright (c) 2023 Forrest M. Hilton <forrestmhilton@gmail.com>
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from typing import List, Callable
from manim import (
    BLUE,
    RED,
    BLACK,
    Dot,
    Mobject,
    VMobject,
    Circle,
)
from manim.utils.color import Colors, Color
from points import NaryFraction
from chord import Chord, make_and_append_bezier


background = BLACK


class Lamination:
    polygons: List[List[NaryFraction]]
    chords: List["Chord"]
    points: List[NaryFraction]
    radix: int
    colorizer: Callable[[NaryFraction], Colors]

    def __init__(
        self,
        polygons: List[List[NaryFraction]],
        chords: List["Chord"],
        points: List[NaryFraction],
        radix: int,
        colorizer=lambda p: Colors.red,
    ) -> None:
        self.polygons = polygons
        self.chords = chords
        self.points = points
        self.radix = radix
        self.colorizer = colorizer

    def auto_populate(self):
        for polygon in self.polygons:
            for i in range(len(polygon)):
                a = polygon[i]
                b = polygon[(i + 1) % len(polygon)]
                chord = Chord(a, b)

                if not (chord in self.chords):
                    self.chords.append(chord)

        for chord in self.chords:
            for point in [chord.min, chord.max]:
                if point not in self.points:
                    self.points.append(point)

    def build(self) -> Mobject:
        ret = Mobject()
        unit_circle = Circle(color=BLACK)  # create a circle
        ret.add(unit_circle)  # show the circle on screen

        for polygon in self.polygons:
            shape = VMobject(BLUE, 1, color=BLACK)
            for i in range(len(polygon)):
                a = polygon[i]
                b = polygon[(i + 1) % len(polygon)]
                make_and_append_bezier(shape, a, b)
            ret.add(shape)

        # for chord in self.chords:
        #     ret.add(chord.build())

        for point in self.points:
            ret.add(Dot(point.to_cartesian(), color=self.colorizer(point).value, radius=0.04))

        return ret

    def apply_function(self, f: Callable[[NaryFraction], NaryFraction]) -> "Lamination":
        new_polygons = []
        for poly in self.polygons:
            new_poly = [f(p) for p in poly]
            new_polygons.append(new_poly)
        new_chords = []
        for chord in self.chords:
            new_min = f(chord.min)
            new_max = f(chord.max)
            new_chord = Chord(new_min, new_max)
            new_chords.append(new_chord)
        new_points = [f(p) for p in self.points]
        return Lamination(new_polygons, new_chords, new_points, self.radix)
