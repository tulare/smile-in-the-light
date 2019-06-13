# -*- encoding: utf8 -*-

import tkinter
from ui.capture import CameraCapture
from processors.counters import FramecountProcessor
from processors.trackers import (
    TrackingProcessor,
    MeanShiftTrackingProcessor,
    CamShiftTrackingProcessor,
    StickingProcessor
)
from processors.pedestrian import PedestrianProcessor
from processors.lines import LinesProcessor
from processors.circles import CirclesProcessor
from processors.backsubtractors import BackSubProcessor

# ------------------------------------------------------------------------------

class Application(tkinter.Tk) :

    def __init__(self) :
        super().__init__()
        self.protocol('WM_DELETE_WINDOW', self.cmd_close)
        self.camera = CameraCapture(self)
        self.createWidgets()

    def createWidgets(self) :
        tkinter.Label(self, text='Device or Url :').pack(side=tkinter.TOP)

        self.source = tkinter.StringVar()
        source_entry = tkinter.Entry(
            self,
            width=60,
            textvariable=self.source
        )
        source_entry.pack(side=tkinter.TOP)
        #self.source.set('http://176.57.73.231/mjpg/video.mjpg')
        self.source.set('0')
                                     
        capture_btn = tkinter.Button(self, text='Capture', command=self.cmd_capture)
        capture_btn.pack(fill=tkinter.BOTH)

        sticking_btn = tkinter.Button(self, text='Sticking', command=self.cmd_sticking)
        sticking_btn.pack(fill=tkinter.BOTH)

        tracking_btn = tkinter.Button(self, text='Tracking', command=self.cmd_tracking)
        tracking_btn.pack(fill=tkinter.BOTH)

        meanshift_btn = tkinter.Button(self, text='Tracking MeanShift', command=self.cmd_meanshift)
        meanshift_btn.pack(fill=tkinter.BOTH)

        camshift_btn = tkinter.Button(self, text='Tracking CamShift', command=self.cmd_camshift)
        camshift_btn.pack(fill=tkinter.BOTH)

        pedestrian_btn = tkinter.Button(self, text='Detect Pedestrians', command=self.cmd_pedestrian)
        pedestrian_btn.pack(fill=tkinter.BOTH)

        lines_btn = tkinter.Button(self, text='Detect Lines', command=self.cmd_lines)
        lines_btn.pack(fill=tkinter.BOTH)

        circles_btn = tkinter.Button(self, text='Detect Circles', command=self.cmd_circles)
        circles_btn.pack(fill=tkinter.BOTH)

        backsub_btn = tkinter.Button(self, text='Background Suppression', command=self.cmd_backsub)
        backsub_btn.pack(fill=tkinter.BOTH)

    def cmd_capture(self) :
        self.camera.reset_counter()
        source = self.source.get()
        processor = FramecountProcessor()      
        if source :
            self.camera.processor = processor
            self.camera.source = int(source) if source.isdecimal() else source            
            self.after(500, self.camera.run)

    def cmd_sticking(self, event=None) :
        self.camera.reset_counter()
        source = self.source.get()
        processor = StickingProcessor()
        if source :
            self.camera.processor = processor
            self.camera.source = int(source) if source.isdecimal() else source
            self.after(500, self.camera.run)

    def cmd_tracking(self, event=None) :
        self.camera.reset_counter()
        source = self.source.get()
        processor = TrackingProcessor()
        if source :
            self.camera.processor = processor
            self.camera.source = int(source) if source.isdecimal() else source
            self.after(500, self.camera.run)

    def cmd_meanshift(self, event=None) :
        self.camera.reset_counter()
        source = self.source.get()
        processor = MeanShiftTrackingProcessor()
        if source :
            self.camera.processor = processor
            self.camera.source = int(source) if source.isdecimal() else source
            self.after(500, self.camera.run)

    def cmd_camshift(self, event=None) :
        self.camera.reset_counter()
        source = self.source.get()
        processor = CamShiftTrackingProcessor()
        if source :
            self.camera.processor = processor
            self.camera.source = int(source) if source.isdecimal() else source
            self.after(500, self.camera.run)

    def cmd_pedestrian(self, event=None) :
        self.camera.reset_counter()
        source = self.source.get()
        processor = PedestrianProcessor()
        if source :
            self.camera.processor = processor
            self.camera.source = int(source) if source.isdecimal() else source
            self.after(500, self.camera.run)

    def cmd_lines(self, event=None) :
        self.camera.reset_counter()
        source = self.source.get()
        processor = LinesProcessor()
        processor.params(minLineLength=60, maxLineGap=3)
        if source :
            self.camera.processor = processor
            self.camera.source = int(source) if source.isdecimal() else source            
            self.after(500, self.camera.run)

    def cmd_circles(self, event=None) :
        self.camera.reset_counter()
        source = self.source.get()
        processor = CirclesProcessor()
        processor.params(minRadius=5, maxRadius=40)
        if source :
            self.camera.processor = processor
            self.camera.source = int(source) if source.isdecimal() else source            
            self.after(500, self.camera.run)

    def cmd_backsub(self, event=None) :
        self.camera.reset_counter()
        source = self.source.get()
        processor = BackSubProcessor()
        if source :
            self.camera.processor = processor
            self.camera.source = int(source) if source.isdecimal() else source            
            self.after(500, self.camera.run)

    def cmd_close(self) :
        self.camera.release()
        self.destroy()

# ------------------------------------------------------------------------------

def main() :
    application = Application()
    application.mainloop()

# ------------------------------------------------------------------------------

if __name__ == '__main__' :
    main()
