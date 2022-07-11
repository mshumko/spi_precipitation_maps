from datetime import datetime, timedelta
import pathlib
import re

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sampex

from sampex_maps.utils import progressbar

class L_MLT_Map:
    def __init__(self, L_bins, MLT_bins, instrument='HILT', counts_col='counts', times=None) -> None:
        """
        Calculate L-MLT map of the mean SAMPEX precipitation. Once you run L_MLT_Map.loop(), the 
        "H" attribute contains the histogram.

        Parameters
        ----------
        L_bins: np.array
            The L bins used to histogram the data.
        MLT_bins: np.array
            The MLT bins used to histogram the data.
        instrument: str
            The SAMPEX instrument. Can be 'HILT', 'PET', or 'LICA'.
        counts_col: str
            What counts column to calculate the quantile.
        times: np.array
            An shape = (n, 2) array of start and end times. Not implemented yet.
        """
        self.L_bins = L_bins
        self.MLT_bins = MLT_bins
        self.mean = np.zeros((L_bins.shape[0]-1, MLT_bins.shape[0]-1))
        self.mean_sampes = np.zeros((L_bins.shape[0]-1, MLT_bins.shape[0]-1))
        self.instrument = instrument.upper()
        self.counts_col = counts_col.lower()
        assert instrument.upper() in ['HILT', 'PET', 'LICA']

        if times is not None:
            # TODO use the times kwarg to filter the times over which
            # the loop loops over.
            raise NotImplementedError
        else:
            self.dates = self._get_dates()
            self.dates = [date for date in self.dates if date > datetime(1997, 1, 1)]
        return

    def loop(self):
        """
        Loop over the SAMPEX files and bin each day's data by L and MLT.
        """
        for date in progressbar(self.dates[:10]):
            print(f'Processing SAMPEX-{self.instrument} on {date.date()}')
            try:
                self.hilt = sampex.HILT(date)
                if self.hilt.state != 4:
                    continue  # I dont' have the state 1-3 loaders written yet.
                self.hilt.load()
            except (ValueError, AssertionError, NotImplementedError) as err:
                # Sometimes the HILT time stamps are out of order. We think the
                # data quality is compromised so we ignore it.
                if 'data is not in order for' in str(err):
                    continue
                elif '3 matched HILT files found.' in str(err):
                    continue
                elif 'State 1 and 3 are not implemented yet.' in str(err):
                    continue
                elif 'data is not in order for' in str(err):
                    continue
                else:
                    raise

            try:
                self.attitude = sampex.Attitude(date)
                self.attitude.load()
            except ValueError as err:
                # Sometimes there is HILT data and no attitude data.
                if 'A matched file not found in' in str(err):
                    continue
                else:
                    raise
            # Magic merging!
            try:
                merged = pd.merge_asof(self.hilt.data, self.attitude.data, left_index=True, 
                    right_index=True, tolerance=pd.Timedelta(seconds=3), 
                    direction='nearest')
            except ValueError as err:
                if 'keys must be sorted' in str(err):
                    continue
                else:
                    raise
            
            self.bin_data(merged)

    def bin_data(self, merged):
        """
        Groups the SAMPEX data in each L and MLT and calculates self.stat statistic
        on the grouped counts.
        """
        for i, (start_L, end_L) in enumerate(zip(self.L_bins[:-1], self.L_bins[1:])):
            for j, (start_MLT, end_MLT) in enumerate(zip(self.MLT_bins[:-1], self.MLT_bins[1:])):
                filtered_data = merged.loc[
                    (merged.loc[:, 'L_Shell'] > start_L) &
                    (merged.loc[:, 'L_Shell'] <= end_L) &
                    (merged.loc[:,'MLT'] > start_MLT) &
                    (merged.loc[:, 'MLT'] <= end_MLT),
                    :
                ]
                if filtered_data.shape[0] == 0:
                    continue
                # Calculate incremental mean since were looping over many days.
                # https://math.stackexchange.com/questions/106700/incremental-averaging
                # https://ubuntuincident.wordpress.com/2012/04/25/calculating-the-average-incrementally/
                # Maybe this for loop can be replaced by itertools.accumulate?
                # for _, row in filtered_data.iterrows():
                #     adjustment = (row[self.counts_col] - self.mean[i, j])/self.mean_sampes[i, j]
                #     self.mean[i, j] += adjustment
                #     self.mean_sampes[i, j] += 1
                self.mean[i,j] = (
                    self.mean_sampes[i, j]*self.mean[i,j] + np.sum(filtered_data[self.counts_col])
                    )/(self.mean_sampes[i, j]+filtered_data.shape[0])
        return

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
    try:
        m.loop()
    finally:
        plt.pcolormesh(MLT_bins, L_bins, m.mean)
        plt.colorbar()
        plt.show()