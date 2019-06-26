# -*- encoding: utf8 -*-

import sys
import cv2 as cv
import numpy as np
import time

__all__ = [ 'CaptureManager', 'CameraCapture' ]

# ------------------------------------------------------------------------------

class CaptureManager :

    def __init__(self, camera, previewWindowManager = None,
                 shouldMirrorPreview = False) :

        self.previewWindowManager = previewWindowManager
        self.shouldMirrorPreview = shouldMirrorPreview

        self._camera = camera
        self._channel = 0
        self._enteredFrame = False
        self._frame = None
        self._imageFilename = None
        self._videoFilename = None
        self._videoEncoding = None
        self._videoWriter = None

        self.framesElapsed = 0
        self.fpsEstimate = 0

    @property
    def camera(self) :
        return self._camera

    @property
    def width(self) :
        return int(self._camera.get(cv.CAP_PROP_FRAME_WIDTH))

    @width.setter
    def width(self, width) :
        self._camera.set(cv.CAP_PROP_FRAME_WIDTH, width)

    @property
    def height(self) :
        return int(self._camera.get(cv.CAP_PROP_FRAME_HEIGHT))

    @height.setter
    def height(self, height) :
        return self._camera.set(cv.CAP_PROP_FRAME_HEIGHT, height)

    @property
    def fpsAnnounced(self) :
        return self._camera.get(cv.CAP_PROP_FPS)

    def openSettings(self) :
        self._camera.set(cv.CAP_PROP_SETTINGS, 1)

    @property
    def channel(self) :
        return self._channel

    @channel.setter
    def channel(self, value) :
        if self._channel != value :
            self._channel = value
            self._frame = None

    @property
    def frame(self) :
        if self._enteredFrame and self._frame is None :
            _, self._frame = self._camera.retrieve()
        return self._frame

    @property
    def isWritingImage(self) :
        return self._imageFilename is not None

    @property
    def isWritingVideo(self) :
        return self._videoFilename is not None

    def enterFrame(self) :
        """Capture the next frame, if any."""

        # But first, check that any previous frame was exited.
        assert not self._enteredFrame, \
               'previous enterFrame() had no matching exitFrame()'

        # prepare to evaluate fps
        self.ticks_start = cv.getTickCount()

        if self._camera is not None :
            self._enteredFrame = self._camera.grab()

    def exitFrame(self) :
        """Draw to the window. Write to file. Release the frame."""

        # Check whether any grabbed frame is retreivable.
        # The getter may retreive and cache the frame.
        if self.frame is None :
            self._enteredFrame = False
            return

        # Draw to the window, if any
        if self.previewWindowManager is not None :
            if self.shouldMirrorPreview :
                mirroredFrame = np.fliplr(self._frame).copy()
                self.previewWindowManager.show(mirroredFrame)
            else :
                self.previewWindowManager.show(self._frame)
            self.previewWindowManager.processEvents()

        # Update the FPS estimate and related variables.
        self.framesElapsed += 1
        self.fpsEstimate = cv.getTickFrequency() / (cv.getTickCount() - self.ticks_start)

        # Write to the image file, if any.
        if self.isWritingImage :
            cv.imwrite(self._imageFilename, self._frame)
            self._imageFilename = None

        # Write to the video file, if any.
        self._writeVideoFrame()

        # Release the frame.
        self._frame = None
        self._enteredFrame = False
        
    def writeImage(self, filename) :
        """Write the next exited frame to an image file."""
        self._imageFilename = filename

    def startWritingVideo(self, filename, encoding='I420') :
        """Start writing exited frames to a video file."""
        self._videoFilename = filename
        self._videoEncoding = cv.VideoWriter_fourcc(*encoding)

    def stopWritingVideo(self) :
        """Stop writing exited frames to a video file."""
        self._videoFilename = None
        self._videoEncoding = None
        self._videoWriter = None

    def _writeVideoFrame(self) :

        if not self.isWritingVideo :
            return

        if self._videoWriter is None :
            fps = self._camera.get(cv.CAP_PROP_FPS)
            if fps == 0.0 :
                # The capture's FPS is unknown so use an estimate.
                if self.framesElapsed < 20 :
                    # Wait until more frames elapse so that the
                    # estimate is more stable
                    return
                else :
                    fps = self.fpsEstimate

            size = (
                int(self._camera.get(cv.CAP_PROP_FRAME_WIDTH)),
                int(self._camera.get(cv.CAP_PROP_FRAME_HEIGHT))
            )

            self._videoWriter = cv.VideoWriter(
                self._videoFilename,
                self._videoEncoding,
                fps,
                size
            )

        self._videoWriter.write(self._frame)
    
# ------------------------------------------------------------------------------

class CameraCapture(object) :

    def __init__(self, master=None, source=0, windowName='Camera', processor=None, zone=None) :
        self.master = master
        self.source = source
        self.windowName = windowName
        self.processor = processor
        self.zone = zone
        self.camera = None
        self.clicked = False
        self.frameno = 0
        
    @property
    def size(self) :
        try :
            return (
                int(self.camera.get(cv.CAP_PROP_FRAME_WIDTH)),
                int(self.camera.get(cv.CAP_PROP_FRAME_HEIGHT))
            )
        except :
            return (-1, -1)

    @property
    def fps(self) :
        try :
            return self.camera.get(cv.CAP_PROP_FPS)
        except :
            return -1

    def acquire(self) :
        if self.camera is None :
            self.clicked = False
            cv.namedWindow(self.windowName)
            cv.setMouseCallback(self.windowName, self.onMouse)
            api = cv.CAP_ANY
            if sys.platform == 'win32' and isinstance(self.source, int) :
                api = cv.CAP_DSHOW
            self.camera = cv.VideoCapture(self.source, api)

    def release(self) :
        if self.camera is not None :        
            self.camera.release()
            cv.destroyWindow(self.windowName)
            self.camera = None

    def reset_counter(self) :
        self.frameno = 0

    def process_frame(self, frame) :
        if self.zone is not None :
            return self.zone.update(frame)
        if self.processor is not None :
            return self.processor.apply(frame, self)
        return frame

    def run(self) :
        print('start capture, processor={}'.format(self.processor))

        # avoid multiple instance of capture
        if self.camera is not None :
            return
        
        # start capture
        self.acquire()
        tempo = round(1000 / (self.fps if self.fps > 0 else 30.0))

        # capture loop
        self.frameno = 0
        while self.camera is not None :
            # capture frame
            success, frame = self.camera.read()

            # event key code and window state
            keycode = cv.waitKey(tempo)
            wstate = cv.getWindowProperty(self.windowName, 0) 

            # check for loop exit conditions
            if not success or keycode != -1 or self.clicked or wstate == -1 :
                break

            # processing frame
            self.frameno += 1
            frame = self.process_frame(frame)

            # show frame
            cv.imshow(self.windowName, frame)

            # update master ?
            if self.master :
                self.master.update()

        # release capture and close window
        self.release()

    def onMouse(self, event, x, y, flags, param) :
        if event == cv.EVENT_LBUTTONUP :
            self.clicked = True
