from typing import Callable, Iterable

from manim import Scene, tempconfig

from manim_lamination_builder.chord import Chord
from manim_lamination_builder.lamination import LeafLamination
from manim_lamination_builder.main import Main
from manim_lamination_builder.malaugh import Psi, psi
from manim_lamination_builder.orbits import Orbit
from manim_lamination_builder.points import Angle, NaryFraction


class GenerateLams(Scene):
    "displays all the laminations in sorted order generated from the points using the function provided"

    def __init__(
        self, points: Iterable[Angle], quig_function: Callable[[Angle], LeafLamination]
    ):
        self.points = points
        self.quig_function = quig_function
        super().__init__()

    def construct(self):
        for point in sorted(self.points):
            self.add(self.quig_function(point).build(2))
            self.wait(0.1)
            self.clear()


def base_strings(length, radix):
    if radix < 2:
        raise ValueError("radix must be at least 2")
    for i in range(radix**length):
        n = i
        chars = []
        for _ in range(length):
            chars.append(n % radix)
            n //= radix
        yield tuple(reversed(chars))


def periodic_points(max_period=6):
    rets = cumulative_base_strings(max_period, 2)
    return set([NaryFraction(exact=(), repeating=tuple(str), degree=2) for str in rets])


def pre_iterates_of_zero():
    strs = cumulative_base_strings(6, 2)
    return set([NaryFraction(exact=tuple(str), repeating=(), degree=2) for str in strs])


def cumulative_base_strings(max_length, radix):
    for length in range(max_length):
        for string in base_strings(length, radix):
            yield string


def duplicate_by_fixed_points(lam: LeafLamination) -> LeafLamination:
    d = lam.degree
    leaves = []
    for i in range(lam.degree):
        for leaf in lam.leafs:
            leaves.append(Chord(leaf.min + i / (d - 1), leaf.max + i / (d - 1)))

    return LeafLamination(points=[], leafs=leaves, degree=lam.degree)


def Psi_lam(
    lam: LeafLamination, insertion_point: Angle, additional_leaves=False
) -> LeafLamination:
    leaves = []
    for leaf in lam.leafs:
        leaves.append(
            Chord(
                psi(leaf.min, insertion_point),
                psi(leaf.max, insertion_point, lesser=False),
            )
        )
    assert not additional_leaves
    return LeafLamination(points=[], leafs=leaves, degree=lam.degree)


def build_quig(insertion_point: NaryFraction) -> LeafLamination:
    eventual_preimages = []
    for exact in cumulative_base_strings(8, 2):
        eventual_preimages.append(
            NaryFraction(
                exact=exact + insertion_point.exact,
                repeating=insertion_point.repeating,
                degree=2,
            )
        )

    leaves = []
    for p in eventual_preimages:
        leaves.append(Psi(p, insertion_point))
    return LeafLamination(points=[], leafs=leaves, degree=3)


def generable_co_majors() -> LeafLamination:
    leaves = []
    for insertion_point in sorted(periodic_points(9)):
        sibling = insertion_point.other_sibling()[0]
        leaves.append(Psi(sibling, insertion_point))
    return LeafLamination(points=[], leafs=leaves, degree=3)


def short_quig(insertion_point: NaryFraction) -> LeafLamination:
    "takes a quadratic insertion point and performs two insertions"
    assert insertion_point.degree == 2
    cubic = build_quig(insertion_point)
    new_insertion_point = psi(insertion_point, insertion_point)
    return Psi_lam(cubic, new_insertion_point)


def long_quig(insertion_point: NaryFraction) -> LeafLamination:
    "takes a quadratic insertion point and performs two insertions"
    assert insertion_point.degree == 2
    cubic = build_quig(insertion_point)
    new_insertion_point = psi(insertion_point.other_sibling()[0], insertion_point)
    return Psi_lam(
        cubic, new_insertion_point, additional_leaves=not insertion_point.periodic()
    )


if __name__ == "__main__":
    with tempconfig({"quality": "high_quality", "preview": True}):
        GenerateLams(periodic_points(5), long_quig).render()
    with tempconfig(
        {"quality": "fourk_quality", "preview": True}  # , "background_color": WHITE
    ):
        pass
        # Main([build_quig(NaryFraction.from_string(2, "_01"))]).render()
        # Main([duplicate_by_fixed_points(generable_co_majors())]).render()
        # Quigs(pre_iterates_of_zero).render()
        # Main([short_quig(NaryFraction.from_string(2, "_01"))]).render()
