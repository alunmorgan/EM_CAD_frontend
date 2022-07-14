from math import asin, atan, cos, pi, radians, sin, sqrt
from FreeCAD import Base, Units
import Part
from FreeCAD_geometry_generation.freecad_operations import rotate_cartesian

# This has to run using the FreeCAD built in python interpreter.


def make_racetrack_aperture(aperture_height, aperture_width):
    """Creates a wire outline of a symmetric racetrack.
    aperture_height and aperture_width are the full height and width
    (the same as if it were a rectangle).
    The end curves are defined as 180 degree arcs.

    Args:
        aperture_height (float): Total height of the aperture
        aperture_width (float): Total width of the aperture

    Returns:
        wire1 (FreeCAD wire definition): An outline description of the shape.
        face1 (FreeCAD face definition): A surface description of the shape.
    """
    # Create the initial four vertices where line meets curve.
    v1 = Base.Vector(
        0, aperture_height / 2.0, (-aperture_width + aperture_height) / 2.0
    )
    v2 = Base.Vector(0, aperture_height / 2.0, (aperture_width - aperture_height) / 2.0)
    v3 = Base.Vector(
        0, -aperture_height / 2.0, (aperture_width - aperture_height) / 2.0
    )
    v4 = Base.Vector(
        0, -aperture_height / 2.0, (-aperture_width + aperture_height) / 2.0
    )
    # Create curves
    curve1 = Part.Circle(
        Base.Vector(0, 0, (-aperture_width + aperture_height) / 2.0),
        Base.Vector(1, 0, 0),
        aperture_height / 2.0,
    )
    arc1 = Part.Arc(curve1, pi / 2.0, 3 * pi / 2.0)  # angles are in radian here
    curve2 = Part.Circle(
        Base.Vector(0, 0, (aperture_width - aperture_height) / 2.0),
        Base.Vector(1, 0, 0),
        aperture_height / 2.0,
    )
    arc2 = Part.Arc(curve2, -pi / 2.0, -3 * pi / 2.0)  # angles are in radian here
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
    """Creates a wire outline of a rectangle.
    aperture_height and aperture_width are the full height and width.


    Args:
        aperture_height (float): Total height of the aperture
        aperture_width (float): Total width of the aperture

    Returns:
        wire1 (FreeCAD wire definition): An outline description of the shape.
        face1 (FreeCAD face definition): A surface description of the shape.
    """
    # Create the initial four vertices where line meets curve.
    v1 = Base.Vector(0, aperture_height / 2.0, -aperture_width / 2.0)
    v2 = Base.Vector(0, aperture_height / 2.0, aperture_width / 2.0)
    v3 = Base.Vector(0, -aperture_height / 2.0, aperture_width / 2.0)
    v4 = Base.Vector(0, -aperture_height / 2.0, -aperture_width / 2.0)
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


def make_rounded_rectangle_aperture(aperture_height, aperture_width, corner_radius):
    """Creates a wire outline of a rectangle.
    aperture_height and aperture_width are the full height and width.


    Args:
        aperture_height (float): Total height of the aperture
        aperture_width (float): Total width of the aperture

    Returns:
        wire1 (FreeCAD wire definition): An outline description of the shape.
        face1 (FreeCAD face definition): A surface description of the shape.
    """
    # Create the initial four vertices where line meets curve.
    v1 = Base.Vector(0, aperture_height / 2.0 - corner_radius, -aperture_width / 2.0)
    v2 = Base.Vector(0, aperture_height / 2.0, -aperture_width / 2.0 + corner_radius)
    v3 = Base.Vector(0, aperture_height / 2.0, aperture_width / 2.0 - corner_radius)
    v4 = Base.Vector(0, aperture_height / 2.0 - corner_radius, aperture_width / 2.0)
    v5 = Base.Vector(0, -aperture_height / 2.0 + corner_radius, aperture_width / 2.0)
    v6 = Base.Vector(0, -aperture_height / 2.0, aperture_width / 2.0 - corner_radius)
    v7 = Base.Vector(0, -aperture_height / 2.0, -aperture_width / 2.0 + corner_radius)
    v8 = Base.Vector(0, -aperture_height / 2.0 + corner_radius, -aperture_width / 2.0)
    # Create lines
    line1 = Part.LineSegment(v2, v3)
    line2 = Part.LineSegment(v4, v5)
    line3 = Part.LineSegment(v6, v7)
    line4 = Part.LineSegment(v8, v1)

    centre_curve_offset = corner_radius * (1 - 1 / sqrt(2))
    vc1 = Base.Vector(
        0,
        aperture_height / 2.0 - centre_curve_offset,
        -aperture_width / 2.0 + centre_curve_offset,
    )
    vc2 = Base.Vector(
        0,
        aperture_height / 2.0 - centre_curve_offset,
        aperture_width / 2.0 - centre_curve_offset,
    )
    vc3 = Base.Vector(
        0,
        -aperture_height / 2.0 + centre_curve_offset,
        aperture_width / 2.0 - centre_curve_offset,
    )
    vc4 = Base.Vector(
        0,
        -aperture_height / 2.0 + centre_curve_offset,
        -aperture_width / 2.0 + centre_curve_offset,
    )

    arc1 = Part.Arc(v1, vc1, v2)
    arc2 = Part.Arc(v3, vc2, v4)
    arc3 = Part.Arc(v5, vc3, v6)
    arc4 = Part.Arc(v7, vc4, v8)
    # Make a shape
    shape1 = Part.Shape([arc1, line1, arc2, line2, arc3, line3, arc4, line4])
    # Make a wire outline.
    wire1 = Part.Wire(shape1.Edges)
    # Make a face.
    face1 = Part.Face(wire1)
    return wire1, face1


