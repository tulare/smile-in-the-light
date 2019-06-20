# -*- encoding: utf-8 -*-

import sys
import threading
import cv2 as cv
from processors.core import FrameProcessor
from processors.trackers import Tracker

__all_ = [ 'Detector' ]

# ------------------------------------------------------------------------------

class TrackingProcessor(FrameProcessor) :
    """
    Use an opencv Tracking algo to follow context.rect
    """

    def __init__(self, algo) :
        self.algo = algo
        self.tracker = None
        self.tracked = False
        super().__init__()

    def params(self, **kwargs) :
        self.tracker = Tracker.create(self.algo)
        
    def apply(self, frame, context) :
        # init tracking on first frames
        if not self.tracked :
            self.tracked = self.tracker.init(frame, context.rect)
            return frame

        # update tracking on following frames
        success, rect = self.tracker.update(frame)
        if success :
            x, y, w, h = (int(v) for v in rect)
            context.rect = (x, y, w, h)
            cv.rectangle(frame, context.rect, (0,255,0), 2)
        else :
            cv.rectangle(frame, context.rect, (0,0,255), 2)
        
        return frame

# ------------------------------------------------------------------------------

class Detector(threading.Thread) :
    """
    Use camera (source) to track moves of the subject into the bounding box (bbox).
    Typical algorithms (algo) : MOSSE(default), MEDIANFLOW, KCF, CSRT, MIL
    """

    def __init__(self, source, algo, bbox) :

        # init threading.Thread
        super().__init__(name='DetectorThread', daemon=True)

        # api for capture (use CAP_DSHOW on windows)
        api = cv.CAP_ANY
        if isinstance(source, int) and sys.platform == 'win32' :
            api = cv.CAP_DSHOW

        # init camera capture
        self.cam = cv.VideoCapture(source, api)

        # fps and frameno
        self.fps = 0
        self.frameno = 0

        # initial rect for detection
        self.rect = bbox

        # processor
        self.proc = TrackingProcessor(algo)

    @property
    def width(self) :
        return self.cam.get(cv.CAP_PROP_FRAME_WIDTH)

    @width.setter
    def width(self, value) :
        self.cam.set(cv.CAP_PROP_FRAME_WIDTH, value)

    @property
    def height(self) :
        return self.cam.get(cv.CAP_PROP_FRAME_HEIGHT)

    @height.setter
    def height(self, value) :
        self.cam.set(cv.CAP_PROP_FRAME_HEIGHT, value)

    @property
    def algo(self) :
        return self.proc.algo

    @property
    def center_x(self) :
        """
        x coordinate of the self.rect center
        """
        return self.rect[0] + self.rect[1] // 2

    @property
    def center_y(self) :
        """
        y coordinate of the self.rect center
        """
        return self.rect[1] + self.rect[3] // 2

    def run(self) :
        """
        Run the mainloop for camera capture and processing
        """
        # prepare the preview
        cv.namedWindow(self.name)

        while True :
            t1 = cv.getTickCount()

            # grab a new frame
            ok, frame = self.cam.read()
            self.frameno += 1

            # check frame validity
            if frame is None :
                break

            # horizontal mirror
            frame[:,::-1,:] = frame

            # process the frame
            frame = self.proc.apply(frame, self)

            # add onscreen feedback
            self.display_infos(frame)

            # display the frame
            cv.imshow(self.name, frame)

            # update fps
            self.fps = cv.getTickFrequency() / (cv.getTickCount() - t1)

            # process events
            self.processEvents()

        # close the preview
        cv.destroyWindow(self.name)

    def display_infos(self, frame) :
        text_info = '{} {:.0f}x{:.0f} @{:.0f}fps - {:4d}'.format(
            self.algo,
            self.width, self.height,
            self.fps,
            self.frameno,
        )            
        cv.putText(
            frame,
            text=text_info,
            org=(15, 15),
            fontFace=cv.FONT_HERSHEY_SIMPLEX, fontScale=0.5,
            color=(0, 0, 0),
            thickness=1
        )    
        cv.putText(
            frame,
            text=text_info,
            org=(14, 14),
            fontFace=cv.FONT_HERSHEY_SIMPLEX, fontScale=0.5,
            color=(0, 215, 255),
            thickness=1
        )    

    def terminate(self) :
        """
        Terminate camera capture
        """
        self.cam.release()

    def processEvents(self) :
        """
        Manage key events
        """
        keycode = cv.waitKey(1)
        if keycode == ord('q') :
            self.terminate()
        elif keycode == ord('i') :
            self.cam.set(cv.CAP_PROP_SETTINGS, True)
