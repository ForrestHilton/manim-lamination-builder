from functools import lru_cache
from math import floor, pi
from optparse import Option
from typing import Optional, Union

import matplotlib.pyplot as plt
import numpy as np

from manim_lamination_builder.chord import Chord
from manim_lamination_builder.points import (
    Angle,
    FloatWrapper,
    LiftedAngle,
    NaryFraction,
    sigma,
)


def digit_for_phi(x: Angle, JLeftEnd: Angle) -> Optional[int]:
    assert isinstance(x, Angle) and isinstance(JLeftEnd, Angle)
    d = x.degree
    assert JLeftEnd.to_float() * d + 1 <= d
    if x <= JLeftEnd:
        return floor(x.to_float() * d) % (d - 1)
    if x >= JLeftEnd + 1 / d:
        return (floor(x.to_float() * d) - 1) % (d - 1)
    return None


def phi(x: Angle, JLeftEnd: Angle) -> NaryFraction:
    assert isinstance(x, Angle) and isinstance(JLeftEnd, Angle)
    assert x.degree == JLeftEnd.degree
    d = x.degree

    def overline_sigma(x: Angle):
        if x >= JLeftEnd and x <= JLeftEnd + 1 / d:
            return sigma(JLeftEnd)
        return sigma(x)

    iterate = x
    digits = []
    for i in range(1000):
        digit = digit_for_phi(iterate, JLeftEnd)
        if digit is None:
            digit = JLeftEnd.to_nary_fraction().digit(1)
        digits.append(digit)
        iterate = overline_sigma(iterate)
    return NaryFraction(
        exact=tuple(digits),
        repeating=(),  # TODO: do more with this
        degree=d - 1,
        visual_settings=x.visual_settings,
    )


def graph_phi(a: Angle):
    x = np.linspace(0, 1, 200)  # 400 points from 0 to 1
    x = x[0:-1]
    x = [FloatWrapper(xi, a.degree) for xi in x]
    y = [phi(xi, a) for xi in x]
    plt.plot([x.to_float() for x in x], [yi.to_float() for yi in y], label="phi(x)")
    plt.xlabel("x")
    plt.ylabel("phi(x)")
    plt.title("Graph of phi(x) a = {}".format(a))
    plt.legend()
    plt.grid(True)
    plt.show()


def psi(x: Angle, a: Angle, lesser=True) -> Angle:
    assert isinstance(x, Angle) and isinstance(a, Angle)
    assert x.degree == a.degree
    d = a.degree + 1
    iterate = x
    x = x.to_nary_fraction()
    digits_parts = []
    for old_digits in [x.exact, (x.repeating if x.repeating != () else (0,))]:
        digits = []
        for xi in old_digits:
            # print(iterate)
            criteria = None
            if lesser:
                criteria = iterate <= a
            else:
                criteria = iterate < a
            if criteria:
                digits.append(xi)
            else:
                digits.append(xi + 1)
            iterate = sigma(iterate)
        digits_parts.append(digits)
    return NaryFraction(
        exact=digits_parts[0],
        repeating=digits_parts[1],
        degree=d,
        visual_settings=x.visual_settings,
    )


def Psi(x: Union[Chord, Angle], a: Angle) -> Chord:
    if isinstance(x, Chord):
        return Chord(psi(x.min, a), psi(x.max, a, lesser=False))
    return Chord(psi(x, a), psi(x, a, lesser=False))


def graph_psi(a: Angle, lesser=True):
    x = np.linspace(0, 1, 1000)  # 400 points from 0 to 1
    x = x[0:-1]
    x = [FloatWrapper(xi, a.degree) for xi in x]
    y = [psi(x, a, lesser=lesser) for x in x]
    x = [xi.to_float() for xi in x]
    y = [yi.to_float() for yi in y]
    pos = np.where(np.abs(np.diff(y)) >= 0.01)[0] + 1
    x = np.insert(x, pos, np.nan)
    y = np.insert(y, pos, np.nan)
    plt.plot(x, y)
    plt.xlim(-0.005, 1.005)
    plt.ylim(-0.005, 1.005)
    plt.xlabel("x")
    # plt.ylabel("psi(x)")
    plt.title("Graph of psi^{}(x) a = {}".format("-" if lesser else "+", a))
    plt.legend()
    plt.grid(True)
    plt.show()


def graph_phi_semi_conjigacy(a: Angle):
    x = np.linspace(0, 1, 1000)  # 400 points from 0 to 1
    x = x[0:-1]
    x = [FloatWrapper(xi, a.degree) for xi in x]
    plt.plot(
        [x.to_float() for x in x],
        [sigma(phi(xi, a)).to_float() for xi in x],
        label="sigma(phi(x))",
    )
    plt.plot(
        [x.to_float() for x in x],
        [phi(sigma(xi), a).to_float() for xi in x],
        label="phi(sigma(x))",
    )
    plt.xlabel("x")
    plt.ylabel("phi(x)")
    plt.title("Graph of phi(x) a = {}".format(a))
    plt.legend()
    plt.grid(True)
    plt.show()


# print(psi(0.5, 7.5))


# graph_psi_diagonal()
# test_left_inverse(pi % 1)

# for M_2 in [NaryFraction.from_string(2, "_0")]:
#     # M_2 becomes the major under \Psi
#     siblings = M_2.siblings()
#     sibling = M_2.siblings()[siblings[0] == M_2]
#     print(psi(sibling.to_float(), M_2.to_float(), 3, lesser=False))
#
if __name__ == "__main__":
    # pass
    degree = 2
    # graph_psi(0, lesser=True)
    # graph_psi(NaryFraction.from_string(2, "_0001"), lesser=False)
    # a = NaryFraction.from_string(2, "_0001")
    # print(Psi(a, a))
    # print(
    #     phi(
    #         FloatWrapper(0.7, degree),
    #         FloatWrapper(0.6052287199698223, degree),
    #     )
    # )

    # b = 0.5
    # print(psi(FloatWrapper(b, degree), FloatWrapper(b, degree)).to_float())
    # for m in range(1, 40):
    #     M = 2**m
    #     a = b - 1 / M
    #     print(psi(FloatWrapper(a, degree), FloatWrapper(b, degree)).to_float())

    # graph_phi(FloatWrapper(0.6052287199698223, 3))
    # graph_psi(FloatWrapper(1 / 12, degree))

    graph_phi(FloatWrapper(1 / 3, 3))
    # print(psi(0, 0, 3, lesser=True))
    # print(psi(0, 0, 3, lesser=False))
