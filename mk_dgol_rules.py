import sys
if sys.version[0] == '3':
    import pickle
else:
    import cPickle as pickle
import json

from egolpy_classes import DEAD, ALIVE, WHITE, BLACK, GREEN

ZOMBIE = 2

rules = {DEAD:    ([
                      (1, 2, ALIVE,   {3: ALIVE}), # Rule 4
                      (1, 2, ZOMBIE, {3: ZOMBIE}),
                   ],DEAD),
         ALIVE:   ([
                      (1,2,ZOMBIE, dict([(x, ZOMBIE) for x in range(2,9)])), # New rule
                      (1,2,ALIVE, {2: ALIVE,       # Rule 2
                                   3: ALIVE}),     # Rule 2

                    ],DEAD),   # catches rule 1 and 3
         ZOMBIE: ([
                      (1,2,ZOMBIE, {2: ZOMBIE,
                                    3: ZOMBIE}),
                      (1,2,ALIVE, {1: ZOMBIE,
                                   2: ZOMBIE,
                                   3: ZOMBIE,
                                   4: DEAD,
                                   5: DEAD,
                                   6: DEAD,
                                   7: DEAD,
                                   8: DEAD}),
                      (1,3,ZOMBIE, dict([(x, DEAD) for x in range(6,22)]))

         ], DEAD),
         }

colormap = {ALIVE: WHITE,
            DEAD: BLACK,
            ZOMBIE: GREEN,}


button_action_map = {(1,0,0): ('state_setter',
                                   (ALIVE,)
                                   ),
                     (0,0,1): ('state_setter',
                               (ZOMBIE,)
                               ),
                     }

pickle.dump((rules, colormap, button_action_map),
            open('dgol.rules','wb'))
