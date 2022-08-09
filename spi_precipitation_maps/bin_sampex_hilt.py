import pathlib
import re

import numpy as np
import pandas as pd
import sampex
import matplotlib.pyplot as plt
import matplotlib.colors

from spi_precipitation_maps.bin_data import Bin_Data
from spi_precipitation_maps.dial import Dial

class Bin_SAMPEX_HILT:
    """
    Bins the state 4 HILT data between 1997 and 2012.

    If you have the SAMPEX-HILT data downloaded already, check that the
    sampex.config['data_dir'] points to that directory. Run 
    `python3 -m sampex init` in the command line to change that directory.
    """
    def __init__(self,) -> None:
        self.dates = self._get_dates()
        return

    def __iter__(self):
        """
        The special method called by the Bin_Data class.
        """
        for date in self.dates:
            print(f'Processing SAMPEX-HILT on {date.date()}')
            # try:
            self.hilt = sampex.HILT(date).load()
            # except (ValueError, AssertionError, NotImplementedError) as err:
            #     # Sometimes the HILT time stamps are out of order. We think the
            #     # data quality is compromised so we ignore it.
            #     if 'data is not in order for' in str(err):
            #         continue
            #     elif '3 matched HILT files found.' in str(err):
            #         continue
            #     elif 'State 1 and 3 are not implemented yet.' in str(err):
            #         continue
            #     elif 'data is not in order for' in str(err):
            #         continue
            #     else:
            #         raise

            try:
                self.attitude = sampex.Attitude(date).load()
            except ValueError as err:
                # Sometimes there is HILT data without corresponding attitude data.
                if 'A matched file not found in' in str(err):
                    continue
                else:
                    raise
            try:
                merged_df = pd.merge_asof(self.hilt, self.attitude, left_index=True, 
                    right_index=True, tolerance=pd.Timedelta(seconds=3), 
                    direction='nearest')
            except ValueError as err:
                if 'keys must be sorted' in str(err):
                    continue
                else:
                    raise
            yield merged_df

    def __len__(self):
        """
        How many days to process. It is called by progressbar.
        """
        return len(self.dates)

    def _get_dates(self):
        """
        Finds the SAMPEX files and converts the filenames into dates.
        """
        # Look for local SAMPEX files.
        file_name_glob = f"hhrr*"
        self.hilt_paths = sorted(
            pathlib.Path(sampex.config['data_dir']).rglob(file_name_glob))
        if len(self.hilt_paths):
            date_strs = [re.findall(r"\d+", str(f.name))[0] for f in self.hilt_paths]
            dates = [sampex.load.yeardoy2date(date_str) for date_str in date_strs]
        else:
            # Otherwise get the list of filenames online.
            downloader = sampex.Downloader(
                'https://izw1.caltech.edu/sampex/DataCenter/DATA/HILThires/State4/'
                )
            downloaders = downloader.ls(file_name_glob)
            assert len(downloaders), f'{len(downloaders)} HILT files found at {downloader.url}'

            date_strs = [re.findall(r"\d+", str(d.name()))[0] for d in downloaders]
            dates = [sampex.load.yeardoy2date(date_str) for date_str in date_strs]
        return dates

if __name__ == '__main__':
    L_bins = np.arange(2, 11)
    MLT_bins = np.arange(0, 24.1)

    m = Bin_Data(L_bins, MLT_bins, 'L_Shell', 'MLT', 'counts', Bin_SAMPEX_HILT)
    try:
        m.bin()
    finally:
        m.save_map('sampex_hilt_l_mlt_map.csv')
        # _, ax = plt.subplots(2, 1, sharex=True)
        fig = plt.figure(figsize=(9, 4))
        ax = [plt.subplot(1, 2, i, projection='polar') for i in range(1, 3)]

        L_labels = [2,4,6]
        cmap = 'viridis'

        dial1 = Dial(ax[0], MLT_bins, L_bins, m.mean)
        dial1.draw_dial(L_labels=L_labels,
            mesh_kwargs={'norm':matplotlib.colors.LogNorm(), 'cmap':cmap},
            colorbar_kwargs={'label':'mean > 1 MeV counts', 'pad':0.1})
        dial2 = Dial(ax[1], MLT_bins, L_bins, m.mean_sampes)
        dial2.draw_dial(L_labels=L_labels,
            mesh_kwargs={'norm':matplotlib.colors.LogNorm(), 'cmap':cmap},
            colorbar_kwargs={'label':'Number of sampes', 'pad':0.1})

        for ax_i in ax:
            ax_i.set_rlabel_position(235)
            ax_i.tick_params(axis='y', colors='white')

        plt.suptitle(f'SAMPEX-HILT | L-MLT map\n{m.dates[0].date()} to {m.dates[-1].date()}')
        plt.tight_layout()
        plt.show()