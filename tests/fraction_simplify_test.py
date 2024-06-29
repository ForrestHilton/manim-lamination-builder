from manim_lamination_builder.constructions import sigma
from manim_lamination_builder.points import *

# this document is copied from https://github.com/csfalcione/laminations-lib


def test_redundant_exact_suffix():
    # Test case for redundant exact suffix
    fraction = NaryFraction(degree=4, exact=(1,), repeating=(1, 0, 1))
    assert fraction.exact == ()
    assert fraction.repeating == (1, 1, 0)


# def test_over_specified_repeating_part():
#     # Test case for over-specified repeating part
#     fraction = NaryFraction(degree=4, exact=(), repeating=(1, 0, 1, 1, 0, 1))
#     assert fraction.repeating == (1, 0, 1)
#     fraction = NaryFraction(degree=4, exact=(), repeating=(3, 3, 3))
#     assert fraction.repeating == (3)
#
#
# def test_repeating_d_minus_1_in_base_d():
#     # Test case for repeating d-1 in base d
#     fraction = NaryFraction(degree=3, exact=(), repeating=(2,))
#     assert fraction.exact == ()
#     assert fraction.repeating == ()
#     fraction = NaryFraction(degree=3, exact=(2, 1), repeating=(2,))
#     assert fraction.exact == (2, 2)
#     assert fraction.repeating == ()
#
#
# def test_trailing_zeroes():
#     # Test case for trailing zeroes
#     fraction = NaryFraction(degree=2, exact=(1, 0, 0), repeating=())
#     assert fraction.exact == (1,)
#     assert fraction.repeating == ()
#     fraction = NaryFraction(degree=2, exact=(1,), repeating=(0,))
#     assert fraction.exact == (1,)
#     assert fraction.repeating == ()
