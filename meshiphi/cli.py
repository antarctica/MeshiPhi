import argparse
import json
import inspect
import logging

from meshiphi import __version__ as version
from meshiphi.utils import setup_logging, timed_call, convert_decimal_days
from meshiphi.mesh_generation.mesh_builder import MeshBuilder
from meshiphi.mesh_generation.environment_mesh import EnvironmentMesh


@setup_logging
def get_args(
        default_output: str,
        config_arg: bool = True,
        mesh_arg: bool = False,
        format_arg: bool = False,
        merge_arg: bool = False):
    """
    Adds required command line arguments to all CLI entry points.

    Args:
        default_output (str): The default output file location.
        config_arg (bool): True if the CLI entry point requires a <config.json> file. Default is True.
        mesh_arg (bool): True if the CLI entry point requires a <mesh.json> file. Default is False.

    Returns:

    """
    ap = argparse.ArgumentParser()

    ap.add_argument('--version', action='version',
                        version='%(prog)s {version}'.format(version=version))

    # Optional arguments used in all CLI entry points
    ap.add_argument("-o", "--output",
                    default=default_output,
                    help="Output file")
    ap.add_argument("-v", "--verbose",
                    default=False,
                    action="store_true",
                    help="Turn on DEBUG level logging")

    if config_arg:
        ap.add_argument("config", type=argparse.FileType("r"), 
                    help="File location of a <config.json> file")

    if mesh_arg:
        ap.add_argument("mesh", type=argparse.FileType("r"),
                    help="File location of the environmental mesh")

        
    if format_arg:
        ap.add_argument("format",
                        help = "Export format to transform a mesh into. Supported \
                        formats are JSON, GEOJSON, Tif")
        ap.add_argument( "-f", "--format_conf",
                        default = None,
                        help = "File location of Export to Tif configuration parameters")

    if merge_arg:
        ap.add_argument("merge",
                    help="File location of the environmental mesh to merge with")
        ap.add_argument("-d", "--directory",
                    default=None,
                    action="store_true",
                    help="Flag to indicate that the merge file is a directory of meshes \
                        to merge. If set, the merge file is expected to be a directory of \
                        meshes to merge with the input mesh. The output will be a single merged mesh.")



    return ap.parse_args()

@timed_call
def rebuild_mesh_cli():
    """
        CLI entry point for rebuilding the mesh based on its encoded config files.
    """

    default_output = "rebuild_mesh.output.json"
    args = get_args(default_output, mesh_arg=True, config_arg=False)
    logging.info("{} {}".format(inspect.stack()[0][3][:-4], version))

    mesh_json = json.load(args.mesh)
    config = mesh_json['config']['mesh_info']

    # rebuilding mesh...
    rebuilt_mesh = MeshBuilder(config).build_environmental_mesh()
    rebuilt_mesh_json = rebuilt_mesh.to_json()

    logging.info("Saving mesh to {}".format(args.output))
    
    json.dump(rebuilt_mesh_json, open(args.output, "w"), indent=4)



@timed_call
def create_mesh_cli():
    """
        CLI entry point for the mesh construction
    """
    
    default_output = "create_mesh.output.json"
    args = get_args(default_output)
    logging.info("{} {}".format(inspect.stack()[0][3][:-4], version))

    config = json.load(args.config)

    # Discrete Meshing
    cg = MeshBuilder(config).build_environmental_mesh()

    logging.info("Saving mesh to {}".format(args.output))
    info = cg.to_json()
    json.dump(info, open(args.output, "w"), indent=4)
    

@timed_call
def export_mesh_cli():
    """
        CLI entry point for exporting a mesh to standard formats.
        Currently supported formats are JSON, GEOJSON, TIF, PNG
    """
    # Default, used only by the MeshiPhi and PolarRoute
    args = get_args("mesh.json", 
                    config_arg = False, 
                    mesh_arg = True, 
                    format_arg = True)
        
    if args.format.upper() == "GEOJSON":
        args = get_args("mesh_geo.json", 
                    config_arg = False, 
                    mesh_arg = True, 
                    format_arg = True)
        
    elif args.format.upper() == "TIF":
        args = get_args("mesh.tif", 
                    config_arg = False, 
                    mesh_arg = True, 
                    format_arg = True)

    elif args.format.upper() == "PNG":
        args = get_args("mesh.png", 
                    config_arg = False, 
                    mesh_arg = True, 
                    format_arg = True)
    
    logging.info("{} {}".format(inspect.stack()[0][3][:-4], version))

    mesh = json.load(args.mesh)
    env_mesh = EnvironmentMesh.load_from_json(mesh)

    logging.info(f"exporting mesh to {args.output} in format {args.format}")

    env_mesh.save(args.output, args.format , args.format_conf)

@timed_call
def merge_mesh_cli():
    """
        CLI entry point for merging two meshes.
    """

    from os import listdir 
    from os.path import isfile, join

    default_output = "merged_mesh.output.json"
    args = get_args(default_output, config_arg = False, mesh_arg=True, merge_arg=True)
    logging.info("{} {}".format(inspect.stack()[0][3][:-4], version))

    with open(args.mesh.name, "r") as f:
        mesh1 = json.load(args.mesh)
    env_mesh1 = EnvironmentMesh.load_from_json(mesh1)
    
    if args.directory:
        logging.debug("Merging multiple meshes from directory {} with input mesh".format(args.merge))

        merge_dir = args.merge
        merge_meshes = [f for f in listdir(merge_dir) if isfile(join(merge_dir, f))]

        for mesh in merge_meshes:
            with open(merge_dir + "/" + mesh, "r") as f:
                merge_mesh = json.load(f)
            env_mesh_merge = EnvironmentMesh.load_from_json(merge_mesh)

            env_mesh1.merge_mesh(env_mesh_merge)
    else:
    
        with open(args.merge, "r") as f:
            mesh2 = json.load(f)    
        env_mesh2 = EnvironmentMesh.load_from_json(mesh2)

        env_mesh1.merge_mesh(env_mesh2)
       
    merged_mesh_json = env_mesh1.to_json()

    logging.info("Saving merged mesh to {}".format(args.output))
    json.dump(merged_mesh_json, open(args.output, "w"), indent=4)
