from copy import deepcopy
from math import asin, atan2, cos, log10, pi, sin, sqrt

# import Part
from FreeCAD import Base, Draft, Part, Units, Vector
from numpy import linspace

from FreeCAD_geometry_generation.freecad_apertures import (
    make_arc_aperture,
    make_arched_base_aperture,
    make_arched_corner_cutout_aperture,
    make_arched_cutout_aperture,
    make_circular_aperture,
    make_truncated_arched_cutout_aperture,
)
from FreeCAD_geometry_generation.freecad_operations import (
    make_beampipe,
    make_taper,
    rotate_at,
)


def stripline_curved_end(params):
    stripline_length = params["total_stripline_length"]
    stripline_width = params["stripline_width"]
    stripline_offset = params["stripline_offset"]
    stripline_half_thickness = params["stripline_thickness"] / 2.0
    taper_end_width = params["stripline_taper_end_width"] + Units.Quantity(
        "6.2deg"
    )  # to account for tapering to the main stripline
    arch_radius = Units.Quantity("0.75mm")  # stripline_half_thickness
    y_radius = stripline_offset + stripline_half_thickness
    # min_t = -(stripline_taper_end_width / 2.) / 180 * pi # Assuming degrees
    # max_t = float((taper_end_width / 2.0) / 180 * pi)  # Assuming degrees
    # max_loc = (stripline_offset + stripline_half_thickness) * sin(max_t)
    end_radius = y_radius * sin((taper_end_width / 2.0) / 180 * pi)  # chord /2
    n_points = 51
    points = []
    pointsBottom = []
    end_points = []
    points_mid_end2 = []
    y_level = []
    angs = []
    z_axis = []
    ang_scale = linspace(
        float(-pi / 2.0),
        float(pi / 2.0),
        num=n_points,
        endpoint=True
        # ang_scale = linspace(
        # -float(max_t), float(max_t), num=n_points, endpoint=True
    )  # angular spacing
    for val in ang_scale:
        z_axis.append(float(end_radius) * sin(val))
    # z_axis = linspace(-float(max_loc), float(max_loc), num=n_points, endpoint=True) # distance spacing
    for z in z_axis:
        x_point = (
            stripline_length / 2.0
            - end_radius
            + Units.Quantity(
                str(sqrt(end_radius ** 2.0 - Units.Quantity(str(z) + "mm") ** 2.0))
                + "mm"
            )
        )
        y_point = Units.Quantity(
            str(sqrt((y_radius) ** 2.0 - Units.Quantity(str(z) + "mm") ** 2.0)) + "mm"
        )
        if not points:
            y_level.append(y_point)

        points.append(Vector(x_point, y_point + Units.Quantity("0.125mm"), z))
        pointsBottom.append(Vector(x_point, y_point - Units.Quantity("0.125mm"), z))
        end_points.append(Vector(x_point, y_level[0] - Units.Quantity("5mm"), z))
        points_mid_end2.append(
            Vector(
                x_point + Units.Quantity("10mm"), y_level[0] - Units.Quantity("5mm"), z
            )
        )
    end_points.append(points_mid_end2[-1])
    end_points.append(points_mid_end2[0])
    end_points.append(end_points[0])
    end_curve = Part.makePolygon(end_points)
    end_wire = Part.Wire(end_curve)
    end_face = Part.Face(end_wire)
    end_solid = end_face.extrude(Base.Vector(0, 10, 0))

    makeSolid = True
    cap1_out = []
    cap1_out1 = []
    cap2_out = []
    for sd in range(len(z_axis)):
        cap1_wire, cap1_face = make_truncated_arched_cutout_aperture(
            aperture_height=arch_radius + Units.Quantity("1mm"),
            centre_position=Units.Quantity("0.001mm"),
            aperture_width=arch_radius + Units.Quantity("2mm"),
            arc_radius=arch_radius,
        )

        cap1_wire = rotate_at(cap1_wire, rotation_angles=(90, 180, 0))
        cap1_wire.translate(points[sd])
        cap1_wire.rotate(points[sd], Base.Vector(0, 1, 0), -(ang_scale[sd] + 90))
        cap1_out.append(cap1_wire)

        cap2_wire, cap2_face = make_truncated_arched_cutout_aperture(
            aperture_height=arch_radius + Units.Quantity("1mm"),
            centre_position=Units.Quantity("0.001mm"),
            aperture_width=arch_radius + Units.Quantity("2mm"),
            arc_radius=arch_radius,
        )
        cap2_wire = rotate_at(cap2_wire, rotation_angles=(-90, 0, 0))
        cap2_wire.translate(pointsBottom[sd])
        cap2_wire.rotate(pointsBottom[sd], Base.Vector(0, 1, 0), -(ang_scale[sd] + 90))
        cap2_out.append(cap2_wire)
    print("Apertures constructed")
    sweep = Part.makeLoft(cap1_out, True, False)
    print("Loft 1 completed")
    sweep2 = Part.makeLoft(cap2_out, True, False)
    print("Loft 1 completed")
    sweep = sweep.fuse(sweep2)
    print("fuse completed")
    return sweep, end_solid


