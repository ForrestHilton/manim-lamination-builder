# Licensed under the The AGPLv3 License (AGPLv3)
# Copyright (c) 2023 Forrest M. Hilton <forrestmhilton@gmail.com>
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from typing import Union
from manim import (
    BLACK,
    Mobject,
    VMobject,
    bezier,
    tuplify,
)

from points import NaryFraction, angle_to_cartesian
import numpy as np
from math import pi, tan


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

    def handle_length(self) -> float:
        theta1 = self.min.to_angle()
        theta2 = self.max.to_angle()
        return handle_length(theta1, theta2)

    def build(self) -> Mobject:
        # https://pomax.github.io/bezierinfo/#circles_cubic
        ret = VMobject(color=BLACK)
        make_and_append_bezier(ret, self.min, self.max)
        return ret

    def __eq__(self, other: "Chord"):
        if isinstance(other, Chord):
            return self.min == other.min and self.max == other.max
        return False


def make_and_append_bezier(
    vmob: VMobject,
    theta1: Union[NaryFraction, float],
    theta2: Union[NaryFraction, float],
):
    """Add a cubic Bezier curve to a VMobject using given angles or NaryFractions."""

    a = (
        theta1.to_cartesian()
        if isinstance(theta1, NaryFraction)
        else angle_to_cartesian(theta1)
    )
    b = (
        theta2.to_cartesian()
        if isinstance(theta2, NaryFraction)
        else angle_to_cartesian(theta2)
    )

    handle_len = handle_length(
        theta1.to_angle() if isinstance(theta1, NaryFraction) else theta1,
        theta2.to_angle() if isinstance(theta2, NaryFraction) else theta2,
    )
    vmob.add_cubic_bezier_curve(a, a * (1 - handle_len), b * (1 - handle_len), b)


def handle_length(theta1: float, theta2: float) -> float:
    if theta1 > theta2:
        theta1, theta2 = theta2, theta1
    if abs(theta1 - theta2) - pi < 1e-8:
        # 2.2250738585072014e-308 is the smallest positive number
        theta1 += 1e-7
    # wraping edge case:
    if theta2 - theta1 > pi:
        theta1, theta2 = theta1 + pi, theta2 + pi
    delta_angle = pi - abs(theta1 - theta2)
    alpha = (theta1 + theta2) / 2
    r = tan(alpha - theta1)
    k = 4 / 3 * tan(delta_angle / 4)
    return r * k


a, b, c, d = tuplify(NaryFraction.from_string(4, "0_0").siblings())

assert Chord(a, c).crosses(Chord(b, d))
assert not Chord(a, b).crosses(Chord(c, d))
assert Chord(b, d).crosses(Chord(a, c))
assert not Chord(c, d).crosses(Chord(a, b))
assert NaryFraction.from_string(4, "0_0") == NaryFraction.from_string(4, "0_0")
assert Chord(NaryFraction.from_string(4, "0_0"), b) in [
    Chord(NaryFraction.from_string(4, "0_0"), b)
]
