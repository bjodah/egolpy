#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
egol - Extendable game of life

Copyright (c) 2012, Björn Ingvar Dahlgren and Axel Ingvar Dahlgren

This project is open source and is released under the
2-cluase BSD license. See LICENSE.txt for further details.
"""

from __future__ import division

# Memory scanner for debug/optimization
#from meliae import scanner

import sys, pygame, os
from itertools import product
import logging
from egolpy_classes import GamePlan

if sys.version[0] == '3':
    imap = map
    xrange = range
    import pickle
else:
    from itertools import imap
    import cPickle as pickle

import argparse

logging.basicConfig()
logger = logging.getLogger('egol')
logger.setLevel(logging.DEBUG)

def main(nxcells=40, nycells=40, width=400, height=400,
         periodic=True, update_interval=250,
         load_file='', save_file='', rule_file='',
         largest_neighbour_distance=1):
    """
    Main game
    """
    pygame.init()

    size = width, height

    rules, colormap, button_action_map = None, None, None

    if rule_file != '':
        if os.path.exists(rule_file):
            rules, colormap, button_action_map = pickle.load(\
                open(rule_file, 'rb'))
        else:
            logger.debug('Couldn\'t open: %s. Using std GOL rules',
                         rule_file)

    game_plan = GamePlan((nxcells,nycells), size,
                   pbc=periodic, rules=rules, colormap=colormap,
                   button_action_map=button_action_map,
                   largest_neighbour_distance=largest_neighbour_distance)

    if load_file != '':
        if os.path.exists(load_file): game_plan.load(load_file)
    clock = pygame.time.Clock()
    tick = clock.tick()
    paused = False
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                buttons=[0,0,0]
                buttons[event.button-1] = 1
                game_plan.click(tuple(buttons), *event.pos)
            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0] == 1:
                    game_plan.click(event.buttons, *event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p or \
                       event.key == pygame.K_SPACE:
                    # Puase / unpause game
                    paused = not paused
                elif event.key == pygame.K_s:
                    # Save state of game
                    game_plan.save(save_file)
                elif event.key == pygame.K_l:
                    # Save state of game
                    game_plan.load(load_file)
                # elif event.key == pygame.K_d:
                #     # Dump memory for debug/optimization
                # scanner.dump_all_objects('meliae.dump')
                elif event.key == pygame.K_q or \
                     event.key == pygame.K_ESCAPE:
                    sys.exit(0)

        game_plan.draw()
        if paused:
            game_plan.execute_clicks()
        else:
            tick += clock.tick()
            if tick > update_interval:
                game_plan.propagate()
                tick = 0

        pygame.time.wait(25)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-x', '--nxcells', type=int, default=40,
                        help="Number of cells on the width")
    parser.add_argument('-y', '--nycells', type=int, default=40,
                        help="Number of cells on the height")
    parser.add_argument('-W', '--width', type=int, default=400,
                        help="Width of gameplan in pixels")
    parser.add_argument('-H', '--height', type=int, default=400,
                        help="Height of gameplan in pixels")
    parser.add_argument('-p', '--periodic', action="store_true",
                        default=False, help="Use periodic boundary conditions")
    parser.add_argument('-s', '--save_file', type=str, default='',
                        help="State file to save")
    parser.add_argument('-l', '--load_file', type=str, default='',
                        help="State file to load")
    parser.add_argument('-r', '--rule_file', type=str, default='',
                        help="Rule file to load")
    parser.add_argument('-u', '--update_interval', type=int, default=250,
                        help="Update interval in milliseconds")
    parser.add_argument('-n', '--largest_neighbour_distance',
                        type=int, default=1,
                        help="Largest neighbour distance used in rules.")

    args = parser.parse_args()
    argd = vars(args) # Argument dictionary
    main(**argd)

