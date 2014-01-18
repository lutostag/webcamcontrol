#!/usr/bin/env python2
"""Useful script that detects movement from a v4l camera and outputs useful
text for controlling music players.

"""
import sys
import cv2
import numpy

WIDTH = 320
HEIGHT = 240
DIFFERENCE = min(WIDTH / 2, HEIGHT / 2) * 0.80


def average(points):
    """Calculate a rough estimate of size and central point of a polygon by
    using a bounding box.

    """
    # yeah I know this is ugly, but it works and there is a better solution
    # when bug http://code.opencv.org/issues/2505 is patched and downstreamed
    if not points:
        return 0, 0, 0

    x_axis = [point[0][0] for point in points]
    y_axis = [point[0][1] for point in points]
    size = (max(x_axis) - min(x_axis)) * (max(y_axis) - min(y_axis))
    x_avg = sum(x_axis) / len(points)
    y_avg = sum(y_axis) / len(points)
    return size, x_avg, y_avg


def process(points):
    """Check the array of points to see if we can find an overall direction of
    the movement. If we can print useful phrases to stdout that can be piped
    into a control script.

    """
    if not points:
        return
    yoffset = 0.0
    xoffset = 0.0
    for index, previous in enumerate(points):
        for leading in points[index+1:]:
            xoffset += leading[0] - previous[0]
            yoffset += leading[1] - previous[1]

    greater, lesser = sorted([abs(xoffset), abs(yoffset)])

    # so now we have the large vector, so lets compare the two components
    if abs(xoffset) > (WIDTH / 2) or abs(yoffset) > (HEIGHT / 2) and \
            greater > (DIFFERENCE + lesser):
        if abs(xoffset) > abs(yoffset):  # x-axis
            if xoffset > 0:  # left
                print("prev")
            else:  # right
                print("next")
        elif abs(yoffset) > abs(xoffset):  # y-axis
            if yoffset > 0:  # down
                print("pause")
            else:  # up
                print("pause")
        sys.stdout.flush()


def main(debug=False):
    """The main routine that continually captures images, does preprocessing
    and then sends them to be processed after a movement has been detected.

    """
    camera = cv2.VideoCapture(0)
    camera.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, WIDTH)
    camera.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, HEIGHT)

    img = cv2.cvtColor(camera.read()[1], cv2.COLOR_RGB2GRAY)
    avg = numpy.float32(img)
    pointlist = []

    while(True):
        # Preprocess
        img = cv2.cvtColor(camera.read()[1], cv2.COLOR_RGB2GRAY)
        img = cv2.medianBlur(img, 3)
        cv2.accumulateWeighted(img, avg, 0.2)
        img = cv2.subtract(cv2.convertScaleAbs(img), cv2.convertScaleAbs(avg))
        _, thrsh = cv2.threshold(img, 15, 255, 0)

        # Find large objects in the image that aren't in the static background
        contours, _ = cv2.findContours(
            thrsh,
            cv2.RETR_LIST,
            cv2.CHAIN_APPROX_NONE
        )

        # If there are large objects, use the largest and add it's central
        # point to the list of points in a motion
        # Otherwise process the previous motion list to see if there was any
        # discernable uni-directional motion
        if contours:
            largest_contour = max([average(contour) for contour in contours])
            if largest_contour[0] > 100:
                pointlist.append(largest_contour[1:])
        else:
            process(pointlist)
            pointlist = []

        if debug:
            cv2.imshow('img', img)
            k = cv2.waitKey(20)

            if k == 27:
                break

    if debug:
        cv2.destroyAllWindows()

    camera.release()


if __name__ == '__main__':
    main()
