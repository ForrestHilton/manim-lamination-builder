from copy import deepcopy
from typing import Dict, Iterable, Iterator, List, Callable, Sequence, Set
from manim.animation.animation import config
from itertools import product, permutations
from manim import (
    DOWN,
    WHITE,
    Scene,
    Group,
)

from manim.utils.file_ops import config
from manim_lamination_builder.custom_json import custom_parse

from manim_lamination_builder.lamination import AbstractLamination

from manim_lamination_builder import (
    LeafLamination,
    Chord,
    parse_lamination,
)

from manim_lamination_builder import custom_dump
from manim_lamination_builder.main import Main
from manim_lamination_builder.points import NaryFraction


def _sibling_collections_of_leaf(leaf) -> Iterator[List[Chord]]:
    """
    Returns an iterator over all of the ways of reconnecting the pre-image points into leaves.
    Implementation is clever, but might not be fast.
    """
    pre_a = leaf.min.pre_images()
    pre_b = leaf.max.pre_images()

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


def next_pull_back(
    lam: LeafLamination, cumulative=False
) -> List[LeafLamination]:
    existing_pre_images = pre_image_dictionary(lam)
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


class PullBackTree:
    node: LeafLamination
    children: List["PullBackTree"]

    def __init__(self, lam: LeafLamination, depth: int):
        self.node = lam
        if depth == 0:
            self.children = []
            return
        children = next_pull_back(lam)
        self.children = list(
            map(lambda child: PullBackTree(child, depth - 1), children)
        )

    def flaten(self) -> List[List[LeafLamination]]:
        ret = [[self.node]]
        for child in self.children:
            for i, lam in enumerate(child.flaten()):
                if i + 1 >= len(ret):
                    ret.append(lam)
                else:
                    ret[i + 1] += lam
        return ret


class TreeRender(Scene):
    def __init__(self, tree: PullBackTree):
        self.tree = tree
        super().__init__()

    def construct(self):
        list_of_groups = []
        for row in self.tree.flaten():
            outer_group = Group(*[lamination.build() for lamination in row])
            outer_group.arrange()
            list_of_groups.append(outer_group)
        outer_group = Group(*list_of_groups)
        outer_group.arrange(DOWN)
        outer_group.scale(
            1
            / max(
                outer_group.width / config.frame_width + 0.01,
                outer_group.height / config.frame_height + 0.01,
            )
        )
        self.add(outer_group)


if __name__ == "__main__":
    config.preview = True

    # start = parse_lamination(
    #     """{polygons:[['_100','_010','_001']],degree:2}"""
    # ).to_leafs()
    # print(custom_dump(next_pull_back(start)[0]))

    start = parse_lamination(
        """
{"leafs": [["1_010", "1_100"], ["0_010", "0_100"], ["0_001", "1_010"], ["0_010", "1_001"], ["0_001", "1_100"], ["0_100", "1_001"]], "points": [], "degree": 2}
            """
    )
    # assert start is LeafLamination
    Main(next_pull_back(start)).render()
    #     res = custom_parse(
    #         """
    #                       [

    # {"leafs": [["01_100", "11_010"], ["01_010", "11_100"], ["0_010", "1_100"]], "points": [], "degree": 2}
    # ]
    # """
    #     )
    #     for lam in res:
    #         lam.leafs.update(start.leafs)

    existing = '[{"leafs": [["11_010", "11_100"], ["01_010", "01_100"]], "points": [], "degree": 2}, {"leafs": [["01_100", "11_010"], ["01_010", "11_100"]], "points": [], "degree": 2}]'

    # Main(custom_parse('[{"leafs": [["11_010", "11_100"], ["01_010", "01_100"]], "points": [], "degree": 2}, {"leafs": [["01_100", "11_010"], ["01_010", "11_100"]], "points": [], "degree": 2}]')).render()
