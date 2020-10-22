# This has to run using the FreeCAD built in python interpreter.
import FreeCAD, FreeCADGui
import Part, Mesh, MeshPart
from FreeCAD import Base, Units
from math import pi, asin, sqrt, sin, cos, tan, atan, radians, atan2, degrees
import copy
import os
import sys


class ModelException(Exception):
    """ This is to enable errors generated during the modelling to be separately dealt with, 
    compared to the other coding errors
    """
    def __init__(self, e):
        ex_type, ex_value, ex_traceback = sys.exc_info()
        print("Exception type : %s " % ex_type.__name__)
        print("Exception message : %s" % ex_value)


def base_model(model_name, model_function, input_params, output_path, accuracy=2, just_cad=0):
    """Takes the INPUT_PARAMETERS dictionary as a base. It generates a model based on those inputs.

        Args:
            model_name (str): Name of the current model.
            model_function (function handle): The handle of the specific model being used.
            input_params (dict): A dictionary containing the names and values of teh input parameters of the model.
            output_path (str): The location all the output files will be written to.
            accuracy (int): Represents the fineness of teh mesh. bigger number = finer mesh
            just_cad(int): selects if the STL files are generated. Early in the design it can be useful to turn them off
            """
    inputs = copy.copy(input_params)   # To ensure the base settings are unchanged between sweeps.
    output_loc = copy.copy(output_path)
    try:
        parts_list = model_function(inputs)
        generate_output_files(output_loc, model_name, parts_list, inputs, tag='Base', mesh_resolution=accuracy,
                              just_cad=just_cad)
    except ModelException as e:
        print('Problem with base model ', '\n\t', e)


def parameter_sweep(model_name, model_function, input_params, output_path, sweep_variable, sweep_vals, accuracy=5,
                    just_cad=0):
    """Takes the INPUT_PARAMETERS dictionary as a base. Then changes the requested input variable in a sequence.
        For each iteration it generates a model.

        Args:
            model_name (str): Name of the current model.
            model_function (function handle): The handle of the specific model being used.
            input_params (dict): A dictionary containing the names and values of teh input parameters of the model.
            output_path (str): The location all the output files will be written to.
            sweep_variable (str): Name found in the input_params dictionary.
            sweep_vals (list): A list of values for the swept parameter to take.
            accuracy (int): Represents the fineness of teh mesh. bigger number = finer mesh
            just_cad(int): selects if the STL files are generated. Early in the design it can be useful to turn them off

            """
    if sweep_variable not in input_params:
        raise ValueError('The variable to be swept does not exist in the input parameters dictionary.')
    for sweep_val in sweep_vals:
        inputs = copy.copy(input_params)  # To ensure the base settings are unchanged between sweeps.
        inputs[sweep_variable] = sweep_val
        # Replacing . with p to prevent problems with filename parsing
        value_string = str(inputs[sweep_variable]).replace('.', 'p')
        value_string = value_string.replace(' ', '')
        value_string = value_string.replace(',', '')
        value_string = value_string.replace('[', '')
        value_string = value_string.replace(']', '')
        value_string = value_string.replace('\'', '')
        value_string = value_string.replace('-', 'm')

        model_tag = ''.join([sweep_variable, '_sweep_value_', value_string])
        try:
            parts_list = model_function(inputs)
            generate_output_files(copy.copy(output_path), model_name, parts_list, inputs, tag=model_tag,
                                  mesh_resolution=accuracy, just_cad=just_cad)
        except ModelException as e:
            print('Problem with model ', sweep_variable, '_sweep_value_', str(inputs[sweep_variable]), '\n\t', e)


def add_shadowing_bump(pipe_width, bump_thickness, bump_height, bump_top_length, bump_us_length, bump_ds_length, side,
                       longitudinal_position):
    if side == 'ib':
        us2 = Base.Vector(longitudinal_position - bump_top_length / 2 - bump_us_length,
                          -pipe_width / 2., bump_thickness / 2.)
        us3 = Base.Vector(longitudinal_position - bump_top_length / 2.,
                          -pipe_width / 2. + bump_height, bump_thickness / 2.)
        ds2 = Base.Vector(longitudinal_position + bump_top_length / 2 + bump_ds_length,
                          -pipe_width / 2., bump_thickness / 2.)
        ds3 = Base.Vector(longitudinal_position + bump_top_length / 2.,
                          -pipe_width / 2. + bump_height, bump_thickness / 2.)
    elif side == 'ob':
        us2 = Base.Vector(longitudinal_position - bump_top_length / 2 - bump_us_length, pipe_width / 2.,
                          bump_thickness / 2.)
        us3 = Base.Vector(longitudinal_position - bump_top_length / 2., pipe_width / 2. - bump_height,
                          bump_thickness / 2.)
        ds2 = Base.Vector(longitudinal_position + bump_top_length / 2 + bump_ds_length, pipe_width / 2.,
                          bump_thickness / 2.)
        ds3 = Base.Vector(longitudinal_position + bump_top_length / 2., pipe_width / 2. - bump_height,
                          bump_thickness / 2.)
    else:
        raise ValueError('Valid inputs for bump side is ob or ib')
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
    line1 = Part.LineSegment(v1, v2)
    line2 = Part.LineSegment(v4, v3)
    # Make a shape
    shape1 = Part.Shape([line1, arc1, line2, arc2])
    # Make a wire outline.
    wire1 = Part.Wire(shape1.Edges)
    # Make a face.
    face1 = Part.Face(wire1)
    return wire1, face1


