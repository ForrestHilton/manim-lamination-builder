# Copyright (c) 2023 Forrest M. Hilton <forrestmhilton@gmail.com>
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import bisect
from abc import ABC, abstractmethod
from itertools import combinations
from typing import Callable, Generic, List, Sequence, Set, TypeVar, Union

from manim import BLACK, ORIGIN, WHITE, Circle, Dot, Mobject, VMobject, config
from pydantic import BaseModel, field_validator

from manim_lamination_builder.chord import Chord, make_and_append_bezier
from manim_lamination_builder.points import Angle, Degree, sigma

background = BLACK


T = TypeVar("T", bound="AbstractLamination")


def dark_theme() -> bool:
    return config.background_color == BLACK


class AbstractLamination(ABC, Generic[T]):
    points: List[Angle]
    degree: Degree
    # dark_theme: bool

    def build(self, radius=1.0, center=ORIGIN) -> Mobject:
        return self.to_polygons().build(radius, center)

    def edge_color(self):
        return WHITE if dark_theme() else BLACK

    @abstractmethod
    def apply_function(self, f: Callable[[Angle], Angle]) -> T:
        pass

    @abstractmethod
    def filtered(self: T, f: Callable[[Angle], bool]) -> T:
        pass

    def lifted(self) -> T:
        return self.apply_function(lambda p: p.lifted())

    def to_polygons(self) -> "GapLamination":
        return self  # type: ignore

    def to_leafs(self) -> "LeafLamination":
        return self  # type: ignore

    def after_sigma(self: T) -> T:
        return self.apply_function(lambda x: x.after_sigma())


Polygon = tuple[
    Angle, ...
]  # TODO: add validator to test if this is in order as needed.


class GapLamination(BaseModel, AbstractLamination):
    points: List[Angle]
    degree: Degree
    # dark_theme: bool = True
    polygons: List[Polygon]

    @field_validator("polygons")
    @classmethod
    def _check_polygons_order(cls, polygons):
        sorted_polygons = []
        for polygon in polygons:
            if len(polygon) > 1:
                sorted_polygons.append(
                    tuple(sorted(polygon, key=lambda a: a.to_float()))
                )
        return sorted_polygons

    def __init__(  # TODO: check if I still need this / switch to tuple only.
        self,
        polygons: Sequence[
            Sequence[Angle]
        ],  # the only difrence with the auto gennerated code is here
        points: List[Angle],
        degree: Degree,
        # dark_theme: bool = True,
    ):
        super(GapLamination, self).__init__(
            polygons=polygons,
            points=points,
            degree=degree,  # , dark_theme=dark_theme
        )

    def auto_populated(self) -> "GapLamination":
        new_points = self.points.copy()
        for polygon in self.polygons:
            for point in polygon:
                if point not in self.points:
                    new_points.append(point)
        return GapLamination(
            polygons=self.polygons,  # type: ignore
            points=new_points,
            degree=self.degree,
            # dark_theme=self.dark_theme,
        )

    def build(self, radius=1.0, center=ORIGIN) -> Mobject:
        ret = Mobject()
        unit_circle = Circle(
            color=self.edge_color(),
            radius=radius,
            stroke_width=2,
            fill_color=BLACK if dark_theme() else WHITE,
            fill_opacity=1,
        )
        unit_circle.move_arc_center_to(center)
        ret.add(unit_circle)

        for polygon in self.polygons:
            visual = polygon[0].visual_settings
            stroke_color = visual.stroke_color
            if stroke_color == BLACK and dark_theme():
                stroke_color = WHITE
            shape = VMobject(
                visual.polygon_color,
                1,
                stroke_width=visual.stroke_width,  # type: ignore
                color=stroke_color,
            )
            for i in range(len(polygon)):
                a = polygon[i]
                b = polygon[(i + 1) % len(polygon)]
                make_and_append_bezier(shape, a, b)
            ret.add(shape)

        for point in self.points:
            ret.add(
                Dot(
                    point.to_cartesian(),
                    color=point.visual_settings.point_color,
                    radius=point.visual_settings.point_size,
                )
            )

        for submobject in ret.submobjects:
            if submobject is unit_circle:
                continue
            submobject.points *= radius
            submobject.points += center

        return ret

    def apply_function(self, f: Callable[[Angle], Angle]) -> "GapLamination":
        new_polygons = []
        for poly in self.polygons:
            new_poly = [f(p) for p in poly]
            new_polygons.append(new_poly)
        new_points = [f(p) for p in self.points]
        return GapLamination(
            polygons=new_polygons, points=new_points, degree=self.degree
        )

    def filtered(self, f: Callable[[Angle], bool]) -> "GapLamination":
        new_polygons = []
        for poly in self.polygons:
            if all([f(p) for p in poly]):
                new_polygons.append(poly)
        new_points = list(filter(f, self.points))
        return GapLamination(
            polygons=new_polygons, points=new_points, degree=self.degree
        )

    def to_leafs(self) -> "LeafLamination":
        leafs: List[Chord] = []
        for polygon in self.polygons:
            for i in range(len(polygon)):
                leafs.append(Chord(polygon[i], polygon[(i + 1) % len(polygon)]))
        return LeafLamination(leafs=set(leafs), points=self.points, degree=self.degree)

    def trapped_criticality(self) -> int:
        def degree(p: Polygon) -> int:
            return int(len(p) / len(set(sigma(p))))

        return sum([degree(p) - 1 for p in self.polygons])

    def finer(self, other: "GapLamination") -> bool:
        "return wether self is finer than other"
        for poly in self.polygons:
            parent = next(
                filter(lambda parent: poly[0] in parent, other.polygons), None
            )
            if parent is None:
                return False
            for theta in poly:
                if theta not in parent:
                    return False

        return True

    @staticmethod
    def empty(d) -> "GapLamination":
        return GapLamination(polygons=[], points=[], degree=d)

    @staticmethod
    def polygons_unlinked(a: Polygon, b: Polygon) -> bool:
        assert len(set(a).intersection(set(b))) == 0
        if a[-1].to_float() < b[0].to_float() or b[-1].to_float() < a[0].to_float():
            return True
        return (
            b[-1].to_float()
            < a[
                bisect.bisect_left(a, b[0].to_float(), key=lambda p: p.to_float())
            ].to_float()
            or a[-1].to_float()
            < b[
                bisect.bisect_left(b, a[0].to_float(), key=lambda p: p.to_float())
            ].to_float()
        )

    def unlinked(self) -> bool:
        for i, j in combinations(range(len(self.polygons)), 2):
            if not GapLamination.polygons_unlinked(
                list(self.polygons)[i], list(self.polygons)[j]
            ):
                return False
        return True

    def coexists(self, other: "GapLamination") -> bool:
        for i in range(len(self.polygons)):
            for j in range(len(other.polygons)):
                if not GapLamination.polygons_unlinked(
                    self.polygons[i], other.polygons[j]
                ):
                    return False
        return True

    def rational_lamination(self) -> List[List[str]]:
        return [[th.to_fraction() for th in eq] for eq in self.polygons]


