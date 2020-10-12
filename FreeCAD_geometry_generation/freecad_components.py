from FreeCAD_geometry_generation.freecad_elements import make_beampipe, make_arc_aperture,\
     rotate_at, make_taper
from math import pi
from FreeCAD import Base, Units
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


def ntype_connector_stub(pin_length=Units.Quantity('20 mm'), ring_length=Units.Quantity('2 mm'),
                         rotation=(Units.Quantity('0 deg'), Units.Quantity('0 deg'), Units.Quantity('0 deg')),
                         location=(Units.Quantity('0 mm'), Units.Quantity('0 mm'), Units.Quantity('0 mm')),
                         rotate_around_zero=(Units.Quantity('0 deg'), Units.Quantity('0 deg'), Units.Quantity('0 deg'))):
    # Reference plane is the lower side of the ceramic (vacuum side down).
    # pin_length is the length from the base of the ceramic into the vacuum.
    input_parameters = {'pin_radius': Units.Quantity('3 mm') / 2, 'pin_length': pin_length,
                        'shell_lower_radius': Units.Quantity('9 mm') / 2, 'shell_lower_thickness': ring_length,
                        'shell_lower_inner_radius': Units.Quantity('8.03 mm') / 2
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

    rotate_at(shp=shell_lower,
              rotation_angles=(rotate_around_zero[0], rotate_around_zero[1], rotate_around_zero[2]))
    rotate_at(shp=pin1,
              rotation_angles=(rotate_around_zero[0], rotate_around_zero[1], rotate_around_zero[2]))
    rotate_at(shp=shell_lower2_1,
              rotation_angles=(rotate_around_zero[0], rotate_around_zero[1], rotate_around_zero[2]))
    parts = {'pin': pin1, 'outer': shell_lower, 'vac': shell_lower2_1}
    return parts


def make_nose(aperture_radius, ring_width, ring_length, blend,
              loc=(Units.Quantity('0 mm'), Units.Quantity('0 mm'), Units.Quantity('0 mm')),
              rot=(Units.Quantity('0 deg'), Units.Quantity('0 deg'), Units.Quantity('0 deg'))):
    inner = Part.makeCylinder(aperture_radius, ring_length - ring_width / 2., Base.Vector(loc), Base.Vector(1, 0, 0))
    outer = Part.makeCylinder(aperture_radius + ring_width, ring_length - ring_width / 2., Base.Vector(loc), Base.Vector(1, 0, 0))
    blending = Part.makeCylinder(aperture_radius + ring_width + blend,  blend,
                                 Base.Vector(loc), Base.Vector(1, 0, 0))
    ring = outer.cut(inner)
    blend_ring = blending.cut(outer)
    nose_tip = Part.makeTorus(aperture_radius + ring_width / 2., ring_width / 2.,
                              Base.Vector(loc[0] + ring_length - ring_width / 2., loc[1], loc[2]),
                              Base.Vector(1, 0, 0))
    blend_curve = Part.makeTorus(aperture_radius + ring_width + blend, blend,
                              Base.Vector(loc[0] + blend, loc[1], loc[2]),
                              Base.Vector(1, 0, 0))
    nose = ring.fuse(nose_tip)
    nose = nose.fuse(blend_ring)
    nose = nose.cut(blend_curve)
    nose = rotate_at(nose, loc=loc, rotation_angles=rot)
    return nose


def make_stripline_feedthrough(input_parameters, z_loc='us', xyrotation=0):
    stripline_mid_section_length = input_parameters['total_stripline_length'] - \
                                   2 * input_parameters['stripline_taper_length']
    # total_cavity_length is the total stipline length plus the additional cavity length at each end.
    total_cavity_length = input_parameters['total_stripline_length'] + \
                          2 * input_parameters['additional_cavity_length']
    # Calculating the joining point of the outer conductor to the taper.
    n_type_outer_radius = Units.Quantity('9 mm') / 2.
    port_offset = input_parameters['total_stripline_length'] / 2. - input_parameters['feedthrough_offset']
    feedthrough_outer_x = port_offset + n_type_outer_radius
    feedthrough_outer_y = input_parameters['cavity_radius'] - \
                          (input_parameters['cavity_radius'] - input_parameters['pipe_radius']) / \
                          (total_cavity_length / 2. - stripline_mid_section_length / 2.) * \
                          feedthrough_outer_x
    # Pin stops half way through the stripline.
    pin_length = input_parameters['cavity_radius'] - input_parameters['stripline_offset'] + \
                 input_parameters['pipe_thickness'] - input_parameters['stripline_thickness'] / 2.
    ring_start_y = input_parameters['cavity_radius'] + input_parameters['pipe_thickness']
    ring_length = ring_start_y - feedthrough_outer_y + Units.Quantity('2 mm')
    if z_loc == 'us':
        z = -1
    elif z_loc == 'ds':
        z = 1
    else:
        raise ValueError
    n_parts = ntype_connector_stub(pin_length=pin_length, ring_length=ring_length,
                                    location=(z * port_offset, ring_start_y, 0),
                                    rotation=(0, 0, 0), rotate_around_zero=(xyrotation, 0, 0))
    n_type_outer_inner_radius = Units.Quantity('8.03 mm') / 2.
    feedthrough_vaccum_length = input_parameters['cavity_radius'] + input_parameters['pipe_thickness']
    feedthrough_vaccum = Part.makeCylinder(n_type_outer_inner_radius, feedthrough_vaccum_length,
                                            Base.Vector(z * port_offset, 0, 0),
                                            Base.Vector(0, -1, 0))
    rotate_at(shp=feedthrough_vaccum,
              rotation_angles=(xyrotation, 0, 0))
    return n_parts, feedthrough_vaccum


def make_stripline(input_parameters, xyrotation=0):
    stripline_mid_section_length = input_parameters['total_stripline_length'] - \
                                   2 * input_parameters['stripline_taper_length']
    stripline_main_wire, stripline_main_face = \
        make_arc_aperture(arc_inner_radius=input_parameters['stripline_offset'],
                          arc_outer_radius=input_parameters['stripline_offset'] +
                                           input_parameters['stripline_thickness'],
                          arc_length=input_parameters['stripline_width'],
                          blend_radius=Units.Quantity('0.75 mm'))
    stripline_taper_end_wire, stripline_taper_end_face = \
        make_arc_aperture(arc_inner_radius=input_parameters['stripline_offset'],
                          arc_outer_radius=input_parameters['stripline_offset'] +
                                           input_parameters['stripline_thickness'],
                          arc_length=input_parameters['stripline_taper_end_width'],
                          blend_radius=Units.Quantity('0.75 mm'))

    stripline_main = make_beampipe(pipe_aperture=stripline_main_face,
                                   pipe_length=stripline_mid_section_length,
                                   loc=(0, 0, 0))
    stripline_taper_us = make_taper(aperture1=stripline_taper_end_wire,
                                    aperture2=stripline_main_wire,
                                    taper_length=input_parameters['stripline_taper_length'],
                                    loc=(-input_parameters['stripline_taper_length'] -
                                         stripline_mid_section_length / 2., 0, 0))
    stripline_taper_ds = make_taper(aperture1=stripline_main_wire,
                                    aperture2=stripline_taper_end_wire,
                                    taper_length=input_parameters['stripline_taper_length'],
                                    loc=(stripline_mid_section_length / 2., 0, 0))
    stripline = stripline_main.fuse(stripline_taper_us)
    stripline = stripline.fuse(stripline_taper_ds)
    rotate_at(shp=stripline,
              rotation_angles=(xyrotation, 0, 0))
    return stripline