def make_rectangle_aperture(aperture_height, aperture_width):
    """ Creates a wire outline of a rectangle.
        aperture_height and aperture_width are the full height and width.


        Args:
            aperture_height (float): Total height of the aperture
            aperture_width (float): Total width of the aperture

        Returns:
            wire1 (FreeCAD wire definition): An outline description of the shape.
            face1 (FreeCAD face definition): A surface description of the shape.
        """
    # Create the initial four vertices where line meets curve.
    v1 = Base.Vector(0, aperture_height / 2., -aperture_width / 2.)
    v2 = Base.Vector(0, aperture_height / 2., aperture_width / 2.)
    v3 = Base.Vector(0, -aperture_height / 2., aperture_width / 2.)
    v4 = Base.Vector(0,  -aperture_height / 2., -aperture_width / 2.)
    # Create lines
    line1 = Part.LineSegment(v1, v2)
    line2 = Part.LineSegment(v2, v3)
    line3 = Part.LineSegment(v3, v4)
    line4 = Part.LineSegment(v4, v1)
    # Make a shape
    shape1 = Part.Shape([line1, line2, line3, line4])
    # Make a wire outline.
    wire1 = Part.Wire(shape1.Edges)
    # Make a face.
    face1 = Part.Face(wire1)
    return wire1, face1


def make_keyhole_aperture(pipe_radius, keyhole_height, keyhole_width):
    """ Creates a wire outline of a circular pipe with a keyhole extension on the side.
        aperture_height and aperture_width are the full height and width (the same as if it were a rectangle).
        The end curves are defined as 180 degree arcs.

        Args:
            pipe_radius (float): Radius of the main beam pipe.
            keyhole_height (float): Total height of the keyhole slot.
            keyhole_width (float): Total width of the keyhole slot.

        Returns:
            wire1 (FreeCAD wire definition): An outline description of the shape.
            face1 (FreeCAD face definition): A surface description of the shape.
        """
    # X intersection of keyhole with pipe.
    x_intersection = sqrt(pipe_radius**2 - (keyhole_height / 2.)**2)
    # Create the initial four vertices for the lines.
    v1 = Base.Vector(0, keyhole_height / 2., x_intersection)
    v2 = Base.Vector(0, keyhole_height / 2., x_intersection + keyhole_width - keyhole_height / 2)
    v3 = Base.Vector(0, -keyhole_height / 2., x_intersection + keyhole_width - keyhole_height / 2)
    v4 = Base.Vector(0, -keyhole_height / 2., x_intersection)
    v5 = Base.Vector(0, 0, x_intersection + keyhole_width)
    # Create lines
    line1 = Part.LineSegment(v1, v2)
    arc2 = Part.Arc(v2, v5, v3)
    line3 = Part.LineSegment(v3, v4)

    # angle at which the keyhole intersects the pipe.
    half_angle = asin(keyhole_height / (2 * pipe_radius))
    # Create curves
    curve1 = Part.Circle(Base.Vector(0, 0, 0),
                         Base.Vector(1, 0, 0), pipe_radius)
    arc1 = Part.Arc(curve1, half_angle, (2 * pi) - half_angle)  # angles are in radian here

    # Make a shape
    shape1 = Part.Shape([arc1, line1, arc2, line3])
    # Make a wire outline.
    wire1 = Part.Wire(shape1.Edges)
    # Make a face.
    face1 = Part.Face(wire1)
    return wire1, face1


