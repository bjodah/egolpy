from motif import *

def test_Motif():
    m = Motif(0, dense_data = range(5))
    del m[3]
    print(m)
    del m[1]
    del m[4]
    print(m)
    print('sparse', m._sparse)
    print('state count: ', m._state_counter)
    print('optimizing...  ')
    m.optimize()
    print('sparse', m._sparse)
    print('recounting states... ')
    m.recount_states()
    print('state count: ', m._state_counter)
    print('optimizing...  ')
    m.optimize()
    print('sparse', m._sparse)
    print('state count: ', m._state_counter)
    del m[0]
    m[2] = 2
    m[4] = 99
    m.optimize()
    m[3] = 99
    del m[2]
    print(m)
    print(m._state_counter)


def test_SquareGridMotif(nx = 5, ny = 6):
    sgm = SquareGridMotif(periodic = True,
                          dim = (nx, ny))
    print(sgm)
    print('-'*(2 * nx - 1))
    sgm.redefine_xy(1, 1, 1)
    sgm.redefine_xy(2, 2, 1)
    sgm.redefine_xy(3, 3, 1)
    sgm.redefine_xy(3, 4, 1)
    sgm.redefine_xy(2, 4, 1)
    sgm.redefine_xy(1, 4, 1)
    print(sgm)
    print('-'*(2 * nx - 1))
    sgm.crop()
    print(sgm)
    print('-'*(2 * nx - 1))
    sgm.crop()
    print(sgm)
    print('-'*(2 * nx - 1))


def get_gol_rule_dict():
    DEAD, ALIVE = range(2)
    gol_rule_dict =  GameRuleDict({
        DEAD: StateRuleList(
            [
                CountingRule(ALIVE,
                             SquareNeighbourhoodShellIndexingRule([1]),
                             {3: ALIVE})
                ],
            DEAD),
        ALIVE: StateRuleList(
            [
                CountingRule(ALIVE,
                             SquareNeighbourhoodShellIndexingRule([1]),
                             {2: ALIVE, 3: ALIVE}),
                ],
            DEAD)
        })
    return gol_rule_dict

def get_gol_colormap():
    DEAD, ALIVE = range(2)
    BLACK, WHITE = (0, 0, 0), (255, 255, 255)
    return {DEAD: BLACK, ALIVE: WHITE}

def get_gol_button_action_map():
    DEAD, ALIVE = range(2)
    return {(1, 0, 0): ALIVE, (0, 0, 1): DEAD}

def test_full_scale(nx = 4, ny = 4, sparse_data = {5: 1, 6: 1, 9: 1, 10: 1}):
    gol_rule_dict = get_gol_rule_dict()
    gol_motif = GameMotif(sparse_data     = sparse_data.items(),
                          game_rule_dict  = gol_rule_dict,
                          state_colormap = {DEAD:  BLACK,
                                             ALIVE: WHITE},
                          button_action_map = get_gol_button_action_map(),
                          periodic        = True,
                          dim             = (nx, ny),
                          )
    print(gol_motif)
    print('-' * (2 * gol_motif._nx - 1))
    for k in sparse_data.keys():
        assert k in gol_motif._changed_since_propagate
    pani = gol_motif.get_possibly_affected_neigh_idxs(5)
    print(pani)
    for i in [0, 1, 2, 4, 6, 8, 9, 10]:
        assert i in pani
    gol_motif.propagate()
    # print(gol_motif)
    # print('-' * (2 * gol_motif._nx - 1))
    gol_motif.propagate()
    # print(gol_motif)
    # print('-' * (2 * gol_motif._nx - 1))
    for idx, state in enumerate([0, 0, 0, 0,
                                 0, 1, 1, 0,
                                 0, 1, 1, 0,
                                 0, 0, 0, 0,]):
        assert gol_motif[idx] == state


def test_glider(nx = 6, ny = 6):
    dense_data = map(int, """0 0 0 0 0 0
                             0 0 1 0 0 0
                             0 0 0 1 0 0
                             0 1 1 1 0 0
                             0 0 0 0 0 0
                             0 0 0 0 0 0""".split())
    BLACK, WHITE = (0, 0, 0), (255, 255, 255)
    DEAD, ALIVE = range(2)
    gol_rule_dict =  GameRuleDict({
        DEAD: StateRuleList(
            [
                CountingRule(ALIVE,
                             SquareNeighbourhoodShellIndexingRule([1]),
                             {3: ALIVE})
                ],
            DEAD),
        ALIVE: StateRuleList(
            [
                CountingRule(ALIVE,
                             SquareNeighbourhoodShellIndexingRule([1]),
                             {2: ALIVE, 3: ALIVE}),
                ],
            DEAD)
        })

    gol_motif = GameMotif(dense_data      = dense_data,
                          game_rule_dict  = gol_rule_dict,
                          state_colormap = {DEAD:  BLACK,
                                             ALIVE: WHITE},
                          periodic        = True,
                          dim             = (nx, ny),
                          )
    # print(gol_motif)
    # print('-' * (2 * gol_motif._nx - 1))

    for i in range(24):
        gol_motif.propagate()
        # print(gol_motif)
        # print('-' * (2 * gol_motif._nx - 1))

    for idx, state in enumerate(dense_data):
        assert gol_motif[idx] == state