def sma_connector(pin_length=20e-3, rotation=(0, 1, 0), location=(0, 0, 0)):
    # Reference plane is the lower side of the ceramic (vacuum side down).
    # pin_length is the length from the base of the ceramic into the vacuum.
    input_parameters = {
        "pin_radius": 1.24e-3 / 2,
        "pin_length": pin_length,
        "ceramic_radius": 3e-3 / 2,
        "ceramic_thickness": 2.5e-3,
        "shell_upper_radius": 6e-3 / 2,
        "shell_upper_thickness": 5e-3,
        "shell_upper_inner_radius": 3.5e-3 / 2,
        "shell_lower_radius": 4e-3 / 2,
        "shell_lower_thickness": 5e-3,
        "shell_lower_inner_radius": 3.5e-3 / 2,
    }

    pin = Part.makeCylinder(
        input_parameters["pin_radius"],
        input_parameters["pin_length"]
        + input_parameters["ceramic_thickness"]
        + input_parameters["shell_upper_thickness"],
        Base.Vector(
            location[0], location[1] - input_parameters["pin_length"], location[2]
        ),
        Base.Vector(rotation[0], rotation[1], rotation[2]),
    )

    ceramic1 = Part.makeCylinder(
        input_parameters["ceramic_radius"],
        input_parameters["ceramic_thickness"],
        Base.Vector(location[0], location[1], location[2]),
        Base.Vector(rotation[0], rotation[1], rotation[2]),
    )

    shell_upper1 = Part.makeCylinder(
        input_parameters["shell_upper_radius"],
        input_parameters["shell_upper_thickness"],
        Base.Vector(
            location[0],
            location[1] + input_parameters["ceramic_thickness"],
            location[2],
        ),
        Base.Vector(rotation[0], rotation[1], rotation[2]),
    )
    shell_upper2 = Part.makeCylinder(
        input_parameters["shell_upper_inner_radius"],
        input_parameters["shell_upper_thickness"],
        Base.Vector(
            location[0],
            location[1] + input_parameters["ceramic_thickness"],
            location[2],
        ),
        Base.Vector(rotation[0], rotation[1], rotation[2]),
    )
    shell_middle1 = Part.makeCylinder(
        input_parameters["shell_upper_radius"],
        input_parameters["ceramic_thickness"],
        Base.Vector(location[0], location[1], location[2]),
        Base.Vector(rotation[0], rotation[1], rotation[2]),
    )
    shell_lower1 = Part.makeCylinder(
        input_parameters["shell_lower_radius"],
        input_parameters["shell_lower_thickness"],
        Base.Vector(
            location[0],
            location[1] - input_parameters["shell_lower_thickness"],
            location[2],
        ),
        Base.Vector(rotation[0], rotation[1], rotation[2]),
    )
    shell_lower2 = Part.makeCylinder(
        input_parameters["shell_lower_inner_radius"],
        input_parameters["shell_lower_thickness"],
        Base.Vector(
            location[0],
            location[1] - input_parameters["shell_lower_thickness"],
            location[2],
        ),
        Base.Vector(rotation[0], rotation[1], rotation[2]),
    )
    shell_middle = shell_middle1.cut(ceramic1)
    ceramic = ceramic1.cut(pin)
    shell_lower3 = shell_lower1.cut(shell_lower2)
    shell_lower = shell_lower3.fuse(shell_middle)
    shell_upper = shell_upper1.cut(shell_upper2)
    outer = shell_upper.fuse(shell_lower)

    parts = {"pin": pin, "ceramic": ceramic, "outer": outer}
    return parts


def connector_parameterised(
    input_parameters,
    rotation=(Units.Quantity("0deg"), Units.Quantity("0deg"), Units.Quantity("0deg")),
    location=(Units.Quantity("0mm"), Units.Quantity("0mm"), Units.Quantity("0mm")),
    rotate_around_zero=(
        Units.Quantity("0 deg"),
        Units.Quantity("0 deg"),
        Units.Quantity("0 deg"),
    ),
):
    # Reference plane is the lower side of the ceramic (vacuum side down).
    # pin_length is the length from the base of the ceramic into the vacuum.

    pin = Part.makeCylinder(
        input_parameters["pin_radius"],
        input_parameters["pin_length"]
        + input_parameters["ceramic_thickness"]
        + input_parameters["shell_upper_thickness"],
        Base.Vector(
            location[0], location[1] - input_parameters["pin_length"], location[2]
        ),
        Base.Vector(0, 1, 0),
    )
    pin = rotate_at(
        shp=pin,
        loc=(location[0], location[1], location[2]),
        rotation_angles=(rotation[0], rotation[1], rotation[2]),
    )
    vac = Part.makeCylinder(
        input_parameters["shell_lower_inner_radius"],
        input_parameters["pin_length"],
        Base.Vector(
            location[0], location[1] - input_parameters["pin_length"], location[2]
        ),
        Base.Vector(0, 1, 0),
    )
    vac = rotate_at(
        shp=vac,
        loc=(location[0], location[1], location[2]),
        rotation_angles=(rotation[0], rotation[1], rotation[2]),
    )
    ceramic1 = Part.makeCylinder(
        input_parameters["ceramic_radius"],
        input_parameters["ceramic_thickness"],
        Base.Vector(location[0], location[1], location[2]),
        Base.Vector(0, 1, 0),
    )
    if input_parameters["ceramic_inner_radius"]:
        ceramic_hole = Part.makeCylinder(
        input_parameters["ceramic_inner_radius"],
        input_parameters["ceramic_thickness"],
        Base.Vector(location[0], location[1], location[2]),
        Base.Vector(0, 1, 0),
        )
        ceramic1 = ceramic1.cut(ceramic_hole)
    ceramic1 = rotate_at(
        shp=ceramic1,
        loc=(location[0], location[1], location[2]),
        rotation_angles=(rotation[0], rotation[1], rotation[2]),
    )
    if input_parameters["ceramic_inner_radius"]:
        pin = pin.cut(ceramic1)

    air1 = Part.makeCylinder(
        input_parameters["shell_upper_inner_radius"],
        input_parameters["shell_upper_thickness"],
        Base.Vector(
            location[0],
            location[1] + input_parameters["ceramic_thickness"],
            location[2],
        ),
        Base.Vector(0, 1, 0),
    )
    air1 = rotate_at(
        shp=air1,
        loc=(location[0], location[1], location[2]),
        rotation_angles=(rotation[0], rotation[1], rotation[2]),
    )

    shell_upper1 = Part.makeCylinder(
        input_parameters["shell_upper_radius"],
        input_parameters["shell_upper_thickness"],
        Base.Vector(
            location[0],
            location[1] + input_parameters["ceramic_thickness"],
            location[2],
        ),
        Base.Vector(0, 1, 0),
    )
    shell_upper1 = rotate_at(
        shp=shell_upper1,
        loc=(location[0], location[1], location[2]),
        rotation_angles=(rotation[0], rotation[1], rotation[2]),
    )
    shell_upper2 = Part.makeCylinder(
        input_parameters["shell_upper_inner_radius"],
        input_parameters["shell_upper_thickness"],
        Base.Vector(
            location[0],
            location[1] + input_parameters["ceramic_thickness"],
            location[2],
        ),
        Base.Vector(0, 1, 0),
    )
    shell_upper2 = rotate_at(
        shp=shell_upper2,
        loc=(location[0], location[1], location[2]),
        rotation_angles=(rotation[0], rotation[1], rotation[2]),
    )
    shell_middle1 = Part.makeCylinder(
        input_parameters["shell_upper_radius"],
        input_parameters["ceramic_thickness"],
        Base.Vector(location[0], location[1], location[2]),
        Base.Vector(0, 1, 0),
    )
    shell_middle1 = rotate_at(
        shp=shell_middle1,
        loc=(location[0], location[1], location[2]),
        rotation_angles=(rotation[0], rotation[1], rotation[2]),
    )
    shell_lower1 = Part.makeCylinder(
        input_parameters["shell_lower_radius"],
        input_parameters["shell_lower_thickness"],
        Base.Vector(
            location[0],
            location[1] - input_parameters["shell_lower_thickness"],
            location[2],
        ),
        Base.Vector(0, 1, 0),
    )
    shell_lower1 = rotate_at(
        shp=shell_lower1,
        loc=(location[0], location[1], location[2]),
        rotation_angles=(rotation[0], rotation[1], rotation[2]),
    )
    shell_lower2 = Part.makeCylinder(
        input_parameters["shell_lower_inner_radius"],
        input_parameters["shell_lower_thickness"],
        Base.Vector(
            location[0],
            location[1] - input_parameters["shell_lower_thickness"],
            location[2],
        ),
        Base.Vector(0, 1, 0),
    )
    shell_lower2 = rotate_at(
        shp=shell_lower2,
        loc=(location[0], location[1], location[2]),
        rotation_angles=(rotation[0], rotation[1], rotation[2]),
    )
    shell_middle = shell_middle1.cut(ceramic1)
    ceramic = ceramic1.cut(pin)
    shell_lower3 = shell_lower1.cut(shell_lower2)
    shell_lower = shell_lower3.fuse(shell_middle)
    shell_upper = shell_upper1.cut(shell_upper2)
    outer = shell_upper.fuse(shell_lower)
    air = air1.cut(pin)
    air = air.cut(outer)

    rotate_at(
        shp=outer,
        rotation_angles=(
            rotate_around_zero[0],
            rotate_around_zero[1],
            rotate_around_zero[2],
        ),
    )
    rotate_at(
        shp=ceramic,
        rotation_angles=(
            rotate_around_zero[0],
            rotate_around_zero[1],
            rotate_around_zero[2],
        ),
    )
    rotate_at(
        shp=air,
        rotation_angles=(
            rotate_around_zero[0],
            rotate_around_zero[1],
            rotate_around_zero[2],
        ),
    )
    rotate_at(
        shp=pin,
        rotation_angles=(
            rotate_around_zero[0],
            rotate_around_zero[1],
            rotate_around_zero[2],
        ),
    )
    rotate_at(
        shp=vac,
        rotation_angles=(
            rotate_around_zero[0],
            rotate_around_zero[1],
            rotate_around_zero[2],
        ),
    )

    parts = {"pin": pin, "ceramic": ceramic, "outer": outer, "air": air, "vac": vac}
    return parts


