# -*- encoding: utf-8 -*-

import cv2
import numpy
import time

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
        self.frameCounter = 0
        self.timeBegin = time.time()
        self.tick = 0
        self.fpsEstimate = 0

    @property
    def camera(self) :
        return self._camera

    @property
    def width(self) :
        return int(self._camera.get(cv2.CAP_PROP_FRAME_WIDTH))

    @width.setter
    def width(self, width) :
        self._camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)

    @property
    def height(self) :
        return int(self._camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

    @height.setter
    def height(self, height) :
        return self._camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def openSettings(self) :
        self._camera.set(cv2.CAP_PROP_SETTINGS, 1)

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

        if self._camera is not None :
            self._enteredFrame = self._camera.grab()

    def exitFrame(self) :
        """Draw to the window. Write to file. Release the frame."""

        # Check whether any grabbed frame is retreivable.
        # The getter may retreive and cache the frame.
        if self.frame is None :
            self._enteredFrame = False
            return

        # Update the FPS estimate and related variables.
        self.updateFPS()

        # Draw to the window, if any
        if self.previewWindowManager is not None :
            if self.shouldMirrorPreview :
                mirroredFrame = numpy.fliplr(self._frame).copy()
                self.previewWindowManager.show(mirroredFrame)
            else :
                self.previewWindowManager.show(self._frame)

        # Write to the image file, if any.
        if self.isWritingImage :
            cv2.imwrite(self._imageFilename, self._frame)
            self._imageFilename = None

        # Write to the video file, if any.
        self._writeVideoFrame()

        # Release the frame.
        self._frame = None
        self._enteredFrame = False

    def updateFPS(self) :
        # Update the FPS estimate and related variables.
        self.frameCounter += 1
        self.framesElapsed += 1
        timeNow = time.time() - self.timeBegin
        if timeNow - self.tick >= 1 :
            self.tick += 1
            self.fpsEstimate = self.frameCounter
            self.frameCounter = 0
        
    def writeImage(self, filename) :
        """Write the next exited frame to an image file."""
        self._imageFilename = filename

    def startWritingVideo(self, filename, encoding='I420') :
        """Start writing exited frames to a video file."""
        self._videoFilename = filename
        self._videoEncoding = cv2.VideoWriter_fourcc(*encoding)

    def stopWritingVideo(self) :
        """Stop writing exited frames to a video file."""
        self._videoFilename = None
        self._videoEncoding = None
        self._videoWriter = None

    def _writeVideoFrame(self) :

        if not self.isWritingVideo :
            return

        if self._videoWriter is None :
            fps = self._camera.get(cv2.CAP_PROP_FPS)
            if fps == 0.0 :
                # The capture's FPS is unknown so use an estimate.
                if self.framesElapsed < 20 :
                    # Wait until more frames elapse so that the
                    # estimate is more stable
                    return
                else :
                    fps = self.fpsEstimate

            size = (
                int(self._camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(self._camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            )

            self._videoWriter = cv2.VideoWriter(
                self._videoFilename,
                self._videoEncoding,
                fps,
                size
            )

        self._videoWriter.write(self._frame)
    

class WindowManager :
    def __init__(self, windowName, keypressCallback = None):
        self.keypressCallback = keypressCallback
        self._windowName = windowName
        self._isWindowCreated = False

    @property
    def isWindowCreated(self):
        return self._isWindowCreated

    def createWindow (self):
        cv2.namedWindow(self._windowName)
        self._isWindowCreated = True

    def show(self, frame):
        cv2.imshow(self._windowName, frame)

    def destroyWindow (self):
        cv2.destroyWindow(self._windowName)
        self._isWindowCreated = False

    def processEvents (self):
        keycode = cv2.waitKey(1)
        if self.keypressCallback is not None and keycode != -1:
            # Discard any non-ASCII info encoded by GTK.
            keycode &= 0xFF
            self.keypressCallback(keycode)
