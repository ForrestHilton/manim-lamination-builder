import numpy as np

from manim_lamination_builder.points import NaryFraction


class Orbit:
    def __init__(self, point: NaryFraction = None , deployment_sequence: list = None, rotation_number: list = None, jump_over_sequence: list = None):
        if point != None and deployment_sequence == None and rotation_number == None and jump_over_sequence == None:
            self._temporalOrbit, self._spacialOrbit = self._fullOrbits(point)
        elif point == None and deployment_sequence != None and rotation_number != None:
            if all(isinstance(item, int) for item in deployment_sequence) and all(
                isinstance(item, int) for item in rotation_number 
            ):
                self._temporalOrbit, self._spacialOrbit = self._fullOrbits(
                    self._goldbergOrbit(deployment_sequence, rotation_number)
                )
        elif point == None and deployment_sequence != None and rotation_number == None and jump_over_sequence != None:
            if all(isinstance(item, int) for item in deployment_sequence) and all(
                isinstance(item, int) for item in jump_over_sequence 
            ):
                self._temporalOrbit, self._spacialOrbit = self._fullOrbits(self._jump_over_orbit(deployment_sequence, jump_over_sequence))
        else:
            raise TypeError(
                "Invalid argument(s)."
            )

    def __str__(self):
        return "[" + ", ".join(str(to) for to in self._temporalOrbit) + "]"

    def __eq__(self, other):
        if not isinstance(other, Orbit):
            return NotImplemented
        if len(self._temporalOrbit) != len(other.getTemporalOrbit()):
            return False
        if self._temporalOrbit[0] in other.getTemporalOrbit():
            return True
        return False

    def getTemporalOrbit(self):
        return self._temporalOrbit

    def getSpacialOrbit(self):
        return self._spacialOrbit

    def get_jump_over_sequence(self):
        jos = []
        length = len(self._temporalOrbit)
        for ti, tp in enumerate(self._temporalOrbit):
            if ti == 0:
                prev_index = 0
                continue
            for si, sp in enumerate(self._spacialOrbit):
                if sp == tp:
                    if si > prev_index:
                        jos += [si - prev_index]
                    else:
                        jos += [length - prev_index + si]
                    prev_index = si
        s = sum(jos)
        jos += [length - (s%length)]
        return jos

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

    def _goldbergOrbit(self, deploymentSequence, rotationNumber):
        fps = self._get_fixed_point_sequence(deploymentSequence)
        fpe = self._getFixedPointExpansion(fps)
        od = self._getOrbitDigits(fpe, rotationNumber)
        de = self._getDNaryExpansion(od, rotationNumber)
        return NaryFraction([], de, len(deploymentSequence) + 1)

    def _jump_over_orbit(self, deployment_sequence, jump_over_sequence):
        fps = self._get_fixed_point_sequence(deployment_sequence)
        fpe = self._getFixedPointExpansion(fps)

        #get temporal fpe
        orbit_length = len(jump_over_sequence)
        tfpe = [fpe[0]]
        i = 0
        for j in range(len(fpe)-1):
            i = (i+jump_over_sequence[j])%orbit_length
            tfpe += [fpe[i]]

        #get temporal AR sequence
        tar = []
        i = 0
        for j in range(len(fpe)):
            i = i+jump_over_sequence[j]
            if i >= orbit_length:
                tar += ['-']
                i %= orbit_length 
            else:
                tar += ['+']

        #get final orbit
        for i, ar in enumerate(tar):
            if ar == '-':
                tfpe[i] += 1
        orbit = NaryFraction(exact = (), repeating = tfpe, degree = len(deployment_sequence)+1)

        return orbit


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
        orbitList = [Orbit(NaryFraction(exact=(), repeating=point, degree=self.degree))]
        for i in range(total - 1):
            point = self._incrementBaseN(point, self.degree)
            point = self._padWithZeros(point, self.length)
            if self._isNewOrbit(point, orbitList):
                orbitList.append(
                    Orbit(NaryFraction(exact=(), repeating=point, degree=self.degree))
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

    def _isNewOrbit(self, newPoint:list, orbits:list):
        orbitLength = len(newPoint)
        rotPoint = newPoint
        newOrbit = Orbit(NaryFraction(exact=(), repeating=rotPoint, degree=self.degree))
        for i in range(len(orbits)):
            #print(str(orbits[i]) + "; " + str(newOrbit))
            #print()
            if orbits[i] == newOrbit:
                return False
        return True

    def _rotatePoint(self, point):
        newPoint = point[1:] + point[:1]
        return newPoint


def main():
    ds = [5, 5]
    jos = [1,1,2,4,2]
    jo = Orbit(deployment_sequence = ds, jump_over_sequence = jos)
    print(jo)
    print(jo.get_jump_over_sequence())

    return


if __name__ == "__main__":
    # sys.argv = ["programName.py","--input","test.txt","--output","tmp/test.txt"]
    main()
