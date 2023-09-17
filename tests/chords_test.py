from manim_lamination_builder import Chord, NaryFraction

def test_chords():
    a, b, c, d = tuple(NaryFraction.from_string(4, "0_0").pre_images())

    assert Chord(a, c).crosses(Chord(b, d))
    assert not Chord(a, b).crosses(Chord(c, d))
    assert Chord(b, d).crosses(Chord(a, c))
    assert not Chord(c, d).crosses(Chord(a, b))
    assert NaryFraction.from_string(4, "0_0") == NaryFraction.from_string(4, "0_0")
    assert Chord(NaryFraction.from_string(4, "0_0"), b) in [
        Chord(NaryFraction.from_string(4, "0_0"), b)
    ]