def make_arc_aperture(arc_inner_radius, arc_outer_radius, arc_length, blend_radius=Units.Quantity('0 mm')):
    """ Creates a wire outline of an arc.

        Args:
            arc_inner_radius (float): Radius of the inside edge of the arc.
            arc_outer_radius (float): Radius of the outside edge of the arc.
            arc_length (float): The length of the arc (measured in angle in radians)
            blend_radius (float): The amount to smooth the edges.

        Returns:
            wire1 (FreeCAD wire definition): An outline description of the shape.
            face1 (FreeCAD face definition): A surface description of the shape.
        """

    half_angle = arc_length / 2.  # angles are in radian here
    ho = arc_outer_radius * sin(radians(half_angle))
    hi = arc_inner_radius * sin(radians(half_angle))
    vo = arc_outer_radius * cos(radians(half_angle))
    vi = arc_inner_radius * cos(radians(half_angle))

    # Create vector points for the ends and midpoint of the arcs
    p1 = Base.Vector(0, -ho, vo)
    p2 = Base.Vector(0, ho, vo)
    p3 = Base.Vector(0,  -hi, vi)
    p4 = Base.Vector(0,  hi, vi)
    cp1 = Base.Vector(0, 0, arc_outer_radius)
    cp2 = Base.Vector(0, 0, arc_inner_radius)

    if blend_radius != 0:
        bh = blend_radius * cos(pi/4)
        bv = blend_radius * sin(pi/4)
        hdiff = abs(ho - hi)
        vdiff = abs(vo - vi)
        line_angle = atan(vdiff / hdiff)
        line_length = sqrt(hdiff**2 + vdiff**2)
        hp = blend_radius * cos(line_angle)
        vp = blend_radius * sin(line_angle)
        hap = blend_radius * cos(pi/2 - line_angle)
        vap = blend_radius * sin(pi / 2 - line_angle)
        hcp = blend_radius * cos(-pi/4 - line_angle)
        vcp = blend_radius * sin(-pi / 4 - line_angle)
        R = Units.Quantity(sqrt(blend_radius**2 + blend_radius**2), Units.Unit(1)) # Setting units to mm
        hm1 = (R- blend_radius) * sin(-pi/4 - line_angle + pi)
        vm1 = (R- blend_radius) * cos(-pi/4 - line_angle + pi)
        hm2 = (R- blend_radius) * sin(-pi / 4 - line_angle)
        vm2 = (R- blend_radius) * cos(-pi / 4 - line_angle)
        hm3 = (R- blend_radius) * sin(-pi/2 - line_angle)
        vm3 = (R- blend_radius) * cos(-pi/2 - line_angle)
        chdiff = abs(hp + hap)
        cvdiff = abs(vp - vap)
        cline_angle = atan(cvdiff / chdiff)
        cline_length = sqrt(chdiff ** 2 + cvdiff ** 2)
        hmp2 = cline_length/2 * cos(cline_angle)
        hcp2 = blend_radius * cos(cline_angle + pi/4.)
        hcp3 = blend_radius * cos(cline_angle - pi / 4.)
        vmp2 = cline_length / 2 * sin(cline_angle)
        vcp2 = blend_radius * sin(cline_angle + pi / 4.)
        vcp3 = blend_radius * sin(cline_angle - pi / 4.)
        hp11 = -ho + hp
        hp12 = -ho + hap
        hp21 = ho - hap
        hp22 = ho - hp
        hp31 = -hi + hap
        hp32 = -hi - hp
        hp41 = hi + hp
        hp42 = hi - hap
        vp11 = vo - vp
        vp12 = vo + vap
        vp21 = vo + vap
        vp22 = vo - vp
        vp31 = vi + vap
        vp32 = vi + vp
        vp41 = vi + vp
        vp42 = vi + vap
        p1_1 = Base.Vector(0, hp11, vp11)
        p1_2 = Base.Vector(0, hp12, vp12)
        p2_1 = Base.Vector(0, hp21, vp21)
        p2_2 = Base.Vector(0, hp22, vp22)
        p3_1 = Base.Vector(0, hp31, vp31)
        p3_2 = Base.Vector(0, hp32, vp32)
        p4_1 = Base.Vector(0, hp41, vp41)
        p4_2 = Base.Vector(0, hp42, vp42)
        # cp1_1 = Base.Vector(0, hp11 + hmp2 - hcp2, vp11 + vmp2 + vcp2)
        # cp2_1 = Base.Vector(0, hp22 - hmp2 + hcp2, vp22 + vmp2 + vcp2)
        cp1_1 = Base.Vector(0, -ho + hm1, vo - vm1 )
        cp2_1 = Base.Vector(0, ho + hm2  , vo + vm2)
        cp3_1 = Base.Vector(0, -hi - hm3 , vi - vm3 )
        cp4_1 = Base.Vector(0, hi + hm3 , vi - vm3 )
        # temp extra lines
        line3 = Part.LineSegment(p1_1, cp1_1)
        line4 = Part.LineSegment(cp1_1, p1_2)
        line5 = Part.LineSegment(p2_1, cp2_1)
        line6 = Part.LineSegment(cp2_1, p2_2)
        line7 = Part.LineSegment(p3_1, cp3_1)
        line8 = Part.LineSegment(cp3_1, p3_2)
        line9 = Part.LineSegment(p4_1, cp4_1)
        line10 = Part.LineSegment(cp4_1, p4_2)
        # Create curves
        arc1 = Part.Arc(p1_2, cp1, p2_1)
        arc2 = Part.Arc(p4_2, cp2, p3_1)
        arcp1 = Part.Arc(p1_1, cp1_1, p1_2)
        arcp2 = Part.Arc(p2_1, cp2_1, p2_2)
        arcp3 = Part.Arc(p3_1, cp3_1, p3_2)
        arcp4 = Part.Arc(p4_1, cp4_1, p4_2)

        # Create lines
        line1 = Part.LineSegment(p2_2, p4_1)
        line2 = Part.LineSegment(p3_2, p1_1)

        # Make a shape
        shape1 = Part.Shape([arc1, arcp2, line1, arcp4, arc2, arcp3, line2, arcp1])
        # shape1 = Part.Shape([arc1, line5, line6, line1, line9, line10, arc2, line7, line8, line2, line3, line4])

    else:
        # Create curves
        arc1 = Part.Arc(p1, cp1, p2)
        arc2 = Part.Arc(p4, cp2, p3)

        # Create lines
        line1 = Part.LineSegment(p2, p4)
        line2 = Part.LineSegment(p3, p1)

        # Make a shape
        shape1 = Part.Shape([arc1, line1, arc2, line2])

    # Make a wire outline.
    wire1 = Part.Wire(shape1.Edges)
    # Make a face.
    face1 = Part.Face(wire1)
    return wire1, face1


def make_arched_base_aperture(aperture_height, aperture_width, arc_radius):
    """ Creates a wire outline of a rectangle with an arc removed from one edge..

        Args:
            arc_radius (float): Radius of the arc.
            aperture_height (float): Total height of the aperture
            aperture_width (float): Total width of the aperture

        Returns:
            wire1 (FreeCAD wire definition): An outline description of the shape.
            face1 (FreeCAD face definition): A surface description of the shape.
        """
    # Create the initial four vertices where line meets curve.
    v1 = Base.Vector(0, aperture_height / 2., -aperture_width / 2.)
    v2 = Base.Vector(0, aperture_height / 2., aperture_width / 2.)
    v3 = Base.Vector(0, -aperture_height / 2., aperture_width / 2.)
    v4 = Base.Vector(0, -aperture_height / 2., -aperture_width / 2.)
    cv1 = Base.Vector(0, -aperture_height / 2. + arc_radius - Units.Quantity(sqrt(arc_radius ** 2 - (aperture_width ** 2) / 4), 1), 0)
    # Create lines
    line1 = Part.LineSegment(v4, v1)
    line2 = Part.LineSegment(v1, v2)
    line3 = Part.LineSegment(v2, v3)
    # Create curves
    arc1 = Part.Arc(v3, cv1, v4)
    # Make a shape
    shape1 = Part.Shape([line1, line2, line3, arc1])
    # Make a wire outline.
    wire1 = Part.Wire(shape1.Edges)
    # Make a face.
    face1 = Part.Face(wire1)

    return wire1, face1


