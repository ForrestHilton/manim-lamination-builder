from copy import deepcopy
from manim import WHITE, Scene, tempconfig, Mobject
from manim_lamination_builder.custom_json import custom_dump, custom_parse
from manim_lamination_builder.lamination import Lamination
from manim_lamination_builder.points import FloatWrapper, UnitPoint
from typing import Tuple, Union
from manim_lamination_builder.animation import AnimateLamination
from manim_lamination_builder.generate import curried_colorize_with_respect_to


def remove_occluded(
    lam: Lamination, occlusion: Tuple[UnitPoint, UnitPoint]
) -> Lamination:
    ret = deepcopy(lam)
    a, b = occlusion[0].to_float(), occlusion[1].to_float()

    def criteria(point):  # weather it is not occluded
        if b > a:
            return point.to_float() < a or point.to_float() >= b
        else:
            return not (point.to_float() < b or point.to_float() >= a)

    ret.occlusion = occlusion

    ret.points = list(filter(criteria, ret.points))
    ret.polygons = list(
        filter(lambda polly: all(criteria(point) for point in polly), ret.polygons)
    )
    return ret


def morph_function(x: float, occlusion: Tuple[UnitPoint, UnitPoint]) -> float:
    a, b = occlusion[0].to_float(), occlusion[1].to_float()
    if a > b:
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


def result(lam: Lamination) -> Lamination:
    assert lam.occlusion is not None
    remaining_degree = lam.radix
    if (
        lam.occlusion[0].has_degree()
        and lam.occlusion[1].has_degree()
        and lam.occlusion[0].after_sigma().cleared()
        == lam.occlusion[1].after_sigma().cleared()
    ):
        lost_criticalitys = int(
            lam.occlusion[1].after_sigma().to_float()
            - lam.occlusion[0].after_sigma().to_float()
        )
        remaining_degree = lam.radix - lost_criticalitys

    def mapping(p: UnitPoint) -> UnitPoint:
        assert lam.occlusion is not None
        return FloatWrapper(
            morph_function(p.to_float(), lam.occlusion), remaining_degree
        )

    ret = remove_occluded(lam, occlusion=lam.occlusion).apply_function(mapping)

    ret.occlusion = None
    ret.radix = remaining_degree
    ret.colorizer = curried_colorize_with_respect_to(ret.points)

    return ret


class MorphOcclusion(AnimateLamination):
    def __init__(
        self,
        initial: Lamination,
        occlusion: Tuple[UnitPoint, UnitPoint],
        start_mobject: Union[Mobject, None] = None,
        **kwargs,
    ) -> None:
        initial.occlusion = occlusion
        reported_initial = remove_occluded(initial, occlusion)
        reported_final = result(initial)
        super().__init__(reported_initial, reported_final, start_mobject, **kwargs)


class _MyScene(Scene):
    def construct(self):
        self.camera.background_color = WHITE

        initial = custom_parse(
            """{
        "polygons": [["0_003", "0_030", "0_300"],
          ["1_003", "3_030", "3_300"],
          ["2_003", "2_030", "2_300"],
          ["3_003", "1_030", "1_300"]],
        "chords": [],
        "points": [],
        "radix": 4}"""
        )
        assert isinstance(initial, Lamination)
        initial.auto_populate()
        occlusion = (initial.polygons[0][0], initial.polygons[0][2])
        self.add(initial.build())
        self.wait(2)
        self.clear()
        self.play(MorphOcclusion(initial, occlusion, run_time=5))
        self.wait(2)


if __name__ == "__main__":
    with tempconfig({"quality": "medium_quality", "preview": True}):
        scene = _MyScene()
        scene.render()
