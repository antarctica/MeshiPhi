from meshiphi import Boundary
from meshiphi.dataloaders.scalar.abstract_scalar import ScalarDataLoader
from meshiphi.utils import longitude_domain

import unittest

import numpy as np
import xarray as xr
import pandas as pd


DATASET_SHAPE = [10, 10]

ZEROS_DATASET = np.zeros(DATASET_SHAPE)
ONES_DATASET  = np.ones(DATASET_SHAPE)
NANS_DATASET  = np.empty(DATASET_SHAPE)


def gen_dataset(bounds, data_name, data=ZEROS_DATASET):
    
    data_shape = data.shape
    lat  = np.linspace(bounds.get_lat_min(), 
                        bounds.get_lat_max(),
                        data_shape[0])
    long = np.linspace(bounds.get_long_min(), 
                        bounds.get_long_max(),
                        data_shape[1])

    dataset = xr.Dataset(
        data_vars={
            data_name: (['x','y'], data)
            },
        coords={
            'lat' :(['x','y'], lat),
            'long':(['x','y'], long)
        }
    )
    return dataset

def around_val(mid_val, total_range=10, axis=None):
    range_min = mid_val - total_range/2
    range_max = mid_val + total_range/2

    if axis == 'lat':
        if range_min < -90 or range_max > 90:
            raise ValueError(f"Lat range {range_min}:{range_max} doesn't make sense")
    elif axis == 'long':
        range_min = longitude_domain(range_min)
        range_max = longitude_domain(range_max)
    else:
        raise ValueError(f"Unknown axis {axis}")
    
    return [range_min, range_max]

def year_of(year):
    return [f'{year}-01-01', f'{year}-12-31']

def create_bounds(mid_lat, mid_long, year, deg_range=10):
    lat_range = around_val(mid_lat, total_range=deg_range, axis='lat')
    long_range = around_val(mid_long, total_range=deg_range, axis='long')
    time_range = year_of(year)

    return Boundary(lat_range, long_range, time_range)


ALL_BOUNDS = {
    # Quadrants of earth
    'north_east':   create_bounds( 45,  90, 2000),
    'north_west':   create_bounds( 45, -90, 2000),
    'south_east':   create_bounds(-45,  90, 2000),
    'south_west':   create_bounds(-45, -90, 2000),
    # Edge cases
    'equatorial':   create_bounds(  0,  90, 2000),
    'meridian':     create_bounds(-45,   0, 2000),
    'antimeridian': create_bounds(-45, 180, 2000),
    'north_pole':   create_bounds( 85,  90, 2000),
    'south_pole':   create_bounds(-85,  90, 2000)
}


class PytestDataLoader(ScalarDataLoader):
    def import_data(self, bounds):

        self.data = gen_dataset(bounds, 
                                'test_data', 
                                data=ZEROS_DATASET)
    
    def set_data(self, bounds, data, datatype=None):

        if datatype is None:
            datatype = type(data)
        elif datatype == 'pd':
            datatype = pd.core.frame.DataFrame
        elif datatype == 'xr':
            datatype = xr.core.dataset.Dataset
        
        dataloader_data = gen_dataset(bounds, 
                                      'test_data', 
                                      data=data)
        if datatype == xr.core.dataset.Dataset:
            self.data = dataloader_data
        elif datatype == pd.core.frame.DataFrame:
            self.data = dataloader_data.to_dataframe()

class TestScalarDataloader(unittest.TestCase):
    def setUp(self, bounds):
        self.xr_dataloader = PytestDataLoader(bounds)
        self.xr_dataloader.set_data(bounds, ZEROS_DATASET, datatype='xr')
        
        self.pd_dataloader = PytestDataLoader(bounds)
        self.pd_dataloader.set_data(bounds, ZEROS_DATASET, datatype='df')
        
        self.dataloaders = [self.xr_dataloader, self.pd_dataloader]
    
    def test_add_default_params(self):
        incomplete_params = {
            'irrelevant_key': None
        }
        for dataloader in self.dataloaders:
            complete_params = dataloader.add_default_params(incomplete_params)
            
            self.assertIsNone(complete_params['data_name'])
            self.assertEqual(complete_params['dataloader_name'], 'PytestDataLoader')
            self.assertEqual(complete_params['downsample_factors'], [1,1])
            self.assertEqual(complete_params['aggregate_type'], 'MEAN')
            self.assertEqual(complete_params['min_dp'], 5)
            self.assertEqual(complete_params['in_proj'], 'EPSG:4326')
            self.assertEqual(complete_params['out_proj'], 'EPSG:4326')
            self.assertEqual(complete_params['x_col'], 'lat')
            self.assertEqual(complete_params['y_col'], 'long')
            self.assertFalse(complete_params['fast_reprojection'])


    def test_calculate_coverage(self):
        raise NotImplementedError

    def test_trim_datapoints(self):
        raise NotImplementedError

    def test_get_value(self):
        raise NotImplementedError

    def test_get_hom_condition(self):
        raise NotImplementedError

    def test_reproject(self):
        raise NotImplementedError

    def test_downsample(self):
        for dataloader in self.dataloaders:
            dataloader.downsample_factors = (2,2)

            data = dataloader.downsample(agg_type='MIN')
            data = dataloader.downsample(agg_type='MAX')
            data = dataloader.downsample(agg_type='MEAN')
            data = dataloader.downsample(agg_type='MEDIAN')
            data = dataloader.downsample(agg_type='STD')
            data = dataloader.downsample(agg_type='COUNT')


    def test_get_data_col_name(self):
        # For xr and pd dataloaders
        for dataloader in self.dataloaders:
            # Make sure it returns the default variable name
            assert dataloader.get_data_col_name() == 'test_data'

    def test_set_data_col_name(self):
        # For xr and pd dataloaders
        for dataloader in self.dataloaders:
            # Set variable name to something other than 'test_data'
            data = dataloader.set_data_col_name('data_test')
            # Get a list of variables stored
            if isinstance(data, pd.core.frame.DataFrame):
                data_names = data.columns
            elif isinstance(data, xr.core.dataset.Dataset):
                data_names = list(data.keys())
            # Ensure there is still only one variable, with the name 'data_test'
            assert len(data_names) == 1
            assert 'data_test' in data_names