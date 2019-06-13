# -*- encoding: utf8 -*-

import cv2 as cv
import numpy as np
import imutils

from .core import FrameProcessor

__all__ = [ 'LinesProcessor' ]

# ------------------------------------------------------------------------------

class LinesProcessor(FrameProcessor) :

    def params(self, **kwargs) :
        self.minLineLength = kwargs.get('minLineLength', 10)
        self.maxLineGap = kwargs.get('maxLineGap', 3)
        
    def apply(self, frame, context) :
        frame = imutils.resize(frame, width=min(640, frame.shape[1]))

        contours = imutils.auto_canny(frame)
        lines = cv.HoughLinesP(
            contours, 1, np.pi/180, 80,
            minLineLength=self.minLineLength,
            maxLineGap=self.maxLineGap,
        )

        if lines is not None :
            for x1,y1,x2,y2 in lines[:,0] :
                cv.line(frame, (x1,y1), (x2,y2), (0, 255, 0))

        return frame

# ------------------------------------------------------------------------------
