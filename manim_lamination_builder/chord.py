# Licensed under the The AGPLv3 License (AGPLv3)
# Copyright (c) 2023 Forrest M. Hilton <forrestmhilton@gmail.com>
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from math import pi, tan

from manim import BLACK, TAU, Mobject, VMobject
from pydantic import BaseModel

from manim_lamination_builder.points import Angle


class Chord(BaseModel):
    min: Angle
    max: Angle

    def __init__(self, a: Angle, b: Angle):
        min, max = b, a
        if a.to_float() < b.to_float():
            min, max = max, min
        super(Chord, self).__init__(min=min, max=max)

    def __hash__(self):
        return hash((self.min, self.max))

    def crosses(self, other: "Chord") -> bool:
        if other == self:
            return False
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

    def length(self) -> float:
        "length in rotations"
        theta1 = self.min.to_float() % 1
        theta2 = self.max.to_float() % 1
        assert theta2 - theta1 >= 0
        return theta2 - theta1

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

    def after_sigma(self):
        return Chord(self.min.after_sigma(), self.max.after_sigma())


def make_and_append_bezier(vmob: VMobject, theta1: Angle, theta2: Angle):
    """Add a cubic Bezier curve to a VMobject using given angles or NaryFractions."""

    a = theta1.to_cartesian()
    b = theta2.to_cartesian()

    handle_len = handle_length(theta1.to_angle(), theta2.to_angle())
    vmob.add_cubic_bezier_curve(a, a * (1 - handle_len), b * (1 - handle_len), b)


def handle_length(theta1: float, theta2: float) -> float:
    theta1, theta2 = theta1 % TAU, theta2 % TAU
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
