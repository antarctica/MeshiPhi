import unittest
from meshiphi.mesh_generation.metadata import Metadata
from meshiphi.dataloaders.factory import DataLoaderFactory
from meshiphi.mesh_generation.cellbox import CellBox

from meshiphi.mesh_generation.boundary import Boundary
from meshiphi.utils import longitude_domain


def create_cellbox(bounds, id=0, parent=None, params=None, splitting_conds=None):
    """
    Helper function that simplifies creation of test cases

    Args:
        bounds (Boundary): Boundary of cellbox
        id (int, optional): Cellbox ID to initialise. Defaults to 0.
        parent (CellBox, optional): Cellbox to link as a parent. Defaults to None.

    Returns:
        CellBox: Cellbox with completed attributes
    """
    dataloader = create_dataloader(bounds, params)
    metadata = create_metadata(bounds, dataloader, splitting_conds=splitting_conds)

    new_cellbox = CellBox(bounds, id)
    new_cellbox.data_source = [metadata]
    new_cellbox.parent = parent
    
    return new_cellbox

def create_dataloader(bounds, params=None):
    if params is None:
        params = {
            'dataloader_name': 'rectangle',
            'data_name': 'dummy_data',
            'width': bounds.get_width(),
            'height': bounds.get_height()/3,
            'centre': (bounds.getcx(), bounds.getcy())
        }
    dataloader = DataLoaderFactory().get_dataloader(params['dataloader_name'],
                                                    bounds,
                                                    params,
                                                    min_dp=10)
    return dataloader

def create_metadata(bounds, dataloader, splitting_conds = None):
    if splitting_conds is None:
        splitting_conds = {
            'threshold': 0.5,
            'upper_bound': 0.75,
            'lower_bound': 0.25
        }
    data_source = Metadata(dataloader,
                           splitting_conds=splitting_conds,
                           value_fill_type='parent',
                           data_subset=dataloader.trim_datapoints(bounds))
    return data_source

class TestCellBox (unittest.TestCase):

    def setUp(self):
        
        self.parent_cellbox = create_cellbox(Boundary([-10, 10], [-10, 10]), 
                                             id=0, 
                                             parent=None)
        self.child_cellbox1 = create_cellbox(Boundary([-10,  0], [-10,  0]), 
                                             id=1, 
                                             parent=self.parent_cellbox)
        self.child_cellbox2 = create_cellbox(Boundary([-10,  0], [  0, 10]), 
                                             id=2, 
                                             parent=self.parent_cellbox)
        self.child_cellbox3 = create_cellbox(Boundary([  0, 10], [-10,  0]), 
                                             id=3, 
                                             parent=self.parent_cellbox)
        self.child_cellbox4 = create_cellbox(Boundary([  0, 10], [  0, 10]), 
                                             id=4, 
                                             parent=self.parent_cellbox)
        
        self.dummy_cellbox = create_cellbox(Boundary([10, 20], [30, 40]))


    def test_set_minimum_datapoints(self):
        self.assertRaises(ValueError, self.dummy_cellbox.set_minimum_datapoints, -1)
        
        self.dummy_cellbox.set_minimum_datapoints(5)
        self.assertEqual(self.dummy_cellbox.minimum_datapoints, 5)

    def test_get_minimum_datapoints(self):
        self.assertEqual(self.arbitrary_cellbox.get_minimum_datapoints(), 10)

    def test_set_data_source(self):
        arbitrary_bounds = Boundary([-50, -40], [-30, -20])
        arbitrary_params = {
            'dataloader_name': 'gradient',
            'data_name': 'dummy_data',
            'vertcal': True
        }
        arbitrary_dataloader  = create_dataloader(arbitrary_bounds, arbitrary_params)
        arbitrary_data_source = create_metadata(arbitrary_bounds, arbitrary_dataloader)
        
        self.dummy_cellbox.set_data_source([arbitrary_data_source])
        self.assertEqual(self.dummy_cellbox.data_source, arbitrary_data_source)

    def test_get_data_source(self):
        arbitrary_bounds = Boundary([-40, -20], [-20, 0])
        arbitrary_params = {
            'dataloader_name': 'gradient',
            'data_name': 'dummy_data',
            'vertcal': False
        }
        arbitrary_dataloader  = create_dataloader(arbitrary_bounds, arbitrary_params)
        arbitrary_data_source = create_metadata(arbitrary_bounds, arbitrary_dataloader)

        self.dummy_cellbox.data_source = arbitrary_data_source
        self.assertEqual(self.dummy_cellbox.get_data_source(), arbitrary_data_source)

    def test_set_parent(self):
        arbitrary_cellbox = create_cellbox(Boundary([10, 30], [30, 50]))
        self.dummy_cellbox.set_parent(arbitrary_cellbox)
        self.assertEqual(self.dummy_cellbox.parent, arbitrary_cellbox)

    def test_get_parent(self):
        # Make sure to set bounds values different to test_set_parent() method
        # to ensure that the value being checked isn't leftover from a previous test
        arbitrary_cellbox = create_cellbox(Boundary([0, 20], [20, 40]))
        self.dummy_cellbox.parent = arbitrary_cellbox
        self.assertEqual(self.dummy_cellbox.get_parent(), arbitrary_cellbox)

    def test_set_split_depth(self):
        self.assertRaises(ValueError, self.dummy_cellbox.set_split_depth, -1)

        self.dummy_cellbox.set_split_depth(5)
        self.assertEqual(self.dummy_cellbox.split_depth, 5)

    def test_get_split_depth(self):
        # Make sure to set split_depth values different to test_set_split_depth() method
        # to ensure that the value being checked isn't leftover from a previous test
        self.dummy_cellbox.split_depth = 3
        self.assertEqual(self.dummy_cellbox.get_split_depth(), 3)

    def test_set_id(self):
        self.dummy_cellbox.set_id(123)
        self.assertEqual(self.dummy_cellbox.id, 123)
        
    def test_get_id(self):
        self.assertEqual(self.arbitrary_cellbox.get_id(), 1)

    def test_set_bounds(self):
        arbitrary_bounds = Boundary([30, 50], [50, 70])
        self.dummy_cellbox.set_bounds(arbitrary_bounds)
        self.assertEqual(self.dummy_cellbox.bounds, arbitrary_bounds)

    def test_get_bounds(self):
        # Make sure to set bounds values different to test_set_bounds() method
        # to ensure that the value being checked isn't leftover from a previous test
        arbitrary_bounds = Boundary([20, 40], [40, 60])
        self.dummy_cellbox.bounds = arbitrary_bounds
        self.assertEqual(self.dummy_cellbox.get_bounds(), arbitrary_bounds)

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




