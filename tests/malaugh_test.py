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


# TODO: at least one test with NaryFraction that repeats


def perameterized_test_constant_interval(a: Angle):
    image_of_J = set()

    for xi in x:
        if a < xi and xi < a + 1 / degree:
            image_of_J.add(phi(xi, a))
    assert len(image_of_J) == 1, "{} doesn't work".format(a)


def test_constant_interval():
    for a in a_values:
        perameterized_test_semi_conjigacy(a)


def test_monotone():
    for a in a_values:
        y = FloatWrapper(0, degree)
        for xi in x:
            yi = phi(xi, a)
            if yi != 0.0:
                assert yi >= y, "{} doesn't work".format(a)
            y = yi