def make_arched_base_trapezoid_aperture(aperture_height, base_width, top_width, arc_radius):
    """ Creates a wire outline of a rectangle with an arc removed from one edge..

        Args:
            arc_radius (float): Radius of the arc.
            aperture_height (float): Total height of the aperture.
            base_width (float): Total width of the base of the aperture.
            top_width (float): Total width of the top of the aperture.

        Returns:
            wire1 (FreeCAD wire definition): An outline description of the shape.
            face1 (FreeCAD face definition): A surface description of the shape.
        """
    # Create the initial four vertices where line meets curve.
    v1 = Base.Vector(0, aperture_height / 2., -top_width / 2.)
    v2 = Base.Vector(0, aperture_height / 2., top_width / 2.)
    v3 = Base.Vector(0, -aperture_height / 2., base_width / 2.)
    v4 = Base.Vector(0, -aperture_height / 2., -base_width / 2.)
    cv1 = Base.Vector(0, -aperture_height / 2. + arc_radius - sqrt(arc_radius ** 2 - (base_width ** 2) / 4), 0)
    # Create lines
    line1 = Part.LineSegment(v4, v1)
    line2 = Part.LineSegment(v1, v2)
    line3 = Part.LineSegment(v2, v3)
    # Create curves
    arc1 = Part.Arc(v3, cv1, v4)
    # arc1_edge = arc1.toShape()
    # Make a shape
    shape1 = Part.Shape([line1, line2, line3, arc1])
    # Make a wire outline.
    wire1 = Part.Wire(shape1.Edges)
    # Make a face.
    face1 = Part.Face(wire1)

    return wire1, face1


def make_cylinder_with_inserts(outer_radius, inner_radius, insert_angle, blend_radius=Units.Quantity('0 mm')):
    """ Creates a wire outline of a cylinder with inserts to a smaller cylinder for part of the radius.

        Args:
            outer_radius (float): Radius main cylinder.
            inner_radius (float): Radius of the inner surface of the inserts.
            insert_angle (float): Angle the inserts cover (each insert is 2*angle)
            blend_radius (float): The amount to smooth the edges.

        Returns:
            wire1 (FreeCAD wire definition): An outline description of the shape.
            face1 (FreeCAD face definition): A surface description of the shape.
        """
    # Create the initial four vertices where line meets curve.
    ho = outer_radius * cos(radians(insert_angle))
    hi = inner_radius * cos(radians(insert_angle))
    vo = outer_radius * sin(radians(insert_angle))
    vi = inner_radius * sin(radians(insert_angle))
    bh = blend_radius * cos(radians(insert_angle))
    bv = blend_radius * sin(radians(insert_angle))

    p1 = Base.Vector(0, ho, vo)
    p2 = Base.Vector(0, -ho, vo)
    p3 = Base.Vector(0, -hi, vi)
    p4 = Base.Vector(0, -hi, -vi)
    p5 = Base.Vector(0, -ho, -vo)
    p6 = Base.Vector(0, ho, -vo)
    p7 = Base.Vector(0, hi, -vi)
    p8 = Base.Vector(0, hi, vi)
    cp1 = Base.Vector(0, 0, outer_radius)
    cp3 = Base.Vector(0, 0, -outer_radius)
    cp2 = Base.Vector(0, -inner_radius, 0)
    cp4 = Base.Vector(0, inner_radius, 0)

    if blend_radius != 0:
        p1_1 = Base.Vector(0, ho - bh, vo - bv)
        cp1_1 = Base.Vector(0, ho - bh / 1.8, vo)
        p1_2 = Base.Vector(0, ho - bh, vo + bv)
        p2_1 = Base.Vector(0, -ho + bh, vo + bv)
        cp2_1 = Base.Vector(0, -ho + bh / 1.8, vo)
        p2_2 = Base.Vector(0, -ho + bh, vo - bv)
        p3_1 = Base.Vector(0, -hi - bh, vi + bv)
        cp3_1 = Base.Vector(0, -hi - bh / 2.5, vi)
        p3_2 = Base.Vector(0, -hi - bh / 2, vi - bv)
        p4_1 = Base.Vector(0, -hi - bh / 2, -vi + bv)
        cp4_1 = Base.Vector(0, -hi - bh / 2.5, -vi)
        p4_2 = Base.Vector(0, -hi - bh, -vi - bv)
        p5_1 = Base.Vector(0, -ho + bh, -vo + bv)
        cp5_1 = Base.Vector(0, -ho + bh / 1.8, -vo)
        p5_2 = Base.Vector(0, -ho + bh, -vo - bv)
        p6_1 = Base.Vector(0, ho - bh, -vo - bv)
        cp6_1 = Base.Vector(0, ho - bh / 1.8, -vo)
        p6_2 = Base.Vector(0, ho - bh, -vo + bv)
        p7_1 = Base.Vector(0, hi + bh, -vi - bv)
        cp7_1 = Base.Vector(0, hi + bh / 2.5, -vi)
        p7_2 = Base.Vector(0, hi + bh/2, -vi + bv)
        p8_1 = Base.Vector(0, hi + bh/2, vi - bv)
        cp8_1 = Base.Vector(0, hi + bh/ 2.5, vi)
        p8_2 = Base.Vector(0, hi + bh, vi + bv)

        # Create lines
        line1 = Part.LineSegment(p2_2, p3_1)
        line2 = Part.LineSegment(p4_2, p5_1)
        line3 = Part.LineSegment(p6_2, p7_1)
        line4 = Part.LineSegment(p8_2, p1_1)
        # Create main curves
        arc1 = Part.Arc(p1_2, cp1, p2_1)
        arc3 = Part.Arc(p5_2, cp3, p6_1)
        arc2 = Part.Arc(p3_2, cp2, p4_1)
        arc4 = Part.Arc(p7_2, cp4, p8_1)
        # Create blending curves
        arc1_1 = Part.Arc(p1_1, cp1_1, p1_2)
        arc2_1 = Part.Arc(p2_1, cp2_1, p2_2)
        arc3_1 = Part.Arc(p3_1, cp3_1, p3_2)
        arc4_1 = Part.Arc(p4_1, cp4_1, p4_2)
        arc5_1 = Part.Arc(p5_1, cp5_1, p5_2)
        arc6_1 = Part.Arc(p6_1, cp6_1, p6_2)
        arc7_1 = Part.Arc(p7_1, cp7_1, p7_2)
        arc8_1 = Part.Arc(p8_1, cp8_1, p8_2)
        # Make a shape
        shape1 = Part.Shape([arc4, arc8_1, line4, arc1_1, arc1, arc2_1, line1, arc3_1, arc2, arc4_1, line2, arc5_1, arc3, arc6_1, line3, arc7_1])
    else:
        # Create lines
        line1 = Part.LineSegment(p2, p3)
        line2 = Part.LineSegment(p4, p5)
        line3 = Part.LineSegment(p6, p7)
        line4 = Part.LineSegment(p8, p1)
        # Create curves
        arc1 = Part.Arc(p1, cp1, p2)
        arc3 = Part.Arc(p5, cp3, p6)
        arc2 = Part.Arc(p4, cp2, p3)
        arc4 = Part.Arc(p8, cp4, p7)
        # Make a shape
        shape1 = Part.Shape([arc4, line4, arc1, line1, arc2, line2, arc3, line3])

    # Make a wire outline.
    wire1 = Part.Wire(shape1.Edges)
    # Make a face.
    face1 = Part.Face(wire1)

    return wire1, face1


