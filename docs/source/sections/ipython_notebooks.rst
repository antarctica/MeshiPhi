###############################
Python & iPython Notebooks
###############################

Route planning may also be done using a python terminal. This is case, the CLI is not required but the steps required for route planning 
follow the same format - create a digital environment; simulated a vessel against it; optimise a route plan through the digital environment.
 

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Creating the digital environment.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A configuration file is needed to initialise the **`Mesh`** object which forms the digital environment. This configuration file
is of the same format used in the :ref:`create_mesh` CLI entry-point, and may either be loaded from a *json* file or constructed 
within the python terminal.

Loading configuration from *json* file:
::

    import json
    with open('config.json', 'r') as f:
        config = json.load(f)    


The digital environment **`Mesh`** object can then be initialised. This mesh object will be constructed using parameters in it
configuration file. This mesh object can be manipulated further, such as increasing its resolution through further 
splitting, adding additional data sources or altering is configuration parameters using functions listed in 
the :ref:`Methods - Mesh Construction` section of the documentation. The digital environment **`Mesh`** object can then be cast to 
a json object and saved to a file. 
::

    from cartographi.mesh import Mesh

    cg = Mesh(config)
    mesh = cg.to_json()
    with open('mesh.json') as f:
        json.dumps(mesh)
