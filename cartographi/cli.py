import argparse
import json
import inspect
import logging

from cartographi import __version__ as version
from cartographi.utils import setup_logging, timed_call, convert_decimal_days
from cartographi.mesh_generation.mesh_builder import MeshBuilder
from cartographi.mesh_generation.environment_mesh import EnvironmentMesh


@setup_logging
def get_args(
        default_output: str,
        config_arg: bool = True,
        mesh_arg: bool = False,
        format_arg: bool = False):
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
    config = mesh_json['config']

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
        Currently supported formats are JSON, GEOJSON, TIF
    """
    # Default, used only by the Mesh Builder and CartograPhi
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
    
    logging.info("{} {}".format(inspect.stack()[0][3][:-4], version))

    mesh = json.load(args.mesh)
    env_mesh = EnvironmentMesh.load_from_json(mesh)

    logging.info(f"exporting mesh to {args.output} in format {args.format}")

    env_mesh.save(args.output, args.format , args.format_conf)
