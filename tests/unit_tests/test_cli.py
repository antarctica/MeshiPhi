from meshiphi.cli import get_args
from meshiphi.cli import rebuild_mesh_cli
from meshiphi.cli import create_mesh_cli
from meshiphi.cli import export_mesh_cli
from meshiphi.cli import merge_mesh_cli
from meshiphi.cli import meshiphi_test_cli


import tempfile
import sys
import shutil
import unittest
import filecmp
import difflib
import json
from unittest.mock import patch


# Contents of JSON files to run through each CLI command with
# Config to create BASIC_OUTPUT
BASIC_CONFIG = {"region":{"lat_min":-10,"lat_max":10,"long_min":-10,"long_max":10,"start_time":"2000-01-01","end_time":"2000-12-31","cell_width":10,"cell_height":10},"data_sources":[],"splitting":{"split_depth":1,"minimum_datapoints":5}}
# Mesh to rebuild to create BASIC_OUTPUT
BASIC_MESH   = {"config":{"mesh_info":{"region":{"lat_min":-10,"lat_max":10,"long_min":-10,"long_max":10,"start_time":"2000-01-01","end_time":"2000-12-31","cell_width":10,"cell_height":10},"data_sources":[],"splitting":{"split_depth":1,"minimum_datapoints":5}}},"cellboxes":[{"geometry":"POLYGON ((-10 -10, -10 0, 0 0, 0 -10, -10 -10))","cx":-5,"cy":-5,"dcx":5,"dcy":5,"id":"0"},{"geometry":"POLYGON ((0 -10, 0 0, 10 0, 10 -10, 0 -10))","cx":5,"cy":-5,"dcx":5,"dcy":5,"id":"1"},{"geometry":"POLYGON ((-10 0, -10 10, 0 10, 0 0, -10 0))","cx":-5,"cy":5,"dcx":5,"dcy":5,"id":"2"},{"geometry":"POLYGON ((0 0, 0 10, 10 10, 10 0, 0 0))","cx":5,"cy":5,"dcx":5,"dcy":5,"id":"3"}],"neighbour_graph":{"0":{"1":[3],"2":[1],"3":[],"4":[],"-1":[],"-2":[],"-3":[],"-4":[2]},"1":{"1":[],"2":[],"3":[],"4":[],"-1":[],"-2":[0],"-3":[2],"-4":[3]},"2":{"1":[],"2":[3],"3":[1],"4":[0],"-1":[],"-2":[],"-3":[],"-4":[]},"3":{"1":[],"2":[],"3":[],"4":[1],"-1":[0],"-2":[2],"-3":[],"-4":[]}}}
BASIC_OUTPUT = {"config":{"mesh_info":{"region":{"lat_min":-10,"lat_max":10,"long_min":-10,"long_max":10,"start_time":"2000-01-01","end_time":"2000-12-31","cell_width":10,"cell_height":10},"data_sources":[],"splitting":{"split_depth":1,"minimum_datapoints":5}}},"cellboxes":[{"geometry":"POLYGON ((-10 -10, -10 0, 0 0, 0 -10, -10 -10))","cx":-5,"cy":-5,"dcx":5,"dcy":5,"id":"0"},{"geometry":"POLYGON ((0 -10, 0 0, 10 0, 10 -10, 0 -10))","cx":5,"cy":-5,"dcx":5,"dcy":5,"id":"1"},{"geometry":"POLYGON ((-10 0, -10 10, 0 10, 0 0, -10 0))","cx":-5,"cy":5,"dcx":5,"dcy":5,"id":"2"},{"geometry":"POLYGON ((0 0, 0 10, 10 10, 10 0, 0 0))","cx":5,"cy":5,"dcx":5,"dcy":5,"id":"3"}],"neighbour_graph":{"0":{"1":[3],"2":[1],"3":[],"4":[],"-1":[],"-2":[],"-3":[],"-4":[2]},"1":{"1":[],"2":[],"3":[],"4":[],"-1":[],"-2":[0],"-3":[2],"-4":[3]},"2":{"1":[],"2":[3],"3":[1],"4":[0],"-1":[],"-2":[],"-3":[],"-4":[]},"3":{"1":[],"2":[],"3":[],"4":[1],"-1":[0],"-2":[2],"-3":[],"-4":[]}}}
# Meshes to merge to produce BASIC_MERGED_MESH
BASIC_HALF_MESH_1 = {"config":{"mesh_info":{"region":{"lat_min":-10,"lat_max":0,"long_min":-10,"long_max":10,"start_time":"2000-01-01","end_time":"2000-12-31","cell_width":10,"cell_height":10},"data_sources":[],"splitting":{"split_depth":1,"minimum_datapoints":5}}},"cellboxes":[{"geometry":"POLYGON ((-10 -10, -10 0, 0 0, 0 -10, -10 -10))","cx":-5,"cy":-5,"dcx":5,"dcy":5,"id":"0"},{"geometry":"POLYGON ((0 -10, 0 0, 10 0, 10 -10, 0 -10))","cx":5,"cy":-5,"dcx":5,"dcy":5,"id":"1"}],"neighbour_graph":{"0":{"1":[],"2":[1],"3":[],"4":[],"-1":[],"-2":[],"-3":[],"-4":[]},"1":{"1":[],"2":[],"3":[],"4":[],"-1":[],"-2":[0],"-3":[],"-4":[]}}}
BASIC_HALF_MESH_2 = {"config":{"mesh_info":{"region":{"lat_min":0,"lat_max":10,"long_min":-10,"long_max":10,"start_time":"2000-01-01","end_time":"2000-12-31","cell_width":10,"cell_height":10},"data_sources":[],"splitting":{"split_depth":1,"minimum_datapoints":5}}},"cellboxes":[{"geometry":"POLYGON ((-10 0, -10 10, 0 10, 0 0, -10 0))","cx":-5,"cy":5,"dcx":5,"dcy":5,"id":"0"},{"geometry":"POLYGON ((0 0, 0 10, 10 10, 10 0, 0 0))","cx":5,"cy":5,"dcx":5,"dcy":5,"id":"1"}],"neighbour_graph":{"0":{"1":[],"2":[1],"3":[],"4":[],"-1":[],"-2":[],"-3":[],"-4":[]},"1":{"1":[],"2":[],"3":[],"4":[],"-1":[],"-2":[0],"-3":[],"-4":[]}}}
BASIC_MERGED_MESH = {"config":{"mesh_info":{"region":{"lat_min":-10,"lat_max":0,"long_min":-10,"long_max":10,"start_time":"2000-01-01","end_time":"2000-12-31","cell_width":10,"cell_height":10},"data_sources":[],"splitting":{"split_depth":1,"minimum_datapoints":5},"merged":[{"region":{"lat_min":0,"lat_max":10,"long_min":-10,"long_max":10,"start_time":"2000-01-01","end_time":"2000-12-31","cell_width":10,"cell_height":10},"data_sources":[],"splitting":{"split_depth":1,"minimum_datapoints":5}}]}},"cellboxes":[{"geometry":"POLYGON ((-10 -10, -10 0, 0 0, 0 -10, -10 -10))","cx":-5,"cy":-5,"dcx":5,"dcy":5,"id":"0"},{"geometry":"POLYGON ((0 -10, 0 0, 10 0, 10 -10, 0 -10))","cx":5,"cy":-5,"dcx":5,"dcy":5,"id":"1"},{"geometry":"POLYGON ((-10 0, -10 10, 0 10, 0 0, -10 0))","cx":-5,"cy":5,"dcx":5,"dcy":5,"id":"2"},{"geometry":"POLYGON ((0 0, 0 10, 10 10, 10 0, 0 0))","cx":5,"cy":5,"dcx":5,"dcy":5,"id":"3"}],"neighbour_graph":{"0":{"1":[3],"2":[1],"3":[],"4":[],"-1":[],"-2":[],"-3":[],"-4":[2]},"1":{"1":[],"2":[],"3":[],"4":[],"-1":[],"-2":[0],"-3":[2],"-4":[3]},"2":{"1":[],"2":[3],"3":[1],"4":[0],"-1":[],"-2":[],"-3":[],"-4":[]},"3":{"1":[],"2":[],"3":[],"4":[1],"-1":[0],"-2":[2],"-3":[],"-4":[]}}}

