import networkx as nx
from manim import BLACK, Graph, Mobject
from copy import deepcopy

from typing import List
from manim_lamination_builder import UnitPoint, Lamination
from manim_lamination_builder.morph import remove_occluded


def first_polygon(lam: Lamination) -> List[UnitPoint]:
    "select first polygon CCW"
    sorted_points = sorted(lam.points, key=lambda x: x.to_float())
    for p in sorted_points:
        polygon = next(filter(lambda lst: p in lst, lam.polygons), None)
        if polygon is not None:
            return polygon


def make_regions(lam: Lamination) -> List[Lamination]:
    "seperate the lamination into regions based on the first polygon"
    # use it partition into n pieces in CCW order
    polygon = first_polygon(lam)

    regions = []
    n = len(polygon)
    sorted_polygon = sorted(polygon, key=lambda x: x.to_float())
    sorted_polygon.append((lam.occlusion or sorted_polygon)[0])
    for i in range(n):
        chord = (sorted_polygon[i + 1], sorted_polygon[i])
        region = deepcopy(lam)
        lam.occlusion = chord
        regions.append(remove_occluded(region, chord))
    return regions


def construct_nested_tuple(lam: Lamination):
    if len(lam.polygons) == 0:
        return ()

    return tuple(reversed([construct_nested_tuple(lam) for lam in make_regions(lam)]))


# make copy first
def construct_tree(lam: Lamination) -> Mobject:
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
