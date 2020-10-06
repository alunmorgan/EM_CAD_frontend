from FreeCAD_geometry_generation.freecad_elements import make_beampipe, make_circular_aperture, \
    ModelException, rotate_at, make_taper, make_spoked_cylinder
from FreeCAD_geometry_generation.freecad_components import make_stripline_feedthrough, make_stripline
from math import pi, atan, sin , cos
from FreeCAD import Units


def longitudinal_cavity_model_orig(input_parameters):
    """ Generates the geometry for a longitudinal cavity in FreeCAD. Also writes out the geometry as STL files
       and writes a "sidecar" text file containing the input parameters used.

         Args:
            input_parameters (dict): Dictionary of input parameter names and values.
        """
    for n in input_parameters.keys():
        input_parameters[n] = Units.Quantity(input_parameters[n])
        print(n, input_parameters[n])
    print('Parsing complete')
    wg_length = input_parameters['wg_ridge_length'] + input_parameters['bc_length']
    # Height of the floor of the back cavity
    h = input_parameters['wg_ir'] + input_parameters['wg_offset'] + input_parameters['pipe_th']
    # angle implied by ridge width and height
    wg_ratio = (input_parameters['wg_ridge_width'] / 2) / \
               (input_parameters['wg_ridge_radius'] + input_parameters['wg_offset'])
    # wg_ang = 2 * atan(wg_ratio / (1 + (1 - wg_ratio ** 2) ** 0.5)) / pi * 180
    # length of full longitudinal cavity.
    lcav_length = input_parameters['cav_length'] + 2 * input_parameters['taper_length']
    # Geometry description
     # Up stream waveguide structure
    # Put in wg base
    # -brick
    # xlow = -h, xhigh = h
    # ylow = -h, yhigh = h
    # zlow = -cav_length / 2 - wg_length
    # zhigh = 0
    make_waveguide_structure()
    # Now add the machining details and coax lines
    # coax_lines()
    # wg_blend()
    # # spoke_blend()
    # wg_ridge_curve_blend()
    # bc_back_blend()
    # spoke_blend_radial()
    # -rotate, axis(0, 0, 1), angle(90), doit
    # coax_lines()
    # wg_blend()
    # # spoke_blend()
    # wg_ridge_curve_blend()
    # bc_back_blend()
    # spoke_blend_radial()
    # -rotate, axis(0, 0, 1), angle(90), doit
    # coax_lines()
    # wg_blend()
    # # spoke_blend()
    # wg_ridge_curve_blend()
    # bc_back_blend()
    # spoke_blend_radial()
    # -rotate, axis(0, 0, 1), angle(90), doit
    # coax_lines()
    # wg_blend()
    # # spoke_blend()
    # wg_ridge_curve_blend()
    # bc_back_blend()
    # spoke_blend_radial()
    # Down stream waveguide structure
    # -rotate,axis = (0, 1, 0), angle = 180
    # Put in wg base
    # -brick
    # xlow = -h, xhigh = h
    # ylow = -h, yhigh = h
    # zlow = 0, zhigh = -cav_length / 2 - wg_length
    make_waveguide_structure()
    # Now add the machining details and coax lines
    # coax_lines()
    # wg_blend()
    # # spoke_blend()
    # wg_ridge_curve_blend()
    # bc_back_blend()
    # spoke_blend_radial()
    # -rotate, axis(0, 0, 1), angle(90), doit
    # coax_lines()
    # wg_blend()
    # # spoke_blend()
    # wg_ridge_curve_blend()
    # bc_back_blend()
    # spoke_blend_radial()
    # -rotate, axis(0, 0, 1), angle(90), doit
    # coax_lines()
    # wg_blend()
    # # spoke_blend()
    # wg_ridge_curve_blend()
    # bc_back_blend()
    # spoke_blend_radial()
    # -rotate, axis(0, 0, 1), angle(90), doit
    # coax_lines()
    # wg_blend()
    # # spoke_blend()
    # wg_ridge_curve_blend()
    # bc_back_blend()
    # spoke_blend_radial()
    # Insert cavity
    # # add in the ring around the cavity
    # -gcc
    # radius = (cav_rad + wg_offset)
    # length = ring_length
    # origin = (0, 0, -ring_length / 2)
    # direction = (0, 0, 1)
    # -gcc
    # radius = ring_rad
    # length = cav_length
    # origin = (0, 0, -cav_length / 2)
    # direction = (0, 0, 1)
    # Add in the nose
    # -rotate,axis = (0, 0, 1)angle = 45
    # nose()
    # -rotate,axis = (0, 1, 0)angle = 180
    # -rotate,axis = (0, 0, 1)angle = 45
    # nose()
    # vacuum
    beampipe_vac_wire, beampipe_vac_face = make_circular_aperture(aperture_radius=input_parameters['bp_major'])
    outer_cavity_vac_wire, outer_cavity_vac_face = make_circular_aperture(aperture_radius=input_parameters['cav_rad'] +
                                                                          input_parameters['wg_offset'])
    inner_cavity_vac_wire, inner_cavity_vac_face = make_circular_aperture(aperture_radius=input_parameters['cav_rad'])
    us_pipe_vac = make_beampipe(pipe_aperture=beampipe_vac_face,
                                pipe_length=input_parameters['pipe_length'],
                                loc=(-input_parameters['cav_length'] / 2. - input_parameters['taper_length'] -
                                     input_parameters['pipe_length'] / 2., 0, 0)
                                )
    us_taper_vac = make_taper(aperture1=beampipe_vac_wire, aperture2=inner_cavity_vac_wire,
                              taper_length=input_parameters['taper_length'],
                              loc=(-input_parameters['cav_length'] / 2. - input_parameters['taper_length'], 0, 0)
                              )
    us_wg_cavity_vac = make_beampipe(pipe_aperture=outer_cavity_vac_face,
                                     pipe_length=input_parameters['cav_length'],
                                     loc=(-input_parameters['cav_length'] / 2., 0, 0)
                                     )
    cavity_vac = make_beampipe(pipe_aperture=inner_cavity_vac_face,
                               pipe_length=input_parameters['cav_length'],
                               loc=(0, 0, 0)
                               )
    ds_wg_cavity_vac = make_beampipe(pipe_aperture=outer_cavity_vac_face,
                                     pipe_length=input_parameters['cav_length'],
                                     loc=(input_parameters['cav_length'] / 2., 0, 0)
                                     )
    ds_taper_vac = make_taper(aperture1=inner_cavity_vac_wire, aperture2=beampipe_vac_wire,
                              taper_length=input_parameters['taper_length'],
                              loc=(input_parameters['cav_length'] / 2., 0, 0)
                              )
    ds_pipe_vac = make_beampipe(pipe_aperture=beampipe_vac_face,
                                pipe_length=input_parameters['pipe_length'],
                                loc=(input_parameters['cav_length'] / 2. + input_parameters['taper_length'] +
                                      input_parameters['pipe_length'] / 2., 0, 0)
                                )
    inner_spokes_wire, inner_spokes_face = make_spoked_cylinder(outer_radius=input_parameters['cav_rad'] +
                                                                          input_parameters['wg_offset'],
                                                                 inner_radius=input_parameters['cav_rad'],
                                                                insert_angle=input_parameters['spoke_angle'],
                                                                blend_radius=Units.Quantity('0 mm'))
    us_spokes = make_beampipe(pipe_aperture=inner_spokes_face,
                                     pipe_length=input_parameters['cav_length'],
                                     loc=(-input_parameters['cav_length'] / 2., 0, 0)
                                     )
    ds_spokes = make_beampipe(pipe_aperture=inner_spokes_face,
                                     pipe_length=input_parameters['cav_length'],
                                     loc=(input_parameters['cav_length'] / 2., 0, 0)
                                     )
    us_waveguide_vacuum = us_wg_cavity_vac.cut(us_spokes)
    ds_waveguide_vacuum = ds_wg_cavity_vac.cut(ds_spokes)
    # except Exception as e:
    #     raise ModelException(e)
    # An entry in the parts dictionary corresponds to an STL file. This is useful for parts of differing materials.
    parts = {'us_pipe': us_pipe_vac, 'ds_pipe': ds_pipe_vac, 'cavity': cavity_vac,
             'us_taper': us_taper_vac, 'ds_taper': ds_taper_vac,
             'us_wg_cavity': us_waveguide_vacuum, 'ds_wg_cavity': ds_waveguide_vacuum,
             'us_spokes': us_spokes, 'ds_spokes': ds_spokes}
    return parts


