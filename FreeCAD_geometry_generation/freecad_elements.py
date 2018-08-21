import sys
# The location of the binary for the FreeCAD installation. In this case it is a Windows installation.
FREECADPATH = "C:\Program Files (x86)\FreeCAD 0.14\bin"
sys.path.append(FREECADPATH)
# This has to run using the FreeCAD built in python interpreter.
import FreeCAD, FreeCADGui
import Part, Mesh, MeshPart
from FreeCAD import Base
from math import pi
import copy
import os


class ModelException(Exception):
    """ This is to enable errors generated during the modelling to be separately dealt with, 
    compared to the other coding errors
    """
    pass


def base_model(model_function, input_params, output_path, accuracy=2):
    """Takes the INPUT_PARAMETERS dictionary as a base. It generates a model based on those inputs.

        Args:
            model_function (function handle): The handle of the specific model being used.
            input_params (dict): A dictionary containing the names and values of teh input parameters of the model.
            output_path (str): The location all the output files will be written to.
            accuracy (int): Represents the fineness of teh mesh. bigger number = finer mesh
 
            """
    inputs = copy.copy(input_params)   # To ensure the base settings are unchanged between sweeps.
    output_loc = copy.copy(output_path)
    try:
        parts_list, model_name = model_function(inputs)
        generate_output_files(output_loc, model_name, parts_list, inputs, tag='Base', mesh_resolution=accuracy)
    except ModelException as e:
        print 'Problem with base model ', '\n\t', e


def parameter_sweep(model_function, input_params, output_path, sweep_variable, sweep_vals, accuracy=2):
    """Takes the INPUT_PARAMETERS dictionary as a base. Then changes the requested input variable in a sequence.
        For each iteration it generates a model.

        Args:
            model_function (function handle): The handle of the specific model being used.
            input_params (dict): A dictionary containing the names and values of teh input parameters of the model.
            output_path (str): The location all the output files will be written to.
            sweep_variable (str): Name found in the input_params dictionary.
            sweep_vals (list): A list of valuse for the swept parameter to take.
            accuracy (int): Represents the fineness of teh mesh. bigger number = finer mesh

            """
    if sweep_variable not in input_params:
        raise ValueError('The variable to be swept does not exist in the input parameters dictionary.')
    inputs = copy.copy(input_params)   # To ensure the base settings are unchanged between sweeps.
    output_loc = copy.copy(output_path)
    for inputs[sweep_variable] in sweep_vals:
        # Replacing . with p to prevent problems with filename parsing
        value_string = str(inputs[sweep_variable]).replace('.', 'p')
        model_tag = ''.join([sweep_variable, '_sweep_value_', value_string])
        try:
            parts_list, model_name = model_function(inputs)
            generate_output_files(output_loc, model_name, parts_list, inputs, tag=model_tag, mesh_resolution=accuracy)
        except ModelException as e:
            print 'Problem with model ', sweep_variable, '_sweep_value_', str(inputs[sweep_variable]), '\n\t', e


def make_racetrack_aperture(aperture_height, aperture_width):
    """ Creates a wire outline of a symmetric racetrack.
        aperture_height and aperture_width are the full height and width (the same as if it were a rectangle).
        The end curves are defined as 180 degree arcs.

        Args:
            aperture_height (float): Total height of the aperture
            aperture_width (float): Total width of the aperture

        Returns:
            wire1 (FreeCAD wire definition): An outline description of the shape.
            face1 (FreeCAD face definition): A surface description of the shape.
        """
    # Create the initial four vertices where line meets curve.
    v1 = Base.Vector(0, aperture_height / 2., (-aperture_width + aperture_height) / 2.)
    v2 = Base.Vector(0, aperture_height / 2., (aperture_width - aperture_height) / 2.)
    v3 = Base.Vector(0, -aperture_height / 2.,  (aperture_width - aperture_height) / 2.)
    v4 = Base.Vector(0,  -aperture_height / 2., (-aperture_width + aperture_height) / 2.)
    # Create curves
    curve1 = Part.Circle(Base.Vector(0, 0, (-aperture_width + aperture_height) / 2.),
                         Base.Vector(1, 0, 0), aperture_height / 2.)
    arc1 = Part.Arc(curve1, pi / 2., 3 * pi / 2.)  # angles are in radian here
    curve2 = Part.Circle(Base.Vector(0, 0, (aperture_width - aperture_height) / 2.),
                         Base.Vector(1, 0, 0), aperture_height / 2.)
    arc2 = Part.Arc(curve2, -pi / 2., -3 * pi / 2.)  # angles are in radian here
    # Create lines
    line1 = Part.Line(v1, v2)
    line2 = Part.Line(v4, v3)
    # Make a shape
    shape1 = Part.Shape([arc1, arc2, line1, line2])
    # Make a wire outline.
    wire1 = Part.Wire(shape1.Edges)
    # Make a face.
    face1 = Part.Face(wire1)
    return wire1, face1


