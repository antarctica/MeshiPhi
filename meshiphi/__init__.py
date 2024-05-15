__version__ = "2.0.9"
__description__ = "MeshiPhi: Earth's digital twin mapped on a non-uniform mesh"
__license__ = "MIT"
__author__ = "Autonomous Marine Operations Planning (AMOP) Team, AI Lab, British Antarctic Survey"
__email__ = "amop@bas.ac.uk"
__copyright__ = "2021-, BAS AI Lab"

# Wrapped in try-except so that setup.py can import meshiphi without crashing due to dependency errors
try:
    from meshiphi.mesh_generation.mesh_builder import MeshBuilder as MeshBuilder
    from meshiphi.dataloaders.factory import DataLoaderFactory as DataLoaderFactory
    from meshiphi.mesh_generation.boundary import Boundary as Boundary

except ModuleNotFoundError as err:
    print(f'{err}\n Is meshiphi installed correctly?')
