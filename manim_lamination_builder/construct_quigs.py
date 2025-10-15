from manim import Scene, tempconfig
from numpy import binary_repr

from manim_lamination_builder.chord import Chord
from manim_lamination_builder.lamination import LeafLamination
from manim_lamination_builder.main import Main
from manim_lamination_builder.malaugh import psi
from manim_lamination_builder.orbits import Orbit
from manim_lamination_builder.points import NaryFraction

# insert at _10 in degree 2 to make a quig in degree 3.


def base_strings(length, radix):  # TODO: convert to an iteraitor of narryfractions
    if radix < 2:
        raise ValueError("radix must be at least 2")
    for i in range(radix**length):
        n = i
        chars = []
        for _ in range(length):
            chars.append(n % radix)
            n //= radix
        yield reversed(chars)


def build_quig(insertion_point: NaryFraction) -> LeafLamination:
    grand_orbit = []
    for periodic in Orbit(insertion_point).getTemporalOrbit():  # TODO: compute orbit
        for exact in base_strings(8, 2):
            grand_orbit.append(
                NaryFraction(exact=tuple(exact), repeating=periodic.repeating, degree=2)
            )

    leaves = []
    for p in grand_orbit:
        leaves.append(
            Chord(psi(p, insertion_point), psi(p, insertion_point, lesser=False))
        )
    return LeafLamination(points=[], leafs=leaves, degree=3)


class Quigs(Scene):
    def construct(self):
        # points = set()
        for str in base_strings(5, 2):
            point = NaryFraction(exact=(), repeating=tuple(str), degree=2)
            if len(point.repeating) == 0:
                continue
            # if point in points:
            #     continue
            # points.update(point)
            self.add(build_quig(point).build(2))
            self.wait(0.1)
            self.clear()


insertion_point = NaryFraction.from_string(2, "_10")
if __name__ == "__main__":
    with tempconfig(
        {"quality": "high_quality", "preview": True}  # , "background_color": WHITE
    ):
        Quigs().render()

# first generate all
