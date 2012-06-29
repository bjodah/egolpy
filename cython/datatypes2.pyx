import cython
cimport cython

from libc.stdlib cimport malloc,  free


#from libcpp.vector cimport vector

# References
# http://wiki.cython.org/ListExample
# http://wiki.cython.org/DynamicMemoryAllocation

cimport cython

cdef class FixedLengthIntList:

    # cdef long n
    # cdef int *data

    def __cinit__(self, long n):
        cdef int *data = <int*>malloc(n * sizeof(int))
        cdef long i
        self.n = n
        for i in range(n):
            data[i] = 0
        self.data = data

    #@cython.boundscheck(False)
    def __getitem__(self, long index):
        cdef int *data = self.data
        cdef long n = self.n
        if index < n:
            return data[index]
        else:
            raise IndexError

    def __setitem__(self, long index, int value):
        cdef int *data = self.data
        cdef long n = self.n
        if index < n:
            data[index] = value
        else:
            raise IndexError

    def __delitem__(self, long index):
        cdef int *data = self.data
        cdef long n = self.n
        if index < n:
            data[index] = 0
        else:
            raise IndexError

    def __dealloc__(self):
        cdef int *data = self.data
        free(data)

cdef class FLIL_cumsum(FixedLengthIntList):

    @cython.boundscheck(False)
    cpdef cumsum(self):
        cdef int *data = self.data
        cdef long n = self.n
        cdef long i

        for i in range(1, n):
            data[i] = data[i - 1] + data[i]
