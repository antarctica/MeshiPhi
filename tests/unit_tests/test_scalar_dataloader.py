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

# Quadrants of Earth
NE_BOUNDARY   = Boundary(around_val( 45, axis='lat'), around_val( 90, axis='long'), year_of(2000))
NW_BOUNDARY   = Boundary(around_val( 45, axis='lat'), around_val(-90, axis='long'), year_of(2000))
SE_BOUNDARY   = Boundary(around_val(-45, axis='lat'), around_val( 90, axis='long'), year_of(2000))
SW_BOUNDARY   = Boundary(around_val(-45, axis='lat'), around_val(-90, axis='long'), year_of(2000))
# Equator, meridian, antimeridian
EQ_BOUNDARY   = Boundary(around_val(  0, axis='lat'), around_val( 90, axis='long'), year_of(2000))
M_BOUNDARY    = Boundary(around_val( 45, axis='lat'), around_val(  0, axis='long'), year_of(2000))
AM_BOUNDARY   = Boundary(around_val(-45, axis='lat'), around_val(180, axis='long'), year_of(2000))


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
        pass

    def test_calculate_coverage(self):
        pass

    def test_trim_datapoints(self):
        pass

    def test_get_value(self):
        pass

    def test_get_hom_condition(self):
        pass

    def test_reproject(self):
        pass

    def test_downsample(self):
        pass

    def test_get_data_col_name(self):
        pass

    def test_set_data_col_name(self):
        pass