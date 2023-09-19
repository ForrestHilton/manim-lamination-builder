from manim_lamination_builder.points import *


def test_original_point_operations():
    assert NaryFraction(3, [1], [1, 0, 1]).to_string() == "1_101"
    assert NaryFraction(2, [1], []).to_string() == "1"

    assert NaryFraction.from_string(3, "1_101") == NaryFraction(3, [1], [1, 0, 1])
    assert NaryFraction.from_string(2, "1") == NaryFraction(2, [1], [])

    assert NaryFraction.from_string(3, "_101").after_sigma().to_string() == "1._011"
    assert NaryFraction.from_string(3, "1._101").to_string() == "1._101"
    assert (
        NaryFraction.from_string(10, "_33").to_float()
        == NaryFraction.from_string(3, "1").to_float()
    )

    assert NaryFraction.from_string(10, "_9").to_float() == 1.0

    assert (
        NaryFraction.from_string(4, "0_300").without_enharmonics().to_string() == "_030"
    )

    a = NaryFraction.from_string(4, "_230")
    assert a.after_sigma().to_string() == "2._302"
    assert a.to_string() == "_230"

    assert a.after_sigma_shortest_ccw().to_string() == "_302"
    assert a.to_string() == "_230"

def test_not_wraping1():
    a = NaryFraction.from_string(4, "_230")
    assert a.after_sigma().to_float() == NaryFraction.from_string(4,"_302").to_float()

def test_not_wraping2():
    a = NaryFraction.from_string(4, "_230")
    assert a.after_sigma().to_string() == "_302"
