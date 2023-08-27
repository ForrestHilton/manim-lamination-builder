from manim_lamination_builder import Main, rabbit_nth_pullback
from manim import config

if __name__ == "__main__":
    config.preview = True
    Main([rabbit_nth_pullback(4)]).render()
