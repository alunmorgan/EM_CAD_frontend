import copy
import os
import sys
from math import atan2, cos, radians, sin, sqrt

import FreeCAD

import MeshPart
import Part
from FreeCAD import Base, Units


class ModelException(Exception):
    """This is to enable errors generated during the modelling to be separately dealt with,
    compared to the other coding errors
    """

    def __init__(self, e):
        ex_type, ex_value, ex_traceback = sys.exc_info()
        print("Exception type : %s " % ex_type.__name__)
        print("Exception message : %s" % ex_value)


def breakup_lists(input_dict):
    output_dict = {}
    for key in input_dict:
        if type(input_dict[key]) is list:
            ck = 1
            for val in input_dict[key]:
                output_dict[key + str(ck)] = val
                ck += 1
        else:
            output_dict[key] = input_dict[key]
    return output_dict

def parse_input_parameters(input_parameters):
    for n in input_parameters.keys():
        if type(input_parameters[n]) is list:
            for eh in range(len(input_parameters[n])):
                input_parameters[n][eh] = Units.Quantity(input_parameters[n][eh])
        else:
            input_parameters[n] = Units.Quantity(input_parameters[n])
    print("Parsing completed")
    return input_parameters

def base_model(
    model_name, model_function, input_params, output_path, accuracy=2, just_cad=0
):
    """Takes the INPUT_PARAMETERS dictionary as a base.
    It generates a model based on those inputs.

    Args:
        model_name (str): Name of the current model.
        model_function (function handle): The handle of the specific model being used.
        input_params (dict): A dictionary containing the names and values of the input
                             parameters of the model.
        output_path (str): The location all the output files will be written to.
        accuracy (int): Represents the fineness of the mesh. bigger number = finer mesh
        just_cad(int): selects if the STL files are generated. Early in the design it
                       can be useful to turn them off
    """
    inputs = copy.copy(
        input_params
    )  # To ensure the base settings are unchanged between sweeps.
    inputs_nolists = breakup_lists(
        inputs
    )  # If you use a variable which is a list for controlling the
    # mesh fixed lines the code breaks.
    # This breaks lists into separate directory entries.
    # However you do want lists in the original inputs as this allows more flexibity
    # in the parameter sweeps.
    output_loc = copy.copy(output_path)
    try:
        inputs = parse_input_parameters(inputs)
        parts_list = model_function(inputs)

        generate_output_files(
            output_loc,
            model_name,
            parts_list,
            inputs_nolists,
            tag="Base",
            mesh_resolution=accuracy,
            just_cad=just_cad,
        )
    except ModelException as e:
        print("Problem with base model ", "\n\t", e)


def parameter_sweep(
    model_name,
    model_function,
    input_params,
    output_path,
    sweep_variable,
    sweep_vals,
    accuracy=5,
    just_cad=0,
):
    """Takes the INPUT_PARAMETERS dictionary as a base. Then changes the requested
    input variable in a sequence.
    For each iteration it generates a model.

    Args:
        model_name (str): Name of the current model.
        model_function (function handle): The handle of the specific model being used.
        input_params (dict): A dictionary containing the names and values of the input
                             parameters of the model.
        output_path (str): The location all the output files will be written to.
        sweep_variable (str): Name found in the input_params dictionary.
        sweep_vals (list): A list of values for the swept parameter to take.
        accuracy (int): Represents the fineness of teh mesh. bigger number = finer mesh
        just_cad(int): selects if the STL files are generated. Early in the design it
                       can be useful to turn them off

    """
    if sweep_variable not in input_params:
        raise ValueError(
            "".join(
                (
                    "The variable to be swept does not exist in the ",
                    "input parameters dictionary.",
                )
            )
        )
    for sweep_val in sweep_vals:
        inputs = copy.copy(
            input_params
        )  # To ensure the base settings are unchanged between sweeps.
        inputs[sweep_variable] = sweep_val
        inputs_nolists = breakup_lists(
            inputs
        )  # If you use a variable which is a list for controlling the
        # mesh fixed lines the code breaks.
        # This breaks lists into separate directory entries.
        # However you do want lists in the original inputs as this allows more flexibity
        # in the parameter sweeps.
        
        # Replacing . with p to prevent problems with filename parsing
        value_string = str(inputs[sweep_variable]).replace(".", "p")
        value_string = value_string.replace(" ", "")
        value_string = value_string.replace(",", "")
        value_string = value_string.replace("[", "")
        value_string = value_string.replace("]", "")
        value_string = value_string.replace("'", "")
        value_string = value_string.replace("-", "m")

        model_tag = "".join([sweep_variable, "_sweep_value_", value_string])
        try:
            inputs = parse_input_parameters(inputs)
            parts_list = model_function(inputs)
            generate_output_files(
                copy.copy(output_path),
                model_name,
                parts_list,
                inputs_nolists,
                tag=model_tag,
                mesh_resolution=accuracy,
                just_cad=just_cad,
            )
        except ModelException as e:
            print(
                "Problem with model ",
                sweep_variable,
                "_sweep_value_",
                str(inputs[sweep_variable]),
                "\n\t",
                e,
            )