def make_waveguide_structure():
    pass

    # # Putting on the main spokes
    # spoke_angles = [45, 360, 90]
    # for dr in spoke_angles
    #     -gbor
    #     range = (-spoke_angle / 2 + dr, spoke_angle / 2 + dr)
    #     # point= (z,r)
    #     point = (-cav_length / 2, 0)
    #     point = (-cav_length / 2, (cav_rad + wg_offset))
    #     point = (-cav_length / 2 - wg_length, (cav_rad + wg_offset))
    #     point = (-cav_length / 2 - wg_length, 0)
    #
    #     # putting in the gap
    #     -gbor
    #     range = (-spoke_angle / 2 + dr, spoke_angle / 2 + dr)
    #     # point= (z,r)
    #     point = (-cav_length / 2 - 1E-3, cav_rad)
    #     point = (-cav_length / 2 - wg_length, cav_rad)
    #     point = (-cav_length / 2 - wg_length, cav_rad - spoke_gap)
    #     point = (-cav_length / 2 - 1E-3, cav_rad - spoke_gap)
    #     point = (-cav_length / 2 - 1E-3, cav_rad)
    #
    #     hs = 1, 6, 1
    #
    #     # putting in the spring fingers
    #     spring_width = input_parameters['wg_ridge_length'] + input_parameters['bc_length'] - 3E-3
    #     spring_st = -input_parameters['cav_length'] / 2 - input_parameters['wg_length'] + 1.5e-3
    #     sx1 = (cav_rad - spoke_gap) * sin((spoke_angle / 2 + dr) * pi / 180)
    #     sy1 = (cav_rad - spoke_gap) * cos((spoke_angle / 2 + dr) * pi / 180)
    #     sx2 = (cav_rad - spoke_gap) * sin((-spoke_angle / 2 + dr) * pi / 180)
    #     sy2 = (cav_rad - spoke_gap) * cos((-spoke_angle / 2 + dr) * pi / 180)
    #     sx3 = (cav_rad + 0.5e-3) * sin((spoke_angle / 4 + dr) * pi / 180)
    #     sy3 = (cav_rad + 0.5e-3) * cos((spoke_angle / 4 + dr) * pi / 180)
    #     sx4 = (cav_rad + 0.5e-3) * sin((-spoke_angle / 4 + dr) * pi / 180)
    #     sy4 = (cav_rad + 0.5e-3) * cos((-spoke_angle / 4 + dr) * pi / 180)
    #     -ggcylinder
    #     range = (spring_st + (hs - 1) * spring_width, spring_st + hs * spring_width - spring_gap)
    #
    #     point = (sx1, sy1)
    #     point = (sx3, sy3)
    #     point = (sx4, sy4)
    #     point = (sx2, sy2)
    #     point = (sx1, sy1)
    #
    # # Putting in the waveguide ridges
    # -brick
    # xlow = -(cav_rad + wg_offset), xhigh = (cav_rad + wg_offset)
    # ylow = -wg_ridge_width / 2, yhigh = wg_ridge_width / 2
    # zlow = -cav_length / 2 - wg_ridge_length + wg_ridge_width / 2, zhigh = -cav_length / 2
    #
    #
    # -brick
    # xlow = -wg_ridge_width / 2, xhigh = wg_ridge_width / 2
    # ylow = -(cav_rad + wg_offset), yhigh = (cav_rad + wg_offset)
    # zlow = -cav_length / 2 - wg_ridge_length + wg_ridge_width / 2, zhigh = -cav_length / 2
    #
    # # curved end of waveguide
    # -gcc
    # radius = wg_ridge_width / 2
    # length = 2 * (cav_rad + wg_offset)
    # origin = (0, -(cav_rad + wg_offset), -cav_length / 2 - wg_ridge_length + wg_ridge_width / 2)
    # direction = (0, 1, 0)
    #
    # -gcc
    # radius = wg_ridge_width / 2
    # length = 2 * (cav_rad + wg_offset)
    # origin = (-(cav_rad + wg_offset), 0, -cav_length / 2 - wg_ridge_length + wg_ridge_width / 2)
    # direction = (1, 0, 0)
    #
    # gap_list = [0, 350, 90]
    # for dz in gap_list
    #     # putting in the gap
    #     -gbor
    #     range = (-wg_ang + dz, wg_ang + dz)
    #     # point= (z,r)
    #     point = (-cav_length / 2, (wg_ridge_radius + wg_offset))
    #     point = (-cav_length / 2 - wg_ridge_length, (wg_ridge_radius + wg_offset))
    #     point = (-cav_length / 2 - wg_ridge_length, (wg_ridge_radius + wg_offset) + wg_gap)
    #     point = (-cav_length / 2, (wg_ridge_radius + wg_offset) + wg_gap)
    #     point = (-cav_length / 2, (wg_ridge_radius + wg_offset))
    #

