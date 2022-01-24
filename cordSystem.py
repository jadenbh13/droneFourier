import argparse
import imutils
import cv2
import sys
from djitellopy import Tello
from PIL import Image
import math
import time


referImg = "thirtyRef.png"


ARUCO_DICT = {
	"DICT_4X4_50": cv2.aruco.DICT_4X4_50,
	"DICT_4X4_100": cv2.aruco.DICT_4X4_100,
	"DICT_4X4_250": cv2.aruco.DICT_4X4_250,
	"DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
	"DICT_5X5_50": cv2.aruco.DICT_5X5_50,
	"DICT_5X5_100": cv2.aruco.DICT_5X5_100,
	"DICT_5X5_250": cv2.aruco.DICT_5X5_250,
	"DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
	"DICT_6X6_50": cv2.aruco.DICT_6X6_50,
	"DICT_6X6_100": cv2.aruco.DICT_6X6_100,
	"DICT_6X6_250": cv2.aruco.DICT_6X6_250,
	"DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
	"DICT_7X7_50": cv2.aruco.DICT_7X7_50,
	"DICT_7X7_100": cv2.aruco.DICT_7X7_100,
	"DICT_7X7_250": cv2.aruco.DICT_7X7_250,
	"DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
	"DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
#	"DICT_APRILTAG_16h5": cv2.aruco.DICT_APRILTAG_16h5,
#	"DICT_APRILTAG_25h9": cv2.aruco.DICT_APRILTAG_25h9,
#	"DICT_APRILTAG_36h10": cv2.aruco.DICT_APRILTAG_36h10,
#	"DICT_APRILTAG_36h11": cv2.aruco.DICT_APRILTAG_36h11
}

arucoDict = cv2.aruco.Dictionary_get(ARUCO_DICT["DICT_4X4_250"])
arucoParams = cv2.aruco.DetectorParameters_create()


def Focal_Length_Finder(measured_distance, real_width, width_in_rf_image):
    focal_length = (width_in_rf_image * measured_distance) / real_width
    return focal_length


def Distance_finder(Focal_Length, real_face_width, face_width_in_frame):
    global prevDistance
    distance = 0
    if face_width_in_frame == 0:
        distance = prevDistance
    else:
        distance = (real_face_width * Focal_Length)/face_width_in_frame
    prevDistance = distance
    return distance



def writeLineEq(x, slope, b):
    value = (x * slope) + b
    return value


def finiteIntegral(n, start, end, x, slope, b):
    numStar = (end - start) / n
    totalIntegral = 0
    for i in range(1, n + 1):
        currYMark = start + (numStar * i)
        currLength = writeLineEq(x, slope, b)
        squareValue = currLength * numStar
        totalIntegral += squareValue
    return totalIntegral



