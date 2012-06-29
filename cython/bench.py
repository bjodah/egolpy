#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division,  print_function
import sys
if sys.version[0] == '2':
    range = xrange
    # Do list(range()) if you want 2.x behaviour

from itertools import product
import subprocess
from time import time

from python_lcg import lcg_gen as python_lcg_gen
from python_lcg import firstn as python_firstn
from lcg import lcg_gen as cython_lcg_gen
from lcg import LCG as cython_LCG_class
from lcg import firstn as cython_firstn
from lcg import FLIL_LCG, FLIL_LCG2

firstn_impls =  [('python', python_firstn),
                 ('cython', cython_firstn),
                 ]

lcg_impls = [('python', python_lcg_gen),
             ('cython_lcg_gen', cython_lcg_gen),
             ('cython_lcg_class', cython_LCG_class),
             ]

N = 10000000
seed = 101

for lcg_impl, firstn_impl in product(lcg_impls, firstn_impls):
    lcg_name, lcg_cb = lcg_impl
    firstn_name, firstn_cb =  firstn_impl
    print("LCG impl: {}, firstn impl: {}".format(lcg_name,
                                                 firstn_name))
    t = time()
    lcg_gen = lcg_cb(seed)
    firstn_g = firstn_cb(lcg_gen,N)
    l = list(firstn_g)
    t =  time() - t
    print(l[-10:], t)


N *= 10
print("cython: Subclassed FixedLengthIntList: FLIL_LCG ({})".format(N))
t = time()
flil_lcg = FLIL_LCG(N)
flil_lcg.apply_vb_lcg(seed)
t = time() - t
print([flil_lcg[x] for x in range(N - 10, N)], t)

del flil_lcg
print("cython: Subclassed FixedLengthIntList: FLIL_LCG2 ({})".format(N))
t = time()
flil_lcg2 = FLIL_LCG2(N)
flil_lcg2.apply_vb_lcg(seed)
t = time() - t
print([flil_lcg2[x] for x in range(N - 10, N)], t)

del flil_lcg2
print("ansi c external call ({})".format(N))
t = time()
print(subprocess.call(["./lcg_ansi_c", str(N), str(seed)]))
t = time() - t
print(t)

print("Now let us see what happens if we dont store the value")
print("ansi c external call ({})".format(N))
t = time()
print(subprocess.call(["./lcg_ansi_c_np", str(N), str(seed)]))
t = time() - t
print(t)