def ntype_connector50Ohm(
    pin_length="20mm",
    rotation=(Units.Quantity("0deg"), Units.Quantity("0deg"), Units.Quantity("0deg")),
    location=(Units.Quantity("0mm"), Units.Quantity("0mm"), Units.Quantity("0mm")),
    ceramic_radius=Units.Quantity("3.5mm"),
    ceramic_thickness=Units.Quantity("5mm"),
    shell_lower_thickness=Units.Quantity("5mm"),
    shell_upper_thickness=Units.Quantity("10mm"),
    rotate_around_zero=(
        Units.Quantity("0 deg"),
        Units.Quantity("0 deg"),
        Units.Quantity("0 deg"),
    ),
):
    # Reference plane is the lower side of the ceramic (vacuum side down).
    # pin_length is the length from the base of the ceramic into the vacuum.
    input_parameters = {
        "pin_radius": "1.75mm",
        "pin_length": pin_length,
        "ceramic_radius": ceramic_radius,
        "ceramic_thickness": ceramic_thickness,
        "shell_upper_radius": "8mm",
        "shell_upper_thickness": shell_upper_thickness,
        "shell_upper_inner_radius": "4.015mm",
        "shell_lower_radius": "5mm",
        "shell_lower_thickness": shell_lower_thickness,
        "shell_lower_inner_radius": "4.015mm",
    }
    for n in input_parameters.keys():
        if type(input_parameters[n]) is list:
            for eh in range(len(input_parameters[n])):
                input_parameters[n][eh] = Units.Quantity(input_parameters[n][eh])
        else:
            input_parameters[n] = Units.Quantity(input_parameters[n])
        print(n, input_parameters[n])
    print("Parsing complete")
    pin = Part.makeCylinder(
        input_parameters["pin_radius"],
        input_parameters["pin_length"]
        + input_parameters["ceramic_thickness"]
        + input_parameters["shell_upper_thickness"],
        Base.Vector(
            location[0], location[1] - input_parameters["pin_length"], location[2]
        ),
        Base.Vector(0, 1, 0),
    )
    pin = rotate_at(
        shp=pin,
        loc=(location[0], location[1], location[2]),
        rotation_angles=(rotation[0], rotation[1], rotation[2]),
    )

    ceramic1 = Part.makeCylinder(
        input_parameters["ceramic_radius"],
        input_parameters["ceramic_thickness"],
        Base.Vector(location[0], location[1], location[2]),
        Base.Vector(0, 1, 0),
    )
    ceramic1 = rotate_at(
        shp=ceramic1,
        loc=(location[0], location[1], location[2]),
        rotation_angles=(rotation[0], rotation[1], rotation[2]),
    )
    air1 = Part.makeCylinder(
        input_parameters["shell_upper_inner_radius"],
        input_parameters["shell_upper_thickness"],
        Base.Vector(
            location[0],
            location[1] + input_parameters["ceramic_thickness"],
            location[2],
        ),
        Base.Vector(0, 1, 0),
    )
    air1 = rotate_at(
        shp=air1,
        loc=(location[0], location[1], location[2]),
        rotation_angles=(rotation[0], rotation[1], rotation[2]),
    )

    shell_upper1 = Part.makeCylinder(
        input_parameters["shell_upper_radius"],
        input_parameters["shell_upper_thickness"],
        Base.Vector(
            location[0],
            location[1] + input_parameters["ceramic_thickness"],
            location[2],
        ),
        Base.Vector(0, 1, 0),
    )
    shell_upper1 = rotate_at(
        shp=shell_upper1,
        loc=(location[0], location[1], location[2]),
        rotation_angles=(rotation[0], rotation[1], rotation[2]),
    )
    shell_upper2 = Part.makeCylinder(
        input_parameters["shell_upper_inner_radius"],
        input_parameters["shell_upper_thickness"],
        Base.Vector(
            location[0],
            location[1] + input_parameters["ceramic_thickness"],
            location[2],
        ),
        Base.Vector(0, 1, 0),
    )
    shell_upper2 = rotate_at(
        shp=shell_upper2,
        loc=(location[0], location[1], location[2]),
        rotation_angles=(rotation[0], rotation[1], rotation[2]),
    )
    shell_middle1 = Part.makeCylinder(
        input_parameters["shell_upper_radius"],
        input_parameters["ceramic_thickness"],
        Base.Vector(location[0], location[1], location[2]),
        Base.Vector(0, 1, 0),
    )
    shell_middle1 = rotate_at(
        shp=shell_middle1,
        loc=(location[0], location[1], location[2]),
        rotation_angles=(rotation[0], rotation[1], rotation[2]),
    )
    shell_lower1 = Part.makeCylinder(
        input_parameters["shell_lower_radius"],
        input_parameters["shell_lower_thickness"],
        Base.Vector(
            location[0],
            location[1] - input_parameters["shell_lower_thickness"],
            location[2],
        ),
        Base.Vector(0, 1, 0),
    )
    shell_lower1 = rotate_at(
        shp=shell_lower1,
        loc=(location[0], location[1], location[2]),
        rotation_angles=(rotation[0], rotation[1], rotation[2]),
    )
    shell_lower2 = Part.makeCylinder(
        input_parameters["shell_lower_inner_radius"],
        input_parameters["shell_lower_thickness"],
        Base.Vector(
            location[0],
            location[1] - input_parameters["shell_lower_thickness"],
            location[2],
        ),
        Base.Vector(0, 1, 0),
    )
    shell_lower2 = rotate_at(
        shp=shell_lower2,
        loc=(location[0], location[1], location[2]),
        rotation_angles=(rotation[0], rotation[1], rotation[2]),
    )
    shell_middle = shell_middle1.cut(ceramic1)
    ceramic = ceramic1.cut(pin)
    shell_lower3 = shell_lower1.cut(shell_lower2)
    shell_lower = shell_lower3.fuse(shell_middle)
    shell_upper = shell_upper1.cut(shell_upper2)
    outer = shell_upper.fuse(shell_lower)
    air = air1.cut(pin)
    air = air.cut(outer)

    rotate_at(
        shp=outer,
        rotation_angles=(
            rotate_around_zero[0],
            rotate_around_zero[1],
            rotate_around_zero[2],
        ),
    )
    rotate_at(
        shp=ceramic,
        rotation_angles=(
            rotate_around_zero[0],
            rotate_around_zero[1],
            rotate_around_zero[2],
        ),
    )
    rotate_at(
        shp=air,
        rotation_angles=(
            rotate_around_zero[0],
            rotate_around_zero[1],
            rotate_around_zero[2],
        ),
    )
    rotate_at(
        shp=pin,
        rotation_angles=(
            rotate_around_zero[0],
            rotate_around_zero[1],
            rotate_around_zero[2],
        ),
    )

    parts = {"pin": pin, "ceramic": ceramic, "outer": outer, "air": air}
    return parts