def make_keyhole_aperture(pipe_radius, keyhole_height, keyhole_width):
    """Creates a wire outline of a circular pipe with a keyhole extension on the side.
    aperture_height and aperture_width are the full height and width
    (the same as if it were a rectangle).
    The end curves are defined as 180 degree arcs.

    Args:
        pipe_radius (Base.Unit): Radius of the main beam pipe.
        keyhole_height (Base.Unit): Total height of the keyhole slot.
        keyhole_width (Base.Unit): Total width of the keyhole slot.

    Returns:
        wire1 (FreeCAD wire definition): An outline description of the shape.
        face1 (FreeCAD face definition): A surface description of the shape.
    """
    # X intersection of keyhole with pipe.
    x_intersection = Units.Quantity(
        sqrt(pipe_radius ** 2 - (keyhole_height / 2.0) ** 2), 1
    )
    # Create the initial four vertices for the lines.
    v1 = Base.Vector(0, keyhole_height / 2.0, x_intersection)
    v2 = Base.Vector(
        0, keyhole_height / 2.0, x_intersection + keyhole_width - keyhole_height / 2
    )
    v3 = Base.Vector(
        0, -keyhole_height / 2.0, x_intersection + keyhole_width - keyhole_height / 2
    )
    v4 = Base.Vector(0, -keyhole_height / 2.0, x_intersection)
    v5 = Base.Vector(0, 0, x_intersection + keyhole_width)
    # Create lines
    line1 = Part.LineSegment(v1, v2)
    arc2 = Part.Arc(v2, v5, v3)
    line3 = Part.LineSegment(v3, v4)

    # angle at which the keyhole intersects the pipe.
    half_angle = asin(keyhole_height / (2 * pipe_radius))
    # Create curves
    curve1 = Part.Circle(Base.Vector(0, 0, 0), Base.Vector(1, 0, 0), pipe_radius)
    arc1 = Part.Arc(
        curve1, half_angle, (2 * pi) - half_angle
    )  # angles are in radian here

    # Make a shape
    shape1 = Part.Shape([arc1, line1, arc2, line3])
    # Make a wire outline.
    wire1 = Part.Wire(shape1.Edges)
    # Make a face.
    face1 = Part.Face(wire1)
    return wire1, face1


def make_keyhole_aperture_flat_end(pipe_radius, keyhole_height, keyhole_width):
    """Creates a wire outline of a circular pipe with a keyhole extension on the side.
    aperture_height and aperture_width are the full height and width
    (the same as if it were a rectangle).
    The end curves are defined as 180 degree arcs.

    Args:
        pipe_radius (Base.Unit): Radius of the main beam pipe.
        keyhole_height (Base.Unit): Total height of the keyhole slot.
        keyhole_width (Base.Unit): Total width of the keyhole slot.

    Returns:
        wire1 (FreeCAD wire definition): An outline description of the shape.
        face1 (FreeCAD face definition): A surface description of the shape.
    """
    # X intersection of keyhole with pipe.
    x_intersection = Units.Quantity(
        sqrt(pipe_radius ** 2 - (keyhole_height / 2.0) ** 2), 1
    )
    # Create the initial four vertices for the lines.
    v1 = Base.Vector(0, keyhole_height / 2.0, x_intersection)
    v2 = Base.Vector(0, keyhole_height / 2.0, keyhole_width)
    v3 = Base.Vector(0, -keyhole_height / 2.0, keyhole_width)
    v4 = Base.Vector(0, -keyhole_height / 2.0, x_intersection)
    v5 = Base.Vector(0, 0, x_intersection + keyhole_width)
    # Create lines
    line1 = Part.LineSegment(v1, v2)
    line2 = Part.LineSegment(v2, v3)
    line3 = Part.LineSegment(v3, v4)

    # angle at which the keyhole intersects the pipe.
    half_angle = asin(keyhole_height / (2 * pipe_radius))
    # Create curves
    curve1 = Part.Circle(Base.Vector(0, 0, 0), Base.Vector(1, 0, 0), pipe_radius)
    arc1 = Part.Arc(
        curve1, half_angle, (2 * pi) - half_angle
    )  # angles are in radian here

    # Make a shape
    shape1 = Part.Shape([arc1, line1, line2, line3])
    # Make a wire outline.
    wire1 = Part.Wire(shape1.Edges)
    # Make a face.
    face1 = Part.Face(wire1)
    return wire1, face1


def make_arc_aperture(
    arc_inner_radius, arc_outer_radius, arc_length, blend_radius=Units.Quantity("0 mm")
):
    """Creates a wire outline of an arc.

    Args:
        arc_inner_radius (float): Radius of the inside edge of the arc.
        arc_outer_radius (float): Radius of the outside edge of the arc.
        arc_length (float): The length of the arc (measured in angle in radians)
        blend_radius (float): The amount to smooth the edges.

    Returns:
        wire1 (FreeCAD wire definition): An outline description of the shape.
        face1 (FreeCAD face definition): A surface description of the shape.
    """

    half_angle = arc_length / 2.0  # angles are in radian here
    ho = arc_outer_radius * sin(radians(half_angle))
    hi = arc_inner_radius * sin(radians(half_angle))
    vo = arc_outer_radius * cos(radians(half_angle))
    vi = arc_inner_radius * cos(radians(half_angle))

    # Create vector points for the ends and midpoint of the arcs
    p1 = Base.Vector(0, -ho, vo)
    p2 = Base.Vector(0, ho, vo)
    p3 = Base.Vector(0, -hi, vi)
    p4 = Base.Vector(0, hi, vi)
    cp1 = Base.Vector(0, 0, arc_outer_radius)
    cp2 = Base.Vector(0, 0, arc_inner_radius)

    if blend_radius != 0:
        # bh = blend_radius * cos(pi / 4)
        # bv = blend_radius * sin(pi / 4)
        hdiff = abs(ho - hi)
        vdiff = abs(vo - vi)
        line_angle = atan(vdiff / hdiff)
        # line_length = sqrt(hdiff ** 2 + vdiff ** 2)
        hp = blend_radius * cos(line_angle)
        vp = blend_radius * sin(line_angle)
        hap = blend_radius * cos(pi / 2 - line_angle)
        vap = blend_radius * sin(pi / 2 - line_angle)
        # hcp = blend_radius * cos(-pi / 4 - line_angle)
        # vcp = blend_radius * sin(-pi / 4 - line_angle)
        R = Units.Quantity(
            sqrt(blend_radius ** 2 + blend_radius ** 2), Units.Unit(1)
        )  # Setting units to mm
        hm1 = (R - blend_radius) * sin(-pi / 4 - line_angle + pi)
        vm1 = (R - blend_radius) * cos(-pi / 4 - line_angle + pi)
        hm2 = (R - blend_radius) * sin(-pi / 4 - line_angle)
        vm2 = (R - blend_radius) * cos(-pi / 4 - line_angle)
        hm3 = (R - blend_radius) * sin(-pi / 2 - line_angle)
        vm3 = (R - blend_radius) * cos(-pi / 2 - line_angle)
        # chdiff = abs(hp + hap)
        # cvdiff = abs(vp - vap)
        # cline_angle = atan(cvdiff / chdiff)
        # cline_length = sqrt(chdiff ** 2 + cvdiff ** 2)
        # hmp2 = cline_length / 2 * cos(cline_angle)
        # hcp2 = blend_radius * cos(cline_angle + pi / 4.0)
        # hcp3 = blend_radius * cos(cline_angle - pi / 4.0)
        # vmp2 = cline_length / 2 * sin(cline_angle)
        # vcp2 = blend_radius * sin(cline_angle + pi / 4.0)
        # vcp3 = blend_radius * sin(cline_angle - pi / 4.0)
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
        cp1_1 = Base.Vector(0, -ho + hm1, vo - vm1)
        cp2_1 = Base.Vector(0, ho + hm2, vo + vm2)
        cp3_1 = Base.Vector(0, -hi - hm3, vi - vm3)
        cp4_1 = Base.Vector(0, hi + hm3, vi - vm3)
        # temp extra lines
        # line3 = Part.LineSegment(p1_1, cp1_1)
        # line4 = Part.LineSegment(cp1_1, p1_2)
        # line5 = Part.LineSegment(p2_1, cp2_1)
        # line6 = Part.LineSegment(cp2_1, p2_2)
        # line7 = Part.LineSegment(p3_1, cp3_1)
        # line8 = Part.LineSegment(cp3_1, p3_2)
        # line9 = Part.LineSegment(p4_1, cp4_1)
        # line10 = Part.LineSegment(cp4_1, p4_2)
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
        # shape1 = Part.Shape([arc1, line5, line6, line1, line9, line10, arc2, line7,
        # line8, line2, line3, line4])

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


