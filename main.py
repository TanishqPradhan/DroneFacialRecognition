from djitellopy import tello
import cv2
import numpy as np
import time

me = tello.Tello()
me.connect()
print(me.get_battery())

me.streamon()
me.takeoff()
me.send_rc_control(0, 0, 25, 0)
time.sleep(2.2)

fbRange = [6200, 6800]
pid = [0.4, 0.4, 0]
pError = 0
w, h = 360, 240


def findFace(image):
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    imageGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(imageGray, 1.2, 8)

    myFaceListC = []
    myFaceListArea = []

    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cx = x + w // 2
        cy = y + h // 2
        area = w * h
        myFaceListC.append([cx, cy])
        myFaceListArea.append(area)

    if len(myFaceListArea) != 0:
        i = myFaceListArea.index(max(myFaceListArea))
        return image, [myFaceListC[i], myFaceListArea[i]]
    else:
        return image, [[0, 0], 0]


def trackFace( info, w, pid, pError):
    area = info[1]
    x, y = info[0]
    fb = 0

    error = x - w // 2
    speed = pid[0] * error + pid[1] * (error - pError)
    speed = int(np.clip(speed, -100, 100))

    if area > fbRange[0] and area < fbRange[1]:
        fb = 0
    elif area > fbRange[1]:
        fb = -20
    elif area < fbRange[0] and area != 0:
        fb = 20

    if x == 0:
        speed = 0
        error = 0

    me.send_rc_control(0, fb, 0, speed)
    return error


# videoCapture = cv2.VideoCapture(1)

while True:
    # _, image = videoCapture.read()
    image = me.get_frame_read().frame
    image = cv2.resize(image, (w, h))
    image, info = findFace(image)
    pError = trackFace( info, w, pid, pError)
    print("Center", info[0], "Area", info[1])
    cv2.imshow("Output", image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        me.land()
        break