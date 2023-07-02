from copy import deepcopy
from typing import List, Callable
from manim.utils.color import Colors
from itertools import product, permutations

from manim_lamination_builder import (
    UnitPoint,
    NaryFraction,
    LeafLamination,
    Chord,
    custom_dump,
    custom_parse,
    parse_lamination,
)


def sibling_collections_of_leaf_in_existing(
    leaf: Chord, existing: LeafLamination
) -> List[LeafLamination]:
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
            if collection.crosses(l):
                break
            collection.leafs.append(l)
        else:  # exited normally
            collections.append(collection)
    return collections
