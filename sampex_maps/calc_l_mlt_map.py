# Calculate L-MLT map of SAMPEX-HILT (>1 MeV electron) precipitation.

from datetime import datetime, timedelta

import numpy as np
import sampex

from sampex_maps.utils import progressbar

class L_MLT_Map:
    def __init__(self, L_bins, MLT_bins, times=None) -> None:
        self.H = np.zeros((L_bins.shape[0]-1, MLT_bins.shape[0]-1))

        if times is not None:
            # TODO use the times kwarg to filter the times over which
            # the loop loops over.
            raise NotImplementedError
        else:
            self.dates = None
        return

    def loop():
        pass


if __name__ == '__main__':
    L_bins = np.arange(2, 11)
    MLT_bins = np.arange(0, 24.1)

    m = L_MLT_Map(L_bins, MLT_bins)