class LeafLamination(BaseModel, AbstractLamination):
    points: List[Angle]
    degree: Degree
    # dark_theme: bool = True
    leafs: Set[Chord]
    as_q_lamination: bool = True

    def to_polygons(self) -> GapLamination:
        "identifies finite gaps unless it is meant to be a non-q-lamination"
        polygons: List[Set[Angle]] = []
        if not self.as_q_lamination:
            for leaf in self.leafs:
                polygons.append(set([leaf.min, leaf.max]))
        else:
            for leaf in self.leafs:
                used_leaf = False
                for p, other in [(leaf.min, leaf.max), (leaf.max, leaf.min)]:
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
                                polygon.update(
                                    polygons.pop(polygons.index(polygon_with_other))
                                )
                            used_leaf = True
                            break
                    if used_leaf:
                        break
                if not used_leaf:
                    polygons.append(set([leaf.min, leaf.max]))

        polygons_ = list(
            map(lambda s: tuple(sorted(s, key=lambda p: p.to_float())), polygons)
        )
        return GapLamination(
            polygons=polygons_,
            points=self.points,
            degree=self.degree,  # type:ignore
        )

    def crosses(self, target: Chord) -> bool:
        return any([target.crosses(reference) for reference in self.leafs])

    def unlinked(self) -> bool:
        for i, j in combinations(range(len(self.leafs)), 2):
            if list(self.leafs)[i].crosses(list(self.leafs)[j]):
                return False
        return True

    @staticmethod
    def empty(d) -> "LeafLamination":
        return LeafLamination(leafs=set(), points=[], degree=d)

    def apply_function(self, f: Callable[[Angle], Angle]) -> "LeafLamination":
        new_leaves = []
        for leaf in self.leafs:
            new_leaf = Chord(f(leaf.min), f(leaf.max))
            new_leaves.append(new_leaf)
        new_points = [f(p) for p in self.points]
        return LeafLamination(
            leafs=set(new_leaves), points=new_points, degree=self.degree
        )

    def filtered(self, f: Callable[[Angle], bool]) -> "LeafLamination":
        new_leaves = []
        for leaf in self.leafs:
            if f(leaf.min) and f(leaf.max):
                new_leaves.append(leaf)
        new_points = list(filter(f, self.points))
        return LeafLamination(
            leafs=set(new_leaves), points=new_points, degree=self.degree
        )

    def major(self) -> Chord:
        def length(leaf):
            ret = leaf.max.to_float() - leaf.min.to_float()
            if ret > 0.5:
                ret = 1 - ret
            return ret

        return max(self.leafs, key=length)

    def minor(self) -> Chord:
        M = self.major()
        return Chord(M.min.after_sigma(), M.max.after_sigma())


AgnosticLamination = Union[LeafLamination, GapLamination]
