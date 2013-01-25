import sys
import cv2
import math
import numpy as np

#these are the main sources of information that I squeezed into this program:
#http://www.steinm.com/blog/motion-detection-webcam-python-opencv-differential-images/
#http://derek.simkowiak.net/motion-tracking-with-python/
#http://stackoverflow.com/questions/3374828/how-do-i-track-motion-using-opencv-in-python
#http://opencvpython.blogspot.com/2012/07/background-extraction-using-running.html
#http://stackoverflow.com/questions/9013703/how-to-find-the-location-of-red-region-in-an-image-using-matlab/

def average(a):
    #yeah I know this is ugly, but it works and there is a much better solution
    #when bug http://code.opencv.org/issues/2505 is patched and sent downstream
    x, y = 0, 0
    maxx = -1
    minx = -1
    maxy = -1
    miny = -1
    for i in a:
        if i[0][0] < minx or minx == -1:
            minx = i[0][0]
        if i[0][0] > maxx:
            maxx = i[0][0]
        if i[0][1] < miny or miny == -1:
            miny = i[0][1]
        if i[0][1] > maxy:
            maxy = i[0][1]
        
        x += i[0][0]
        y += i[0][1]

    size = (maxx - minx)*(maxy - miny)
    x = x/len(a)
    y = y/len(a)
    return size, x, y

def process(points):
    entries = len(points)
    if entries == 0:
        return
    yoffset = 0.0
    xoffset = 0.0
    for i in range(0,entries):
        for j in range(i+1,entries):
            yoffset += points[j][1] - points[i][1]
            xoffset += points[j][0] - points[i][0]
    
    #so now we have the large vector, so lets compare the two components
    if abs(xoffset) > 160 or abs(yoffset) > 120:
        #print xoffset,yoffset
        if abs(xoffset) > 100+abs(yoffset):
            if xoffset > 0:
                #left
                print "prev"
            else:
                #right
                print "next"
        if abs(yoffset) > 100+abs(xoffset):
            if yoffset > 0:
                #down
                print "pause"
            else:
                #up
                print "pause"
        sys.stdout.flush()



c = cv2.VideoCapture(0)
c.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 320)
c.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 240)

img = cv2.cvtColor(c.read()[1], cv2.COLOR_RGB2GRAY)

avg = np.float32(img)

pointlist = []

while(1):
    img = cv2.cvtColor(c.read()[1], cv2.COLOR_RGB2GRAY)
    
    img = cv2.medianBlur(img, 3)

    cv2.accumulateWeighted(img, avg, 0.2)
    
    img = cv2.subtract(cv2.convertScaleAbs(img),cv2.convertScaleAbs(avg))
    _, thrsh = cv2.threshold(img,15,255,0)
    
    contours, _ = cv2.findContours(thrsh, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    maxarea = 0
    realx = -1
    realy = -1

    for i in contours:
        area, x, y = average(i)
        if area > maxarea and area > 100:
            maxarea = area
            realx = x
            realy = y
    
    if realx == -1 and realy == -1:
        process(pointlist)
        pointlist = []
    else:
        pointlist.append((realx,realy))
    
    #cv2.imshow('img',img)
    #k = cv2.waitKey(20)

    #if k == 27:
    #    break

#cv2.destroyAllWindows()
c.release()