def add_shadowing_bump(
    pipe_width,
    bump_thickness,
    bump_height,
    bump_top_length,
    bump_us_length,
    bump_ds_length,
    side,
    longitudinal_position,
):
    if side == "ib":
        us2 = Base.Vector(
            longitudinal_position - bump_top_length / 2 - bump_us_length,
            -pipe_width / 2.0,
            bump_thickness / 2.0,
        )
        us3 = Base.Vector(
            longitudinal_position - bump_top_length / 2.0,
            -pipe_width / 2.0 + bump_height,
            bump_thickness / 2.0,
        )
        ds2 = Base.Vector(
            longitudinal_position + bump_top_length / 2 + bump_ds_length,
            -pipe_width / 2.0,
            bump_thickness / 2.0,
        )
        ds3 = Base.Vector(
            longitudinal_position + bump_top_length / 2.0,
            -pipe_width / 2.0 + bump_height,
            bump_thickness / 2.0,
        )
    elif side == "ob":
        us2 = Base.Vector(
            longitudinal_position - bump_top_length / 2 - bump_us_length,
            pipe_width / 2.0,
            bump_thickness / 2.0,
        )
        us3 = Base.Vector(
            longitudinal_position - bump_top_length / 2.0,
            pipe_width / 2.0 - bump_height,
            bump_thickness / 2.0,
        )
        ds2 = Base.Vector(
            longitudinal_position + bump_top_length / 2 + bump_ds_length,
            pipe_width / 2.0,
            bump_thickness / 2.0,
        )
        ds3 = Base.Vector(
            longitudinal_position + bump_top_length / 2.0,
            pipe_width / 2.0 - bump_height,
            bump_thickness / 2.0,
        )
    else:
        raise ValueError("Valid inputs for bump side is ob or ib")
    line1 = Part.LineSegment(ds2, us2)
    line2 = Part.LineSegment(us2, us3)
    line3 = Part.LineSegment(us3, ds3)
    line4 = Part.LineSegment(ds3, ds2)
    shape1 = Part.Shape([line1, line2, line3, line4])
    # Make a wire outline.
    wire1 = Part.Wire(shape1.Edges)
    # Make a face.
    face1 = Part.Face(wire1)
    bump = face1.extrude(Base.Vector(0, 0, -bump_thickness))
    return bump


def make_beampipe(pipe_aperture, pipe_length, loc=(0, 0, 0), rotation_angles=(0, 0, 0)):
    """Takes an aperture and creates a pipe.
    The centre of the beam pipe will be at loc and rotations will happen
    about that point.
    Assumes the aperture is initially centred on (0,0,0)

        Args:
            pipe_aperture (FreeCad wire): Outline of aperture.
            pipe_length (float): Length of pipe.
            loc (tuple): The co ordinates of the final location of the
                         centre of the pipe.
            rotation_angles (tuple) : The angles to rotate about in the three
                                      cartesian directions.

        Returns:
            p (FreeCad shape): A model of the pipe.
    """
    p = pipe_aperture.extrude(Base.Vector(pipe_length, 0, 0))
    p.translate(Base.Vector(-pipe_length / 2.0, 0, 0))  # move to be centred on (0,0,0)
    p.rotate(
        Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), rotation_angles[2]
    )  # Rotate around Z
    p.rotate(
        Base.Vector(0, 0, 0), Base.Vector(1, 0, 0), rotation_angles[0]
    )  # Rotate around X
    p.rotate(
        Base.Vector(0, 0, 0), Base.Vector(0, 1, 0), rotation_angles[1]
    )  # Rotate around Y
    p.translate(Base.Vector(loc[0], loc[1], loc[2]))  # Move to be centred on loc
    return p