def make_spoked_cylinder(outer_radius, inner_radius, insert_angles, spoke_extents,  blend_radius=Units.Quantity('0 mm')):
    """ Creates a wire outline of a cylinder with inserts to a smaller cylinder for part of the radius.

        Args:
            outer_radius (float): Radius main cylinder.
            inner_radius (float): Radius of the inner surface of the inserts.
            insert_angles (list): Angle the at the centre of each spoke
            spoke_extents (list): Angular extent of each spoke
            blend_radius (float): The amount to smooth the edges.

        Returns:
            wire1 (FreeCAD wire definition): An outline description of the shape.
            face1 (FreeCAD face definition): A surface description of the shape.
        """
    # Create the initial four vertices where line meets curve.
    model_points = []
    model_edges = []
    tk = 0
    ck = 0
    for dn in range(len(insert_angles)):
        a1 = radians(insert_angles[dn] - spoke_extents[dn] / 2.)
        h1 = inner_radius * cos(a1)
        v1 = inner_radius * sin(a1)
        model_points.append(Base.Vector(0, h1, v1))
        if dn > 0:
            model_edges.append(Part.Arc(model_points[tk-2], model_points[tk-1], model_points[tk]))
        tk = tk + 1
        ck = ck + 1
        a2 = radians(insert_angles[dn] - spoke_extents[dn] / 2.)
        h2 = outer_radius * cos(a2)
        v2 = outer_radius * sin(a2)
        model_points.append(Base.Vector(0, h2, v2))
        model_edges.append(Part.LineSegment(model_points[tk-1], model_points[tk]))
        tk = tk + 1
        ck = ck + 1
        a3 = radians(insert_angles[dn])
        h3 = outer_radius * cos(a3)
        v3 = outer_radius * sin(a3)
        model_points.append(Base.Vector(0, h3, v3))
        tk = tk + 1
        a4 = radians(insert_angles[dn] + spoke_extents[dn] / 2.)
        h4 = outer_radius * cos(a4)
        v4 = outer_radius * sin(a4)
        model_points.append(Base.Vector(0, h4, v4))
        model_edges.append(Part.Arc(model_points[tk-2], model_points[tk-1], model_points[tk]))
        tk = tk + 1
        ck = ck + 1
        a5 = radians(insert_angles[dn] + spoke_extents[dn] / 2.)
        h5 = inner_radius * cos(a5)
        v5 = inner_radius * sin(a5)
        model_points.append(Base.Vector(0, h5, v5))
        model_edges.append(Part.LineSegment(model_points[tk-1], model_points[tk]))
        tk = tk + 1
        ck = ck + 1
        if dn == len(insert_angles) -1:
            a6 = radians(insert_angles[dn] + (insert_angles[0] - insert_angles[dn]) / 2. - Units.Quantity('180deg'))
        else:
            a6 = radians(insert_angles[dn] + (insert_angles[dn + 1] - insert_angles[dn]) / 2.)
        h6 = inner_radius * cos(a6)
        v6 = inner_radius * sin(a6)
        model_points.append(Base.Vector(0, h6, v6))
        if dn == len(insert_angles) - 1:
            model_edges.append(Part.Arc(model_points[tk - 1], model_points[tk], model_points[0]))
        tk = tk + 1
    shape1 = Part.Shape(model_edges)

    # Make a wire outline.
    wire1 = Part.Wire(shape1.Edges)
    # Make a face.
    face1 = Part.Face(wire1)

    return wire1, face1


