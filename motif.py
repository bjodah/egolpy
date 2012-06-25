#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division

import sys

try:
    import cPickle as pickle
except ImportError:
    import pickle

class Motif(object):
    """
    A motif class for storing 2D motifs of arbitrary
    form and number of states. It has a background state
    property. Methods are provided for pickling and unpickling
    as well as getting generating a minimal rectangle of data
    (datastrip of a width) with the motif on its corresponding
    background.
    """

    def __init__(self, state_coords=None, bgstate=0, datastrip=None,
                 stripwidth=None):
        """

        Arguments:
        - `state_coords`: a list of (x, y, state) entries
        - `bgstate`:      an integer representing the background
                          state of the motif (used when generating
                          a minimal_rectangle_data_strip)
        """
        self._data = data

    def __getstate__(self):
        # What to pickle
        return self.items()

    def __setstate__(self, items):
        # How to unpickle
        pass

    def save(self,):
        # use pickle.dump
        pass

    def load(self):
        # use pickle.load

    def query(self, x, y):
        pass

    def redefine(self, x, y):
        pass

    def rotate(self):
        pass

    @property
    def minimal_rectangle_data_strip(self):
        return None

