from copy import deepcopy
from typing import Dict, Iterator, List
from itertools import permutations
from manim_lamination_builder.lamination import LeafLamination
from manim_lamination_builder.chord import Chord


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