def coax_lines():
    pass
    # # first vacuum for the coax outer radius
    # -gcc
    # material = vacuum
    # radius = coax_outer_rad
    # length = INF
    # origin = (0, (wg_ridge_radius + wg_offset), -cav_length / 2 - wg_ridge_length + coax_z_offset)
    # direction = (0, 1, 0)
    # # Now the centre pins
    # -gcc
    # material = coax_pin_mat
    # radius = pin_rad
    # length = INF
    # origin = (0, (wg_ir + wg_offset) + 2e-3, -cav_length / 2 - wg_ridge_length + coax_z_offset)
    # direction = (0, 1, 0)


def wg_blend():
    pass
    # # Putting in the wg curves.
    # x_r = wg_ridge_width / 2
    # y_r = h
    # x_i = x_r + m_rad1
    # y_i = y_r
    # x_c = x_r
    # y_c = y_r + m_rad1
    #
    # -ggcylinder
    # range = (-cav_length / 2 - wg_ridge_length + wg_ridge_width / 2, -cav_length / 2)
    # point = (x_c, y_c)
    # arc, radius = m_rad1, size = small, type = counterclockwise
    # point = (x_i, y_i)
    # point = (x_r, y_r)
    # point = (x_c, y_c)
    #
    # -ggcylinder
    # range = (-cav_length / 2 - wg_ridge_length + wg_ridge_width / 2, -cav_length / 2)
    # point = (-x_c, y_c)
    # arc, radius = m_rad1, size = small, type = clockwise
    # point = (-x_i, y_i)
    # point = (-x_r, y_r)
    # point = (-x_c, y_c)


