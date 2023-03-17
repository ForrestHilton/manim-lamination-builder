# Licensed under the The AGPLv3 License (AGPLv3)
# Copyright (c) 2023 Forrest M. Hilton <forrestmhilton@gmail.com>
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from typing import List

from math import cos, pi, sin


class NaryFraction:
    def __init__(self, base: int, exact: List[int], repeating: List[int]):
        assert base != 1
        self.base = base
        self.exact = exact
        self.repeating = repeating

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    @staticmethod
    def from_string(base, string_representation):
        parts = string_representation.split("_")
        exact = [int(i) for i in parts[0]]
        repeating = []
        if len(parts) > 1:
            repeating = [int(i) for i in parts[1]]
        return NaryFraction(base, exact, repeating)

    def to_string(self):
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

        return exact_string + repeating_string

    def sigma(self):
        # multiply the exact part by base
        carry = self.repeating.pop(0)
        self.repeating.append(carry)
        self.exact.append(carry)
        self.exact.pop(0)
        return self

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

    def to_angle(self):
        return self.to_float() * 2 * pi

    def to_cartesian(self):
        angle = self.to_angle()
        return (cos(angle), sin(angle))


assert NaryFraction(3, [1], [1, 0, 1]).to_string() == "1_101"
assert NaryFraction(2, [1], []).to_string() == "1"

assert NaryFraction.from_string(3, "1_101") == NaryFraction(3, [1], [1, 0, 1])
assert NaryFraction.from_string(2, "1") == NaryFraction(2, [1], [])

assert NaryFraction.from_string(3, "_101").sigma().to_string() == "_011"
assert (
    NaryFraction.from_string(10, "_33").to_float()
    == NaryFraction.from_string(3, "1").to_float()
)


assert NaryFraction.from_string(10, "_9").to_float() == 1.0