def make_arc_aperture_with_notched_flat(
    arc_inner_radius,
    arc_outer_radius,
    arc_length,
    flat_width,
    notch_height,
    notch_depth,
    notch_blend_radius=Units.Quantity("0 mm"),
    blend_radius=Units.Quantity("0 mm"),
):
    """Creates a wire outline of an arc with a flat section on the inner profile. In that flat section there is a cut out.

    Args:
        arc_inner_radius (float): Radius of the inside edge of the arc.
        arc_outer_radius (float): Radius of the outside edge of the arc.
        arc_length (float): The length of the arc (measured in angle in radians)
        flat_width (float): The width of the inner surface which is flat.
        notch_height (float): The height of the cut out.
        notch_depth (float): The depth of the cut out.
        notch_blend_radius (float): the amount of smoothing between the inner flat and the cut out.
        blend_radius (float): The amount to smooth the edges on the curved sections.


    Returns:
        wire1 (FreeCAD wire definition): An outline description of the shape.
        face1 (FreeCAD face definition): A surface description of the shape.
    """

    half_angle = arc_length / 2.0  # angles are in radian here
    flat_angle = Units.Quantity(str(atan((flat_width /2.0) / arc_inner_radius) * 180 / pi)+"deg")
    blend_angle = Units.Quantity(str(atan(blend_radius / (arc_inner_radius + (arc_outer_radius - arc_inner_radius)/2.0)) * 180 / pi)+"deg")
    ho = arc_outer_radius * sin(radians(half_angle))
    vo = arc_outer_radius * cos(radians(half_angle))
    hi = arc_inner_radius * sin(radians(half_angle))
    vi = arc_inner_radius * cos(radians(half_angle))
    hif = arc_inner_radius * sin(radians(flat_angle))
    vif = arc_inner_radius * cos(radians(flat_angle))
    hifcp = arc_inner_radius * sin(
        radians(flat_angle + 0.5 * (half_angle - flat_angle))
    )
    vifcp = arc_inner_radius * cos(
        radians(flat_angle + 0.5 * (half_angle - flat_angle))
    )
    # Create vector points for the ends and midpoint of the arcs
    p1 = Base.Vector(0, -ho, vo)
    p2 = Base.Vector(0, ho, vo)
    p3 = Base.Vector(0, hi, vi)
    p4 = Base.Vector(0, hif, vif)
    p5_1 = Base.Vector(0, notch_height / 2.0 + notch_blend_radius, vif)
    p5_2 = Base.Vector(0, notch_height / 2.0, vif + notch_blend_radius)
    p6 = Base.Vector(0, notch_height / 2.0, arc_inner_radius + notch_depth - notch_height / 2.0)
    p7 = Base.Vector(0, -notch_height / 2.0, arc_inner_radius + notch_depth - notch_height / 2.0)
    p8_1 = Base.Vector(0, -notch_height / 2.0, vif + notch_blend_radius)
    p8_2 = Base.Vector(0, -notch_height / 2.0 - notch_blend_radius, vif)
    p9 = Base.Vector(0, -hif, vif)
    p10 = Base.Vector(0, -hi, vi)
    cp1 = Base.Vector(0, 0, arc_outer_radius)
    cp2 = Base.Vector(0, hifcp, vifcp)
    cp3 = Base.Vector(0, 0, arc_inner_radius + notch_depth)
    cp4 = Base.Vector(0, -hifcp, vifcp)
    cp5 = Base.Vector(0, notch_height / 2.0 + notch_blend_radius * (1 - 1 / sqrt(2)), vif + notch_blend_radius  * (1- 1 / sqrt(2)))
    cp6 = Base.Vector(0, -notch_height / 2.0 - notch_blend_radius * (1 - 1 / sqrt(2)), vif + notch_blend_radius * (1 - 1 / sqrt(2)))

    # Create curves
    arc1 = Part.Arc(p1, cp1, p2)
    arc2 = Part.Arc(p3, cp2, p4)
    arc3 = Part.Arc(p6, cp3, p7)
    arc4 = Part.Arc(p9, cp4, p10)
    arc5 = Part.Arc(p5_1, cp5, p5_2)
    arc6 = Part.Arc(p8_1, cp6, p8_2)

    # Create lines
    line1 = Part.LineSegment(p2, p3)
    line2 = Part.LineSegment(p4, p5_1)
    line3 = Part.LineSegment(p5_2, p6)
    line4 = Part.LineSegment(p7, p8_1)
    line5 = Part.LineSegment(p8_2, p9)
    line6 = Part.LineSegment(p10, p1)

    if blend_radius == 0:
        # Make a shape
        shape1 = Part.Shape(
            [arc1, line1, arc2, line2, arc5, line3, arc3, line4, arc6, line5, arc4, line6]
        )
    else:
        hp1_1 = -ho + blend_radius * sin(radians(half_angle))
        vp1_1 = vo - blend_radius * cos(radians(half_angle))
        p1_1 = Base.Vector(0, hp1_1, vp1_1)
        #hp1_2 = -ho + blend_radius * sin(radians(half_angle))
        #vp1_2 = vo + blend_radius * cos(radians(half_angle))
        hp1_2 = -arc_outer_radius * sin(radians(half_angle - blend_angle))
        vp1_2 = arc_outer_radius * cos(radians(half_angle - blend_angle))
        p1_2 = Base.Vector(0, hp1_2, vp1_2)
        p1_centre_h = hp1_1 + 0.5 * abs(hp1_1 - hp1_2)
        p1_centre_v = vp1_1 + 0.5 * abs(vp1_1 - vp1_2)
        p1_angle = atan(abs(vp1_1 - vp1_2) / abs(hp1_1 - hp1_2))
        half_chord = 0.5 * sqrt((vp1_1 - vp1_2) ** 2 + (hp1_1 - hp1_2) ** 2)
        R_correction1 = Units.Quantity(
            sqrt(blend_radius ** 2 - Units.Quantity(half_chord, 1) ** 2), 1
        )
        hcp1_1 = p1_centre_h - (blend_radius - R_correction1) * sin(p1_angle)
        vcp1_1 = p1_centre_v + (blend_radius - R_correction1) * cos(p1_angle)
        cp1_1 = Base.Vector(0, hcp1_1, vcp1_1)

        hp2_1 = arc_outer_radius * sin(radians(half_angle - blend_angle))
        vp2_1 = arc_outer_radius * cos(radians(half_angle - blend_angle))
        p2_1 = Base.Vector(0, hp2_1, vp2_1)
        hp2_2 = ho - blend_radius * sin(radians(half_angle))
        vp2_2 = vo - blend_radius * cos(radians(half_angle))
        p2_2 = Base.Vector(0, hp2_2, vp2_2)
        p2_centre_h = hp2_1 + 0.5 * abs(hp2_1 - hp2_2)
        p2_centre_v = vp2_1 - 0.5 * abs(vp2_1 - vp2_2)
        p2_angle = atan(abs(vp2_1 - vp2_2) / abs(hp2_1 - hp2_2))
        half_chord = 0.5 * sqrt((vp2_1 - vp2_2) ** 2 + (hp2_1 - hp2_2) ** 2)
        R_correction2 = Units.Quantity(
            sqrt(blend_radius ** 2 - Units.Quantity(half_chord, 1) ** 2), 1
        )
        hcp2_1 = p2_centre_h + (blend_radius - R_correction2) * sin(p2_angle)
        vcp2_1 = p2_centre_v + (blend_radius - R_correction2) * cos(p2_angle)
        cp2_1 = Base.Vector(0, hcp2_1, vcp2_1)

        hp3_1 = hi + blend_radius * sin(radians(half_angle))
        vp3_1 = vi + blend_radius * cos(radians(half_angle))
        p3_1 = Base.Vector(0, hp3_1, vp3_1)
        hp3_2 = arc_inner_radius * sin(radians(half_angle - blend_angle))
        vp3_2 = arc_inner_radius * cos(radians(half_angle - blend_angle))
        p3_2 = Base.Vector(0, hp3_2, vp3_2)
        p3_centre_h = hp3_1 - 0.5 * abs(hp3_1 - hp3_2)
        p3_centre_v = vp3_1 - 0.5 * abs(vp3_1 - vp3_2)
        p3_angle = atan(abs(vp3_1 - vp3_2) / abs(hp3_1 - hp3_2))
        half_chord = 0.5 * sqrt((vp3_1 - vp3_2) ** 2 + (hp3_1 - hp3_2) ** 2)
        R_correction3 = Units.Quantity(
            sqrt(blend_radius ** 2 - Units.Quantity(half_chord, 1) ** 2), 1
        )
        hcp3_1 = p3_centre_h + (blend_radius - R_correction3) * sin(p3_angle)
        vcp3_1 = p3_centre_v - (blend_radius - R_correction3) * cos(p3_angle)
        cp3_1 = Base.Vector(0, hcp3_1, vcp3_1)

        hp10_1 = -arc_inner_radius * sin(radians(half_angle - blend_angle))
        vp10_1 = arc_inner_radius * cos(radians(half_angle - blend_angle))
        p10_1 = Base.Vector(0, hp10_1, vp10_1)
        hp10_2 = -hi - blend_radius * sin(radians(half_angle))
        vp10_2 = vi + blend_radius * cos(radians(half_angle))
        p10_2 = Base.Vector(0, hp10_2, vp10_2)
        p10_centre_h = hp10_1 - 0.5 * abs(hp10_1 - hp10_2)
        p10_centre_v = vp10_1 + 0.5 * abs(vp10_1 - vp10_2)
        p10_angle = atan(abs(vp10_1 - vp10_2) / abs(hp10_1 - hp10_2))
        half_chord = 0.5 * sqrt((vp10_1 - vp10_2) ** 2 + (hp10_1 - hp10_2) ** 2)
        R_correction10 = Units.Quantity(
            sqrt(blend_radius ** 2 - Units.Quantity(half_chord, 1) ** 2), 1
        )
        hcp10_1 = p10_centre_h - (blend_radius - R_correction10) * sin(p10_angle)
        vcp10_1 = p10_centre_v - (blend_radius - R_correction10) * cos(p10_angle)
        cp10_1 = Base.Vector(0, hcp10_1, vcp10_1)

        hdiff = abs(hif - hp10_1)
        vdiff = abs(vif - vp10_1)
        line_angle = atan(vdiff / hdiff)
        hifcp1 = arc_inner_radius * sin(radians(flat_angle) + 0.5 * line_angle)
        vifcp1 = arc_inner_radius * cos(radians(flat_angle) + 0.5 * line_angle)
        cpp2 = Base.Vector(0, hifcp1, vifcp1)
        cpp4 = Base.Vector(0, -hifcp1, vifcp1)

        # Create curves
        arcp1 = Part.Arc(p1_1, cp1_1, p1_2)
        arcp2 = Part.Arc(p1_2, cp1, p2_1)
        arcp3 = Part.Arc(p2_1, cp2_1, p2_2)
        arcp4 = Part.Arc(p3_1, cp3_1, p3_2)
        arcp5 = Part.Arc(p3_2, cpp2, p4)
        arcp6 = Part.Arc(p9, cpp4, p10_1)
        arcp7 = Part.Arc(p10_1, cp10_1, p10_2)

        # Create lines
        linep1 = Part.LineSegment(p2_2, p3_1)
        linep2 = Part.LineSegment(p10_2, p1_1)

        shape1 = Part.Shape(
            [
                arcp1,
                arcp2,
                arcp3,
                linep1,
                arcp4,
                arcp5,
                line2,
                arc5,
                line3,
                arc3,
                line4,
                arc6,
                line5,
                arcp6,
                arcp7,
                linep2,
            ]
        )

    # Make a wire outline.
    wire1 = Part.Wire(shape1.Edges)
    # Make a face.
    face1 = Part.Face(wire1)
    return wire1, face1


