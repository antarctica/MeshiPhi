from polar_route.dataloaders.vector.abstract_vector import VectorDataLoader

import pandas as pd

class VectorCSVDataLoader(VectorDataLoader):
    def import_data(self, bounds):
        '''
        Reads in data from a CSV file. 
        
        Args:
            bounds (Boundary): Initial boundary to limit the dataset to
            
        Returns:
            pd.DataFrame: 
                Vector dataset within limits of bounds. 
                Dataset has coordinates 'lat', 'long', potentially 'time',
                and variable defined by column heading in csv file
        '''
        # Read in data
        df_list = []
        # NOTE: All csv files must have same columns for this to work
        for file in self.files:
            df_list += [pd.read_csv(file)]
        data = pd.concat(df_list)
        # Trim to initial datapoints
        data = self.trim_datapoints(bounds, data=data)
        
        return data
