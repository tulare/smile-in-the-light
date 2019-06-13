# -*- encoding: utf8 -*-

import cv2 as cv
import numpy as np

from .core import FrameProcessor

__all__ = [ 'BackgroundSubtractor' ]

# ------------------------------------------------------------------------------

OPENCV_BACKSUB_ALGOS = {
    'MOG2' : cv.createBackgroundSubtractorMOG2,
    'KNN' : cv.createBackgroundSubtractorKNN,
}

# ------------------------------------------------------------------------------

class BackSubProcessor(FrameProcessor) :

    def params(self, **kwargs) :
        algo = kwargs.get('algo', 'MOG2')
        try :
            self.backsub = OPENCV_BACKSUB_ALGOS[algo]()
        except KeyError :
            self.backsub = OPENCV_BACKSUB_ALGOS['KNN']()

    def apply(self, frame, context) :
        fgmask = self.backsub.apply(frame)
        frame = cv.bitwise_and(frame, frame, mask=fgmask)
        return frame
        
# ------------------------------------------------------------------------------