def make_arched_cutout_aperture(aperture_height, aperture_width, arc_radius):
    """Creates a wire outline of a rectangle with an arc removed from the centre of one edge.

    Args:
        arc_radius (float): Radius of the arc.
        aperture_height (float): Total height of the aperture
        aperture_width (float): Total width of the aperture

    Returns:
        wire1 (FreeCAD wire definition): An outline description of the shape.
        face1 (FreeCAD face definition): A surface description of the shape.
    """
    # Create the initial four vertices where line meets curve.
    v1 = Base.Vector(0, aperture_height / 2.0, -aperture_width / 2.0)
    v2 = Base.Vector(0, aperture_height / 2.0, aperture_width / 2.0)
    v3 = Base.Vector(0, -aperture_height / 2.0, aperture_width / 2.0)
    v4 = Base.Vector(0, -aperture_height / 2.0, arc_radius)
    v5 = Base.Vector(0, -aperture_height / 2.0, -arc_radius)
    v6 = Base.Vector(0, -aperture_height / 2.0, -aperture_width / 2.0)
    cv1 = Base.Vector(
        0,
        -aperture_height / 2.0 + arc_radius,
        0,
    )
    # Create lines
    line1 = Part.LineSegment(v6, v1)
    line2 = Part.LineSegment(v1, v2)
    line3 = Part.LineSegment(v2, v3)
    line4 = Part.LineSegment(v3, v4)
    line5 = Part.LineSegment(v5, v6)
    # Create curves
    arc1 = Part.Arc(v4, cv1, v5)
    # Make a shape
    shape1 = Part.Shape([line1, line2, line3, line4, arc1, line5])
    # Make a wire outline.
    wire1 = Part.Wire(shape1.Edges)
    # Make a face.
    face1 = Part.Face(wire1)

    return wire1, face1


