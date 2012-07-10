#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Written by Björn Dahlgren
"""

from contrib.GameSpecification import BaseClass

from rules import StateRuleList, CountingRule, SquareNeighbourhoodShellIndexingRule, GameRuleDict

class GameOfLife(BaseClass.GameSpecification):
    def __init__(self):
        self.DEAD, self.ALIVE = range(2)
        dead_rules = StateRuleList(
            [
                CountingRule(self.ALIVE,
                             SquareNeighbourhoodShellIndexingRule([1]),
                             {3: self.ALIVE}),
                ],
            self.DEAD)
        alive_rules = StateRuleList(
            [
                CountingRule(self.ALIVE,
                             SquareNeighbourhoodShellIndexingRule([1]),
                             {2: self.ALIVE,
                              3: self.ALIVE}),
                ],
            self.DEAD)
        self.rule_dict = GameRuleDict({self.DEAD: dead_rules,
                                       self.ALIVE: alive_rules})
        self.colormap = {self.DEAD: BaseClass.colors['black'],
                         self.ALIVE: BaseClass.colors['white']}
        self.button_action_map = {BaseClass.buttons['left']: self.ALIVE,
                                  BaseClass.buttons['right']: self.DEAD}

