from itertools import accumulate
from typing import List, Set
from manim_lamination_builder import (
    parse_lamination,
    custom_dump,
    Lamination,
    UnitPoint,
)


def polygons_to_leafs(lam: Lamination) -> Lamination:
    leafs: List[List[UnitPoint]] = []
    for polygon in lam.polygons:
        for i in range(len(polygon)):
            leafs.append([polygon[i], polygon[(i + 1) % len(polygon)]])
    return Lamination(leafs, lam.points, lam.radix)


lam = parse_lamination(
    """
{
    "polygons": [["0_003", "0_030", "0_300"], 
      ["1_003", "3_030", "3_300"], 
      ["2_003", "2_030", "2_300"], 
      ["3_003", "1_030", "1_300"]], 
    "points": [], 
    "radix": 4
  }
"""
)


def leafs_to_polygons(lam: Lamination) -> Lamination:
    "assumes all polygons are leafs and identifies finite gaps"
    polygons: List[Set[UnitPoint]] = []
    for leaf in lam.polygons:
        used_leaf = False
        for p, other in [(leaf[0], leaf[1]), (leaf[1], leaf[0])]:
            for polygon in polygons:
                if p in polygon:
                    polygon_with_other = next(
                        filter(
                            lambda others_polygon: other in others_polygon
                            and polygon is not others_polygon,
                            polygons,
                        ),
                        None,
                    )
                    if polygon_with_other is None:
                        polygon.add(other)
                    else:
                        polygon.update(polygons.pop(polygons.index(polygon_with_other)))
                    used_leaf = True
                    break
            if used_leaf:
                break
        if not used_leaf:
            polygons.append(set(leaf))

    polygons_ = list(map(lambda s: sorted(s, key=lambda p: p.to_float()), polygons))
    return Lamination(polygons_, lam.points, lam.radix)


leafs = polygons_to_leafs(lam)
print(custom_dump(leafs))
polygons = leafs_to_polygons(leafs)
print(custom_dump(polygons))
