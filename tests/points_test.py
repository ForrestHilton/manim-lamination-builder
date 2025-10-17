from numpy.random import rand

from manim_lamination_builder.points import *


def test_original_point_operations():
    assert NaryFraction(degree=3, exact=[0], repeating=[1, 0, 1]).to_string() == "0_101"
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

    a = NaryFraction.from_string(4, "_230")
    assert a.after_sigma().to_string() == "_302"
    assert a.to_string() == "_230"

    assert a.to_string() == "_230"


def test_no_reapeating9s():
    assert NaryFraction.from_string(10, "_9").to_float() == 0.0
    assert NaryFraction.from_string(3, "_2").to_string() != "_2"
    assert NaryFraction.from_string(4, "1_3").to_string() == "2"


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


def test_to_frac():
    assert NaryFraction.from_string(2, "_001").to_fraction() == "1/7"
    assert NaryFraction.from_string(2, "_010").to_fraction() == "2/7"
    assert NaryFraction.from_string(2, "0_001").to_fraction() == "1/14"
    assert NaryFraction.from_string(2, "001").to_fraction() == "1/8"


def test_rand_from_float():
    for d in range(2, 10):
        x = rand()
        assert abs(NaryFraction.from_float(x, 2).to_float()) - x < 0.000001


def test_fraction_float_round_trip():
    for string in ["_001", "_010", "0_001", "001", "_01"]:
        point = NaryFraction.from_string(2, string)
        assert NaryFraction.from_float(point.to_float(), 2) == point
