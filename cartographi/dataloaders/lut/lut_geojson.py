from cartographi.dataloaders.lut.abstract_lut import LutDataLoader
from cartographi.mesh_generation.boundary import Boundary
import logging

import geopandas as gpd
import pandas as pd
from shapely.ops import unary_union
import numpy as np

class LutGeoJSON(LutDataLoader):
        
    def add_default_params(self, params):
        '''
        Set default values for LUT dataloader. Only unique addition over
        the regular abstracted add_default_params is the data_name
        
        Args:
            params (dict): 
                Dictionary containing attributes that are required for the
                LUT being loaded.
            
        Returns:
            (dict): 
                Dictionary of attributes the dataloader will require, 
                completed with default values if not provided in config.
        '''
        # Add default scalar params
        params = super().add_default_params(params)
        
        # Name of data being read in from GeoJSONs
        if 'data_name' not in params:
            params['data_name'] = 'dummy_data'
            
        return params
    
    
    def import_data(self, bounds):
        """
        Import a list of GeoJSON files, assign regions a value specified in
        config params, regions outside this are numpy nan values.
        
        Args:
            bounds (Boundary): Initial boundary to limit the dataset to
            
        Returns:
            exclusion_df (pd.DataFrame): 
                Dataframe of polygons with value specified in config.
                DataFrame has columns 'geometry' and 
                data_name ('dummy_data' by default)
        """
        # Read in all files specified and extract geometry of exclusion zones
        gdf_list = [gpd.read_file(file) for file in self.files]
        exclusion_df = gpd.GeoDataFrame(pd.concat(gdf_list, ignore_index=True))
        # Denote all geometries as exclusion zones
        exclusion_df[self.data_name] = self.value
        exclusion_df = pd.DataFrame(exclusion_df[['geometry',self.data_name]])
        
        # Create boundary denoting the world 
        world_polygon = Boundary([-90, 90], [-180, 180]).to_polygon()
        # Subtract out all exclusion zones
        exclusion_polygon = unary_union(exclusion_df.geometry)
        inclusion_polygon = world_polygon - exclusion_polygon
        # Add line
        exclusion_df.loc[len(exclusion_df.index)] = [inclusion_polygon, np.nan]
        # Limit to boundary
        exclusion_df = self.trim_datapoints(bounds, data=exclusion_df)

        return exclusion_df