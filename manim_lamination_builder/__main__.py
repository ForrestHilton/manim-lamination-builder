from manim import WHITE


if __name__ == "__main__":
    from manim_lamination_builder import custom_dump, read_file_to_laminations, Main
    from manim import (
        tempconfig,
    )
    import sys
    import os

    file = sys.argv[-1]

    path = os.path.join(os.getcwd(), file)
    laminations = read_file_to_laminations(path)
    if sys.argv[-2] == "-p":
        for lamination in laminations:
            lamination.auto_populate()
    # TODO: command line args and white theme? 

    with tempconfig(
        {"quality": "medium_quality", "preview": True} # , "background_color": WHITE
    ):
        scene = Main(laminations)
        scene.render()
