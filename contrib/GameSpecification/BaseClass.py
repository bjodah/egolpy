#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import division, print_function

buttons = {'left': (1, 0, 0),
           'middle': (0, 1, 0),
           'right': (0, 0, 1)}

colors = {'black': (0, 0, 0),
          'white': (255, 255, 255),
          'red': (255, 0, 0),
          'green': (0, 255, 0),
          'blue': (0, 0, 255),
          'darkblue': (0, 0, 127),
          'ddarkblue': (0, 0, 96),
          'yellow': (255, 255, 0),
          'grey': (127, 127, 127),
          'purple': (255, 0, 255),
          'orange': (255, 127, 0),
          'turqoise': (0, 255, 255),
          }

class GameSpecification(object):
    _subclasses = {}
    def __init__(self):
        """
        Here you write code to generate:
        * self.rule_dict = GameRuleDict(...)
        * self.colormap =  {0: (0, 0, 0), 1: (255, 255, 255),...  }
        * self.button_action_map = {(1, 0, 0): 1, (0, 0, 1): 0}
        """

        pass

