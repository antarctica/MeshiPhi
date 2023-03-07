from polar_route.mesh_generation.environment_mesh import EnvironmentMesh
from polar_route.vessel_performance.VesselFactory import VesselFactory
import numpy as np
import logging

class VesselPerformanceModeller:
    """
        Class for modelling the vessel performance.
        Takes both an environmental mesh and vessel config as input in json format and modifies the input mesh to
        include vessel specifics.
    """
    def __init__(self, env_mesh_json, vessel_config):
        """

        Args:
            env_mesh_json (dict): a dictionary loaded from an environmental mesh json file
            vessel_config (dict): a dictionary loaded from a vessel config json file
        """
        logging.info("Initialising Vessel Performance Modeller")

        self.env_mesh = EnvironmentMesh.load_from_json(env_mesh_json)
        self.vessel = VesselFactory.get_vessel(vessel_config)

        self.filter_nans()

    def model_accessibility(self):
        """

        Method to determine the accessibility of cells in the environmental mesh and remove inaccessible cells from the
        neighbour graph.

        """
        for i, cellbox in enumerate(self.env_mesh.agg_cellboxes):
            access_values = self.vessel.model_accessibility(cellbox)
            self.env_mesh.update_cellbox(i, access_values)
        inaccessible_nodes = [c.id for c in self.env_mesh.agg_cellboxes if c.agg_data['inaccessible']]
        for in_node in inaccessible_nodes:
            self.env_mesh.neighbour_graph.remove_node_and_update_neighbours(in_node)

    def model_performance(self):
        """

        Method to calculate the relevant vessel performance values for each cell in the environmental mesh and update
        the mesh accordingly.

        """
        for i, cellbox in enumerate(self.env_mesh.agg_cellboxes):
            performance_values = self.vessel.model_performance(cellbox)
            self.env_mesh.update_cellbox(i, performance_values)

    def to_json(self):
        """
            Method to return the modified mesh in json format.

            Returns:
                j_mesh (dict): a dictionary representation of the modified mesh.
        """
        j_mesh = self.env_mesh.to_json()
        return j_mesh

    def filter_nans(self):
        """
            Method to check for NaNs in the input cell boxes and zero them if present
        """
        for i, cellbox in enumerate(self.env_mesh.agg_cellboxes):
            if any(np.isnan(val) for val in cellbox.agg_data.values() if type(val) == float):
                filtered_data = {k: 0 if np.isnan(v) else v for k, v in cellbox.agg_data.items() if type(v) == float}
                self.env_mesh.update_cellbox(i, filtered_data)