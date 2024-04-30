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
        pass
    
    def set_data(self, data, datatype='xr'):
        if datatype == 'xr':
            pass
        elif datatype == 'pd':
            pass
        else:
            raise ValueError(f'Data type {datatype} not recognised')

class TestScalarDataloader(unittest.TestCase):
    def setUp(self, bounds):
        self.xr_dataloader = PytestDataLoader(bounds).set_data(ZEROS_DATASET,
                                                               datatype='xr')
        
        self.pd_dataloader = PytestDataLoader(bounds).set_data(ZEROS_DATASET,
                                                               datatype='pd')
        
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