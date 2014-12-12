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
    #fgbg = cv2.BackgroundSubtractorMOG2(history, 16, False)


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
    #cv2.setWindowProperty("App", cv2.WND_PROP_FULLSCREEN, cv2.cv.CV_WINDOW_FULLSCREEN)

    cv2.createTrackbar('history', 'App', history, 1000, setHistory)
    cv2.createTrackbar('nmixtures', 'App', nmixtures, 10, setNmixtures)
    cv2.createTrackbar('backgroundRatio', 'App', 6, 100, setBackgroundRatio)
    cv2.createTrackbar('noiseSigma', 'App', 1, 100, setNoiseSigma)
    cv2.createTrackbar('alpha', 'App', 1, 100, setAlpha)

    kernel = np.ones((3, 3), np.uint8)
    fgbg = cv2.BackgroundSubtractorMOG(history, nmixtures, backgroundRatio, noiseSigma)
    #fgbg = cv2.BackgroundSubtractorMOG2(history, 16, True)

    cap = cv2.VideoCapture(filename)
    cap.read()

    play()



def play():
    counter = 0
    while(True):
        ret, frame = cap.read()
        if ret == False:
            break
        
        origframe = frame
        

        #(rows, cols, a) = frame.shape

        #M = cv2.getRotationMatrix2D((cols/2,rows/2),-90,1)
        #frame = cv2.warpAffine(frame,M,(cols,rows))
        #cv2.equalizeHist(frame, frame)
        red = frame[:,:,2]
        green = frame[:,:,1]
        blue = frame[:,:,0]
        

        
        #frame = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
        #frame = source
        #cv2.equalizeHist(source, source)
        #frame = red
        #frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

        
        fgmask = fgbg.apply(frame, None, alpha)
        #fgmask = cv2.erode(fgmask, kernel, iterations=20)
        thresh, fgmask = cv2.threshold(fgmask, 250, 255, cv2.THRESH_BINARY)

        fgmask = cv2.dilate(fgmask, kernel, iterations=4)


        fgimg = cv2.cvtColor(fgmask, cv2.COLOR_GRAY2BGR)
        #fgimg = fgmask

        #fgmask = cv2.dilate(fgmask, kernel, iterations=1)
        #fgmask = cv2.erode(fgmask, kernel, iterations=1)
    
        contours, hierarchy = cv2.findContours(fgmask, cv2.cv.CV_RETR_EXTERNAL, cv2.cv.CV_CHAIN_APPROX_SIMPLE)
        #cv2.drawContours(frame, contours, -1, cv2.cv.Scalar(0, 0, 255), 2)
        p1 = (40, 680)
        p2 = (1240, 700)
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
                #if (x > x2 and y > y2 and x + w < x2 + w2 and y + h < y2 + h2):
                #    inside = True
                #    color = (255,0,0)
                #    break
                
                
                
                if ((x > x2 and x < x2 + w2 and x + w > x2 + w2 and w2 > w) or (x < x2 and x + w > x2 and x + w < x2 + w2 and w2 > w) or (x > x2 and x + w < x2 + w2)) and ((y > y2 and y < y2 + h2 and y + h > y2 + h2 and h2 > h) or (y < y2 and y + h > y2 and y + h < y2 + h2 and h2 > h) or (y > y2 and y + h < y2 + h2)):
                    inside = True
                    #color = (0,0,255)
                    break
                
                
            if not inside:
                point = (x + x + w)/2, (y + y + h)/2
                if point[0] > p1[0] and point[0] < p2[0] and point[1] > p1[1] and point[1] < p2[1]:
                    counter += 1
                cv2.rectangle(origframe, (x, y), (x + w, y + h), color, 2) 
                cv2.circle(origframe, ((x + x + w)/2, (y + y + h)/2), 4, (0,0,255), -1)

                
                
        #cv2.line(frame, (40, 680), (1240, 680), (0, 255, 0), 10)

        #final = []
        #for contour in detected:
       #     (x, y, w, h) = cv2.boundingRect(contour)
      #      for c in detected:
     #           (x2, y2, w2, h2) = cv2.boundingRect(c)
    #            if x == x2 and y == y2 and w == w2 and h == h2:
   #                 continue
  #              if (x >= x2 and x <= x2 + w2) or (y >= y2 and y <= y2 + h2):
 #                   final.append((min(x, x2), min(y, y2), max(w, w2), max(h,h2)))
#
        #    cv2.rectangle(origframe, (x, y), (x + w, y + h), (0, 255, 0), 2) 


        #for (x, y, w, h) in final:
        #    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2) 
        #    cv2.circle(frame, ((x + x + w)/2, (y + y + h)/2), 4, (0, 0, 255), -1)


        text = str(counter)
        cv2.putText(frame, text, (600, 100), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 0, 255), 4)
        image = np.hstack((origframe, fgimg))
        cv2.imshow('App', image) 
        #cv2.imshow('App', origframe) 

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
