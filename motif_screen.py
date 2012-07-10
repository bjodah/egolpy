#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Stdlib imp.
from itertools import product

# External dep.
import pygame


# TODO:
# Implement ncurses screen
# Implement pyglet screen

class PygameMotifScreen(object):
    """
    gameplan class for use with pygame and games of
    the kind of Conway's Game of Life
    """
    def __init__(self, screen_res, motif, celldim,
                 line_color = (125, 125, 125),
                 bgcolor = (0, 0, 0)):

        self._screen_res = screen_res
        self._motif      = motif

        # Create a pygame.Surface for the screen
        self._screen     = pygame.display.set_mode(self._screen_res)
        self._w          = screen_res[0] // celldim[0]
        self._h          = screen_res[1] // celldim[1]

        # Generate coloured surfaces for bliting states
        self._state_img  = dict([(k, pygame.Surface((self._w-1,
                                     self._h - 1))) for\
                            k, v in self._motif.state_colormap.items()])
        for k, v in self._motif.state_colormap.items():
            self._state_img[k].fill(v)
        # self._rect = [pygame.Rect(self._w*x+1,
        #                           self._h*y+1,
        #                           self._w-1,
        #                           self._h-1) for y, x \
        #               in product(range(celldim[1]),
        #                      range(celldim[0]))]
        self._cellcoords = [(self._w*x+1, self._h*y+1) for y, x \
                            in product(range(celldim[1]),
                                       range(celldim[0]))]
        self._clicklist = []
        self._line_color = line_color
        self._bgcolor = bgcolor
        self.draw_init()


    def draw_init(self):
        self._screen.fill(self._bgcolor)
        for start, stop in self._motif.get_raster_line_coords(
            self._w, self._h, self._screen_res[0], self._screen_res[1]):
            pygame.draw.line(self._screen, self._line_color, start, stop)
        pygame.display.flip()


    def propagate(self):
        self.execute_clicks()
        self._motif.propagate()

    def full_redraw(self):
        self.draw_init()
        for index in range(self._motif._n):
            self._screen.blit(self._state_img[self._motif[index]],
                              (self._cellcoords[index]))
            # pygame.draw.rect(self._screen,
            #                  self._motif.get_color(index),
            #                  self._get_rect(index))

    def draw(self):
        redefined_i = self._motif._changed_since_propagate
        if redefined_i == []: return None
        for index in redefined_i:
            self._screen.blit(self._state_img[self._motif[index]],
                              (self._cellcoords[index]))
            # pygame.draw.rect(self._screen,
            #                  self._motif.get_color(index),
            #                  self._get_rect(index))
        pygame.display.flip()


    def click(self, buttons, screen_x, screen_y):
        ix, iy = screen_x // self._w, screen_y // self._h
        if not (ix, iy) in self._clicklist:
            self._clicklist.append((buttons, ix, iy))


    def execute_clicks(self):
        for clicked in self._clicklist:
            self._motif.click(*clicked)
        self._clicklist = []


    # def _get_rect(self, index):
    #     return self._rect[index]

