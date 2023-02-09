This is a re-implementation of lamination-builder that runs in python without dependencies on a browser and focusing on convenient generation of figures. Instead it uses Manim, and which has several dependencies. 

The input format is as follows: A list of laminations to be placed in the figure (tilling is a best effort left to righ and top to bottom Placemen based on a 16:9 screen). The blank lamination is permited.

Each lamination may have of the following fields: polygons, chords (must be a list of lists of length two), point_lables, point_colors ("*" for default color which defaults to red), and points. Omissions in each field will be filled based on the fields that proceed it in the list above. 

[
  {
    "polygons":[["_001","_010","_100"]],
    "chords":[["_100","2"]],
    "point_lables": {"_001": "starting point", "_010": "maps to _100"},
    "point_colors": {"*": "blue", "_001":}
    "points": ["1","2","_3"]
  },
  {}
]

Feature requests will be entertained. I have yet to see a need for any of the following featurs: maping foward, pull backs, automatically placing descriptions or tittles at the top.
