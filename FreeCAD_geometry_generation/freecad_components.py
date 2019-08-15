from FreeCAD_geometry_generation.freecad_elements import make_beampipe, make_circular_aperture, make_arc_aperture,\
     rotate_at

from FreeCAD import Base
import Part


def sma_connector(pin_length=20e-3, rotation=(0, 1, 0), location=(0, 0, 0)):
    # Reference plane is the lower side of the ceramic (vacuum side down).
    # pin_length is the length from the base of the ceramic into the vacuum.
    input_parameters = {'pin_radius': 1.24E-3 / 2, 'pin_length': pin_length,
                        'ceramic_radius': 3e-3 / 2, 'ceramic_thickness': 2.5E-3,
                        'shell_upper_radius': 6e-3 / 2, 'shell_upper_thickness': 5e-3,
                        'shell_upper_inner_radius': 3.5e-3 / 2,
                        'shell_lower_radius': 4e-3 / 2, 'shell_lower_thickness': 5e-3,
                        'shell_lower_inner_radius': 3.5e-3 / 2
                        }

    pin = Part.makeCylinder(input_parameters['pin_radius'],
                            input_parameters['pin_length'] + input_parameters['ceramic_thickness'] +
                            input_parameters['shell_upper_thickness'],
                            Base.Vector(location[0], location[1] - input_parameters['pin_length'], location[2]),
                            Base.Vector(rotation[0], rotation[1], rotation[2]))

    ceramic1 = Part.makeCylinder(input_parameters['ceramic_radius'], input_parameters['ceramic_thickness'],
                                 Base.Vector(location[0], location[1], location[2]),
                                 Base.Vector(rotation[0], rotation[1], rotation[2]))

    shell_upper1 = Part.makeCylinder(input_parameters['shell_upper_radius'], input_parameters['shell_upper_thickness'],
                                     Base.Vector(location[0], location[1] + input_parameters['ceramic_thickness'],
                                                 location[2]),
                                     Base.Vector(rotation[0], rotation[1], rotation[2]))
    shell_upper2 = Part.makeCylinder(input_parameters['shell_upper_inner_radius'],
                                     input_parameters['shell_upper_thickness'],
                                     Base.Vector(location[0], location[1] + input_parameters['ceramic_thickness'],
                                                 location[2]),
                                     Base.Vector(rotation[0], rotation[1], rotation[2]))
    shell_middle1 = Part.makeCylinder(input_parameters['shell_upper_radius'],
                                     input_parameters['ceramic_thickness'],
                                     Base.Vector(location[0], location[1], location[2]),
                                     Base.Vector(rotation[0], rotation[1], rotation[2]))
    shell_lower1 = Part.makeCylinder(input_parameters['shell_lower_radius'], input_parameters['shell_lower_thickness'],
                                     Base.Vector(location[0], location[1] - input_parameters['shell_lower_thickness'],
                                                 location[2]),
                                     Base.Vector(rotation[0], rotation[1], rotation[2]))
    shell_lower2 = Part.makeCylinder(input_parameters['shell_lower_inner_radius'],
                                     input_parameters['shell_lower_thickness'],
                                     Base.Vector(location[0], location[1] - input_parameters['shell_lower_thickness'],
                                                 location[2]),
                                     Base.Vector(rotation[0], rotation[1], rotation[2]))
    shell_middle = shell_middle1.cut(ceramic1)
    ceramic = ceramic1.cut(pin)
    shell_lower3 = shell_lower1.cut(shell_lower2)
    shell_lower = shell_lower3.fuse(shell_middle)
    shell_upper = shell_upper1.cut(shell_upper2)
    outer = shell_upper.fuse(shell_lower)

    parts = {'pin': pin, 'ceramic': ceramic, 'outer': outer}
    return parts


