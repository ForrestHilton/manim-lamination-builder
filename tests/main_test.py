from manim.animation.animation import config
from manim.utils.testing.frames_comparison import frames_comparison

from manim_lamination_builder import (
    Lamination,
    fussCatalan,
    unicritical_polygon,
    Main,
    next_pull_back,
    generate_sibling_portraits,
    parse_lamination,
    group,
)


def test_sibling_portraits():
    shape = parse_lamination(
        """{polygons:[['_001','_010','_100']],radix:3}"""
    ).polygons[0]
    portraits = generate_sibling_portraits(shape)
    assert len(portraits) == 3


def test_catalan():
    for d in range(2, 5):
        for n in range(2, 5):
            shape = unicritical_polygon(d, n)
            lamination = Lamination([shape], [], d)
            options = next_pull_back(lamination.to_leafs())
            filtered_options = list(
                filter(
                    lambda lam: n
                    == max([len(poly) for poly in lam.to_polygons().polygons]),
                    options,
                )
            )
            assert len(filtered_options) == fussCatalan(d - 1, n)


if __name__ == "__main__":
    n = 4
    d = 3
    shape = unicritical_polygon(d, n)
    lamination = Lamination([shape], [], d)
    config.preview = True
    options = next_pull_back(lamination.to_leafs())
    Main([lam.to_polygons() for lam in options]).render()
    filtered_options = list(
        filter(
            lambda lam: n == max([len(poly) for poly in lam.to_polygons().polygons]),
            options,
        )
    )