def json_dict_to_file(json_dict, filename):
    with open(filename, 'w') as fp:
        json.dump(json_dict, fp, indent=4)

def file_to_json(filename):
    with open(filename, 'r') as fp:
        json_dict = json.load(fp)
    return json_dict

class TestCLI (unittest.TestCase):

    def setUp(self):
        self.output_base_directory = tempfile.mkdtemp()
        self.tmp_config_file = tempfile.NamedTemporaryFile()
        self.tmp_mesh_file   = tempfile.NamedTemporaryFile()
        self.tmp_mesh_file_1 = tempfile.NamedTemporaryFile()
        self.tmp_mesh_file_2 = tempfile.NamedTemporaryFile()
        self.tmp_merge_file  = tempfile.NamedTemporaryFile()
        self.tmp_output_file = tempfile.NamedTemporaryFile()

    def tearDown(self):
        self.tmp_config_file.close()
        self.tmp_mesh_file.close()
        self.tmp_mesh_file_1.close()
        self.tmp_mesh_file_2.close()
        self.tmp_merge_file.close()
        self.tmp_output_file.close()
    
    def test_get_args_cli(self):
        raise NotImplementedError
    
    def test_rebuild_mesh_cli(self):

        test_args = ['rebuild_mesh', 
                     self.tmp_mesh_file.name,
                     '-o', self.tmp_output_file.name]
        
        # Create files with relevant data for test
        json_dict_to_file(BASIC_MESH, self.tmp_mesh_file.name)

        with patch.object(sys, 'argv', test_args):
            rebuild_mesh_cli()
            
            orig_mesh  = file_to_json(self.tmp_mesh_file.name)
            rebuilt_mesh = file_to_json(self.tmp_output_file.name)

            self.assertEqual(orig_mesh, rebuilt_mesh)

    def test_create_mesh_cli(self):
        test_args = ['create_mesh', 
                     self.tmp_config_file.name,
                     '-o', self.tmp_output_file.name]
        
        # Create files with relevant data for test
        json_dict_to_file(BASIC_CONFIG, self.tmp_config_file.name)
        json_dict_to_file(BASIC_MESH, self.tmp_mesh_file.name)

        with patch.object(sys, 'argv', test_args):
            create_mesh_cli()
            
            orig_mesh  = file_to_json(self.tmp_mesh_file.name)
            created_mesh = file_to_json(self.tmp_output_file.name)

            self.assertEqual(orig_mesh, created_mesh)
    
    def test_export_mesh_cli(self):
        raise NotImplementedError
    
    def test_merge_mesh_cli(self):
        test_args = ['merge_mesh', 
                     self.tmp_mesh_file_1.name,
                     self.tmp_mesh_file_2.name,
                     '-o', self.tmp_output_file.name]
        
        # Create files with relevant data for test
        json_dict_to_file(BASIC_HALF_MESH_1, self.tmp_mesh_file_1.name)
        json_dict_to_file(BASIC_HALF_MESH_2, self.tmp_mesh_file_2.name)
        json_dict_to_file(BASIC_MERGED_MESH, self.tmp_mesh_file.name)
        
        with patch.object(sys, 'argv', test_args):
            merge_mesh_cli()
            
            orig_mesh  = file_to_json(self.tmp_mesh_file.name)
            created_mesh = file_to_json(self.tmp_output_file.name)

            self.assertEqual(orig_mesh, created_mesh)
        
    def test_meshiphi_test_cli(self):
        raise NotImplementedError