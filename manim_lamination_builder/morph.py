from copy import deepcopy
from manim import ORIGIN, RED, TAU, WHITE, Arc, Scene, tempconfig, Mobject, VMobject
from manim_lamination_builder.chord import make_and_append_bezier
from manim_lamination_builder.custom_json import custom_dump, custom_parse
from manim_lamination_builder.lamination import AbstractLamination, Lamination
from manim_lamination_builder.points import CarryingFloatWrapper, FloatWrapper, UnitPoint
from typing import Tuple, Union


class HalfOpenArc:
    def __init__(self, a: UnitPoint, b: UnitPoint, left_is_closed: bool):
        """a is the beginning(left), and b is the end(right).
        This class represents the arc from a to the to b CCW
        If a is greater than b, then 0 is included.
        a and b should not be equal, and many kinds of degenerate intervals should not and can not
        be represented with this class.


        """

        # TODO: make sure we are handling wrapping wright -- probably by asserting not carrying or by converting here
        assert a != b
        self.a = a
        self.b = b
        self.left_is_closed = left_is_closed

    def included(self, point: UnitPoint):  # weather it is not occluded
        a, b = self.a.to_float(), self.b.to_float()
        if self.a == point:
            return self.left_is_closed
        if self.b == point:
            return not self.left_is_closed
        if b > a:
            return not (point.to_float() < a or point.to_float() > b)
        else:
            return point.to_float() < b or point.to_float() > a

    def excluded(self, point: UnitPoint):
        return not self.included(point)

    def criticality(self) -> Union[bool, None, int]:
        "returns false if not critical, None if degree is not specified, and otherwise, the number of comicalities included"
        if not (self.a.has_degree() and self.b.has_degree()):
            return None

        if not self.a.after_sigma() == self.b.after_sigma():
            return False

        return int(
            self.b.to_carrying().after_sigma().to_float()
            - self.a.to_carrying().after_sigma().to_float()
        )

    def length_rotations(self) -> float:
        a, b = self.a.to_float(), self.b.to_float()
        if a > b:
            b += 1
        return b - a

    def morph_function(self, x: float) -> float:
        """forms a well behaved function mapping the complement of self to the circle, but with
        good handling for animating smoothly without weird wrapping,
        """
        a, b = self.a.to_float(), self.b.to_float()
        if a > b:  # TODO: what??!!
            a, b = b, a
        bite_length = b - a
        remaining_length = 1 - bite_length
        # Calculate the midpoint of the range
        midpoint = (a + b) / 2
        # Calculate the opposite of the midpoint
        opposite = midpoint + 0.5 if midpoint < 0.5 else midpoint - 0.5

        # Determine which side of the midpoint the angle is on
        if x >= a and x <= b:
            # The angle is in the range, so map it to the midpoint
            return midpoint
        elif x < a:
            # The angle is below the range, so stretch the lower half of the circle
            return ((x - a) / remaining_length) + midpoint
        else:
            # The angle is above the range, so stretch the upper half of the circle
            return ((x - b) / remaining_length) + midpoint


class OccludedLamination:
    """Describes a lamination not of the unit disk, but of a part/region of the unit disk.
    In particular, the region is the complement of the region bounded by the circle arc
    stored in self.occlusion and the corresponding geodesic.
    Leafs may not have any end points along the boundary geodesic, and any laminational objects
     that do something of the sort will be removed at time of initialization.
    """

    def __init__(self, lam: AbstractLamination, occlusion: Union[HalfOpenArc, None]):
        "filters at time of initialization"
        self.lam = lam.filtered(occlusion.excluded) if occlusion else lam
        self.occlusion = occlusion

    def result(self) -> AbstractLamination:
        if self.occlusion is None:
            return self.lam
        orriginal_degree = self.lam.radix
        lost_criticalitys = self.occlusion.criticality()
        remaining_degree = (
            orriginal_degree - lost_criticalitys
            if lost_criticalitys
            else orriginal_degree
        )

        def mapping(p: UnitPoint) -> UnitPoint:
            assert self.occlusion is not None
            return CarryingFloatWrapper(
                self.occlusion.morph_function(p.to_float()),
                remaining_degree,
                p.visual_settings,
            )

        ret = self.lam.apply_function(mapping)
        ret.radix = remaining_degree
        return ret

    def build(self, radius=1.0, center=ORIGIN) -> Mobject:
        ret = self.lam.build(radius, center)
        if self.occlusion is None:
            return ret
        ret.submobjects.pop(0)
        delta = TAU * (1 - self.occlusion.length_rotations())
        unit_circle = Arc(
            start_angle=self.occlusion.b.to_angle(),
            angle=delta,
            color=self.lam.edge_color(),
            radius=radius,
        )
        ret.submobjects.insert(0, unit_circle)
        self.occlusion

        occlusion = VMobject(color=RED)
        make_and_append_bezier(occlusion, self.occlusion.a, self.occlusion.b)
        ret.add(occlusion)
        return ret

# TODO: data handling for this in custom_json

def interpolate_quotent_of_region_under_the_first_listed_polygon(lam: Lamination):
    d = lam.radix
    critical_cord = HalfOpenArc(
        lam.polygons[0][0],
        FloatWrapper(lam.polygons[0][0].to_float() + 1 / d, d),  # TODO: change this
        True,
    )
    return OccludedLamination(lam, critical_cord).result()
