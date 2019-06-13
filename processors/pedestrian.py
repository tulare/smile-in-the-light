# -*- encoding: utf8 -*-

import cv2 as cv
import numpy as np
import imutils
from imutils.object_detection import non_max_suppression

from .core import FrameProcessor

__all__ = [ 'PedestrianProcessor' ]

# ------------------------------------------------------------------------------

class PedestrianProcessor(FrameProcessor) :

    def __init__(self) :
        self.hog = cv.HOGDescriptor()
        self.hog.setSVMDetector(cv.HOGDescriptor_getDefaultPeopleDetector())
        super().__init__()

    def params(self, **kwargs) :
        self.winStride = kwargs.get('winStride', (4, 4))
        self.padding = kwargs.get('padding', (8, 8))
        self.scale = kwargs.get('scale', 1.05)
        self.meanShift = kwargs.get('meanShift', False)
        
    def apply(self, frame, context) :
        frame = imutils.resize(frame, width=min(640, frame.shape[1]))

        (rects, weights) = self.hog.detectMultiScale(
            frame,
            winStride=self.winStride,
            padding=self.padding,
            scale=self.scale,
            useMeanshiftGrouping=self.meanShift
        )

        for (x, y, w, h) in rects :
            cv.rectangle(frame, (x,y), (x+w, y+h), (0, 0, 255), 2)

        rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
        pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)

        for (xA, yA, xB, yB) in pick :
            cv.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)

        return frame
        
# ------------------------------------------------------------------------------
