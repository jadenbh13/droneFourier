import matplotlib.pyplot as plt
import numpy as np
import wave
import sys
import math
import time

sampFreq = 8


def getPhaseAngle(x, y):
    phaseA = 0
    if x == 0 and y == 0:
        phaseA = 0
    elif x == 0 and y != 0:
        if y > 0:
            phaseA = math.pi / 2
        elif y < 0:
            phaseA = (3 * math.pi) / 2
    elif x != 0 and y == 0:
        if x > 0:
            phaseA = 0
        elif x < 0:
            phaseA = math.pi
    else:
        if (x > 0) and (y > 0):
            angs = math.atan(y / x)
            phaseA = angs
        elif (x < 0) and (y > 0):
            angs = math.pi + (math.atan(y / x))
            phaseA = angs
        elif (x < 0) and (y < 0):
            angs = math.pi + (math.atan(y / x))
            phaseA = angs
        elif (x > 0) and (y < 0):
            angs = ((3 * math.pi) / 2) + math.atan(abs(x) / abs(y))
            phaseA = angs
    degPhase = phaseA * (180 / math.pi)
    #print(f"Degrees: {degPhase}")
    return phaseA, degPhase



def timeToFreq(xList, yList, freq):
    nyquistLimit = freq / 2
    N = len(xList)
    freqGraphX = []
    freqGraphY = []
    correspondingAng = []
    degreeAng = []
    for firstFactor in range(0, len(xList)):
        reals = 0
        ims = 0
        #print("   ")
        for secondFactor in range(0, (len(xList))):
            innerFactor = (-1) * ((2 * math.pi * firstFactor * secondFactor) / N)
            #print(yList[secondFactor])
            currentReal = (yList[secondFactor]) * (math.cos(innerFactor))
            currentIm = (yList[secondFactor]) * (math.sin(innerFactor))
            reals += currentReal
            ims += currentIm
        realPart = reals
        imaginaryPart = ims
        #print("   ")
        #print(f"{firstFactor} real: {realPart}")
        #print(f"{firstFactor} imaginary: {imaginaryPart}")
        #if hertzOnGraph < nyquistLimit:
        rawMag = math.sqrt((realPart ** 2) + (imaginaryPart ** 2))
        magnitude = (rawMag * 2) / N
        phaseAngle = getPhaseAngle(realPart, imaginaryPart)
        freqGraphY.append(magnitude)
        correspondingAng.append(phaseAngle[0])
        degreeAng.append(phaseAngle[1])
        #print(f"Magnitude: {magnitude}, Phase: {phaseAngle[1]}")
        #print("   ")
    X = np.array(freqGraphY)
    N = len(X)
    n = np.arange(N)
    T = N/freq
    freqInts = n/T
    intervl = freq/len(xList)
    """print(freqInts)
    print(intervl)
    newInts = []
    ol = 0
    for lm in range(0, len(xList)):
        ol += intervl
        newInts.append(ol)
    print(newInts)"""
    return freqInts, abs(np.array(freqGraphY)), correspondingAng, degreeAng




"""diffIn = (2 * math.pi) / 8

xLt = []
yLt = []
bas = 0
while bas < (2 * math.pi):
    xTu = bas
    yTu = (math.sin(bas)) + (3 * (math.sin(2 * bas))) + (0.5 * (math.sin(3 * bas)))
    xLt.append(xTu)
    yLt.append(yTu)
    bas += diffIn
fourierGraph = timeToFreq(xLt, yLt, sampFreq)
#plt.scatter(xLt, yLt, color='red')
plt.scatter(fourierGraph[0], fourierGraph[1], color='blue')
plt.show()"""
