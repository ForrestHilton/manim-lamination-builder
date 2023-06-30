# write a python function that takes a single argument which is a list length n of lists of length d. it should generate all of the ways of combining the elements of the lists into lists with no overlap and taking exactly one element from each of the original lists.  attempt to use combinatoric function from itertools.


from copy import deepcopy
from typing import List, Callable
from manim.utils.color import Colors
from itertools import product, permutations

from manim_lamination_builder import (
    UnitPoint,
    NaryFraction,
    Lamination,
    Chord,
    custom_dump,
    custom_parse,
)


def sibling_collections_of_leaf_in_existing(
    leaf: Chord, existing: Lamination
) -> List[Lamination]:
    """
    note that it includes the existing laminaition in addition to
    """
    collections = []
    pre_a = leaf.min.pre_images()
    pre_b = leaf.max.pre_images()
    for indesies in permutations(range(len(pre_b))):
        collection = deepcopy(existing)
        for i, j in enumerate(indesies):
            l = Chord(pre_a[i], pre_b[j])
            if crosses(collection, l):
                break
            collection.polygons.append(l)
        else:  # exited normally
            collections.append(collection)
    return collections


def crosses(self, target):
    cords: List[Chord] = self.cords()

    return any([target.crosses(reference) for reference in cords])