def make_beampipe_from_end(pipe_aperture, pipe_length, loc=(0, 0, 0), rotation_angles=(0, 0, 0)):
    """Takes an aperture and creates a pipe.
    The centre of the face of aperture1 will be at loc and rotations will happen
    about that point.
    Assumes the aperture is initially centred on (0,0,0)

        Args:
            pipe_aperture (FreeCad wire): Outline of aperture.
            pipe_length (float): Length of pipe.
            loc (tuple): The co ordinates of the final location of the
                         centre of the pipe.
            rotation_angles (tuple) : The angles to rotate about in the three
                                      cartesian directions.

        Returns:
            p (FreeCad shape): A model of the pipe.
    """
    p = pipe_aperture.extrude(Base.Vector(pipe_length, 0, 0))
    p.rotate(
        Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), rotation_angles[2]
    )  # Rotate around Z
    p.rotate(
        Base.Vector(0, 0, 0), Base.Vector(1, 0, 0), rotation_angles[0]
    )  # Rotate around X
    p.rotate(
        Base.Vector(0, 0, 0), Base.Vector(0, 1, 0), rotation_angles[1]
    )  # Rotate around Y
    p.translate(Base.Vector(loc[0], loc[1], loc[2]))  # Move to be centred on loc
    return p


def make_taper(
    aperture1,
    aperture2,
    taper_length,
    loc=(0, 0, 0),
    rotation_angles=(0, 0, 0),
    aperture_xy_offset=(0, 0),
):
    """Takes two aperture descriptions and creates a taper between them.
    The centre of the face of aperture1 will be at loc and rotations will happen
    about that point.
    Assume both apertures are initially centred on (0,0,0)

    Args:
       aperture1 (FreeCad wire): Outline of starting aperture.
       aperture2 (FreeCad wire): Outline of ending aperture.
       taper_length (float): distance between apertures.
       loc (tuple) : The co ordinates of the final location of the centre of aperture1.
       rotation_angles (tuple) : The angles to rotate about in the three
                                 cartesian directions.
       aperture_xy_offset(tuple): The translational offsets between teh two apertures.

    Returns:
       taper (FreeCAD shape): A model of the shape.
    """
    aperture2.translate(
        Base.Vector(taper_length, aperture_xy_offset[0], aperture_xy_offset[1])
    )
    taper = Part.makeLoft([aperture1, aperture2], True, False, False)
    taper.rotate(
        Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), rotation_angles[2]
    )  # Rotate around Z
    taper.rotate(
        Base.Vector(0, 0, 0), Base.Vector(1, 0, 0), rotation_angles[0]
    )  # Rotate around X
    taper.rotate(
        Base.Vector(0, 0, 0), Base.Vector(0, 1, 0), rotation_angles[1]
    )  # Rotate around Y
    taper.translate(Base.Vector(loc[0], loc[1], loc[2]))  # Move to be centred on loc
    # Returning the aperture to it's original location so that it is
    # where other functions expect.
    aperture2.translate(Base.Vector(-taper_length, 0, 0))
    return taper


def rotate_cartesian(x, y, angle):
    r = Units.Quantity(sqrt(x * x + y * y), 1)  # Forcing length units
    a = atan2(y, x)
    a2 = a + radians(angle)
    x_out = r * cos(a2)
    y_out = r * sin(a2)
    return x_out, y_out


def rotate_at(shp, loc=(0, 0, 0), rotation_angles=(0, 0, 0)):
    """Rotates a shape around a point in space.

    Args:
        shp (FreeCAD shape): The shape you are wanting to rotate.
        loc (tuple): The co ordinates of the centre of rotation.
        rotation_angles (tuple) : The angles to rotate about in the three
                                  cartesian directions.

    Returns:
        shp (FreeCad shape): The rotated shape.
    """
    shp.rotate(
        Base.Vector(loc[0], loc[1], loc[2]), Base.Vector(0, 0, 1), rotation_angles[2]
    )  # Rotate around Z
    shp.rotate(
        Base.Vector(loc[0], loc[1], loc[2]), Base.Vector(1, 0, 0), rotation_angles[0]
    )  # Rotate around X
    shp.rotate(
        Base.Vector(loc[0], loc[1], loc[2]), Base.Vector(0, 1, 0), rotation_angles[1]
    )  # Rotate around Y
    return shp


def ellipse_track(e_height, e_width, x):
    a = e_width / 2.0
    b = e_height / 2.0
    y = (b ** 2.0 - ((b / a) * x) ** 2.0) ** 0.5
    return y


def clean_stl(stl_object):
    ncycles = 5
    for cycles in range(ncycles):
        fixed_normals = stl_object.harmonizeNormals()
        fixed_facets = stl_object.removeDuplicatedFacets()
        fixed_points = stl_object.removeDuplicatedPoints()
        # fixed_manifolds = stl_object.removeNonManifolds()
        fixed_indicies = stl_object.fixIndices()
        fixed_degenerations = stl_object.fixDegenerations(0.00000)
        # fixed_folds = stl_object.removeFoldsOnSurface()
        # fixed_intersections = stl_object.fixSelfIntersections()
        print("Fixed normals", fixed_normals)
        # print('Fixed manifolds', fixed_manifolds)
        print("fixed indicies", fixed_indicies)
        print("fixed degenerations", fixed_degenerations)
        # print('fixed surface folds', fixed_folds)
        print("fixed duplicated facets", fixed_facets)
        print("fixed duplicated points", fixed_points)
        # print('fixed self intersections', fixed_intersections)
        status = [
            fixed_normals,
            fixed_indicies,
            fixed_degenerations,
            fixed_facets,
            fixed_points,
        ]
        new_status = [True for i in status if i is None]
        if len(status) == len(new_status):
            print("Nothing to fix")
            return
        elif cycles == ncycles - 1:
            print("Max number of cycles reached")
            return
        else:
            print("One more loop")


