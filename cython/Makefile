all: lcg.so datatypes2.so lcg_ansi_c lcg_ansi_c_np
.PHONY: all

lcg.so: lcg.pyx lcgstep.pxd datatypes2.so
	python setup.py build_ext --inplace

datatypes2.so: datatypes2.pyx datatypes2.pxd
	python setup.py build_ext --inplace

lcg_ansi_c: lcg_ansi_c.c
	gcc -O2 lcg_ansi_c.c -o lcg_ansi_c

lcg_ansi_c_np: lcg_ansi_c_np.c
	gcc -O2 lcg_ansi_c_np.c -o lcg_ansi_c_np