def make_cylinder_with_tags(outer_radius, inner_radius, insert_angles, tag_widths):
    """ Creates a wire outline of a cylinder with inserts to a smaller cylinder for part of the radius.

        Args:
            outer_radius (float): Radius main cylinder.
            inner_radius (float): Radius of the inner surface of the inserts.
            insert_angles (list): Angle the at the centre of each spoke
            tag_widths (list): extent of each tag

        Returns:
            wire1 (FreeCAD wire definition): An outline description of the shape.
            face1 (FreeCAD face definition): A surface description of the shape.
        """
    # Create the initial four vertices where line meets curve.
    model_points = []
    model_edges = []
    tk = 0
    for dn in range(len(insert_angles)):
        d1 = inner_radius - Units.Quantity(sqrt(inner_radius * inner_radius - (tag_widths[dn] * tag_widths[dn]) / 4.), 1)
        d2 = outer_radius - Units.Quantity(sqrt(outer_radius * outer_radius - (tag_widths[dn] * tag_widths[dn]) / 4.), 1)
        top_corner_height = outer_radius - d2
        bottom_corner_height = inner_radius - d1
        h1, v1 = rotate_cartesian(tag_widths[dn] / 2., bottom_corner_height, insert_angles[dn])
        model_points.append(Base.Vector(0, h1, v1))
        if dn > 0:
            model_edges.append(Part.ArcOfCircle(model_points[tk-2], model_points[tk-1], model_points[tk]))
            model_edges[-1] = force_short_arc(p1=model_points[tk - 2], p2=model_points[tk - 1], edge=model_edges[-1])
        tk = tk + 1
        h2, v2 = rotate_cartesian(tag_widths[dn] / 2., top_corner_height, insert_angles[dn])
        model_points.append(Base.Vector(0, h2, v2))
        model_edges.append(Part.LineSegment(model_points[tk-1], model_points[tk]))
        tk = tk + 1
        h3 = outer_radius * sin(-radians(insert_angles[dn]))
        v3 = outer_radius * cos(-radians(insert_angles[dn]))
        model_points.append(Base.Vector(0, h3, v3))
        tk = tk + 1
        h4, v4 = rotate_cartesian(-tag_widths[dn] / 2., top_corner_height, insert_angles[dn])
        model_points.append(Base.Vector(0, h4, v4))
        model_edges.append(Part.ArcOfCircle(model_points[tk-2], model_points[tk-1], model_points[tk]))
        model_edges[-1] = force_short_arc(p1=model_points[tk-2], p2=model_points[tk-1], edge=model_edges[-1])
        tk = tk + 1
        h5, v5 = rotate_cartesian(-tag_widths[dn] / 2., bottom_corner_height, insert_angles[dn])
        model_points.append(Base.Vector(0, h5, v5))
        model_edges.append(Part.LineSegment(model_points[tk-1], model_points[tk]))
        tk = tk + 1
        if dn == len(insert_angles) - 1:
            a6 = radians(insert_angles[dn] + (- insert_angles[dn] + insert_angles[0]) / 2. + Units.Quantity('180deg'))
        else:
            a6 = radians(insert_angles[dn] + (insert_angles[dn + 1] - insert_angles[dn]) / 2.)
        h6 = inner_radius * sin(-a6)
        v6 = inner_radius * cos(-a6)
        model_points.append(Base.Vector(0, h6, v6))
        if dn == len(insert_angles) - 1:
            model_edges.append(Part.ArcOfCircle(model_points[tk - 1], model_points[tk], model_points[0]))
            # model_edges[-1] = force_short_arc(p1=model_points[tk - 2], p2=model_points[tk - 1], edge=model_edges[-1])
        tk = tk + 1
        # print('h',dn+1,'=[ ', h1, h2, h3, h4, h5, h6,'];')
        # print('v',dn+1,'=[ ', v1, v2, v3, v4, v5, v6,'];')

    shape1 = Part.Shape(model_edges)
    # Make a wire outline.
    wire1 = Part.Wire(shape1.Edges)
    # Make a face.
    face1 = Part.Face(wire1)
    return wire1, face1


def make_polygon_with_tags(inner_radius, tag_radii, insert_angles, tag_widths):
    """ Creates a wire outline of a cylinder with inserts to a smaller cylinder for part of the radius.

        Args:
            tag_radii (list): Radius of each tag.
            inner_radius (float): Radius of the inner surface of the inserts.
            insert_angles (list): Angle the at the centre of each spoke
            tag_widths (list): extent of each tag

        Returns:
            wire1 (FreeCAD wire definition): An outline description of the shape.
            face1 (FreeCAD face definition): A surface description of the shape.
        """
    # Create the initial four vertices where line meets curve.
    model_points = []
    model_edges = []
    tk = 0
    for dn in range(len(insert_angles)):
        d1 = inner_radius - Units.Quantity(sqrt(inner_radius * inner_radius - (tag_widths[dn] * tag_widths[dn]) / 4.), 1)
        d2 = tag_radii[dn] - Units.Quantity(sqrt(tag_radii[dn] * tag_radii[dn] - (tag_widths[dn] * tag_widths[dn]) / 4.), 1)
        top_corner_height = tag_radii[dn] - d2
        bottom_corner_height = inner_radius - d1
        h1, v1 = rotate_cartesian(tag_widths[dn] / 2., bottom_corner_height, insert_angles[dn])
        model_points.append(Base.Vector(0, h1, v1))
        if dn > 0:
            model_edges.append(Part.LineSegment(model_points[tk-1], model_points[tk]))
        tk = tk + 1
        h2, v2 = rotate_cartesian(tag_widths[dn] / 2., top_corner_height, insert_angles[dn])
        model_points.append(Base.Vector(0, h2, v2))
        model_edges.append(Part.LineSegment(model_points[tk-1], model_points[tk]))
        tk = tk + 1
        h3 = tag_radii[dn] * sin(-radians(insert_angles[dn]))
        v3 = tag_radii[dn] * cos(-radians(insert_angles[dn]))
        model_points.append(Base.Vector(0, h3, v3))
        tk = tk + 1
        h4, v4 = rotate_cartesian(-tag_widths[dn] / 2., top_corner_height, insert_angles[dn])
        model_points.append(Base.Vector(0, h4, v4))
        model_edges.append(Part.ArcOfCircle(model_points[tk-2], model_points[tk-1], model_points[tk]))
        model_edges[-1] = force_short_arc(p1=model_points[tk-2], p2=model_points[tk-1], edge=model_edges[-1])
        tk = tk + 1
        h5, v5 = rotate_cartesian(-tag_widths[dn] / 2., bottom_corner_height, insert_angles[dn])
        model_points.append(Base.Vector(0, h5, v5))
        model_edges.append(Part.LineSegment(model_points[tk-1], model_points[tk]))
        tk = tk + 1
        if dn == len(insert_angles) - 1:
            model_edges.append(Part.LineSegment(model_points[tk-1], model_points[0]))

    shape1 = Part.Shape(model_edges)
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
    curve1 = Part.Circle(Base.Vector(0, 0, 0), Base.Vector(1, 0, 0), aperture_radius)
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
    line1 = Part.LineSegment(v1, v2)
    line2 = Part.LineSegment(v2, v3)
    line3 = Part.LineSegment(v3, v4)
    line4 = Part.LineSegment(v4, v5)
    line5 = Part.LineSegment(v5, v6)
    line6 = Part.LineSegment(v6, v7)
    line7 = Part.LineSegment(v7, v8)
    line8 = Part.LineSegment(v8, v1)
    # Make a shape
    shape1 = Part.Shape([line1, line2, line3, line4, line5, line6, line7, line8])
    # Make a wire outline.
    wire1 = Part.Wire(shape1.Edges)
    # Make a face.
    face1 = Part.Face(wire1)
    return wire1, face1


