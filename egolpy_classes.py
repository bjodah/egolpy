#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division

import sys,pygame,json

from copy import copy
from itertools import product

if sys.version[0] == '3':
    # For Python 3 compability
    imap = map
    xrange = range
else:
    from itertools import imap

BLACK = (  0,   0,   0)
GREY  = (150, 150, 150)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)

# se: south east
motifs_str = {'glider_se': """
010
001
111
"""}

motifs = {}
for k in motifs_str:
    segms = motifs_str[k].split()
    mnx = len(segms[0])
    data = [int(x) for x in ''.join(segms)]
    motifs[k] = (data, mnx)

class StateMap(object):
    """
    StateMap class to be useful to games of
    the same kind as Conway's Game of Life
    """
    def __init__(self, nx, ny, data=None, default_state=0, pbc=False,
                 nth_neighbour_indices=None, might_be_affected_i=None,
                 largest_neighbour_distance=1):
        self._nx, self._ny = nx, ny
        self._n = nx * ny
        self._default_state = default_state
        self._largest_neighbour_distance = largest_neighbour_distance
        if data:
            self._data = data
        else:
            self._data = [self._default_state]*(self._nx*self._ny)

        self._pbc = pbc # Periodic boundary conditions
        if nth_neighbour_indices:
            self.nth_neighbour_indices = nth_neighbour_indices
        else:
            self.nth_neighbour_indices = [list() for x in range(self._largest_neighbour_distance)]
            for nth_m1 in range(self._largest_neighbour_distance):
                for index in range(self._n):
                    self.nth_neighbour_indices[nth_m1].append(\
                        self.get_nth_neighbour_indices(index, nth_m1+1))

        self._redefined_i = []
        if might_be_affected_i:
            self._might_be_affected_i = might_be_affected_i
        else:
            self._might_be_affected_i = range(self._n)

    def __copy__(self):
        return StateMap(self._nx, self._ny, self._data[:], None, self._pbc,
                        self.nth_neighbour_indices, self._might_be_affected_i)

    def get_nr_matching_nth_neighbours_i(self, i, match, nth):
        nr = 0
        for index in self.nth_neighbour_indices[nth-1][i]:
            if self.query_i(index) == match: nr += 1
        return nr

    def get_index_from_x_y(self, x, y):
        return y*self._nx+x

    def get_coord_from_index(self,i):
        return (i % self._nx, i // self._ny)

    def query_i(self, i):
        return self._data[i]

    def redefine_i(self, i, state):
        self._data[i] = state
        self._redefined_i.append(i)
        self._might_be_affected_i.append(i)
        for nth in range(1,self._largest_neighbour_distance):
            for index in self.nth_neighbour_indices[nth-1][i]:
                if not index in self._might_be_affected_i:
                    self._might_be_affected_i.append(index)


    def get_nth_neighbour_indices(self, i, nth):
        y = i // self._nx
        x = i % self._nx
        result = [-1]*((2*nth+1)**2-(2*(nth-1)+1)**2)
        j = 0
        for ox in range(x-nth, x+nth+1):
            for oy in (y-nth, y+nth):
                result[j] = self.get_data_index(ox, oy)
                j += 1
        for oy in range(y-nth+1, y+nth):
            for ox in (x-nth, y+nth):
                result[j] = self.get_data_index(ox, oy)
                j += 1
        if -1 in result:
            result = [x for x in result if x != -1]
        return result


    def get_data_index(self, x, y):
        """
        Returns -1 if self._pbc = False and out of bounds
        """
        if x >= 0 and x < self._nx:
            if y >= 0 and y < self._ny:
                return y*self._nx+x
            else:
                if self._pbc:
                    return self.get_data_index(x, y % self._ny)
                else:
                    return -1
        else:
            if self._pbc:
                return self.get_data_index(x % self._nx, y)
            else:
                return -1


    def save(self, outfile):
        ofh = open(outfile,'wt')
        dumpdata = [self._data[s:e] for s,e in \
                    zip(xrange(0,self._nx*(self._ny-1)+1,self._nx),
                        xrange(self._nx,self._nx*self._ny+1,self._nx))]
        json.dump(dumpdata,ofh)
        ofh.close()


    def load(self, infile):
        ifh = open(infile, 'rt')
        loaddata = json.load(ifh)
        ifh.close()
        self._data = []
        for segm in loaddata:
            self._data.extend(segm)
        self._redefined_i = range(self._n)
        self._might_be_affected_i = range(self._n)


    def get_redefined_i_since_last_call(self):
        tmp = copy(self._redefined_i)
        self._redefined_i = []
        return tmp


    def get_might_be_affected_i_since_last_call(self):
        tmp = copy(self._might_be_affected_i)
        self._might_be_affected_i = []
        return tmp


    def __str__(self):
        nx, ny = self._nx, self._ny
        rows = [self._data[start:stop] for (start,stop) in \
            zip(range(0,nx*(ny-1)+1,nx),range(nx,nx*ny+1,nx))]
        return "\n".join([" ".join([str(x) for x in row]) for row in rows])

    def put_motif_on_data(self, offset_coord, motif='glider_se'):
        data, mnx = motifs[motif]
        mny = len(data)//mnx
        for x in range(mnx):
            for y in range(mny):
                self.redefine_i(self.get_index_from_x_y(offset_coord[0]+x,
                                                        offset_coord[1]+y),
                                data[y*mnx+x])

def test_StateMap( nx=5, ny=5, pbc=True):

    state_map = StateMap(nx, ny, pbc=pbc, largest_neighbour_distance=2)
    state_map.put_motif_on_data((1,1), 'glider_se')
    print state_map
    print ''.join(['- ']*nx)
    for i in range(len(data)):
        print state_map.query_i(i),
        if (i+1) % nx == 0: print '\n',

    assert state_map.get_nr_matching_nth_neighbours_i(12,1,1) == 5
    assert state_map.get_nr_matching_nth_neighbours_i(12,1,2) == 0
    assert state_map.get_nr_matching_nth_neighbours_i(6,1,2) == 4

    def print_neighbours(center_i, nth):
        data_copy = copy(state_map._data)
        neighbour_indices =  state_map.get_nth_neighbour_indices(center_i, nth)
        for index in range(len(data_copy)):
            if not index in neighbour_indices:
                data_copy[index] = ' '

        for i in range(len(data_copy)):
            print data_copy[i],
            if (i+1) % nx == 0: print '\n',

    print ''.join(['- ']*nx)
    print_neighbours(12,1)

    print ''.join(['- ']*nx)
    print_neighbours(12,2)

    print ''.join(['- ']*nx)
    print_neighbours(6,1)

    print ''.join(['- ']*nx)
    print_neighbours(6,2)



class Game(object):
    """
    Remember to define a class variable 'std_rule_dict'
    """

    def __init__(self, nx, ny, pbc=False, rule_dict=None, default_state=0,
         colormap=None, button_action_map=None,
                 largest_neighbour_distance=1,
                 max_state=None):
        self._state = StateMap(nx, ny, default_state, pbc=pbc,
                               largest_neighbour_distance=\
                               largest_neighbour_distance)
        if rule_dict:
            self._rule_dict = self.compile_rule_dict(rule_dict)
        else:
            self._rule_dict = self.__class__.std_rule_dict

        if colormap:
            self._colormap = colormap
        else:
            self._colormap = self.__class__.std_colormap

        if button_action_map:
            self._button_action_map = button_action_map
        else:
            self._button_action_map = self.__class__.std_button_action_map

        if max_state:
            self._max_state = max_state
        else:
            self._max_state = max(self._rule_dict.keys())

        self.state_rules = self.compile_rule_dict(self.__class__.std_rule_dict)


    def compile_rule_dict(self, rules_dict):
        # Generate a GameRuleSet
        state_rules = [list() for dummy in range(self._max_state+1)]
        for state in range(self._max_state+1):
            # Generate a StateRuleSet
            rule_list, default_outcome = rules_dict[state]
            rules = []
            for rule_name, rule_args in rule_list:
                # Generate a CountingRule
                rules.append(counting_rule[rule_name](*rule_args))
            state_rules[state] = StateRuleSet(rules, default_outcome)
        return GameRuleSet(state_rules)

    def propagate(self):
        # Make a copy of the last state
        old_state = copy(self._state)

        # Loop over all cells
        might_have_been_affected_i = self._state.get_might_be_affected_i_since_last_call()
        for index in might_have_been_affected_i:
            cellstate = old_state.query_i(index)
            cur_state_rules, default_outcome = self._rules[cellstate]
            new_cellstate = None
            for rule in cur_state_rules:
                i0, ie, match, outcome = rule
                cumsum = 0
                for nth in range(i0, ie):
                    cumsum += old_state.get_nr_matching_nth_neighbours_i(index, match, nth)
                if cumsum in outcome:
                    new_cellstate = outcome[cumsum]
                    #print index, cumsum, cellstate, new_cellstate
                    if cellstate != new_cellstate:
                        self._state.redefine_i(index, new_cellstate)
                    break # Do not investigate any more rules
            if new_cellstate == None:
                new_cellstate = default_outcome
                if cellstate != new_cellstate:
                    self._state.redefine_i(index, new_cellstate)

    def __str__(self):
        return str(self._state)


class SumOfTypeGame(Game):
    """
    """

    def propagate(self):
        pass

class SumOfStateValuesGames(Game):
    """
    """

    def propagate(self):
        pass

def autodetect(folder):
    return {}

game_classes = {'sum_of_type': SumOfTypeGame,
              'sum_of_state': SumOfStateValuesGames}
contrib_folder = './contrib/'
auto_detected = autodetect(contrib_folder)
game_classes.update(auto_detected)


DEAD, ALIVE = 0, 1

def inverter(state, *args):
    return {DEAD: ALIVE,
        ALIVE: DEAD}.get(state)

def state_setter(state, *args):
    return args[0][0]


class GameRuleSet(object):
    """
    GameRuleSet contyainer class for StateRuleSet's
    """

    def __init__(self, state_rule_sets):
        """
        """
        self._state_rule_sets = state_rule_sets


class StateRuleSet(object):
    """
    Set of rules for a state
    """

    def __init__(self, rule_list, default_outcome):
        """
        A state has a ordered rule set
        """
        self._rule_list       = rule_list
        self.default_outcome = default_outcome

    def compile(self):
        pass



class CountingRule(object):
    """
    Rule class for egol
    """

    def __init__(self, neighbour_shell_indices):
        """
        """
        self._neighbour_shell_indices = neighbour_shell_indices

    def nth_neighbours_state_count(self, states):
        pass

    def nth_neighbours_state_sum(self, states):
        pass


class MatchingStateCountingRule(CountingRule):
    """
    Rule class for counting matching states
    """
    def nth_neighbours_state_count(self, states):
        return Counter(states)

    def nth_neighbours_state_sum(self, states):
        raise ValueError("Wrong counting rule applied!")


class SumStateValuesCountingRule(CountingRule):
    """
    Rule class for summing state values
    """
    def nth_neighbours_state_count(self, states):
        raise ValueError("Wrong counting rule applied!")

    def nth_neighbours_state_sum(self, states):
        return sum(states)

counting_rules = {'matching_state':    MatchingStateCountingRule,
                  'sum_state_values':  SumStateValuesCountingRule}


class NeighbourIndexRule(object):
    """
    Derive subclasses for specific topologies
    """
    def __init__(self, dimensions):
        pass

    def get_nth_neighbour_indices_at_i(nth, i):
        pass

    def get_nr_neighbours_in_nth_shell(nth):
        pass

class TwoDimPeriodicTorusSquareGrid(NeighbourIndexRule):
    pass


class Gol(Game):
    """
    Conway's Game of Life
    http://en.wikipedia.org/wiki/Conway%27s_Game_of_Life

    Rules of Conway's game of life:

        1. Any live cell with fewer than two live
           neighbours dies, as if caused by under-population.
        2. Any live cell with two or three live neighbours
           lives on to the next generation.
        3. Any live cell with more than three live neighbours
           dies, as if by overcrowding.
        4. Any dead cell with exactly three live neighbours
           becomes a live cell, as if by reproduction.

    """
    std_rule_dict = {DEAD:  ([
                              (1,2,ALIVE, {3: ALIVE}),     # Rule 4.
                             ], DEAD),     # Note: range(1,2) == [1]
                     ALIVE: ([
                              (1,2,ALIVE, {2: ALIVE, # Rule 2
                                           3: ALIVE}), # Rule 2
                             ], DEAD),   # catches rule 1 and 3
                     }


    std_colormap = {ALIVE: WHITE,
            DEAD: BLACK}


    std_button_action_map = {(1,0,0): ('state_setter',
                                       (ALIVE,)
                                       ),
                             (0,0,1): ('state_setter',
                                       (DEAD,)
                                       ),
                             }

    actions = {'inverter':     inverter,
               'state_setter': state_setter}

    def __init__(self, nx, ny, pbc=False, rules=None,
                 colormap=None, button_action_map=None,
                 largest_neighbour_distance=1):
        default_state = DEAD
        super(self.__class__, self).__init__(nx,
                                  ny,
                                  pbc,
                                  rules,
                                  default_state,
                                  colormap,
                                  button_action_map,
                                  largest_neighbour_distance)


    def get_color(self, i):
        return self._colormap[self._state.query_i(i)]


    def click(self, buttons, x, y):
        """
        Give the user the ability to kill or
        create live cells by clicking
        """
        cur_state   = self._state.query_i(self._state.get_index_from_x_y(x, y))
        action_name = self._button_action_map[buttons][0]
        action      = self.__class__.actions[action_name]
        action_args = self._button_action_map[buttons][1]
        new_state   = action(cur_state, action_args)
        self._state.redefine_i(self._state.get_index_from_x_y(x, y), new_state)

    def __str__(self):
        return self._state.__str__()


def test_Gol(pbc=True):
    game = Gol(5,5,pbc=pbc)
    game._state.put_motif_on_data((1,1),'glider_se')
    print game
    game.propagate()
    print ''.join(['-']*10)
    print game
    game.propagate()
    print ''.join(['-']*10)
    print game
    game.propagate()
    print ''.join(['-']*10)
    print game


class GamePlan(object):
    """
    gameplan class for use with pygame and games of
    the kind of Conway's Game of Life
    """
    def __init__(self, nobj, screen_res, pbc=False, GameCls=Gol, rules=None,
             colormap=None, button_action_map=None,
                 largest_neighbour_distance=1):
        self._nobj       = nobj
        self._screen_res = screen_res
        self._game       = GameCls(nobj[0], nobj[1], pbc,
                             rules, colormap, button_action_map,
                             largest_neighbour_distance)
        self._screen     = pygame.display.set_mode(self._screen_res)
        self._w          = screen_res[0] // nobj[1]
        self._h          = screen_res[1] // nobj[1]
        self._rect       = [0]*(nobj[0]*nobj[1])
        for x, y in self.all_coords:
            self._rect[y*nobj[0]+x] = pygame.Rect(self._w*x+1,
                                                  self._h*y+1,
                                                  self._w-1,
                                                  self._h-1)
        self.draw_init()
        self._clicklist = []

    def save(self, outfile):
        self._game._state.save(outfile)

    def load(self, infile):
        self._game._state.load(infile)

    def propagate(self):
        self.execute_clicks()
        self._game.propagate()

    def draw_init(self):
        self._screen.fill(BLACK)
        for x in range(self._w, self._screen_res[0]+1,self._w):
            pygame.draw.line(self._screen, GREY, (x,0), (x,self._screen_res[1]))
        for y in range(self._h,self._screen_res[1]+1,self._h):
            pygame.draw.line(self._screen, GREY, (0,y), (self._screen_res[0],y))
        pygame.display.flip()
    def draw(self):
        redefined_i = self._game._state.get_redefined_i_since_last_call()
        if redefined_i == []: return None
        for index in redefined_i:
            pygame.draw.rect(self._screen, self._game.get_color(index),
                             self._get_rect(index))
        pygame.display.flip()

    def click(self, buttons, screen_x, screen_y):
        ix, iy = screen_x // self._w, screen_y // self._h
        if not (ix, iy) in self._clicklist:
            self._clicklist.append((buttons, ix, iy))

    def execute_clicks(self):
        for clicked in self._clicklist:
            self._game.click(*clicked)
        self._clicklist = []

    def _get_rect(self, index):
        return self._rect[index]

    @property
    def all_coords(self):
        return map(self._game._state.get_coord_from_index,
                   range(self._game._state._n))

