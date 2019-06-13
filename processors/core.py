# -*- encoding: utf8 -*-

# abstract base class : compatible python 2.x *and* 3.x
import abc
# ABC = abc.ABCMeta(str('ABC'), (object,), { '__slots__' : ()})

__all__ = [ 'FrameProcessor' ]

# ------------------------------------------------------------------------------

class FrameProcessor(abc.ABC) :

    def __init__(self) :
        self.params()

    @abc.abstractmethod
    def params(self, **kwargs) :
        pass

    @abc.abstractmethod
    def apply(self, frame, context) :
        pass

# ------------------------------------------------------------------------------
