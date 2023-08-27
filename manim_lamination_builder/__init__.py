"""
This is a re-implementation of lamination-builder that runs in python without dependencies on a browser and focusing on animations and convenient generation of figures. Instead it uses Manim, which has several dependencies, which you are responsible for installing in accordance with Manim's installation instructions.
"""
from manim_lamination_builder.lamination import Lamination, LeafLamination
from manim_lamination_builder.custom_json import (
    custom_dump,
    custom_parse,
    read_file_to_laminations,
    parse_lamination,
)
from manim_lamination_builder.points import FloatWrapper, UnitPoint, NaryFraction, sigma
from manim_lamination_builder.animation import AnimateLamination
from manim_lamination_builder.chord import Chord
from manim_lamination_builder.generate import (
    generate_sibling_portraits,
    generate_unicritical_lamination,
    remove_non_original_pollygons,
)
from manim_lamination_builder.new_generate import (
    TreeRender,
    next_pull_back,
    PullBackTree,
)
from manim_lamination_builder.main import group, Main
import manim_lamination_builder.morph
import manim_lamination_builder.__main__
from manim_lamination_builder.visual_settings import VisualSettings, get_color
from manim_lamination_builder.sibling_trees import (
    first_polygon,
    make_regions,
    construct_nested_tuple,
    construct_tree,
)
from manim_lamination_builder.constructions import (
    double_orbit,
    uniquely_color,
    unicritical_polygon,
    add_points_preimages,
)
from manim_lamination_builder.pull_backs import CriticalTree, rabbit_nth_pullback
