from copy import deepcopy
from typing import Dict, List, Callable, Set
from manim.animation.animation import config
from manim.utils.color import Colors
from itertools import product, permutations
from manim import (
    DOWN,
    WHITE,
    Scene,
    Group,
)

from manim.utils.file_ops import config

from manim_lamination_builder.lamination import AbstractLamination

from manim_lamination_builder import (
    Main,
    LeafLamination,
    Chord,
    parse_lamination,
)


def next_pull_back(
    _lam: LeafLamination, included_images=LeafLamination.empty()
) -> List[LeafLamination]:
    existing_pre_images: Dict[Chord, List[Chord]] = {}
    for l in _lam.leafs:
        image = Chord(l.min.after_sigma().cleared(), l.max.after_sigma().cleared())
        if image in existing_pre_images.keys():
            existing_pre_images[image].append(l)
        else:
            existing_pre_images[image] = [l]

    def sibling_collections_of_leaf_in_existing(
        leaf: Chord, existing: LeafLamination
    ) -> List[LeafLamination]:
        collections = []
        pre_a = leaf.min.pre_images()
        pre_b = leaf.max.pre_images()

        required_pre_images = existing_pre_images.get(leaf,[])

        for indexes in permutations(range(len(pre_b))):
            requirements_fulfiled = 0
            collection = deepcopy(existing)
            for i, j in enumerate(indexes):
                l = Chord(pre_a[i], pre_b[j])
                if l in required_pre_images:
                    requirements_fulfiled += 1
                if collection.crosses(l):
                    break
                collection.leafs.add(l)
            else:  # exited normally
                if len(required_pre_images) == requirements_fulfiled:
                    collections.append(collection)
        return collections

    # TODO: auto create included_images
    ret = [deepcopy(_lam)]
    for l in list(_lam.leafs - included_images.leafs):
        new_ret = []
        for lam2 in ret:
            new_ret += sibling_collections_of_leaf_in_existing(l, lam2)
        ret = new_ret
    return ret


def render_expanded_3_3_minashery():
    start = parse_lamination(
        """{polygons:[['_100','_010','_001']],radix:3}"""
    ).to_leafs()

    result = list(map(lambda lam: lam.to_polygons(), next_pull_back(start)))
    config.preview = True
    Main(result).render()


class PullBackTree:
    node: LeafLamination
    children: List["PullBackTree"]

    def __init__(self, lam: LeafLamination, depth: int, parent=LeafLamination.empty()):
        self.node = lam
        if depth == 0:
            self.children = []
            return
        children = next_pull_back(lam, parent)
        self.children = list(
            map(lambda child: PullBackTree(child, depth - 1, lam), children)
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
        self.background_color = WHITE
        list_of_groups = []
        print(self.tree.flaten())
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
    start = parse_lamination(
        """{polygons:[['_100','_010','_001']],radix:2}"""
    ).to_leafs()
    tree = PullBackTree(start, 4)
    config.preview = True
    config.background_color = WHITE
    TreeRender(tree).render()