def ntype_connector(pin_length=20e-3, rotation=(0, 1, 0), location=(0, 0, 0)):
    # Reference plane is the lower side of the ceramic (vacuum side down).
    # pin_length is the length from the base of the ceramic into the vacuum.
    input_parameters = {'pin_radius': 3E-3 / 2, 'pin_length': pin_length,
                        'ceramic_radius': 7e-3 / 2, 'ceramic_thickness': 5E-3,
                        'shell_upper_radius': 16e-3 / 2, 'shell_upper_thickness': 10e-3,
                        'shell_upper_inner_radius': 8.03e-3 / 2,
                        'shell_lower_radius': 9e-3 / 2, 'shell_lower_thickness': 5e-3,
                        'shell_lower_inner_radius': 8.03e-3 / 2
                        }

    pin = Part.makeCylinder(input_parameters['pin_radius'],
                            input_parameters['pin_length'] + input_parameters['ceramic_thickness'] +
                            input_parameters['shell_upper_thickness'],
                            Base.Vector(location[0], location[1] - input_parameters['pin_length'], location[2]),
                            Base.Vector(rotation[0], rotation[1], rotation[2]))

    ceramic1 = Part.makeCylinder(input_parameters['ceramic_radius'], input_parameters['ceramic_thickness'],
                                 Base.Vector(location[0], location[1], location[2]),
                                 Base.Vector(rotation[0], rotation[1], rotation[2]))

    shell_upper1 = Part.makeCylinder(input_parameters['shell_upper_radius'], input_parameters['shell_upper_thickness'],
                                     Base.Vector(location[0], location[1] + input_parameters['ceramic_thickness'],
                                                 location[2]),
                                     Base.Vector(rotation[0], rotation[1], rotation[2]))
    shell_upper2 = Part.makeCylinder(input_parameters['shell_upper_inner_radius'],
                                     input_parameters['shell_upper_thickness'],
                                     Base.Vector(location[0], location[1] + input_parameters['ceramic_thickness'],
                                                 location[2]),
                                     Base.Vector(rotation[0], rotation[1], rotation[2]))
    shell_middle1 = Part.makeCylinder(input_parameters['shell_upper_radius'],
                                     input_parameters['ceramic_thickness'],
                                     Base.Vector(location[0], location[1], location[2]),
                                     Base.Vector(rotation[0], rotation[1], rotation[2]))
    shell_lower1 = Part.makeCylinder(input_parameters['shell_lower_radius'], input_parameters['shell_lower_thickness'],
                                     Base.Vector(location[0], location[1] - input_parameters['shell_lower_thickness'],
                                                 location[2]),
                                     Base.Vector(rotation[0], rotation[1], rotation[2]))
    shell_lower2 = Part.makeCylinder(input_parameters['shell_lower_inner_radius'],
                                     input_parameters['shell_lower_thickness'],
                                     Base.Vector(location[0], location[1] - input_parameters['shell_lower_thickness'],
                                                 location[2]),
                                     Base.Vector(rotation[0], rotation[1], rotation[2]))
    shell_middle = shell_middle1.cut(ceramic1)
    ceramic = ceramic1.cut(pin)
    shell_lower3 = shell_lower1.cut(shell_lower2)
    shell_lower = shell_lower3.fuse(shell_middle)
    shell_upper = shell_upper1.cut(shell_upper2)
    outer = shell_upper.fuse(shell_lower)

    parts = {'pin': pin, 'ceramic': ceramic, 'outer': outer}
    return parts


def ntype_connector_stub(pin_length=20e-3, ring_length=2e-3, rotation=(0, 0, 0), location=(0, 0, 0)):
    # Reference plane is the lower side of the ceramic (vacuum side down).
    # pin_length is the length from the base of the ceramic into the vacuum.
    input_parameters = {'pin_radius': 3E-3 / 2, 'pin_length': pin_length,
                        'shell_lower_radius': 9e-3 / 2, 'shell_lower_thickness': ring_length,
                        'shell_lower_inner_radius': 8.03e-3 / 2
                        }

    pin = Part.makeCylinder(input_parameters['pin_radius'], input_parameters['pin_length'],
                            Base.Vector(location[0], location[1] - input_parameters['pin_length'], location[2]),
                            Base.Vector(0, 1, 0))
    pin1 = rotate_at(shp=pin,
                     loc=(location[0], location[1], location[2]),
                     rotation_angles=(rotation[0], rotation[1], rotation[2]))
    shell_lower1 = Part.makeCylinder(input_parameters['shell_lower_radius'], input_parameters['shell_lower_thickness'],
                                     Base.Vector(location[0], location[1] - input_parameters['shell_lower_thickness'],
                                                 location[2]),
                                     Base.Vector(0, 1, 0))
    shell_lower1_1 = rotate_at(shp=shell_lower1,
                               loc=(location[0], location[1], location[2]),
                               rotation_angles=(rotation[0], rotation[1], rotation[2]))
    shell_lower2 = Part.makeCylinder(input_parameters['shell_lower_inner_radius'],
                                     input_parameters['shell_lower_thickness'],
                                     Base.Vector(location[0], location[1] - input_parameters['shell_lower_thickness'],
                                                 location[2]),
                                     Base.Vector(0, 1, 0))
    shell_lower2_1 = rotate_at(shp=shell_lower2,
                               loc=(location[0], location[1], location[2]),
                               rotation_angles=(rotation[0], rotation[1], rotation[2]))

    shell_lower = shell_lower1_1.cut(shell_lower2_1)

    parts = {'pin': pin1, 'outer': shell_lower}
    return parts
