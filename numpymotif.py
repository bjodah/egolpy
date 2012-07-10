from motif import GameMotif
import numpy as np

class NumpyGameMotif(GameMotif):

    def __init__(self, **kwargs):

        # Use of numpy array enforces dense data mode
        ddt = 'dense_data_type'
        mca =  'mode_change_allowed'
        if ddt in kwargs:
            assert kwargs[ddt] == np.array
        else:
            kwargs[ddt] = np.array

        mca =  'mode_change_allowed'
        if mca in kwargs:
            assert kwargs[mca] == False
        else:
            kwargs[mca] = False
        super(NumpyGameMotif, self).__init__(**kwargs)
        assert not self._sparse

    def count_state_at_indices(self, counted_state, idxs):
        """ Utilize numpy array """
        bc = np.bincount(self._dense_data[idxs])
        if counted_state >= len(bc):
            return 0
        else:
            return bc[counted_state]
