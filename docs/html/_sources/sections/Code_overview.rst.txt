**********
Background
**********


Code Structure
##############
The outline of this manual is to provide the user with all the tools that they need to run the software for a set of examples. We also hope that the background information supplied for each section allows the user to understand the methods used throughout this toolkit.

The separate stages of the codebase can be broken down into:

1. :ref:`Dataloaders <dataloaders-overview>` - Reading in different datasets of differing types. Throughout this section we will outline the form that the input datasets should take and useful tips for pre-processing your data.
2. :ref:`Mesh Construction <mesh_construction_overview>` - Generating a Digital Twin of the environmental conditions. In this section we outline the different Python classes that are used to construct a discretised representation across the user defined datasets, giving a coding background to the dynamic splitting of the mesh to finer resolution in regions of datasets that are spatially varying.

Each stage of this pipeline makes use of a configuration file, found in the :ref:`Configuration Overview` section of the documentation
and produces an output file, the form of which can be found in the :ref:`outputs` section of this document.

In addition to the main section of the codebase we have also developed a series of plotting classes that allows the user to generate interactive maps and static figures for the Mesh Features. These can be found in the `Plotting` section later in the manual.