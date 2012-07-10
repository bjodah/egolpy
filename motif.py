#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function


# Stdlib imp.
from itertools import product
import sys
import logging


try:
    import cPickle as pickle
except ImportError:
    import pickle

from collections import Counter

# Intraproj.  imp.
from project_helpers import ExtendedInitDecoratorFactory,\
     memoize

INT_NAN = None

logging.basicConfig()


#@with_storing_functionality
class Motif(object):
    """
    A motif class for storing 2D motifs of arbitrary
    form and number of states. It has a background state
    property. Methods are provided for pickling and unpickling
    as well as getting generating a minimal rectangle of data
    (dense_data of a width) with the motif on its corresponding
    background.
    """

    def __init__(self, bgstate=0, sparse_data=None,
                 dense_data=None, dim = None,
                 sparse_data_type = dict,
                 dense_data_type = list,
                 mode_change_allowed = True,
                 specialized_propagate = False,
                 save_history = False,
                 ):
        """
        TODO nx, ny, is associated with SQUARE, not e.g. TRIANGLE
        Arguments:
        - `bgstate`:      an integer representing the background
                          state of the motif (used when generating
                          a minimal_rectangle_data_strip)
        - `sparse_data`: a list of (index, state) entries
        - `dense_data`: (optional) a list of states
        - `dim`: Dimension of Motif (assumed to be length in
                 baseclass)
        - `sparse_data_type`: dict or specialized dict
        - `dense_data_type`: list or specialized list
        - `mode_change_allowed`: Controls whether switching between
              sparse and dense mode is allowed (matters for
              specialized propagate methods)
        """
        self._dense_data_type  = dense_data_type
        self._sparse_data_type = sparse_data_type
        self._mode_change_allowed = mode_change_allowed
        self._specialized_propagate = specialized_propagate

        if sparse_data != None:
            # sparse_data provided
            self._sparse = True
            # make sure not also dense_data provided (ambigous)
            assert dense_data == None
        else:
            self._sparse = False

        self.set_dim(dim) # stores self._dim and sets: self._n

        # Now store bgstate
        self._bgstate = bgstate

        if not self._specialized_propagate:
            # To facilitate efficient propagate methods of subclasses
            # a list is maintained on what cells have been changed
            # since last invocation of propagate
            self._changed_since_propagate = set()

        self._state_counter = Counter()
        if self._sparse:
            self._sparse_data = self._sparse_data_type()
            for idx, state in sparse_data:
                self[idx] = state
        else:
            # no sparse_data provided
            if dense_data != None:
                self._dense_data = self._dense_data_type(\
                    dense_data)
                for idx, state in enumerate(self._dense_data):
                    if state != self._bgstate: self._changed_since_propagate.add(idx)
            else:
                # neither sparse_data nor dense_data provided
                # initialize _dense_data with bgstate with length
                # self._n
                if dim != None:
                    self._dense_data = self._dense_data_type(\
                        [self._bgstate]*self._n)
                else:
                    raise ValueError("At least dim must be provided when sparse_data and dense_data is both None")

        # Now _sparse and (_dense_data or _sparse_data) are stored

        # Make a state count Counter and store as:
        # self._state_counter
        self.recount_states()

        # Decide optimal mode of operation (dense/sparse) and set:
        # self._sparse = True/False, where False -> dense mode
        self.set_optimal_dense_sparse_mode()

        # Keep track of what generation we are watching
        self.generation = 0

        self._save_history = save_history
        if self._save_history:
            self._history = []

        self.logger = logging.getLogger('motif')
        self.logger.setLevel(logging.INFO)


    def set_dim(self, dim):
        """
        For arbitrary topology assume dim to represent number
        of cells: (triangular tiling of tetrahedron, square
        tiling of qube)
        """

        if dim == None:
            if self._sparse:
                raise ValueError("Cannot infer dimension from sparse data")
            else:
                self._dim = len(self._dense_data)
        else:
            self._dim = dim
        self._n = self._dim


    def propagate(self):
        # changes has format [(idx, prev_state, new_state), ... ]
        if self._sparse:
            if self._specialized_propagate:
                changes = self._sparse_data.propagate()
                self._changed_since_propagate.clear()
                map(self.update_count, *zip(*changes))
            else:
                self.propagate_sparse()
        else:
            if self._specialized_propagate:
                changes = self._dense_data.propagate()
                self._changed_since_propagate.clear()
                map(self.update_count, *zip(*changes))
            else:
                self.propagate_dense()
        self.generation += 1

    def propagate_sparse(self):
        """ To be overloaded """
        NotImplemented

    def propagate_dense(self):
        """ To be overloaded """
        NotImplemented

    def count_state_at_indices(self, counted_state, idxs):
        """ Operates not via __getitem__ in order
            to be efficiently overloaded
            This function is called by CountingRule.match() """
        #return sum([self[i] == counted_state for i in idxs])
        if self._sparse:
            count = 0
            if counted_state != self._bgstate:
                for idx in idxs:
                    if idx in self._sparse_data:
                        if self._sparse_data[idx] == counted_state:
                            count += 1
            else:
                for idx in idxs:
                    if idx not in self._sparse_data:
                        count += 1
        else:
            count = sum([self[i] == counted_state for i in idxs])
        return count

    def recount_states(self):
        if self._sparse:
            self._state_counter = Counter(self._sparse_data.values())
            self._state_counter[self._bgstate] = self._n -\
                                                 len(self._sparse_data)
            if self._specialized_propagate:
                for key in self._sparse_data:
                    self._changed_since_propagate.add(key)
        else:
            self._state_counter = Counter(self._dense_data)
            if self._specialized_propagate:
                for idx, state in enumerate(dense_data):
                    # States other than bgstate are interpreted
                    # as changed
                    if idx != self._bgstate:
                        self._changed_since_propagate.add(idx)

    def update_count(self, index, dec_by_one, inc_by_one):
        self._state_counter[inc_by_one] += 1
        self._state_counter[dec_by_one] -= 1
        if self._state_counter[dec_by_one] == 0:
            self._state_counter.pop(dec_by_one)
        if not self._specialized_propagate:
            self._changed_since_propagate.add(index)


    def add_to_changed_reg(self, index):
        self._changed.append(index)

    def __len__(self):
        if self._sparse:
            return len(self._sparse_data)
        else:
            return len(self._dense_data)

    def __getitem__(self, index):
        if self._sparse:
            if isinstance(index, slice):
                return [self[x] for x in range(*index.indices(self._n))]
            if index > self._n:
                raise IndexError('Out of bounds')
            return self._sparse_data.get(index, self._bgstate)
        else:
            # Assume _dense_data supports slicing
            return self._dense_data[index]

    def __delitem__(self, index):
        """
        Del only calls
        """
        if self._sparse:
            if index in self._sparse_data:
                # Data change!
                prev_state = self._sparse_data.pop(index)
                # __setitem__ not called, calibrate number of states manually
                self.update_count(self.index, prev_state, _bgstate)
        else:
            self[index] = self._bgstate


    def __setitem__(self, index, new_state):
        cur_state = self[index]
        if cur_state != new_state:
            # Data change!
            self.update_count(index, cur_state, new_state)
            if self._sparse:
                if new_state == self._bgstate:
                    self._sparse_data.pop(index)
                else:
                    self._sparse_data[index] = new_state
            else:
                self._dense_data[index] = new_state


    def optimize_bgstate(self):
        most_occuring_state, num = self._state_counter.most_common(1)[0]
        if not self._bgstate == most_occuring_state:
            self.log('Setting new bgstate: %i', self._bgstate)
            self._bgstate = most_occuring_state

    def set_optimal_dense_sparse_mode(self):
        if not self._mode_change_allowed: return None
        # TODO: Confirm 75% break-even dense vs. sparse
        if self._state_counter[self._bgstate] \
               > (self._n // 4 * 3):
            self.make_sparse()
        else:
            self.make_dense()


    def make_sparse(self):
        # Make it sparse if it isn't already!
        assert self._mode_change_allowed
        if self._sparse == False:
            self.log('Switching to sparse mode')
            self._sparse_data = self.get_sparse_data()
            self._sparse = True
            del self._dense_data
        else:
            self.log('Did not switching to sparse mode, already in sparse mode!')

    def make_dense(self):
        # Make it dense if it isn't already!
        assert self._mode_change_allowed
        if self._sparse == True:
            self.log('Switching to dense mode')
            self._dense_data = self.get_dense_data()
            self._sparse = False
            del self._sparse_data
        else:
            self.log('Did not switching to dense mode, already in dense mode!')

    def get_sparse_data(self):
        if self._sparse: return self._sparse_data
        sparse = self._sparse_data_type()
        for idx, state in enumerate(self._dense_data):
            if state != self._bgstate:
                sparse[idx] = state
        return sparse


    def get_dense_data(self):
        if self._sparse:
            return self._dense_data_type([self[idx] for idx \
                                          in range(self._n)])
        else:
            return self._dense_data


    def crop(self):
        """ To be overloaded by specific Motif class"""
        pass

    def optimize(self):
        self.optimize_bgstate()
        self.set_optimal_dense_sparse_mode()


    def __str__(self):
        return str([self[x] for x in range(self._n)])

    def get_raster_line_coords(self, w, h,
                               screen_width,
                               screen_height):
        start, stop = [], []
        for x in range(w, screen_width, w):
            start.append((x, 0))
            stop.append((x, screen_height))
        for y in range(h, screen_width + 1, h):
            start.append((0, y))
            stop.append((screen_width, y))
        return zip(start, stop)

    def log(self, msg, lvl ='info'):
        if lvl == 'info':
            self.logger.info(msg)
        elif lvl == 'debug':
            self.logger.debug(msg)
        else:
            raise ValueError()

    # Useful ND method for use by subclasses
    def rotate(self):
        NotImplemented

    # Useful 2D method for use by subclasses
    def get_index_from_xy(self, x, y):
        """ Overload this with appropriate handling of
        self._dim and respect to _pbc """
        NotImplemented

    # Useful 2D method for use by subclasses
    def redefine_xy(self, x, y, new_state):
        self[self.get_index_from_xy(x, y)] = new_state

    # Useful 2D method for use by subclasses
    def query_xy(self, x, y):
        return self[self.get_index_from_xy(x, y)]


    # Useful 2D method for use by subclasses
    @property
    def minimal_rectangle_dense_data(self):
        NotImplemented

    # Useful 2D method for use by subclasses
    @property
    def minimal_rectangle_sparse_data(self):
        NotImplemented



class SquareGridMotif(Motif):

    @ExtendedInitDecoratorFactory(Motif, periodic = False)
    def __init__(self, *args, **kwargs):
        """
        Optional arguments in overloaded init:
        - `periodic`: Use periodic boundary conditions? (Default: True)
        """
        self._periodic = kwargs['periodic']


    @memoize
    def get_index_from_xy(self, x, y):
        """
        Get data index from x and y possibly using periodic
        boundary conditions. If not and a coordinate outside
        the boundaries is probed `None` will be returned.
        """
        if self._periodic:
            return (y % self._ny)*self._nx + x % self._nx
        else:
            if x >= self._nx or x < 0 \
                   or y < 0 or y >= self._ny:
                return INT_NAN # too bad integers dont support NaN
            return self._nx*y+x

    @memoize
    def get_nth_square_neighbour_indices(self, nth, idx):
        y = idx // self._nx
        x = idx % self._nx
        nxy1 = product(range(x-nth, x+nth+1), (y - nth, y + nth))
        nxy2 = product((x - nth, x + nth), range(y - nth + 1, y + nth))
        nidxs  =  map(self.get_index_from_xy,*zip(*(list(nxy1) + list(nxy2))))
        return [x for x in nidxs if x != INT_NAN]


    def set_dim(self, dim):
        Motif.set_dim(self, dim)
        self._nx, self._ny = dim
        self._n = self._nx * self._ny
        assert self._n % self._nx == 0
        assert self._n % self._ny == 0

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
                    'right':  zip([self._nx - 1 - depth] * self._ny,
                                  range(self._ny))
                    }.get(side)

        # Loop i to maximum crop depth
        reached_depth = -1
        for i in range(max([self._nx, self._ny])):
            for x, y in get_range(i):
                if self[self.get_index_from_xy(x, y)] != self._bgstate:
                    reached_depth = i
                    self.log("We reached depth %i in %s-side" % (i, side), 'debug')
                    break
            if reached_depth != -1:
                break
        if reached_depth > 0:
            x, y, width, height = 0, 0, self._nx, self._ny
            if side == 'top':
                y += reached_depth
                height -= reached_depth
            if side == 'bottom':
                height -= reached_depth
            if side == 'left':
                x += reached_depth
                width -= reached_depth
            if side == 'right':
                width -= reached_depth
            self.resize(x,y,width,height)

    def resize(self, xstart, ystart, width, height):
        self.log("Resizing to: %i, %i, %i, %i" % \
                     (xstart, ystart, width, height), 'debug')
        if self._sparse:
            new_sparse_data = {}
            for y in range(ystart, ystart + height):
                for x in range(xstart, xstart + width):
                    newx, newy = x - xstart, y - ystart
                    state = self[y*self._nx + x]
                    if state != self._bgstate:
                        new_sparse_data[newy * width + newx] = state
            self.__init__(sparse_data = new_sparse_data.items(),
                          dim = (width, height),
                          periodic = self._periodic)
        else:
            new_dense_data = []
            for y in range(ystart, ystart+height):
                for x in range(xstart, xstart+width):
                    new_dense_data.append(self[self.get_index_from_xy(x,y)])
            self.__init__(dense_data=new_dense_data,
                          dim=(width, height),
                          periodic = self._periodic)


    def crop(self):
        for side in ('top', 'bottom', 'left', 'right'):
            self.crop_side(side)

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
        return cls(dense_data=dense_data,nx=nx)

    def __str__(self):
        rows = []
        for rowi in range(self._ny):
            start, stop = rowi * self._nx, (rowi + 1) * self._nx
            rows.append(' '.join(map(str, self[start:stop])))
        return '\n'.join(rows)


