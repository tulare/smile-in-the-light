# -*- encoding: utf-8 -*-

import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import cv2 as cv

import os
import datetime
import functools

from ui.capture import CaptureManager
from ui.settings import CameraSettings
from processors import filters

class Application :

    def __init__(self) :

        self.root = root = tk.Tk()
        root.title("Webcam capture")

        self.vidcap = cv.VideoCapture(0, cv.CAP_DSHOW)
        self.capman = CaptureManager(self.vidcap)
        self.capcfg = CameraSettings(self.vidcap)
        
        self.filter = None

        body = tk.Frame(root)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        root.grab_set()

        if not self.initial_focus :
            self.initial_focus = root

        root.protocol('WM_DELETE_WINDOW', self.cancel)
        self.initial_focus.focus_set()

        self.video_loop()
        self.refresh_stats()

    def body(self, master) :
        self.panel = tk.Label(master)
        self.panel.pack(padx=10, pady=10)

        btnGroup = tk.Frame(master)
        btnGroup.pack(fill=tk.X, expand=True, padx=10, pady=10)
        for btn in ('Réglages',
                    'Dump',
                    'Velvia',
                    'XProcess',
                    'Stroke Edges',
                    'Canny Edges',
                    'Threshold',
                    ) :
            tk.Button(
                btnGroup,
                text=' ' + btn + ' ',
                command=functools.partial(self.do_action, btn)
            ).pack(
                side=tk.LEFT,
                fill=tk.X,
                expand=True,
                padx=5,
            )

        btnSnap = tk.Button(master, text="Snapshot !", command=self.take_snapshot)
        btnSnap.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.fps = tk.Label(master)
        self.fps.pack(side=tk.LEFT, padx=10, pady=10)

        return btnSnap

    def cancel(self) :
        self.root.destroy()
        self.vidcap.release()

    def take_snapshot(self) :
        """ Take snapshot and save to file """
        ts = datetime.datetime.now()
        filename = '{}.jpg'.format(ts.strftime('%Y-%m-%d_%H-%M-%S'))
        p = os.path.join('./', filename)
        self.capman.writeImage(p)

    def do_action(self, action) :
        if action == 'Réglages' :
            self.capcfg.openSettings()
        elif action == 'Dump' :
            print(self.capcfg.settings)
        elif action == 'Velvia' :
            self.filter = filters.BGRVelviaCurveFilter()
        elif action == 'XProcess' :
            self.filter = filters.BGRCrossProcessCurveFilter()
        elif action == 'Stroke Edges' :
            self.filter = filters.StrokeEdgesFilter()
        elif action == 'Canny Edges' :
            self.filter = filters.CannyEdgesFilter(threshold=30)
        elif action == 'Threshold' :
            self.filter = filters.ThresholdFilter()

    def refresh_stats(self) :
        self.fps.config(text='{:.2f}'.format(self.capman.fpsEstimate))

    def show_frame(self, frame) :
        # convert to PIL Image (change colorspace BGR -> RGBA)
        frameImage = Image.fromarray(
            cv.cvtColor(frame, cv.COLOR_BGR2RGBA)
        )
        # convert to PhotoImage (keep reference into self.panel)
        self.panel.imgTk = ImageTk.PhotoImage(image=frameImage)
        self.panel.config(image=self.panel.imgTk)
        
    def video_loop(self) :
        self.capman.enterFrame()
        frame = self.capman.frame

        if self.filter is not None :
            self.filter.apply(frame, frame)

        self.show_frame(frame)

        self.capman.exitFrame()
        self.refresh_stats()
        
        self.root.after(20, self.video_loop)

if __name__ == '__main__' :
    app = Application()
    app.root.mainloop()
