# -*- encoding: utf-8 -*-

import sys
import time
import cv2 as cv
import numpy as np

from ui.window import WindowManager
from ui.capture import CaptureManager
from processors import filters

class Camera :

    def __init__(self, source) :

        # api
        self.api = cv.CAP_ANY

        # source
        self.source = source
        self.iscam = False
        if source.isdigit() :
            self.source = int(source)
            self.iscam = True
            if sys.platform == 'win32' :
                # adapt api on windows
                self.api = cv.CAP_DSHOW

        self.preview = WindowManager('preview', self.onKeypress)
        self.capture = CaptureManager(
            cv.VideoCapture(self.source, self.api),
            self.preview
        )

        self.capture.width = 640
        self.capture.height = 480
        self.h_mirror = False
        self.v_mirror = False

        if self.capture.fpsAnnounced > 0 :
            self.preview.waitKeyDelay = int(1000.0 / self.capture.fpsAnnounced)

    def run(self) :
        self.preview.createWindow()

        while True :
            # enter frame
            self.capture.enterFrame()
            frame = self.capture.frame

            if frame is None :
                break
            
            # process frame
            # ex : horizontal mirror
            if self.h_mirror :
                frame[:,::-1,:] = frame
            # ex : vertical mirror
            if self.v_mirror :
                frame[::-1,:,:] = frame

            # display infos
            self.display_infos(frame)
            
            # exit frame
            self.capture.exitFrame()

        self.preview.destroyWindow()

    def display_infos(self, frame) :
        info_text = """{}x{} {:2.0f}fps [{:2.0f}fps] {}{} {}ms - {:4d} frames""".format(
            self.capture.width, self.capture.height,
            self.capture.fpsEstimate,
            self.capture.fpsAnnounced,
            'H' if self.h_mirror else 'h',
            'V' if self.v_mirror else 'v',
            self.preview.waitKeyDelay,
            self.capture.framesElapsed,
        )
        cv.putText(
            frame,
            text=info_text,
            org=(15, 15),
            fontFace=cv.FONT_HERSHEY_SIMPLEX, fontScale=0.5,
            color=(0, 0, 0),
            thickness=1
        )
        cv.putText(
            frame,
            text=info_text,
            org=(14, 14),
            fontFace=cv.FONT_HERSHEY_SIMPLEX, fontScale=0.5,
            color=(0, 215, 255),
            thickness=1
        )

    def onKeypress(self, keycode) :
        """
        keypress manager
        """
        if keycode == 27 or keycode == ord('q'):
            self.capture.camera.release()
        elif keycode == ord('i') :
            self.capture.openSettings()
        elif keycode == ord('h') :
            self.h_mirror = not self.h_mirror
        elif keycode == ord('v') :
            self.v_mirror = not self.v_mirror
        elif keycode == ord('1') :
            self.capture.width = 320
            self.capture.height = 240
        elif keycode == ord('2') :
            self.capture.width = 640
            self.capture.height = 480
        elif keycode == ord('+') :
            self.preview.waitKeyDelay += 1
        elif keycode == ord('-') :
            self.preview.waitKeyDelay -= 1
            if self.preview.waitKeyDelay < 1 :
                self.preview.waitKeyDelay = 1
            
            

if __name__ == '__main__' :
    source = ''.join(sys.argv[1:2])
    if not source :
        source = '0'
    Camera(source).run()

