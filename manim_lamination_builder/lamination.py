# Licensed under the The AGPLv3 License (AGPLv3)
# Copyright (c) 2023 Forrest M. Hilton <forrestmhilton@gmail.com>
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from abc import ABC, abstractmethod
from collections.abc import Iterable
from itertools import accumulate
from typing import List, Set
from typing import List, Callable, Tuple, Union
from manim import (
    BLUE,
    ORIGIN,
    RED,
    BLACK,
    TAU,
    Arc,
    Dot,
    Mobject,
    VMobject,
    Circle,
)
from manim.utils.color import Colors, Color
from manim_lamination_builder.points import UnitPoint
from manim_lamination_builder.chord import make_and_append_bezier, Chord


background = BLACK


class AbstractLamination(ABC):
    points: List[UnitPoint]
    # occludes the region bounded by the chord and the arc from the first to the second CCW
    occlusion: Union[Tuple[UnitPoint, UnitPoint], None]
    radix: int
    colorizer: Callable[[UnitPoint], Colors]

    @abstractmethod
    def build(self) -> Mobject:
        pass


class Lamination(AbstractLamination):
    polygons: List[List[UnitPoint]]

    def __init__(
        self,
        polygons: List[List[UnitPoint]],
        points: List[UnitPoint],
        radix: int,
        colorizer=lambda p: Colors.red,
        occlusion: Union[Tuple[UnitPoint, UnitPoint], None] = None,
    ) -> None:
        self.polygons = polygons
        self.points = points
        self.radix = radix
        self.colorizer = colorizer
        self.occlusion = occlusion

    def auto_populate(self):
        for polygon in self.polygons:
            for point in polygon:
                if point not in self.points:
                    self.points.append(point)

    def build(self, radius=1.0, center=ORIGIN) -> Mobject:
        ret = Mobject()
        if self.occlusion is not None:
            delta = self.occlusion[0].to_angle() - self.occlusion[1].to_angle()
            if delta < 0:
                delta += TAU
            unit_circle = Arc(
                start_angle=self.occlusion[1].to_angle(),
                angle=delta,
                color=BLACK,
                radius=radius,
            )
        else:
            unit_circle = Circle(color=BLACK, radius=radius)  # create a circle
        unit_circle.move_arc_center_to(center)
        ret.add(unit_circle)  # show the circle on screen

        for polygon in self.polygons:
            shape = VMobject(BLUE, 1, color=BLACK)
            for i in range(len(polygon)):
                a = polygon[i]
                b = polygon[(i + 1) % len(polygon)]
                make_and_append_bezier(shape, a, b)
            ret.add(shape)

        for point in self.points:
            ret.add(
                Dot(
                    point.to_cartesian(), color=self.colorizer(point).value, radius=0.04
                )
            )

        # build a chord for occlusion

        if self.occlusion is not None:
            occlusion = VMobject(color=RED)
            make_and_append_bezier(occlusion, self.occlusion[0], self.occlusion[1])
            ret.add(occlusion)

        for submobject in ret.submobjects:
            if submobject is unit_circle:
                continue
            submobject.points *= radius
            submobject.points += center

        return ret

    def apply_function(self, f: Callable[[UnitPoint], UnitPoint]) -> "Lamination":
        new_polygons = []
        for poly in self.polygons:
            new_poly = [f(p) for p in poly]
            new_polygons.append(new_poly)
        new_points = [f(p) for p in self.points]
        return Lamination(new_polygons, new_points, self.radix, self.colorizer)

    def to_leafs(self) -> "LeafLamination":
        leafs: List[Chord] = []
        for polygon in self.polygons:
            for i in range(len(polygon)):
                leafs.append(Chord(polygon[i], polygon[(i + 1) % len(polygon)]))
        return LeafLamination(leafs, self.points, self.radix)


class LeafLamination(AbstractLamination):
    leafs: Set[Chord]

    def __init__(
        self,
        leafs: Iterable[Chord],
        points: List[UnitPoint],
        radix: int,
        colorizer=lambda p: Colors.red,
        occlusion: Union[Tuple[UnitPoint, UnitPoint], None] = None,
    ) -> None:
        self.leafs = set(leafs)
        self.points = points
        self.radix = radix
        self.colorizer = colorizer
        self.occlusion = occlusion

    def to_polygons(self) -> Lamination:
        "identifies finite gaps"
        polygons: List[Set[UnitPoint]] = []
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
        return Lamination(polygons_, self.points, self.radix)

    def crosses(self, target: Chord):
        return any([target.crosses(reference) for reference in self.leafs])

    def build(self) -> Mobject:
        return self.to_polygons().build()

    @staticmethod
    def empty() -> "LeafLamination":
        return LeafLamination([], [], 0)
