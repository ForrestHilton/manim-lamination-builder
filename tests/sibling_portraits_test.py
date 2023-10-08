from manim.animation.animation import config
from manim.utils.testing.frames_comparison import frames_comparison

from manim_lamination_builder import (
    Lamination,
    fussCatalan,
    unicritical_polygon,
    Main,
    next_pull_back,
    parse_lamination,
    group,
)
from manim_lamination_builder.constructions import pollygons_are_one_to_one


def test_fuss_catalan():
    "For reasons described in my may 18th talk at the Nippising Topology workshop, this can be predicted using the Fuss-Catillan numbers."
    for d in range(2, 5):
        for n in range(2, 5):
            shape = unicritical_polygon(d, n)
            lamination = Lamination([shape], [], d)
            options = next_pull_back(lamination.to_leafs())
            filtered_options = list(
                filter(
                    lambda lam: pollygons_are_one_to_one(lam),
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
