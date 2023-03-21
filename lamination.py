# Licensed under the The AGPLv3 License (AGPLv3)
# Copyright (c) 2023 Forrest M. Hilton <forrestmhilton@gmail.com>
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from typing import List, Optional, Type

from manim import tuplify

from points import NaryFraction


class Lamination:
    polygons: Optional[List[List[NaryFraction]]]
    chords: Optional[List[List[NaryFraction]]]
    points: Optional[List[NaryFraction]]
    radix: int

    def __init__(
        self,
        polygons: Optional[List[List[NaryFraction]]],
        chords: Optional[List[List[NaryFraction]]],
        points: Optional[List[NaryFraction]],
        radix: int,
    ) -> None:
        self.polygons = polygons
        self.chords = chords
        self.points = points
        self.radix = radix


class Chord:
    min: NaryFraction
    max: NaryFraction

    def __init__(self, a: NaryFraction, b: NaryFraction):  # TODO: min max
        if a.to_float() < b.to_float():
            self.min = a
            self.max = b
        else:
            self.min = b
            self.max = a

    def crosses(self, other):
        if (
            self.max.to_float() <= other.min.to_float()
            or self.min.to_float() >= other.max.to_float()
        ):
            return False
        if (
            self.min.to_float() > other.min.to_float()
            and self.max.to_float() > other.max.to_float()
        ) or (
            self.min.to_float() < other.min.to_float()
            and self.max.to_float() < other.max.to_float()
        ):
            return True


a, b, c, d = tuplify(NaryFraction.from_string(4, "0_0").siblings())

assert Chord(a, c).crosses(Chord(b, d))
assert not Chord(a, b).crosses(Chord(c, d))
assert Chord(b, d).crosses(Chord(a, c))
assert not Chord(c, d).crosses(Chord(a, b))