def ntype_connector(
    pin_length="20mm",
    rotation=(Units.Quantity("0deg"), Units.Quantity("0deg"), Units.Quantity("0deg")),
    location=(Units.Quantity("0mm"), Units.Quantity("0mm"), Units.Quantity("0mm")),
):
    # Reference plane is the lower side of the ceramic (vacuum side down).
    # pin_length is the length from the base of the ceramic into the vacuum.
    input_parameters = {
        "pin_radius": "1.5mm",
        "pin_length": pin_length,
        "ceramic_radius": "3.5mm",
        "ceramic_thickness": "5mm",
        "shell_upper_radius": "8mm",
        "shell_upper_thickness": "10mm",
        "shell_upper_inner_radius": "4.015mm",
        "shell_lower_radius": "4.5mm",
        "shell_lower_thickness": "5mm",
        "shell_lower_inner_radius": "4.015mm",
    }
    for n in input_parameters.keys():
        if type(input_parameters[n]) is list:
            for eh in range(len(input_parameters[n])):
                input_parameters[n][eh] = Units.Quantity(input_parameters[n][eh])
        else:
            input_parameters[n] = Units.Quantity(input_parameters[n])
        print(n, input_parameters[n])
    print("Parsing complete")
    pin = Part.makeCylinder(
        input_parameters["pin_radius"],
        input_parameters["pin_length"]
        + input_parameters["ceramic_thickness"]
        + input_parameters["shell_upper_thickness"],
        Base.Vector(
            location[0], location[1] - input_parameters["pin_length"], location[2]
        ),
        Base.Vector(0, 1, 0),
    )
    pin = rotate_at(
        shp=pin,
        loc=(location[0], location[1], location[2]),
        rotation_angles=(rotation[0], rotation[1], rotation[2]),
    )

    ceramic1 = Part.makeCylinder(
        input_parameters["ceramic_radius"],
        input_parameters["ceramic_thickness"],
        Base.Vector(location[0], location[1], location[2]),
        Base.Vector(0, 1, 0),
    )
    ceramic1 = rotate_at(
        shp=ceramic1,
        loc=(location[0], location[1], location[2]),
        rotation_angles=(rotation[0], rotation[1], rotation[2]),
    )

    shell_upper1 = Part.makeCylinder(
        input_parameters["shell_upper_radius"],
        input_parameters["shell_upper_thickness"],
        Base.Vector(
            location[0],
            location[1] + input_parameters["ceramic_thickness"],
            location[2],
        ),
        Base.Vector(0, 1, 0),
    )
    shell_upper1 = rotate_at(
        shp=shell_upper1,
        loc=(location[0], location[1], location[2]),
        rotation_angles=(rotation[0], rotation[1], rotation[2]),
    )
    shell_upper2 = Part.makeCylinder(
        input_parameters["shell_upper_inner_radius"],
        input_parameters["shell_upper_thickness"],
        Base.Vector(
            location[0],
            location[1] + input_parameters["ceramic_thickness"],
            location[2],
        ),
        Base.Vector(0, 1, 0),
    )
    shell_upper2 = rotate_at(
        shp=shell_upper2,
        loc=(location[0], location[1], location[2]),
        rotation_angles=(rotation[0], rotation[1], rotation[2]),
    )
    shell_middle1 = Part.makeCylinder(
        input_parameters["shell_upper_radius"],
        input_parameters["ceramic_thickness"],
        Base.Vector(location[0], location[1], location[2]),
        Base.Vector(0, 1, 0),
    )
    shell_middle1 = rotate_at(
        shp=shell_middle1,
        loc=(location[0], location[1], location[2]),
        rotation_angles=(rotation[0], rotation[1], rotation[2]),
    )
    shell_lower1 = Part.makeCylinder(
        input_parameters["shell_lower_radius"],
        input_parameters["shell_lower_thickness"],
        Base.Vector(
            location[0],
            location[1] - input_parameters["shell_lower_thickness"],
            location[2],
        ),
        Base.Vector(0, 1, 0),
    )
    shell_lower1 = rotate_at(
        shp=shell_lower1,
        loc=(location[0], location[1], location[2]),
        rotation_angles=(rotation[0], rotation[1], rotation[2]),
    )
    shell_lower2 = Part.makeCylinder(
        input_parameters["shell_lower_inner_radius"],
        input_parameters["shell_lower_thickness"],
        Base.Vector(
            location[0],
            location[1] - input_parameters["shell_lower_thickness"],
            location[2],
        ),
        Base.Vector(0, 1, 0),
    )
    shell_lower2 = rotate_at(
        shp=shell_lower2,
        loc=(location[0], location[1], location[2]),
        rotation_angles=(rotation[0], rotation[1], rotation[2]),
    )
    shell_middle = shell_middle1.cut(ceramic1)
    ceramic = ceramic1.cut(pin)
    shell_lower3 = shell_lower1.cut(shell_lower2)
    shell_lower = shell_lower3.fuse(shell_middle)
    shell_upper = shell_upper1.cut(shell_upper2)
    outer = shell_upper.fuse(shell_lower)

    parts = {"pin": pin, "ceramic": ceramic, "outer": outer}
    return parts


