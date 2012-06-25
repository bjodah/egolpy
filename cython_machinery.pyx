#cython
# -*- coding: utf-8 -*-

cdef class StateMap:

     cdef int _nx, _ny, _default_state, \
          largest_neighbour_distance

     def __init__(self, nx, ny, data=None, default_state=0, pbc=False,
                 nth_neighbour_coordinates=None,
                 largest_neighbour_distance=1):

