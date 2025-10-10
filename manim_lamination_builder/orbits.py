import numpy as np

from manim_lamination_builder.points import NaryFraction


# input list deployment sequence: depSeq
def getFixedPointSequence(depSeq):
    fixedPointSequence = []
    i = 0
    for n in depSeq:
        if i == 0:
            fixedPointSequence.append(n)
        else:
            fixedPointSequence.append(n - depSeq[i - 1])
        i = i + 1
    return fixedPointSequence


# input list fixed point sequence: fps
def getFixedPointExpansion(fps):
    fixedPointExpansion = []
    j = 0
    for n in fps:
        for i in range(n):
            fixedPointExpansion.append(j)
        j = j + 1
    return fixedPointExpansion


# input list fixed point expansion: fpe, list rotation number: rn
def getOrbitDigits(fpe, rn):
    orbitDigits = []
    adv = rn[1] - rn[0]
    for i in range(len(fpe)):
        if i < adv:
            orbitDigits.append(fpe[i])
        else:
            orbitDigits.append(fpe[i] + 1)
    return orbitDigits


# input list orbit digits: od, list rotation number: rn
def getDNaryExpansion(od, rn):
    assert rn[0] != 0 and rn[1] != 0, (
        "Rotation number should not have 0 as either number."
    )
    factor = np.gcd(rn[0], rn[1])
    step = rn[0]
    base = rn[1]
    dNaryExpansion = []
    dneTemp = []
    for k in range(factor):
        for n in range(int(base / factor)):
            dneTemp.append(od[((n * step) + k) % base])
        dNaryExpansion.append(dneTemp)
        dneTemp = []
    return dNaryExpansion[0]


def goldbergOrbit(deploymentSequence, rotationNumber):
    fps = getFixedPointSequence(deploymentSequence)
    fpe = getFixedPointExpansion(fps)
    od = getOrbitDigits(fpe, rotationNumber)
    de = getDNaryExpansion(od, rotationNumber)
    return NaryFraction([], de, len(deploymentSequence) + 1)




class Orbit:

    def __init__(self, point:NaryFraction):
        self._temporalOrbit, self._spacialOrbit = self._fullOrbits(point) 

        
#returns a full orbit in spacial order
    def _fullOrbits(self, point:NaryFraction):
        p = point
        fOrbit = []
        sOrbit = []
        tOrbit = []
        for i in range(len(point.repeating)):
            p = p.after_sigma()
            fOrbit += [p]
        sOrbit = sorted(fOrbit) 
        startPoint = sOrbit[0]
        startIndex = fOrbit.index(startPoint)
        l = len(fOrbit)
        for i in range(l):
            tOrbit += [fOrbit[(startIndex+i)%l]]
        return tOrbit, sOrbit
    
    def getTemporalOrbit(self):
        return self._temporalOrbit
    def getSpacialOrbit(self):
        return self._spacialOrbit
    
def main():
    #deploymentSequence = [3, 4]
    #rotationNumber = [2, 4]
    #orbit = goldbergOrbit(deploymentSequence, rotationNumber)
    #print(orbit)
    p = NaryFraction(exact=(),repeating=(0,1,1),degree=2)
    o = Orbit(p) 
    print(o.getTemporalOrbit())
    print(o.getSpacialOrbit())
    return

if __name__ == "__main__":
    # sys.argv = ["programName.py","--input","test.txt","--output","tmp/test.txt"]
    main()

