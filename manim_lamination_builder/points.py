# Licensed under the The AGPLv3 License (AGPLv3)
# Copyright (c) 2023 Forrest M. Hilton <forrestmhilton@gmail.com>
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from functools import lru_cache

from typing import Annotated, List, Optional, Sequence, Union

from math import cos, pi, sin, floor

from manim.animation.animation import deepcopy
from pydantic import BaseModel, ValidationInfo, field_validator, model_validator
from annotated_types import Gt
from abc import ABC, abstractmethod
import numpy as np

from manim_lamination_builder.visual_settings import VisualSettings


def angle_to_cartesian(angle: float):
    return np.array([cos(angle), sin(angle), 0])


Degree = Annotated[int, Gt(1)]


class _Angle(ABC):
    visual_settings: VisualSettings = VisualSettings()
    degree: Degree

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
    def after_sigma(self) -> "_Angle":
        pass

    def to_angle(self) -> float:
        return self.to_float() * 2 * pi

    def to_cartesian(self):
        return angle_to_cartesian(self.to_angle())

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        return hash(floor(self.to_float() / 0.0000002))

    def has_degree(self) -> bool:
        return True

    def siblings(self) -> Sequence["_Angle"]:
        ret = self.after_sigma().pre_images()
        assert self in ret
        return ret

    @abstractmethod
    def pre_images(self) -> Sequence["_Angle"]:
        pass

    def lifted(self) -> "LiftedAngle":
        return LiftedAngle(
            self.to_float(), self.degree, visual_settings=self.visual_settings
        )


class FloatWrapper(_Angle, BaseModel):
    value: float

    def __init__(self, value: float, degree: Degree, visual_settings=VisualSettings()):
        super(FloatWrapper, self).__init__(
            value=value % 1, degree=degree, visual_settings=visual_settings
        )

    def to_float(self):
        return self.value

    def to_string(self):
        return str(self.value)

    def after_sigma(self) -> "FloatWrapper":
        after = deepcopy(self)
        assert self.degree is not None
        after.value *= self.degree
        after.value %= 1
        return after

    def has_degree(self):
        return self.degree is not None

    def pre_images(self) -> List["FloatWrapper"]:
        assert self.degree is not None
        return [
            FloatWrapper(self.value / self.degree + digit / self.degree, self.degree)
            for digit in range(self.degree)
        ]


class NaryFraction(_Angle, BaseModel):
    degree: Degree
    exact: tuple[int, ...]
    repeating: tuple[int, ...]

    @field_validator("exact", "repeating")
    @classmethod
    def _check_values(cls, v, info: ValidationInfo):
        degree = int(info.data["degree"])
        for n in v:
            assert n >= 0 and n < degree, "{} not a valid {}-ary digit".format(
                n, degree
            )
        return v

    # https://github.com/csfalcione/laminations-lib/blob/master/src/fractions.ts
    @model_validator(mode="before")
    @classmethod
    def _simplify(cls, v: dict) -> dict:
        assert isinstance(v, dict)
        degree = v["degree"]
        exact = v["exact"]
        repeating = v["repeating"]
        while len(exact) > 0 and len(repeating) > 0 and exact[-1] == repeating[-1]:
            exact = exact[:-1]
            repeating = (repeating[-1],) + tuple(repeating[:-1])

        return {"degree": degree, "exact": exact, "repeating": repeating}

    @staticmethod
    def from_string(degree, string_representation):
        assert "." not in string_representation
        parts = string_representation.split("_")
        exact = tuple([int(i) for i in parts[0]])
        repeating = ()
        if len(parts) > 1:
            repeating = tuple([int(i) for i in parts[1]])
        return NaryFraction(degree=degree, exact=exact, repeating=repeating)

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
        # multiply the exact part by degree
        exact = self.exact
        repeating = self.repeating
        if self.repeating:
            carry = repeating[0]
            repeating = repeating[1:] + (carry,)
            exact = exact + (carry,)
        exact = exact[1:]
        return NaryFraction(
            degree=self.degree,
            exact=exact,
            repeating=repeating,
            visual_settings=self.visual_settings,  # pyright: ignore
        )

    def pre_images(self) -> List["NaryFraction"]:
        ret = self
        return [
            NaryFraction(
                degree=self.degree,
                exact=(digit,) + ret.exact,
                repeating=ret.repeating,
                visual_settings=self.visual_settings,  # pyright: ignore
            )
            for digit in range(self.degree)
        ]

    @lru_cache(maxsize=None)
    @staticmethod
    def _cached_to_float(
        degree: Degree, exact: tuple[int, ...], repeating: tuple[int, ...]
    ) -> float:
        value = sum([n / degree ** (i + 1) for i, n in enumerate(exact)])
        if len(repeating) != 0:
            value += (
                sum(
                    [
                        n / degree ** (i + 1 - len(repeating))
                        for i, n in enumerate(repeating)
                    ]
                )
                / degree ** len(exact)
                / (degree ** len(repeating) - 1)
            )
        return value

    def to_float(self) -> float:
        return NaryFraction._cached_to_float(self.degree, self.exact, self.repeating)

    def pre_period(self) -> int:
        return len(self.exact)


class LiftedAngle(_Angle, BaseModel):
    """like FloatWrapper, but keeps track of the most recent overflowed digit,
    mostly for purpose of animation"""

    value: float

    def __init__(self, value: float, degree: Degree, visual_settings=VisualSettings()):
        super(LiftedAngle, self).__init__(
            value=value, degree=degree, visual_settings=visual_settings
        )

    def principal(self) -> "FloatWrapper":
        return FloatWrapper(self.value % 1, self.degree, self.visual_settings)

    def after_sigma(self) -> "LiftedAngle":
        after = deepcopy(self)
        assert self.degree is not None
        after.value *= self.degree
        return after

    def centered(self, center: _Angle) -> "LiftedAngle":
        # https://www.desmos.com/calculator/jrc4g7ljum
        x = self.value % 1
        a = center.to_float()
        ret = x - floor(x - a + 0.5)
        return LiftedAngle(ret, self.degree)

    def to_float(self):
        return self.value

    def to_string(self):
        return str(self.value)

    def has_degree(self):
        return self.degree is not None

    def pre_images(self) -> List["LiftedAngle"]:
        assert self.degree is not None
        return [
            LiftedAngle(self.value / self.degree + digit / self.degree, self.degree)
            for digit in range(self.degree)
        ]


Angle = Union[NaryFraction, FloatWrapper, LiftedAngle]
PrincipalAngle = Union[NaryFraction, FloatWrapper]
