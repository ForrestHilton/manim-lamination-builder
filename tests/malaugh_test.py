import math
import random

import numpy as np

from manim_lamination_builder import FloatWrapper, sigma
from manim_lamination_builder.chord import Chord
from manim_lamination_builder.construct_quigs import build_quig
from manim_lamination_builder.lamination import LeafLamination
from manim_lamination_builder.malaugh import Psi, phi, psi
from manim_lamination_builder.points import Angle, NaryFraction

degree = 3
x = np.linspace(0, 1, 20)  # 400 points from 0 to 1
x = x[0:-1]
x = [FloatWrapper(xi, degree) for xi in x]
a_values = [FloatWrapper(random.random() % 0.66, degree) for _ in range(16)]


def perameterized_test_semi_conjigacy(a: Angle):
    for xi in x:
        if xi < a or a + 1 / degree < xi:
            assert math.isclose(
                phi(sigma(xi), a).to_float(), sigma(phi(xi, a)).to_float()
            ), "{} doesn't work".format(a)


def test_semi_conjigacy():
    for a in a_values:
        perameterized_test_semi_conjigacy(a)


def test_one_semi_conjigacy():
    perameterized_test_semi_conjigacy(FloatWrapper(0.2126636966021872, degree))


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


def test_psi_examples():
    assert psi(
        NaryFraction.from_string(2, "0"), NaryFraction.from_string(2, "0")
    ) == NaryFraction.from_string(3, "0")

    assert psi(
        NaryFraction.from_string(2, "0"), NaryFraction.from_string(2, "0"), lesser=False
    ) == NaryFraction.from_string(3, "_1")

    assert psi(
        NaryFraction.from_string(2, "1"), NaryFraction.from_string(2, "0")
    ) == NaryFraction.from_string(3, "2")
    assert psi(
        NaryFraction.from_string(2, "1"), NaryFraction.from_string(2, "0"), lesser=False
    ) == NaryFraction.from_string(3, "2_1")


def test_quigs_period_shortens_major():
    "tests that the length of the major of a quig decreases as the period increases"
    len = 1
    for period in range(1, 10):
        point = NaryFraction.from_string(2, "_" + "0" * (period - 1) + "1")
        quig = build_quig(point)
        new_len = quig.major().length()
        assert new_len > 1 / 3
        assert new_len < len
        len = new_len


test_quigs_period_shortens_major()


def test_reg_critical_quigs_have_correct_major_length():
    for len in range(1, 10):
        point = NaryFraction.from_string(2, "0" * (len - 1) + "1")
        quig = build_quig(point)
        assert math.isclose(quig.major().length(), 1 / 3)


def test_you_can_have_degenerate_leaves():
    zero = NaryFraction.from_string(2, "0")
    assert (
        len(LeafLamination(points=[], leafs=[Chord(zero, zero)], degree=2).leafs) == 1
    )


def test_manual_examples():
    # first test the examples worked in Dr Mayer's office on Oct 27
    assert psi(
        NaryFraction.from_string(2, "_0011"), NaryFraction.from_string(2, "_100")
    ) == NaryFraction.from_string(3, "_0022")

    assert Psi(
        NaryFraction.from_string(3, "_0022"), NaryFraction.from_string(3, "_2002")
    ) == Chord(
        NaryFraction.from_string(4, "_0032"), NaryFraction.from_string(4, "_0033")
    )
