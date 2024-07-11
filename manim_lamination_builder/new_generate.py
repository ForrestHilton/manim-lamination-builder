from copy import deepcopy
from typing import Dict, Iterator, List, Sequence
from itertools import combinations, combinations_with_replacement, permutations, product
from manim_lamination_builder.lamination import GapLamination, LeafLamination, Polygon
from manim_lamination_builder.chord import Chord
from manim_lamination_builder.points import PrincipalAngle


def valid_polygon_indices(degree, di, order):
    for indices in combinations_with_replacement(range(degree), di * order - 1):
        indices = (0,) + indices
        valid = True
        # check if any vertex is used twice
        for color in range(order):
            if len(set(indices[color::order])) != di:
                valid = False
                break
        # check that it doesn't jump back at end of cycle
        for edge in range(1, di):
            if indices[edge * order] == indices[edge * order - 1]:
                valid = False

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
    verticies = sorted(verticies, key=lambda lst: lst[0].to_float())
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

                new_child_options = []
                for a, b in product(
                    child_options,
                    sibling_portraits(subtended_arc),
                ):
                    new = GapLamination(a.polygons + b.polygons, [], lam_degree)
                    new_child_options.append(new)
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


def pre_image_dictionary(lam: GapLamination) -> Dict[Polygon, List[Polygon]]:
    "maps each cord to any preimages it might already have"

    from manim_lamination_builder.constructions import sigma

    ret = {}
    for poly in lam.polygons:
        image = sigma(poly)
        if image in ret.keys():
            ret[image].append(poly)
        else:
            ret[image] = [poly]
    return ret


def next_pull_back(lam: GapLamination, cumulative=False) -> List[GapLamination]:
    d = lam.degree
    existing_pre_images = pre_image_dictionary(lam)
    assert not cumulative
    # TODO: deal make non-cumulative
    if cumulative:
        ret = [deepcopy(lam)]
    else:
        ret = [GapLamination.empty(d)]
    for poly in list(lam.polygons):
        new_ret = []
        required_pre_images = existing_pre_images.get(poly, [])
        portraits = []
        if sum([len(p) for p in required_pre_images]) == d * len(poly):
            portraits = [
                GapLamination(polygons=required_pre_images, points=[], degree=d)
            ]
        else:
            verticies = [p.pre_images() for p in poly]
            portraits = sibling_portraits(verticies)
            portraits = filter(
                lambda port: all([req in port.polygons for req in required_pre_images]),
                portraits,
            )
        for portrait in portraits:
            for existing in ret:
                if portrait.coexists(existing):
                    new = GapLamination(
                        polygons=existing.polygons + portrait.polygons,
                        points=[],
                        degree=d,
                    )
                    new_ret.append(new)
        ret = new_ret
    return ret


if __name__ == "__main__":
    from manim_lamination_builder.custom_json import parse_lamination

    start = parse_lamination(
        """{polygons:[['_100','_010','_001'],['1_100','1_010','0_001']],degree:2}"""
    ).to_polygons()
    start = next_pull_back(start)[0]
