#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

import sys
from collections import Counter
from itertools import product

try:
    import cPickle as pickle
except ImportError:
    import pickle

from project_helpers import ExtendedInitDecoratorFactory

INT_NAN = None


#Logging
import logging
logging.basicConfig()
logger = logging.getLogger('motif')
logger.setLevel(logging.INFO)


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

        self.set_dim(dim) # stores self._dim and sets: self._n

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
                             "for specialized propagate, no " + \
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
            if hasattr(self._dense_data, 'propagate'):
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
                return INT_NAN # too bad integers dont support NaN
            return self._nx*y+x

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
                    logger.debug("We reached depth %i in %s-side", i, side)
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
        logger.debug("Resizing to: %i, %i, %i, %i",
                     xstart, ystart, width, height)
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


def test_SquareGridMotif(nx = 5, ny = 6):
    sgm = SquareGridMotif(periodic = True,
                          dim = (nx, ny))
    print(sgm)
    print('-'*(2 * nx - 1))
    sgm.redefine_xy(1, 1, 1)
    sgm.redefine_xy(2, 2, 1)
    sgm.redefine_xy(3, 3, 1)
    sgm.redefine_xy(3, 4, 1)
    sgm.redefine_xy(2, 4, 1)
    sgm.redefine_xy(1, 4, 1)
    print(sgm)
    print('-'*(2 * nx - 1))
    sgm.crop()
    print(sgm)
    print('-'*(2 * nx - 1))
    sgm.crop()
    print(sgm)
    print('-'*(2 * nx - 1))



class GameMotif(SquareGridMotif):

    @ExtendedInitDecoratorFactory(SquareGridMotif,
                                  game_rule_dict = None,
                                  state_color_map = None,
                                  )
    def __init__(self, *args, **kwargs):
        """
        Optional arguments in overloaded init:
        - `game_rule_dict`: Game rule dict mapping state to a list of
           counting rule instances.
        - `state_color_map`: Dicttionary mapping state to RGB tuples.
        """
        self.game_rule_dict = kwargs['game_rule_dict']
        if self.game_rule_dict == None:
            raise ValueError("You must provide a game_rule_dict")
        self.state_color_map = kwargs['state_color_map']
        if self.state_color_map == None:
            self.state_color_map = dict([(i, (i, i, i)) for i in range(256)])
        self.propagate_dense = self.propagate_generic
        self.propagate_sparse =  self.propagate_generic
        self.game_rule_dict.bind_to_motif(self)
        self._old = {} # Remember last changes one step back


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
        logger.debug('Entering propagate_generic')
        con_idxs = set() # Considered indices
        prop_chngs = []  # List of (idx, new_state) items
        for chg_idx in self._changed_since_propagate:
            con_idxs.add(chg_idx)
            map(con_idxs.add, self.get_possibly_affected_neigh_idxs(chg_idx))
        logger.debug('Considering indices in propagate: %s', con_idxs)
        for con_idx in con_idxs:
            for counting_rule in self.game_rule_dict[self[con_idx]]:
                outcome = counting_rule.match(con_idx)
                logger.debug('At index %i, considering counting_rule: %s, gave outcome: %s',
                             con_idx, counting_rule, outcome)
                if outcome != None:
                    if outcome != self[con_idx]:
                        prop_chngs.append((con_idx, outcome))
                        break
                    else:
                        # Rule matched but its ideompotent
                        break
            if outcome ==  None:
                # No counting rules matched
                outcome = self.game_rule_dict[self[con_idx]].default_outcome
                if outcome != self[con_idx]:
                    prop_chngs.append((con_idx, outcome))
        self._changed_since_propagate.clear()
        self._old = {} # Remember last changes one step back
        for idx, state in prop_chngs:
            self._old[idx] = self[idx]
            self[idx] = state

class GameRuleDict(dict):
    def bind_to_motif(self, motif):
        self._motif = motif
        for state, state_rule_list in self.items():
            state_rule_list.bind_to_motif(motif)

def test_GameRuleDict():
    grd = GameRuleDict({'a': 1, 'b': 2})
    assert hasattr(grd, 'bind_to_motif')
    assert grd['a'] == 1
    assert grd['b'] == 2
    assert grd.get('c', None) == None


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
        self.reverse_map = None

    def bind_to_motif(self, motif):
        self._motif = motif
        for counting_rule in self:
            counting_rule.bind_to_motif(motif)


def test_StateRuleList():
    srl = StateRuleList([1, 2, 3], 7)
    assert srl.default_outcome == 7
    assert srl[:] == [1, 2, 3]


class NeigbourCounting(object):
    pass


class CountingRule(object):
    """
    Rule class for egol
    """

    def __init__(self, counted_state, neighbour_indexing_rule,
                 count_outcomes):
        """
        """
        self.counted_state = counted_state
        self._neighbour_indexing_rule = neighbour_indexing_rule
        self._count_outcomes = count_outcomes

    def bind_to_motif(self, motif):
        self._motif = motif
        self._neighbour_indexing_rule.bind_to_motif(motif)

    def count(self, index):
        states = [self._motif[x] for x in self._neighbour_indexing_rule.get_neigh_idxs(index)]
        return Counter(states)[self.counted_state]

    def match(self, index):
        nr = self.count(index)
        return self._count_outcomes.get(nr, None)

    def get_neigh_idxs(self, index):
        return self._neighbour_indexing_rule.get_neigh_idxs(index)

    def __str__(self):
        fmtstr = "CountingRule({},{},{})"
        return fmtstr.format(self.counted_state, self._neighbour_indexing_rule, self._count_outcomes)

