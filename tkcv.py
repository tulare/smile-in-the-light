# -*- encoding: utf-8 -*-

import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import cv2 as cv
import datetime
import os

from ui.capture import CaptureManager 

class Application :

    def __init__(self) :

        self.root = root = tk.Tk()
        root.title("Webcam capture")

        self.vidcap = cv.VideoCapture(0, cv.CAP_DSHOW)
        self.capman = CaptureManager(self.vidcap)

        body = tk.Frame(root)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        root.grab_set()

        if not self.initial_focus :
            self.initial_focus = root

        root.protocol('WM_DELETE_WINDOW', self.cancel)
        self.initial_focus.focus_set()

        self.video_loop()

    def body(self, master) :
        self.panel = tk.Label(master)
        self.panel.pack(padx=10, pady=10)

        btn = tk.Button(master, text="Snapshot !", command=self.take_snapshot)
        btn.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        btn = tk.Button(master, text="Camera Settings", command=self.open_settings)
        btn.pack(fill=tk.BOTH, expand=True, padx=10, pady=1)

        self.fps = tk.Label(master)
        self.fps.pack(padx=10, pady=10)

        return btn

    def cancel(self) :
        self.root.destroy()
        self.vidcap.release()

    def take_snapshot(self) :
        """ Take snapshot and save to file """
        ts = datetime.datetime.now()
        filename = '{}.jpg'.format(ts.strftime('%Y-%m-%d_%H-%M-%S'))
        p = os.path.join('./', filename)
        self.capman.writeImage(p)

    def open_settings(self) :
        self.vidcap.set(cv.CAP_PROP_SETTINGS, 1)

    def show_frame(self, frame) :
        frameImage = Image.fromarray(
            cv.cvtColor(frame, cv.COLOR_BGR2RGBA)
        )
        self.panel.imgTk = ImageTk.PhotoImage(image=frameImage)
        self.panel.config(image=self.panel.imgTk)

    def video_loop(self) :
        self.capman.enterFrame()
        frame = self.capman.frame

        self.show_frame(frame)
        
        self.capman.exitFrame()
        self.fps.config(text='fps : {:2d}'.format(self.capman.fpsEstimate))
        self.root.after(20, self.video_loop)

if __name__ == '__main__' :
    app = Application()
    app.root.mainloop()
