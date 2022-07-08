from datetime import datetime, timedelta
import pathlib
import re

import pandas as pd
import numpy as np
import sampex

from sampex_maps.utils import progressbar

class L_MLT_Map:
    def __init__(self, L_bins, MLT_bins, instrument='HILT', times=None, stat=50) -> None:
        """
        Calculate L-MLT map of SAMPEX precipitation. Once you run L_MLT_Map.loop(), the 
        "H" attribute contains the histogram.

        Parameters
        ----------
        L_bins: np.array
            The L bins used to histogram the data.
        MLT_bins: np.array
            The MLT bins used to histogram the data.
        instrument: str
            The SAMPEX instrument. Can be 'HILT', 'PET', or 'LICA'.
        times: np.array
            An shape = (n, 2) array of start and end times. Not implemented yet.
        stat: float
            What percentile to calculate. Default is the median.
        """
        self.H = np.zeros((L_bins.shape[0]-1, MLT_bins.shape[0]-1))
        self.instrument = instrument.upper()
        assert instrument.upper() in ['HILT', 'PET', 'LICA']

        if times is not None:
            # TODO use the times kwarg to filter the times over which
            # the loop loops over.
            raise NotImplementedError
        else:
            self.dates = self._get_dates()
        return

    def loop(self):
        """
        Loop over the SAMPEX files and bin each day's data by L and MLT.
        """
        for date in progressbar(self.dates):
            self.hilt = sampex.HILT(date)
            self.attitude = sampex.Attitude(date)

    def _yeardoy2date(self, yeardoy):
        """
        Converts a date in the year day-of-year format (YEARDOY)
        into a datetime.datetime object.
        """
        return datetime.strptime(yeardoy, "%Y%j")

    def _get_dates(self):
        """
        Finds the SAMPEX files and converts the filenames into dates.
        """
        if self.instrument.upper() == 'HILT':
            # Find the files and convert the YYYYDOY component of the filename 
            # to a datetime.
            file_name_glob = f"hhrr*"
            self.hilt_paths = sorted(
                pathlib.Path(sampex.config['sampex_data_dir']).rglob(file_name_glob))
            assert len(self.hilt_paths), (
                f'{len(self.hilt_paths)} HILT files found in '
                f'{sampex.config["sampex_data_dir"]}'
                )
            date_strs = [re.findall(r"\d+", str(f.name))[0] for f in self.hilt_paths]
            dates = [self._yeardoy2date(date_str) for date_str in date_strs]
        else:
            raise NotImplementedError
        return dates

if __name__ == '__main__':
    L_bins = np.arange(2, 11)
    MLT_bins = np.arange(0, 24.1)

    m = L_MLT_Map(L_bins, MLT_bins)
    m.loop()