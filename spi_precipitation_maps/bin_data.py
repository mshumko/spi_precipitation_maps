import pathlib
from typing import Union, ClassVar

import pandas as pd
import numpy as np
import progressbar


class Bin_Data:
    """
    Bin the precipitation data by the x_col and y_col variables and 
    calculate the mean of the precipitation_col variable in each x-y bin.

    Parameters
    ----------
    x_bins: np.array
        The x bins used to histogram the data.
    y_bins: np.array
        The y bins used to histogram the data.
    x_col, y_col: str
        The names of the x and y columns to bin.
    precipitation_col: str
        The name of the counts column to bin.
    instrument: str
        The instrument class that supports looping (implements the __iter__ 
        special method and returns).

    Example
    -------
    See the example in bin_sampex_hilt.py

    Attributes
    ----------
    mean: np.array
        The mean value of precipitation_col in each x-y bin. The array shape is
        (x_bins.shape[0]-1, y_bins.shape[0]-1).
    mean_sampes: np.array
        The number of sampes in each x-y bin. The array shape is
        (x_bins.shape[0]-1, y_bins.shape[0]-1).
    """
    def __init__(
        self, x_bins: np.array, y_bins: np.array, x_col: str, y_col: str, 
        precipitation_col: str, instrument
        ) -> None:
        self.x_bins = x_bins
        self.y_bins = y_bins
        self.x_col = x_col
        self.y_col = y_col
        self.precipitation_col = precipitation_col

        self.mean = np.zeros((x_bins.shape[0]-1, y_bins.shape[0]-1))
        self.mean_sampes = np.zeros((x_bins.shape[0]-1, y_bins.shape[0]-1))
        self.instrument = instrument
        return

    def bin(self):
        """
        Loop over the instrument data (i.e. files), bin each data chunk by 
        self.x_col and self.y_col, and calculate the average of self.precipitation_col.
        """
        instrument = self.instrument()  # Need to initialize the class first.
        for data in progressbar.progressbar(instrument, redirect_stdout=True):
            self._bin_data(data)
        return

    def save_map(self, filename: str, save_dir: Union[str, pathlib.Path]=None):
        """
        Save map to a csv file.

        Parameters
        ----------
        filename: str
            The file name to save the precipitation map, in the csv format.
        save_dir: str or pathlib.Path
            The directory to save the map to. If None, it will save it to the
            spi_precipitation_maps/data/ folder.

        Returns
        -------
        pathlib.Path
            The full file path to the csv file.
        """
        if save_dir is None:
            save_dir = pathlib.Path(__file__).parent / 'data'
        else:
            save_dir = pathlib.Path(save_dir)
        save_path = save_dir / filename
        df = pd.DataFrame(
            data=self.mean, 
            index=self.x_bins[:-1], 
            columns=self.y_bins[:-1]
            )
        df.to_csv(save_path)
        return save_path

    def _bin_data(self, merged):
        """
        Groups the SAMPEX data in each L and MLT and calculates self.stat statistic
        on the grouped counts.
        """
        for i, (start_x, end_x) in enumerate(zip(self.x_bins[:-1], self.x_bins[1:])):
            for j, (start_y, end_y) in enumerate(zip(self.y_bins[:-1], self.y_bins[1:])):
                filtered_data = merged.loc[
                    (merged.loc[:, self.x_col] > start_x) &
                    (merged.loc[:, self.x_col] <= end_x) &
                    (merged.loc[:, self.y_col] > start_y) &
                    (merged.loc[:, self.y_col] <= end_y),
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
                self.mean_sampes[i,j] += filtered_data.shape[0]
        return