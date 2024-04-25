import pandas as pd
from meshiphi.mesh_generation.boundary import Boundary
from meshiphi.utils import round_to_sigfig


class MeshComparator:
    SIG_FIG_TOLERANCE = 4
    
    def compare_cellbox_boundaries(self, mesh1, mesh2):
        """
        Compare the boundaries of the cellboxes in the two meshes

        Args: 
            mesh1 (json): the first mesh to compare
            mesh2 (json): the second mesh to compare

        Returns:
            dict: a dictionary containing the results of the comparison

        """
        results = {}

        cellboxes1 = pd.DataFrame(mesh1['cellboxes'].set_index('geometry'))
        cellboxes2 = pd.DataFrame(mesh2['cellboxes'].set_index('geometry'))

        matching_cells = 0
        mismatch_cells = 0
        split_cells = 0

        for cell in cellboxes1.index:
            if cell in cellboxes2.index:
                matching_cells += 1
            else:
                # Test if the split cellboxes exist in the other mesh
                bounds = Boundary.from_poly_string(row)
                split_bounds = bounds.split()

                found_split_cells = 0 
                for bound in split_bounds:
                    if bound.to_poly_string() in cellboxes2.index:
                        found_split_cells += 1    
                
                if found_split_cells == 4:
                    split_cells += 1
                else:
                    mismatch_cells += 1

        results['matching_cells'] = matching_cells
        results['mismatch_cells'] = mismatch_cells
        results['split_cells'] = split_cells   

        return results  

    def get_missing_cellbox_ids(self, mesh1, mesh2):
        """
            Returns the ID's all all cellboxes in mesh1 which are not#
            in mesh2

            Args: 
                mesh1 (json): The first mesh to compare
                mesh2 (json): The second mesh to compare

            Returns:

                list: A list of the ID's of the missing cellboxes
        """

        cellboxes1 = pd.DataFrame(mesh1['cellboxes']).set_index('geometry')
        cellboxes2 = pd.DataFrame(mesh2['cellboxes']).set_index('geometry')

        missing_cells = []

        for cell in cellboxes1.index:
            if cell not in cellboxes2.index:
                cellbox = cellboxes1.loc[cell]
                missing_cells.append(cellbox['id'])

        for cell in cellboxes2.index:
            if cell not in cellboxes1.index:
                cellbox = cellboxes2.loc[cell]
                missing_cells.append(cellbox['id'])
        

        return missing_cells

        
    def compare_cellbox_values(self, mesh1, mesh2):
        """
        Compare the values of the cellboxes in the two meshes

        Args:
            mesh1 (json): the first mesh to compare
            mesh2 (json): the second mesh to compare

        Returns:
            DataFrame: a dataframe containing the results of the comparison
        """

        df_a = pd.DataFrame(mesh1['cellboxes']).set_index('geometry')
        df_b = pd.DataFrame(mesh2['cellboxes']).set_index('geometry')

        
        for df in [df_a, df_b]:
            # Round float values to significant figure
            float_cols = df.select_dtypes(include=float).columns
            for col in float_cols:
                df[col] = round_to_sigfig(df[col].to_numpy(), self.SIG_FIG_TOLERANCE)

            # Round all float values in lists to significant figure
            list_cols = df.select_dtypes(include=list).columns
            for col in list_cols:
                round_col = list()
                for val in df[col]:
                    if isinstance(val, list) and all([isinstance(x, float) for x in val]):
                        round_col.append(round_to_sigfig(v, self.SIG_FIG_TOLERANCE))
                    else:
                        round_col.append(val)
                df[col] = round_col

        # Compare the two dataframes
        diff = df_a.compare(df_b).rename(columns={'self': 'mesh1', 'other': 'mesh2'})

        return diff

    def compare_cellbox_attributes(self, mesh1, mesh2):  
        """
        Compare the attributes of the cellboxes in the two meshes

        Args:
            mesh1 (json): the first mesh to compare
            mesh2 (json): the second mesh to compare

        Returns:
            dict: a dictionary containing the results of the comparison
        """

        mesh1_attributes = set(mesh1['cellboxes'][0].keys())
        mesh2_attributes = set(mesh2['cellboxes'][0].keys())

        missing_attributes_1 = mesh1_attributes.difference(mesh2_attributes)
        missing_attributes_2 = mesh2_attributes.difference(mesh1_attributes)

        results = {}

        results['missing_attributes_1'] = missing_attributes_1
        results['missing_attributes_2'] = missing_attributes_2

        return results    

    def compare_neighbour_graph_values(self, mesh1, mesh2):
        """
        Compare the values of the neighbour graph in the two meshes 

        Args:
            mesh1 (json): the first mesh to compare
            mesh2 (json): the second mesh to compare

        Returns:
            dict: a dictionary containing the results of the comparison
        """

        ng_1 = mesh1['neighbour_graph']
        ng_2 = mesh2['neighbour_graph']

        mismatch_neighbours = dict()

        for node in ng_1.keys():
            if node in ng_2.keys():
                
                neighbours_1 = ng_1[node]
                neighbours_2 = ng_2[node]

                sorted_neighbours_1 = {k:sorted(neighbours_1[k]) for k in neighbours_1.keys()}
                sorted_neighbours_2 = {k:sorted(neighbours_2[k]) for k in neighbours_2.keys()}

                if sorted_neighbours_1 != sorted_neighbours_2:
                    mismatch_neighbours[node] = sorted_neighbours_2

        return mismatch_neighbours