def make_octagonal_aperture_with_keyholes_and_antichamber(aperture_height, tb_width,
                                                          ib_oct_width, ob_oct_width,
                                                          ib_keyhole_height, ib_keyhole_width,
                                                          ob_keyhole_height, ob_keyhole_width,
                                                          antichamber_taper_width, antichamber_height,
                                                          antichamber_width):
    """ Creates a wire outline of a symmetric octagon specified by 4 inputs.
    aperture_height and aperture_width are the full height and width (the same as if it were a rectangle)
    side_length and tb_length specify the lengths of the top/ bottom and sides
    and so implicitly allow the diagonals to be defined.

    Args:
        aperture_height (float): Total height of the octagon.
        tb_width (float): Length of the horizontal sides.
        ib_oct_width (float): width of the angled side of the octagon.
        ob_oct_width (float): width of the angled side of the octagon.
        ib_keyhole_height (float): height of the inboard keyhole slot.
        ib_keyhole_width (float): width of the inboard keyhole slot.
        ob_keyhole_height (float): height of the outboard keyhole slot.
        ob_keyhole_width (float): width of the outboard keyhole slot.
        antichamber_taper_width (float): width of the taper between the inboard slot and the antichamber.
        antichamber_width (float): width of the antichamber.
        antichamber_height (float): height of the antichamber.

    Returns:
        wire1 (FreeCAD wire definition): An outline description of the shape.
        face1 (FreeCAD face definition): A surface description of the shape.
    """

    # Create the initial vertices.
    x1 = -tb_width / 2. - ob_oct_width - ob_keyhole_width
    x2 = -tb_width / 2. - ob_oct_width
    x3 = -tb_width / 2.
    x4 = tb_width / 2.
    x5 = tb_width / 2. + ib_oct_width
    x6 = tb_width / 2. + ib_oct_width + ib_keyhole_width
    x7 = tb_width / 2. + ib_oct_width + ib_keyhole_width + antichamber_taper_width
    x8 = tb_width / 2. + ib_oct_width + ib_keyhole_width + antichamber_taper_width + antichamber_width
    y1 = ob_keyhole_height / 2.
    y2 = aperture_height / 2.
    y3 = ib_keyhole_height / 2.
    y4 = antichamber_height / 2.

    v1 = Base.Vector(0, y1, x1)
    v2 = Base.Vector(0, y1, x2)
    v3 = Base.Vector(0, y2, x3)
    v4 = Base.Vector(0, y2, x4)
    v5 = Base.Vector(0, y3, x5)
    v6 = Base.Vector(0, y3, x6)
    v7 = Base.Vector(0, y4, x7)
    v8 = Base.Vector(0, y4, x8)
    v9 = Base.Vector(0, -y4, x8)
    v10 = Base.Vector(0, -y4, x7)
    v11 = Base.Vector(0, -y3, x6)
    v12 = Base.Vector(0, -y3, x5)
    v13 = Base.Vector(0, -y2, x4)
    v14 = Base.Vector(0, -y2, x3)
    v15 = Base.Vector(0, -y1, x2)
    v16 = Base.Vector(0, -y1, x1)
    # Create lines
    line1 = Part.LineSegment(v1, v2)
    line2 = Part.LineSegment(v2, v3)
    line3 = Part.LineSegment(v3, v4)
    line4 = Part.LineSegment(v4, v5)
    line5 = Part.LineSegment(v5, v6)
    line6 = Part.LineSegment(v6, v7)
    line7 = Part.LineSegment(v7, v8)
    line8 = Part.LineSegment(v8, v9)
    line9 = Part.LineSegment(v9, v10)
    line10 = Part.LineSegment(v10, v11)
    line11 = Part.LineSegment(v11, v12)
    line12 = Part.LineSegment(v12, v13)
    line13 = Part.LineSegment(v13, v14)
    line14 = Part.LineSegment(v14, v15)
    line15 = Part.LineSegment(v15, v16)
    line16 = Part.LineSegment(v16, v1)
    # Make a shape
    shape1 = Part.Shape([line1, line2, line3, line4, line5, line6, line7, line8, line9,
                         line10, line11, line12, line13, line14, line15, line16])
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

    el1 = Part.Ellipse(Base.Vector(0, 0, 0), a, b)
    # Make a shape
    shape1 = el1.toShape()
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


