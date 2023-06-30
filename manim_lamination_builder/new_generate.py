# write a python function that takes a single argument which is a list length n of lists of length d. it should generate all of the ways of combining the elements of the lists into lists with no overlap and taking exactly one element from each of the original lists.  attempt to use combinatoric function from itertools.


from copy import deepcopy
from typing import List, Callable
from manim.utils.color import Colors
from itertools import product

from manim_lamination_builder import (
    UnitPoint,
    NaryFraction,
    Lamination,
    Chord,
    custom_dump,
    custom_parse,
)


def crosses(A: NaryFraction, B: NaryFraction, decided_on: Lamination):
    cords: List[Chord] = []

    target = Chord(A, B)
    return any([target.crosses(reference) for reference in cords])


def combine(list_of_lists):
    return list(product(*list_of_lists))


input_lists = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]


result = combine(input_lists)
print(result)
# [(1, 3, 5), (1, 3, 6), (1, 4, 5), (1, 4, 6), (2, 3, 5), (2, 3, 6), (2, 4, 5), (2, 4, 6)]
