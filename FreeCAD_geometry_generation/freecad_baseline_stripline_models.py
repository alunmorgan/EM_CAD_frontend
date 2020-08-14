from FreeCAD_geometry_generation.freecad_elements import make_beampipe, make_circular_aperture, \
    ModelException, rotate_at, make_taper, make_cylinder_with_inserts
from FreeCAD_geometry_generation.freecad_components import make_stripline_feedthrough, make_stripline
from math import pi
from FreeCAD import Units


def stripline_model_curved_tapered_2_blade(input_parameters):
    """ Generates the geometry for a simplified stripline in FreeCAD. Also writes out the geometry as STL files
       and writes a "sidecar" text file containing the input parameters used.

         Args:
            input_parameters (dict): Dictionary of input parameter names and values.
        """

    # try:
    for n in input_parameters.keys():
        input_parameters[n] = Units.Quantity(input_parameters[n])
        print(n, input_parameters[n])
    print('Parsing complete')

    stripline_mid_section_length = input_parameters['total_stripline_length'] - \
                                   2 * input_parameters['stripline_taper_length']
    # total_cavity_length is the total stipline length plus the additional cavity length at each end.
    total_cavity_length = input_parameters['total_stripline_length'] + \
                          2 * input_parameters['additional_cavity_length']
    pipe_extension_z_centre = (input_parameters['pipe_length'] + total_cavity_length) / 2. + input_parameters[
        'pipe_stub_length'] / 2.
    pipe_stub_z_centre = (total_cavity_length + input_parameters['pipe_stub_length']) / 2.
    # Make cavity
    # If you try to make the taper to a point the meshing errors. As this is not mechanically achievable it is OK
    # to put a small step in to releive that constraint.
    # Also the EM simulations will be running at 60um mesh density at the most.
    taper_end_step = Units.Quantity('20 um')
    pipe_vac_wire, pipe_vac_face = make_circular_aperture(aperture_radius=input_parameters['pipe_radius'])
    pipe_vac_taper_wire, pipe_vac_taper_face = make_cylinder_with_inserts(outer_radius=input_parameters['pipe_radius'] +
                                                                                       taper_end_step,
                                                                          inner_radius=input_parameters['pipe_radius'],
                                                                          insert_angle=input_parameters[
                                                                              'cavity_insert_angle'],
                                                                          blend_radius=taper_end_step / 4)

    cavity_vac_wire, cavity_vac_face = make_cylinder_with_inserts(outer_radius=input_parameters['cavity_radius'],
                                                                  inner_radius=input_parameters['pipe_radius'],
                                                                  insert_angle=input_parameters[
                                                                      'cavity_insert_angle'],
                                                                  blend_radius=Units.Quantity('2 mm'))
    us_pipe_vac = make_beampipe(pipe_aperture=pipe_vac_face,
                                pipe_length=input_parameters['pipe_length'],
                                loc=(-(total_cavity_length + input_parameters['pipe_length']) / 2., 0, 0)
                                )
    ds_pipe_vac = make_beampipe(pipe_aperture=pipe_vac_face,
                                pipe_length=input_parameters['pipe_length'],
                                loc=((total_cavity_length + input_parameters['pipe_length']) / 2., 0, 0)
                                )
    us_taper_vac = make_taper(aperture1=pipe_vac_taper_wire, aperture2=cavity_vac_wire,
                              taper_length=(total_cavity_length - stripline_mid_section_length) / 2.,
                              loc=(-total_cavity_length / 2., 0, 0)
                              )
    ds_taper_vac = make_taper(aperture1=cavity_vac_wire, aperture2=pipe_vac_taper_wire,
                              taper_length=(total_cavity_length - stripline_mid_section_length) / 2.,
                              loc=(stripline_mid_section_length / 2., 0, 0)
                              )

    cavity_vac = make_beampipe(pipe_aperture=cavity_vac_face, pipe_length=stripline_mid_section_length)

    pipe_wire, pipe_face = make_circular_aperture(aperture_radius=input_parameters['pipe_radius'] +
                                                                  input_parameters['pipe_thickness'])
    # Additional 3 degrees is to give ~few mm wall thickness on radial sides.
    pipe_taper_wire, pipe_taper_face = make_cylinder_with_inserts(outer_radius=input_parameters['pipe_radius'] +
                                                                               input_parameters['pipe_thickness'] +
                                                                               Units.Quantity('2 mm'),
                                                                  inner_radius=input_parameters['pipe_radius'] +
                                                                               input_parameters['pipe_thickness'],
                                                                  insert_angle=input_parameters['cavity_insert_angle'] -
                                                                               Units.Quantity('3 deg'))

    cavity_wire, cavity_face = make_cylinder_with_inserts(outer_radius=input_parameters['cavity_radius'] +
                                                                       input_parameters['pipe_thickness'],
                                                          inner_radius=input_parameters['pipe_radius'] +
                                                                       input_parameters['pipe_thickness'],
                                                          insert_angle=input_parameters['cavity_insert_angle'] -
                                                                       Units.Quantity('3 deg'))

    us_pipe_extension = make_beampipe(pipe_aperture=pipe_face,
                                      pipe_length=input_parameters['pipe_length'] -
                                                  input_parameters['pipe_stub_length'],
                                      loc=(-pipe_extension_z_centre, 0, 0)
                                      )
    ds_pipe_extension = make_beampipe(pipe_aperture=pipe_face,
                                      pipe_length=input_parameters['pipe_length'] -
                                                  input_parameters['pipe_stub_length'],
                                      loc=(pipe_extension_z_centre, 0, 0)
                                      )
    us_pipe_stub = make_beampipe(pipe_aperture=pipe_face, pipe_length=input_parameters['pipe_stub_length'],
                                 loc=(-pipe_stub_z_centre, 0, 0)
                                 )
    ds_pipe_stub = make_beampipe(pipe_aperture=pipe_face, pipe_length=input_parameters['pipe_stub_length'],
                                 loc=(pipe_stub_z_centre, 0, 0)
                                 )
    us_taper = make_taper(aperture1=pipe_taper_wire, aperture2=cavity_wire,
                          taper_length=(total_cavity_length - stripline_mid_section_length) / 2.,
                          loc=(-total_cavity_length / 2., 0, 0)
                          )
    ds_taper = make_taper(aperture1=cavity_wire, aperture2=pipe_taper_wire,
                          taper_length=(total_cavity_length - stripline_mid_section_length) / 2.,
                          loc=(stripline_mid_section_length / 2., 0, 0)
                          )
    cavity = make_beampipe(pipe_aperture=cavity_face,
                           pipe_length=stripline_mid_section_length)
    # Basic feedthrough
    n_parts_us_upper, feedthrough_vaccum_us_upper = make_stripline_feedthrough(input_parameters, z_loc='us',
                                                                               xyrotation=0)
    n_parts_us_lower, feedthrough_vaccum_us_lower = make_stripline_feedthrough(input_parameters, z_loc='us',
                                                                               xyrotation=180)
    n_parts_ds_upper, feedthrough_vaccum_ds_upper = make_stripline_feedthrough(input_parameters, z_loc='ds',
                                                                               xyrotation=0)
    n_parts_ds_lower, feedthrough_vaccum_ds_lower = make_stripline_feedthrough(input_parameters, z_loc='ds',
                                                                               xyrotation=180)

    # Basic striplines
    stripline_upper = make_stripline(input_parameters, xyrotation=-90)
    stripline_lower = make_stripline(input_parameters, xyrotation=90)

    feedthrough_vac = feedthrough_vaccum_us_upper.fuse(feedthrough_vaccum_us_lower)
    feedthrough_vac = feedthrough_vac.fuse(feedthrough_vaccum_ds_upper)
    feedthrough_vac = feedthrough_vac.fuse(feedthrough_vaccum_ds_lower)

    chamber_vac = us_taper_vac.fuse(ds_taper_vac)
    chamber_vac = chamber_vac.fuse(cavity_vac)
    chamber_vac = chamber_vac.fuse(us_pipe_vac)
    chamber_vac = chamber_vac.fuse(ds_pipe_vac)
    rotate_at(shp=chamber_vac, rotation_angles=(-90, 0, 0))
    vac = chamber_vac.fuse(feedthrough_vac)

    rotate_at(shp=feedthrough_vac, rotation_angles=(-90, 0, 0))
    us_pipe_stub = us_pipe_stub.cut(us_pipe_vac)
    ds_pipe_stub = ds_pipe_stub.cut(ds_pipe_vac)
    us_taper = us_taper.cut(us_taper_vac)
    us_taper = us_taper.cut(feedthrough_vac)
    ds_taper = ds_taper.cut(ds_taper_vac)
    ds_taper = ds_taper.cut(feedthrough_vac)
    cavity = cavity.cut(cavity_vac)
    us_pipe_extension = us_pipe_extension.cut(us_pipe_vac)
    ds_pipe_extension = ds_pipe_extension.cut(ds_pipe_vac)

    outer = us_taper.fuse(ds_taper)
    outer = outer.fuse(cavity)
    outer = outer.fuse(us_pipe_stub)
    outer = outer.fuse(ds_pipe_stub)
    rotate_at(shp=outer, rotation_angles=(-90, 0, 0))
    outer = outer.cut(vac)

    trimmed_outers = n_parts_us_upper['outer'].fuse(n_parts_us_lower['outer'])
    trimmed_outers = trimmed_outers.fuse(n_parts_ds_upper['outer'])
    trimmed_outers = trimmed_outers.fuse(n_parts_ds_lower['outer'])
    trimmed_outers = trimmed_outers.cut(chamber_vac)
    outer = outer.fuse(trimmed_outers)

    stripline_upper = stripline_upper.cut(n_parts_us_upper['pin'])
    stripline_upper = stripline_upper.cut(n_parts_ds_upper['pin'])
    stripline_lower = stripline_lower.cut(n_parts_us_lower['pin'])
    stripline_lower = stripline_lower.cut(n_parts_ds_lower['pin'])

    # except Exception as e:
    #     raise ModelException(e)
    # An entry in the parts dictionary corresponds to an STL file. This is useful for parts of differing materials.
    # parts = {'wire1': pipe_vac_taper_wire, 'wire2': cavity_vac_wire}
    parts = {'us_pipe': us_pipe_extension, 'ds_pipe': ds_pipe_extension, 'cavity': outer,
             'vac': vac,
             'stripline_upper': stripline_upper, 'stripline_lower': stripline_lower,
             'pin_us_upper': n_parts_us_upper['pin'], 'pin_us_lower': n_parts_us_lower['pin'],
             'pin_ds_upper': n_parts_ds_upper['pin'], 'pin_ds_lower': n_parts_ds_lower['pin']}
    return parts


