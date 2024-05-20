from typing import List
from manim import DOWN, Scene, Group, config
import networkx as nx

from pydantic import BaseModel

from manim_lamination_builder.lamination import LeafLamination
from manim_lamination_builder.new_generate import next_pull_back


class PullBackTree(BaseModel):
    node: LeafLamination
    children: List["PullBackTree"]

    @staticmethod
    def build(lam: LeafLamination, depth: int, lone_leaf=False) -> "PullBackTree":
        node = lam
        if depth == 0:
            children = []
            return PullBackTree(node=node, children=[])
        children = next_pull_back(lam)
        if (
            lone_leaf
        ):  # TODO: this is a hack to give sub hyperbolic laminations starting from lone leaves
            assert lam.degree == 2
            if len(children) == 2:
                leafs = children[0].leafs.union(children[1].leafs)
                children.append(
                    LeafLamination(points=[], degree=lam.degree, leafs=leafs)
                )
        children = list(
            map(lambda child: PullBackTree.build(child, depth - 1, lone_leaf), children)
        )
        return PullBackTree(node=node, children=children)

    def flatten(self) -> List[List[LeafLamination]]:
        ret = [[self.node]]
        for child in self.children:
            for i, lam in enumerate(child.flatten()):
                if i + 1 >= len(ret):
                    ret.append(lam)
                else:
                    ret[i + 1] += lam
        return ret

    def nx_tree(
        self, G=nx.DiGraph(), table=[], parent=None
    ) -> tuple[nx.DiGraph, List[LeafLamination]]:
        i = len(table)
        table.append(self.node)
        G.add_node(i)
        if parent is not None:
            G.add_edge(parent, i)

        for child in reversed(self.children):
            child.nx_tree(G, table, i)
        return (G, table)


class TreeRender(Scene):
    def __init__(self, tree: PullBackTree):
        self.tree = tree
        super().__init__()

    def construct(self):
        list_of_groups = []
        for row in self.tree.flatten():
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

    from manim_lamination_builder.custom_json import custom_parse, parse_lamination
    from manim_lamination_builder.main import Main

    config.preview = True
