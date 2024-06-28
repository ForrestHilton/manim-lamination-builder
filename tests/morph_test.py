from manim import *
from manim_lamination_builder import custom_parse, GapLamination
from manim_lamination_builder.animation import AnimateLamination
from manim_lamination_builder.custom_json import custom_dump
from manim_lamination_builder.morph import HalfOpenArc, OccludedLamination
from manim_lamination_builder.points import FloatWrapper, NaryFraction


def test_morph():
    initial = custom_parse(
        """{
    "polygons": [["0_003", "0_030", "0_300"],
      ["1_003", "3_030", "3_300"],
      ["2_003", "2_030", "2_300"],
      ["3_003", "1_030", "1_300"]],
    "chords": [],
    "points": [],
    "degree": 4}"""
    )
    assert isinstance(initial, GapLamination)
    occlusion = HalfOpenArc(
        a=initial.polygons[0][0], b=initial.polygons[0][2], left_is_closed=True
    )
    assert occlusion.included(NaryFraction.from_string(4, "0_030"))
    assert occlusion.excluded(FloatWrapper(0.7, 4))
    initial = initial.auto_populated()
    assert 3 == len(
        OccludedLamination(lam=initial, occlusion=occlusion).lam.to_polygons().polygons
    )
    assert occlusion.morph_function(NaryFraction.from_string(4, "3_300").to_float()) > 1
    assert (
        len(
            OccludedLamination(lam=initial, occlusion=occlusion)
            .result()
            .filtered(lambda p: p.to_float() > 1)
            .points
        )
        > 0
    )


class _MyScene(Scene):
    def construct(self):
        initial = custom_parse(
            """{
        "polygons": [["0_003", "0_030", "0_300"],
          ["1_003", "3_030", "3_300"],
          ["2_003", "2_030", "2_300"],
          ["3_003", "1_030", "1_300"]],
        "chords": [],
        "points": [],
        "degree": 4}"""
        )
        assert isinstance(initial, GapLamination)
        occlusion = HalfOpenArc(
            a=initial.polygons[0][0], b=initial.polygons[0][2], left_is_closed=True
        )
        initial = initial.auto_populated()
        initial = OccludedLamination(lam=initial, occlusion=occlusion)
        assert (
            occlusion.morph_function(NaryFraction.from_string(4, "3_300").to_float())
            > 1
        )
        self.add(initial.build())
        self.wait(2)
        self.clear()
        self.play(
            AnimateLamination(initial, initial.result().to_polygons(), run_time=5)
        )
        self.wait(2)


if __name__ == "__main__":
    with tempconfig({"quality": "medium_quality", "preview": True}):
        scene = _MyScene()
        scene.render()
