# -*- encoding: utf8 -*-

import cv2 as cv
import numpy as np
import imutils
from imutils.object_detection import non_max_suppression

from .core import FrameProcessor

__all__ = [
    'TrackingProcessor', 'StickingProcessor',
    'MeanShiftTrackingProcessor', 'CamShiftTrackingProcessor'
]

# ------------------------------------------------------------------------------

class TrackingProcessor(FrameProcessor) :

    def params(self, **kwargs) :
        #self.tracker = cv.TrackerMOSSE_create()
        self.tracker = cv.TrackerCSRT_create()
        
    def apply(self, frame, context) :
        if context.frameno == 1 :
            roi = cv.selectROI('Select Roi', frame)
            cv.destroyWindow('Select Roi')
            print('roi', roi)
            ok = self.tracker.init(frame, roi)
            return frame

        success, rect = self.tracker.update(frame)
        if success :
            x, y, w, h = (int(v) for v in rect)
            cv.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)
        
        return frame
        
# ------------------------------------------------------------------------------

class StickingProcessor(FrameProcessor) :

    def params(self, **kwargs) :
        self.tracking = False
        self.hog = cv.HOGDescriptor()
        self.hog.setSVMDetector(cv.HOGDescriptor_getDefaultPeopleDetector())
        self.winStride = kwargs.get('winStride', (4, 4))
        self.padding = kwargs.get('padding', (8, 8))
        self.scale = kwargs.get('scale', 1.05)
        self.meanShift = kwargs.get('meanShift', False)
                
    def apply(self, frame, context) :
        if not self.tracking :
            self.tracker = cv.TrackerMOSSE_create()
            
            #roi = cv.selectROI('Select Roi', frame)
            #cv.destroyWindow('Select Roi')
            #print('roi', roi)

            rects, weights = self.hog.detectMultiScale(
                frame,
                winStride=self.winStride,
                padding=self.padding,
                scale=self.scale,
                useMeanshiftGrouping=self.meanShift
            )

            for x, y, w, h in rects :
                cv.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 1)
            
            for rect, weight in zip(rects, weights) :
                # pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)
                x, y, w, h = rect
                roi = x, y, w, h

                if weight >= 0.85 :
                    print('tracking', roi, weight)
                    self.tracking = self.tracker.init(frame, roi)
                    break
                
            return frame

        self.tracking, rect = self.tracker.update(frame)
        if self.tracking :
            x, y, w, h = (int(v) for v in rect)
            cv.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)
        
        return frame
        
# ------------------------------------------------------------------------------

class MeanShiftTrackingProcessor(FrameProcessor) :

    def params(self, **kwargs) :
        self.term_crit = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 1)

    def apply(self, frame, context) :
        if context.frameno == 1 :
            self.track_window = cv.selectROI('Select ROI', frame)
            cv.destroyWindow('Select ROI')
            x, y, w, h = self.track_window
            self.roi_hist = calc_hist(frame[y:y+h, x:x+w])
            return frame

        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        dst = cv.calcBackProject([hsv], [0], self.roi_hist, [0, 180], 1)
        ret, self.track_window = cv.meanShift(dst, self.track_window, self.term_crit)
        x, y, w, h = self.track_window
        cv.rectangle(frame, (x, y), (x+w, y+h), 255, 2)

        return frame

# ------------------------------------------------------------------------------

class CamShiftTrackingProcessor(FrameProcessor) :

    def params(self, **kwargs) :
        self.term_crit = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 1)

    def apply(self, frame, context) :
        if context.frameno == 1 :
            self.track_window = cv.selectROI('Select ROI', frame)
            cv.destroyWindow('Select ROI')
            x, y, w, h = self.track_window
            self.roi_hist = calc_hist(frame[y:y+h, x:x+w])
            return frame

        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        dst = cv.calcBackProject([hsv], [0], self.roi_hist, [0, 180], 1)
        ret, self.track_window = cv.CamShift(dst, self.track_window, self.term_crit)
        pts = cv.boxPoints(ret)
        pts = np.int0(pts)
        frame = cv.polylines(frame, [pts], True, 255, 2)

        return frame

# ------------------------------------------------------------------------------

def calc_hist(img) :
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    mask = cv.inRange(hsv, np.array((0., 60., 32.)), np.array((180., 255., 255.)))
    hist = cv.calcHist([hsv], [0], mask, [180], [0, 180])
    cv.normalize(hist, hist, 0, 255, cv.NORM_MINMAX)
    return hist
