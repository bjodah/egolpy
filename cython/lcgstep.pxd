import cython

@cython.cdivision(True)
cdef inline int vb_lcg_step(int x):
    return (1140671485*x + 12820163) % 16777216
