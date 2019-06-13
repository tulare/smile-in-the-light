# -*- encoding: utf-8 -*-

import cv2 as cv
import numpy as np
from . import utils

class Filter :

    def __init__(self) :
        """Method to override to add parameters to the filter.
        """
        pass

    def apply(self, src, dst) :
        """Method to override to apply the filter.

        Pseudocode :
        b, g, r = cv.split(src)
        filter b, g, r composants
        cv.merge((b, g, r), dst)
        """
        pass


class RecolorRC(Filter) :

    def apply(self, src, dst) :
        """Simulate conversion from BGR to RC (red, cyan).

        The source and destination images must both be in BGR format.
        Blues and greens are replaced with cyans.

        Pseudocode:
        dst.b = dst.g = 0.5 * (src.b + src.g)
        dst.r = src.r
        """
        b, g, r = cv.split(src)
        cv.addWeighted(b, 0.5, g, 0.5, 0, b)
        cv.merge((b, b, r), dst)


class RecolorRGV(Filter) :

    def apply(self, src, dst) :
        """Simulate conversion from BGR to RGV (red, green, value).

        The source and destination images must both be in BGR format.
        Blues are desaturated.

        Pseudocode:
        dst.b = min(src.b, src.g, src.r)
        dst.g = src.g
        dst.r = src.r
        """
        b, g, r = cv.split(src)
        cv.min(b, g, b)
        cv.min(b, r, b)
        cv.merge((b, g, r), dst)

class RecolorCMV(Filter) :

    def apply(self, src, dst) :
        """Simulate conversion from BGR to CMV (cyan, magenta, value).

        The source and destination images must both be in BGR format.
        Yellows are desaturated.

        Pseudocode:
        dst.b = max(src.b, src.g, src.r)
        dst.g = src.g
        dst.r = src.r
        """
        b, g, r = cv.split(src)
        cv.max(b, g, b)
        cv.max(b, r, b)
        cv.merge((b, g, r), dst)


class VFuncFilter(Filter) :
    """A filter that applies a function to V (or all of BGR)."""
    
    def __init__(self, vFunc = None, dtype = np.uint8) :
        length = np.iinfo(dtype).max + 1
        self._vLookupArray = utils.createLookupArray(vFunc, length)

    def apply(self, src, dst):
        """Apply the filter with a BGR or gray source/destination."""

        srcFlatView = utils.flatView(src)
        dstFlatView = utils.flatView(dst)
        utils.applyLookupArray(
            self._vLookupArray,
            srcFlatView,
            dstFlatView
        )


class VCurveFilter(VFuncFilter):
    """A filter that applies a curve to V (or all of BGR)."""

    def __init__(self, vPoints, dtype = np.uint8) :
        super().__init__(
            utils.createCurveFunc(vPoints),
            dtype
        )


class BGRFuncFilter(Filter) :
    """A filter that applies different functions to each of BGR."""

    def __init__(self, vFunc = None, bFunc = None, gFunc = None,
                 rFunc = None, dtype = np.uint8) :
        
        length = np.iinfo(dtype).max + 1
        self._bLookupArray = utils.createLookupArray(
            utils.createCompositeFunc(bFunc, vFunc),
            length
        )
        self._gLookupArray = utils.createLookupArray(
            utils.createCompositeFunc(gFunc, vFunc),
            length
        )
        self._rLookupArray = utils.createLookupArray(
            utils.createCompositeFunc(rFunc, vFunc),
            length
        )

    def apply(self, src, dst):
        """Apply the filter with a BGR source/destination."""
        
        b, g, r = cv.split(src)
        utils.applyLookupArray(self._bLookupArray, b, b)
        utils.applyLookupArray(self._gLookupArray, g, g)
        utils.applyLookupArray(self._rLookupArray, r, r)
        cv.merge([b, g, r], dst)


class BGRCurveFilter(BGRFuncFilter):
    """A filter that applies different curves to each of BGR."""

    def __init__(self, vPoints = None, bPoints = None,
                 gPoints = None, rPoints = None, dtype = np.uint8):
        super().__init__(
            utils.createCurveFunc(vPoints),
            utils.createCurveFunc(bPoints),
            utils.createCurveFunc(gPoints),
            utils.createCurveFunc(rPoints),
            dtype
        )


class BGRPortraCurveFilter(BGRCurveFilter):
    """A filter that applies Portra-like curves to BGR."""

    def __init__(self, dtype = np.uint8):
        super().__init__(
            vPoints = [(0,0),(23,20),(157,173),(255,255)],
            bPoints = [(0,0),(41,46),(231,228),(255,255)],
            gPoints = [(0,0),(52,47),(189,196),(255,255)],
            rPoints = [(0,0),(69,69),(213,218),(255,255)],
            dtype = dtype
        )


class BGRProviaCurveFilter(BGRCurveFilter):
    """A filter that applies Provia-like curves to BGR."""

    def __init__(self, dtype = np.uint8):
        super().__init__(
            bPoints = [(0,0),(35,25),(205,227),(255,255)],
            gPoints = [(0,0),(27,21),(196,207),(255,255)],
            rPoints = [(0,0),(59,54),(202,210),(255,255)],
            dtype = dtype
        )


class BGRVelviaCurveFilter(BGRCurveFilter):
    """A filter that applies Velvia-like curves to BGR."""

    def __init__(self, dtype = np.uint8):
        super().__init__(
            vPoints = [(0,0),(128,118),(221,215),(255,255)],
            bPoints = [(0,0),(25,21),(122,153),(165,206),(255,255)],
            gPoints = [(0,0),(25,21),(95,102),(181,208),(255,255)],
            rPoints = [(0,0),(41,28),(183,209),(255,255)],
            dtype = dtype
        )


