# Licensed under the The AGPLv3 License (AGPLv3)
# Copyright (c) 2023 Forrest M. Hilton <forrestmhilton@gmail.com>
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from typing import List

from math import cos, pi, sin

from manim.animation.animation import deepcopy
from abc import ABC, abstractmethod
import numpy as np


def angle_to_cartesian(angle: float):
    return np.array([cos(angle), sin(angle), 0])


class UnitPoint(ABC):
    @abstractmethod
    def to_float(self) -> float:
        pass

    @abstractmethod
    def cleared(self) -> "UnitPoint":
        pass

    @abstractmethod
    def after_sigma(self) -> "FloatWrapper":
        pass

    def to_angle(self) -> float:
        return self.to_float() * 2 * pi

    def to_cartesian(self):
        return angle_to_cartesian(self.to_angle())

    def __eq__(self, other):
        return abs(self.to_float() - other.to_float()) < 0.0000001

    def has_degree(self):
        return True


class FloatWrapper(UnitPoint):
    def __init__(self, value: float, degree: int = None):
        self.value = value
        self.degree = degree

    def to_float(self):
        return self.value

    def cleared(self) -> "FloatWrapper":
        return FloatWrapper(self.value % 1, self.degree)

    def after_sigma(self) -> "FloatWrapper":
        after = deepcopy(self.cleared())
        after.value *= self.degree
        return after

    def has_degree(self):
        return self.degree is not None


class NaryFraction(UnitPoint):
    def __init__(self, base: int, exact: List[int], repeating: List[int], overflow=0):
        assert base != 1
        self.base = base
        self.exact = exact
        self.repeating = repeating
        self.overflow = overflow

    def cleared(self) -> "NaryFraction":
        return NaryFraction(self.base, self.exact, self.repeating)

    @staticmethod
    def from_string(base, string_representation):
        overflow = 0
        if "." in string_representation:
            overflow, string_representation = string_representation.split(".")
            overflow = int(overflow)
        parts = string_representation.split("_")
        exact = [int(i) for i in parts[0]]
        repeating = []
        if len(parts) > 1:
            repeating = [int(i) for i in parts[1]]
        return NaryFraction(base, exact, repeating, overflow)

    def to_string(self):
        overflow_string = ""
        if self.overflow != 0:
            overflow_string = str(self.overflow) + "."
        # convert exact part to string
        exact_string = ""
        for i in self.exact:
            exact_string += str(i)

        # convert repeating part to string
        repeating_string = ""
        if self.repeating:
            repeating_string = "_"
            for i in self.repeating:
                repeating_string += str(i)

        return overflow_string + exact_string + repeating_string

    def after_sigma(self) -> "NaryFraction":
        after = deepcopy(self)
        # multiply the exact part by base
        if after.repeating:
            carry = after.repeating.pop(0)
            after.repeating.append(carry)
            after.exact.append(carry)
        after.overflow = after.exact.pop(0)
        return after

    def without_enharmonics(self):
        # TODO: refer to original to do more of this
        ret = deepcopy(self)
        while (
            len(ret.exact) != 0
            and len(ret.repeating) != 0
            and ret.repeating[-1] == ret.exact[-1]
        ):
            ret.exact.pop(-1)
            ret.repeating.insert(0, ret.repeating.pop(-1))
        # to many zeros
        while len(ret.exact) != 0 and ret.exact[-1] == 0 and sum(ret.repeating) == 0:
            ret.exact.pop(-1)

        assert (
            abs(self.to_float() - ret.to_float()) < 1e-9
        ), "Assertion Error: self not equal to ret after converting to float."
        return ret

    def pre_images(self) -> List["NaryFraction"]:
        ret = self.without_enharmonics()
        return [
            NaryFraction(self.base, [digit] + ret.exact, self.repeating)
            for digit in range(self.base)
        ]

    def siblings(self) -> List["NaryFraction"]:
        assert max(self.exact + self.repeating) < self.base
        ret = self.after_sigma().cleared().pre_images()
        assert self.cleared() in ret, "{} is not in {}".format(
            self.cleared().to_string(), list(map(lambda p: p.to_string(), ret))
        )
        return ret

    def to_float(self) -> float:
        value = sum([n / self.base ** (i + 1) for i, n in enumerate(self.exact)])
        if len(self.repeating) != 0:
            value += (
                sum(
                    [
                        n / self.base ** (i + 1 - len(self.repeating))
                        for i, n in enumerate(self.repeating)
                    ]
                )
                / self.base ** len(self.exact)
                / (self.base ** len(self.repeating) - 1)
            )
        return value + self.overflow

    def cartesian_lerp(self, other: "NaryFraction", alpha: float):
        angle = (1 - alpha) * self.to_angle() + alpha * other.to_angle()
        return angle_to_cartesian(angle)

    def after_sigma_shortest_ccw(self):
        assert self == self.cleared()
        ret = self.after_sigma().cleared()
        if ret.to_angle() < self.to_angle():
            ret = NaryFraction(ret.base, ret.exact, ret.repeating, 1)
        assert ret.to_angle() > self.to_angle()
        assert ret.to_float() - self.to_float() <= 1
        assert ret.overflow <= 1
        return ret

def sigma(p:UnitPoint):
    return p.after_sigma()


assert NaryFraction(3, [1], [1, 0, 1]).to_string() == "1_101"
assert NaryFraction(2, [1], []).to_string() == "1"

assert NaryFraction.from_string(3, "1_101") == NaryFraction(3, [1], [1, 0, 1])
assert NaryFraction.from_string(2, "1") == NaryFraction(2, [1], [])

assert NaryFraction.from_string(3, "_101").after_sigma().to_string() == "1._011"
assert NaryFraction.from_string(3, "1._101").to_string() == "1._101"
assert (
    NaryFraction.from_string(10, "_33").to_float()
    == NaryFraction.from_string(3, "1").to_float()
)


assert NaryFraction.from_string(10, "_9").to_float() == 1.0

assert NaryFraction.from_string(4, "0_300").without_enharmonics().to_string() == "_030"


# ["_302", "_322", "_023", "_223"]
# ["_230", "_232", "_302", "_322"]

# assert NaryFraction.from_string(4,"_230").to_string() == "1._023"
# assert NaryFraction.from_string(4, "_232").to_string() == "1._223"
a = NaryFraction.from_string(4, "_230")
assert a.after_sigma().to_string() == "2._302"
assert a.to_string() == "_230"

assert a.after_sigma_shortest_ccw().to_string() == "_302"
assert a.to_string() == "_230"
