# Licensed under the The AGPLv3 License (AGPLv3)
# Copyright (c) 2023 Forrest M. Hilton <forrestmhilton@gmail.com>
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


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
from manim_lamination_builder.chord import make_and_append_bezier


background = BLACK


class Lamination:
    polygons: List[List[UnitPoint]]
    points: List[UnitPoint]
    # occludes the region bounded by the chord and the arc from the first to the second CCW
    occlusion: Union[Tuple[UnitPoint, UnitPoint], None]
    radix: int
    colorizer: Callable[[UnitPoint], Colors]

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
        return Lamination(new_polygons, new_points, self.radix)
