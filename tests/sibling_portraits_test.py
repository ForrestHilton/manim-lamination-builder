from manim.animation.animation import config
from manim.utils.testing.frames_comparison import frames_comparison

from manim_lamination_builder import (
    GapLamination,
    fussCatalan,
    unicritical_polygon,
    Main,
    next_pull_back,
    parse_lamination,
    group,
)
from manim_lamination_builder.constructions import pollygons_are_one_to_one


def test_full_portraits():
    "For reasons described in my may 18th talk at the Nippising Topology workshop, this can be predicted using the Fuss-Catillan numbers."
    for d in range(2, 5):
        for n in range(2, 5):
            shape = unicritical_polygon(d, n)
            lamination = GapLamination(polygons=[shape], points=[], degree=d)
            options = next_pull_back(lamination)
            filtered_options = list(
                filter(
                    lambda lam: pollygons_are_one_to_one(lam),
                    options,
                )
            )
            assert len(filtered_options) == fussCatalan(d - 1, n)


def test_all_portraits():
    "This test will pass for reasons explained in my talk at The 57th Spring Topology and Dynamics Conference"
    for d in range(2, 3):
        for n in range(3, 5):
            shape = unicritical_polygon(d, n)
            lamination = GapLamination(polygons=[shape], points=[], degree=d)
            options = next_pull_back(lamination)
            assert len(options) == fussCatalan(d - 1, n + 1)


if __name__ == "__main__":
    pass
