from copy import deepcopy
from typing import Dict, Iterator, List, Sequence
from itertools import combinations, combinations_with_replacement, permutations, product
from manim_lamination_builder.lamination import GapLamination, LeafLamination
from manim_lamination_builder.chord import Chord
from manim_lamination_builder.points import PrincipalAngle


def valid_polygon_indices(degree, di, order):
    for indices in combinations_with_replacement(range(degree), di * order - 1):
        indices = (0,) + indices
        # check if polygon is valid
        valid = True
        for color in range(order):
            if len(set(indices[color::order])) != di:
                valid = False
                break
        if valid:
            yield indices


def sibling_portraits(
    verticies: Sequence[Sequence[PrincipalAngle]],
) -> List[GapLamination]:
    """
    Takes a list of verticies to be connected. It is a list of the preimages of the
    verticies of the original polygons. On both levels, we use positional order.

    This assumes that all the verticies are in the same round gap. If they are not,
    that can be filteded afterward.
    """
    ret = []
    order = len(verticies)
    degree = len(verticies[0])
    if degree == 0:
        return [GapLamination([], [], 2)]  # the 2 here will not be
    print(verticies)
    lam_degree = verticies[0][0].degree
    assert all([len(verticies[i]) == degree for i in range(len(verticies))])

    # this is for the polygon containing the vertex [0][0]
    # choose the degree of the polygon
    for di in range(1, degree + 1):
        # we have degree - di balls and di*order-1 bars
        for indices in valid_polygon_indices(degree, di, order):
            polygon: List[PrincipalAngle] = []
            child_options = [GapLamination([], [], verticies[0][0].degree)]
            lens = 0
            for i, j in enumerate(indices):
                color = i % order
                polygon.append(verticies[color][j])
                next = degree + 1 if i + 1 == order * di else indices[i + 1]
                if (i + 1) % order == 0:
                    next -= 1
                subtended_arc = [
                    verticies[color][j + 1 : next + 1] for color in range(0, color + 1)
                ] + [verticies[color][j:next] for color in range(color + 1, order)]

                lens += len(subtended_arc[0])
                assert di + len(subtended_arc[0]) <= degree

                if indices == (0, 1, 1, 2) and len(subtended_arc[0]) > 0:
                    assert (
                        0.3333333333333333 - subtended_arc[0][0].to_float()
                    ) ** 2 < 0.000001

                new_child_options = []
                for a, b in product(
                    child_options,
                    sibling_portraits(subtended_arc),
                ):
                    new_child_options.append(
                        GapLamination(a.polygons + b.polygons, [], lam_degree)
                    )
                child_options = new_child_options
            assert di + lens == degree
            for lam in child_options:
                lam.polygons.append(tuple(polygon))
                # assert set(sum(verticies, [])) == set(sum(lam.polygons, ()))
            ret += child_options

    return ret


def _sibling_collections_of_leaf(leaf) -> Iterator[List[Chord]]:
    """
    Returns an iterator over all of the ways of reconnecting the pre-image points into leaves.
    Implementation is clever, but might not be fast.
    """
    pre_a = leaf.min.pre_images()
    pre_b = leaf.max.pre_images()
    assert pre_a[0].visual_settings == leaf.min.visual_settings

    for indexes in permutations(range(len(pre_b))):
        ret = []
        for i, j in enumerate(indexes):
            l = Chord(pre_a[i], pre_b[j])
            if any([l2.crosses(l) for l2 in ret]):
                break
            ret.append(l)
        else:
            yield ret


def _sibling_collections_of_leaf_in_existing(
    leaf: Chord,
    existing: LeafLamination,
    required_pre_images: List[Chord],
    cumulative=False,
) -> List[LeafLamination]:
    """
    Considers one leaf at a time and considers all the ways to fit in exactly the right number of pre images.
    Takes into consideration a list of pre_images that is is required to have.
    """
    contextual_collections = []

    for collection in _sibling_collections_of_leaf(leaf):
        requirements_fulfiled = 0
        contextual_collection = deepcopy(existing)
        for l in collection:
            if contextual_collection.crosses(l):
                break
            if l in required_pre_images:
                requirements_fulfiled += 1
                if not cumulative:
                    contextual_collection.leafs.add(l)
                continue
            elif len(required_pre_images) == len(collection):
                break
            contextual_collection.leafs.add(l)
        else:  # exited normally
            if len(required_pre_images) == requirements_fulfiled:
                contextual_collections.append(contextual_collection)
    return contextual_collections


def pre_image_dictionary(lam: LeafLamination) -> Dict[Chord, List[Chord]]:
    "maps each cord to any preimages it might already have"
    ret = {}
    for l in lam.leafs:
        image = Chord(l.min.after_sigma(), l.max.after_sigma())
        if image in ret.keys():
            ret[image].append(l)
        else:
            ret[image] = [l]
    return ret


def next_pull_back(lam: LeafLamination, cumulative=False) -> List[LeafLamination]:
    existing_pre_images = pre_image_dictionary(lam)
    assert not cumulative
    # TODO: auto create included_images???
    # TODO: deal make non-cumulative
    if cumulative:
        ret = [deepcopy(lam)]
    else:
        ret = [LeafLamination.empty(lam.degree)]
    for l in list(lam.leafs):
        required_pre_images = existing_pre_images.get(l, [])
        new_ret = []
        for lam2 in ret:
            new_ret += _sibling_collections_of_leaf_in_existing(
                l, lam2, required_pre_images, cumulative
            )
        ret = new_ret
        if len(ret) == 0:
            return []
    return ret
