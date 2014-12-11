import numpy as np
import cv2
import sys

history = 50
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
    cv2.namedWindow("App", cv2.WND_PROP_FULLSCREEN)          
    cv2.setWindowProperty("App", cv2.WND_PROP_FULLSCREEN, cv2.cv.CV_WINDOW_FULLSCREEN)

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
    counter = 0
    while(True):
        ret, frame = cap.read()
        if ret == False:
            break

        red = frame[:,:,2]
        green = frame[:,:,1]
        blue = frame[:,:,0]
        #frame = red
        fgmask = fgbg.apply(frame, None, alpha)
        fgmask = cv2.erode(fgmask, kernel, iterations=1)
        fgmask = cv2.dilate(fgmask, kernel, iterations=1)

        fgimg = cv2.cvtColor(fgmask, cv2.COLOR_GRAY2BGR)

        #fgmask = cv2.dilate(fgmask, kernel, iterations=1)
        #fgmask = cv2.erode(fgmask, kernel, iterations=1)
       
        contours, hierarchy = cv2.findContours(fgmask, cv2.cv.CV_RETR_EXTERNAL, cv2.cv.CV_CHAIN_APPROX_NONE)
        #cv2.drawContours(frame, contours, -1, cv2.cv.Scalar(0, 0, 255), 2)
        p1 = (40, 680)
        p2 = (1240, 700)
        cv2.rectangle(frame, p1, p2, (0, 255, 0), cv2.cv.CV_FILLED)
        
        try: hierarchy = hierarchy[0]
        except: hierarchy = []
        for contour, hier in zip(contours, hierarchy):
            (x, y, w, h) = cv2.boundingRect(contour)
            if w > 45 and h > 45:
                point = (x + x + w)/2, (y + y + h)/2
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2) 
                cv2.circle(frame, point, 6, (0, 0, 255), -1)
                if point[0] > p1[0] and point[0] < p2[0] and point[1] > p1[1] and point[1] < p2[1]:
                    counter += 1

        text = str(counter)
        cv2.putText(frame, text, (600, 100), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 0, 255), 4)
        image = np.hstack((frame, fgimg))
        cv2.imshow('App', image) 

        k = cv2.waitKey(30) & 0xff
        if k == 27:
            cap.release()
            cv2.destroyAllWindows()
            break


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print "Usage: " + sys.argv[0] + " [filename.mp4]"
    else:
        read(sys.argv[1])