def generate_output_files(
    root_loc,
    model_name,
    parts_list,
    input_parameters,
    tag,
    solvertype="standard",
    mesh_resolution=5,
    just_cad=0,
):
    """Takes the dictionary of parts, converts them to meshes.
    Saves the resulting meshes in both binary and ascii STL format.
    (ECHO needs binary, GdfidL needs ASCII).
     Also saves the Geometry in a freeCAD document.

     Args:
            root_loc (str): location of the folder the results are writen to.
            model_name (str): name of the model.
            parts_list (dict): dictionary of shapes used to construct the model.
            input_parameters (dict): dictionary of input parameters used to
                                     make the model.
            tag (str): Unique identifier string for a particular model iteration.
            solvertype(str): selects which meshing solver to use (standard or netgen).
            mesh_resolution (int): the resolution of the meshing (equivalent to the
                                   Fineness parameter in meshFromShape)
            just_cad(int): selects if the STL files are generated. Early in the design
                           it can be useful to turn them off
    """
    document_name = "".join([model_name, "_model__", tag])
    output_loc = os.path.join(root_loc, "".join([model_name, "_", tag]))
    if not os.path.exists(output_loc):
        os.makedirs(output_loc)
    if not os.path.exists(os.path.join(output_loc, "binary")):
        os.makedirs(os.path.join(output_loc, "binary"))
    if not os.path.exists(os.path.join(output_loc, "ascii")):
        os.makedirs(os.path.join(output_loc, "ascii"))

    doc = FreeCAD.newDocument(document_name)
    part_labels = parts_list.keys()
    for part in part_labels:
        part_name = "-".join([model_name, part])
        my_object = doc.addObject("Part::Feature", part_name)
        my_object.Shape = parts_list[part]
    doc.recompute()
    # Saving to a short named temp file then doing an OS rename in order to avoid path
    #  length limitation issues when saving the temp file.
    doc.saveAs(os.path.join(output_loc, "".join(["A", ".FCStd"])))
    outfilename = os.path.join(output_loc, "".join([model_name, "_", tag, ".FCStd"]))
    if os.path.exists(outfilename):
        os.remove(outfilename)
    os.rename(os.path.join(output_loc, "".join(["A", ".FCStd"])), outfilename)
    print(outfilename)
    if just_cad == 0:
        for part in part_labels:
            part_name = "-".join([model_name, part])
            # Generate a mesh from the shape.
            mesh_name = "".join([part_name, " (Meshed)"])
            print("".join(["generating STL mesh for ", mesh_name]))
            if solvertype == "netgen":
                # Using the netgen mesher
                m1 = MeshPart.meshFromShape(
                    Shape=parts_list[part],
                    GrowthRate=0.1,
                    SegPerEdge=mesh_resolution,
                    SegPerRadius=mesh_resolution,
                    SecondOrder=0,
                    Optimize=1,
                    AllowQuad=0,
                )
            elif solvertype == "standard":
                # Using standard mesher
                m1 = MeshPart.meshFromShape(
                    Shape=parts_list[part],
                    LinearDeflection=0.01,
                    AngularDeflection=0.1,
                    Relative=True,
                )
            else:
                raise ValueError("solver type should be netgen or standard")

            clean_stl(m1)

            mymesh = doc.addObject("Mesh::Feature", "Mesh")
            mymesh.Mesh = m1
            mymesh.Label = mesh_name
            mymesh.Mesh.write(
                os.path.join(output_loc, "ascii", "".join([part_name, ".stl"])),
                "AST",
                mesh_name,
            )

    FreeCAD.closeDocument(document_name)

    paramfilename = os.path.join(output_loc, "A.txt")
    parameter_file_name = os.path.join(
        output_loc, "".join([model_name, "_", tag, "_parameters.txt"])
    )
    if os.path.exists(paramfilename):
        os.remove(paramfilename)
    if os.path.exists(parameter_file_name):
        os.remove(parameter_file_name)

    param_file = open(paramfilename, "w")
    for name, value in input_parameters.items():
        param_file.write("".join([name, " : ", str(value), "\n"]))
    param_file.close()

    os.rename(paramfilename, parameter_file_name)
