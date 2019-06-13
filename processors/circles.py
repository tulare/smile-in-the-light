# -*- encoding: utf8 -*-

import cv2 as cv
import numpy as np
import imutils
import webcolors

from .core import FrameProcessor

__all__ = [ 'CirclesProcessor' ]

# ------------------------------------------------------------------------------

class CirclesProcessor(FrameProcessor) :

    def params(self, **kwargs) :
        self.param1 = kwargs.get('param1', 50)
        self.param2 = kwargs.get('param2', 30)
        self.minRadius = kwargs.get('minRadius', 0)
        self.maxRadius = kwargs.get('maxRadius', 80)
        
    def apply(self, frame, context) :
        frame = imutils.resize(frame, width=min(640, frame.shape[1]))
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        gray = cv.GaussianBlur(gray, (9, 9), 2, 2)
        dim = frame.shape[0]/32
        circles = cv.HoughCircles(
            gray,
            cv.HOUGH_GRADIENT,
            1, dim,
            param1=self.param1,
            param2=self.param2,
            minRadius=self.minRadius,
            maxRadius=self.maxRadius
        )
        
        if circles is not None :
            #print(len(circles[0]))
            for circle in circles[0] :
                #print('-> ', circle)
                drawCircle(frame, circle)

        return frame
        
# ------------------------------------------------------------------------------

def makeColor(name) :
    try :
        coul = webcolors.name_to_rgb(name)
    except ValueError :
        coul = webcolors.name_to_rgb('black')
    return list(reversed(coul))

# ------------------------------------------------------------------------------

def drawCircle(image, circle, center='SaddleBrown', border='AquaMarine') :
    x1, y1, radius = circle
    color_center = makeColor(center)
    color_border = makeColor(border)
    cv.circle(image, (x1, y1), 2, color_center)
    cv.circle(image, (x1, y1), 3, color_center)
    cv.circle(image, (x1, y1), radius, color_border)


