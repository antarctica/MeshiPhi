import unittest
from meshiphi.mesh_generation.metadata import Metadata
from meshiphi.dataloaders.factory import DataLoaderFactory
from meshiphi.mesh_generation.cellbox import CellBox

from meshiphi.mesh_generation.boundary import Boundary
from meshiphi.utils import longitude_domain
class TestCellBox (unittest.TestCase):

    def setUp(self):

        def create_cellbox(bounds, id=0):
            params = {
                'dataloader_name': 'circle',
                'data_name': 'dummy_data',
                'radius': bounds.get_width()/2
            }

            splitting_conds = {
                'threshold': 0.5,
                'upper_bound': 0.75,
                'lower_bound': 0.25
            }

            dataloader = DataLoaderFactory().get_dataloader('circle', bounds, params, min_dp=10)
            datasource = Metadata(dataloader, 
                                  splitting_conditions=splitting_conds, 
                                  value_fill_type='parent', 
                                  data_subset=dataloader.trim_datapoints(bounds))

            new_cellbox = CellBox(bounds, id)

            new_cellbox.data_source = [datasource]
            
            # Create a parent boundary defined as being twice as big in each axis. Parent extends cellbox boundary to the NW
            parent_bounds = Boundary([bounds.get_lat_min(),  bounds.get_lat_max()  + bounds.get_height()],
                                     [longitude_domain(bounds.get_long_min()), 
                                      longitude_domain(bounds.get_long_max() + bounds.get_width())])
            # Make ID a 2 digit number to avoid any conflicts
            new_cellbox.parent = CellBox(parent_bounds, id + 10)
            
            return new_cellbox


        # Set a 'dummy_cellbox' for testing all the setters
        self.dummy_cellbox        = create_cellbox(Boundary([ 10,  20], [ 30,  40]), id=0)
        # Don't want to reuse dummy cellbox for testing getters since the values may be borked from the setter tests
        self.arbitrary_cellbox    = create_cellbox(Boundary([ 10,  20], [ 30,  40]), id=1)

    def test_set_minimum_datapoints(self):
        self.assertRaises(ValueError, self.dummy_cellbox.set_minimum_datapoints, -1)
        
        self.dummy_cellbox.set_minimum_datapoints(5)
        self.assertEqual(self.dummy_cellbox.minimum_datapoints, 5)

    def test_get_minimum_datapoints(self):
        self.assertEqual(self.arbitrary_cellbox.get_minimum_datapoints(), 10)

    def test_set_data_source(self):
        raise NotImplementedError

    def test_get_data_source(self):
        raise NotImplementedError
    
    def test_set_parent(self):
        raise NotImplementedError

    def test_get_parent(self):
        raise NotImplementedError

    def test_set_split_depth(self):
        self.assertRaises(ValueError, self.dummy_cellbox.set_split_depth, -1)

        self.dummy_cellbox.set_split_depth(5)
        self.assertEqual(self.dummy_cellbox.split_depth, 5)

    def test_get_split_depth(self):
        raise NotImplementedError

    def test_set_id(self):
        self.dummy_cellbox.set_id(123)
        self.assertEqual(self.dummy_cellbox.id, 123)
        
    def test_get_id(self):
        self.assertEqual(self.arbitrary_cellbox.get_id(), 1)

    def test_get_bounds(self):
        raise NotImplementedError

    def test_should_split(self):
        raise NotImplementedError

    def test_should_split_breadth_first(self):
        raise NotImplementedError

    def test_split(self):
        raise NotImplementedError

    def test_create_splitted_cell_boxes(self):
        raise NotImplementedError

    def test_aggregate(self):
        raise NotImplementedError

    def test_check_vector_data(self):
        raise NotImplementedError

    def test_deallocate_cellbox(self):
        raise NotImplementedError


   # def setUp(self):
   #       boundary = Boundary([-85,-84.9], [-135,-134.9], ['1970-01-01','2021-12-31'])
   #       self.cellbox = CellBox (boundary , 1)
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
         
   #       gebco = DataLoaderFactory().get_dataloader('GEBCO', boundary, params, min_dp = 5)
   #       self.cellbox.set_data_source ([Metadata (gebco , [split_conds] , params ['value_fill_types'])])

   # def test_minimum_data_points (self):
   #    self.assertRaises(ValueError, self.cellbox.set_minimum_datapoints , -1 )
   
   # def test_split_depth (self):
   #    self.assertRaises(ValueError, self.cellbox.set_split_depth ,  -1 )

   # def test_should_split (self):
   #    self.assertTrue(self.cellbox.should_split(1))

   # def test_split (self):
   #     splitted_boxes = self.cellbox.split (1)
   #     # test the splitted cellboxes have valid Ids
   #     self.assertEqual ('1' , splitted_boxes [0].get_id())
   #     self.assertEqual ('2' , splitted_boxes [1].get_id())
   #     self.assertEqual ('3', splitted_boxes [2].get_id())
   #     self.assertEqual ('4' , splitted_boxes [3].get_id())

   #    # test the bounds of the splitted cellboxes
   #     self.assertEqual ( self.cellbox.bounds.get_long_min() , splitted_boxes [0].bounds.get_long_min ())
   #     self.assertGreater ( self.cellbox.bounds.get_long_max() , splitted_boxes [0].bounds.get_long_max ())
   #     self.assertLess ( self.cellbox.bounds.get_lat_min() , splitted_boxes [0].bounds.get_lat_min ())
   #     self.assertEqual ( self.cellbox.bounds.get_lat_max() , splitted_boxes [0].bounds.get_lat_max ())

   #     self.assertLess ( self.cellbox.bounds.get_long_min() , splitted_boxes [1].bounds.get_long_min ())
   #     self.assertEqual( self.cellbox.bounds.get_long_max() , splitted_boxes [1].bounds.get_long_max ())
   #     self.assertLess ( self.cellbox.bounds.get_lat_min() , splitted_boxes [1].bounds.get_lat_min ())
   #     self.assertEqual ( self.cellbox.bounds.get_lat_max() , splitted_boxes [1].bounds.get_lat_max ())

   #     self.assertEqual ( self.cellbox.bounds.get_long_min() , splitted_boxes [2].bounds.get_long_min ())
   #     self.assertGreater( self.cellbox.bounds.get_long_max() , splitted_boxes [2].bounds.get_long_max ())
   #     self.assertEqual ( self.cellbox.bounds.get_lat_min() , splitted_boxes [2].bounds.get_lat_min ())
   #     self.assertGreater ( self.cellbox.bounds.get_lat_max() , splitted_boxes [2].bounds.get_lat_max ())

   #     self.assertLess ( self.cellbox.bounds.get_long_min() , splitted_boxes [3].bounds.get_long_min ())
   #     self.assertEqual( self.cellbox.bounds.get_long_max() , splitted_boxes [3].bounds.get_long_max ())
   #     self.assertEqual ( self.cellbox.bounds.get_lat_min() , splitted_boxes [3].bounds.get_lat_min ())
   #     self.assertGreater ( self.cellbox.bounds.get_lat_max() , splitted_boxes [3].bounds.get_lat_max ())

       
   # def test_aggregate (self):
   #    self.assertEqual ({'elevation': 627.0}, self.cellbox.aggregate().get_agg_data())




