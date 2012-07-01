#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

import sys
from collections import Counter

from bz2 import BZ2File

try:
    import cPickle as pickle
except ImportError:
    import pickle


#Logging
import logging
logging.basicConfig()
logger = logging.getLogger('motif')
logger.setLevel(logging.DEBUG)


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

        if sparse_data != None:
            # sparse_data provided
            self._sparse = True
            # make sure not also dense_data provided (ambigous)
            assert dense_data == None
        else:
            self._sparse = False

        # Determine whether provided types provide own
        # propagate methods:
        if mode_change_allowed == True:
            # We might switch between sparse and dense
            if hasattr(self._dense_data_type, 'propagate') and \
               hasattr(self._sparse_data_type, 'propagate'):
                logger.debug("Both sparse and dense data " + \
                             "types support propagate " + \
                             "specialized methods will be used.")
                self._specialized_propagate = True
            else:
                logger.debug("At least one of the sparse and " + \
                             "densedata types lack support " + \
                             "for specialized propagate, no" + \
                             "specialized methods will be used.")
                self._specialized_propagate = False
        else:
            # We will never switch between sparse and dense
            if self._sparse:
                logger.debug("We are sparse and always will be" + \
                             ".  Specialized methods will be used.")
                if hasattr(self._sparse_data_type, 'propagate'):
                    self._specialized_propagate = True
                else:
                    self._specialized_propagate = False
            else:
                logger.debug("We are dense and always will be" + \
                             ".  Specialized methods will be used.")
                if hasattr(self._dense_data_type, 'propagate'):
                    self._specialized_propagate = True
                else:
                    self._specialized_propagate = False

        # Now store bgstate
        self._bgstate = bgstate

        if not self._specialized_propagate:
            # To facilitate efficient propagate methods of subclasses
            # a list is maintained on what cells have been changed
            # since last invocation of propagate
            self._changed_since_propagate = set()

        if self._sparse:
            self._sparse_data = self._sparse_data_type()
            for idx, state in sparse_data:
                self[idx] = state
        else:
            # no sparse_data provided
            if dense_data != None:
                self._dense_data = self._dense_data_type(\
                    dense_data)
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

        self.set_dim(dim) # stores self._dim and sets: self._n

        # Make a state count Counter and store as:
        # self._state_counter
        self.recount_states()

        # Decide optimal mode of operation (dense/sparse) and set:
        # self._sparse = True/False, where False -> dense mode
        self.set_optimal_dense_sparse_mode()


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
            if hasattr(self._sparse_data, 'propagate'):
                changes = self._sparse_data.propagate()
                self._changed_since_propagate.clear()
                map(self.update_count, *zip(*changes))
            else:
                self.propagate_sparse()
        else:
            if hasttr(self._dense_data, 'propagate'):
                changes = self._dense_data.propagate()
                self._changed_since_propagate.clear()
                map(self.update_count, *zip(*changes))
            else:
                self.propagate_dense()

    def propagate_sparse(self):
        """ To be overloaded """
        NotImplemented

    def propagate_dense(self):
        """ To be overloaded """
        NotImplemented

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

    def __getitem__(self, index):
        if self._sparse:
            if index > self._n:
                raise IndexError('Out of bounds')
            return self._sparse_data.get(index, self._bgstate)
        else:
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
    #def redefine(self, index, new_state):
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
            logger.debug('Setting new bgstate: %i', self._bgstate)
            self._bgstate = most_occuring_state

    def set_optimal_dense_sparse_mode(self):
        if not self._mode_change_allowed: return None
        # TODO: Confirm 75% break-even dense vs. sparse
        if self._state_counter[self._bgstate] \
               > (self._n // 4 * 3):
            # Make it sparse if it isn't already!
            if self._sparse == False:
                logger.debug('Switching to sparse mode')
                self._sparse_data = self.get_sparse_data()
                self._sparse = True
                del self._dense_data
        else:
            # Make it dense if it isn't already!
            if self._sparse == True:
                logger.debug('Switching to dense mode')
                self._dense_data = self.get_dense_data()
                self._sparse = False
                del self._sparse_data


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


def test_Motif():
    m = Motif(0, dense_data = range(5))
    del m[3]
    print(m)
    del m[1]
    del m[4]
    print(m)
    print('sparse', m._sparse)
    print('state count: ', m._state_counter)
    print('optimizing...  ')
    m.optimize()
    print('sparse', m._sparse)
    print('recounting states... ')
    m.recount_states()
    print('state count: ', m._state_counter)
    print('optimizing...  ')
    m.optimize()
    print('sparse', m._sparse)
    print('state count: ', m._state_counter)
    del m[0]
    m[2] = 2
    m[4] = 99
    m.optimize()
    m[3] = 99
    del m[2]
    print(m)
    print(m._state_counter)


class ExtendedInitDecoratorFactory:

    def __init__(self, superclass, **intercept_kwargs):
        self._superclass      = superclass
        self.intercept_kwargs = intercept_kwargs

    def __call__(self, init):
        def wrapper(_self, *args, **kwargs):
            intercepted_kwargs = {}
            for k, v in self.intercept_kwargs.iteritems():
                if key in kwargs:
                    intercept_kwargs[key] = kwargs.pop(key)
                else:
                    intercept_kwargs[key] = v
            super(_self.__class__, _self).__init__( *args, **kwargs)
            init(**intercepted_kwargs) # Need _self here?
        wrapper.__name__ = init.__name__
        wrapper.__doc__ = init.__doc__ + '\n Docstring of overloaded init: \n'+\
                          self._superclass.__init__.__doc__
        return wrapper

class SquareGridMotif(Motif):

    @ExtendedInitDecoratorFactory(Motif, periodic = False)
    def __init__(self, *args, **kwargs):
        """
        Optional arguments in overloaded init:
        - `periodic`: Use periodic boundary conditions? (Default: True)
        """
        self._periodic = kwargs['periodic']


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
                return None # too bad integers dont support NaN
            return self._nx*y+x

    def get_nth_square_neighbour_indices(nth, idx):
        y = i // self._nx
        x = i % self._nx
        result = [-1]*((2*nth+1)**2-(2*(nth-1)+1)**2)
        j = 0
        for ox in range(x-nth, x+nth+1):
            for oy in (y-nth, y+nth):
                result[j] = self.get_index_from_xy(ox, oy)
                j += 1
        for oy in range(y-nth+1, y+nth):
            for ox in (x-nth, y+nth):
                result[j] = self.get_index_from_xy(ox, oy)
                j += 1
        if -1 in result:
            result = [x for x in result if x != -1]
        return result

    def set_dim(self, dim):
        super(self.__class__, self).set_dim(dim)
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
                    'right':  zip(range(self._ny),
                                  [self._nx-1-depth]*self._ny),
                    }.get(side)

        # Loop i to maximum crop depth
        reached_depth = -1
        for i in range(max([self._nx, self._ny])):
            for x, y in ranges[side]:
                if self[self.get_index_from_xy(x, y)] != self._bgstate:
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
                    new_dense_data.append(self[self.get_index_from_xy(x,y)])
            self.__init__(dense_data=new_dense_data,
                          nx=width)


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




