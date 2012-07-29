#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Written by Björn Dahlgren
"""

from __future__ import division

from contrib.GameSpecification import BaseClass

from rules import StateRuleList, CountingRule, SquareNeighbourhoodShellIndexingRule, GameRuleDict

class Proxy(BaseClass.GameSpecification):
    alive_rules = True
    extra_dead_rule = True
    def __init__(self):
        self.DEAD, self.ALIVE = range(2)
        dl = [ CountingRule(self.ALIVE,
                            SquareNeighbourhoodShellIndexingRule([2]),
                            {1: self.DEAD}),
               ] if self.extra_dead_rule else []

        dl.extend( [
                CountingRule(self.ALIVE,
                             SquareNeighbourhoodShellIndexingRule([2]),
                             {2: self.ALIVE}),
                ])
        dead_rules = StateRuleList(
            dl,
            self.DEAD)
        al = [
                CountingRule(self.ALIVE,
                             SquareNeighbourhoodShellIndexingRule([1]),
                             {2: self.DEAD,
                              3: self.DEAD}),
                ] if self.alive_rules else []
        alive_rules = StateRuleList(
            al,
            self.ALIVE)
        self.rule_dict = GameRuleDict({self.DEAD: dead_rules,
                                       self.ALIVE: alive_rules})
        self.colormap = {self.DEAD: BaseClass.colors['black'],
                         self.ALIVE: BaseClass.colors['white']}
        self.button_action_map = {BaseClass.buttons['left']: self.ALIVE,
                                  BaseClass.buttons['right']: self.DEAD}


class Pulse(BaseClass.GameSpecification):

    nr_states = 10

    def __init__(self):
        self.rule_dict = GameRuleDict({x: self.rule(x) for x in range(self.nr_states)})
        self.colormap = {s: (255 // self.nr_states * s,) * 3 for s in range(self.nr_states)}
        print(self.colormap)
        self.button_action_map = {BaseClass.buttons['left']: self.nr_states - 1,
                                  BaseClass.buttons['right']: 0}
    def rule(self, i):
        return StateRuleList(self.counting_rules(i),
                             self.default_outcome(i))

    def counting_rules(self, i):
        return [CountingRule(self.counted(i, x),
                             self.indexing(i, x),
                             self.outcomes(i, x)) for x in \
                range(self.nr_counting_rules(i))]#[::-1]]

    def counted(self, i, x):
        if i == 0 and x == 0: return self.nr_states - 1
        if x == 0: return i
        if i < self.nr_states // 2:
            return max(i + self.nr_states // 2 + x, self.nr_states - 1)
        else:
            return max(i - self.nr_states // 2 - x, 0)

    def indexing(self, i, x):
        return SquareNeighbourhoodShellIndexingRule([1])

    def outcomes(self, i, x):
        if i == 0 and x == 0: return {3: self.nr_states - 1}
        if i < x:
            return {2: i,
                    3: i,
                    4: max(i + x ** 2, self.nr_states - 1)}
        else:
            return {2: i,
                    3: i,
                    4: max(i - x ** 2, 0)}

    def nr_counting_rules(self, i):
        return 1 + int(abs(i - self.nr_states // 2) ** 0.5)

    def default_outcome(self, i):
        return max(0, i - 1)

class Pulse20(Pulse):
    nr_states = 20


class Pulse4(Pulse):
    nr_states = 4

class LivePulse(Pulse):
    def counting_rules(self, i):
        return [CountingRule(self.counted(i, x),
                             self.indexing(i, x),
                             self.outcomes(i, x)) for x in \
                range(self.nr_counting_rules(i))]#[::-1]]

    def outcomes(self, i, x):
        if i == 0 and x == 0: return {2: self.nr_states - 2, 3: self.nr_states - 1}
        if i < self.counted(i, x):
            return {2: i,
                    3: max((i + 1) % (self.nr_states - 1), self.nr_states - 1),
                    4: max((i + x ** 2) % (self.nr_states - 1), self.nr_states - 1)}
        else:
            return {2: max(i - 2, 0),
                    3: max(i - 1, 0),
                    4: min(i + 1, self.nr_states - 1),
                    }

    def nr_counting_rules(self, i):
        return self.nr_states


    def counted(self, i, x):
        if i == 0 and x == 0: return self.nr_states - 1
        return x


class LivePulse12(LivePulse):
    nr_states = 12


class LivePulse8(LivePulse):
    nr_states = 8
