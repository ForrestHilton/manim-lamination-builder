# Licensed under the The AGPLv3 License (AGPLv3)
# Copyright (c) 2023 Forrest M. Hilton <forrestmhilton@gmail.com>
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from manim import (
    BLACK,
    Arc,
    Mobject,
    VMobject,
    Circle,
    tuplify,
)

from points import NaryFraction
import numpy as np
from math import pi, tan, sqrt, cos, sin


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

    def crosses(self, other: "Chord") -> bool:
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
        return False

    def _graphical_description(self):
        theta1 = self.min.to_angle()
        theta2 = self.max.to_angle()
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
        return (r, kapa1, delta_angle, center)
        # print("Circle({})".format(r))
        # print(".move_to({})".format(center))

    def handle_length(self) -> float:
        (r, kapa1, delta_angle, center) = self._graphical_description()
        k = 4 / 3 * tan(delta_angle / 4)
        return r * k

    def build(self) -> Mobject:
        # https://pomax.github.io/bezierinfo/#circles_cubic
        ret = VMobject(color=BLACK)
        a = self.max.to_cartesian()
        b = self.min.to_cartesian()
        ret.points = np.array(
            [a, a * (1 - self.handle_length()), b * (1 - self.handle_length()), b]
        )

        return ret

    def circle(self) -> Mobject:
        (r, _, _, center) = self._graphical_description()
        c = Circle(r)
        c.move_to(center)
        return c

    def __eq__(self, other: "Chord"):
        if isinstance(other, Chord):
            return self.min == other.min and self.max == other.max
        return False


a, b, c, d = tuplify(NaryFraction.from_string(4, "0_0").siblings())

assert Chord(a, c).crosses(Chord(b, d))
assert not Chord(a, b).crosses(Chord(c, d))
assert Chord(b, d).crosses(Chord(a, c))
assert not Chord(c, d).crosses(Chord(a, b))
assert NaryFraction.from_string(4, "0_0") == NaryFraction.from_string(4, "0_0")
assert Chord(NaryFraction.from_string(4, "0_0"), b) in [
    Chord(NaryFraction.from_string(4, "0_0"), b)
]
