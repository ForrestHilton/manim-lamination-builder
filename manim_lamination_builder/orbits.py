import numpy as np

deploymentSequence = [3,6]

#rotation number p/q as [p,q]
rotationNumber = [3,6]
rotationFactor = np.gcd(rotationNumber[0],rotationNumber[1])


#input list deployment sequence: depSeq
def getFixedPointSequence(depSeq):
    fixedPointSequence = []
    i=0
    for n in depSeq:
        if i==0:
            fixedPointSequence.append(n)
        else:
            fixedPointSequence.append(n-depSeq[i-1])
        i=i+1
    return fixedPointSequence

#input list fixed point sequence: fps
def getFixedPointExpansion(fps):
    fixedPointExpansion = []
    j=0
    for n in fps:
        for i in range(n):
            fixedPointExpansion.append(j)
        j=j+1
    return fixedPointExpansion

#input list fixed point expansion: fpe, list rotation number: rn
def getOrbitDigits(fpe,rn):
    orbitDigits = []
    adv = rn[1]-rn[0]
    i=0
    for n in fpe:
        if i<adv:
            orbitDigits.append(fpe[i])
        else:
            orbitDigits.append(fpe[i]+1)
        i=i+1
    return orbitDigits

#input list orbit digits: od, list rotation number: rn
def getDNaryExpansion(od, rn):
    factor = rotationFactor
    step = rn[0]
    base = rn[1]
    dNaryExpansion = [1]
    dneTemp = []
    for k in range(factor):
        for n in range(int(base/factor)):
            dneTemp.append(od[((n*step)+k)%base])
        if k==0:
            dNaryExpansion[0] = dneTemp
        else:
            dNaryExpansion.append(dneTemp)
        dneTemp = []
    return dNaryExpansion

def main():
    fps = getFixedPointSequence(deploymentSequence)
    fpe = getFixedPointExpansion(fps)
    od = getOrbitDigits(fpe, rotationNumber)
    de = getDNaryExpansion(od, rotationNumber)

    print(rotationFactor)
    print(fps)
    print(fpe)
    print(od)
    print(de)
    return

if __name__ == '__main__':
    #sys.argv = ["programName.py","--input","test.txt","--output","tmp/test.txt"]
    main()