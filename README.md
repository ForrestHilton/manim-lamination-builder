This is a re-implementation of lamination-builder that runs in python without dependencies on a browser. Instead it uses Manim, and which has several dependencies. 

The input format is as follows: a list of laminations to be placed in the figure (tiling is a best effort aproach based on a 16:9 screen). Each lamination may have of the following fields: polygons, chords, point_lables, and points. Omissions in each field will be filled based on the previous fields. The blank lamination is permited.

[
  {
    "polygons":[["_001","_010","_100"]],
    "chords":[[]]
    "point_lables": {"_001": "starting point", "_010": "maps to _100"},
    "points": ["1","2","_3"]
  },
  {}
]

Feature requests will be entertained. 
