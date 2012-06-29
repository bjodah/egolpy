import cython
cimport cython

from libc.stdlib cimport malloc,  free


#from libcpp.vector cimport vector

# References
# http://wiki.cython.org/ListExample
# http://wiki.cython.org/DynamicMemoryAllocation

cdef class FixedLengthUIntList(list):

    cdef uint N
    cdef uint *data

    def __init__(self, *args):
        cdef uint self._default

        if len(args) == 1:
            # Iterable provided, mimic list behaviour
            self._default = cython.uint(0)
            iterable = args[0]
            N = len(args[0])
            *data = <int*>malloc(N * sizeof(int))
            for idx, val in enumerate(iterable):
                data[idx] = cython.uint(val)

        elif len(args) == 2:
            # length, stdval provided
            length, stdval = args
            N = cython.uint(length)
            self._default = cython.uint(stdval)
            *data = <int*>malloc(N * sizeof(int))
            for idx in range(N):
                data[idx] = self._default

    def __getitem__(self, index):
        return data[index]

    def __setitem__(self, index,  value):
        data[index] = cython.uint(value)

    def __delitem__(self, index):
        data[index] = cython.uint(value)

    def __del__(self):
        free(data)
