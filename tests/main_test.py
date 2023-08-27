from manim_lamination_builder import generate_sibling_portraits, parse_lamination, group
from manim.utils.testing.frames_comparison import frames_comparison


def test_sibling_portraits():
    shape = parse_lamination(
        """{polygons:[['_001','_010','_100']],radix:3}"""
    ).polygons[0]
    portraits = generate_sibling_portraits(shape)
    assert len(portraits) == 3
