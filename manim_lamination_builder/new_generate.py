from copy import deepcopy
from typing import List, Callable
from manim.animation.animation import config
from manim.utils.color import Colors
from itertools import product, permutations

from manim_lamination_builder import (
    Main,
    group,
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

    # TODO: precompute elsewhere
    existing_pre_images = {}
    for l in existing.leafs:
        existing_pre_images[Chord(l.min.after_sigma().cleared(), l.max.after_sigma().cleared())] = l
    required_pre_image = existing_pre_images[leaf]

    for indesies in permutations(range(len(pre_b))):
        met_goal = required_pre_image is None
        collection = deepcopy(existing)
        for i, j in enumerate(indesies):
            l = Chord(pre_a[i], pre_b[j])
            if l == required_pre_image:
                met_goal = True
            if collection.crosses(l):
                break
            collection.leafs.add(l)
        else:  # exited normally
            if met_goal:
                collections.append(collection)
    return collections


def next_pull_back(
    _lam: LeafLamination, included_images: LeafLamination
) -> List[LeafLamination]:
    # TODO: auto create included_images
    ret = [deepcopy(_lam)]
    for l in list(_lam.leafs - included_images.leafs):
        new_ret = []
        for lam in ret:
            new_ret += sibling_collections_of_leaf_in_existing(l, lam)
        ret = new_ret
    return ret


start = parse_lamination("""{polygons:[['_100','_010','_001']],radix:2}""").to_leafs()

result = list(
    map(lambda lam: lam.to_polygons(), next_pull_back(start, LeafLamination([], [], 2)))
)
config.preview = True
print(custom_dump(result))
Main(result).render()
