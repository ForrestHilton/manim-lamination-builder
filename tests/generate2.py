from manim_lamination_builder import (
    sibling_collections_of_leaf_in_existing,
    parse_lamination,
    custom_parse,
    custom_dump
)

lam = parse_lamination("""{polygons:[['_100','_010','_001']],radix:2}""")

leavs = lam.to_leafs()
print(custom_dump(leavs))
print(custom_dump(sibling_collections_of_leaf_in_existing(leavs.leafs[0], leavs)))
