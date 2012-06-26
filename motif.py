#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division

import sys
from collections import Counter

from bz2 import BZ2File

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
    (dense_data of a width) with the motif on its corresponding
    background.
    """

    def __init__(self, state_coords=None, bgstate=0, dense_data=None,
                 stripwidth=None, nx=None, ny=None, from_file=None):
        """

        Arguments:
        - `state_coords`: a list of (x, y, state) entries
        - `bgstate`:      an integer representing the background
                          state of the motif (used when generating
                          a minimal_rectangle_data_strip)
        """
        if from_file != None:
            self.load(from_file)
            return None
        if state_coords != None:
            # state_coords provided
            # make sure not also dense_data provided (ambigous)
            assert dense_data == None
            if nx == None:
                # No nx, ny provided
                # assign from largest coords
                assert ny == None
                nx, ny = 0, 0
                for x, y, state in state_coords:
                    if x > nx: nx = x
                    if y > ny: ny = y
                nx += 1; ny += 1
            assert nx, ny != (None, None)
            # let's store _nx, _ny
            self._nx = nx; self._ny = ny
            # set state_coords
            self._sparse_data = {}
            for x, y, state in state_coords:
                self._sparse_data[self.get_index(x,y)] = state
            self._sparse = True
        else:
            # no state_coords provided
            if dense_data != None:
                assert stripwidth != None
                self._dense_data = dense_data
                self._sparse = False
                nx = stripwidth
                ny = len(dense_data)//nx
                assert len(dense_data) % nx == 0
            else:
                # neither state_coords nor dense_data provided
                # initialize _dense_data with bgstate with
                # dimensions equal to nx, ny (must be provided)
                assert nx, ny != (None, None)
                self._dense_data = [bgstate]*nx*ny
            # let's store _nx, _ny
            self._nx = nx; self._ny = ny

        # Now _nx, _ny, _sparse and
        # (_dense_data / _sparse_data) are stored

        # Now store bgstate
        self._bgstate = bgstate

        # Make a state count Counter and store as:
        # self._state_counter
        self.recount_states()

        # Decide optimal mode of operation (dense/sparse) and set:
        # self._sparse = True/False, where False -> dense mode
        self.set_optimal_dense_sparse_mode()

    def recount_states(self):
        if self._sparse:
            self._state_counter = Counter(self._sparse_data.values())
        else:
            self._state_counter = Counter(self._dense_data)

    def __getitem__(self, index):
        if self._sparse:
            if index > self._nx*self._ny:
                raise IndexError('Out of bounds')
            return self._sparse_data.get(index, self._bgstate)
        else:
            return self._dense_data[index]

    def __delitem__(self, index):
        self[index] = self._bgstate

    def query_xy(self, x, y):
        return self[self.get_index(x, y)]

    def __setitem__(self, index, new_state):
    #def redefine(self, index, new_state):
        cur_state = self[index]
        if cur_state != new_state:
            self._state_counter[cur_state] -= 1
            self._state_counter[new_state] += 1
            if self._sparse:
                self._sparse_data[index] = new_state
            else:
                self._dense_data[index] = new_state

    def redefine_xy(self, x, y, new_state):
        self[self.get_index(x, y)] = new_state

    def get_index(self, x, y):
        return self._nx*y+x

    def optimize_bgstate(self):
        most_occuring_state = max(self._state_counter.keys())
        if not self._bgstate == most_occuring_state:
            self._bgstate = most_occuring_state

    def crop_side(self, side):
        """ Once you crop, you cannot change
            bgstate any more, or you'll risk
            losing information by recursive,
            bgstate optimization + cropping """

        # Don't crop an empty motif
        assert self._state_counter[self._bgstate] \
               < self._nx*self._ny

        def get_range(depth):
            return {'top':    zip(range(self._nx),
                                  [depth]*self._nx),
                    'bottom': zip(range(self._nx),
                                  [self._ny-1-depth]*self._nx),
                    'left':   zip([depth]*self._ny,
                                  range(self._ny)),
                    'right':  zip(range(self._ny),
                                  [self._nx-1-depth]*self._ny),
                    }.get(side)

        # Loop i to maximum crop depth
        reached_depth = -1
        for i in range(max([self._nx, self._ny]):
            for x, y in ranges[side]:
                if self[self.get_index(x, y) != self._bgstate:
                    reached_depth = i
                    break
            if reached_depth != -1:
                break
        if reached_depth > 0:
            x, y, width, height = 0, 0, self._nx, self._ny
            if side == 'top':    y += reached_depthb
            if side == 'bottom': y -= reached_depth
            if side == 'left':   x += reached_depth
            if side == 'right':  x -= reached_depth
            self.resize(x,y,width,height)

    def resize(self, xstart, ystart, width, height):
        if self._sparse:
            NotImplemented
        else:
            new_dense_data = []
            for y in range(ystart, ystart+height):
                for x in range(xstart, xstart+width):
                    new_dense_data.append(self[self.get_index(x,y)])
            self.__init__(dense_data=new_dense_data,
                          stripwidth=width)


    def crop(self):
        for side in ('top', 'bottom', 'left', 'right'):
            self.crop_side(side)

    def set_optimal_dense_sparse_mode(self):
        # TODO: Confirm 75% break-even dense vs. sparse
        if self._state_counter[self._bgstate] \
           > self._nx*self._ny // 4 * 3:
            # Make it sparse if it isn't already!
            if self._sparse == False:
                self._sparse_data = get_sparse_data()
                self._sparse = True
                del self._dense_data
        else:
            # Make it dense if it isn't already!
            if self._sparse == True:
                self._dense_data = get_dense_data()
                self._sparse = False
                del self._sparse_data


    def get_sparse_data(self):
        if self._sparse: return self._sparse_data
        sparse = {}
        for idx, state in enumerate(self._dense_data):
            if state != self._bgstate:
                sparse[idx] = state
        return sparse

    def get_dense_data(self):
        if not self._sparse: return self._dense_data
        dense = []
        for idx in range(self._nx*self._ny):
            self._sparse_data.get(idx, self._bgstate)

    def optimize(self):
        self.crop()
        self.optimize_bgstate()
        self.set_optimal_dense_sparse_mode()

    def save(self, path):
        # Optimize
        self.optimize()

        # use pickle.dump to BZ2File
        if not path.endswith('.bz2'):
            path += '.bz2'
        if not path.endswith('.motif.bz2'):
            path = path[:-4] + '.motif.bz2'

        pickle.dump(self, BZ2File(path,'wb'))

    @classmethod
    def load_instance_from_file(cls, path):
        # use pickle.load from BZ2File
        if path.endswith('.motif.bz2'):
            return pickle.load(BZ2File(path,'rb'))
        else:
            raise ValueError('Motif file must end with ".motif.bz2"')

    @classmethod
    def load_instance_from_legacy_txt(cls, path):
        # Support for loading legacy format:
        import json
        ifh = open(path, 'rt')
        loaddata = json.load(ifh)
        nx = len(loaddata[0])
        ifh.close()
        dense_data = []
        for segm in loaddata:
            dense_data.extend(segm)
        return cls(dense_data=dense_data,stripwidth=nx)

    def rotate(self):
        pass

    @property
    def minimal_rectangle_dense_data(self):
        NotImplemented

    @property
    def minimal_rectangle_sparse_data(self):
        NotImplemented
