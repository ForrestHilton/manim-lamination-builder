from manim_lamination_builder import NaryFraction
from manim_lamination_builder.orbits import goldbergOrbit

def test_deploymentSequence():

    assert goldbergOrbit([3],[1,3]).to_string() == "_001"
    assert goldbergOrbit([2,3],[1,3]).to_string() == "_002"
    assert goldbergOrbit([1,3],[1,3]).to_string() == "_012"
    
def test_rotationNumber():
    
    assert goldbergOrbit([2,3],[1,3]).to_string() == "_002"
    assert goldbergOrbit([2,3],[2,3]).to_string() == "_021"

def test_compositeRotationNumber():
    
    assert goldbergOrbit([2,4],[2,4]).to_string() == "_02"
    assert goldbergOrbit([4,4],[2,4]).to_string() == "_01"