class NeighbourIndexingRule(object):
    def __init__(self, *args):
        pass

    def __str__(self):
        pass

class SquareNeighbourhoodShellIndexingRule(NeighbourIndexingRule):
    """
    TODO:
    Implement caching?
    """

    def __init__(self, shell_idxs):
        self._shell_idxs = shell_idxs
        self._motif = None

    def bind_to_motif(self, motif):
        assert isinstance(motif, SquareGridMotif)
        self._motif = motif

    def get_neigh_idxs(self, index):
        result = []
        for shell_idx in self._shell_idxs:
            result.extend(self._motif.get_nth_square_neighbour_indices(shell_idx, index))
        return result

    def __str__(self):
        return "<SqNeighShIdxRl({})>".format(self._shell_idxs)

def test_SquareNeighbourhoodShellIndexingRule():
    snsir = SquareNeighbourhoodShellIndexingRule([1])
    motif = SquareGridMotif(sparse_data= {5: 1, 6: 1, 9: 1, 10: 1}.items(),
                            dim = (4, 4))
    snsir.bind_to_motif(motif)
    neigh7 = snsir.get_neigh_idxs(7)
    count = 0
    for ni in neigh7:
        print(motif[ni])
        count += 1 if motif[ni] == 1 else 0
    print(count)
    print(motif)
    print(neigh7)
    for ni in neigh7:
        motif[ni] = 2
    print(motif)


def get_gol_rule_dict():
    DEAD, ALIVE = range(2)
    gol_rule_dict =  GameRuleDict({
        DEAD: StateRuleList(
            [
                CountingRule(ALIVE,
                             SquareNeighbourhoodShellIndexingRule([1]),
                             {3: ALIVE})
                ],
            DEAD),
        ALIVE: StateRuleList(
            [
                CountingRule(ALIVE,
                             SquareNeighbourhoodShellIndexingRule([1]),
                             {2: ALIVE, 3: ALIVE}),
                ],
            DEAD)
        })
    return gol_rule_dict

def get_gol_colormap():
    DEAD, ALIVE = range(2)
    BLACK, WHITE = (0, 0, 0), (255, 255, 255)
    return {DEAD: BLACK, ALIVE: WHITE}

def test_full_scale(nx = 4, ny = 4, sparse_data = {5: 1, 6: 1, 9: 1, 10: 1}):
    gol_rule_dict = get_gol_rule_dict()
    gol_motif = GameMotif(sparse_data     = sparse_data.items(),
                          game_rule_dict  = gol_rule_dict,
                          state_color_map = {DEAD:  BLACK,
                                             ALIVE: WHITE},
                          periodic        = True,
                          dim             = (nx, ny),
                          )
    print(gol_motif)
    print('-' * (2 * gol_motif._nx - 1))
    for k in sparse_data.keys():
        assert k in gol_motif._changed_since_propagate
    pani = gol_motif.get_possibly_affected_neigh_idxs(5)
    print(pani)
    for i in [0, 1, 2, 4, 6, 8, 9, 10]:
        assert i in pani
    gol_motif.propagate()
    # print(gol_motif)
    # print('-' * (2 * gol_motif._nx - 1))
    gol_motif.propagate()
    # print(gol_motif)
    # print('-' * (2 * gol_motif._nx - 1))
    for idx, state in enumerate([0, 0, 0, 0,
                                 0, 1, 1, 0,
                                 0, 1, 1, 0,
                                 0, 0, 0, 0,]):
        assert gol_motif[idx] == state


def test_glider(nx = 6, ny = 6):
    dense_data = map(int, """0 0 0 0 0 0
                             0 0 1 0 0 0
                             0 0 0 1 0 0
                             0 1 1 1 0 0
                             0 0 0 0 0 0
                             0 0 0 0 0 0""".split())
    BLACK, WHITE = (0, 0, 0), (255, 255, 255)
    DEAD, ALIVE = range(2)
    gol_rule_dict =  GameRuleDict({
        DEAD: StateRuleList(
            [
                CountingRule(ALIVE,
                             SquareNeighbourhoodShellIndexingRule([1]),
                             {3: ALIVE})
                ],
            DEAD),
        ALIVE: StateRuleList(
            [
                CountingRule(ALIVE,
                             SquareNeighbourhoodShellIndexingRule([1]),
                             {2: ALIVE, 3: ALIVE}),
                ],
            DEAD)
        })

    gol_motif = GameMotif(dense_data      = dense_data,
                          game_rule_dict  = gol_rule_dict,
                          state_color_map = {DEAD:  BLACK,
                                             ALIVE: WHITE},
                          periodic        = True,
                          dim             = (nx, ny),
                          )
    # print(gol_motif)
    # print('-' * (2 * gol_motif._nx - 1))

    for i in range(24):
        gol_motif.propagate()
        # print(gol_motif)
        # print('-' * (2 * gol_motif._nx - 1))

    for idx, state in enumerate(dense_data):
        assert gol_motif[idx] == state
