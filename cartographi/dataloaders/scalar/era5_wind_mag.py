from cartographi.dataloaders.scalar.abstract_scalar import ScalarDataLoader

import xarray as xr
import numpy as np


class ERA5WindMagDataLoader(ScalarDataLoader):
    def import_data(self, bounds):
        """
        Reads in data from an ERA5 NetCDF file.
        Renames coordinates to 'lat' and 'long'

        Args:
            bounds (Boundary): Initial boundary to limit the dataset to

        Returns:
            xr.Dataset:
                ERA5 wave dataset within limits of bounds.
                Dataset has coordinates 'lat', 'long', and variable 'wind_mag'
        """
        # Open Dataset
        if len(self.files) == 1:    data = xr.open_dataset(self.files[0])
        else:                       data = xr.open_mfdataset(self.files)
        # Change column names
        data = data.rename({'latitude': 'lat',
                            'longitude': 'long'})
        # Change domain of dataset from [0:360) to [-180:180)
        data = data.assign_coords(long=((data.long + 180) % 360) - 180)
        # Sort the 'long' axis so that sel() will work
        data = data.sortby('long')

        # Calculate magnitude from vector components
        data['wind_mag'] = np.sqrt(data['u10']**2 + data['v10']**2)

        # Limit to just rnn variables
        data = data['wind_mag'].to_dataset()
        # Reverse order of lat as array goes from max to min
        data = data.reindex(lat=data.lat[::-1])
        # Trim to initial datapoints
        data = self.trim_datapoints(bounds, data=data)
        
        return data