def ntype_connector_stub(
    pin_length=Units.Quantity("20 mm"),
    ring_length=Units.Quantity("2 mm"),
    rotation=(
        Units.Quantity("0 deg"),
        Units.Quantity("0 deg"),
        Units.Quantity("0 deg"),
    ),
    location=(Units.Quantity("0 mm"), Units.Quantity("0 mm"), Units.Quantity("0 mm")),
    rotate_around_zero=(
        Units.Quantity("0 deg"),
        Units.Quantity("0 deg"),
        Units.Quantity("0 deg"),
    ),
):
    # Reference plane is the lower side of the ceramic (vacuum side down).
    # pin_length is the length from the base of the ceramic into the vacuum.
    input_parameters = {
        "pin_radius": Units.Quantity("3 mm") / 2,
        "pin_length": pin_length,
        "shell_lower_radius": Units.Quantity("9 mm") / 2,
        "shell_lower_thickness": ring_length,
        "shell_lower_inner_radius": Units.Quantity("8.03 mm") / 2,
    }

    pin = Part.makeCylinder(
        input_parameters["pin_radius"],
        input_parameters["pin_length"],
        Base.Vector(
            location[0], location[1] - input_parameters["pin_length"], location[2]
        ),
        Base.Vector(0, 1, 0),
    )
    pin1 = rotate_at(
        shp=pin,
        loc=(location[0], location[1], location[2]),
        rotation_angles=(rotation[0], rotation[1], rotation[2]),
    )
    shell_lower1 = Part.makeCylinder(
        input_parameters["shell_lower_radius"],
        input_parameters["shell_lower_thickness"],
        Base.Vector(
            location[0],
            location[1] - input_parameters["shell_lower_thickness"],
            location[2],
        ),
        Base.Vector(0, 1, 0),
    )
    shell_lower1_1 = rotate_at(
        shp=shell_lower1,
        loc=(location[0], location[1], location[2]),
        rotation_angles=(rotation[0], rotation[1], rotation[2]),
    )
    shell_lower2 = Part.makeCylinder(
        input_parameters["shell_lower_inner_radius"],
        input_parameters["shell_lower_thickness"],
        Base.Vector(
            location[0],
            location[1] - input_parameters["shell_lower_thickness"],
            location[2],
        ),
        Base.Vector(0, 1, 0),
    )
    shell_lower2_1 = rotate_at(
        shp=shell_lower2,
        loc=(location[0], location[1], location[2]),
        rotation_angles=(rotation[0], rotation[1], rotation[2]),
    )

    shell_lower = shell_lower1_1.cut(shell_lower2_1)

    rotate_at(
        shp=shell_lower,
        rotation_angles=(
            rotate_around_zero[0],
            rotate_around_zero[1],
            rotate_around_zero[2],
        ),
    )
    rotate_at(
        shp=pin1,
        rotation_angles=(
            rotate_around_zero[0],
            rotate_around_zero[1],
            rotate_around_zero[2],
        ),
    )
    rotate_at(
        shp=shell_lower2_1,
        rotation_angles=(
            rotate_around_zero[0],
            rotate_around_zero[1],
            rotate_around_zero[2],
        ),
    )
    parts = {"pin": pin1, "outer": shell_lower, "vac": shell_lower2_1}
    return parts


