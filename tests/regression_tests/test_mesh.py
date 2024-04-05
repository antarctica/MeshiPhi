"""
    Regression testing package to ensure consistent functionality in development
    of the PolarRoute python package.
"""

import json
import pytest
import time
import os

from meshiphi import __version__ as pr_version
from meshiphi import MeshBuilder

# Import tests, which are automatically run

from .mesh_test_functions import test_mesh_cellbox_attributes
from .mesh_test_functions import test_mesh_cellbox_count
from .mesh_test_functions import test_mesh_cellbox_ids
from .mesh_test_functions import test_mesh_cellbox_values
from .mesh_test_functions import test_mesh_neighbour_graph_count
from .mesh_test_functions import test_mesh_neighbour_graph_ids
from .mesh_test_functions import test_mesh_neighbour_graph_values


import logging
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


#File locations of all environmental meshes to be recalculated for regression testing.
TEST_ENV_MESHES = [
    './example_meshes/env_meshes/grf_normal.json',
    # './example_meshes/env_meshes/grf_downsample.json',
    # './example_meshes/env_meshes/grf_reprojection.json',
    # './example_meshes/env_meshes/grf_sparse.json'
]

TEST_ABSTRACT_MESHES = [
    './example_meshes/abstract_env_meshes/vgrad.json',
    # './example_meshes/abstract_env_meshes/hgrad.json',
    # './example_meshes/abstract_env_meshes/checkerboard_1.json',
    # './example_meshes/abstract_env_meshes/checkerboard_2.json',
    # './example_meshes/abstract_env_meshes/checkerboard_3.json',
    # './example_meshes/abstract_env_meshes/circle.json',
    # './example_meshes/abstract_env_meshes/circle_quadrant_split.json',
    # './example_meshes/abstract_env_meshes/circle_quadrant_nosplit.json'
]

def setup_module():
    LOGGER.info(f'PolarRoute version: {pr_version}')

@pytest.fixture(scope='session', autouse=False, params=TEST_ENV_MESHES + TEST_ABSTRACT_MESHES)
def mesh_pair(request):
    """
    Creates a pair of JSON objects, one newly generated, one as old reference
    Args:
        request (fixture):
            fixture object including list of meshes to regenerate

    Returns:
        list: old and new mesh jsons for comparison
    """

    
    LOGGER.info(f'Test File: {request.param}')
   

    with open(request.param, 'r') as fp:
        old_mesh = json.load(fp)
    
    mesh_config = old_mesh['config']['mesh_info']
    new_mesh = calculate_env_mesh(mesh_config)
    
    test_name = os.path.basename(request.param)

    return {"test": test_name,
            "old_mesh": old_mesh,
            "new_mesh": new_mesh}

def calculate_env_mesh(mesh_config):
    """
    Creates a new environmental mesh from the old mesh's config

    Args:
        mesh_config (json): Config to generate new mesh from

    Returns:
        json: Newly regenerated mesh
    """
    start = time.perf_counter()

    mesh_builder = MeshBuilder(mesh_config)
    new_mesh = mesh_builder.build_environmental_mesh()

    end = time.perf_counter()
    
    cellbox_count = len(new_mesh.agg_cellboxes)
    LOGGER.info(f'Mesh containing {cellbox_count} cellboxes built in {end - start} seconds')


    return new_mesh.to_json()


def test_record_output(mesh_pair, record_property):
    """
    Hacky solution to storing fixtures after they're generated. 
    Code that saves fixture is in conftest.py

    Args:
        mesh_pair (dict): 
            Fixture holding generated meshes
        record_property (fixture): 
            Pytest built-in fixture that stores user-defined dicts for later 
            processing
    """
    record_property('meshes', mesh_pair)