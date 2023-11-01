# Licensed under the The AGPLv3 License (AGPLv3)
# Copyright (c) 2023 Forrest M. Hilton <forrestmhilton@gmail.com>
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from typing import List, Optional

from math import ceil, cos, pi, sin, floor

from manim.animation.animation import deepcopy
from abc import ABC, abstractmethod
import numpy as np

from manim_lamination_builder.visual_settings import VisualSettings


def angle_to_cartesian(angle: float):
    return np.array([cos(angle), sin(angle), 0])


class UnitPoint(ABC):
    visual_settings: VisualSettings
    base: Optional[int]

    def __repr__(self) -> str:
        return self.to_string()

    def __str__(self) -> str:
        return self.to_string()

    @abstractmethod
    def to_float(self) -> float:
        pass

    @abstractmethod
    def to_string(self) -> str:
        pass

    @abstractmethod
    def after_sigma(self) -> "UnitPoint":
        pass

    def to_angle(self) -> float:
        return self.to_float() * 2 * pi

    def to_cartesian(self):
        return angle_to_cartesian(self.to_angle())

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        return hash(floor(self.to_float() / 0.0000002))

    def has_degree(self):
        return True

    def siblings(self) -> List["UnitPoint"]:
        ret = self.after_sigma().pre_images()
        assert self in ret
        return ret

    @abstractmethod
    def pre_images(self) -> List["UnitPoint"]:
        pass

    def to_carrying(self) -> "CarryingFloatWrapper":
        return CarryingFloatWrapper(self.to_float(), self.base, visual_settings=self.visual_settings)


class FloatWrapper(UnitPoint):
    value: float

    def __init__(self, value: float, degree=None, visual_settings=VisualSettings()):
        self.value = value % 1
        self.base = degree
        self.visual_settings = visual_settings

    def to_float(self):
        return self.value

    def to_string(self):
        return str(self.value)

    def after_sigma(self) -> "FloatWrapper":
        after = deepcopy(self)
        assert self.base is not None
        after.value *= self.base
        after.value %= 1
        return after

    def has_degree(self):
        return self.base is not None

    def pre_images(self) -> List["FloatWrapper"]:
        assert self.base is not None
        return [
            FloatWrapper(self.value / self.base + digit / self.base, self.base)
            for digit in range(self.base)
        ]


class NaryFraction(UnitPoint):
    base: int

    def __init__(
        self,
        base: int,
        exact: List[int],
        repeating: List[int],
        visual_settings=VisualSettings(),
    ):
        assert base != 1
        self.base = base
        self.exact = exact
        self.repeating = repeating
        self.visual_settings = visual_settings
        assert max(self.exact + self.repeating) < self.base

    @staticmethod
    def from_string(base, string_representation):
        # TODO: regex
        assert not "." in string_representation
        parts = string_representation.split("_")
        exact = [int(i) for i in parts[0]]
        repeating = []
        if len(parts) > 1:
            repeating = [int(i) for i in parts[1]]
        return NaryFraction(base, exact, repeating)

    def to_string(self):
        overflow_string = ""
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
        after.exact.pop(0)
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
            NaryFraction(
                self.base, [digit] + ret.exact, ret.repeating, self.visual_settings
            )
            for digit in range(self.base)
        ]

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
        return value


class CarryingFloatWrapper(FloatWrapper):
    """like FloatWrapper, but keeps track of the most recent overflowed digit,
    mostly for purpose of animation"""

    def __init__(self, value: float, degree=None, visual_settings=VisualSettings()):
        self.value = value
        self.base = degree
        self.visual_settings = visual_settings

    def cleared(self) -> "FloatWrapper":
        return FloatWrapper(self.value % 1, self.base, self.visual_settings)

    def after_sigma(self) -> "FloatWrapper":
        after = deepcopy(self)
        assert self.base is not None
        after.value *= self.base
        return after

    def centered(self, center: UnitPoint) -> "CarryingFloatWrapper":
        # https://www.desmos.com/calculator/jrc4g7ljum
        x = self.value % 1
        a = center.to_float()
        ret = x - floor(x - a + 0.5)
        return CarryingFloatWrapper(ret, self.base)
