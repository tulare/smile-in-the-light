# -*- encoding: utf-8 -*-

import sys
import cv2 as cv
import numpy

from ui.capture import CaptureManager
from ui.window import WindowManager
from processors import filters

class Cameo :

    def __init__(self, source=0) :
        if isinstance(source, int) :
            camera = cv.VideoCapture(source, cv.CAP_DSHOW)
        else :
            camera = cv.VideoCapture(source)        
        self.win = WindowManager('Cameo', self.onKeypress)
        self.capture = CaptureManager(
            camera=camera,
            previewWindowManager=self.win,
            shouldMirrorPreview=False
        )
        self.capture.width = 800
        self.capture.height = 448
        self._filter = None
        self._display = True

    def run(self) :
        """Run the main loop."""
        self.win.createWindow()
        while self.win.isCreated :
            self.capture.enterFrame()
            frame = self.capture.frame

            # filters
            if self._filter is not None :
                self._filter.apply(frame, frame)

            # show infos ?
            if self._display :
                H,W = frame.shape[:2]
                info = [
                    ('Size', '{}x{}'.format(self.capture.width, self.capture.height)),
                    ('Filter', self._filter.__class__.__name__),
                    ('Elapsed', self.capture.framesElapsed),
                    ('FPS/cv', self.capture.camera.get(cv.CAP_PROP_FPS)),
                    ('FPS', self.capture.fpsEstimate)
                ]
                for (i, (k, v)) in enumerate(info):
                    text = "{}: {}".format(k, v)
                    cv.putText(
                        frame, text, (10, H - ((i * 15) + 15)),
                        cv.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1
                    )

            self.capture.exitFrame()
            self.win.processEvents()
    
    def onKeypress(self, keycode) :
        """Handle a keypress.

        space  -> Take a screenshot.
        tab    -> Start/stop recording a screencast.
        escape -> Quit
        """
        if keycode == 32 : # space
            self.capture.writeImage('screenshot.png')
        elif keycode == 9 : # tab
            if not self.capture.isWritingVideo :
                self.capture.startWritingVideo('screencast.avi', 'XVID')
            else :
                self.capture.stopWritingVideo()
        elif keycode == 27 or keycode == ord('q') : # 27 = escape
            self.capture.camera.release()
            self.win.destroyWindow()
        elif keycode == ord('b') :
            self._filter = filters.BlurFilter()
        elif keycode == ord('g') :
            self._filter = filters.FindEdgesFilter()
        elif keycode == ord('!') :
            self._filter = filters.StrokeEdgesFilter()
        elif keycode == ord('e') :
            self._filter = filters.EmbossFilter()
        elif keycode == ord('s') :
            self._filter = filters.SharpenFilter()
        elif keycode == ord('G') :
            self._filter = filters.GaussianBlurFilter(kernel=(21,21))
        elif keycode == ord('c') :
            self._filter = filters.CannyEdgesFilter(threshold=30, overlay=False)
        elif keycode == ord('i') :
            self._display = not self._display
        elif keycode == ord('p') :
            self.capture.openSettings()
        elif keycode == ord('x') :
            self._filter = None

if __name__ == '__main__' :
    source = ''.join(sys.argv[1:]) or '0'
    print(source)
    source = int(source) if source.isdigit() else source
    Cameo(source).run()
