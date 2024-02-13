*************************
Visual_ice Dataloader
*************************

Visual_ice is a dataloader for .tiff images generated from the visual_ice library, 
developed my Martin Rodgers at the British Antarctic Surveys AI Lab. The Visual_iced 
images are ice/water binary files, generated from a combination of MODIS and SAR 
satelite imagery. 

In the source data, 0's are representaive of open water, and 1's are representative of 
ice. In the dataloader, we map theses values to Sea ice concentration, in range of 0 to 100.
Values between 0 and 100 are achived by the aggregation of the 0's and 1's which each cell.  

.. automodule:: meshiphi.dataloaders.scalar.visual_ice
    :special-members: __init__
    :members: