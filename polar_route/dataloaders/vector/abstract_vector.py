from polar_route.dataloaders.dataloader_interface import DataLoaderInterface
from abc import abstractmethod

from pyproj import Transformer, CRS

import logging
import numpy as np
import xarray as xr
import pandas as pd

class VectorDataLoader(DataLoaderInterface):
    '''
    Abstract class for all vector Datasets.
    '''
    def __init__(self, bounds, params):
        '''
        This is where large-scale operations are performed, 
        such as importing data, downsampling, reprojecting, and renaming 
        variables
        
        Args:
            bounds (Boundary): 
                Initial mesh boundary to limit scope of data ingest
            params (dict): 
                Values needed by dataloader to initialise. Unique to each
                dataloader

        Attributes:
            self.data (pd.DataFrame or xr.Dataset): 
                Data stored by dataloader to use when called upon by the mesh.
                Must be saved in mercator projection (EPSG:4326), with 
                coordinates names 'lat', 'long', and 'time' (if applicable).
            self.data_name (str): 
                Name of scalar variable. Must be the column name if self.data
                is pd.DataFrame. Must be variable if self.data is xr.Dataset
        '''
        logging.info(f"Initialising {params['dataloader_name']} dataloader")
        # Translates parameters from config input to desired inputs
        params = self.add_params(params)
        # Creates a class attribute for all keys in params
        for key, val in params.items():
            setattr(self, key, val)
            
        # Read in and manipulate data to standard form
        if 'files' in params:
            logging.info('\tReading in files:')
            for file in self.files:
                logging.info(f'\t\t{file}')
        self.data = self.import_data(bounds)
        # If need to downsample data
        self.data = self.downsample()
        # If need to reproject data
        if self.in_proj != self.out_proj:
            self.data = self.reproject(
                                in_proj  = self.in_proj,
                                out_proj = self.out_proj,
                                x_col    = self.x_col,
                                y_col    = self.y_col
                                )
        # Cut dataset down to initial boundary
        logging.info(
            "\tTrimming data to initial boundary: {min} to {max}".format(
                min=(bounds.get_lat_min(), bounds.get_long_min()),
                max=(bounds.get_lat_max(), bounds.get_long_max())
            ))
        self.data = self.trim_datapoints(bounds)

        # Get data name from column name if not set in params
        if self.data_name is None:
            logging.debug('- Setting self.data_name from column name')
            self.data_name = self.get_data_col_name()
        # or if set in params, set col name to data name
        else:
            logging.debug(f'- Setting data column name to {self.data_name}')
            self.data = self.set_data_col_name(self.data_name.split(','))
        # Store data names in a list for easier access in future
        self.data_name_list = self.data_name.split(',')
        
        # Add magnitude and direction to dataset
        self.data = self.add_mag_dir()

    @abstractmethod
    def import_data(self, bounds):
        '''
        User defined method for importing data from files, or even generating 
        data from scratch
                
        Returns:
            xr.Dataset or pd.DataFrame:
                Coordinates and data being imported from file \n
                if xr.Dataset, 
                    - Must have coordinates 'lat' and 'long'
                    - Should have multiple data variables
                    
                if pd.DataFrame, 
                    - Must have columns 'lat' and 'long'
                    - Should have multiple data columns
                    
                Downsampling and reprojecting happen in __init__() method
        '''
        pass
    
    def add_params(self, params):
        '''
        Provides option to add parameters before dataloader initialised,
        useful for translating params from config to specific default 
        parameters for dataloader. Does nothing by default, but user can
        overload to add to specific dataloader
        
        Args:
            params (dict): 
                Dictionary holding keys and values that will be turned into 
                object attributes
        
        Returns:
            dict:
                Params dictionary with addition of translated key/value pairs
        '''
        return params
    
    def add_mag_dir(self, data=None, data_names=None):
        
        def add_mag_dir_to_df(data, names):
            x, y = names
            data['magnitude'] = np.linalg.norm([data[x], data[y]], axis=0)
            data['direction'] = np.arctan(data[y] / data[x])
            return data
        
        def add_mag_dir_to_xr(data, names):
            x, y = names
            data = data.assign(
                _magnitude=lambda l: (['lat', 'long'],
                                        np.linalg.norm([l[x], l[y]], axis=0)))
            data = data.assign(
                _direction=lambda l:(['lat','long'],
                                        np.arctan(l[y].data / l[x].data)))
            return data
        
        if data is None:
            data = self.data
        
        if data_names is None:
            names = self.data_name_list
        
        
        if type(data) == pd.core.frame.DataFrame:
            return add_mag_dir_to_df(data, names)
        elif type(data) == xr.core.dataset.Dataset:
            return add_mag_dir_to_xr(data, names)

    def trim_datapoints(self, bounds, data=None):
        '''
        Trims datapoints from self.data within boundary defined by 'bounds'.
        self.data can be pd.DataFrame or xr.Dataset
        
        Args:
            bounds (Boundary): Limits of lat/long/time to select data from

        Returns:
            pd.DataFrame or xr.Dataset: 
                Trimmed dataset in same format as self.data
        '''
        def trim_datapoints_from_df(data, bounds):
            '''
            Extracts data from a pd.DataFrame
            '''
            # Mask off any positions not within spatial bounds
            mask = (data['lat']  > bounds.get_lat_min())  & \
                   (data['lat']  <= bounds.get_lat_max())  & \
                   (data['long'] > bounds.get_long_min()) & \
                   (data['long'] <= bounds.get_long_max())
            # Mask with time if time column exists
            if 'time' in data.columns:
                mask &= (data['time'] >= bounds.get_time_min()) & \
                        (data['time'] <= bounds.get_time_max())
                        
            # Return column of data from within bounds
            return data.loc[mask]

        def trim_datapoints_from_xr(data, bounds):
            '''
            Extracts data from a xr.Dataset
            '''
            # Select data region within spatial bounds
            # NOTE slice in xarray is inclusive of bounds
            data = data.sel(lat=slice(bounds.get_lat_min(),  bounds.get_lat_max() ))
            data = data.sel(long=slice(bounds.get_long_min(), bounds.get_long_max()))
            # Select data region within temporal bounds if time exists as a coordinate
            if 'time' in data.coords.keys():
                data = data.sel(time=slice(bounds.get_time_min(),  bounds.get_time_max()))

            # Trim off any data on the min boundary to be consistent with df
            if bounds.get_lat_min() in data.lat:
                data = data.where(data.lat  != bounds.get_lat_min(), drop=True)
            if bounds.get_long_min() in data.long:
                data = data.where(data.long != bounds.get_long_min(), drop=True)
            
            # Return column of data from within bounds
            return data
        
        # If no specific data passed in, default to entire dataset
        if data is None:
            data = self.data
        
        # Skip trimming if data already completely within bounds
        if data.lat.min() >  bounds.get_lat_min() and \
           data.lat.max() <= bounds.get_lat_max() and \
           data.long.min() >  bounds.get_long_min() and \
           data.long.max() <= bounds.get_long_max():
            logging.debug('Data is already trimmed to bounds!')
            return data
        
        if type(data) == pd.core.frame.DataFrame:
            return trim_datapoints_from_df(data, bounds)
        elif type(data) == xr.core.dataset.Dataset:
            return trim_datapoints_from_xr(data, bounds)

    def get_dp_from_coord(self, long=None, lat=None, return_coords=False):
        '''
        Extracts datapoint from self.data with lat and long specified in kwargs.
        self.data can be pd.DataFrame or xr.Dataset. Will return multiple values
        if one set of coordinates have multiple entries (e.g. time series data)
        
        Args:
            long (float): Longitude coordinate to search for
            lat (float) : Latitude coordinate to search for
            
        Returns:
            pd.Dataframe:  
                Column of data values with chosen lat/long. Could be many 
                datapoints because either bad data or multiple time steps 
        '''
        def get_dp_from_coord_df(data, names, long, lat, return_coords):
            '''
            Extracts data from a pd.DataFrame
            '''
            # Mask off any positions not within spatial bounds
            mask = (data['lat']  == lat)  & \
                   (data['long'] == long) 

            # Include lat/long/time if requested
            if return_coords: columns = list(data.columns)
            else:             columns = names
            # Return column of data from within bounds
            return data.loc[mask][columns]
        
        def get_dp_from_coord_xr(data, names, long, lat, return_coords):
            '''
            Extracts data from a xr.Dataset
            '''
            # Select data region within spatial bounds
            data = data.sel(lat=lat, long=long)
            # Cast as a pd.DataFrame
            data = data.to_dataframe().reset_index()
            # Include lat/long/time if requested
            if return_coords: columns = list(data.columns)
            else:             columns = names
            # Return column of data from within bounds
            return data[columns]
        
        # Ensure that lat and long provided
        assert (lat is not None) and (long) is not None, \
            'Must provide lat and long to this method!'
            
        # Choose which method to retrieve data based on input type
        if type(self.data) == pd.core.frame.DataFrame:
            return get_dp_from_coord_df(self.data, self.data_name_list, long, lat, return_coords)
        elif type(self.data) == xr.core.dataset.Dataset:
            return get_dp_from_coord_xr(self.data, self.data_name_list, long, lat, return_coords)
    
    def get_value(self, bounds, agg_type=None, skipna=True):
        '''
        Retrieve aggregated value from within bounds
        
        Args:
            aggregation_type (str): Method of aggregation of datapoints within
                bounds. Can be upper or lower case. 
                Accepts 'MIN', 'MAX', 'MEAN', 'MEDIAN', 'STD', 'COUNT'
            bounds (Boundary): Boundary object with limits of lat/long
            skipna (bool): Defines whether to propogate NaN's or not
                Default = True (ignore's NaN's)

        Returns:
            dict: 
                {variable (str): aggregated_value (float)}
                Aggregated value within bounds following aggregation_type
                
        Raises:
            ValueError: aggregation type not in list of available methods
        '''
        def get_value_from_df(dps, variable_names, bounds, agg_type, skipna):
            '''
            Aggregates a value from a pd.Series.
            
            Args:
                dps (pd.Series): Datapoints within boundary
                bounds (Boundary): 
                    Boundary dps was trimmed to. Not used for any calculations,
                    just the logging.debug message.
                agg_type (str):
                    Method of aggregation for the value, 
                    e.g. agg_type = 'MIN' => min(dps) returned 
                skipna (bool): 
                    Flag for whether NaN's should be included in aggregation. 
            
            Returns:
                np.float64: Aggregated value
            '''
            data_count = len(dps)
            logging.debug(f"    {data_count} datapoints found for attribute '{self.data_name}' within bounds '{bounds}'")
            # If no data
            if data_count == 0:
                values = [np.nan, np.nan]
            # If want the number of datapoints
            elif agg_type =='COUNT':
                values = [data_count, data_count]
            elif agg_type == 'MIN':
                index = dps['_magnitude'].idxmin(skipna=skipna)
                values = [dps[name][index] for name in variable_names]
            elif agg_type == 'MAX':
                index = dps['_magnitude'].idxmax(skipna=skipna)
                values = [dps[name][index] for name in variable_names]
            elif agg_type == 'MEAN':
                values = [dps[name].mean(skipna=skipna) for name in variable_names]
            elif agg_type == 'STD':
                values = [dps[name].std(skipna=skipna) for name in variable_names]
            elif agg_type == 'MEDIAN':
                raise ValueError('Aggregation type "MEDIAN" is non-sensical for vector dataset!')
            else:
                raise ValueError(f'Unknown aggregation type {agg_type}')
            
            return values

        
        def get_value_from_xr(dps, variable_names, bounds, agg_type, skipna):
            '''
            Aggregates a value from a xr.DataArray.
            
            Args:
                dps (xr.DataArray): Datapoints within boundary
                bounds (Boundary): 
                    Boundary dps was trimmed to. Not used for any calculations,
                    just the logging.debug message.
                agg_type (str):
                    Method of aggregation for the value, 
                    e.g. agg_type = 'MIN' => min(dps) returned 
                skipna (bool): 
                    Flag for whether NaN's should be included in aggregation. 
            
            Returns:
                dict:
                    {variable_name: np.float64}: Aggregated value in a dictionary
            '''
            # Info on size of array
            data_count = dps._magnitude.size 
            logging.debug(f"    {data_count} datapoints found for attribute '{self.data_name}' within bounds '{bounds}'")
            # If no data, return np.nan for each variable
            if data_count == 0:
                values = [np.nan, np.nan]
            # If want count
            elif agg_type == 'COUNT':
                # If including nan's, just want size
                if skipna:  
                    values = [data_count, data_count]
                # Otherwise count non-nan values
                else:       
                    values = [dps[name].count().item() for name in variable_names]
            elif agg_type == 'MIN':
                # Get 2D index of minimum magnitude point
                index = np.unravel_index(
                            dps._magnitude.argmin(skipna=skipna), 
                            dps._magnitude.shape)
                # Get cartesian vector from index
                values = [dps[name][index].item() for name in variable_names]
            elif agg_type == 'MAX':
                # Get 2D index of minimum magnitude point
                index = np.unravel_index(
                            dps._magnitude.argmax(skipna=skipna), 
                            dps._magnitude.shape)
                # Get cartesian vector from index
                values = [dps[name][index].item() for name in variable_names]
            # And the rest self explanatory
            elif agg_type == 'MEAN':
                values = [dps[name].mean(skipna=skipna) for name in variable_names]
            elif agg_type == 'STD':
                values = [dps[name].std(skipna=skipna) for name in variable_names]
            elif agg_type == 'MEDIAN':
                raise ValueError('Aggregation type "MEDIAN" is non-sensical for vector dataset!')
            else:
                raise ValueError(f'Unknown aggregation type {agg_type}')
            
            return values
    

        # Set to params if no specific aggregate type specified
        if agg_type is None:
            agg_type = self.aggregate_type
            
        # Limit data to boundary
        dps = self.trim_datapoints(bounds)
        # Get list of values
        if type(self.data) == pd.core.frame.DataFrame:
            values = get_value_from_df(dps, bounds, agg_type, skipna)
        elif type(self.data) == xr.core.dataset.Dataset:
            values = get_value_from_xr(dps, self.data_name_list, bounds, agg_type, skipna)
            
        # Put in dict to map variable to values
        return {self.data_name_list[i]: values[i] for i in range(len(self.data_name_list))}

    def get_hom_condition(self, bounds, splitting_conds, agg_type='MEAN'):
        '''
        Not implemented yet. Retrieves homogeneity condition of data within
        boundary.
         
        Args: 
            bounds (Boundary): Boundary object with limits of datarange to analyse
            splitting_conds (dict): Containing the following keys: \n
                'threshold':  
                    `(float)` The threshold at which data points of 
                    type 'value' within this CellBox are checked to be either 
                    above or below
                'upper_bound': 
                    `(float)` The lowerbound of acceptable percentage 
                    of data_points of type value within this boundary that are 
                    above 'threshold'
                'lower_bound': 
                    `(float)` The upperbound of acceptable percentage 
                    of data_points of type value within this boundary that are 
                    above 'threshold'

        Returns:
            str:
                The homogeniety condtion returned is of the form: \n
                'MIN' = the cellbox contains less than a minimum number of 
                data points \n
                'HET' = Threshold values defined in config are exceeded \n
                'CLR' = None of the HET conditions were triggered \n
        '''
        # Get length of dataset in bounds  
        if type(self.data) == pd.core.frame.DataFrame:
            num_dp = len(self.trim_datapoints(bounds))
        elif type(self.data) == xr.core.dataset.Dataset:
            num_dp = min(self.trim_datapoints(bounds).count().values())

        # Check to see if it's above the minimum threshold
        if num_dp < self.min_dp:
            return 'MIN'
        
        # To allow multiple modes of splitting, chuck them in the splitting conditions
        # Split if magnitude of curl(data) is larger than threshold 
        if 'curl' in splitting_conds:
            curl = self.calc_curl(bounds)
            if np.abs(curl) > splitting_conds['curl']:
                return 'HET'
        # Split if max magnitude(any_vector - ave_vector) is larger than threshold
        if 'dmag' in splitting_conds:
            dmag = self.calc_dmag(bounds)
            if np.abs(dmag) > splitting_conds['dmag']:
                return 'HET'
            
        # Split if Reynolds number is larger than threshold
        if 'reynolds' in splitting_conds:        
            reynolds = self.calc_reynolds_number(bounds)
            if reynolds > splitting_conds['reynolds']:
                return 'HET'
        
        # TODO
        # HOM would only apply if whole cell is faster than vehicle, which wouldn't be calculated in the mesh generation stage?
        # Non-navigable cells pruned in next step so leaving out for now
                
        # If none of the above return conditions are triggered, cell is clear
        return 'CLR'

    def reproject(self, in_proj='EPSG:4326', out_proj='EPSG:4326', 
                        x_col='lat', y_col='long'):
        '''
        Reprojects data using pyProj.Transformer
        self.data can be pd.DataFrame or xr.Dataset
        
        Args:
            in_proj (str): 
                Projection that the imported dataset is in
                Must be allowed by PyProj.CRS (Coordinate Reference System)
            out_proj (str): 
                Projection required for final data output
                Must be allowed by PyProj.CRS (Coordinate Reference System)
                Shouldn't change from default value (EPSG:4326)
            x_col (str): Name of coordinate column 1
            y_col (str): Name of coordinate column 2
                x_col and y_col will be cast into lat and long by the 
                reprojection 
            
        Returns:
            pd.DataFrame: 
                Reprojected data with 'lat', 'long' columns 
                replacing 'x_col' and 'y_col'
        '''
        def reproject_df(data, in_proj, out_proj, x_col, y_col):
            '''
            Reprojects a pandas dataframe
            '''
            # Do the reprojection
            x, y = Transformer\
                    .from_crs(CRS(in_proj), CRS(out_proj), always_xy=True)\
                    .transform(data[x_col].to_numpy(), data[y_col].to_numpy())
            # Replace columns with reprojected columns called 'lat'/'long'
            if x_col != 'lat':  data = data.drop(x_col, axis=1)
            if y_col != 'long': data = data.drop(y_col, axis=1)
            data['lat']  = y
            data['long'] = x
            
            return data
            
        def reproject_xr(data, in_proj, out_proj, x_col, y_col):
            '''
            Reprojects a xarray dataset
            '''
            # Cast to dataframe, then reproject using reproject_df
            # Cannot reproject directly as memory usage skyrockets
            df = data.to_dataframe().reset_index()
            return reproject_df(df, in_proj, out_proj, x_col, y_col)

        # If no reprojection to do
        if in_proj == out_proj:
            logging.debug("\tself.reproject() called but don't need to")
            return self.data
        else:
            logging.info(f"\tReprojecting data from {in_proj} to {out_proj}")
        # Choose appropriate method of reprojection based on data type
        if type(self.data) == pd.core.frame.DataFrame:
            return reproject_df(self.data, in_proj, out_proj, x_col, y_col)
        elif type(self.data) == xr.core.dataset.Dataset:
            return reproject_xr(self.data, in_proj, out_proj, x_col, y_col)
    
    def downsample(self, agg_type=None):
        '''
        Downsamples imported data to be more easily manipulated. Data size 
        should be reduced by a factor of m*n, where (m,n) are the 
        downsample_factors defined in the params.        
        self.data can be pd.DataFrame or xr.Dataset
        
        Args:
            agg_type (str): 
                Method of aggregation to bin data by to downsample. Default is
                same method used for homogeneity condition.            

        Returns:
            xr.Dataset or pd.DataFrame: 
                Downsampled data
        '''
        def downsample_xr(data, ds, agg_type):
            '''
            Downsample xarray dataset according to aggregation type
            
            Args:
                data (xr.Dataset):
                    Dataset containing data to be downsampled. Must have 
                    coordinates 'lat' and 'long'
                ds (int, int):
                    Downsampling factors. 
                    ds[0] is longitude
                    ds[1] is latitude
                agg_type (str):
                    Aggregation method to use for binning. Default is same as 
                    set in config, passed in by parent
            
            Returns:
                xr.Dataset:
                    Downsampled data
            '''
            if agg_type == 'MIN':
                # Returns min of bin
                data = data.coarsen(lat=ds[1],boundary='pad').min()
                data = data.coarsen(long=ds[0],boundary='pad').min()
            elif agg_type == 'MAX':
                # Returns max of bin
                data = data.coarsen(lat=ds[1],boundary='pad').max()
                data = data.coarsen(long=ds[0],boundary='pad').max()
            elif agg_type == 'MEAN':
                # Returns mean of bin
                data = data.coarsen(lat=ds[1],boundary='pad').mean()
                data = data.coarsen(long=ds[0],boundary='pad').mean()
            elif agg_type == 'MEDIAN':
                # Returns median of bin
                data = data.coarsen(lat=ds[1],boundary='pad').median()
                data = data.coarsen(long=ds[0],boundary='pad').median()
            elif agg_type == 'STD':
                # Returns std_dev of range
                data = data.coarsen(lat=ds[1],boundary='pad').std()
                data = data.coarsen(long=ds[0],boundary='pad').std()
            elif agg_type =='COUNT': 
                # Returns every first element in bin
                data = data.thin(lat=ds[1])
                data = data.thin(long=ds[0])
            return data
    
        def downsample_df(data, ds, agg_type):
            '''
            Downsample pandas dataframe
            Not implemented as it just adds to processing time, 
            defeating the purpose
            '''
            logging.warning(
                '- Downsampling called on pd.DataFrame! Downsampling a df' \
                'too computationally expensive, returning original df'
                )
            return data

        # Set to params if no specific aggregate type specified
        if agg_type is None:
            agg_type = self.aggregate_type
        
        # If no downsampling
        if self.downsample_factors == (1,1) or \
           self.downsample_factors == [1,1]:
            logging.debug("- self.downsample() called but don't have to")
            return self.data
        else:
            logging.info(f"- Downsampling data by {self.downsample_factors}")
        # Otherwise, downsample appropriately
        if type(self.data) == pd.core.frame.DataFrame:
            return downsample_df(self.data, self.downsample_factors, agg_type)
        elif type(self.data) == xr.core.dataset.Dataset:
            return downsample_xr(self.data, self.downsample_factors, agg_type)
        
    def get_data_col_name(self):
        '''
        Retrieve name of data column (for pd.DataFrame), or variable 
        (for xr.Dataset). Used for when data_name not defined in params.
        Variable names are appended and comma seperated

        Returns:
            str: 
                Name of data columns, comma seperated
        '''
        def get_data_names_from_df(data):
            '''
            Filters out standard columns to extract only data column's name
            '''
            # Store name of data column for future reference
            columns = data.columns
            # Filter out lat, long, time columns leaves us with data column name
            filtered_cols = filter(lambda col: \
                                    col not in ['lat','long','time'], columns)
            data_names = list(filtered_cols)
            # Turn into comma seperated string and return
            return ','.join(data_names)
        
        def get_data_names_from_xr(data):
            '''
            Extracts variable name directly from xr.Dataset metadata
            '''
            # Extract data variables from xr.Dataset
            data_names = list(data.keys())
            # Turn into comma seperated string and return
            return ','.join(data_names)
        
        # Choose method of extraction based on data type
        if type(self.data) == pd.core.frame.DataFrame:
            return get_data_names_from_df(self.data)
        elif type(self.data) == xr.core.dataset.Dataset:
            return get_data_names_from_xr(self.data)

    def get_data_col_name_list(self):
        '''
        Retrieve names of data columns (for pd.DataFrame), or variable 
        (for xr.Dataset). Used for when data_name not defined in params.

        Returns:
            list: 
                Contains strings of data namesk
        '''
        return self.get_data_col_name().split(',')

    def set_data_col_name(self, new_names):
        '''
        Sets name of data column/data variables
        
        Args:
            name_dict (dict): 
                Dictionary mapping old variable names to new variable names,
                of the form {old_name (str): new_name (str)}

        Returns:
            xr.Dataset or pd.DataFrame: 
                Data with variable name changed
        '''
        def set_names_df(data, name_dict):
            '''
            Renames data columns in pandas dataframe
            '''
            # Rename data column to new name
            return data.rename(columns=name_dict)
        def set_names_xr(data, name_dict):
            '''
            Renames data variables in xarray dataset
            '''
            # Rename data variable to new name
            return data.rename(name_dict)
        # Get existing column names
        old_names = self.get_data_col_name().split(',')
        # Ensure that can do replacement of columns
        assert len(old_names) == len(new_names)
        # Set up mapping of old names to new names
        name_dict = {old_col: new_names[i] 
                     for i, old_col in enumerate(old_names)}
        # Change names
        # Change data name depending on data type
        if type(self.data) == pd.core.frame.DataFrame:
            return set_names_df(self.data, name_dict)
        elif type(self.data) == xr.core.dataset.Dataset:
            return set_names_xr(self.data, name_dict)
        
    def set_data_col_name_list(self, new_names):
        assert type(new_names) == list, f"'new_names' must be a list! Instead it is a {type(new_names)}"
        assert len(new_names) == 2, f"'new_names' must have a length of 2! Instead it has length {len(new_names)}"
        str_items = [isinstance(name, str) for name in new_names]
        assert all(str_items, f"'new_names' must be list of 'str'. Currently {sum(str_items)} / 2 are strings!")
        new_data_name = ','.join(new_names)
        
        logging.info(f'Setting data names to {new_names}')
        self.data_name_list = new_names
        self.data = self.set_data_col_name(new_data_name)

    def calc_reynolds_number(self, bounds, agg_type='MEAN'):
        # Extract the speed
        velocity = self.get_value(bounds, agg_type=agg_type)
        speed = np.linalg.norm(list(velocity.values())) # Calculates magnitude
        # Extract the characteristic length
        length = bounds.calc_size()
        # Calculate the reynolds number and return
        return 1028 * 0.00167 * speed * length

    def calc_divergence(self, bounds, data=None, collapse=True, agg_type='MAX'):
        # Create a meshgrid of vectors from the data
        vector_field = self._create_vector_meshgrid(bounds, data)
        # Get component values for each vector
        fx, fy = vector_field[:, :, 0], vector_field[:, :, 1]
        # Compute partial derivatives
        dfx_dy = np.gradient(fx, axis=1)
        dfy_dx = np.gradient(fy, axis=0)
        # Compute divergence
        div = dfy_dx + dfx_dy
        
        # If want to collapse to max mag value, return scalar
        if collapse:   
            if agg_type == 'MAX': return max(np.nanmax(div), np.nanmin(div), key=abs)
            else:                 return np.nanmean(div)
        # Else return field
        else:          return div


    def calc_curl(self, bounds, data=None, collapse=True, agg_type='MAX'):
        # Create a meshgrid of vectors from the data
        dps = self.trim_datapoints(bounds, data=data)
        vector_field = self._create_vector_meshgrid(dps, self.data_name_list)
        # Get component values for each vector
        fx, fy = vector_field[:, :, 0], vector_field[:, :, 1]
        # Compute partial derivatives
        dfx_dy = np.gradient(fx, axis=1)
        dfy_dx = np.gradient(fy, axis=0)
        # Compute curl
        curl = dfy_dx - dfx_dy
        
        # If want to collapse to max mag value, return scalar
        if collapse:
            if agg_type == 'MAX': return max(np.nanmax(curl), np.nanmin(curl), key=abs)
            else:                 return np.nanmean(curl)
        # Else return field
        else:          return curl

    def calc_dmag(self, bounds, data=None, collapse=True, agg_type='MEAN'):
        # Create a meshgrid of vectors from the data
        dps = self.trim_datapoints(bounds, data=data).dropna()
        data_names = self.data_name_list
        each_vector = dps[data_names].to_numpy()
        ave_vector = list(self.get_value(bounds, agg_type=agg_type).values())
        
        delta_vector = each_vector - ave_vector
        
        d_mag = np.linalg.norm(delta_vector, axis=1)
        if len(d_mag) == 0:
            return np.nan
        
        # If want to collapse to max mag value, return scalar
        elif collapse:   return np.nanmean(d_mag)
        # Else return field
        else:          return d_mag
    
    @staticmethod
    def _create_vector_meshgrid(data, data_name_list):
        # Manipulate into meshgrid of 2D vectors
        x, y = data_name_list
        # Fields of each vector component
        vector_x_field = data.pivot(index='lat', columns='long', values=x)
        vector_y_field = data.pivot(index='lat', columns='long', values=y)
        # Combine into field of vectors
        vector_field = np.stack((vector_x_field, vector_y_field), axis=-1)
        vector_field = np.swapaxes(vector_field, 0, 1)
        
        return vector_field
    
    