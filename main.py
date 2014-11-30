import numpy as np
import cv2

history = 500
nmixtures = 5
backgroundRatio = 0.6
noiseSigma = 0.01
alpha = 0.01

def setHistory(value):
    global history, fgbg
    history = value
    fgbg = cv2.BackgroundSubtractorMOG(history, nmixtures, backgroundRatio, noiseSigma)

def setNmixtures(value):
    global nmixtures, fgbg
    nmixtures = value
    fgbg = cv2.BackgroundSubtractorMOG(history, nmixtures, backgroundRatio, noiseSigma)
    
def setBackgroundRatio(value):
    global backgroundRatio, fgbg
    backgroundRatio = (float)(value)/100
    fgbg = cv2.BackgroundSubtractorMOG(history, nmixtures, backgroundRatio, noiseSigma)

def setNoiseSigma(value):
    global noiseSigma, fgbg
    noiseSigma = (float)(value)/100
    fgbg = cv2.BackgroundSubtractorMOG(history, nmixtures, backgroundRatio, noiseSigma)

def setAlpha(value):
    global alpha, fgbg, cap
    alpha = (float)(value)/100

def read(filename):
    global cap, fgbg, kernel
    cv2.namedWindow('App', cv2.WINDOW_NORMAL)
    cv2.createTrackbar('history', 'App', history, 1000, setHistory)
    cv2.createTrackbar('nmixtures', 'App', nmixtures, 10, setNmixtures)
    cv2.createTrackbar('backgroundRatio', 'App', 6, 100, setBackgroundRatio)
    cv2.createTrackbar('noiseSigma', 'App', 1, 100, setNoiseSigma)
    cv2.createTrackbar('alpha', 'App', 1, 100, setAlpha)

    kernel = np.ones((3, 3), np.uint8)
    fgbg = cv2.BackgroundSubtractorMOG(history, nmixtures, backgroundRatio, noiseSigma)

    cap = cv2.VideoCapture(filename)
    cap.read()

    play()
    
def play():
    while(True):
        ret, frame = cap.read()
        if ret == False:
            break

        fgmask = fgbg.apply(frame, None, alpha)
        fgmask = cv2.erode(fgmask, kernel, iterations=1)
        fgmask = cv2.dilate(fgmask, kernel, iterations=1)

        #fgmask = cv2.dilate(fgmask, kernel, iterations=1)
        #fgmask = cv2.erode(fgmask, kernel, iterations=1)
       
        contours, hierarchy = cv2.findContours(fgmask, cv2.cv.CV_RETR_EXTERNAL, cv2.cv.CV_CHAIN_APPROX_NONE)
        cv2.drawContours(frame, contours, -1, cv2.cv.Scalar(0, 0, 255), 2)
        cv2.imshow('App', frame) 

        k = cv2.waitKey(30) & 0xff
        if k == 27:
            cap.release()
            cv2.destroyAllWindows()
            break


if __name__ == "__main__":
    read('../video/CAM00206.mp4')