def make_truncated_arched_cutout_aperture(
    aperture_height, centre_position, aperture_width, arc_radius
):
    """Creates a wire outline of a rectangle with an arc removed from the centre of one edge.

    Args:
        arc_radius (float): Radius of the arc.
        centre_position (float): position along width making the centre of the cutout arc.
        aperture_height (float): Total height of the aperture
        aperture_width (float): Total width of the aperture

    Returns:
        wire1 (FreeCAD wire definition): An outline description of the shape.
        face1 (FreeCAD face definition): A surface description of the shape.
    """
    # Create the initial four vertices where line meets curve.
    v1 = Base.Vector(0, aperture_height - arc_radius, -aperture_width + centre_position)
    v2 = Base.Vector(0, aperture_height - arc_radius, centre_position)
    v3 = Base.Vector(
        0,
        -float(arc_radius) + sqrt(arc_radius ** 2 - centre_position ** 2),
        centre_position,
    )
    v4 = Base.Vector(0, -arc_radius, -arc_radius)
    v5 = Base.Vector(0, -arc_radius, -aperture_width + centre_position)
    cv1 = Base.Vector(
        0,
        0,
        0,
    )
    # Create lines
    line1 = Part.LineSegment(v5, v1)
    line2 = Part.LineSegment(v1, v2)
    line3 = Part.LineSegment(v2, v3)
    line4 = Part.LineSegment(v4, v5)
    # Create curves
    arc1 = Part.Arc(v3, cv1, v4)
    # Make a shape
    shape1 = Part.Shape([line1, line2, line3, arc1, line4])
    # Make a wire outline.
    wire1 = Part.Wire(shape1.Edges)
    # Make a face.
    face1 = Part.Face(wire1)

    return wire1, face1


def make_arched_corner_cutout_aperture(aperture_height, aperture_width, arc_radius):
    """Creates a wire outline of a rectangle with an arc removed from one corner.

    Args:
        arc_radius (float): Radius of the arc.
        aperture_height (float): Total height of the aperture
        aperture_width (float): Total width of the aperture

    Returns:
        wire1 (FreeCAD wire definition): An outline description of the shape.
        face1 (FreeCAD face definition): A surface description of the shape.
    """
    # Create the initial four vertices where line meets curve.
    v1 = Base.Vector(0, aperture_height, 0)
    v2 = Base.Vector(0, aperture_height, aperture_width)
    v3 = Base.Vector(0, -aperture_height, aperture_width)
    v4 = Base.Vector(0, -aperture_height, arc_radius)
    v5 = Base.Vector(0, -aperture_height + arc_radius, 0)
    cv1 = Base.Vector(
        0,
        -float(aperture_height) + sqrt(arc_radius / 2.0),
        sqrt(arc_radius / 2.0),
    )
    # Create lines
    line1 = Part.LineSegment(v5, v1)
    line2 = Part.LineSegment(v1, v2)
    line3 = Part.LineSegment(v2, v3)
    line4 = Part.LineSegment(v3, v4)
    # Create curves
    arc1 = Part.Arc(v4, cv1, v5)
    # Make a shape
    shape1 = Part.Shape([line1, line2, line3, line4, arc1])
    # Make a wire outline.
    wire1 = Part.Wire(shape1.Edges)
    # Make a face.
    face1 = Part.Face(wire1)

    return wire1, face1


def make_arched_base_aperture(aperture_height, aperture_width, arc_radius):
    """Creates a wire outline of a rectangle with an arc removed from one edge..

    Args:
        arc_radius (float): Radius of the arc.
        aperture_height (float): Total height of the aperture
        aperture_width (float): Total width of the aperture

    Returns:
        wire1 (FreeCAD wire definition): An outline description of the shape.
        face1 (FreeCAD face definition): A surface description of the shape.
    """
    # Create the initial four vertices where line meets curve.
    v1 = Base.Vector(0, aperture_height / 2.0, -aperture_width / 2.0)
    v2 = Base.Vector(0, aperture_height / 2.0, aperture_width / 2.0)
    v3 = Base.Vector(0, -aperture_height / 2.0, aperture_width / 2.0)
    v4 = Base.Vector(0, -aperture_height / 2.0, -aperture_width / 2.0)
    cv1 = Base.Vector(
        0,
        -aperture_height / 2.0
        + arc_radius
        - Units.Quantity(str(sqrt(arc_radius ** 2 - (aperture_width ** 2) / 4)) + "mm"),
        0,
    )
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