class GameMotif (SquareGridMotif):

    @ExtendedInitDecoratorFactory(SquareGridMotif,
                                  game_rule_dict = None,
                                  state_color_map = None,
                                  )
    def __init__(self, *args, **kwargs):
        """
        Optional arguments in overloaded init:
        - `game_rule_dict`: Game rule set specifying the rules of the game
        - `state_color_map`: Dicttionary mapping state to RGB tuples.
        """
        self.game_rule_dict =  game_rule_dict
        if self.game_rule_dict == None:
            raise ValueError("You must provide a game_rule_dict")
        self.state_color_map = state_color_map
        if self.state_color_map == None:
            self.state_color_map = dict([(i, (i, i, i)) for i in range(256)])
        self._periodic = kwargs['periodic']


    def get_max_neigh_idxs(self, index):
        max_neigh_idxs = set()
        for counting_rule in self.game_rule_dict[self[index]]:
            max_neigh_idxs.add(counting_rule.get_neigh_idxs(index, self))

    def propagate_sparse(self):
        considered_indices = set()
        prop_chngs = []
        for chg_idx in self._changed_since_propagate:
            for neigh_idx in self.get_max_neigh_idxs(index):
                considered_indices.add(neigh_idx)
        for con_idx in considered_indices:
            state_rule = self.game_rule_dict[self[con_idx]]:
            for counting_rule in state_rule.counting_rules:
                outcome = counting_rule.match()
                if outcome != None:
                    if outcome != self[con_idx]:
                        prop_chngs.append((con_idx, outcome))
                        break
            if outcome ==  None:
                outcome = state_rule.default_outcome
                if outcome != self[con_idx]:
                    prop_chngs.append((con_idx, outcome))
        self._changed_since_propagate.clear()
        for idx, state in prop_chngs:
            self[idx] = state


    def propagate_dense(self):
        return self.propagate_sparse()

class StateRuleList(list):
    """
    Set of rules for a state
    """

    def __init__(self, counting_rule_list, default_outcome):
        """
        A state has a ordered rule set
        """
        super(self.__class__, self).__init__(counting_rule_list)
        self.default_outcome = default_outcome

    def get_neighbourhood_counts(self, neighhood_repr, motif):
        counter = Counter()
        for idx in self.neighhood[neighhood_repr]:
            counter[motif[idx]] += 1
        return counter

    def set_neighbourhoods(index, motif):
        for counting_rule in self.counting_rule_list:
            neighhood_repr = (index_gen,* args)
            if not neighhood_repr in self.neighhood:
                new_neighhood = counting_rule.get_neigh_idxs(index, motif)
                self.neighhood[neighhood_repr] = new_neighhood


class NeigbourCounting(object):
    pass

class CountingRule(object):
    """
    Rule class for egol
    """

    def __init__(self, match, neighbour_shell_indices, outcomes):
        """
        """
        self._neighbour_shell_indices = neighbour_shell_indices
        self._match = match
        self._outcomes = outcomes

    def count(self, motif):
        self._count = Counter([motif[x] for x in self._neighbour_shell_indices])

    def match(self, neighbourhood_count):
        for matching_nr, outcome_state in self._outcomes:
            if neighbourhood_count[self._match] == matching_nr:
                return outcome_state

        return self.outcomes.get(nr, None)

    def get_neigh_idxs(self, index, motif):
        pass

class MatchingStateCountingRule(CountingRule):
    """
    Rule class for counting matching states
    """

    def __init__(self, neighbour_shell_indices, matching):

    def nth_neighbours_state_count(self, nth, motif):
        self._neighbour_shell_indices


    def nth_neighbours_state_sum(self, states):
        raise ValueError("Wrong counting rule applied!")


DEAD, ALIVE = range(2)
game_of_life_rule_dict = {DEAD: dead_state_rule_list,
                          ALIVE: alive_state_rule_list,}

Gol = GameMotif
