import numpy as np
import cv2
import sys

history = 40
nmixtures = 5
backgroundRatio = 0.5
alpha = 0.03


class Point:
    def __init__(self, p=None):
        self.x = p[0]
        self.y = p[1]

def setHistory(value):
    global history, fgbg
    history = value
    fgbg = cv2.BackgroundSubtractorMOG(history, nmixtures, backgroundRatio)

def setNmixtures(value):
    global nmixtures, fgbg
    nmixtures = value
    fgbg = cv2.BackgroundSubtractorMOG(history, nmixtures, backgroundRatio)
    
def setBackgroundRatio(value):
    global backgroundRatio, fgbg
    backgroundRatio = (float)(value)/100
    fgbg = cv2.BackgroundSubtractorMOG(history, nmixtures, backgroundRatio)

def setAlpha(value):
    global alpha, fgbg, cap
    alpha = (float)(value)/100

def read(filename):
    global cap, fgbg, kernel
    cv2.namedWindow("App", cv2.WND_PROP_FULLSCREEN)          
    cv2.setWindowProperty("App", cv2.WND_PROP_FULLSCREEN, cv2.cv.CV_WINDOW_FULLSCREEN)

    cv2.createTrackbar('history', 'App', history, 1000, setHistory)
    cv2.createTrackbar('nmixtures', 'App', nmixtures, 10, setNmixtures)
    cv2.createTrackbar('backgroundRatio', 'App', (int)(backgroundRatio * 100), 100, setBackgroundRatio)
    cv2.createTrackbar('alpha', 'App', (int)(alpha * 100), 100, setAlpha)

    kernel = np.ones((3, 3), np.uint8)
    fgbg = cv2.BackgroundSubtractorMOG(history, nmixtures, backgroundRatio)

    cap = cv2.VideoCapture(filename)
    cap.read()

    play()


def play():
    cframe = 0
    counter = 0
    counted = []

    while(True):
        ret, frame = cap.read()
        if ret == False:
            break

        cframe += 1
        origframe = frame
        
        fgmask = fgbg.apply(frame, None, alpha)
        #fgmask = cv2.erode(fgmask, kernel, iterations=2)
        thresh, fgmask = cv2.threshold(fgmask, 250, 255, cv2.THRESH_BINARY)
        fgmask = cv2.dilate(fgmask, kernel, iterations=4)

        fgimg = cv2.cvtColor(fgmask, cv2.COLOR_GRAY2BGR)
    
        contours, hierarchy = cv2.findContours(fgmask, cv2.cv.CV_RETR_EXTERNAL, cv2.cv.CV_CHAIN_APPROX_SIMPLE)
        p1 = (40, 660)
        pLT = Point(p1)
        p2 = (1240, 700)
        pRB = Point(p2)
        cv2.rectangle(frame, p1, p2, (0, 255, 0), cv2.cv.CV_FILLED)
        
        try: hierarchy = hierarchy[0]
        except: hierarchy = []

        detected = []
        for contour, hier in zip(contours, hierarchy):
            (x, y, w, h) = cv2.boundingRect(contour)                
            if w > 30 and h > 30:
                detected.append(contour)
                
        for contour in detected:
            (x, y, w, h) = cv2.boundingRect(contour)
            
            inside = False
            color = (255,0,0)
            for c in detected:
                (x2, y2, w2, h2) = cv2.boundingRect(c)
                
                if ((x > x2 and x < x2 + w2 and x + w > x2 + w2 and w2 > w) or (x < x2 and x + w > x2 and x + w < x2 + w2 and w2 > w) or (x > x2 and x + w < x2 + w2)) and ((y > y2 and y < y2 + h2 and y + h > y2 + h2 and h2 > h) or (y < y2 and y + h > y2 and y + h < y2 + h2 and h2 > h) or (y > y2 and y + h < y2 + h2)):
                    inside = True
                    break
                
            if not inside:
                p3 = ((x + x + w)/2, (y + y + h)/2)
                middle = Point(p3)
                if middle.x > pLT.x and middle.x < pRB.x and middle.y > pLT.y and middle.y < pRB.y:
                    if len(counted) == 0:
                        counted.append((middle, cframe))
                        counter += 1
                    new = True
                    for k in counted:
                        if abs(middle.x - k[0].x) <= 40 and abs(middle.y - k[0].y) <= 40 and cframe - k[1] < 15:
                            new = False
                
                    if new:        
                       counter += 1
                       counted.append((middle, cframe))

                cv2.rectangle(origframe, (x, y), (x + w, y + h), color, 2) 
                cv2.circle(origframe, ((x + x + w)/2, (y + y + h)/2), 4, (0,0,255), -1)

        text = str(counter)
        cv2.putText(frame, text, (600, 100), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 0, 255), 4)
        image = np.hstack((origframe, fgimg))
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
