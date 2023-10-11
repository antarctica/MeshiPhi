__version__ = "1.1.5"

__description__ = "meshiphi: Earth's digital twin mapped on a non-uniform mesh"
__license__ = "MIT"
__author__ = "Samuel Hall, George Coombs, Harrison Abbot, Ayat Fekry, Jonathan Smith, Maria Fox, James Byrne, Michael Thorne"
__email__ = "polarroute@bas.ac.uk"
__copyright__ = "2022-2023, BAS AI Lab"

# Wrapped in try-except so that setup.py can import meshiphi without crashing due to dependency errors
try:
    from meshiphi.mesh_generation.mesh_builder import MeshBuilder as MeshBuilder
    from meshiphi.dataloaders.factory import DataLoaderFactory as DataLoaderFactory
    from meshiphi.mesh_generation.boundary import Boundary as Boundary

except ModuleNotFoundError as err:
    print(f'{err}\n Is meshiphi installed correctly?')
