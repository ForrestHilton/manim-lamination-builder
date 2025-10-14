from manim import tempconfig
from numpy import binary_repr

from manim_lamination_builder.chord import Chord
from manim_lamination_builder.lamination import LeafLamination
from manim_lamination_builder.main import Main
from manim_lamination_builder.malaugh import psi
from manim_lamination_builder.points import NaryFraction

# insert at _10 in degree 2 to make a quig in degree 3.
binary_strings = []
i = 0
length = 8
while i < 2**length:
    binary_strings.append(binary_repr(i, length))

    i += 1


def base_strings(length, radix):
    if radix < 2:
        raise ValueError("radix must be at least 2")
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:radix]
    for i in range(radix**length):
        n = i
        chars = []
        for _ in range(length):
            chars.append(digits[n % radix])
            n //= radix
        yield "".join(reversed(chars))


grand_orbit = []
insertion_point = NaryFraction.from_string(2, "_10")
for repeating in [(0, 1), (1, 0)]:  # TODO: compute orbit
    for exact in binary_strings:
        grand_orbit.append(
            NaryFraction(exact=tuple(exact), repeating=repeating, degree=2)
        )

leaves = []
for p in grand_orbit:
    leaves.append(Chord(psi(p, insertion_point), psi(p, insertion_point, lesser=False)))

if __name__ == "__main__":
    with tempconfig(
        {"quality": "high_quality", "preview": True}  # , "background_color": WHITE
    ):
        Main([LeafLamination(points=[], leafs=leaves, degree=3)]).render()

# first generate all
