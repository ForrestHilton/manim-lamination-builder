import random

import numpy as np

from manim_lamination_builder import FloatWrapper, sigma
from manim_lamination_builder.malaugh import phi, psi
from manim_lamination_builder.points import Angle

degree = 3
x = np.linspace(0, 1, 20)  # 400 points from 0 to 1
x = x[0:-1]
x = [FloatWrapper(xi, degree) for xi in x]
a_values = [FloatWrapper(random.random() % 0.66, degree) for _ in range(16)]


def perameterized_test_semi_conjigacy(a: Angle):
    for xi in x:
        if xi < a or a + 1 / degree < xi:
            assert phi(sigma(xi), a) == sigma(phi(xi, a)), "{} doesn't work".format(a)


def test_semi_conjigacy():
    for a in a_values:
        perameterized_test_semi_conjigacy(a)


def test_one_semi_conjigacy():
    perameterized_test_semi_conjigacy(FloatWrapper(0.2126636966021872, degree))


# TODO: at least one test with NaryFraction that repeats


# TODO: 0.2126636966021872 doesn't work
def perameterized_test_constant_interval(a: Angle):
    image_of_J = set()

    for xi in x:
        if a < xi and xi < a + 1 / degree:
            image_of_J.add(phi(xi, a))
    assert len(image_of_J) == 1, "{} doesn't work".format(a)


def test_constant_interval():
    for a in a_values:
        perameterized_test_constant_interval(a)


def test_one_constant_interval():
    perameterized_test_constant_interval(FloatWrapper(0.2126636966021872, degree))


def test_monotone_degree_one():
    for a in a_values:
        y = FloatWrapper(0, degree)
        components_of_zero_fiber = 1
        for xi in x:
            yi = phi(xi, a)
            if yi != 0.0:
                assert yi >= y, "{} doesn't work".format(a)
            if yi == 0 and y != 0:
                components_of_zero_fiber += 1
            y = yi
        assert components_of_zero_fiber < 3, "{} doesn't work".format(a)


def perameterized_test_semi_conjigacy_psi(a: Angle):
    for xi in x:
        assert psi(sigma(xi), a) == sigma(psi(xi, a)), "{} doesn't work".format(a)


def test_semi_conjigacy_psi():
    for a in a_values:
        perameterized_test_semi_conjigacy_psi(a)


# import random
#
# for i in range(100):
#     test_semi_conjigacy_psi(random.random())

# print(psi(1 / 3, 1 / 4))


def perameterized_test_left_inverse(a: Angle):
    b = psi(a, a, lesser=True)
    for xi in x:
        assert phi(psi(xi, a), b) == xi
