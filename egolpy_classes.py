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


class StateMap(object):
    """
    StateMap class to be useful to games of
    the same kind as Conway's Game of Life
    """
    def __init__(self, nx, ny, data=None, default_state=0, pbc=False,
                 nth_neighbour_coordinates=None,
                 largest_neighbour_distance=1):
        self._nx, self._ny = nx, ny
        self._default_state = default_state
        self._largest_neighbour_distance = largest_neighbour_distance
        if data:
            self._data = data
        else:
            self._data = [self._default_state]*(self._nx*self._ny)

        self._pbc = pbc # Periodic boundary conditions
        self.nth_neighbour_coordinates = {}
        if nth_neighbour_coordinates:
            self.nth_neighbour_coordinates = nth_neighbour_coordinates
        else:
            for nth in range(1,self._largest_neighbour_distance+1):
                self.nth_neighbour_coordinates[nth] = {}
                for coord in self.all_indices:
                    self.nth_neighbour_coordinates[nth][coord] = \
                        self.get_nth_neighbour_coordinates(coord[0],
                                                       coord[1], nth)
        self._redefined = []
        self._non_might_be_affected = dict([(coord, False) for coord in
                                         self._redefined])
        self._all_might_be_affected = dict([(coord, True) for coord in\
                                        self.all_indices])
        self._might_be_affected = self._all_might_be_affected
    def __copy__(self):
        return StateMap(self._nx, self._ny, self._data[:], None, self._pbc, self.nth_neighbour_coordinates)

    def get_nr_matching_nth_neighbours(self, x, y, match, nth):
        nr = 0
        for ox, oy in self.nth_neighbour_coordinates[nth][(x, y)]:
            if self.query(ox, oy) == match: nr += 1
        return nr

    def query(self,x,y):
        if x < self._nx and x >= 0 and \
               y < self._ny and y >= 0:
            return self._data[y*self._nx+x]
        else:
            if self._pbc:
                # Periodic boundary conditions
                if x >= self._nx:
                    return self.query(x-self._nx,y)
                if x < 0:
                    return self.query(self._nx+x,y)
                if y >= self._ny:
                    return self.query(x,y-self._ny)
                if y < 0:
                    return self.query(x,self._ny+y)
            else:
                if x == self._nx or x == -1 or y == self._ny or y == -1:
                    return self._default_state
        raise ValueError("Out of bounds (x=%s, nx=%s, y=%s, ny=%s)." % (x,self._nx,y,self._ny))

    def redefine(self, x, y, state):
        self._data[y*self._nx+x] = state
        self._redefined.append((x,y))
        for coord in self.nth_neighbour_coordinates[\
            self._largest_neighbour_distance][(x, y)]:
            self._might_be_affected[coord] = True
        #print self._might_be_affected

    def get_nth_neighbour_coordinates(self, x, y, nth):
        result = []
        for ox in range(x-nth, x+nth+1):
            for oy in (y-nth, y+nth):
                entry = ox % self._nx, oy % self._ny
                if not entry in result:
                    result.append(entry)
        for oy in range(y-nth+1, y+nth):
            for ox in (x-nth, x+nth):
                entry = ox % self._nx, oy % self._ny
                if not entry in result:
                    result.append(entry)

        # for ox, oy in product(xrange(x-nth,x+nth+1), xrange(y-nth, y+nth+1)):
            # if not (ox == x and oy == y):
            #     entry = ox % self._nx, oy % self._ny
            #     if not entry in result:
            #         result.append(entry)
        return result

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
        self._redefined = list(self.all_indices)
        self._might_be_affected = self._all_might_be_affected

    @property
    def all_indices(self):
        return product(*imap(xrange, [self._nx,self._ny]))


    def get_redefined_since_last_call(self):
        tmp = copy(self._redefined)
        self._redefined = []
        return tmp

    def __str__(self):
        nx, ny = self._nx, self._ny
        rows = [self._data[start:stop] for (start,stop) in \
            zip(range(0,nx*(ny-1)+1,nx),range(nx,nx*ny+1,nx))]
        return "\n".join([" ".join([str(x) for x in row]) for row in rows])

#rules
# example_rules: {state0: <state 0 rules>, ... stateN: <state N rules> }
# state0_rules = {<n_neibours_between_distance_a_b_of_state_N>: (<n_state_outcome_map>, fallback_state)}
# <n_neighbours_distance_a_b_of_state_N> -> (a,b)
# <n_state_outcome_map> -> {0:0,1:0,2:1,3:1}

DEAD, ALIVE = 0, 1


