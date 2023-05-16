from manim_lamination_builder import custom_dump, read_file_to_laminations, Main
from manim import (
    tempconfig,
)
import sys
import os

file = sys.argv[-1]

path = os.path.join(os.getcwd(), file)
laminations = read_file_to_laminations(path)
for lamination in laminations:
    lamination.auto_populate()

with tempconfig({"quality": "medium_quality", "preview": True}):
    scene = Main(laminations)
    scene.render()