def make_nose(
    aperture_radius,
    ring_width,
    ring_length,
    blend,
    loc=(Units.Quantity("0 mm"), Units.Quantity("0 mm"), Units.Quantity("0 mm")),
    rot=(Units.Quantity("0 deg"), Units.Quantity("0 deg"), Units.Quantity("0 deg")),
):
    inner = Part.makeCylinder(
        aperture_radius,
        ring_length - ring_width / 2.0,
        Base.Vector(loc),
        Base.Vector(1, 0, 0),
    )
    outer = Part.makeCylinder(
        aperture_radius + ring_width,
        ring_length - ring_width / 2.0,
        Base.Vector(loc),
        Base.Vector(1, 0, 0),
    )
    blending = Part.makeCylinder(
        aperture_radius + ring_width + blend,
        blend,
        Base.Vector(loc),
        Base.Vector(1, 0, 0),
    )
    ring = outer.cut(inner)
    blend_ring = blending.cut(outer)
    nose_tip = Part.makeTorus(
        aperture_radius + ring_width / 2.0,
        ring_width / 2.0,
        Base.Vector(loc[0] + ring_length - ring_width / 2.0, loc[1], loc[2]),
        Base.Vector(1, 0, 0),
    )
    blend_curve = Part.makeTorus(
        aperture_radius + ring_width + blend,
        blend,
        Base.Vector(loc[0] + blend, loc[1], loc[2]),
        Base.Vector(1, 0, 0),
    )
    nose = ring.fuse(nose_tip)
    nose = nose.fuse(blend_ring)
    nose = nose.cut(blend_curve)
    nose = rotate_at(nose, loc=loc, rotation_angles=rot)
    return nose


def make_stripline_feedthrough_parameterised(
    input_parameters, z_loc="us", xyrotation=0
):
    stripline_mid_section_length = (
        input_parameters["total_stripline_length"]
        - 2 * input_parameters["stripline_taper_length"]
    )
    # total_cavity_length is the total stipline length plus the additional
    # cavity length at each end.
    total_cavity_length = (
        input_parameters["total_stripline_length"]
        + 2 * input_parameters["additional_cavity_length"]
    )
    # Calculating the joining point of the outer conductor to the taper.
    port_offset = (
        input_parameters["total_stripline_length"] / 2.0
        - input_parameters["feedthrough_offset"]
    )
    feedthrough_outer_x = port_offset + input_parameters["n_type_outer_radius"]
    feedthrough_outer_y = (
        input_parameters["cavity_radius"]
        - (input_parameters["cavity_radius"] - input_parameters["pipe_radius"])
        / (total_cavity_length / 2.0 - stripline_mid_section_length / 2.0)
        * feedthrough_outer_x
    )
    # Pin stops half way through the stripline.
    input_parameters["pin_length"] = (
        input_parameters["port_height"]
        + input_parameters["cavity_radius"]
        - input_parameters["stripline_offset"]
        + input_parameters["pipe_thickness"]
        - input_parameters["stripline_thickness"] / 2.0
    )
    ring_start_y = (
        input_parameters["port_height"]
        + input_parameters["cavity_radius"]
        + input_parameters["pipe_thickness"]
    )
    ring_length = ring_start_y - feedthrough_outer_y + Units.Quantity("2 mm")

    if z_loc == "us":
        z = -1
    elif z_loc == "ds":
        z = 1
    else:
        raise ValueError

    port_link = Part.makeCylinder(
        input_parameters["port_ouside_radius"],
        ring_length,
        Base.Vector(z * port_offset, ring_start_y, 0),
        Base.Vector(0, -1, 0),
    )
    n_parts = connector_parameterised(
        input_parameters,
        location=(z * port_offset, ring_start_y, 0),
        rotation=(0, 0, 0),
        rotate_around_zero=(xyrotation, 0, 0),
    )
    feedthrough_vaccum_length = ring_start_y
    feedthrough_vaccum = Part.makeCylinder(
        input_parameters["n_type_outer_inner_radius"],
        feedthrough_vaccum_length,
        Base.Vector(z * port_offset, 0, 0),
        Base.Vector(0, -1, 0),
    )
    port_link = port_link.cut(feedthrough_vaccum)
    rotate_at(shp=feedthrough_vaccum, rotation_angles=(xyrotation, 0, 0))
    rotate_at(shp=port_link, rotation_angles=(xyrotation, 0, 0))
    n_parts["outer"] = n_parts["outer"].fuse(port_link)
    return n_parts, feedthrough_vaccum


def make_stripline_feedthrough_full(input_parameters, z_loc="us", xyrotation=0):
    stripline_mid_section_length = (
        input_parameters["total_stripline_length"]
        - 2 * input_parameters["stripline_taper_length"]
    )
    # total_cavity_length is the total stipline length plus the additional
    # cavity length at each end.
    total_cavity_length = (
        input_parameters["total_stripline_length"]
        + 2 * input_parameters["additional_cavity_length"]
    )
    # Calculating the joining point of the outer conductor to the taper.
    port_offset = (
        input_parameters["total_stripline_length"] / 2.0
        - input_parameters["feedthrough_offset"]
    )
    feedthrough_outer_x = port_offset + input_parameters["n_type_outer_radius"]
    feedthrough_outer_y = (
        input_parameters["cavity_radius"]
        - (input_parameters["cavity_radius"] - input_parameters["pipe_radius"])
        / (total_cavity_length / 2.0 - stripline_mid_section_length / 2.0)
        * feedthrough_outer_x
    )
    # Pin stops half way through the stripline.
    pin_length = (
        input_parameters["port_height"]
        + input_parameters["cavity_radius"]
        - input_parameters["stripline_offset"]
        + input_parameters["pipe_thickness"]
        - input_parameters["stripline_thickness"] / 2.0
    )
    ring_start_y = (
        input_parameters["port_height"]
        + input_parameters["cavity_radius"]
        + input_parameters["pipe_thickness"]
    )
    ring_length = ring_start_y - feedthrough_outer_y + Units.Quantity("2 mm")

    if z_loc == "us":
        z = -1
    elif z_loc == "ds":
        z = 1
    else:
        raise ValueError

    port_link = Part.makeCylinder(
        Units.Quantity("10 mm"),
        ring_length,
        Base.Vector(z * port_offset, ring_start_y, 0),
        Base.Vector(0, -1, 0),
    )
    n_parts = ntype_connector50Ohm(
        pin_length=pin_length,
        location=(z * port_offset, ring_start_y, 0),
        rotation=(0, 0, 0),
        rotate_around_zero=(xyrotation, 0, 0),
    )
    n_type_outer_inner_radius = Units.Quantity("8.03 mm") / 2.0
    feedthrough_vaccum_length = ring_start_y
    feedthrough_vaccum = Part.makeCylinder(
        n_type_outer_inner_radius,
        feedthrough_vaccum_length,
        Base.Vector(z * port_offset, 0, 0),
        Base.Vector(0, -1, 0),
    )
    port_link = port_link.cut(feedthrough_vaccum)
    rotate_at(shp=feedthrough_vaccum, rotation_angles=(xyrotation, 0, 0))
    rotate_at(shp=port_link, rotation_angles=(xyrotation, 0, 0))
    n_parts["outer"] = n_parts["outer"].fuse(port_link)
    return n_parts, feedthrough_vaccum


