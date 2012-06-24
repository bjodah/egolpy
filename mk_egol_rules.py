import cPickle as pickle
import json

from egolpy_classes import DEAD, ALIVE, WHITE, BLACK

rules = {DEAD:  ([
                   (1,2,ALIVE, {3: ALIVE}),     # Rule 4.
                 ], DEAD),     # Note: range(1,2) == [1]
         ALIVE: ([
                   (1,2,ALIVE, {2: ALIVE, # Rule 2
                                3: ALIVE}), # Rule 2
                 ], DEAD),   # catches rule 1 and 3
             }

colormap = {ALIVE: WHITE,
            DEAD: BLACK}


button_action_map = {(1,0,0): ('state_setter',
                                   (ALIVE,)
                                   ),
                     (0,0,1): ('state_setter',
                                   (DEAD,)
                                   ),}

pickle.dump((rules, colormap, button_action_map),
            open('egol.rules','wb'))