def make_arched_base_trapezoid_aperture(
    aperture_height, base_width, top_width, arc_radius
):
    """Creates a wire outline of a rectangle with an arc removed from one edge..

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
    v1 = Base.Vector(0, aperture_height / 2.0, -top_width / 2.0)
    v2 = Base.Vector(0, aperture_height / 2.0, top_width / 2.0)
    v3 = Base.Vector(0, -aperture_height / 2.0, base_width / 2.0)
    v4 = Base.Vector(0, -aperture_height / 2.0, -base_width / 2.0)
    cv1 = Base.Vector(
        0,
        -aperture_height / 2.0
        + arc_radius
        - sqrt(arc_radius ** 2 - (base_width ** 2) / 4),
        0,
    )
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


def make_cylinder_with_inserts(
    outer_radius, inner_radius, insert_angle, blend_radius=Units.Quantity("0 mm")
):
    """Creates a wire outline of a cylinder with inserts to a smaller
       cylinder for part of the radius.

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
    if blend_radius == 0:
        # Make a shape
        shape1 = Part.Shape([arc4, line4, arc1, line1, arc2, line2, arc3, line3])
    else:
        # shift required along the linear sections
        bh = blend_radius * cos(radians(insert_angle))
        bv = blend_radius * sin(radians(insert_angle))
        # location along the arc sections
        # length of the hypotonuse
        lc = sqrt((inner_radius -hi) ** 2 + vi ** 2)
        lc_frac = blend_radius / Units.Quantity(lc,1)
        arcbh = inner_radius * cos(radians(insert_angle * (1 - lc_frac)))
        arcbv = inner_radius * sin(radians(insert_angle * (1 - lc_frac)))
        p3_1 = Base.Vector(0, -hi - bh, vi + bv)#
        cp3_1 = Base.Vector(0, -hi - blend_radius * (1 - 1 / sqrt(2)), vi - blend_radius * (1 - 1 / sqrt(2)))
        p3_2 = Base.Vector(0, -arcbh , arcbv)
        p4_1 = Base.Vector(0, -arcbh , -arcbv)
        cp4_1 = Base.Vector(0, -hi - blend_radius * (1 - 1 / sqrt(2)), -vi + blend_radius * (1 - 1 / sqrt(2)))
        p4_2 = Base.Vector(0, -hi - bh, -vi - bv)#
        p7_1 = Base.Vector(0, hi + bh, -vi - bv)#
        cp7_1 = Base.Vector(0, hi + blend_radius * (1 - 1 / sqrt(2)), -vi + blend_radius * (1 - 1 / sqrt(2)))
        p7_2 = Base.Vector(0, arcbh, -arcbv)
        p8_1 = Base.Vector(0, arcbh, arcbv)
        cp8_1 = Base.Vector(0, hi + blend_radius * (1 - 1 / sqrt(2)), vi - blend_radius * (1 - 1 / sqrt(2)))
        p8_2 = Base.Vector(0, hi + bh, vi + bv)#

        # Create lines
        line1 = Part.LineSegment(p2, p3_1)
        line2 = Part.LineSegment(p4_2, p5)
        line3 = Part.LineSegment(p6, p7_1)
        line4 = Part.LineSegment(p8_2, p1)
                # Create main curves
        #arc1t1 = Part.LineSegment(p1, cp1)
        #arc1t2 = Part.LineSegment(cp1, p2)
        #arc3t1 = Part.LineSegment(p5, cp3)
        #arc3t2 = Part.LineSegment(cp3, p6)
        #arc2t1 = Part.LineSegment(p3_2, cp2)
        #arc2t2 = Part.LineSegment(cp2, p4_1)
        #arc4t1 = Part.LineSegment(p7_2, cp4)
        #arc4t2 = Part.LineSegment(cp4, p8_1)

        # Create blending curves
        #arc3_1t1 = Part.LineSegment(p3_1, cp3_1)
        #arc3_1t2 = Part.LineSegment(cp3_1, p3_2)
        #arc4_1t1 = Part.LineSegment(p4_1, cp4_1)
        #arc4_1t2 = Part.LineSegment(cp4_1, p4_2)
        #arc7_1t1 = Part.LineSegment(p7_1, cp7_1)
        #arc7_1t2 = Part.LineSegment(cp7_1, p7_2)
        #arc8_1t1 = Part.LineSegment(p8_1, cp8_1)
        #arc8_1t2 = Part.LineSegment(cp8_1, p8_2)
        # Create main curves
        arc1 = Part.Arc(p1, cp1, p2)
        arc3 = Part.Arc(p5, cp3, p6)
        arc2 = Part.Arc(p3_2, cp2, p4_1)
        arc4 = Part.Arc(p7_2, cp4, p8_1)
        # Create blending curves
        arc3_1 = Part.Arc(p3_1, cp3_1, p3_2)
        arc4_1 = Part.Arc(p4_1, cp4_1, p4_2)
        arc7_1 = Part.Arc(p7_1, cp7_1, p7_2)
        arc8_1 = Part.Arc(p8_1, cp8_1, p8_2)
        # Make a shape
       # shape1 = Part.Shape(
       #     [
       #         arc4t1,
       #         arc4t2,
       #         arc8_1t1,
       #         arc8_1t2,
       #         line4,
       #         arc1t1,
       #         arc1t2,
       #         line1,
       #         arc3_1t1,
       #         arc3_1t2,
       #         arc2t1,
       #         arc2t2,
       #         arc4_1t1,
       #         arc4_1t2,
       #         line2,
       #         arc3t1,
       #         arc3t2,
       #         line3,
       #         arc7_1t1,
       #         arc7_1t2,
       #     ]
       # )  
        shape1 = Part.Shape(
            [
                arc4,
                arc8_1,
                line4,
                arc1,
                line1,
                arc3_1,
                arc2,
                arc4_1,
                line2,
                arc3,
                line3,
                arc7_1,
            ]
        )  

    # Make a wire outline.
    wire1 = Part.Wire(shape1.Edges)
    # Make a face.
    face1 = Part.Face(wire1)

    return wire1, face1


