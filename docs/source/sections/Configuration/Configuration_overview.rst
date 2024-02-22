######################################
Configuration Overview
######################################

In this section we will outline the standard structure for a configuration file used in 
all portions of the MeshiPhi software package.

Each stage of the route-planning process is configured by a separate configuration file. 
The configuration files are written in JSON, and are passed to each stage of the 
route-planning process as command-line arguments or through a Python script.

Example configuration files are provided in the `config` directory.

Descriptions of the configuration options for the Mesh Construction can be found in 
the :ref:`Configuration - Mesh Construction` section of the documentation.


.. toctree::
   :maxdepth: 1

   ./Mesh_construction_config


Config Validation
^^^^^^^^^^^^^^^^^

At each major stage of the code (mesh construction, vessel performance modelling, 
and route planning), the configs supplied are validated using a template JSON Schema.
These schema check that the correct keywords and datatypes are provided in the config 
JSONs, as well as the waypoints CSV file. They also perform rudimentary checks on the
values to ensure that they make sense (e.g. start_time is before end_time).

.. automodule:: meshiphi.config_validation.config_validator
   :members: