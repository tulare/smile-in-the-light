# -*- encoding: utf-8 -*-

import cv2 as cv
import inspect

__all__ = [ 'CameraSettings' ]

# --------------------------------------------------------------------

def propSettings() :
    exclude_list = (
        'DC1394', 'GIGA', 'GPHOTO', 'GSTREAMER',
        'INTELPERC', 'IOS',
        'OPENNI', 'PVAPI', 'XI',
    )
    return dict(
        (k, v)
        for k, v in vars(cv).items()
        if k.startswith('CAP_PROP_')
        and all('_{}'.format(m) not in k for m in exclude_list) 
    )
    

# --------------------------------------------------------------------

class CameraSettings :

    def __init__(self, videoCapture) :
        self.capture = videoCapture

    def listSettings(self) :
        for key, value in propSettings().items() :
            print(key, self.get(value))

    @property
    def settings(self) :
        return dict(
            (name, prop.fget(self))
            for name, prop in inspect.getmembers(
                CameraSettings,
                lambda o : isinstance(o, property)
	    )
            if name != 'settings'
        )

    def openSettings(self) :
        self.capture.set(cv.CAP_PROP_SETTINGS, 1)

    def get(self, key) :
        if not self.capture.isOpened() :
            raise ValueError("Can't read this setting", key)
        return self.capture.get(key)

    def set(self, key, value) :
        if not self.capture.set(key, value) :
            raise ValueError("Can't change this setting", key, value)

    @property
    def autofocus(self) :
        return self.get(cv.CAP_PROP_AUTOFOCUS)

    @autofocus.setter
    def autofocus(self, value) :
        self.set(cv.CAP_PROP_AUTOFOCUS, value)

    @property
    def focus(self) :
        return self.get(cv.CAP_PROP_FOCUS)

    @focus.setter
    def focus(self, value) :
        self.set(cv.CAP_PROP_FOCUS, value)

    @property
    def brightness(self) :
        return self.get(cv.CAP_PROP_BRIGHTNESS)

    @brightness.setter
    def brightness(self, value) :
        self.set(cv.CAP_PROP_BRIGHTNESS, value)

    @property
    def contrast(self) :
        return self.get(cv.CAP_PROP_CONTRAST)

    @contrast.setter
    def contrast(self, value) :
        self.set(cv.CAP_PROP_CONTRAST, value)

    @property
    def saturation(self) :
        return self.get(cv.CAP_PROP_SATURATION)

    @saturation.setter
    def saturation(self, value) :
        self.set(cv.CAP_PROP_SATURATION, value)
    
    @property
    def hue(self) :
        return self.get(cv.CAP_PROP_HUE)

    @hue.setter
    def hue(self, value) :
        self.set(cv.CAP_PROP_HUE, value)

    @property
    def gamma(self) :
        return self.get(cv.CAP_PROP_GAMMA)

    @gamma.setter
    def gamma(self, value) :
        self.set(cv.CAP_PROP_GAMMA, value)

    @property
    def sharpness(self) :
        return self.get(cv.CAP_PROP_SHARPNESS)

    @sharpness.setter
    def sharpness(self, value) :
        self.set(cv.CAP_PROP_SHARPNESS, value)

    @property
    def exposure(self) :
        return self.get(cv.CAP_PROP_EXPOSURE)

    @exposure.setter
    def exposure(self, value) :
        self.set(cv.CAP_PROP_EXPOSURE, value)

    @property
    def whitebalance(self) :
        return self.get(cv.CAP_PROP_WHITE_BALANCE_BLUE_U)

    @whitebalance.setter
    def whitebalance(self, value) :
        self.set(cv.CAP_PROP_WHITE_BALANCE_BLUE_U, value)

    @property
    def backlight(self) :
        return self.get(cv.CAP_PROP_BACKLIGHT)

    @backlight.setter
    def backlight(self, value) :
        self.set(cv.CAP_PROP_BACKLIGHT, value)

    @property
    def gain(self) :
        return self.get(cv.CAP_PROP_GAIN)

    @gain.setter
    def gain(self, value) :
        self.set(cv.CAP_PROP_GAIN, value)

    @property
    def zoom(self) :
        return self.get(cv.CAP_PROP_ZOOM)

    @zoom.setter
    def zoom(self, value) :
        self.set(cv.CAP_PROP_ZOOM, value)

    @property
    def pan(self) :
        return self.get(cv.CAP_PROP_PAN)

    @pan.setter
    def pan(self, value) :
        self.set(cv.CAP_PROP_PAN, value)

    @property
    def tilt(self) :
        return self.get(cv.CAP_PROP_TILT)

    @tilt.setter
    def tilt(self, value) :
        self.set(cv.CAP_PROP_TILT, value)


# --------------------------------------------------------------------

if __name__ == '__main__' :

    def demo(cs) :
        cv.namedWindow('demo')
        while True :
            ok, frame = cs.capture.read()
            if not ok :
                break

            cv.imshow('demo', frame)

            keycode = cv.waitKey(1)
            if keycode == 27 :
                break
            elif keycode == ord('²') :
                cs.openSettings()
            elif keycode == ord('+') :
                try:
                    cs.exposure += 1
                    print('exposure', cs.exposure)
                except :
                    pass
            elif keycode == ord('-') :
                try :
                    cs.exposure -= 1
                    print('exposure', cs.exposure)
                except :
                    pass
            elif keycode == ord('@') :
                print(cs.settings)
            elif keycode == ord('a') :
                try :
                    cs.autofocus = 1
                    print('focus', cs.focus)
                except :
                    pass
            elif keycode == ord('z') :
                try :
                    cs.focus = cs.focus - (cs.focus % 5) - 5
                    print('focus', cs.focus)
                except :
                    pass
            elif keycode == ord('e') :
                try :
                    cs.focus = cs.focus - (cs.focus % 5) + 5
                    print('focus', cs.focus)
                except :
                    pass
            elif keycode != -1 :
                print(keycode, chr(keycode))
                
        cv.destroyWindow('demo')

    cam = cv.VideoCapture(0, cv.CAP_DSHOW)
    cs = CameraSettings(cam)
