from manim_lamination_builder import (
    PullBackTree,
    parse_lamination,
)


for d in range(2, 7):
    start = parse_lamination(
        "{degree:" + str(d) + ', polygons:[["_001","_010","_100"]]}'
    ).to_leafs()
    depth = 6 - d
    print(d, depth, len(PullBackTree.build(start, depth).flatten()[-1]))

# time python -OO tree_benchmark.py
# 2 4 4
# 3 3 28
# 4 2 247
# 5 1 140
# 6 0 1
#
# real    0m30.973s
# user    0m33.439s
# sys     0m1.542s
# real    0m31.193s
# user    0m33.741s
# sys     0m1.469s

# 2 4 4
# 3 3 208
# 4 2 1060
# 5 1 140
# 6 0 1
#
# real    2m0.175s
# user    2m2.563s
# sys     0m1.508s

# 2 4 4
# 3 3 28
# 4 2 247
# 5 1 140
# 6 0 1
#
# real    0m39.653s
# user    0m42.247s
# sys     0m1.518s

# 2 4 4
# 3 3 28
# 4 2 247
# 5 1 140
# 6 0 1
#
# real    0m3.431s
# user    0m5.998s
# sys     0m1.346s
# 2 4 4
# 3 3 28
# 4 2 247
# 5 1 140
# 6 0 1
#
# real    0m5.328s
# user    0m7.942s
# sys     0m1.474s