def spoke_blend():
    pass
    # # Putting in the spoke curves.
    # spoke_angle_rad = spoke_angle / 2 * pi / 180
    # phi = pi / 4 - spoke_angle_rad
    # theta = atan(m_rad1 / (((wg_ir + wg_offset) + pipe_th) + m_rad1))
    # r1 = ((wg_ir + wg_offset) + pipe_th) - ((wg_ir + wg_offset) + pipe_th) * (
    #             sin(spoke_angle_rad) - 1 + cos(spoke_angle_rad)) / cos(spoke_angle_rad)
    # x_r = r1 * cos(phi)
    # y_r = (r1 + (m_rad1 / 2) / cos(phi)) * sin(phi)  # + m_rad1 * tan(phi))
    # x_c = x_r
    # y_c = y_r - m_rad1
    # x_i = x_r + m_rad1 / 2
    # y_i = y_r
    #
    # -ggcylinder
    # range = (-cav_length / 2 - wg_length, -cav_length / 2)
    # point = (x_i, y_i)
    # arc, radius = m_rad1, size = small, type = counterclockwise
    # point = (x_c, y_c)
    # point = (x_r, y_r)
    # point = (x_i, y_i)
    # phi = pi / 4 + spoke_angle / 2 * pi / 180
    # spoke_angle_rad = spoke_angle / 2 * pi / 180
    # theta = atan(m_rad1 / ((wg_ir + wg_offset) + m_rad1))
    # r1 = ((wg_ir + wg_offset) + pipe_th) - ((wg_ir + wg_offset) + pipe_th) * (
    #             sin(spoke_angle_rad) - 1 + cos(spoke_angle_rad)) / cos(spoke_angle_rad)
    # x_r = (r1 + (m_rad1 / 2) / cos(phi)) * cos(phi)
    # y_r = r1 * sin(phi)
    # x_c = x_r - m_rad1
    # y_c = y_r
    # x_i = x_r
    # y_i = y_r + m_rad1 / 2
    #
    # -ggcylinder
    # range = (-cav_length / 2 - wg_length, -cav_length / 2)
    #  point = (x_c, y_c)
    # arc, radius = m_rad1, size = small, type = counterclockwise
    # point = (x_i, y_i)
    # point = (x_r, y_r)
    # point = (x_c, y_c)


