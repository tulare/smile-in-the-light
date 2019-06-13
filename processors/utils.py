# -*- encoding: utf-8 -*-

import cv2
import numpy as np
import scipy.interpolate


class Histogram1D :

    def __init__(self) :
        self.histSize = [256,]
        self.hranges = [0.0, 256.0]
        self.ranges = self.hranges
        self.channels = list(range(1))

    def getHistogram(self, image) :
        if isGray(image) :
            gray = image
        else :
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.calcHist(
            [gray],
            self.channels,
            None,
            self.histSize,
            self.ranges
        )

    def getHistogramImage(self, image) :

        bins = np.arange(self.histSize[0]).reshape(self.histSize[0], 1)
        hpoint = np.int32(0.90 * self.histSize[0])

        histo = self.getHistogram(image)
        cv2.normalize(histo, histo, 0, hpoint, cv2.NORM_MINMAX)
        histo = np.int32(np.around(histo))
        pts = np.column_stack((bins, 255 - histo))
        pts = np.vstack((pts, [0, 255]))

        imgHisto = np.full(
            (self.histSize[0], self.histSize[0]),
            255,
            dtype=np.uint8
        )
        cv2.fillPoly(imgHisto, [pts], 128)
        cv2.polylines(imgHisto, [pts], False, 0)
        
        return imgHisto


class HistogramBGR :

    def __init__(self) :
        self.histSize = [256,] * 3
        self.b_ranges = [0.0, 256.0]
        self.g_ranges = [0.0, 256.0]
        self.r_ranges = [0.0, 256.0]
        self.ranges = self.b_ranges + self.g_ranges + self.r_ranges
        self.channels = list(range(3))

    def getHistogram(self, image) :
        return cv2.calcHist(
            [image],
            self.channels,
            None,
            self.histSize,
            self.ranges
        )
        

class HistogramHSV :

    def __init__(self) :
        self.histSize = [180, 256, 256]
        self.hranges = [0.0, 180.0]
        self.sranges = [0.0, 256.0]
        self.vranges = [0.0, 256.0]
        self.ranges = self.hranges + self.sranges + self.vranges
        self.channels = list(range(3))

    def getHistogramHS(self, image) :
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        return cv2.calcHist(
            [hsv_image],
            self.channels[:2],
            None,
            self.histSize[:2],
            self.ranges[:4]
        )

    def getHistogramH(self, image) :
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        return cv2.calcHist(
            [hsv_image],
            self.channels[:1],
            None,
            self.histSize[:1],
            self.ranges[:2]
        )

    def getHistogramS(self, image) :
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        return cv2.calcHist(
            [hsv_image],
            self.channels[1:2],
            None,
            self.histSize[1:2],
            self.ranges[2:4]
        )
        
    def getHistogramV(self, image) :
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        return cv2.calcHist(
            [hsv_image],
            self.channels[2:],
            None,
            self.histSize[2:],
            self.ranges[4:]
        )


def createCurveFunc(points):
    """Return a function derived from control points."""

    if points is None:
        return None

    numPoints = len(points)
    if numPoints < 2 :
        return None

    xs, ys = zip(*points)
    if numPoints < 3 :
        kind = 'linear'
    elif numPoints < 4 :
        kind = 'quadratic'
    else:
        kind = 'cubic'

    return scipy.interpolate.interp1d(xs, ys, kind,
                                      bounds_error = False)

def createLookupArray(func, length = 256):
    """Return a lookup for whole-number inputs to a function.

    The lookup values are clamped to [0, length - 1].
    """

    if func is None:
        return None

    lookupArray = np.empty(length)
    i = 0
    while i < length:
        func_i = func(i)
        lookupArray[i] = min(max(0, func_i), length - 1)
        i += 1

    return lookupArray


def applyLookupArray(lookupArray, src, dst):
    """Map a source to a destination using a lookup."""

    if lookupArray is None:
        return
    dst[:] = lookupArray[src]


def createCompositeFunc(func0, func1):
    """Return a composite of two functions."""

    if func0 is None:
        return func1
    if func1 is None:
        return func0

    return lambda x: func0(func1(x))


def createFlatView(array):
    """Return a 1D view of an array of any dimensionality."""

    flatView = array.view()
    flatView.shape = array.size

    return flatView


def isGray(image):
    """Return True if the image has one channel per pixel."""

    return image.ndim < 3


def widthHeightDividedBy(image, divisor):
    """Return an image's dimensions, divided by a value."""

    h, w = image.shape[:2]
    return (w//divisor, h//divisor)

