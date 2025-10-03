from functools import lru_cache
from math import floor, pi
from optparse import Option
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np

from manim_lamination_builder import Angle, NaryFraction, sigma
from manim_lamination_builder.points import FloatWrapper, LiftedAngle


def digit_for_phi(x: Angle, JLeftEnd: Angle) -> Optional[int]:
    assert isinstance(x, Angle) and isinstance(JLeftEnd, Angle)
    d = x.degree
    assert JLeftEnd.to_float() * d + 1 <= d
    if x <= JLeftEnd:
        return floor(x.to_float() * d) % (d - 1)
    if x >= JLeftEnd + 1 / d:
        return (floor(x.to_float() * d) - 1) % (d - 1)
    return None


@lru_cache(maxsize=None)  # maxsize=None means unlimited cache size
def image_of_b(a: Angle) -> NaryFraction:
    assert isinstance(a, Angle)
    d = a.degree
    iterate = a
    digits = []
    for _ in range(1000):
        digit = digit_for_phi(iterate, a)
        if digit is None:
            if all([digit2 == d - 2 for digit2 in digits]):
                return LiftedAngle(1, d - 1)
            return NaryFraction(exact=(), repeating=tuple(digits), degree=d - 1)
        digits.append(digit)
        iterate = sigma(iterate)

    return NaryFraction(exact=tuple(digits), repeating=(), degree=d - 1)


def phi(x: Angle, JLeftEnd: Angle) -> NaryFraction:
    assert isinstance(x, Angle) and isinstance(JLeftEnd, Angle)
    assert x.degree == JLeftEnd.degree
    d = x.degree
    added_stuff = image_of_b(JLeftEnd)
    sum = 0  # TODO: do this with NaryFraction
    iterate = x
    for i in range(1000):
        digit = digit_for_phi(iterate, JLeftEnd)
        if digit is None:
            return FloatWrapper(sum + added_stuff.to_float() / (d - 1) ** (i), d - 1)
        sum += digit / (d - 1) ** (i + 1)
        iterate = sigma(iterate)
    return FloatWrapper(sum, d - 1)


def graph_phi(a: Angle):
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
    old_digits = x.to_nary_fraction().exact
    assert x.to_nary_fraction().repeating == (), (
        "it should be obvious how to change the implementation"
    )
    digits = []
    for i, xi in enumerate(old_digits):
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
    return NaryFraction(exact=tuple(digits), repeating=(), degree=d)


def graph_psi(a: Angle, lesser=True):
    x = np.linspace(0, 1, 1000)  # 400 points from 0 to 1
    x = x[0:-1]
    x = [FloatWrapper(xi, degree) for xi in x]
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


# print(psi(0.5, 7.5))


def test_semi_conjigacy_psi(a):
    plt.plot(x, [psi(sigma(x, d - 1), a, d) for x in x], label="psi(sigma_{d-1}(x))")
    plt.plot(x, [sigma(psi(x, a, d), d) for x in x], label="sigma_d(psi(x))")
    plt.xlabel("x")
    plt.title("Semi-Conjigate?")
    plt.legend()
    plt.grid(True)
    plt.show()


# import random
#
# for i in range(100):
#     test_semi_conjigacy_psi(random.random())

# print(psi(1 / 3, 1 / 4))


def test_left_inverse(a):
    b = psi(a, a, d, lesser=True)
    # plt.plot(x, , label="psi(sigma_3(x))")
    plt.plot(x, [phi(psi(x, a, d), b, d) for x in x], label="phi_b(psi_a(x))")
    plt.xlabel("x")
    plt.title("Left Inverse? b=psi_a(a)")
    plt.legend()
    plt.grid(True)
    plt.show()


# import random
#
# for i in range(5):
#     test_left_inverse(random.random())


def graph_psi_diagonal():
    plt.plot(x, [psi(x, x, d) for x in x], label="psi_x(x)")
    plt.xlabel("x")
    plt.title("Monotone Diagonal?")
    plt.legend()
    plt.grid(True)
    plt.show()


# graph_psi_diagonal()
# test_left_inverse(pi % 1)

# for M_2 in [NaryFraction.from_string(2, "_0")]:
#     # M_2 becomes the major under \Psi
#     siblings = M_2.siblings()
#     sibling = M_2.siblings()[siblings[0] == M_2]
#     print(psi(sibling.to_float(), M_2.to_float(), 3, lesser=False))
#
if __name__ == "__main__":
    degree = 2
    x = np.linspace(0, 1, 1000)  # 400 points from 0 to 1
    x = x[0:-1]
    x = [FloatWrapper(xi, degree) for xi in x]
    # graph_psi(0, lesser=True)
    # graph_psi(0, lesser=False)
    # print(
    #     phi(
    #         FloatWrapper(0.7, degree),
    #         FloatWrapper(0.6052287199698223, degree),
    #     )
    # )

    # graph_phi(FloatWrapper(0.6052287199698223, degree))
    graph_psi(FloatWrapper(1 / 12, degree))

    # graph_phi(1 / 3)
    # print(psi(0, 0, 3, lesser=True))
    # print(psi(0, 0, 3, lesser=False))
