from manim import WHITE

if __name__ == "__main__":
    import os
    import readline
    import sys

    from manim import tempconfig

    from manim_lamination_builder import (Main, custom_dump,
                                          read_file_to_laminations,
                                          str_to_laminations)

    file = sys.argv[-1]
    if file == "repl":
        conf = {"quality": "medium_quality", "preview": True}
        while True:
            # Read user input
            string = input(">>> ")

            # Exit on empty input
            # if string == "":
            #     break
            try:
                laminations = str_to_laminations(string)
            except:
                continue

            with tempconfig(conf):
                scene = Main([laminations])
                scene.render()

            conf = {"quality": "medium_quality"}

    path = os.path.join(os.getcwd(), file)
    laminations = read_file_to_laminations(path)
    if sys.argv[-2] == "-p":
        laminations = [
            lamination.to_polygons().auto_populated() for lamination in laminations
        ]
    # TODO: command line args and white theme?

    with tempconfig(
        {"quality": "medium_quality", "preview": True}  # , "background_color": WHITE
    ):
        scene = Main(laminations)
        scene.render()
