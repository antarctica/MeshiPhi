
import unittest
from meshiphi.mesh_generation.direction import Direction
from meshiphi.mesh_generation.neighbour_graph import NeighbourGraph
from meshiphi.mesh_generation.metadata import Metadata
from meshiphi.dataloaders.factory import DataLoaderFactory
from meshiphi.mesh_generation.cellbox import CellBox

from meshiphi.mesh_generation.boundary import Boundary
class TestNeighbourGraph (unittest.TestCase):
    
    def setUp(self):
        pass

    def test_from_json(self):
        raise NotImplementedError
    
    def test_increment_ids(self):
        raise NotImplementedError
    
    def test_get_graph(self):
        raise NotImplementedError
    
    def test_update_neighbour(self):
        raise NotImplementedError
    
    def test_add_neighbour(self):
        raise NotImplementedError
    
    def test_remove_node_and_update_neighbours(self):
        raise NotImplementedError
    
    def test_get_neighbours(self):
        raise NotImplementedError
    
    def test_add_node(self):
        raise NotImplementedError
    
    def test_remove_node(self):
        raise NotImplementedError
    
    def test_update_neighbours(self):
        raise NotImplementedError
    
    def test_remove_node_from_neighbours(self):
        raise NotImplementedError
    
    def test_update_corner_neighbours(self):
        raise NotImplementedError
    
    def test_get_neighbour_case_bounds(self):
        raise NotImplementedError
    
    def test_get_neighbour_case(self):
        raise NotImplementedError
    
    def test_get_global_mesh_neighbour_case(self):
        raise NotImplementedError
    
    def test_remove_neighbour(self):
        raise NotImplementedError
    
    def test_initialise_neighbour_graph(self):
        raise NotImplementedError
    
    def test_initialise_map(self):
        raise NotImplementedError
    
    def test_set_global_mesh(self):
        raise NotImplementedError
    
    def test_is_global_mesh(self):
        raise NotImplementedError
    
    def test_get_neighbour_map(self):
        raise NotImplementedError



   # def setUp(self):
   #       boundary = Boundary([-85,-80], [-135,-130], ['1970-01-01','2021-12-31'])
   #       cellbox = CellBox (boundary , 0)
   #       params = {
   #    'file': '../../datastore/bathymetry/GEBCO/gebco_2022_n-40.0_s-90.0_w-140.0_e0.0.nc',
	# 	'downsample_factors': (5,5),
	# 	'data_name': 'elevation',
	# 	'aggregate_type': 'MAX',
   #     'value_fill_types': "parent"
   #       }
   #       split_conds = {
	# 'threshold': 620,
	# 'upper_bound': 0.9,
	# 'lower_bound': 0.1
	# }
        
   #       gebco = DataLoaderFactory().get_dataloader('GEBCO', boundary , params, min_dp = 5)
   #       cellbox.set_data_source ([Metadata (gebco , [split_conds] ,  params ['value_fill_types'])])
   #       self.cellboxes = cellbox.split(0)
   #       cell_width = 2.5
   #       grid_width = (boundary.get_long_max() - boundary.get_long_min()) / cell_width
   #       self.neighbour_graph = NeighbourGraph (self.cellboxes ,grid_width )
         

   # def test_initialize_NG(self):
   #    self.assertEqual ( 4 , len (self.neighbour_graph.get_graph()))
   #    self.assertEqual ( {1: [3], 2: [1], 3: [], 4: [], -1: [], -2: [], -3: [], -4: [2]} , self.neighbour_graph.get_graph()[0]) # NW cellbox
   #    self.assertEqual ( {1: [], 2: [], 3: [], 4: [], -1: [], -2: [0], -3: [2], -4: [3]} , self.neighbour_graph.get_graph()[1]) # NE cellbox
   #    self.assertEqual ( {1: [], 2: [3], 3: [1], 4: [0], -1: [], -2: [], -3: [], -4: []} , self.neighbour_graph.get_graph()[2]) # SW cellbox
   #    self.assertEqual ( {1: [], 2: [], 3: [], 4: [1], -1: [0], -2: [2], -3: [], -4: []} , self.neighbour_graph.get_graph()[3]) # SE cellbox

   
   # def test_remove_neighbour (self):
   #    self.neighbour_graph.remove_neighbour(0 ,  Direction.east , 1)
   #    self.assertEqual ( {1: [3], 2: [], 3: [], 4: [], -1: [], -2: [], -3: [], -4: [2]} , self.neighbour_graph.get_graph()[0]) # NW cellbox
   #    self.neighbour_graph.update_neighbour(0 , Direction.east , [1]) # undo the remove

   # def test_update_neighbour (self):
   #    self.neighbour_graph.update_neighbour(0 ,  Direction.south_east , [3])
   #    self.assertEqual ( {1: [3], 2: [1], 3: [3], 4: [], -1: [], -2: [], -3: [], -4: [2]} , self.neighbour_graph.get_graph()[0]) # NW cellbox
   #    self.neighbour_graph.remove_neighbour(0 ,  Direction.south_east , 3)# undo the update
  
   # def test_get_neighbour_case(self):
   #    case = self.neighbour_graph.get_neighbour_case(self.cellboxes[0] , self.cellboxes[1])
   #    self.assertEqual ( 2, case)
   #    case = self.neighbour_graph.get_neighbour_case(self.cellboxes[0] , self.cellboxes[2])
   #    self.assertEqual ( 4, case)
   #    case = self.neighbour_graph.get_neighbour_case(self.cellboxes[0] , self.cellboxes[3])
   #    self.assertEqual (3 , case)
   #    case = self.neighbour_graph.get_neighbour_case(self.cellboxes[2] , self.cellboxes[0])
   #    self.assertEqual ( -4, case)
   #    case = self.neighbour_graph.get_neighbour_case(self.cellboxes[1] , self.cellboxes[2])
   #    self.assertEqual ( -1, case)
   #    case = self.neighbour_graph.get_neighbour_case(self.cellboxes[2] , self.cellboxes[1])
   #    self.assertEqual ( 1, case)
   #    case = self.neighbour_graph.get_neighbour_case(self.cellboxes[3] , self.cellboxes[0])
   #    self.assertEqual ( -3, case)
   #    case = self.neighbour_graph.get_neighbour_case(self.cellboxes[3] , self.cellboxes[2])
   #    self.assertEqual ( -2, case)
   #    case = self.neighbour_graph.get_neighbour_case(self.cellboxes[3] , self.cellboxes[1])
   #    self.assertEqual ( -4, case)
   #    case = self.neighbour_graph.get_neighbour_case(self.cellboxes[1] , self.cellboxes[3])
   #    self.assertEqual ( 4, case)

   # def test_update_neighbours (self):
   #    self.neighbour_graph.update_neighbours(0, [2,1], Direction.north_east, self.cellboxes)
   #    self.assertEqual (  {1: [], 2: [], 3: [], 4: [1], -1: [], -2: [2,2], -3: [], -4: [1]} , self.neighbour_graph.get_graph()[3]) # SE cellbox
   #    self.neighbour_graph.update_neighbour(3, Direction.south, [1]) # undo the first update 
   #    self.neighbour_graph.update_neighbour(3, Direction.west, [2]) # undo the first update 
   #    self.neighbour_graph.update_neighbour(3, Direction.north, []) # undo the first update 
  
   # def test_update_corner_neighbours(self):
   #    self.neighbour_graph.update_corner_neighbours (3 , -1, -1, -1, -1 )
   #    self.assertEqual ( {1: [-1], 2: [1], 3: [], 4: [], -1: [], -2: [], -3: [], -4: [2]} , self.neighbour_graph.get_graph()[0]) # SE cellbox