def make_spoked_cylinder(
    outer_radius,
    inner_radius,
    insert_angles,
    spoke_extents,
    blend_radius=Units.Quantity("0 mm"),
):
    """Creates a wire outline of a cylinder with inserts to a smaller cylinder
       for part of the radius.

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
        a1 = radians(insert_angles[dn] - spoke_extents[dn] / 2.0)
        h1 = inner_radius * cos(a1)
        v1 = inner_radius * sin(a1)
        model_points.append(Base.Vector(0, h1, v1))
        if dn > 0:
            model_edges.append(
                Part.Arc(model_points[tk - 2], model_points[tk - 1], model_points[tk])
            )
        tk = tk + 1
        ck = ck + 1
        a2 = radians(insert_angles[dn] - spoke_extents[dn] / 2.0)
        h2 = outer_radius * cos(a2)
        v2 = outer_radius * sin(a2)
        model_points.append(Base.Vector(0, h2, v2))
        model_edges.append(Part.LineSegment(model_points[tk - 1], model_points[tk]))
        tk = tk + 1
        ck = ck + 1
        a3 = radians(insert_angles[dn])
        h3 = outer_radius * cos(a3)
        v3 = outer_radius * sin(a3)
        model_points.append(Base.Vector(0, h3, v3))
        tk = tk + 1
        a4 = radians(insert_angles[dn] + spoke_extents[dn] / 2.0)
        h4 = outer_radius * cos(a4)
        v4 = outer_radius * sin(a4)
        model_points.append(Base.Vector(0, h4, v4))
        model_edges.append(
            Part.Arc(model_points[tk - 2], model_points[tk - 1], model_points[tk])
        )
        tk = tk + 1
        ck = ck + 1
        a5 = radians(insert_angles[dn] + spoke_extents[dn] / 2.0)
        h5 = inner_radius * cos(a5)
        v5 = inner_radius * sin(a5)
        model_points.append(Base.Vector(0, h5, v5))
        model_edges.append(Part.LineSegment(model_points[tk - 1], model_points[tk]))
        tk = tk + 1
        ck = ck + 1
        if dn == len(insert_angles) - 1:
            a6 = radians(
                insert_angles[dn]
                + (insert_angles[0] - insert_angles[dn]) / 2.0
                - Units.Quantity("180deg")
            )
        else:
            a6 = radians(
                insert_angles[dn] + (insert_angles[dn + 1] - insert_angles[dn]) / 2.0
            )
        h6 = inner_radius * cos(a6)
        v6 = inner_radius * sin(a6)
        model_points.append(Base.Vector(0, h6, v6))
        if dn == len(insert_angles) - 1:
            model_edges.append(
                Part.Arc(model_points[tk - 1], model_points[tk], model_points[0])
            )
        tk = tk + 1
    shape1 = Part.Shape(model_edges)

    # Make a wire outline.
    wire1 = Part.Wire(shape1.Edges)
    # Make a face.
    face1 = Part.Face(wire1)

    return wire1, face1


def make_cylinder_with_tags(outer_radius, inner_radius, insert_angles, tag_widths):
    """Creates a wire outline of a cylinder with inserts to a smaller
       cylinder for part of the radius.

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
        d1 = inner_radius - Units.Quantity(
            sqrt(inner_radius * inner_radius - (tag_widths[dn] * tag_widths[dn]) / 4.0),
            1,
        )
        d2 = outer_radius - Units.Quantity(
            sqrt(outer_radius * outer_radius - (tag_widths[dn] * tag_widths[dn]) / 4.0),
            1,
        )
        top_corner_height = outer_radius - d2
        bottom_corner_height = inner_radius - d1
        h1, v1 = rotate_cartesian(
            tag_widths[dn] / 2.0, bottom_corner_height, insert_angles[dn]
        )
        model_points.append(Base.Vector(0, h1, v1))
        if dn > 0:
            model_edges.append(
                Part.ArcOfCircle(
                    model_points[tk - 2], model_points[tk - 1], model_points[tk]
                )
            )
            model_edges[-1] = force_short_arc(
                p1=model_points[tk - 2], p2=model_points[tk - 1], edge=model_edges[-1]
            )
        tk = tk + 1
        h2, v2 = rotate_cartesian(
            tag_widths[dn] / 2.0, top_corner_height, insert_angles[dn]
        )
        model_points.append(Base.Vector(0, h2, v2))
        model_edges.append(Part.LineSegment(model_points[tk - 1], model_points[tk]))
        tk = tk + 1
        h3 = outer_radius * sin(-radians(insert_angles[dn]))
        v3 = outer_radius * cos(-radians(insert_angles[dn]))
        model_points.append(Base.Vector(0, h3, v3))
        tk = tk + 1
        h4, v4 = rotate_cartesian(
            -tag_widths[dn] / 2.0, top_corner_height, insert_angles[dn]
        )
        model_points.append(Base.Vector(0, h4, v4))
        model_edges.append(
            Part.ArcOfCircle(
                model_points[tk - 2], model_points[tk - 1], model_points[tk]
            )
        )
        model_edges[-1] = force_short_arc(
            p1=model_points[tk - 2], p2=model_points[tk - 1], edge=model_edges[-1]
        )
        tk = tk + 1
        h5, v5 = rotate_cartesian(
            -tag_widths[dn] / 2.0, bottom_corner_height, insert_angles[dn]
        )
        model_points.append(Base.Vector(0, h5, v5))
        model_edges.append(Part.LineSegment(model_points[tk - 1], model_points[tk]))
        tk = tk + 1
        if dn == len(insert_angles) - 1:
            a6 = radians(
                insert_angles[dn]
                + (-insert_angles[dn] + insert_angles[0]) / 2.0
                + Units.Quantity("180deg")
            )
        else:
            a6 = radians(
                insert_angles[dn] + (insert_angles[dn + 1] - insert_angles[dn]) / 2.0
            )
        h6 = inner_radius * sin(-a6)
        v6 = inner_radius * cos(-a6)
        model_points.append(Base.Vector(0, h6, v6))
        if dn == len(insert_angles) - 1:
            model_edges.append(
                Part.ArcOfCircle(
                    model_points[tk - 1], model_points[tk], model_points[0]
                )
            )
        tk = tk + 1

    shape1 = Part.Shape(model_edges)
    # Make a wire outline.
    wire1 = Part.Wire(shape1.Edges)
    # Make a face.
    face1 = Part.Face(wire1)
    return wire1, face1


def make_polygon_with_tags(inner_radius, tag_radii, insert_angles, tag_widths):
    """Creates a wire outline of a cylinder with inserts to a smaller
       cylinder for part of the radius.

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
        d1 = inner_radius - Units.Quantity(
            sqrt(inner_radius * inner_radius - (tag_widths[dn] * tag_widths[dn]) / 4.0),
            1,
        )
        d2 = tag_radii[dn] - Units.Quantity(
            sqrt(
                tag_radii[dn] * tag_radii[dn] - (tag_widths[dn] * tag_widths[dn]) / 4.0
            ),
            1,
        )
        top_corner_height = tag_radii[dn] - d2
        bottom_corner_height = inner_radius - d1
        h1, v1 = rotate_cartesian(
            tag_widths[dn] / 2.0, bottom_corner_height, insert_angles[dn]
        )
        model_points.append(Base.Vector(0, h1, v1))
        if dn > 0:
            model_edges.append(Part.LineSegment(model_points[tk - 1], model_points[tk]))
        tk = tk + 1
        h2, v2 = rotate_cartesian(
            tag_widths[dn] / 2.0, top_corner_height, insert_angles[dn]
        )
        model_points.append(Base.Vector(0, h2, v2))
        model_edges.append(Part.LineSegment(model_points[tk - 1], model_points[tk]))
        tk = tk + 1
        h3 = tag_radii[dn] * sin(-radians(insert_angles[dn]))
        v3 = tag_radii[dn] * cos(-radians(insert_angles[dn]))
        model_points.append(Base.Vector(0, h3, v3))
        tk = tk + 1
        h4, v4 = rotate_cartesian(
            -tag_widths[dn] / 2.0, top_corner_height, insert_angles[dn]
        )
        model_points.append(Base.Vector(0, h4, v4))
        model_edges.append(
            Part.ArcOfCircle(
                model_points[tk - 2], model_points[tk - 1], model_points[tk]
            )
        )
        model_edges[-1] = force_short_arc(
            p1=model_points[tk - 2], p2=model_points[tk - 1], edge=model_edges[-1]
        )
        tk = tk + 1
        h5, v5 = rotate_cartesian(
            -tag_widths[dn] / 2.0, bottom_corner_height, insert_angles[dn]
        )
        model_points.append(Base.Vector(0, h5, v5))
        model_edges.append(Part.LineSegment(model_points[tk - 1], model_points[tk]))
        tk = tk + 1
        if dn == len(insert_angles) - 1:
            model_edges.append(Part.LineSegment(model_points[tk - 1], model_points[0]))

    shape1 = Part.Shape(model_edges)
    # Make a wire outline.
    wire1 = Part.Wire(shape1.Edges)
    # Make a face.
    face1 = Part.Face(wire1)
    return wire1, face1


def make_circular_aperture(aperture_radius):
    """Creates a wire outline of a circle.
    aperture_radius is the radius of the circle

    Args:
        aperture_radius (float): Total radius of the aperture

    Returns:
        wire1 (FreeCAD wire definition): An outline description of the shape.
        face1 (FreeCAD face definition): A surface description of the shape.
    """
    # Create curves
    curve1 = Part.Circle(
        Base.Vector(
            Units.Quantity("0mm"), Units.Quantity("0mm"), Units.Quantity("0mm")
        ),
        Base.Vector(1, 0, 0),
        aperture_radius,
    )
    arc1 = Part.Arc(curve1, 0.0, 2 * pi)  # angles are in radian here

    # Make a shape
    shape1 = Part.Shape([arc1])
    # Make a wire outline.
    wire1 = Part.Wire(shape1.Edges)
    # Make a face.
    face1 = Part.Face(wire1)
    return wire1, face1


def make_octagonal_aperture_asymetric(
    aperture_height,
    aperture_width1,
    aperture_width2,
    side_length1,
    side_length2,
    tb_length,
):
    """Creates a wire outline of a symmetric octagon specified by 4 inputs.
    aperture_height and aperture_width are the full height and width
    (the same as if it were a rectangle)
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
    v1 = Base.Vector(0, aperture_height / 2.0, -tb_length / 2.0)
    v2 = Base.Vector(0, aperture_height / 2.0, tb_length / 2.0)
    v3 = Base.Vector(0, side_length1 / 2.0, aperture_width1)
    v4 = Base.Vector(0, -side_length1 / 2.0, aperture_width1)
    v5 = Base.Vector(0, -aperture_height / 2.0, tb_length / 2.0)
    v6 = Base.Vector(0, -aperture_height / 2.0, -tb_length / 2.0)
    v7 = Base.Vector(0, -side_length2 / 2.0, -aperture_width2)
    v8 = Base.Vector(0, side_length2 / 2.0, -aperture_width2)

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


