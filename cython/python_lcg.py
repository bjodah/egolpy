def firstn(g, n):
    for i in range(n):
        yield g.next()


def lcg_gen(seed, m = 16777216, a = 1140671485, c = 12820163):
    while True:
        seed = (a * seed + c) % m
        yield seed
