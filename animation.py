from manim import WHITE, Animation, Scene, tempconfig, Arc, Dot, RED, VMobject, Mobject
from chord import Chord, make_and_append_bezier
from custom_json import custom_dump, custom_parse
from lamination import Lamination
from points import FloatWrapper, NaryFraction, angle_to_cartesian


def lerp(a: float, b: float, alpha: float) -> float:
    "Linearly interpolate between two floats a and b using time value alpha."
    return (1 - alpha) * a + alpha * b


class AnimateLamination(Animation):
    def __init__(
        self,
        initial: Lamination,
        final: Lamination,
        start_mobject: Mobject = None,
        **kwargs,
    ) -> None:
        super().__init__(start_mobject or initial.build(), **kwargs)
        self.initial = initial
        self.final = final
        # TODO: check if laminations are compatible in terms of same length of properys

    def interpolate(self, alpha: float) -> None:
        # lamination_radius = 1
        count_arcs = 0
        count_polygons = 0
        for i, submobject in enumerate(self.mobject.submobjects):
            if isinstance(submobject, Dot):
                # Set the position of the Dot based on its position in the list of submobjects
                index_in_list_of_points = i - count_polygons - count_arcs
                point_initial = self.initial.points[index_in_list_of_points]
                point_final = self.final.points[index_in_list_of_points]
                submobject.move_arc_center_to(
                    angle_to_cartesian(
                        lerp(point_initial.to_angle(), point_final.to_angle(), alpha)
                    )
                )
            elif isinstance(submobject, Arc):
                count_arcs += 1
                continue
            else:
                assert isinstance(submobject, VMobject)
                # Set the position of all the points for the submobject based on its position in the list of submobjects
                count_polygons += 1
                index_in_list_of_vmobjects = i - count_arcs
                if index_in_list_of_vmobjects < len(self.initial.polygons):
                    polygon_initial = self.initial.polygons[index_in_list_of_vmobjects]
                    polygon_final = self.final.polygons[index_in_list_of_vmobjects]

                    submobject.reset_points()
                    for i in range(len(polygon_final)):
                        a = lerp(
                            polygon_initial[i].to_float(),
                            polygon_final[i].to_float(),
                            alpha,
                        )
                        b = lerp(
                            polygon_initial[(i + 1) % len(polygon_final)].to_float(),
                            polygon_final[(i + 1) % len(polygon_final)].to_float(),
                            alpha,
                        )
                        make_and_append_bezier(
                            submobject, FloatWrapper(a), FloatWrapper(b)
                        )
                else:  # occlusion
                    occlusion_initial = self.initial.occlusion
                    assert occlusion_initial is not None
                    # TODO: be more clever about wrap around
                    midpoint = (
                        occlusion_initial[0].to_float()
                        + occlusion_initial[1].to_float()
                    ) / 2
                    a = lerp(occlusion_initial[0].to_float(), midpoint, alpha)
                    b = lerp(occlusion_initial[1].to_float(), midpoint, alpha)
                    submobject.reset_points()
                    make_and_append_bezier(submobject, FloatWrapper(a), FloatWrapper(b))


class MyScene(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        initial = custom_parse(
            """
 {
    "polygons": [["_300","_003", "_030"]],
    occlusion: ["1","2"],
    "radix": 4
  }
                     """
        )

        final = custom_parse(
            """
 {
    "polygons": [["_003","_030", "_300"]],
    "radix": 4
  }
                     """
        )
        initial.auto_populate()
        final.auto_populate()
        # initial.polygons.pop(0)
        # final.polygons.pop(0)
        print(custom_dump(initial))
        print(custom_dump(final))
        self.play(AnimateLamination(initial, final, run_time=5))


if __name__ == "__main__":
    with tempconfig({"quality": "medium_quality", "preview": True}):
        scene = MyScene()
        scene.render()