def make_stripline_feedthrough_stub(input_parameters, z_loc="us", xyrotation=0):
    stripline_mid_section_length = (
        input_parameters["total_stripline_length"]
        - 2 * input_parameters["stripline_taper_length"]
    )
    # total_cavity_length is the total stipline length plus the additional
    # cavity length at each end.
    total_cavity_length = (
        input_parameters["total_stripline_length"]
        + 2 * input_parameters["additional_cavity_length"]
    )
    # Calculating the joining point of the outer conductor to the taper.
    n_type_outer_radius = Units.Quantity("9 mm") / 2.0
    port_offset = (
        input_parameters["total_stripline_length"] / 2.0
        - input_parameters["feedthrough_offset"]
    )
    feedthrough_outer_x = port_offset + n_type_outer_radius
    feedthrough_outer_y = (
        input_parameters["cavity_radius"]
        - (input_parameters["cavity_radius"] - input_parameters["pipe_radius"])
        / (total_cavity_length / 2.0 - stripline_mid_section_length / 2.0)
        * feedthrough_outer_x
    )
    # Pin stops half way through the stripline.
    pin_length = (
        input_parameters["cavity_radius"]
        - input_parameters["stripline_offset"]
        + input_parameters["pipe_thickness"]
        - input_parameters["stripline_thickness"] / 2.0
    )
    ring_start_y = (
        input_parameters["cavity_radius"] + input_parameters["pipe_thickness"]
    )
    ring_length = ring_start_y - feedthrough_outer_y + Units.Quantity("2 mm")
    if z_loc == "us":
        z = -1
    elif z_loc == "ds":
        z = 1
    else:
        raise ValueError
    n_parts = ntype_connector_stub(
        pin_length=pin_length,
        ring_length=ring_length,
        location=(z * port_offset, ring_start_y, 0),
        rotation=(0, 0, 0),
        rotate_around_zero=(xyrotation, 0, 0),
    )
    n_type_outer_inner_radius = Units.Quantity("8.03 mm") / 2.0
    feedthrough_vaccum_length = (
        input_parameters["cavity_radius"] + input_parameters["pipe_thickness"]
    )
    feedthrough_vaccum = Part.makeCylinder(
        n_type_outer_inner_radius,
        feedthrough_vaccum_length,
        Base.Vector(z * port_offset, 0, 0),
        Base.Vector(0, -1, 0),
    )
    rotate_at(shp=feedthrough_vaccum, rotation_angles=(xyrotation, 0, 0))
    return n_parts, feedthrough_vaccum


def make_stripline_fixed_ratio_launch(input_parameters, xyrotation=0):
    stripline_mid_section_length = (
        input_parameters["total_stripline_length"]
        - 2 * input_parameters["stripline_taper_length"]
    )
    stripline_main_wire, stripline_main_face = make_arc_aperture(
        arc_inner_radius=input_parameters["stripline_offset"],
        arc_outer_radius=input_parameters["stripline_offset"]
        + input_parameters["stripline_thickness"],
        arc_length=input_parameters["stripline_width"],
        blend_radius=Units.Quantity("0.75 mm"),
    )
    stripline_taper_end_wire, stripline_taper_end_face = make_arc_aperture(
        arc_inner_radius=input_parameters["stripline_offset"],
        arc_outer_radius=input_parameters["stripline_offset"]
        + input_parameters["stripline_thickness"],
        arc_length=input_parameters["stripline_taper_end_width"],
        blend_radius=Units.Quantity("0.75 mm"),
    )

    stripline_main = make_beampipe(
        pipe_aperture=stripline_main_face,
        pipe_length=stripline_mid_section_length,
        loc=(0, 0, 0),
    )
    stripline_taper_us = make_taper(
        aperture1=stripline_taper_end_wire,
        aperture2=stripline_main_wire,
        taper_length=input_parameters["stripline_taper_length"],
        loc=(
            -input_parameters["stripline_taper_length"]
            - stripline_mid_section_length / 2.0,
            0,
            0,
        ),
    )
    stripline_taper_ds = make_taper(
        aperture1=stripline_main_wire,
        aperture2=stripline_taper_end_wire,
        taper_length=input_parameters["stripline_taper_length"],
        loc=(stripline_mid_section_length / 2.0, 0, 0),
    )
    stripline = stripline_main.fuse(stripline_taper_us)
    stripline = stripline.fuse(stripline_taper_ds)
    if "Launch_height" in input_parameters:
        us_launch = Part.makeCone(
            input_parameters["Launch_rad"],
            input_parameters["pin_radius"],
            input_parameters["Launch_height"],
            Base.Vector(
                -input_parameters["total_stripline_length"] / 2.0
                + input_parameters["feedthrough_offset"],
                0,
                input_parameters["stripline_offset"],
            ),
        )
        ds_launch = Part.makeCone(
            input_parameters["Launch_rad"],
            input_parameters["pin_radius"],
            input_parameters["Launch_height"],
            Base.Vector(
                input_parameters["total_stripline_length"] / 2.0
                - input_parameters["feedthrough_offset"],
                0,
                input_parameters["stripline_offset"],
            ),
        )
        cone_base = Units.Quantity(
            str(float(input_parameters["Launch_rad"]) * 10**(50 / 138)) + "mm"
        )
        cone_top = Units.Quantity(
            str(float(input_parameters["pin_radius"]) * 10**(50 / 138)) + "mm"
        )
        print("Launch rad ", input_parameters["Launch_rad"])
        print("cone base ", cone_base)
        print("pin_radius ", input_parameters["pin_radius"])
        print("cone top ", cone_top)
        us_launch_vac = Part.makeCone(
            cone_base,
            cone_top,
            input_parameters["Launch_height"],
            Base.Vector(
                -input_parameters["total_stripline_length"] / 2.0
                + input_parameters["feedthrough_offset"],
                0,
                input_parameters["stripline_offset"],
            ),
        )
        ds_launch_vac = Part.makeCone(
            cone_base,
            cone_top,
            input_parameters["Launch_height"],
            Base.Vector(
                input_parameters["total_stripline_length"] / 2.0
                - input_parameters["feedthrough_offset"],
                0,
                input_parameters["stripline_offset"],
            ),
        )
        launch_vac = us_launch_vac.fuse(ds_launch_vac)
        # stripline = stripline.cut(stripline_end_us)
        # stripline = stripline.cut(stripline_end_ds)
        # us_launch = us_launch.cut(stripline_end_us)
        # ds_launch = ds_launch.cut(stripline_end_ds)
        stripline = stripline.fuse(us_launch)
        stripline = stripline.fuse(ds_launch)

        rotate_at(shp=launch_vac, rotation_angles=(xyrotation, 0, 0))
        rotate_at(shp=stripline, rotation_angles=(xyrotation, 0, 0))
        return stripline, launch_vac
    else:
        rotate_at(shp=stripline, rotation_angles=(xyrotation, 0, 0))
        return stripline


