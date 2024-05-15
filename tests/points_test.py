from manim_lamination_builder.constructions import sigma
from manim_lamination_builder.points import *


def test_original_point_operations():
    assert NaryFraction(degree=3, exact=[1], repeating=[1, 0, 1]).to_string() == "1_101"
    assert NaryFraction(degree=2, exact=[1], repeating=[]).to_string() == "1"

    assert NaryFraction.from_string(3, "1_101") == NaryFraction(
        degree=3, exact=[1], repeating=[1, 0, 1]
    )
    assert NaryFraction.from_string(2, "1") == NaryFraction(
        degree=2, exact=[1], repeating=[]
    )

    assert NaryFraction.from_string(3, "_101").after_sigma().to_string() == "_011"
    assert (
        NaryFraction.from_string(10, "_33").to_float()
        == NaryFraction.from_string(3, "1").to_float()
    )

    assert NaryFraction.from_string(10, "_9").to_float() == 1.0

    a = NaryFraction.from_string(4, "_230")
    assert a.after_sigma().to_string() == "_302"
    assert a.to_string() == "_230"

    assert a.to_string() == "_230"


def test_not_wraping1():
    a = NaryFraction.from_string(4, "_230")
    assert a.after_sigma().to_float() == NaryFraction.from_string(4, "_302").to_float()


def test_not_wraping2():
    a = NaryFraction.from_string(4, "_230")
    assert a.after_sigma().to_string() == "_302"


def test_preimage():
    a = NaryFraction.from_string(4, "_230")
    assert all([sigma(p) == a for p in a.pre_images()])
    b = FloatWrapper(0.5, 4)
    assert all([sigma(p) == b for p in b.pre_images()])
    assert len(b.pre_images()) == len(a.pre_images()) == 4
