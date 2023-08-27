from manim import *
from manim_lamination_builder import custom_parse, Lamination
from manim_lamination_builder.morph import MorphOcclusion


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