def make_stripline(input_parameters, xyrotation=0):
    stripline_mid_section_length = (
        input_parameters["total_stripline_length"]
        - 2 * input_parameters["stripline_taper_length"]
    )
    stripline_main_wire, stripline_main_face = make_arc_aperture(
        arc_inner_radius=input_parameters["stripline_offset"],
        arc_outer_radius=input_parameters["stripline_offset"]
        + input_parameters["stripline_thickness"],
        arc_length=input_parameters["stripline_width"],
        blend_radius=Units.Quantity("0.75 mm"),
    )
    stripline_taper_end_wire, stripline_taper_end_face = make_arc_aperture(
        arc_inner_radius=input_parameters["stripline_offset"],
        arc_outer_radius=input_parameters["stripline_offset"]
        + input_parameters["stripline_thickness"],
        arc_length=input_parameters["stripline_taper_end_width"],
        blend_radius=Units.Quantity("0.75 mm"),
    )

    stripline_main = make_beampipe(
        pipe_aperture=stripline_main_face,
        pipe_length=stripline_mid_section_length,
        loc=(0, 0, 0),
    )
    stripline_taper_us = make_taper(
        aperture1=stripline_taper_end_wire,
        aperture2=stripline_main_wire,
        taper_length=input_parameters["stripline_taper_length"],
        loc=(
            -input_parameters["stripline_taper_length"]
            - stripline_mid_section_length / 2.0,
            0,
            0,
        ),
    )
    stripline_taper_ds = make_taper(
        aperture1=stripline_main_wire,
        aperture2=stripline_taper_end_wire,
        taper_length=input_parameters["stripline_taper_length"],
        loc=(stripline_mid_section_length / 2.0, 0, 0),
    )
    stripline = stripline_main.fuse(stripline_taper_us)
    stripline = stripline.fuse(stripline_taper_ds)
    if "Launch_height" in input_parameters:
        us_launch = Part.makeCone(
            input_parameters["Launch_rad"],
            Units.Quantity("1.75mm"),
            input_parameters["Launch_height"],
            Base.Vector(
                -input_parameters["total_stripline_length"] / 2.0
                + input_parameters["feedthrough_offset"],
                0,
                input_parameters["stripline_offset"],
            ),
        )
        ds_launch = Part.makeCone(
            input_parameters["Launch_rad"],
            Units.Quantity("1.75mm"),
            input_parameters["Launch_height"],
            Base.Vector(
                input_parameters["total_stripline_length"] / 2.0
                - input_parameters["feedthrough_offset"],
                0,
                input_parameters["stripline_offset"],
            ),
        )
        conductor_gap = 4.015 - 1.75
        us_launch_vac = Part.makeCone(
            input_parameters["Launch_rad"] + Units.Quantity(str(conductor_gap) + "mm"),
            Units.Quantity("1.75mm") + Units.Quantity(str(conductor_gap) + "mm"),
            input_parameters["Launch_height"],
            Base.Vector(
                -input_parameters["total_stripline_length"] / 2.0
                + input_parameters["feedthrough_offset"],
                0,
                input_parameters["stripline_offset"],
            ),
        )
        ds_launch_vac = Part.makeCone(
            input_parameters["Launch_rad"] + Units.Quantity(str(conductor_gap) + "mm"),
            Units.Quantity("1.75mm") + Units.Quantity(str(conductor_gap) + "mm"),
            input_parameters["Launch_height"],
            Base.Vector(
                input_parameters["total_stripline_length"] / 2.0
                - input_parameters["feedthrough_offset"],
                0,
                input_parameters["stripline_offset"],
            ),
        )
        launch_vac = us_launch_vac.fuse(ds_launch_vac)
        # stripline = stripline.cut(stripline_end_us)
        # stripline = stripline.cut(stripline_end_ds)
        # us_launch = us_launch.cut(stripline_end_us)
        # ds_launch = ds_launch.cut(stripline_end_ds)
        stripline = stripline.fuse(us_launch)
        stripline = stripline.fuse(ds_launch)

        rotate_at(shp=launch_vac, rotation_angles=(xyrotation, 0, 0))
        rotate_at(shp=stripline, rotation_angles=(xyrotation, 0, 0))
        return stripline, launch_vac
    else:
        rotate_at(shp=stripline, rotation_angles=(xyrotation, 0, 0))
        return stripline
