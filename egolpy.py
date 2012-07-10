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

#from egolpy_classes import GamePlan
from motif import GameMotif
from rules import GameRuleDict
from motif_screen import PygameMotifScreen
from numpymotif import NumpyGameMotif

import contrib.GameSpecification as GameSpecification

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

Motif_routine = {'numpy': NumpyGameMotif,
                 'python': GameMotif}

DEAD, ALIVE = range(2)
BLACK, WHITE = (0, 0, 0), (255, 255, 255)

def pyglet_loop(game_motif, nxcells, nycells,
                width, height, periodic,
                update_interval, load_file,
                save_file, rule_file):
    pass



def pygame_loop(game_motif, nxcells, nycells,
                width, height, periodic,
                update_interval, load_file,
                save_file, rule_file):
    """
    Pygame event loop
    """

    pygame.init()

    screen_res = width, height
    motif_screen = PygameMotifScreen(screen_res, game_motif,
                               (nxcells, nycells))

    clock = pygame.time.Clock()
    tick = clock.tick()
    paused = False
    nr_skip_draw = 0
    t_wait = int(update_interval / 6) + 1
    p_wait = 100
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                buttons=[0,0,0]
                buttons[event.button-1] = 1
                motif_screen.click(tuple(buttons), *event.pos)
            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0] == 1:
                    motif_screen.click(event.buttons, *event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p or \
                       event.key == pygame.K_SPACE:
                    # Puase / unpause game
                    paused = not paused
                    logger.info('Pused' if paused else 'Unpaused')
                elif event.key == pygame.K_s:
                    # Save state of game
                    motif_screen.save(save_file)
                elif event.key == pygame.K_l:
                    # Save state of game
                    motif_screen.load(load_file)
                elif event.key == pygame.K_j:
                    # Jump X steps forward
                    nr_skip_draw = int(raw_input('Skip nr steps: '))
                # elif event.key == pygame.K_d:
                #     # Dump memory for debug/optimization
                # scanner.dump_all_objects('meliae.dump')
                elif event.key == pygame.K_q or \
                     event.key == pygame.K_ESCAPE:
                    sys.exit(0)


        if paused:
            motif_screen.execute_clicks()
            motif_screen.draw()
            pygame.time.wait(p_wait)
        else:
            if nr_skip_draw == 0:
                motif_screen.draw()
                pygame.time.delay(t_wait)
                tick += clock.tick()
                if tick > update_interval:
                    motif_screen.propagate()
                    tick = 0
            else:
                motif_screen.propagate()
                nr_skip_draw -= 1
                if nr_skip_draw == 0:
                    motif_screen.full_redraw()

    pygame.quit()
    return 0

def main(nxcells, nycells, width, height,
         periodic, sparse, update_interval,
         load_file, save_file, rule_file,
         motif_routine,
         spec_name,
         backend='pygame'):
    """
    Main routine, initializes gamemotif and launches
    eventloops
    """
    game_spec = GameSpecification.subclasses[spec_name]()
    game_motif = Motif_routine[motif_routine](#sparse_data = {},
        game_rule_dict = game_spec.rule_dict,
        dim = (nxcells, nycells),
        periodic = periodic,
        state_colormap = game_spec.colormap,
        button_action_map = game_spec.button_action_map
    )

    if sparse:
        game_motif.make_sparse()
    else:
        game_motif.make_dense()


    if backend == 'pygame':
        return pygame_loop(game_motif, nxcells, nycells, width, height,
                    periodic, update_interval, load_file,
                    save_file, rule_file)
    elif backend == 'pyglet':
        return pylget_loop(nxcells, nycells, width, height,
                    periodic, update_interval, load_file,
                    save_file, rule_file)

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
    parser.add_argument('-a', '--sparse', action="store_true",
                        default=False, help="Use sparse data representation (incomp numpy, dense is default)")
    parser.add_argument('-s', '--save_file', type=str, default='',
                        help="State file to save")
    parser.add_argument('-l', '--load_file', type=str, default='',
                        help="State file to load")
    parser.add_argument('-r', '--rule_file', type=str, default='',
                        help="Rule file to load")
    parser.add_argument('-u', '--update_interval', type=int, default=150,
                        help="Update interval in milliseconds")
    parser.add_argument('-m', '--motif_routine', type=str,
                        default='python',
                        help="Motif routine to use [{}] (default: python)".format(', '.join(Motif_routine.keys())))
    parser.add_argument('-n', '--spec_name', type=str,
                        default='cgol_GameOfLife',
                        help="GameSpecification class [{}] (default: cgol_GameOfLife)".format(', '.join(GameSpecification.subclasses.keys())))

    args = parser.parse_args()
    argd = vars(args) # Argument dictionary
    sys.exit(main(**argd))

