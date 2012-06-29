# Future imporvements

Implemnt pseudo random number bit mask routines for Linear congruential generator.
Leaves 8 bits (256) states unaffected. May enable "Monte Carlo Cellular Automata"

# imp, m, a, c = "Microsoft Visual Basic (6 and earlier)[6]", 2**24, 1140671485, 12820163

def lcg(x0, m=2**24, a=1140671485, c=12820163):
    """
    Linear congruential generator with parameters for
    Microsoft Visual Basic (6 and earlier)[6]
    """
    while True:
        x0 = (a*x0 + c) % m
        yield x0