class Game(object):
    """
    Remember to define a class variable 'std_rules'
    """

    def __init__(self, nx, ny, predefined_cells,
         pbc=False, rules=None, default_state=0,
         colormap=None, button_action_map=None,
                 largest_neighbour_distance=1):
        self._state = StateMap(nx, ny, default_state, pbc=pbc,
                               largest_neighbour_distance=\
                               largest_neighbour_distance)
        if rules:
            self._rules = rules
        else:
            self._rules = self.__class__.std_rules
            for cx, cy, state in predefined_cells:
                self._state.redefine(cx, cy, state)
        if colormap:
            self._colormap = colormap
        else:
            self._colormap = self.__class__.std_colormap
        if button_action_map:
            self._button_action_map = button_action_map
        else:
            self._button_action_map = self.__class__.std_button_action_map


    def propagate(self):
        # Make a copy of the last state
        old_state = copy(self._state)

        # Loop over all cells
        might_have_been_affected = copy(self._state._might_be_affected)
        self._state._might_be_affected = self._state._non_might_be_affected
        for coord, maybe_affected in might_have_been_affected.items():
            if not maybe_affected: continue
            x, y = coord
            state = old_state.query(x,y)
            cur_state_rules, default_outcome = self._rules[state]
            new_state = None
            for rule in cur_state_rules:
                i0, ie, match, outcome = rule
                cumsum = 0
                for nth in range(i0, ie):
                    cumsum += old_state.get_nr_matching_nth_neighbours(x,
                                 y, match, nth)
                if cumsum in outcome:
                    new_state = outcome[cumsum]
                    if state != new_state:
                        self._state.redefine(x, y, new_state)
                    break # Do not investigate any more rules
            if new_state == None:
                new_state = default_outcome
                if state != new_state:
                    self._state.redefine(x, y, new_state)

            # for neighbour_criteria, outcome_map in \
            #         cur_rule.items():
            #     cumsum = 0
            # for nth in range(*neighbour_criteria[:2]):
            #     cumsum += old_state.\
            #           get_nr_matching_nth_neighbours(x,
            #              y,
            #              neighbour_criteria[2],
            #              nth)
            # self._state.redefine(x, y, outcome_map[0].get(cumsum,
            #                     outcome_map[1]))

def inverter(state, *args):
    return {DEAD: ALIVE,
        ALIVE: DEAD}.get(state)

def state_setter(state, *args):
    return args[0][0]

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
    std_rules = {DEAD:  ([
                   (1,2,ALIVE, {3: ALIVE}),     # Rule 4.
                 ], DEAD),     # Note: range(1,2) == [1]
         ALIVE: ([
                   (1,2,ALIVE, {2: ALIVE, # Rule 2
                                3: ALIVE}), # Rule 2
                 ], DEAD),   # catches rule 1 and 3
             }


# {DEAD:{(1,2,ALIVE): ({3: ALIVE},  # Rule 4.
#                      DEAD)},    # Note: range(1,2) == [1]
#          ALIVE:{(1,2,ALIVE): ({2: ALIVE, # Rule 2
#                        3: ALIVE} # Rule 2
#                       ,DEAD)},   # catches rule 1 and 3
#          }

    std_colormap = {ALIVE: WHITE,
            DEAD: BLACK}


    std_button_action_map = {(1,0,0): ('state_setter',
                                   (ALIVE,)
                                   ),
                     (0,0,1): ('state_setter',
                                   (DEAD,)
                                   ),}

    actions = {'inverter': inverter,
               'state_setter': state_setter}

    def __init__(self, nx, ny, alive_cells, pbc=False, rules=None,
             colormap=None, button_action_map=None,
                 largest_neighbour_distance=1):
        predefined_cells = [(x, y, ALIVE) for x,y in alive_cells]
        default_state = DEAD
        super(self.__class__, self).__init__(nx,
                                  ny,
                                  predefined_cells,
                                  pbc,
                                  rules,
                                  default_state,
                                  colormap,
                                  button_action_map,
                                  largest_neighbour_distance)


    def get_color(self, x, y):
        return self._colormap[self._state.query(x, y)]


    def click(self, buttons, x, y):
        """
        Give the user the ability to kill or
        create live cells by clicking
        """
        cur_state   = self._state.query(x, y)
        action_name = self._button_action_map[buttons][0]
        action      = self.__class__.actions[action_name]
        action_args = self._button_action_map[buttons][1]
        new_state   = action(cur_state, action_args)
        self._state.redefine(x, y, new_state)

    def __str__(self):
        return self._state.__str__()

    @property
    def all_indices(self):
        return self._state.all_indices

class GamePlan(object):
    """
    gameplan class for use with pygame and games of
    the kind of Conway's Game of Life
    """
    def __init__(self, nobj, screen_res, alive_cells=[],
                 pbc=False, GameCls=Gol, rules=None,
             colormap=None, button_action_map=None,
                 largest_neighbour_distance=1):
        self._nobj       = nobj
        self._screen_res = screen_res
        self._game       = GameCls(nobj[0], nobj[1], alive_cells, pbc,
                             rules, colormap, button_action_map,
                             largest_neighbour_distance)
        self._screen     = pygame.display.set_mode(self._screen_res)
        self._w          = screen_res[0] // nobj[1]
        self._h          = screen_res[1] // nobj[1]
        self._rect       = [0]*(nobj[0]*nobj[1])
        for x, y in self.all_indices:
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
        #self._screen.fill(BLACK)
        redefined = self._game._state.get_redefined_since_last_call()
        if redefined == []: return None
        for x,y in redefined:#all_indices:
            pygame.draw.rect(self._screen, self._game.get_color(x,y), self._get_rect(x,y))
        pygame.display.flip()

    def click(self, buttons, screen_x, screen_y):
        ix, iy = screen_x // self._w, screen_y // self._h
        if not (ix, iy) in self._clicklist:
            self._clicklist.append((buttons, ix, iy))

    def execute_clicks(self):
        for clicked in self._clicklist:
            self._game.click(*clicked)
        self._clicklist = []

    def _get_rect(self, x, y):
        return self._rect[y*self._nobj[0]+x]

    @property
    def all_indices(self):
        return self._game.all_indices
