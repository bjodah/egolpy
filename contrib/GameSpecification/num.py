#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Written by Björn Dahlgren
"""

from contrib.GameSpecification import BaseClass

from rules import StateRuleList, CountingRule, SquareNeighbourhoodShellIndexingRule, GameRuleDict

class Num(BaseClass.GameSpecification):

    max = 0
    low_state_reach = 0
    mid_state_reach = 2
    high_state_reach = 0

    low_add = 1
    mid_add = 2
    high_add = 3

    _def_decr = 1
    low_nr_range = range(2, 4)
    mid_nr_range = range(2, 4)
    high_nr_range = range(2, 4)

    def __init__(self):
        self.post_init()

    def post_init(self):
        self.rule_dict = GameRuleDict(dict([(x, self[x]) for x in range(self.max)]))
        self.colormap = dict([(x, (x*255 // (self.max - 1), ) * 3) for x in range(self.max)])
        self.button_action_map = {BaseClass.buttons['left']: self.max - 1,
                                  BaseClass.buttons['right']: 0}


    def __getitem__(self, key):
        default_outcome = key - self._def_decr if key > self._def_decr else 0
        return StateRuleList(
            [CountingRule(STATE, SquareNeighbourhoodShellIndexingRule([1]),
                dict([(k, min(self.max - 1, k + self.mid_add)) for k in self.mid_nr_range])) for STATE in range(key, min(self.max, key + self.mid_state_reach))] + \
            [CountingRule(STATE, SquareNeighbourhoodShellIndexingRule([1]),
                dict([(k, min(self.max - 1, k + self.high_add)) for k in self.high_nr_range])) for STATE in range(min(self.max, key + self.mid_state_reach),
                                                                                                       min(self.max, key + self.mid_state_reach + self.high_state_reach))] + \
            [CountingRule(STATE, SquareNeighbourhoodShellIndexingRule([1]),
                          dict([(k, min(self.max - 1, max(0, k + self.low_add))) for k in self.low_nr_range])) for STATE in range(max(0, key - self.low_state_reach), key)],
            default_outcome)

class ThreeStateZigZag(Num):
    max = 3

    low_state_reach  = 2
    mid_state_reach  = 2
    high_state_reach = 1

    low_nr_range = range(1, 9)
    mid_nr_range = range(8, 9)
    high_nr_range = range(3, 4)

    low_add  = -2
    mid_add  = 0
    high_add = 1

class Three(Num):
    max = 3

    low_state_reach  = 2
    mid_state_reach  = 1
    high_state_reach = 2

    low_nr_range = range(1, 8)
    mid_nr_range = range(3, 5)
    high_nr_range = range(4, 5)

    low_add  = -2
    mid_add  = 0
    high_add = 2


class Four(Num):
    max = 4

    low_state_reach  = 3
    mid_state_reach  = 1
    high_state_reach = 2

    low_nr_range = range(2, 8)
    mid_nr_range = range(2, 4)
    high_nr_range = range(3, 8)

    low_add  = -1
    mid_add  = 0
    high_add = 1

class Bug(Num):
    max = 4
    low_state_reach = 2 # Change to two
    low_nr_range = range(2, 9)


class Five(Num):
    max = 5
class Ten(Num):
    max = 10
class Twenty(Num):
    max = 20