def arucoMarker(image):
    (corners, ids, rejected) = cv2.aruco.detectMarkers(image, arucoDict,
    parameters=arucoParams)
    imageWd = 0
    if len(corners) > 0:
        ids = ids.flatten()
        for (markerCorner, markerID) in zip(corners, ids):
            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners
            topRight = (int(topRight[0]), int(topRight[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))
            xWid = abs(topLeft[0] - topRight[0])
            yWid = abs(topLeft[1] - topRight[1])
            widInIm = math.sqrt((xWid ** 2) + (yWid ** 2))
            imageWd = widInIm
    return imageWd


def difference(ars):
    differ = max(ars) - min(ars)
    return differ


Known_distance = 30
Known_width = 22
ref_image = cv2.imread(referImg)
ref_image_width_frame = arucoMarker(ref_image)
Focal_length_found = Focal_Length_Finder(
    Known_distance, Known_width, ref_image_width_frame)
print(Focal_length_found)





tello = Tello()
tello.connect()
tello.streamon()
frame_read = tello.get_frame_read()
initialYaw = tello.get_yaw()



prevXFrom = 0
prevYFrom = 0
prevZFrom = 0
prevTime = 0
prevWid = 0
speedCap = 50


def detectMarker(image, xOrigin, yOrigin, zOrigin):
    global Focal_length_found
    global Known_width
    global initialYaw
    global prevXFrom
    global prevYFrom
    global prevZFrom
    global prevTime
    global prevWid
    global speedCap
    he, we, ce = image.shape
    midX = int(we / 2)
    midY = int((he / 2) - 100)
    defaultYaw = 0
    if (tello.get_yaw()) > initialYaw:
        defaultYaw = int(((tello.get_yaw()) - initialYaw) * (-1.5))
    elif (tello.get_yaw()) < initialYaw:
        defaultYaw = int((initialYaw - (tello.get_yaw())) * (1.5))
    (corners, ids, rejected) = cv2.aruco.detectMarkers(image, arucoDict,
    parameters=arucoParams)
    #print(corners)
    if len(corners) > 0:
        # flatten the ArUco IDs list
        ids = ids.flatten()

        # loop over the detected ArUCo corners
        for (markerCorner, markerID) in zip(corners, ids):
            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners
            topRight = (int(topRight[0]), int(topRight[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))
            currentTime = time.time()

            #widInIm = math.sqrt((xWid ** 2) + (yWid ** 2))
            widInIm = int(abs(topLeft[0] - topRight[0]))
            cv2.line(image, topLeft, topRight, (0, 255, 0), 2)
            cv2.line(image, topRight, bottomRight, (0, 255, 0), 2)
            cv2.line(image, bottomRight, bottomLeft, (0, 255, 0), 2)
            cv2.line(image, bottomLeft, topLeft, (0, 255, 0), 2)
            #print(widInIm)
            distToMark = Distance_finder(Focal_length_found, Known_width, widInIm) - 130
            eachPixel = 0
            if widInIm == 0:
                eachPixel = abs(Known_width / prevWid)
            else:
                eachPixel = abs(Known_width / widInIm)
            #yEach = abs(Known_width / yWidth)
            cv2.rectangle(image, topLeft, bottomRight, (255,0,0), 4)
            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomLeft[1]) / 2.0)
            centPx = ((we / 2) + (xOrigin / eachPixel)) - cX
            centPy = (midY + (yOrigin / eachPixel)) - cY
            cmFromCentX = (centPx * eachPixel)
            cmFromCentY = (centPy * eachPixel) * (-1)
            #cmFromCentY = (abs(midY - cY))
            xPTerm = cmFromCentX
            yPTerm = cmFromCentY
            zPTerm = distToMark - zOrigin


            xDTerm = (cmFromCentX - prevXFrom) / (currentTime - prevTime)
            xYInt = xPTerm - (currentTime * xDTerm)
            xITerm = finiteIntegral(6, prevTime, currentTime, currentTime, xDTerm, xYInt)
            xTotalPid = int((xPTerm * 1) + (xITerm * 2.0) + (xDTerm * 2.3) * (1/2)) * (-1)
            if xTotalPid > speedCap:
                xTotalPid = speedCap
            if xTotalPid < (speedCap * (-1)):
                xTotalPid = (speedCap * (-1))
            print("   ")
            print(f"X PTerm {xPTerm}")
            print(f"Y PTerm {yPTerm}")
            print(f"Z PTerm {zPTerm}")
            #print(f"X PID {xTotalPid}")
            print("   ")


            yDTerm = (cmFromCentY - prevYFrom) / (currentTime - prevTime)
            yYInt = yPTerm - (currentTime * yDTerm)
            yITerm = finiteIntegral(6, prevTime, currentTime, currentTime, yDTerm, yYInt)
            yTotalPid = int((yPTerm * 1) + (yITerm * 2.0) + (yDTerm * 2.3) * (1/2)) * (-1)

            if yTotalPid > speedCap:
                yTotalPid = speedCap
            if yTotalPid < (speedCap * (-1)):
                yTotalPid = (speedCap * (-1))

            #print(f"Y PID {yTotalPid}")
            #print("   ")


            zDTerm = (zPTerm - prevZFrom) / (currentTime - prevTime)
            zYInt = zPTerm - (currentTime * zDTerm)
            zITerm = finiteIntegral(6, prevTime, currentTime, currentTime, zDTerm, zYInt)
            zTotalPid = int((zPTerm * 1) + (zITerm * 2.0) + (zDTerm * 2.3) * (1/2))

            if zTotalPid > speedCap:
                zTotalPid = speedCap
            if zTotalPid < (speedCap * (-1)):
                zTotalPid = (speedCap * (-1))


            """print(f"Z PID {zTotalPid}")
            print("   ")"""


            cv2.circle(image, (cX, cY), 10, (0, 0, 255), 10)
            cv2.putText(image, str(markerID),
            	(topLeft[0], topLeft[1] - 15), cv2.FONT_HERSHEY_SIMPLEX,
            	0.5, (0, 255, 0), 2)
            prevXFrom = xPTerm
            prevYFrom = yPTerm
            prevZFrom = zPTerm
            prevWid = widInIm
            prevTime = currentTime

            tello.send_rc_control(xTotalPid, zTotalPid, yTotalPid, defaultYaw)
    else:
        print("No aruco")
        tello.send_rc_control(0, 0, 0, defaultYaw)
    cv2.circle(image, (midX, midY), 12, (0, 255, 0), 12)
    cv2.imshow("Image", image)



xFile = "xDesire.txt"
yFile = "yDesire.txt"
zFile = "zDesire.txt"


print("Starting...")
iuos = 1
while iuos < 4:
    print(iuos)
    time.sleep(1)
    iuos += 1


tello.takeoff()
prevLocsX = 0
prevLocsY = 0
prevLocsZ = 0
while True:
    frm = frame_read.frame
    xDes = 0
    with open(xFile) as f:
        try:
            xDes = float(f.read()) * (-1)
        except:
            xDes = prevLocsX

    yDes = 0
    with open(yFile) as f:
        try:
            yDes = float(f.read())
        except:
            yDes = prevLocsY

    zDes = 0
    with open(zFile) as f:
        try:
            zDes = float(f.read())
        except:
            zDes = prevLocsZ

    print(xDes)
    print(yDes)
    print(zDes)
    #print(xDes)
    detMs = detectMarker(frm, xDes, yDes, zDes)
    if cv2.waitKey(1) == ord("q"):
        break
    time.sleep(0.1)
    prevLocsX = xDes
    prevLocsY = yDes
    prevLocsZ = zDes

tello.land()
cv2.destroyAllWindows()
tello.streamoff()
