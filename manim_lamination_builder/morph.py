from copy import deepcopy
from manim import ORIGIN, RED, TAU, Arc, Mobject, VMobject
from pydantic import BaseModel, field_validator
from manim_lamination_builder.chord import make_and_append_bezier
from manim_lamination_builder.constructions import sigma
from manim_lamination_builder.custom_json import custom_dump, custom_parse
from manim_lamination_builder.lamination import (
    AbstractLamination,
    AgnosticLamination,
    GapLamination,
)
from manim_lamination_builder.points import (
    Angle,
    LiftedAngle,
    FloatWrapper,
    Angle,
)
from typing import Union


class HalfOpenArc(BaseModel):
    """a is the beginning(left), and b is the end(right).
    This class represents the arc from a to the to b CCW
    If a is greater than b, then 0 is included.
    a and b should not be equal, and many kinds of degenerate intervals should not and can not
    be represented with this class.
    """

    a: Angle
    b: Angle
    left_is_closed: bool

    @field_validator("b")
    @classmethod
    def _check_values(cls, b, info):
        a = info.data["a"]
        assert b != a
        return b

    # TODO: make sure we are handling wrapping wright -- probably by asserting not carrying or by converting here

    def included(self, point: Angle):  # weather it is not occluded
        a, b = self.a.to_float(), self.b.to_float()
        if self.a == point:
            return self.left_is_closed
        if self.b == point:
            return not self.left_is_closed
        if b > a:
            return not (point.to_float() < a or point.to_float() > b)
        else:
            return point.to_float() < b or point.to_float() > a

    def excluded(self, point: Angle):
        return not self.included(point)

    def criticality(self) -> Union[bool, None, int]:
        "returns false if not critical, None if degree is not specified, and otherwise, the number of comicalities included"
        if not (self.a.has_degree() and self.b.has_degree()):
            return None

        if not self.a.after_sigma() == self.b.after_sigma():
            return False

        return int(
            self.b.lifted().after_sigma().to_float()
            - self.a.lifted().after_sigma().to_float()
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


class OccludedLamination(BaseModel):
    """Describes a lamination not of the unit disk, but of a part/region of the unit disk.
    In particular, the region is the complement of the region bounded by the circle arc
    stored in self.occlusion and the corresponding geodesic.
    Leafs may not have any end points along the boundary geodesic, and any laminational objects
     that do something of the sort will be removed at time of initialization.
    """

    occlusion: Union[HalfOpenArc, None]
    lam: AgnosticLamination

    @field_validator("lam")
    @classmethod
    def _filter(cls, lam, info):
        occlusion = info.data["occlusion"]
        return lam.filtered(occlusion.excluded) if occlusion else lam

    def result(self) -> AbstractLamination:
        if self.occlusion is None:
            return self.lam
        orriginal_degree = self.lam.degree
        lost_criticalitys = self.occlusion.criticality()
        remaining_degree = (
            orriginal_degree - lost_criticalitys
            if lost_criticalitys
            else orriginal_degree
        )

        def mapping(p: Angle) -> Angle:
            assert self.occlusion is not None
            return LiftedAngle(
                self.occlusion.morph_function(p.to_float()),
                remaining_degree,
                p.visual_settings,
            )

        ret = self.lam.apply_function(mapping)
        ret.degree = remaining_degree
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


def interpolate_quotent_of_region_of_rotational_polygon(lam: GapLamination):
    fixed = sigma(lam.polygons[0])
    start = min(fixed, key=lambda v: v.to_float())

    d = lam.degree
    critical_cord = HalfOpenArc(
        a=start,
        b=FloatWrapper(start.to_float() + 1 / d, d),
        left_is_closed=True,
    )

    for v in fixed:
        assert critical_cord.included(v)

    return OccludedLamination(lam=lam, occlusion=critical_cord).result()