class BGRCrossProcessCurveFilter(BGRCurveFilter):
    """A filter that applies cross-process-like curves to BGR."""

    def __init__(self, dtype = np.uint8):
        super().__init__(
            bPoints = [(0,20),(255,235)],
            gPoints = [(0,0),(56,39),(208,226),(255,255)],
            rPoints = [(0,0),(56,22),(211,255),(255,255)],
            dtype = dtype
        )

class StrokeEdgesFilter(Filter) :

    def __init__(self, blurKsize=7, edgeKsize=5) :

        self.blurKsize = blurKsize
        self.edgeKsize = edgeKsize

    def apply(self, src, dst):

        if self.blurKsize >= 3:
            blurredSrc = cv.medianBlur(src, self.blurKsize)
            graySrc = cv.cvtColor(blurredSrc, cv.COLOR_BGR2GRAY)
        else:
            graySrc = cv.cvtColor(src, cv.COLOR_BGR2GRAY)

        cv.Laplacian(graySrc, cv.CV_8U, graySrc, ksize=self.edgeKsize)
        normalizedInverseAlpha = (1.0 / 255) * (255 - graySrc)
        channels = cv.split(src)

        for channel in channels:
            channel[:] = channel * normalizedInverseAlpha

        cv.merge(channels, dst)


class CannyEdgesFilter(Filter) :

    def __init__(self, threshold=10, apertureSize=3, overlay=False) :
        self._threshold = threshold
        self._apertureSize = apertureSize
        self._overlay = overlay

    def apply(self, src, dst) :

        assert src.shape == dst.shape

        if utils.isGray(src) :
            gray = src
        else :
            gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)

        cedge = cv.Canny(
            gray,
            self._threshold,
            self._threshold * 3,
            apertureSize=self._apertureSize
        )
        alpha = (1.0 / 255) * (255 - cedge)

        channels = cv.split(src)

        for channel in channels :
            if self._overlay :
                channel[:] = channel * alpha
            else :
                channel[:] = cedge

        cv.merge(channels, dst)


class ThresholdFilter(Filter) :

    def __init__(self, threshold=127, otsu=False) :
        self._threshold = threshold
        self._max = 255
        self._otsu = otsu

    def apply(self, src, dst) :

        if utils.isGray(src) :
            gray = src
        else :
            gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)

        if self._otsu :
            th, thresh = cv.threshold(
                gray,
                0, self._max,
                cv.THRESH_BINARY + cv.THRESH_OTSU
            )    
        else :
            th, thresh = cv.threshold(
                gray,
                self._threshold, self._max,
                cv.THRESH_BINARY
            )

        cv.merge((thresh, thresh, thresh), dst)

class AdaptiveGaussianThresholdFilter(Filter) :

    def __init__(self, size=11, c=2) :
        self._max = 255
        self._size = size
        self._c = c

    def apply(self, src, dst) :

        if utils.isGray(src) :
            gray = src
        else :
            gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)

        thresh = cv.adaptiveThreshold(
                gray,
                self._max,
                cv.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv.THRESH_BINARY,
                self._size, self._c
            )

        cv.merge((thresh, thresh, thresh), dst)

class AdaptiveMeanThresholdFilter(Filter) :

    def __init__(self, size=11, c=2) :
        self._max = 255
        self._size = size
        self._c = 2

    def apply(self, src, dst) :

        if utils.isGray(src) :
            gray = src
        else :
            gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)

        thresh = cv.adaptiveThreshold(
                gray,
                self._max,
                cv.ADAPTIVE_THRESH_MEAN_C,
                cv.THRESH_BINARY,
                self._size, self._c
            )

        cv.merge((thresh, thresh, thresh), dst)

        
class GaussianBlurFilter(Filter) :

    def __init__(self, kernel=(5,5)) :
        self._kernel = kernel

    def apply(self, src, dst) :
        cv.GaussianBlur(src, self._kernel, 0, dst)

        
class VConvolutionFilter(Filter) :
    """A filter that applies a convolution to V (or all of BGR)."""

    def __init__(self, kernel):
        super().__init__()
        self._kernel = kernel

    def apply(self, src, dst):
        """Apply the filter with a BGR or gray source/destination."""
        assert src.shape == dst.shape

        cv.filter2D(src, -1, self._kernel, dst)


class SharpenFilter(VConvolutionFilter):
    """A sharpen filter with a 1-pixel radius."""

    def __init__(self):
        kernel = np.array([
            [-1, -1, -1],
            [-1,  9, -1],
            [-1, -1, -1]
        ])
        super().__init__(kernel)


class FindEdgesFilter(VConvolutionFilter):
    """An edge-finding filter with a 1-pixel radius."""

    def __init__(self):
        kernel = np.array([
            [-1, -1, -1],
            [-1,  8, -1],
            [-1, -1, -1]
        ])
        super().__init__(kernel)


class BlurFilter(VConvolutionFilter):
    """A blur filter with a 2-pixel radius."""

    def __init__(self):
        kernel = np.array([
            [0.04, 0.04, 0.04, 0.04, 0.04],
            [0.04, 0.04, 0.04, 0.04, 0.04],
            [0.04, 0.04, 0.04, 0.04, 0.04],
            [0.04, 0.04, 0.04, 0.04, 0.04],
            [0.04, 0.04, 0.04, 0.04, 0.04]
        ])
        super().__init__(kernel)


class EmbossFilter(VConvolutionFilter):
    """An emboss filter with a 1-pixel radius."""

    def __init__(self):
        kernel = np.array([
            [-2, -1, 0],
            [-1,  1, 1],
            [ 0,  1, 2]
        ])
        super().__init__(kernel)
