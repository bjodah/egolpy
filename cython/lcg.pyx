cimport lcgstep
from datatypes2 cimport FixedLengthIntList

def vb_lcg_gen(int x0):
    while True:
        x0 = (1140671485*x0 + 12820163) % 16777216
        yield x0

def lcg_gen(int x0):
    while True:
        x0 = lcgstep.vb_lcg_step(x0)
        yield x0


def firstn(g, long n):
    cdef long i
    for i in range(n):
        yield g.next()


cdef class LCG:

    cdef int x

    def __cinit__(self, int x):
        self.x = x

    cpdef int next(self):
        cdef int x = self.x
        x = lcgstep.vb_lcg_step(self.x)
        self.x = x
        return self.x

#cimport datatypes2

#cdef extern class datatypes2.FixedLengthIntList


cdef class FLIL_LCG(FixedLengthIntList):
     def apply_vb_lcg(self, int seed):
         cdef long i
         cdef long n = self.n
         cdef int* data = self.data
         data[0] = seed
         for i in range(1, n):
             data[i] = lcgstep.vb_lcg_step(data[i - 1])

cdef class FLIL_LCG2(FixedLengthIntList):
     def apply_vb_lcg(self, int seed):
         cdef long i
         cdef long n = self.n
         cdef int* data = self.data
         data[0] = seed
         for i in range(1, n):
             data[i] = (1140671485*data[i - 1] + 12820163) % 16777216

