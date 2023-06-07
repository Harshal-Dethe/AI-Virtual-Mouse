import cv2
import imutils as imutils
import numpy as np
import HandTrackingModule as htm
import time
import pyautogui as pyautogui
from pynput.keyboard import Key, Controller
import autopy
import math

##############################
wCam, hCam = 640, 480
frameR = 100 # Frame reduction
smoothening = 7
##############################
pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
detector = htm.handDetector(maxHands=1)
wScr, hScr = autopy.screen.size()
# print(wScr, hScr)
keyboard = Controller()

while True:
    success, img = cap.read()
    # 1. Find the hand landmarks
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)
    # 2. Get the tips of the index  and middle finger
    if (len(lmList))!=0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        x3, y3 = lmList[4][1:]  # for thumb
        # print(x1,y1,x2,y2,x3,y3)
        # 3. check which fingers are up
        fingers = detector.fingersUp()
        # print(fingers)
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)

        # Volume controller function
        if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
            cx3, cy3 = (x1 + x3) // 2, (y1 + y3) // 2
            r, t = 9, 2
            if True:
                cv2.line(img, (x3, y3), (x1, y1), (255, 0, 255), t)
                cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
                cv2.circle(img, (x3, y3), r, (255, 0, 255), cv2.FILLED)
                cv2.circle(img, (cx3, cy3), r, (0, 0, 255), cv2.FILLED)
                length = math.hypot(x3 - x1, y3 - y1)

                if length < 100:
                    cv2.circle(img, (cx3, cy3), 10, (0, 255, 0), cv2.FILLED)
                    keyboard.press(Key.media_volume_up)
                    keyboard.release(Key.media_volume_up)
                    time.sleep(0.1)
                if length > 100:
                    cv2.circle(img, (cx3, cy3), 10, (0, 0, 0), cv2.FILLED)
                    keyboard.press(Key.media_volume_down)
                    keyboard.release(Key.media_volume_down)
                    time.sleep(0.1)

        # Right Click function
        if fingers[4] == 1:
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            r, t = 9, 2
            if True:
                cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
                cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
                cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
                cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)
                length = math.hypot(x2 - x1, y2 - y1)
                if length < 40:
                    cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)
                    pyautogui.rightClick()

        # Scroll function
        if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1:
            pyautogui.scroll(-40)
        if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 0:
            pyautogui.scroll(40)

        # 4. Only index finger: Moving mode
        if fingers[1] == 1 and fingers[2] == 0:
            # 5. Convert coordinates
            x3 = np.interp(x1, (frameR, wCam-frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam-frameR), (0, hScr))
            # 6. Smoothen Values
            clocY = plocY + (y3 - plocY) / smoothening
            clocX = plocX + (x3 - plocX) / smoothening
            # 7. Move Mouse
            autopy.mouse.move(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY

        # 8. Both index and middle fingers are up: Clicking Mode
        if fingers[1] == 1 and fingers[2] == 1:
            # 9. Find the distance between fingers
            length, img, lineInfo = detector.findDistance(8, 12, img)
            print(length)
            # 10. Click mouse if distance short
            if length < 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                autopy.mouse.click()

        # 11. Frame Rate
    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                (255, 0, 0), 3)
    # 12. Display
    cv2.imshow("AI virtual mouse", img)
    cv2.waitKey(1)