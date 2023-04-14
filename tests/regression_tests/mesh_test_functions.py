import numpy as np


def test_mesh_cellbox_count(mesh_pair):
    compare_cellbox_count(mesh_pair[0], mesh_pair[1])

def test_mesh_cellbox_ids(mesh_pair):
    compare_cellbox_ids(mesh_pair[0], mesh_pair[1])

def test_mesh_cellbox_values(mesh_pair):
    compare_cellbox_values(mesh_pair[0], mesh_pair[1])

def test_mesh_cellbox_attributes(mesh_pair):
    compare_cellbox_attributes(mesh_pair[0], mesh_pair[1])

def test_mesh_neighbour_graph_count(mesh_pair):
    compare_neighbour_graph_count(mesh_pair[0], mesh_pair[1])

def test_mesh_neighbour_graph_ids(mesh_pair):
    compare_neighbour_graph_ids(mesh_pair[0], mesh_pair[1])

def test_mesh_neighbour_graph_values(mesh_pair):
    compare_neighbour_graph_values(mesh_pair[0], mesh_pair[1])



def compare_cellbox_count(mesh_a, mesh_b):
    """
        Test if two provided meshes contain the same number of cellboxes

        Args:
            mesh_a (json)
            mesh_b (json)

        Throws:
            Fails if the number of cellboxes in regression_mesh and new_mesh are
            not equal
    """
    regression_mesh = mesh_a['cellboxes']
    new_mesh = mesh_b['cellboxes']

    cellbox_count_a = len(regression_mesh)
    cellbox_count_b = len(new_mesh)

    assert(cellbox_count_a == cellbox_count_b), \
        f"Incorrect number of cellboxes in new mesh. Expected :{cellbox_count_a}, got: {cellbox_count_b}"

def compare_cellbox_ids(mesh_a, mesh_b):
    """
        Test if two provided meshes contain cellboxes with the same IDs

       Args:
            mesh_a (json)
            mesh_b (json)

        Throws:
            Fails if any cellbox exists in regression_mesh that or not in new_mesh,
            or any cellbox exists in new_mesh that is not in regression_mesh
    """
    regression_mesh = mesh_a['cellboxes']
    new_mesh = mesh_b['cellboxes']

    indxed_a = dict()
    for cellbox in regression_mesh:
        indxed_a[cellbox['id']] = cellbox

    indxed_b = dict()
    for cellbox in new_mesh:
        indxed_b[cellbox['id']] = cellbox

    regression_mesh_ids = set(indxed_a.keys())
    new_mesh_ids = set(indxed_b.keys())

    missing_a_ids = list(new_mesh_ids - regression_mesh_ids)
    missing_b_ids = list(regression_mesh_ids - new_mesh_ids)

    assert(indxed_a.keys()  == indxed_b.keys()), \
        f"Mismatch in cellbox IDs. ID's {missing_a_ids} have appeared in the new mesh. ID's {missing_b_ids} are missing from the new mesh"

def compare_cellbox_values(mesh_a, mesh_b):
    """
        Tests if the values in of all attributes in each cellbox and the
        same in both provided meshes.

        Args:
            mesh_a (json)
            mesh_b (json)

        Throws:
            Fails if any values of any attributes differ between regression_mesh
            and new_mesh
    """
    regression_mesh = mesh_a['cellboxes']
    new_mesh = mesh_b['cellboxes']

    indxed_a = dict()
    for cellbox in regression_mesh:
        indxed_a[cellbox['id']] = cellbox

    indxed_b = dict()
    for cellbox in new_mesh:
        indxed_b[cellbox['id']] = cellbox

    mismatch_cellboxes = dict()
    for cellbox_a in indxed_a.values():
        # Prevent crashing if cellbox not in new mesh
        # This error will be detected by 'test_cellbox_ids'
        if cellbox_a['id'] in indxed_b.keys():
            cellbox_b = indxed_b[cellbox_a['id']]

            mismatch_values = []
            mismatch_keys = []
            for key in cellbox_a.keys():
                # To prevent crashing if cellboxes have different attributes
                # This error will be detected by the 'test_cellbox_attributes' test
                if key in cellbox_b.keys():
                    # Round to 5 dec. pl if value is a float, high precision can be issue between OS's
                    if (type(cellbox_a[key]) is float) and (type(cellbox_b[key]) is float):
                        value_b = np.round(float(cellbox_b[key]), decimals=5)
                        value_a = np.round(float(cellbox_a[key]), decimals=5)
                    # We also want to round float values for comparison when contained inside a list
                    elif (type(cellbox_a[key]) is list) and (type(cellbox_b[key]) is list):
                        if any(isinstance(val, float) for val in cellbox_a[key]) and any(isinstance(val, float) for val in cellbox_b[key]):
                            value_b = [np.round(float(v), decimals=5) for v in cellbox_b[key]]
                            value_a = [np.round(float(v), decimals=5) for v in cellbox_a[key]]
                        else:
                            value_b = cellbox_b[key]
                            value_a = cellbox_a[key]
                    # Otherwise just extract values
                    else:
                        value_b = cellbox_b[key]  
                        value_a = cellbox_a[key]

                    # Compare values
                    
                    if str(value_a) != str(value_b):
                        mismatch_keys.append(key)
                        mismatch_values.append([value_a,value_b])
                        mismatch_cellboxes[cellbox_a['id']] = [mismatch_keys, mismatch_values]

    assert(len(mismatch_cellboxes) == 0) , \
        f"Values in <{len(mismatch_cellboxes.keys())}> cellboxes in the new mesh have changed. The changed cellboxes are: {mismatch_cellboxes}"

