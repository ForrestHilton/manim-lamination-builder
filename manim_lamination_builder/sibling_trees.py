import networkx as nx
from manim import BLACK, Graph, Mobject
from copy import deepcopy

from typing import List
from manim_lamination_builder import (
    Angle,
    GapLamination,
    HalfOpenArc,
    OccludedLamination,
)


def first_polygon(lam: GapLamination) -> List[Angle]:
    "select first polygon CCW"
    sorted_points = sorted(lam.points, key=lambda x: x.to_float())
    for p in sorted_points:
        polygon = next(filter(lambda lst: p in lst, lam.polygons), None)
        if polygon is not None:
            return polygon
    assert False, "There were no plygons and you asked for the first of them."


def make_regions(lam: OccludedLamination) -> List[OccludedLamination]:
    "seperate the lamination into regions based on the first polygon"
    # use it partition into n pieces in CCW order
    assert lam.lam is GapLamination
    polygon = first_polygon(lam.lam)

    regions = []
    n = len(polygon)
    sorted_polygon = sorted(polygon, key=lambda x: x.to_float())
    sorted_polygon.append(lam.occlusion.a if lam.occlusion else sorted_polygon[0])
    for i in range(n):
        chord = HalfOpenArc(sorted_polygon[i + 1], sorted_polygon[i], None)
        regions.append(OccludedLamination(lam.lam, chord))
    return regions


def construct_nested_tuple(lam: GapLamination):
    if len(lam.polygons) == 0:
        return ()

    return tuple(
        reversed([
            construct_nested_tuple(lam)
            for lam in make_regions(OccludedLamination(lam, None))
        ])
    )


# make copy first
def construct_tree(lam: GapLamination) -> Mobject:
    tuples = construct_nested_tuple(lam)
    G = nx.from_nested_tuple(tuples)
    return Graph(
        list(G.nodes),
        list(G.edges),
        layout="tree",
        root_vertex=0,
        vertex_config={"fill_color": BLACK},
        edge_config={"stroke_color": BLACK},
    )
