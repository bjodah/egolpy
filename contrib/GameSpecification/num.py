#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Written by Björn Dahlgren
"""

from contrib.GameSpecification import BaseClass

from rules import StateRuleList, CountingRule, SquareNeighbourhoodShellIndexingRule, GameRuleDict

class Num(BaseClass.GameSpecification):

    max = 0
    m = 0
    p = 0
    upward = 2
    _def_decr = 1
    _mid_range = range(2, 4)
    _low_range = range(2, 4)
    _high_range = range(2, 4)

    def __init__(self):
        self.mid_p = self.max // 2
        self.low_p = self.max // 1.5
        self.high_p = self.max // 3
        self.post_init()

    def post_init(self):
        part = (255 - 50) / self.max
        self.rule_dict = GameRuleDict(dict([(x, self[x]) for x in range(self.max)]))
        self.colormap = dict([(x, (50 + (x + 1 )* part, ) * 3) for x in range(self.max)])
        self.button_action_map = {BaseClass.buttons['left']: self.max - 1,
                                  BaseClass.buttons['right']: 0}


    def __getitem__(self, key):
        default_outcome = key - self._def_decr if key > self._def_decr else 0
        return StateRuleList(
            [CountingRule(STATE, SquareNeighbourhoodShellIndexingRule([1]),
                dict([(k, min(self.max, k + self.mid_p)) for k in self._mid_range])) for STATE in range(key, min(self.max, key + self.upward))] + \
            [CountingRule(STATE, SquareNeighbourhoodShellIndexingRule([1]),
                dict([(k, min(self.max, k + self.low_p)) for k in self._low_range])) for STATE in range(max(0, key - self.m), key)] + \
            [CountingRule(STATE, SquareNeighbourhoodShellIndexingRule([1]),
                dict([(k, min(self.max, k + self.high_p)) for k in self._high_range])) for STATE in range(min(self.max, key + self.upward),
                                                                                                       min(self.max, key + self.upward + self.p))],
            default_outcome)


Three = Num; Three.max = 3
Five = Num; Five.max = 5
Ten  = Num; Ten.max = 10
Twenty  = Num; Twenty.max = 20

