"""
some invalid states are representable such as misalignment of the end points
or if the end point is outside where the region where it may be placed.
Otherwise, this works with just one end point of each critical cord and
wether that end point is the one to included with the inside. It infers
how far away the next end point should be by how many critical cords are inside
it. Moreover, it does so in a degree aware way. (It gets the degree from
the point's degree).
"""

from typing import Callable, List, Optional

from pydantic import BaseModel, field_validator, model_validator
from manim_lamination_builder.custom_json import custom_dump
from manim_lamination_builder.points import Angle, FloatWrapper, NaryFraction
from manim_lamination_builder.constructions import unicritical_polygon
from manim_lamination_builder.lamination import (
    AbstractLamination,
    GapLamination,
    LeafLamination,
)


class CriticalTree(BaseModel):
    first_ccw_end_point: Angle  # TODO : non-lifted angle
    first_end_point_on_inside: bool
    inside: Optional["CriticalTree"] = None
    outside: Optional["CriticalTree"] = None

    @field_validator("first_ccw_end_point")
    @classmethod
    def _filter(cls, first_ccw_end_point):
        assert first_ccw_end_point.to_float() <= 0.5
        return first_ccw_end_point

    @staticmethod
    def default():
        "the one provided for the rabbit in lamination builder"
        return CriticalTree(
            first_ccw_end_point=NaryFraction.from_string(2, "_001"),
            first_end_point_on_inside=True,
        )

    def actual_degree(self):
        degree = self.first_ccw_end_point.degree
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
            self.recursive_degree() / degree + self.first_ccw_end_point.to_float(),
            degree,
        )

    def is_inside(self, a: Angle) -> bool:
        if self.first_end_point_on_inside:
            return (
                self.first_ccw_end_point.to_float() <= a.to_float()
                and a.to_float() < self.opposite_end().to_float()
            )
        else:
            return (
                self.first_ccw_end_point.to_float() < a.to_float()
                and a.to_float() <= self.opposite_end().to_float()
            )

    def depth_first_traversal(self) -> List["CriticalTree"]:
        ret: List["CriticalTree"] = [self]
        if self.inside is not None:
            ret.append(self.inside)
        if self.outside is not None:
            ret.append(self.outside)
        return ret

    def is_in_top_branch(self, a: Angle):
        # return self.is_inside(a) and not self.inside.is_inside(a)
        if not self.is_inside(a):
            return False
        if self.inside is not None and self.inside.is_inside(a):
            return False
        return True

    def all_branches_identifyers(self) -> List[Callable[[Angle], bool]]:
        assert self.actual_degree() == self.recursive_degree() + 1
        alternat_branches = list(
            map(lambda tree: tree.is_in_top_branch, self.depth_first_traversal())
        )
        return alternat_branches + [lambda x: not self.is_inside(x)]

    def all_branches(self) -> List[Callable[[Angle], Angle]]:
        def create_branch(identifyer):
            def branch(x):
                return next(filter(identifyer, x.pre_images()))

            return branch

        identifyers = self.all_branches_identifyers()
        return [create_branch(identifyer) for identifyer in identifyers]

    def pull_back1(
        self, lam: AbstractLamination, cumulative=False
    ) -> AbstractLamination:
        branches = self.all_branches()

        polygons = []
        leafs = []
        points = []
        if cumulative:
            points = lam.points
        if isinstance(lam, GapLamination):
            for f in branches:
                if cumulative:
                    polygons = lam.polygons
                polygons += lam.apply_function(f).polygons
                points += lam.apply_function(f).points
            return GapLamination(polygons=polygons, points=points, degree=lam.degree)
        else:
            assert isinstance(lam, LeafLamination)
            for f in branches:
                if cumulative:
                    leafs += lam.leafs
                leafs += lam.apply_function(f).leafs
                points += lam.apply_function(f).points
            return LeafLamination(leafs=set(leafs), points=points, degree=lam.degree)

    def pull_back_n(
        self, lam: AbstractLamination, n, cumulative=False
    ) -> AbstractLamination:
        ret = lam
        for _ in range(n):
            ret = self.pull_back1(ret, cumulative)
        return ret

    # def FDL_child(self, lam: FDL) -> FDL:
    #     def in_image(a: Angle) -> bool:
    #         assert isinstance(a, NaryFraction):
    #             a.pre_period()

    #     stuff = lam.lam.filtered()


def rabbit_nth_pullback(n) -> GapLamination:
    rabbit_seed = GapLamination(
        polygons=[unicritical_polygon(2, 3)], points=[], degree=2
    )
    rabbit_cord = CriticalTree.default()
    return rabbit_cord.pull_back_n(rabbit_seed, n)  # type: ignore


class FDL(BaseModel):
    """A lamination conforming to the definition of FDL paired with its depth"""

    # TODO : abundance of validators
    @model_validator(mode="before")
    @classmethod
    def _simplify(cls, v: dict) -> dict:
        n = v["n"]
        lam = v["lam"]
        assert n == max(
            [poly[0].pre_period() for poly in lam.polygons]
        ), "incorect depth"

        return v

    lam: GapLamination
    n: int

    @staticmethod
    def rabbit_root() -> "FDL":
        return FDL(lam=rabbit_nth_pullback(0), n=0)

    def pulled_back1(self, critical: CriticalTree) -> "FDL":
        polygons = []
        points = []
        if self.n > 0:
            polygons = self.lam.polygons
            points = self.lam.points

        branches = critical.all_branches()

        def preperiod_predicate(a: Angle):
            assert isinstance(a, NaryFraction)
            return a.pre_period() >= self.n

        recent = self.lam.filtered(preperiod_predicate)
        for f in branches:
            polygons += recent.apply_function(f).polygons
            points += recent.apply_function(f).points
        return FDL(
            lam=GapLamination(polygons=polygons, points=points, degree=self.lam.degree),
            n=self.n + 1,
        )

    def pulled_back_n(self, critical: CriticalTree, n: int) -> "FDL":
        ret = self
        for _ in range(n):
            ret = ret.pulled_back1(critical)
        return ret
