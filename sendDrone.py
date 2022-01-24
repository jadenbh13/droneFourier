import math
import time
import matplotlib.pyplot as plt

xFile = "xDesire.txt"
yFile = "yDesire.txt"
zFile = "zDesire.txt"

def sendToLoc(x, y, z):
    print(f"Going to ({x}, {y}, {z})")
    with open(xFile, "w") as myfile:
        myfile.write(str(x))
    with open(yFile, "w") as myfile:
        myfile.write(str(y))
    with open(zFile, "w") as myfile:
        myfile.write(str(z))


xLd = []
yLd = []
zLd = []

ius = 0
while ius < (2 * math.pi):
    yAx = (math.sin(ius)) * 30
    xAx = ius * 8
    xLd.append(0)
    yLd.append(yAx)
    zLd.append(xAx)
    ius += 0.05



def getFloatFromFile(fil):
    filer = open(fil, 'r')
    LineCount = filer.readlines()
    outList = []
    for its in LineCount:
        outList.append(float(its))
    return outList


xFl = 'normX.txt'
yFl = 'normY.txt'
aFl = 'normPhase.txt'

newX = getFloatFromFile(xFl)
newY = getFloatFromFile(yFl)
newA = getFloatFromFile(aFl)

closestFreq = []
def closeP(lisX, xInp):
    disX = []
    for io in range(0, len(lisX)):
        disTo = abs(xInp - lisX[io])
        disX.append(disTo)
    minInd = disX.index(min(disX))
    return minInd


def getSinWave(xs, hertz, norY, phases, norX):
    indx = closeP(xs, hertz)
    magnitude = norY[indx]
    phaseAng = phases[indx]
    frequency = xs[indx]
    normFrequency = norX[indx]
    print(normFrequency)
    sinListX = []
    sinListY = []
    if magnitude > 50:
        magnitude = 50
    ub = 0
    while ub < (2 * math.pi):
        sinVal = magnitude * (math.sin((ub * normFrequency) + phaseAng))
        sinListX.append(ub * 12.74) # Normalize between 0 and 100
        sinListY.append(sinVal)
        ub += 0.03
    return sinListX, sinListY


def sendList(xList, yList, zList):
    timeDelay = 30 / len(xList)
    prevX = 0
    prevY = 0
    prevZ = 0
    for ui in range(0, len(xList)):
        xToSend = 0
        try:
            xToSend = xList[ui]
        except:
            xToSend = prevX

        yToSend = 0
        try:
            yToSend = yList[ui]
        except:
            yToSend = prevY

        zToSend = 0
        try:
            zToSend = zList[ui]
        except:
            zToSend = prevZ

        sendToLoc(xToSend, yToSend, zToSend)
        prevX = xToSend
        prevY = yToSend
        prevZ = zToSend
        time.sleep(timeDelay)
    newDelay = 20 / int(prevZ)
    jn = int(prevZ)
    while jn > 1:
        sendToLoc(0, 0, jn)
        jn -= 1
        time.sleep(newDelay)
    sendToLoc(0, 0, 0)

#sendList(xLd, yLd, zLd)
normalizedX = []
normalizedY = []
xNorm = 80 / max(newX)
for ij in range(0, len(newX)):
    normalizedX.append((xNorm * newX[ij]))
    normalizedY.append((xNorm * newY[ij]) * (3/4))


allX = getFloatFromFile("allX.txt")
allY = getFloatFromFile("allY.txt")
allPhase = getFloatFromFile("allPhase.txt")

normAllX = []
normAllY = []
normYDep = []
xNormOfAll = 80 / max(allX)
yNormOfAll = 50 / max(allY)
for ij in range(0, len(allX)):
    normAllX.append((xNormOfAll * allX[ij]))
    normAllY.append((xNormOfAll * allY[ij]))
    normYDep.append((yNormOfAll * allY[ij]))

print(max(normAllY))

zMain = [0] * len(normalizedX)

sinHertz = getSinWave(allX, 300, normAllY, allPhase, normAllX)
zSin = [0] * len(sinHertz[0])
fig, axs = plt.subplots(3)
#print(sinHertz)
sendToLoc(0, 0, 0)
#sendList(zSin, sinHertz[1], sinHertz[0])
axs[0].scatter(normalizedX, normalizedY, color="blue", s=5)
axs[1].plot(normalizedX, normalizedY, color="green", linewidth=3)
axs[2].scatter(sinHertz[0], sinHertz[1], color="red", s=5)
plt.show()

"""sendToLoc(0, 0, 0)
time.sleep(3)
sendToLoc(20, 20, 10)
time.sleep(3)
sendToLoc(-20, -10, 40)
time.sleep(3)
sendToLoc(0, 0, 0)"""
