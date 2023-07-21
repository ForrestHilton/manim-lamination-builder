"""
some invalid states are representable such as misalignment of the end points
or if the end point is outside where the region where it may be placed.
Otherwise, this works with just one end point of each critical cord and 
wether that end point is the one to included with the inside. It infers 
how far away the next end point should be by how many critical cords are inside 
it. Moreover, it does so in a degree aware way.
"""
from typing import Callable, List, Tuple, Optional
from manim_lamination_builder.points import (
    FloatWrapper,
    NaryFraction,
    UnitPoint,
)
from manim_lamination_builder.generate import unicritical_polygon
from manim_lamination_builder.lamination import AbstractLamination


class CriticalTree:
    def __init__(
        self,
        first_ccw_end_point: UnitPoint,
        first_end_point_on_inside: bool,
        inside: Optional["CriticalTree"] = None,
        outside: Optional["CriticalTree"] = None,
    ):
        self.first_ccw_end_point = first_ccw_end_point.cleared()
        self.first_end_point_on_inside = first_end_point_on_inside
        self.inside = inside
        self.outside = outside

    @staticmethod
    def default():
        "the one provided for the rabbit in lamination builder"
        return CriticalTree(NaryFraction.from_string(2, "_001"), True)

    def actual_degree(self):
        degree = self.first_ccw_end_point.base
        assert degree is not None
        return degree

    def recursive_degree(self):
        "non-none vertices of tree"
        ret = 1
        if self.inside is not None:
            ret += self.inside.recursive_degree()
        if self.outside is not None:
            ret += self.outside.recursive_degree()
        return ret

    def opposite_end(self):
        degree = self.actual_degree()
        return FloatWrapper(
            self.recursive_degree() / degree + self.first_ccw_end_point.to_float()
        )

    def is_inside(self, a: UnitPoint) -> bool:
        if self.first_end_point_on_inside:
            return (
                self.first_ccw_end_point.to_float() <= a.to_float()
                and a.to_float() < self.opposite_end().to_float()
            )
        else:
            return (
                self.first_ccw_end_point.to_float() < a.to_float.to_float()
                and a.to_float.to_float() <= self.opposite_end().to_float()
            )

    def depth_first_traversal(self) -> List["CriticalTree"]:
        ret: List["CriticalTree"] = [self]
        if self.inside is not None:
            ret.append(self.inside)
        if self.outside is not None:
            ret.append(self.outside)
        return ret

    def is_in_top_branch(self, a: UnitPoint):
        # return self.is_inside(a) and not self.inside.is_inside(a)
        if not self.is_inside(a):
            return False
        if self.inside is not None and self.inside.is_inside(a):
            return False
        return True

    def all_branches_identifyers(self) -> List[Callable[[UnitPoint], bool]]:
        assert self.actual_degree() == self.recursive_degree() + 1
        alternat_branches = list(
            map(lambda tree: tree.is_in_top_branch, self.depth_first_traversal())
        )
        return alternat_branches + [lambda x: not self.is_inside(x)]

    def all_branches(self) -> List[Callable[[UnitPoint], UnitPoint]]:
        return [
            lambda x: next(filter(identifyer, x.pre_images()))
            for identifyer in self.all_branches_identifyers()
        ]


class PullBackScheme:
    seed: AbstractLamination
    branches: CriticalTree

    def __init__(self, seed, branches: CriticalTree):
        self.seed = seed
        self.branches = branches

    @staticmethod
    def default():
        "the one provided for the rabbit in lamination builder"
        return PullBackScheme(unicritical_polygon(2, 3), CriticalTree.default())


if __name__ == "__main__":
    example = CriticalTree.default()
    branches = example.all_branches()
    print(branches[0](FloatWrapper(0, 2)).to_float())
    print(branches[1](FloatWrapper(0, 2)).to_float())
    print(branches[0](FloatWrapper(0.4, 2)).to_float())
    print(branches[1](FloatWrapper(0.4, 2)).to_float())
