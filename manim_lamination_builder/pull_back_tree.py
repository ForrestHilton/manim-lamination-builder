from typing import List, cast
from manim import DOWN, LEFT, ORIGIN, RIGHT, UP, DiGraph, Scene, Group, Text, config, np
from manim.mobject.graph import LayoutFunction
import networkx as nx
from math import ceil, sqrt
from numpy import inf
from pydantic import BaseModel
from manim import Graph, tempconfig

from manim_lamination_builder.lamination import (
    AbstractLamination,
    LeafLamination,
    GapLamination,
)
from manim_lamination_builder.new_generate import next_pull_back


class PullBackTree(BaseModel):
    node: GapLamination
    children: List["PullBackTree"]

    @staticmethod
    def build(lam: AbstractLamination, depth: int) -> "PullBackTree":
        node = lam.to_polygons()
        if depth == 0:
            children = []
            return PullBackTree(node=node, children=[])
        children = next_pull_back(node)
        children = list(
            map(lambda child: PullBackTree.build(child, depth - 1), children)
        )
        return PullBackTree(node=node, children=children)

    def extend_by_one_level(self) -> "PullBackTree":
        if not self.children:
            new_children = next_pull_back(self.node)
            children = [PullBackTree(node=child, children=[]) for child in new_children]
        else:
            children = [child.extend_by_one_level() for child in self.children]

        return PullBackTree(node=self.node, children=children)

    def flatten(self) -> List[List[GapLamination]]:
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
    ) -> tuple[nx.DiGraph, List[GapLamination]]:
        i = len(table)
        table.append(self.node)
        G.add_node(i)
        if parent is not None:
            G.add_edge(parent, i)

        for child in reversed(self.children):
            child.nx_tree(G, table, i)
        return (G, table)

    def nx_generation_graph(self, n: int) -> tuple[nx.DiGraph, List[GapLamination]]:
        table: List[GapLamination] = []
        G = nx.DiGraph()
        for i, L in enumerate(self.flatten()[n]):
            G.add_node(i)
            table.append(L.to_polygons())

        for i, a in enumerate(table):
            for j, b in enumerate(table):
                if a.trapped_criticality() + 1 == b.trapped_criticality():
                    if a.finer(b):
                        G.add_edge(i, j)
        return (G, table)

    def show_generation_graph(
        self,
        n: int,
        sf=1,
        radius=2,
        show_numbers=False,
        trans=lambda x: x,
        permute=lambda x: x,
    ):
        (G, table) = self.nx_generation_graph(n)
        table = [table[permute(i)] for i in range(len(table))]
        pos = nx.layout.kamada_kawai_layout(G.to_undirected(), scale=8)
        # pos = map(lambda p: np.array([p[0], p[1], 0]), pos)
        center = ORIGIN
        pos = {
            v: trans((np.array([pos[v][0], pos[v][1], 0]) - center) * sf)
            for v in range(len(table))
        }
        if show_numbers:
            mobs = dict(enumerate([Text(str(i)) for i in range(len(table))]))
        else:
            mobs = dict(enumerate(map(lambda lam: lam.build(2), table)))
        graphMob = DiGraph(
            G.nodes,  # type:ignore
            G.edges,  # type:ignore
            # layout="kamada_kawai",
            layout=pos,
            vertex_mobjects=mobs,
            # layout_scale=1.5 * sqrt(len(table)),  # len(self.flatten()[-1]) * 2.4,
        )

        # print(list(nx.kamada_kawai_layout(G).values()))

        # graphMob.center()

        class CustomGraph(Scene):
            def construct(self):
                self.add(graphMob)

        top, bot, right, left = -inf, inf, -inf, inf
        for mob in graphMob.vertices.values():
            top, right = max(top, mob.get_top()[1]), max(right, mob.get_right()[0])
            bot, left = min(bot, mob.get_bottom()[1]), min(left, mob.get_left()[0])
        pix = 200
        buf = 0  # 0.05
        A = ceil(top - bot + 2 * buf)
        B = ceil(right - left + 2 * buf)
        # graphMob.shift((top + bot) * DOWN + (left + right) * RIGHT)

        with tempconfig(
            {
                # "preview": True,
                "pixel_height": A * pix,
                "pixel_width": B * pix,
                "frame_height": A,
                "frame_width": B,
                "disable_caching": True,
                # "top": (top + buf) * UP,
                # "left_size": left - buf,
            }
        ):
            CustomGraph().render()

    def show_pullback_tree(self):
        (G, table) = self.nx_tree()
        graphMob = Graph(
            G.nodes,  # type:ignore
            G.edges,  # type:ignore
            layout="tree",
            vertex_mobjects=dict(
                enumerate(map(lambda lam: lam.to_polygons().build(2), table))
            ),
            root_vertex=0,
            layout_scale=len(self.flatten()[-1]) * 2.4,
        )

        class CustomTree(Scene):
            def construct(self):
                self.add(graphMob)

        A = ceil(graphMob.height)
        B = ceil(graphMob.width)
        pix = 200
        with tempconfig(
            {
                # "preview": True,
                "pixel_height": A * pix,
                "pixel_width": B * pix,
                "frame_height": A,
                "frame_width": B,
                "disable_caching": True,
            }
        ):
            CustomTree().render()


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
    from manim_lamination_builder.custom_json import (
        custom_parse,
        parse_lamination,
        custom_dump,
    )
    from manim_lamination_builder.main import Main

    # config.preview = True
    start = parse_lamination(
        """{polygons:[['_100','_010','_001']],degree:3}"""
    ).to_leafs()
    tree = PullBackTree.build(start, 2)
    # print(len(tree.flaten()[-1]))
    # print(custom_dump([L.to_polygons() for L in tree.flatten()[-1]]))

    # tree.show_pullback_tree()
    tree.show_generation_graph(2)