def make_circular_aperture(aperture_radius):
    """ Creates a wire outline of a circle.
        aperture_radius is the radius of the circle
        
        Args:
            aperture_radius (float): Total radius of the aperture

        Returns:
            wire1 (FreeCAD wire definition): An outline description of the shape.
            face1 (FreeCAD face definition): A surface description of the shape.
        """
    # Create curves
    curve1 = Part.Circle(Base.Vector(0, 0,0), Base.Vector(1, 0, 0), aperture_radius)
    arc1 = Part.Arc(curve1, 0., 2 * pi)  # angles are in radian here
    
    # Make a shape
    shape1 = Part.Shape([arc1])
    # Make a wire outline.
    wire1 = Part.Wire(shape1.Edges)
    # Make a face.
    face1 = Part.Face(wire1)
    return wire1, face1


def make_octagonal_aperture(aperture_height, aperture_width, side_length, tb_length):
    """ Creates a wire outline of a symmetric octagon specified by 4 inputs.
    aperture_height and aperture_width are the full height and width (the same as if it were a rectangle)
    side_length and tb_length specify the lengths of the top/ bottom and sides
    and so implicitly allow the diagonals to be defined.

    Args:
        aperture_height (float): Total height of the octagon.
        aperture_width (float): Total width of the octagon.
        side_length (float): Length of the vertical sides
        tb_length (float): Length of the horizontal sides.

    Returns:
        wire1 (FreeCAD wire definition): An outline description of the shape.
        face1 (FreeCAD face definition): A surface description of the shape.
    """

    # Create the initial eight vertices where line meets curve.
    v1 = Base.Vector(0, aperture_height / 2., -tb_length / 2.)
    v2 = Base.Vector(0, aperture_height / 2., tb_length / 2.)
    v3 = Base.Vector(0, side_length / 2., aperture_width / 2.)
    v4 = Base.Vector(0, -side_length / 2., aperture_width / 2.)
    v5 = Base.Vector(0, -aperture_height / 2., tb_length / 2.)
    v6 = Base.Vector(0, -aperture_height / 2., -tb_length / 2.)
    v7 = Base.Vector(0, -side_length / 2., -aperture_width / 2.)
    v8 = Base.Vector(0, side_length / 2., -aperture_width / 2.)

    # Create lines
    line1 = Part.Line(v1, v2)
    line2 = Part.Line(v2, v3)
    line3 = Part.Line(v3, v4)
    line4 = Part.Line(v4, v5)
    line5 = Part.Line(v5, v6)
    line6 = Part.Line(v6, v7)
    line7 = Part.Line(v7, v8)
    line8 = Part.Line(v8, v1)
    # Make a shape
    shape1 = Part.Shape([line1, line2, line3, line4, line5, line6, line7, line8])
    # Make a wire outline.
    wire1 = Part.Wire(shape1.Edges)
    # Make a face.
    face1 = Part.Face(wire1)
    return wire1, face1


def make_elliptical_aperture(aperture_height, aperture_width):
    """ Creates a wire outline of a ellipse specified by 2 inputs.
        aperture_height and aperture_width are the full height and width (the same as if it were a rectangle)

        Args:
            aperture_height (float): Total height of the ellipse.
            aperture_width (float): Total width of the ellipse.

        Returns:
            wire1 (FreeCAD wire definition): An outline description of the shape.
            face1 (FreeCAD face definition): A surface description of the shape.
    """
    # # Define the semi axis
    b = aperture_height / 2.
    a = aperture_width / 2.

    test = Part.Ellipse(Base.Vector(0, 0, 0), a, b)
    # Make a shape
    shape1 = test.toShape()
    shape1.rotate(Base.Vector(0, 0, 0), Base.Vector(0, 1, 0), 90)
    # Make a wire outline.
    wire1 = Part.Wire(shape1.Edges)
    face1 = Part.Face(wire1)
    return wire1, face1


def make_beampipe(pipe_aperture, pipe_length, loc=(0, 0, 0), rotation_angles=(0, 0, 0)):
    """ Takes an aperture and creates a pipe.
    The centre of the beam pipe will be at loc and rotations will happen about that point.
    Assumes the aperture is initially centred on (0,0,0)

        Args:
            pipe_aperture (FreeCad wire): Outline of aperture.
            pipe_length (float): Length of pipe.
            loc (tuple): The co ordinates of the final location of the centre of the pipe.
            rotation_angles (tuple) : The angles to rotate about in the three cartesian directions.

        Returns:
            p (FreeCad shape): A model of the pipe.
    """
    p = pipe_aperture.extrude(Base.Vector(pipe_length, 0, 0))
    p.translate(Base.Vector(-pipe_length/2., 0, 0))  # move to be centred on (0,0,0)
    p.rotate(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), rotation_angles[2])    # Rotate around Z
    p.rotate(Base.Vector(0, 0, 0), Base.Vector(1, 0, 0), rotation_angles[0])    # Rotate around X
    p.rotate(Base.Vector(0, 0, 0), Base.Vector(0, 1, 0), rotation_angles[1])    # Rotate around Y
    p.translate(Base.Vector(loc[0], loc[1], loc[2]))  # Move to be centred on loc
    return p