def make_octagonal_aperture(aperture_height, aperture_width, side_length, tb_length):
    """Creates a wire outline of a symmetric octagon specified by 4 inputs.
    aperture_height and aperture_width are the full height and width
    (the same as if it were a rectangle)
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
    v1 = Base.Vector(0, aperture_height / 2.0, -tb_length / 2.0)
    v2 = Base.Vector(0, aperture_height / 2.0, tb_length / 2.0)
    v3 = Base.Vector(0, side_length / 2.0, aperture_width / 2.0)
    v4 = Base.Vector(0, -side_length / 2.0, aperture_width / 2.0)
    v5 = Base.Vector(0, -aperture_height / 2.0, tb_length / 2.0)
    v6 = Base.Vector(0, -aperture_height / 2.0, -tb_length / 2.0)
    v7 = Base.Vector(0, -side_length / 2.0, -aperture_width / 2.0)
    v8 = Base.Vector(0, side_length / 2.0, -aperture_width / 2.0)

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


def make_octagonal_aperture_with_keyholes_and_antichamber(
    aperture_height,
    tb_width,
    ib_oct_width,
    ob_oct_width,
    ib_keyhole_height,
    ib_keyhole_width,
    ob_keyhole_height,
    ob_keyhole_width,
    antichamber_taper_width,
    antichamber_height,
    antichamber_width,
):
    """Creates a wire outline of a symmetric octagon specified by 4 inputs.
    aperture_height and aperture_width are the full height and width
    (the same as if it were a rectangle)
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
        antichamber_taper_width (float): width of the taper between the inboard slot
                                         and the antichamber.
        antichamber_width (float): width of the antichamber.
        antichamber_height (float): height of the antichamber.

    Returns:
        wire1 (FreeCAD wire definition): An outline description of the shape.
        face1 (FreeCAD face definition): A surface description of the shape.
    """

    # Create the initial vertices.
    x1 = -tb_width / 2.0 - ob_oct_width - ob_keyhole_width
    x2 = -tb_width / 2.0 - ob_oct_width
    x3 = -tb_width / 2.0
    x4 = tb_width / 2.0
    x5 = tb_width / 2.0 + ib_oct_width
    x6 = tb_width / 2.0 + ib_oct_width + ib_keyhole_width
    x7 = tb_width / 2.0 + ib_oct_width + ib_keyhole_width + antichamber_taper_width
    x8 = (
        tb_width / 2.0
        + ib_oct_width
        + ib_keyhole_width
        + antichamber_taper_width
        + antichamber_width
    )
    y1 = ob_keyhole_height / 2.0
    y2 = aperture_height / 2.0
    y3 = ib_keyhole_height / 2.0
    y4 = antichamber_height / 2.0

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
    shape1 = Part.Shape(
        [
            line1,
            line2,
            line3,
            line4,
            line5,
            line6,
            line7,
            line8,
            line9,
            line10,
            line11,
            line12,
            line13,
            line14,
            line15,
            line16,
        ]
    )
    # Make a wire outline.
    wire1 = Part.Wire(shape1.Edges)
    # Make a face.
    face1 = Part.Face(wire1)
    return wire1, face1


def make_elliptical_aperture(aperture_height, aperture_width):
    """Creates a wire outline of a ellipse specified by 2 inputs.
    aperture_height and aperture_width are the full height and width
    (the same as if it were a rectangle)

    Args:
        aperture_height (float): Total height of the ellipse.
        aperture_width (float): Total width of the ellipse.

    Returns:
        wire1 (FreeCAD wire definition): An outline description of the shape.
        face1 (FreeCAD face definition): A surface description of the shape.
    """
    # # Define the semi axis
    b = aperture_height / 2.0
    a = aperture_width / 2.0

    el1 = Part.Ellipse(Base.Vector(0, 0, 0), a, b)
    # Make a shape
    shape1 = el1.toShape()
    shape1.rotate(Base.Vector(0, 0, 0), Base.Vector(0, 1, 0), 90)
    # Make a wire outline.
    wire1 = Part.Wire(shape1.Edges)
    face1 = Part.Face(wire1)
    return wire1, face1


def force_short_arc(p1, p2, edge):
    edge.parameter(p1), edge.FirstParameter
    edge.parameter(p2), edge.LastParameter
    if edge.LastParameter - edge.FirstParameter > pi:
        edge = Part.ArcOfCircle(
            edge.Circle, edge.LastParameter, 2 * pi + edge.FirstParameter
        )
    return edge
