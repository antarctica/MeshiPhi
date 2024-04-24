import pytest
import json
import os


def pytest_runtest_teardown(item, nextitem):
    """
    Saves fixtures in .outputs folder to avoid regenerating them for 
    diagnostics.

    Args:
        item (fixture): Pytest fixture that has just been used
        nextitem (fixture): Pytest fixture that will be used next
    """
    # Extract user defined properties (from test_record_output())
    results = dict(item.user_properties)
    if not results:
        return
    
    save_filename = f".outputs/{results['meshes']['test']}"
    # Only care about the meshes used as a fixture
    meshes = {key: val for key, val in results['meshes'].items() if key != 'test'}

    # Create outputs folder if it doesn't exist yet
    os.makedirs(os.path.dirname(save_filename), exist_ok=True)
    # Output as a json
    with open(save_filename,'w') as fp:
        json.dump(meshes, fp, indent=4)