def compare_cellbox_attributes(mesh_a, mesh_b):
    """
        Tests if the attributes of cellboxes in regression_mesh and the same as
        attributes of cellboxes in new_mesh

        Note:
            This assumes that every cellbox in mesh has the same amount
            of attributes, so only compares the attributes of the first
            two cellboxes in the mesh

        Args:
            mesh_a (json)
            mesh_b (json)

        Throws:
            Fails if the cellboxes in the provided meshes contain different
            attributes
    """
    regression_mesh = mesh_a['cellboxes']
    new_mesh = mesh_b['cellboxes']

    regression_regression_meshttributes = set(regression_mesh[0].keys())
    new_mesh_attributes = set(new_mesh[0].keys())

    missing_a_attributes = list(new_mesh_attributes - regression_regression_meshttributes)
    missing_b_attributes = list(regression_regression_meshttributes - new_mesh_attributes)

    assert(regression_regression_meshttributes == new_mesh_attributes), \
        f"Mismatch in cellbox attributes. Attributes {missing_a_attributes} have appeared in the new mesh. Attributes {missing_b_attributes} are missing in the new mesh"

def compare_neighbour_graph_count(mesh_a, mesh_b):
    """
        Tests that the neighbour_graph in the regression mesh and the newly calculated mesh have the 
        same number of nodes.

         Args:
            mesh_a (json)
            mesh_b (json)

    """
    regression_graph = mesh_a['neighbour_graph']
    new_graph = mesh_b['neighbour_graph']

    regression_graph_count = len(regression_graph.keys())
    new_graph_count = len(new_graph.keys())

    assert(regression_graph_count == new_graph_count), \
        f"Incorrect number of nodes in neighbour graph. Expected: <{regression_graph_count}> nodes, got: <{new_graph_count}> nodes."

def compare_neighbour_graph_ids(mesh_a, mesh_b):
    """
        Tests that the neighbour_graph in the regression mesh and the newly calculated mesh contain
        all the same node IDs.

        Args:
            mesh_a (json)
            mesh_b (json)
    """
    regression_graph = mesh_a['neighbour_graph']
    new_graph = mesh_b['neighbour_graph']

    regression_graph_ids = set(regression_graph.keys())
    new_graph_ids = set(new_graph.keys())

    missing_a_keys = list(new_graph_ids - regression_graph_ids)
    missing_b_keys = list(regression_graph_ids - new_graph_ids)

    assert(regression_graph_ids == new_graph_ids) , \
        f"Mismatch in neighbour graph nodes. <{len(missing_a_keys)}> nodes have appeared in the new neighbour graph. <{len(missing_b_keys)}> nodes are missing from the new neighbour graph."

def compare_neighbour_graph_values(mesh_a, mesh_b):
    """
        Tests that each node in the neighbour_graph of the regression mesh and the newly calculated
        mesh have the same neighbours.

        Args:
            mesh_a (json)
            mesh_b (json)

    """
    regression_graph = mesh_a['neighbour_graph']
    new_graph = mesh_b['neighbour_graph']

    mismatch_neighbours = dict()

    for node in regression_graph.keys():
        # Prevent crashing if node not found. 
        # This will be detected by 'test_neighbour_graph_ids'.
        if node in new_graph.keys():
            neighbours_a = regression_graph[node]
            neighbours_b = new_graph[node]

            # Sort the lists of neighbours as ordering is not important
            sorted_neighbours_a = {k:sorted(neighbours_a[k]) for k in neighbours_a.keys()}
            sorted_neighbours_b = {k: sorted(neighbours_b[k]) for k in neighbours_b.keys()}

            if not sorted_neighbours_b == sorted_neighbours_a:
                mismatch_neighbours[node] = sorted_neighbours_b

    assert(len(mismatch_neighbours) == 0), \
        f"Mismatch in neighbour graph neighbours. <{len(mismatch_neighbours.keys())}> nodes have changed in the new mesh."