class GameMotif(SquareGridMotif):

    @ExtendedInitDecoratorFactory(SquareGridMotif,
                                  game_rule_dict = None,
                                  state_colormap = None,
                                  button_action_map = None,
                                  )
    def __init__(self, *args, **kwargs):
        """
        Optional arguments in overloaded init:
        - `game_rule_dict`: Game rule dict mapping state to a list of
           counting rule instances.
        - `state_colormap`: Dicttionary mapping state to RGB tuples.
        """
        self.game_rule_dict = kwargs['game_rule_dict']
        if self.game_rule_dict == None:
            raise ValueError("You must provide a game_rule_dict")
        self.state_colormap = kwargs['state_colormap']
        self.button_action_map = kwargs['button_action_map']
        if self.state_colormap == None:
            self.state_colormap = dict([(i, (i, i, i)) for i in range(256)])
        self.propagate_dense = self.propagate_generic
        self.propagate_sparse =  self.propagate_generic
        self.game_rule_dict.bind_to_motif(self)
        self._old = {} # Remember last changes one step back

    def click(self, buttons, ix, iy):
        if buttons in self.button_action_map:
            self[self.get_index_from_xy(ix, iy)] = \
               self.button_action_map[buttons]

    def get_color(self, index):
        return self.state_colormap[self[index]]

    def get_possibly_affected_neigh_idxs(self, index):
        pan_idxs = set() # Possibly affected neighbour indices
        for state, state_rule_list in self.game_rule_dict.items():
            for counting_rule in state_rule_list:
                if index in self._old:
                    # For states that changed last propagate
                    # we might not catch default outcomes
                    # by only looking at wheter the new state is
                    # actively counted or not
                    if counting_rule.counted_state == self._old[index]:
                        map(pan_idxs.add, counting_rule.get_neigh_idxs(index))
                if counting_rule.counted_state == self[index]:
                    map(pan_idxs.add, counting_rule.get_neigh_idxs(index))
        return pan_idxs

    def propagate_generic(self):
        self.log('Entering propagate_generic', 'debug')
        con_idxs = set() # Considered indices
        prop_chngs = []  # List of (idx, new_state) items
        for chg_idx in self._changed_since_propagate:
            con_idxs.add(chg_idx)
            map(con_idxs.add, self.get_possibly_affected_neigh_idxs(chg_idx))
        self.log('Considering indices in propagate: %s' % con_idxs, 'debug')
        for con_idx in con_idxs:
            outcome = None
            for counting_rule in self.game_rule_dict[self[con_idx]]:
                outcome = counting_rule.match(con_idx)
                self.log('At index %i, considering counting_rule: %s, gave outcome: %s' % \
                             (con_idx, counting_rule, outcome), 'debug')
                if outcome != None:
                    if outcome != self[con_idx]:
                        prop_chngs.append((con_idx, outcome))
                        break
                    else:
                        # Rule matched but its ideompotent
                        break
            if outcome == None:
                # No counting rules matched
                outcome = self.game_rule_dict[self[con_idx]].default_outcome
                if outcome != self[con_idx]:
                    prop_chngs.append((con_idx, outcome))
        self._changed_since_propagate.clear()
        self._old = {} # Remember last changes one step back
        for idx, state in prop_chngs:
            self._old[idx] = self[idx]
            self[idx] = state

        if self._save_history:
            self._history.append(self._old.items())