def wg_ridge_curve_blend():
    pass
    # # Adding the machining detail for the back curve of the waveguide ridge
    # -gbor
    # originprime = (0, h, -cav_length / 2 - wg_ridge_length + wg_ridge_width / 2)
    # zprimedirection = (0, 1, 0)
    # rprimedirection = (1, 0, 0)
    # range = (0, 360)
    # point = (m_rad1, wg_ridge_width / 2)
    # arc, radius = m_rad1, size = small, type = clockwise
    # point = (0, wg_ridge_width / 2 + m_rad1)
    # point = (0, wg_ridge_width / 2)
    # point = (m_rad1, wg_ridge_width / 2)

def bc_back_blend():
    pass
    # -ggcylinder
    # originprime = (0, h, -cav_length / 2 - wg_length)
    # xprimedirection = (0, 1, 0)
    # yprimedirection = (0, 0, 1)
    # range = (-h, h)
    #  point = (0, m_rad1)
    # arc, radius = m_rad1, size = small, type = counterclockwise
    # point = (m_rad1, 0)
    # point = (0, 0)
    # point = (0, m_rad1)


def spoke_blend_radial():
    pass
    # # Putting in the spoke curves.
    # spoke_angle_rad = spoke_angle / 2 * pi / 180
    # phi = pi / 4 + spoke_angle_rad
    # x_r = 0
    # y_r = 0
    # x_c = x_r
    # y_c = y_r - m_rad1
    # x_i = x_r + m_rad1
    # y_i = y_r
    #
    # -ggcylinder
    # originprime = (0, 0, -cav_length / 2 - wg_length)
    # xprimedirection = (0, 0, 1)
    # yprimedirection = (cos(phi), sin(phi), 0)
    # range = ((cav_rad + wg_offset), 0)
    # point = (x_i, y_i)
    # arc, radius = m_rad1, size = small, type = counterclockwise
    # point = (x_c, y_c)
    # point = (x_r, y_r)
    # point = (x_i, y_i)
    #
    # spoke_angle_rad, spoke_angle / 2 * pi / 180)
    # phi = pi / 4 - spoke_angle_rad
    # x_r, 0)
    # y_r, 0)
    # x_c, x_r)
    # y_c, y_r + m_rad1)
    # x_i, x_r + m_rad1)
    # y_i, y_r)
    #
    # -ggcylinder
    # originprime = (0, 0, -cav_length / 2 - wg_length)
    # xprimedirection = (0, 0, 1)
    # yprimedirection = (cos(phi), sin(phi), 0)
    # range = ((cav_rad + wg_offset), 0)
    # point = (x_c, y_c)
    # arc, radius = m_rad1, size = small, type = counterclockwise
    # point = (x_i, y_i)
    # point = (x_r, y_r)
    # point = (x_c, y_c)


