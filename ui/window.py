# -*- encoding: utf-8 -*-

import cv2 as cv

__all__ = [ 'WindowManager' ]

# --------------------------------------------------------------------

class WindowManager :

    def __init__(self, windowName, keypressCallback = None):
        self.keypressCallback = keypressCallback
        self._name = windowName
        self._isCreated = False

    @property
    def isCreated(self):
        return self._isCreated

    @property
    def name(self) :
        return self._name

    def createWindow(self):
        cv.namedWindow(self._name)
        self._isCreated = True

    def show(self, frame):
        cv.imshow(self._name, frame)

    def destroyWindow(self):
        cv.destroyWindow(self._name)
        self._isCreated = False

    def processEvents(self):
        keycode = cv.waitKey(1)
        if self.keypressCallback is not None and keycode != -1 :
            # Discard any non-ASCII info encoded by GTK.
            keycode &= 0xFF
            self.keypressCallback(keycode)

# --------------------------------------------------------------------
