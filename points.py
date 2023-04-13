# Licensed under the The AGPLv3 License (AGPLv3)
# Copyright (c) 2023 Forrest M. Hilton <forrestmhilton@gmail.com>
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from typing import List

from math import cos, pi, sin

from manim.animation.animation import deepcopy

import numpy as np


class NaryFraction:
    def __init__(self, base: int, exact: List[int], repeating: List[int], overflow=0):
        assert base != 1
        self.base = base
        self.exact = exact
        self.repeating = repeating
        self.overflow = overflow

    def clear(self) -> "NaryFraction":
        return NaryFraction(self.base, self.exact, self.repeating)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self.without_enharmonics().__dict__
                == other.without_enharmonics().__dict__
            )
        else:
            return False

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
        ret = self.after_sigma().pre_images()
        assert self in ret, "{} is not in {}".format(
            self.to_string(), map(lambda p: p.to_string(), ret)
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

    def to_angle(self):
        return self.to_float() * 2 * pi

    def to_cartesian(self):
        return angle_to_cartesian(self.to_angle())

    def cartesian_lerp(self, other: "NaryFraction", alpha: float):
        angle = (1 - alpha) * self.to_angle() + alpha * other.to_angle()
        return angle_to_cartesian(angle)


def angle_to_cartesian(angle: float):
    return np.array([cos(angle), sin(angle), 0])


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
