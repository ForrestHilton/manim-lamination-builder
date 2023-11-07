# Copyright (c) 2023 Forrest M. Hilton <forrestmhilton@gmail.com>
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from abc import ABC, abstractmethod
from typing import Generic, List, Set, Callable, TypeVar, Union
from manim import (
    ORIGIN,
    BLACK,
    WHITE,
    Dot,
    Mobject,
    VMobject,
    Circle,
)
from pydantic import BaseModel
from manim_lamination_builder.points import Degree, Angle
from manim_lamination_builder.chord import make_and_append_bezier, Chord


background = BLACK


T = TypeVar("T", bound="AbstractLamination")
class AbstractLamination(ABC, Generic[T]):
    points: List[Angle]
    radix: Degree
    dark_theme: bool

    @abstractmethod
    def build(self, radius=1.0, center=ORIGIN) -> Mobject:
        pass

    def edge_color(self):
        return WHITE if self.dark_theme else BLACK

    @abstractmethod
    def apply_function(self, f: Callable[[Angle], Angle]) -> T:
        pass

    @abstractmethod
    def filtered(self, f: Callable[[Angle], bool]) -> T:
        pass

    def convert_to_carrying(self) -> T:
        return self.apply_function(lambda p: p.to_carrying())

    def to_polygons(self) -> "Lamination":
        return self # type: ignore

    def to_leafs(self) -> "LeafLamination":
        return self # type: ignore


class Lamination(AbstractLamination, BaseModel):
    points: List[Angle]
    radix: Degree
    dark_theme: bool = True
    polygons: List[List[Angle]]

    def auto_populate(self):
        for polygon in self.polygons:
            for point in polygon:
                if point not in self.points:
                    self.points.append(point)

    def build(self, radius=1.0, center=ORIGIN) -> Mobject:
        ret = Mobject()
        unit_circle = Circle(color=self.edge_color(), radius=radius, stroke_width=2)
        unit_circle.move_arc_center_to(center)
        ret.add(unit_circle)

        for polygon in self.polygons:
            visual = polygon[0].visual_settings
            stroke_color = visual.stroke_color.value
            if stroke_color == BLACK and self.dark_theme:
                stroke_color = WHITE
            shape = VMobject(
                visual.polygon_color.value,
                1,
                stroke_width=visual.stroke_width, # type: ignore
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
                    color=point.visual_settings.point_color.value,
                    radius=0.04,
                )
            )

        for submobject in ret.submobjects:
            if submobject is unit_circle:
                continue
            submobject.points *= radius
            submobject.points += center

        return ret

    def apply_function(self, f: Callable[[Angle], Angle]) -> "Lamination":
        new_polygons = []
        for poly in self.polygons:
            new_poly = [f(p) for p in poly]
            new_polygons.append(new_poly)
        new_points = [f(p) for p in self.points]
        return Lamination(polygons=new_polygons, points=new_points, radix=self.radix)

    def filtered(self, f: Callable[[Angle], bool]) -> "Lamination":
        new_polygons = []
        for poly in self.polygons:
            if all([f(p) for p in poly]):
                new_polygons.append(poly)
        new_points = list(filter(f, self.points))
        return Lamination(polygons=new_polygons, points=new_points, radix=self.radix)

    def to_leafs(self) -> "LeafLamination":
        leafs: List[Chord] = []
        for polygon in self.polygons:
            for i in range(len(polygon)):
                leafs.append(Chord(polygon[i], polygon[(i + 1) % len(polygon)]))
        return LeafLamination(leafs=set(leafs), points=self.points, radix=self.radix)


class LeafLamination(AbstractLamination, BaseModel):
    points: List[Angle]
    radix: Degree
    dark_theme: bool = True
    leafs: Set[Chord]

    def to_polygons(self) -> Lamination:
        "identifies finite gaps"
        polygons: List[Set[Angle]] = []
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

        polygons_ = list(map(lambda s: sorted(s, key=lambda p: p.to_float()), polygons))
        return Lamination(polygons=polygons_, points=self.points, radix=self.radix)

    def crosses(self, target: Chord):
        return any([target.crosses(reference) for reference in self.leafs])

    def build(self) -> Mobject:
        return self.to_polygons().build()

    @staticmethod
    def empty(d) -> "LeafLamination":
        return LeafLamination(leafs=set(), points=[], radix=d)

    def apply_function(self, f: Callable[[Angle], Angle]) -> "LeafLamination":
        new_leaves = []
        for leaf in self.leafs:
            new_leaf = Chord(f(leaf.min), f(leaf.max))
            new_leaves.append(new_leaf)
        new_points = [f(p) for p in self.points]
        return LeafLamination(
            leafs=set(new_leaves), points=new_points, radix=self.radix
        )

    def filtered(self, f: Callable[[Angle], bool]) -> "LeafLamination":
        new_leaves = []
        for leaf in self.leafs:
            if f(leaf.min) and f(leaf.max):
                new_leaves.append(leaf)
        new_points = list(filter(f, self.points))
        return LeafLamination(
            leafs=set(new_leaves), points=new_points, radix=self.radix
        )

AgnosticLamination = Union[LeafLamination, Lamination]