def make_taper(aperture1, aperture2, taper_length, loc=(0,0,0), rotation_angles=(0,0,0)):
    """Takes two aperture descriptions and creates a taper between them.
     The centre of the face of aperture1 will be at loc and rotations will happen about that point.
     Assume both apertures are initially centred on (0,0,0)

     Args:
        aperture1 (FreeCad wire): Outline of starting aperture.
        aperture2 (FreeCad wire): Outline of ending aperture.
        taper_length (float): distance between apertures.
        loc (tuple) : The co ordinates of the final location of the centre of aperture1.
        rotation_angles (tuple) : The angles to rotate about in the three cartesian directions.

     Returns:
        taper (FreeCAD shape): A model of the shape.
    """
    aperture2.translate(Base.Vector(taper_length, 0, 0))
    taper = Part.makeLoft([aperture1, aperture2], True, False, False)
    taper.rotate(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), rotation_angles[2])    # Rotate around Z
    taper.rotate(Base.Vector(0, 0, 0), Base.Vector(1, 0, 0), rotation_angles[0])    # Rotate around X
    taper.rotate(Base.Vector(0, 0, 0), Base.Vector(0, 1, 0), rotation_angles[1])    # Rotate around Y
    taper.translate(Base.Vector(loc[0], loc[1], loc[2]))  # Move to be centred on loc
    # Returning the aperture to it's original location so that it is where other functions expect.
    aperture2.translate(Base.Vector(-taper_length, 0, 0))
    return taper


def rotate_at(shp, loc=(0, 0, 0), rotation_angles=(0, 0, 0)):
    """ Rotates a shape around a point in space.
    
        Args:
            shp (FreeCAD shape): The shape you are wanting to rotate.
            loc (tuple): The co ordinates of the centre of rotation.
            rotation_angles (tuple) : The angles to rotate about in the three cartesian directions.
            
        Returns:
            shp (FreeCad shape): The rotated shape.
    """
    shp.rotate(Base.Vector(loc[0], loc[1], loc[2]), Base.Vector(0, 0, 1), rotation_angles[2])    # Rotate around Z
    shp.rotate(Base.Vector(loc[0], loc[1], loc[2]), Base.Vector(1, 0, 0), rotation_angles[0])    # Rotate around X
    shp.rotate(Base.Vector(loc[0], loc[1], loc[2]), Base.Vector(0, 1, 0), rotation_angles[1])    # Rotate around Y
    return shp


def generate_output_files(root_loc, model_name, parts_list, input_parameters, tag, mesh_resolution=2):
    """Takes the dictionary of parts, converts them to meshes.
    Saves the resulting meshes in both binary and ascii STL format. (ECHO needs binary, GdfidL needs ASCII).
     Also saves the Geometry in a freeCAD document.

     Args:
            root_loc (str): location of the folder the results are writen to.
            model_name (str): name of the model.
            parts_list (dict): dictionary of shapes used to construct the model.
            input_parameters (dict): dictionary of input parameters used to make the model.
            tag (str): Unique identifier string for a particular model iteration.
            mesh_resolution (int): the resolution of hte meshing (equivalent to the Fineness parameter in meshFromShape)
    """
    document_name = ''.join([model_name, '_model__', tag])
    output_loc = os.path.join(root_loc, model_name, ''.join([model_name, '_', tag]))
    if not os.path.exists(output_loc):
        os.makedirs(output_loc)
    if not os.path.exists(os.path.join(output_loc, 'binary')):
        os.makedirs(os.path.join(output_loc, 'binary'))
    if not os.path.exists(os.path.join(output_loc, 'ascii')):
        os.makedirs(os.path.join(output_loc, 'ascii'))

    doc = FreeCAD.newDocument(document_name)
    part_labels = parts_list.keys()
    for part in part_labels:
        part_name = '-'.join([model_name, part])
        myObject = doc.addObject("Part::Feature", part_name)
        myObject.Shape = parts_list[part]
        doc.recompute()
        doc.saveAs(os.path.join(output_loc, ''.join([model_name, '_', tag, '.FCStd'])))
        # Generate a mesh from the shape.
        mesh_name = ''.join([part_name, ' (Meshed)'])
        m1 = MeshPart.meshFromShape(Shape=parts_list[part], Fineness=mesh_resolution, SecondOrder=1, Optimize=1,
                                    AllowQuad=1)
        mymesh = doc.addObject("Mesh::Feature", "Mesh")
        mymesh.Mesh = m1
        mymesh.Label = mesh_name
        mymesh.Mesh.write(os.path.join(output_loc, 'binary', ''.join([part_name, '.stl'])), "STL", mesh_name)
        mymesh.Mesh.write(os.path.join(output_loc, 'ascii', ''.join([part_name, '.stl'])), "AST", mesh_name)
    parameter_file_name = ''.join([model_name, '_', tag, '_parameters.txt'])
    param_file = open(os.path.join(output_loc, parameter_file_name), 'w')
    for name, value in input_parameters.items():
        param_file.write(''.join([name, ' : ', str(value), '\n']))
    param_file.close()

