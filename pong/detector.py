# -*- encoding: utf-8 -*-

import sys
import logging
import threading
import cv2 as cv
from processors.core import FrameProcessor
from processors.trackers import Tracker

__all_ = [ 'Detector' ]


# ------------------------------------------------------------------------------

class TrackingZone :

    def __init__(self, bbox, algo) :
        """
        Underlying structure for tracking zone
        """
        self.bbox_ini = bbox
        self.bbox = bbox
        self.algo = algo
        self.proc = TrackingProcessor(self.algo)

# ------------------------------------------------------------------------------

class TrackingProcessor(FrameProcessor) :
    """
    Use an opencv Tracking algo to follow context.bbox
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
            self.tracked = self.tracker.init(frame, context.bbox)
            return frame

        # update tracking on following frames
        success, rect = self.tracker.update(frame)
        if success :
            x, y, w, h = (int(v) for v in rect)
            context.bbox = (x, y, w, h)
            cv.rectangle(frame, context.bbox, (0,255,0), 2)
        else :
            cv.rectangle(frame, context.bbox, (0,0,255), 2)
        
        return frame

# ------------------------------------------------------------------------------

class Detector(threading.Thread) :
    """
    Use camera (source) to track moves of the subject into defined zones.
    Typical algorithms (algo) : MOSSE(default), MEDIANFLOW, KCF, CSRT, MIL
    Zones are defined by theses parameters :
    nZones : number of zones
    yZone : top coordinate of each zone
    wZone, hZone : width and height of each zone
    xZone is computed by spacing zones equaly in the x direction.
    """

    def __init__(self, source, width, height, algo, nZones=3, yZone=100, wZone=100, hZone=320) :

        # init threading.Thread
        super().__init__(name='DetectorThread', daemon=True)

        # api for capture (use CAP_DSHOW on windows)
        api = cv.CAP_ANY
        if isinstance(source, int) and sys.platform == 'win32' :
            api = cv.CAP_DSHOW

        # init camera capture
        self.cam = cv.VideoCapture(source, api)
        self.width = width
        self.height = height
        # to do : verify size

        # fps and frameno
        self.fps = 0
        self.frameno = 0

        # algo
        self._algo = algo

        # ready event
        self.ready = threading.Event()

        # zones for detection
        self.nZones = nZones
        self.yZone, self.wZone, self.hZone = yZone, wZone, hZone
        self.zones = []

    def init_zones(self) :
        """
        Prepare initial zones for detection
        caution : call after setting camera size
        """
        for zone in range(self.nZones) :
            xZone = int(
                zone * self.width // self.nZones
                + self.width // (2*self.nZones)
                - self.wZone // 2
            )
            self.zones.append(
                TrackingZone(
                    bbox=(xZone, self.yZone, self.wZone, self.hZone),
                    algo=self.algo
                )
            )
            logging.debug('init_zones : TrackingZone #%s', zone)

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
        return self._algo

    def center_x(self, index) :
        """
        center_x coordinate of the zones[index].bbox center
        """
        cx = 0
        try :
            cx = self.zones[index].bbox[0] + self.zones[index].bbox[1] // 2
        except IndexError :
            logging.debug('center_x : bad index %d', index)

        return int(cx)

    def delta_x(self, index) :
        """
        delta_x coordinate between zones[index].bbox_ini and zones[index].bbox
        """
        dx = 0
        try :
            icx = self.zones[index].bbox_ini[0] + self.zones[index].bbox_ini[1] // 2
            dx = self.center_x(index) - icx
        except IndexError :
            logging.debug('delta_x : bad index %d', index)

        return int(dx)

    def center_y(self, index) :
        """
        y coordinate of the zones[index].bbox center
        """
        cy = 0
        try :
            cy = self.zones[index].bbox[1] + self.zones[index].bbox[3] // 2
        except IndexError :
            logging.debug('center_y : bad index %d', index)

        return int(cy)

    def delta_y(self, index) :
        """
        delta_y coordinate between zones[index].bbox_ini and zones[index].bbox
        """
        dy = 0
        try :
            iy = self.zones[index].bbox_ini[1] + self.zones[index].bbox_ini[3] // 2
            dy = self.center_y(index) - iy
        except IndexError :
            logging.debug('delta_y : bad index %d', index)
            
        return int(dy)

    def run(self) :
        """
        Run the mainloop for camera capture and processing
        """

        # prepare zones
        self.init_zones()
        
        # prepare the preview
        cv.namedWindow(self.name)

        while True :
            t1 = cv.getTickCount()

            # grab a new frame
            ok, frame = self.cam.read()
            self.frameno += 1

            # check frame validity
            if frame is None :
                logging.debug('no more frame')
                break

            # event
            if self.frameno == 30 :
                logging.debug('trigger ready event')
                self.ready.set()

            # horizontal mirror
            frame[:,::-1,:] = frame

            # process the frame
            for zone in self.zones :
                frame = zone.proc.apply(frame, zone)

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
            org=(16, 16),
            fontFace=cv.FONT_HERSHEY_SIMPLEX, fontScale=0.5,
            color=(0, 0, 0),
            thickness=1
        )    
        cv.putText(
            frame,
            text=text_info,
            org=(15, 15),
            fontFace=cv.FONT_HERSHEY_SIMPLEX, fontScale=0.5,
            color=(0, 215, 255),
            thickness=1
        )
        for n in range(len(self.zones)) :
            text_info = '#{} : {:4d},{:4d}'.format(
                n, self.delta_x(n), self.delta_y(n)
            )
            cv.putText(
                frame,
                text=text_info,
                org=(16, 16+16*(n+1)),
                fontFace=cv.FONT_HERSHEY_SIMPLEX, fontScale=0.5,
                color=(0, 0, 0),
                thickness=1
            )    
            cv.putText(
                frame,
                text=text_info,
                org=(15, 15+16*(n+1)),
                fontFace=cv.FONT_HERSHEY_SIMPLEX, fontScale=0.5,
                color=(60, 200, 60),
                thickness=1
            )


    def terminate(self) :
        """
        Terminate camera capture
        """
        logging.debug('terminate capture')
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
