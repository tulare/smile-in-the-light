# -*- encoding: utf-8 -*-

import cv2 as cv
import numpy as np

from .core import FrameProcessor

__all__ = [ 'FramecountProcessor' ]

# ------------------------------------------------------------------------------

class FramecountProcessor(FrameProcessor) :

    def params(self, **kwargs) :
        pass

    def apply(self, frame, context) :
        cv.rectangle(frame, (10, 2), (100,20), (255,255,255), -1)
        cv.putText(frame, '{} [{}]'.format(context.fps, context.frameno), (15, 15),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0))
        
        return frame

# ------------------------------------------------------------------------------
