import numpy as np

from manim_lamination_builder.points import NaryFraction


class Orbit:
    def __init__(self, arg1, arg2=None):
        if isinstance(arg1, NaryFraction) and arg2 == None:
            self._temporalOrbit, self._spacialOrbit = self._fullOrbits(arg1)
        elif isinstance(arg1, list) and isinstance(arg2, list):
            if all(isinstance(item, int) for item in arg1) and all(
                isinstance(item, int) for item in arg2
            ):
                self._temporalOrbit, self._spacialOrbit = self._fullOrbits(
                    self._goldbergOrbit(arg1, arg2)
                )
        else:
            raise TypeError(
                "Invalid argument(s). Valid arguments are (NaryFraction) or (list[int],list[int])"
            )

    # returns a full orbit in spacial order
    def _fullOrbits(self, point: NaryFraction):
        assert (
            len(point.exact) == 0 and len(point.repeating) != 0
        ), "must be periodic point"
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
            tOrbit += [fOrbit[(startIndex + i) % l]]
        return tOrbit, sOrbit

    def getTemporalOrbit(self):
        return self._temporalOrbit

    def getSpacialOrbit(self):
        return self._spacialOrbit

    def _goldbergOrbit(self, deploymentSequence, rotationNumber):
        fps = self._get_fixed_point_sequence(deploymentSequence)
        fpe = self._getFixedPointExpansion(fps)
        od = self._getOrbitDigits(fpe, rotationNumber)
        de = self._getDNaryExpansion(od, rotationNumber)
        return NaryFraction([], de, len(deploymentSequence) + 1)

    # input list deployment sequence: depSeq
    def _get_fixed_point_sequence(self, depSeq):
        fixed_point_sequence = []
        i = 0
        for n in depSeq:
            if i == 0:
                fixed_point_sequence.append(n)
            else:
                fixed_point_sequence.append(n - depSeq[i - 1])
            i = i + 1
        return fixed_point_sequence

    # input list fixed point sequence: fps
    def _getFixedPointExpansion(self, fps):
        fixedPointExpansion = []
        j = 0
        for n in fps:
            for i in range(n):
                fixedPointExpansion.append(j)
            j = j + 1
        return fixedPointExpansion

    # input list fixed point expansion: fpe, list rotation number: rn
    def _getOrbitDigits(self, fpe, rn):
        orbitDigits = []
        adv = rn[1] - rn[0]
        for i in range(len(fpe)):
            if i < adv:
                orbitDigits.append(fpe[i])
            else:
                orbitDigits.append(fpe[i] + 1)
        return orbitDigits

    # input list orbit digits: od, list rotation number: rn
    def _getDNaryExpansion(self, od, rn):
        assert (
            rn[0] != 0 and rn[1] != 0
        ), "Rotation number should not have 0 as either number."
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


class AllOrbits:
    iter_index = 0

    def __init__(self, degree: int, length: int):
        self.degree = degree
        self.length = length
        self.orbits = self._initOrbits()

    def __iter__(self):
        self.iter_index = 0
        return self

    def __next__(self):
        self.iter_index += 1
        if self.iter_index > len(self.orbits):
            raise StopIteration
        return self.orbits[self.iter_index - 1]

    def _initOrbits(self):
        total = self.degree**self.length
        point = [0]
        orbitList = [NaryFraction(exact=(), repeating=point, degree=self.degree)]
        for i in range(total - 1):
            point = self._incrementBaseN(point, self.degree)
            point = self._padWithZeros(point, self.length)
            if self._isNewOrbit(point, orbitList):
                orbitList.append(
                    NaryFraction(exact=(), repeating=point, degree=self.degree)
                )
        return orbitList

    def _incrementBaseN(self, inputNum, base):
        num = inputNum[:]
        num.reverse()
        outputNum = []
        tempNum = 0
        carry = 1

        for i in range(len(num)):
            tempNum = num[i] + carry
            if tempNum >= base:
                tempNum %= base
                carry = 1
            else:
                carry = 0
            outputNum.append(tempNum)

        if carry == 1:
            outputNum.append(carry)

        outputNum.reverse()
        return outputNum

    def _padWithZeros(self, inputList, totalLength):
        inputList.reverse()
        numZeros = totalLength - len(inputList)
        numZeros = numZeros if numZeros >= 0 else 0
        for i in range(numZeros):
            inputList.append(0)
        inputList.reverse()
        return inputList

    def _isNewOrbit(self, newPoint, orbits):
        orbitLength = len(newPoint)
        newOrbit = []
        rotPoint = newPoint
        for i in range(orbitLength):
            rotPoint = self._rotatePoint(rotPoint)
            newOrbit.append(
                NaryFraction(exact=(), repeating=rotPoint, degree=self.degree)
            )
        for i in range(len(orbits)):
            if orbits[i] in newOrbit:
                return False
        return True

    def _rotatePoint(self, point):
        newPoint = point[1:] + point[:1]
        return newPoint


def main():
    # deploymentSequence = [3, 4]
    # rotationNumber = [2, 4]
    # orbit = goldbergOrbit(deploymentSequence, rotationNumber)
    # print(orbit)
    p = NaryFraction(exact=(), repeating=(0, 1, 2, 1, 2), degree=3)
    o = Orbit(p)
    print(o.getTemporalOrbit())
    print(o.getSpacialOrbit())
    d = [1, 5]
    r = [2, 5]
    q = Orbit(d, r)
    print(q.getTemporalOrbit())
    print(q.getSpacialOrbit())
    # orbits = AllOrbits(3,5)
    # ol = []
    # for o in orbits:
    #     ol.append(o)
    # print(ol)
    # print(len(ol))

    return


if __name__ == "__main__":
    # sys.argv = ["programName.py","--input","test.txt","--output","tmp/test.txt"]
    main()
