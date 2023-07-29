from copy import deepcopy
from manim_lamination_builder.constructions import unicritical_polygon
from manim_lamination_builder.lamination import Lamination
from manim_lamination_builder.chord import Chord

from manim_lamination_builder.custom_json import custom_dump, custom_parse
from typing import List, Callable
from manim.utils.color import Colors
from manim import tempconfig

from manim_lamination_builder.points import UnitPoint, NaryFraction, sigma
from manim_lamination_builder.visual_settings import VisualSettings, get_color


def crosses(A: NaryFraction, B: NaryFraction, loops):
    cords: List[Chord] = []
    for loop in loops:
        for i in range(len(loop)):
            x = loop[i]
            y = loop[(i + 1) % len(loop)]
            cords.append(Chord(x, y))
    cords.pop()

    target = Chord(A, B)
    return any([target.crosses(reference) for reference in cords])


# mutates the given lists
def _generate(
    loops: List[List[NaryFraction]],
    remaining: List[List[NaryFraction]],
    original_shape: List[NaryFraction],
) -> List[List[List[NaryFraction]]]:
    order = len(original_shape)
    # must include original polygon
    if len(loops) == 0:
        loops.append([])
        for i in range(order):
            p = original_shape[i]
            assert p == remaining[i].pop(remaining[i].index(p))
            loops[0].append(p)

    assert len(loops) != 0
    # select the loop in progress
    if len(loops[-1]) == order:  # is it finished?
        if len(remaining[0]) == 0:
            return [loops]
        loops.append([remaining[0].pop(0)])  # start next loop

    sibling_portraits = []
    assert len(loops[-1]) != 0
    next_connection_options = remaining[
        len(loops[-1])
    ]  # iterate over options for its next step / how to continue polygon
    for i, next_point in enumerate(next_connection_options):
        if not crosses(next_point, loops[-1][-1], loops):
            n_remaining = deepcopy(remaining)
            n_loops = deepcopy(loops)
            n_loops[-1].append(n_remaining[len(loops[-1])].pop(i))
            sibling_portraits.extend(_generate(n_loops, n_remaining, original_shape))

    return sibling_portraits


def generate_sibling_portraits(original_shape: List[NaryFraction]) -> List[Lamination]:
    "For reasons descirbed in my may 18th talk at the Nippising Topology workshop, this can be predicted using the Fuss-Catillan numbers."
    order = len(original_shape)
    degree = original_shape[0].base
    original_shape = list(map(lambda x: x.cleared(), original_shape))

    # generate all the point
    # Each index in all points contains the list of points which are sibling to the
    # corresponding point in original shape.
    # For example the points in the 1st list of all points includes the 1st
    # point in the original shape.
    all_points = []

    for i in range(order):
        siblings = original_shape[i].siblings()
        while siblings[0].to_float() < original_shape[i].to_float():
            siblings.append(siblings.pop(0))
        all_points.append(siblings)

    portraits = _generate([], deepcopy(all_points), original_shape)
    data = [Lamination(pollygons, [], degree) for pollygons in portraits]
    for lam in data:
        lam.auto_populate()

    return data


def generate_unicritical_lamination(degree, order):
    original_shape = unicritical_polygon(degree, order)

    data = generate_sibling_portraits(original_shape)
    return data


def remove_non_original_pollygons(lams: List[Lamination]):
    "deceptivly named"
    lam = lams[0]
    lam.polygons = [lam.polygons[0]]
    return [lam]


if __name__ == "__main__":
    with tempconfig(
        {
            "quality": "medium_quality",
            "preview": True,
            "background_color": Colors.white.value,
        }
    ):
        from manim_lamination_builder import Main

        Main(generate_unicritical_lamination(4, 3)).render()

# "0_122" is a proposed test case
