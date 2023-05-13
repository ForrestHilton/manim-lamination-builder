"""
This is a re-implementation of lamination-builder that runs in python without dependencies on a browser and focusing on convenient generation of figures. Instead it uses Manim, which has several dependencies, which you are responsible for installing in accordance with Manim's installation instructions.
"""
from manim_lamination_builder.lamination import Lamination
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
    curried_colorize_with_respect_to,
    generate_sibling_portraits,
    generate_unicritical_lamination,
    remove_non_original_pollygons,
)
from manim_lamination_builder.main import group, Main
