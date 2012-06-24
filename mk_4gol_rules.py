import cPickle as pickle
import json

from egolpy_classes import DEAD, ALIVE, WHITE, BLACK, GREEN, RED

ZOMBIE = 2
MONSTER = 3

rules = {DEAD:    ([
                      (1, 2, ALIVE,   {3: ALIVE}), # Rule 4
                      (1, 2, ZOMBIE,  {3: ZOMBIE}),
                      (1, 2, MONSTER, {3: MONSTER}),
                      (1, 3, ALIVE, dict([(x, ZOMBIE) for x \
                                         in range(18,25)])), # New rule
                   ], DEAD),
         ALIVE:   ([
                      # (1,2,MONSTER, dict([(x, ZOMBIE) for x \
                      #                     in range(1,9)])),
                      # (1,3,MONSTER, dict([(x, ZOMBIE) for x \
                      #                     in range(2,20)] +\
                      #                     [(x, MONSTER) for x \
                      #                     in range(20,25)])),
                      (1,2,ZOMBIE, dict([(x, ZOMBIE) for x \
                                         in range(2,9)])), # New rule
                      (1,2,ALIVE, {2: ALIVE,       # Rule 2
                                   3: ALIVE}),       # Rule 2
                    ],DEAD),   # catches rule 1 and 3
         ZOMBIE: ([
                      (1,2,MONSTER, dict([(x, MONSTER) for x in\
                                        range(1,9)])),#+\
                                        #  [(x, DEAD) for x in\
                                        # range(4,9)])),
                      (1,3,MONSTER, dict([(x, MONSTER) for x in\
                                        range(2,25)])),
                      (1,2,ZOMBIE, {#0: ALIVE,
                                    2: ZOMBIE,
                                    3: ZOMBIE}),
                      (1,3,ZOMBIE, dict([(x, ZOMBIE) for x \
                                          in range(13,19)] +\
                                          [(x, MONSTER) for x \
                                          in range(19,25)])),
                      (1,2,ALIVE, dict([(x, ZOMBIE) for x in\
                                        range(2,3)])),#+\
                                       # [(x, ALIVE) for x in\
                                       #  range(3,4)])),
                   ], DEAD),
         MONSTER: ([
                      (1, 2, MONSTER, dict([(x, MONSTER) for x \
                                          in range(3,5)])),
                      (1, 2, ALIVE, dict([(x, ALIVE) for x \
                                          in range(3,5)] +\
                                         [(x, DEAD) for x \
                                          in range(5,9)])),
                      (1, 2, ZOMBIE, dict([(x, ZOMBIE) for x \
                                          in range(4,5)] +\
                                          [(x, MONSTER) for x \
                                          in range(5,6)])),
                   ], ALIVE), #DEAD
         }

colormap = {ALIVE: WHITE,
            DEAD: BLACK,
            ZOMBIE: GREEN,
            MONSTER: RED,}


button_action_map = {(1,0,0): ('state_setter',
                                   (ALIVE,)
                                   ),
                     (0,0,1): ('state_setter',
                               (ZOMBIE,)
                               ),
                     }

pickle.dump((rules, colormap, button_action_map),
            open('4gol.rules','wb'))
