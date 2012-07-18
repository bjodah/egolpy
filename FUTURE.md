# Future improvements

* Auto-detect stable conformations for rule and store them (pickle_cache with code version control?)
* Write algorithm for spawning stable motifs pseudo randomly (seed) placed on a board
* PyCUDA
* Implement random propagation rules
* Implement genetic routine (complex numbers or the like?) - let the best genes win! (state data better map to binary instructions)
* Other neighbour counting rules
* Triangular and Hexagonal motifs
* Cython + array.array (Full numpy.ndmatrix utilization - Rethink: cython not mature enough, poor support for ndenumerate etc)
* Add pre-commit git hooks for tests and performance regressions
* Write test based optimization routine
* Auto build and cache binaries from contrib/GameSpecification (cython)
* Write SimpleMotif with emphasis on minimum amount of code (refactor Motif as neccessary)
* Implemnt pseudo random number bit mask routines for Linear congruential generator. (for use with random propagation rules) (Leaves 8 bits (256) states unaffected. May enable "Monte Carlo Cellular Automata")

# imp, m, a, c = "Microsoft Visual Basic (6 and earlier)[6]", 2**24, 1140671485, 12820163

def lcg(x0, m=2**24, a=1140671485, c=12820163):
    """
    Linear congruential generator with parameters for
    Microsoft Visual Basic (6 and earlier)[6]
    """
    while True:
        x0 = (a*x0 + c) % m
        yield x0