def nose():
    pass
    # -gbor
    # material = cav_mat
    # originprime = (0, 0, -cav_length / 2)
    # zprimedirection = (0, 0, 1)
    # rprimedirection = (1, 0, 0)
    # range = (0, 360)
    # xscaleprime = 1
    # yscaleprime = pipe_minor / pipe_major
    # point = (0, bp_major)
    # point = (NoseStub - NoseTipCurve, bp_major)
    # arc, radius = NoseTipCurve, size = small, type = counterclockwise
    # point = (NoseStub - NoseTipCurve, bp_major + 2 * NoseTipCurve)
    # point = (NoseBaseCurve, bp_major + 2 * NoseTipCurve)
    # arc, radius = NoseBaseCurve, size = small, type = clockwise
    # point = (0, bp_major + 2 * NoseTipCurve + NoseBaseCurve)
    # point = (0, bp_major)



##################################################

####### REFERENCE ###
    # # try:
    # for n in input_parameters.keys():
    #     input_parameters[n] = Units.Quantity(input_parameters[n])
    #     print(n, input_parameters[n])
    # print('Parsing complete')
    #
    # stripline_mid_section_length = input_parameters['total_stripline_length'] - \
    #                                2 * input_parameters['stripline_taper_length']
    # # total_cavity_length is the total stipline length plus the additional cavity length at each end.
    # total_cavity_length = input_parameters['total_stripline_length'] + \
    #                       2 * input_parameters['additional_cavity_length']
    # pipe_extension_z_centre = (input_parameters['pipe_length'] + total_cavity_length) / 2. + input_parameters[
    #     'pipe_stub_length'] / 2.
    # pipe_stub_z_centre = (total_cavity_length + input_parameters['pipe_stub_length']) / 2.
    # # Make cavity
    # # If you try to make the taper to a point the meshing errors. As this is not mechanically achievable it is OK
    # # to put a small step in to releive that constraint.
    # # Also the EM simulations will be running at 60um mesh density at the most.
    # taper_end_step = Units.Quantity('20 um')
    # pipe_vac_wire, pipe_vac_face = make_circular_aperture(aperture_radius=input_parameters['pipe_radius'])
    # pipe_vac_taper_wire, pipe_vac_taper_face = make_cylinder_with_inserts(outer_radius=input_parameters['pipe_radius'] +
    #                                                                                    taper_end_step,
    #                                                                       inner_radius=input_parameters['pipe_radius'],
    #                                                                       insert_angle=input_parameters[
    #                                                                           'cavity_insert_angle'],
    #                                                                       blend_radius=taper_end_step / 4)
    #
    # cavity_vac_wire, cavity_vac_face = make_cylinder_with_inserts(outer_radius=input_parameters['cavity_radius'],
    #                                                               inner_radius=input_parameters['pipe_radius'],
    #                                                               insert_angle=input_parameters[
    #                                                                   'cavity_insert_angle'],
    #                                                               blend_radius=Units.Quantity('2 mm'))
    # us_pipe_vac = make_beampipe(pipe_aperture=pipe_vac_face,
    #                             pipe_length=input_parameters['pipe_length'],
    #                             loc=(-(total_cavity_length + input_parameters['pipe_length']) / 2., 0, 0)
    #                             )
    # ds_pipe_vac = make_beampipe(pipe_aperture=pipe_vac_face,
    #                             pipe_length=input_parameters['pipe_length'],
    #                             loc=((total_cavity_length + input_parameters['pipe_length']) / 2., 0, 0)
    #                             )
    # us_taper_vac = make_taper(aperture1=pipe_vac_taper_wire, aperture2=cavity_vac_wire,
    #                           taper_length=(total_cavity_length - stripline_mid_section_length) / 2.,
    #                           loc=(-total_cavity_length / 2., 0, 0)
    #                           )
    # ds_taper_vac = make_taper(aperture1=cavity_vac_wire, aperture2=pipe_vac_taper_wire,
    #                           taper_length=(total_cavity_length - stripline_mid_section_length) / 2.,
    #                           loc=(stripline_mid_section_length / 2., 0, 0)
    #                           )
    #
    # cavity_vac = make_beampipe(pipe_aperture=cavity_vac_face, pipe_length=stripline_mid_section_length)
    #
    # pipe_wire, pipe_face = make_circular_aperture(aperture_radius=input_parameters['pipe_radius'] +
    #                                                               input_parameters['pipe_thickness'])
    # # Additional 3 degrees is to give ~few mm wall thickness on radial sides.
    # pipe_taper_wire, pipe_taper_face = make_cylinder_with_inserts(outer_radius=input_parameters['pipe_radius'] +
    #                                                                            input_parameters['pipe_thickness'] +
    #                                                                            Units.Quantity('2 mm'),
    #                                                               inner_radius=input_parameters['pipe_radius'] +
    #                                                                            input_parameters['pipe_thickness'],
    #                                                               insert_angle=input_parameters['cavity_insert_angle'] -
    #                                                                            Units.Quantity('3 deg'))
    #
    # cavity_wire, cavity_face = make_cylinder_with_inserts(outer_radius=input_parameters['cavity_radius'] +
    #                                                                    input_parameters['pipe_thickness'],
    #                                                       inner_radius=input_parameters['pipe_radius'] +
    #                                                                    input_parameters['pipe_thickness'],
    #                                                       insert_angle=input_parameters['cavity_insert_angle'] -
    #                                                                    Units.Quantity('3 deg'))
    #
    # us_pipe_extension = make_beampipe(pipe_aperture=pipe_face,
    #                                   pipe_length=input_parameters['pipe_length'] -
    #                                               input_parameters['pipe_stub_length'],
    #                                   loc=(-pipe_extension_z_centre, 0, 0)
    #                                   )
    # ds_pipe_extension = make_beampipe(pipe_aperture=pipe_face,
    #                                   pipe_length=input_parameters['pipe_length'] -
    #                                               input_parameters['pipe_stub_length'],
    #                                   loc=(pipe_extension_z_centre, 0, 0)
    #                                   )
    # us_pipe_stub = make_beampipe(pipe_aperture=pipe_face, pipe_length=input_parameters['pipe_stub_length'],
    #                              loc=(-pipe_stub_z_centre, 0, 0)
    #                              )
    # ds_pipe_stub = make_beampipe(pipe_aperture=pipe_face, pipe_length=input_parameters['pipe_stub_length'],
    #                              loc=(pipe_stub_z_centre, 0, 0)
    #                              )
    # us_taper = make_taper(aperture1=pipe_taper_wire, aperture2=cavity_wire,
    #                       taper_length=(total_cavity_length - stripline_mid_section_length) / 2.,
    #                       loc=(-total_cavity_length / 2., 0, 0)
    #                       )
    # ds_taper = make_taper(aperture1=cavity_wire, aperture2=pipe_taper_wire,
    #                       taper_length=(total_cavity_length - stripline_mid_section_length) / 2.,
    #                       loc=(stripline_mid_section_length / 2., 0, 0)
    #                       )
    # cavity = make_beampipe(pipe_aperture=cavity_face,
    #                        pipe_length=stripline_mid_section_length)
    # # Basic feedthrough
    # n_parts_us_upper, feedthrough_vaccum_us_upper = make_stripline_feedthrough(input_parameters, z_loc='us',
    #                                                                            xyrotation=0)
    # n_parts_us_lower, feedthrough_vaccum_us_lower = make_stripline_feedthrough(input_parameters, z_loc='us',
    #                                                                            xyrotation=180)
    # n_parts_ds_upper, feedthrough_vaccum_ds_upper = make_stripline_feedthrough(input_parameters, z_loc='ds',
    #                                                                            xyrotation=0)
    # n_parts_ds_lower, feedthrough_vaccum_ds_lower = make_stripline_feedthrough(input_parameters, z_loc='ds',
    #                                                                            xyrotation=180)
    #
    # # Basic striplines
    # stripline_upper = make_stripline(input_parameters, xyrotation=-90)
    # stripline_lower = make_stripline(input_parameters, xyrotation=90)
    #
    # feedthrough_vac = feedthrough_vaccum_us_upper.fuse(feedthrough_vaccum_us_lower)
    # feedthrough_vac = feedthrough_vac.fuse(feedthrough_vaccum_ds_upper)
    # feedthrough_vac = feedthrough_vac.fuse(feedthrough_vaccum_ds_lower)
    #
    # chamber_vac = us_taper_vac.fuse(ds_taper_vac)
    # chamber_vac = chamber_vac.fuse(cavity_vac)
    # chamber_vac = chamber_vac.fuse(us_pipe_vac)
    # chamber_vac = chamber_vac.fuse(ds_pipe_vac)
    # rotate_at(shp=chamber_vac, rotation_angles=(-90, 0, 0))
    # vac = chamber_vac.fuse(feedthrough_vac)
    #
    # rotate_at(shp=feedthrough_vac, rotation_angles=(-90, 0, 0))
    # us_pipe_stub = us_pipe_stub.cut(us_pipe_vac)
    # ds_pipe_stub = ds_pipe_stub.cut(ds_pipe_vac)
    # us_taper = us_taper.cut(us_taper_vac)
    # us_taper = us_taper.cut(feedthrough_vac)
    # ds_taper = ds_taper.cut(ds_taper_vac)
    # ds_taper = ds_taper.cut(feedthrough_vac)
    # cavity = cavity.cut(cavity_vac)
    # us_pipe_extension = us_pipe_extension.cut(us_pipe_vac)
    # ds_pipe_extension = ds_pipe_extension.cut(ds_pipe_vac)
    #
    # outer = us_taper.fuse(ds_taper)
    # outer = outer.fuse(cavity)
    # outer = outer.fuse(us_pipe_stub)
    # outer = outer.fuse(ds_pipe_stub)
    # rotate_at(shp=outer, rotation_angles=(-90, 0, 0))
    # outer = outer.cut(vac)
    #
    # trimmed_outers = n_parts_us_upper['outer'].fuse(n_parts_us_lower['outer'])
    # trimmed_outers = trimmed_outers.fuse(n_parts_ds_upper['outer'])
    # trimmed_outers = trimmed_outers.fuse(n_parts_ds_lower['outer'])
    # trimmed_outers = trimmed_outers.cut(chamber_vac)
    # outer = outer.fuse(trimmed_outers)
    #
    # stripline_upper = stripline_upper.cut(n_parts_us_upper['pin'])
    # stripline_upper = stripline_upper.cut(n_parts_ds_upper['pin'])
    # stripline_lower = stripline_lower.cut(n_parts_us_lower['pin'])
    # stripline_lower = stripline_lower.cut(n_parts_ds_lower['pin'])
    #
    # # except Exception as e:
    # #     raise ModelException(e)
    # # An entry in the parts dictionary corresponds to an STL file. This is useful for parts of differing materials.
    # # parts = {'wire1': pipe_vac_taper_wire, 'wire2': cavity_vac_wire}
    # parts = {'us_pipe': us_pipe_extension, 'ds_pipe': ds_pipe_extension, 'cavity': outer,
    #          'vac': vac,
    #          'stripline_upper': stripline_upper, 'stripline_lower': stripline_lower,
    #          'pin_us_upper': n_parts_us_upper['pin'], 'pin_us_lower': n_parts_us_lower['pin'],
    #          'pin_ds_upper': n_parts_ds_upper['pin'], 'pin_ds_lower': n_parts_ds_lower['pin']}
    # return parts
