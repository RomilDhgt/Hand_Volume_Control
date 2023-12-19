# import necessary libraries
import cv2
import mediapipe as mp
import time
import Hand_Tracking_Module as htm
import math
import numpy as np
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Enabling ability to control volume control 
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

pastTime = 0
currentTime = 0

# Creating the video capture object using my laptops video camera
cap = cv2.VideoCapture(0)

# Setting the width and height of the camera display
camWidth, camHeight = 640*2, 360*2
cap.set(3,camWidth)
cap.set(4,camHeight)

detector = htm.handDetector(dCon=0.7, tCon=0.7)

while True:
    # Getting the video from the camera
    success, img = cap.read()

    img = detector.findHands(img)
    lmList = detector.findPos(img, draw=False)
    if len(lmList) != 0:
        
        x1, y1, = lmList[4][1], lmList[4][2]
        x2, y2, = lmList[8][1], lmList[8][2]
        cx ,cy = (x1+x2)//2 , (y1+y2)//2

        cv2.circle(img, (x1,y1), 15, (255,0,0), cv2.FILLED)
        cv2.circle(img, (x2,y2), 15, (255,0,0), cv2.FILLED)
        cv2.line(img, (x1,y1), (x2,y2), (255,0,0), 3)
        cv2.circle(img, (cx,cy), 15, (255,0,0), cv2.FILLED)

        length = math.hypot(x2-x1,y2-y1)

        if length < 50:
            cv2.circle(img, (cx,cy), 15, (0,0,255), cv2.FILLED)

        # Length range is [50,300]
        # Volume range is [-63.5, 0]
        
        vol = np.interp(length, [50,200], [minVol,maxVol])
        volBar = np.interp(length, [50,200], [400,150])
        #volNum = np.interp(length, [50,300], [0,100])
        
        volume.SetMasterVolumeLevel(vol, None)
        #cv2.putText(img,f'Volume:{int(volNum)}', (40,600), cv2.FONT_HERSHEY_PLAIN, 3, (0,155,255), 3)
        cv2.rectangle(img,(50,150),(85,400),(0,255,0), 3)
        cv2.rectangle(img,(50,int(volBar)),(85,400),(0,255,0), cv2.FILLED)

    # Getting timestamps to be able to use the trackers positioning data
    currentTime = time.time()
    framesPerSec = 1/(currentTime-pastTime)
    pastTime = currentTime
    # Displaying the frames per second the the screen
    cv2.putText(img,f'FPS:{int(framesPerSec)}', (40,50), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)

    # Showing the video from camera in a window
    cv2.imshow("Image",img)
    cv2.waitKey(1)