def stripline_model_curved_tapered_4_blade(input_parameters):
    """ Generates the geometry for a simplified stripline in FreeCAD. Also writes out the geometry as STL files
       and writes a "sidecar" text file containing the input parameters used.

         Args:
            input_parameters (dict): Dictionary of input parameter names and values.
        """

    try:
        stripline_mid_section_length = input_parameters['total_stripline_length'] - \
                                       2 * input_parameters['stripline_taper_length']
        # total_cavity_length is the total stipline length plus the additional cavity length at each end.
        total_cavity_length = input_parameters['total_stripline_length'] + \
                              2 * input_parameters['additional_cavity_length']
        pipe_extension_z_centre = (input_parameters['pipe_length'] + total_cavity_length) / 2. + input_parameters[
            'pipe_stub_length']
        pipe_stub_z_centre = (total_cavity_length + input_parameters['pipe_stub_length']) / 2.
        # Make cavity
        pipe_vac_wire, pipe_vac_face = make_circular_aperture(aperture_radius=input_parameters['pipe_radius'])
        pipe_vac_taper_wire, pipe_vac_taper_face = make_circular_aperture(
            aperture_radius=input_parameters['pipe_radius'])
        cavity_vac_wire, cavity_vac_face = make_circular_aperture(aperture_radius=input_parameters['cavity_radius'])
        pipe_vac = make_beampipe(pipe_aperture=pipe_vac_face,
                                 pipe_length=total_cavity_length + 2 * input_parameters['pipe_length'] + 2. *
                                             input_parameters['pipe_stub_length'],
                                 loc=(0, 0, 0)
                                 )
        us_taper_vac = make_taper(aperture1=pipe_vac_taper_wire, aperture2=cavity_vac_wire,
                                  taper_length=(total_cavity_length - stripline_mid_section_length) / 2.,
                                  loc=(-total_cavity_length / 2., 0, 0)
                                  )
        ds_taper_vac = make_taper(aperture1=cavity_vac_wire, aperture2=pipe_vac_taper_wire,
                                  taper_length=(total_cavity_length - stripline_mid_section_length) / 2.,
                                  loc=(stripline_mid_section_length / 2., 0, 0)
                                  )

        cavity_vac = make_beampipe(pipe_aperture=cavity_vac_face, pipe_length=stripline_mid_section_length)

        vac = us_taper_vac.fuse(ds_taper_vac)
        vac = vac.fuse(cavity_vac)
        vac = vac.fuse(pipe_vac)
        rotate_at(shp=vac, rotation_angles=(-90, 0, 0))

        pipe_wire, pipe_face = make_circular_aperture(aperture_radius=input_parameters['pipe_radius'] +
                                                                      input_parameters['pipe_thickness'])
        pipe_taper_wire, pipe_taper_face = make_circular_aperture(aperture_radius=input_parameters['pipe_radius'] +
                                                                                   input_parameters[
                                                                                       'pipe_thickness'] + 2e-3)
        cavity_wire, cavity_face = make_circular_aperture(aperture_radius=input_parameters['cavity_radius'] +
                                                                           input_parameters['pipe_thickness'])

        us_pipe_extension = make_beampipe(pipe_aperture=pipe_face,
                                          pipe_length=input_parameters['pipe_length'],
                                          loc=(-pipe_extension_z_centre, 0, 0)
                                          )
        ds_pipe_extension = make_beampipe(pipe_aperture=pipe_face,
                                          pipe_length=input_parameters['pipe_length'],
                                          loc=(pipe_extension_z_centre, 0, 0)
                                          )
        us_pipe_stub = make_beampipe(pipe_aperture=pipe_face, pipe_length=input_parameters['pipe_stub_length'],
                                     loc=(-pipe_stub_z_centre, 0, 0)
                                     )
        ds_pipe_stub = make_beampipe(pipe_aperture=pipe_face, pipe_length=input_parameters['pipe_stub_length'],
                                     loc=(pipe_stub_z_centre, 0, 0)
                                     )
        us_taper = make_taper(aperture1=pipe_taper_wire, aperture2=cavity_wire,
                              taper_length=(total_cavity_length - stripline_mid_section_length) / 2.,
                              loc=(-total_cavity_length / 2., 0, 0)
                              )
        ds_taper = make_taper(aperture1=cavity_wire, aperture2=pipe_taper_wire,
                              taper_length=(total_cavity_length - stripline_mid_section_length) / 2.,
                              loc=(stripline_mid_section_length / 2., 0, 0)
                              )
        cavity = make_beampipe(pipe_aperture=cavity_face,
                               pipe_length=stripline_mid_section_length)

        outer = us_taper.fuse(ds_taper)
        outer = outer.fuse(cavity)
        outer = outer.fuse(us_pipe_stub)
        outer = outer.fuse(ds_pipe_stub)
        rotate_at(shp=outer, rotation_angles=(-90, 0, 0))

        # Basic feedthrough
        n_parts_us_upper, feedthrough_vaccum_us_upper = make_stripline_feedthrough(input_parameters, z_loc='us',
                                                                                   xyrotation=-90)
        n_parts_us_right, feedthrough_vaccum_us_right = make_stripline_feedthrough(input_parameters, z_loc='us',
                                                                                   xyrotation=0)
        n_parts_us_lower, feedthrough_vaccum_us_lower = make_stripline_feedthrough(input_parameters, z_loc='us',
                                                                                   xyrotation=90)
        n_parts_us_left, feedthrough_vaccum_us_left = make_stripline_feedthrough(input_parameters, z_loc='us',
                                                                                 xyrotation=-180)
        n_parts_ds_upper, feedthrough_vaccum_ds_upper = make_stripline_feedthrough(input_parameters, z_loc='ds',
                                                                                   xyrotation=-90)
        n_parts_ds_right, feedthrough_vaccum_ds_right = make_stripline_feedthrough(input_parameters, z_loc='ds',
                                                                                   xyrotation=-0)
        n_parts_ds_lower, feedthrough_vaccum_ds_lower = make_stripline_feedthrough(input_parameters, z_loc='ds',
                                                                                   xyrotation=90)
        n_parts_ds_left, feedthrough_vaccum_ds_left = make_stripline_feedthrough(input_parameters, z_loc='ds',
                                                                                 xyrotation=-180)

        # Basic striplines
        stripline_upper = make_stripline(input_parameters, xyrotation=-90)
        stripline_right = make_stripline(input_parameters, xyrotation=0)
        stripline_lower = make_stripline(input_parameters, xyrotation=90)
        stripline_left = make_stripline(input_parameters, xyrotation=180)

        trimmed_outers = n_parts_us_upper['outer'].fuse(n_parts_us_right['outer'])
        trimmed_outers = trimmed_outers.fuse(n_parts_us_lower['outer'])
        trimmed_outers = trimmed_outers.fuse(n_parts_us_left['outer'])
        trimmed_outers = trimmed_outers.fuse(n_parts_ds_upper['outer'])
        trimmed_outers = trimmed_outers.fuse(n_parts_ds_right['outer'])
        trimmed_outers = trimmed_outers.fuse(n_parts_ds_lower['outer'])
        trimmed_outers = trimmed_outers.fuse(n_parts_ds_left['outer'])
        trimmed_outers = trimmed_outers.cut(vac)

        vac = vac.fuse(feedthrough_vaccum_us_upper)
        vac = vac.fuse(feedthrough_vaccum_us_right)
        vac = vac.fuse(feedthrough_vaccum_us_lower)
        vac = vac.fuse(feedthrough_vaccum_us_left)
        vac = vac.fuse(feedthrough_vaccum_ds_upper)
        vac = vac.fuse(feedthrough_vaccum_ds_right)
        vac = vac.fuse(feedthrough_vaccum_ds_lower)
        vac = vac.fuse(feedthrough_vaccum_ds_left)

        us_pipe_extension = us_pipe_extension.cut(vac)
        ds_pipe_extension = ds_pipe_extension.cut(vac)
        outer = outer.cut(vac)
        outer = outer.fuse(trimmed_outers)

        stripline_upper = stripline_upper.cut(n_parts_us_upper['pin'])
        stripline_upper = stripline_upper.cut(n_parts_ds_upper['pin'])
        stripline_right = stripline_right.cut(n_parts_us_right['pin'])
        stripline_right = stripline_right.cut(n_parts_ds_right['pin'])
        stripline_lower = stripline_lower.cut(n_parts_us_lower['pin'])
        stripline_lower = stripline_lower.cut(n_parts_ds_lower['pin'])
        stripline_left = stripline_left.cut(n_parts_us_left['pin'])
        stripline_left = stripline_left.cut(n_parts_ds_left['pin'])

    except Exception as e:
        raise ModelException(e)
    # An entry in the parts dictionary corresponds to an STL file. This is useful for parts of differing materials.
    parts = {'us_pipe': us_pipe_extension, 'ds_pipe': ds_pipe_extension, 'cavity': outer,
             'vac': vac,
             'stripline_upper': stripline_upper, 'stripline_right': stripline_right,
             'stripline_lower': stripline_lower, 'stripline_left': stripline_left,
             'pin_us_upper': n_parts_us_upper['pin'], 'pin_us_right': n_parts_us_right['pin'],
             'pin_us_lower': n_parts_us_lower['pin'], 'pin_us_left': n_parts_us_left['pin'],
             'pin_ds_upper': n_parts_ds_upper['pin'], 'pin_ds_right': n_parts_ds_right['pin'],
             'pin_ds_lower': n_parts_ds_lower['pin'], 'pin_ds_left': n_parts_ds_left['pin']
             }
    return parts