def make_taper(aperture1, aperture2, taper_length, loc=(0, 0, 0), rotation_angles=(0, 0, 0), aperture_xy_offset=(0, 0)):
    """Takes two aperture descriptions and creates a taper between them.
     The centre of the face of aperture1 will be at loc and rotations will happen about that point.
     Assume both apertures are initially centred on (0,0,0)

     Args:
        aperture1 (FreeCad wire): Outline of starting aperture.
        aperture2 (FreeCad wire): Outline of ending aperture.
        taper_length (float): distance between apertures.
        loc (tuple) : The co ordinates of the final location of the centre of aperture1.
        rotation_angles (tuple) : The angles to rotate about in the three cartesian directions.
        aperture_xy_offset(tuple): The translational offsets between teh two apertures.

     Returns:
        taper (FreeCAD shape): A model of the shape.
    """
    aperture2.translate(Base.Vector(taper_length, aperture_xy_offset[0], aperture_xy_offset[1]))
    taper = Part.makeLoft([aperture1, aperture2], True, False, False)
    taper.rotate(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), rotation_angles[2])    # Rotate around Z
    taper.rotate(Base.Vector(0, 0, 0), Base.Vector(1, 0, 0), rotation_angles[0])    # Rotate around X
    taper.rotate(Base.Vector(0, 0, 0), Base.Vector(0, 1, 0), rotation_angles[1])    # Rotate around Y
    taper.translate(Base.Vector(loc[0], loc[1], loc[2]))  # Move to be centred on loc
    # Returning the aperture to it's original location so that it is where other functions expect.
    aperture2.translate(Base.Vector(-taper_length, 0, 0))
    return taper


def force_short_arc(p1, p2, edge):
    edge.parameter(p1), edge.FirstParameter
    edge.parameter(p2), edge.LastParameter
    if edge.LastParameter - edge.FirstParameter > pi:
        edge = Part.ArcOfCircle(edge.Circle, edge.LastParameter, 2 * pi + edge.FirstParameter)
    return edge


def rotate_cartesian(x, y, angle):
    r = Units.Quantity(sqrt(x * x + y * y), 1)  # Forcing length units
    a = atan2(y, x)
    a2 = a + radians(angle)
    x_out = r * cos(a2)
    y_out = r * sin(a2)
    return x_out, y_out


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
        # print('Fixed normals', fixed_normals)
        # print('Fixed manifolds', fixed_manifolds)
        # print('fixed indicies', fixed_indicies)
        # print('fixed degenerations', fixed_degenerations)
        # print('fixed surface folds', fixed_folds)
        # print('fixed duplicated facets', fixed_facets)
        # print('fixed duplicated points', fixed_points)
        # print('fixed self intersections', fixed_intersections)
        # status = [fixed_normals, fixed_manifolds, fixed_indicies, fixed_degenerations,
        #           fixed_folds, fixed_facets, fixed_points, fixed_intersections]
        # new_status = [True for i in status if i is None]
        # if len(status) == len(new_status):
        #     print('Nothing to fix')
        #     return
        # elif cycles == ncycles - 1:
        #     print('Max number of cycles reached')
        #     return
        # else:
        #     print('One more loop')


def generate_output_files(root_loc, model_name, parts_list, input_parameters, tag, solvertype='standard',
                          mesh_resolution=5, just_cad=0):
    """Takes the dictionary of parts, converts them to meshes.
    Saves the resulting meshes in both binary and ascii STL format. (ECHO needs binary, GdfidL needs ASCII).
     Also saves the Geometry in a freeCAD document.

     Args:
            root_loc (str): location of the folder the results are writen to.
            model_name (str): name of the model.
            parts_list (dict): dictionary of shapes used to construct the model.
            input_parameters (dict): dictionary of input parameters used to make the model.
            tag (str): Unique identifier string for a particular model iteration.
            solvertype(str): selects which meshing solver to use (standard or netgen).
            mesh_resolution (int): the resolution of hte meshing (equivalent to the Fineness parameter in meshFromShape)
            just_cad(int): selects if the STL files are generated. Early in the design it can be useful to turn them off
    """
    document_name = ''.join([model_name, '_model__', tag])
    output_loc = os.path.join(root_loc, ''.join([model_name, '_', tag]))
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
        my_object = doc.addObject("Part::Feature", part_name)
        my_object.Shape = parts_list[part]
    doc.recompute()
    # Saving to a short named temp file then doing an OS rename in order to avoid path length limitation issues
    # when saving the temp file.
    doc.saveAs(os.path.join(output_loc, ''.join(['A', '.FCStd'])))
    outfilename = os.path.join(output_loc, ''.join([model_name, '_', tag, '.FCStd']))
    if os.path.exists(outfilename):
        os.remove(outfilename)
    os.rename(os.path.join(output_loc, ''.join(['A', '.FCStd'])), outfilename)

    if just_cad == 0:
        for part in part_labels:
            part_name = '-'.join([model_name, part])
            # Generate a mesh from the shape.
            mesh_name = ''.join([part_name, ' (Meshed)'])
            print(''.join(['generating STL mesh for ', mesh_name]))
            if solvertype == 'netgen':
                # Using the netgen mesher
                m1 = MeshPart.meshFromShape(Shape=parts_list[part], GrowthRate=0.1, SegPerEdge=mesh_resolution,
                                            SegPerRadius=mesh_resolution, SecondOrder=0, Optimize=1, AllowQuad=0)
            elif solvertype == 'standard':
                # Using standard mesher
                m1 = MeshPart.meshFromShape(Shape=parts_list[part], LinearDeflection=0.01, AngularDeflection=0.0174533,
                                            Relative=True)
            else:
                raise ValueError('solver type should be netgen or standard')

            clean_stl(m1)

            mymesh = doc.addObject("Mesh::Feature", "Mesh")
            mymesh.Mesh = m1
            mymesh.Label = mesh_name
            mymesh.Mesh.write(os.path.join(output_loc, 'ascii', ''.join([part_name, '.stl'])), "AST", mesh_name)

    FreeCAD.closeDocument(document_name)

    paramfilename = os.path.join(output_loc, 'A.txt')
    parameter_file_name = os.path.join(output_loc, ''.join([model_name, '_', tag, '_parameters.txt']))
    if os.path.exists(paramfilename):
        os.remove(paramfilename)
    if os.path.exists(parameter_file_name):
        os.remove(parameter_file_name)

    param_file = open(paramfilename, 'w')
    for name, value in input_parameters.items():
        param_file.write(''.join([name, ' : ', str(value), '\n']))
    param_file.close()

    os.rename(paramfilename, parameter_file_name)
