from freecad_elements import make_beampipe, make_elliptical_aperture, ModelException, base_model, rotate_at, \
    parameter_sweep
import Part, Mesh, MeshPart
from FreeCAD import Base
from sys import argv
import os

# baseline model parameters
"""
button_hole_radius (float): Radius of the hole the button of the BPM fits into.
button_hole_horizontal_offset (float): Offset of the buttons from the centre horizontally.
button_hole_s_offset (float): Offset of the buttons from the centre in beam direction. 
button_angle (float): Angle from vertical.
            """
INPUT_PARAMETERS = {'pipe_width': 27e-3, 'pipe_height': 18.4e-3, 'pipe_length': 40e-3, 'pipe_thickness': 2.e-3,
                    'block_radius': 30e-3, 'block_s': 20e-3, 'button_hole_radius': 3.25e-3,
                    'button_horizontal_offset': 6e-3, 'button_s_offset': 0., 'button_angle': 18.65,
                    'button_radius': 3e-3, 'button_thickness': 4e-3, 'button_offset': 0.5e-3,
                    'button_ring_inner_radius': 1.2e-3, 'button_ring_outer_radius': 2.1e-3,
                    'pin_radius': 0.5e-3, 'pin_height': 100e-3,
                    'ceramic_radius': 4.5e-3, 'ceramic_thickness': 2.4e-3, 'ceramic_offset': 5e-3,
                    'shell_upper_radius': 6.5e-3, 'shell_upper_thickness': 9.5e-3, 'shell_upper_inner_radius': 2.5e-3,
                    'shell_lower_radius': 5.e-3, 'shell_lower_thickness': 3.e-3, 'shell_lower_inner_radius': 4.3e-3}

MODEL_NAME, OUTPUT_PATH = argv


def simple_buttons_model(input_parameters):
    """ Generates the geometry for the pillbox cavity in FreeCAD. Also writes out the geometry as STL files 
       and writes a "sidecar" text file containing the input parameters used.

         Args:
            input_parameters (dict): Dictionary of input parameter names and values.
        """

    try:
        wire1, face1 = make_elliptical_aperture(input_parameters['pipe_height'], input_parameters['pipe_width'])
        wire2, face2 = make_elliptical_aperture(input_parameters['pipe_height'] + input_parameters['pipe_thickness'],
                                                input_parameters['pipe_width'] + input_parameters['pipe_thickness'])
        beampipe_vac = make_beampipe(face1, input_parameters['pipe_length'] + 2e-3)
        beampipe = make_beampipe(face2, input_parameters['pipe_length'])

        block = Part.makeCylinder(input_parameters['block_radius'], input_parameters['block_s'],
                                  Base.Vector(-input_parameters['block_s'] / 2., 0, 0),
                                  Base.Vector(1, 0, 0)
                                  )

        hole1 = single_button_hole(input_parameters, quadrants=(1, 1, 1))
        hole2 = single_button_hole(input_parameters, quadrants=(-1, 1, -1))
        hole3 = single_button_hole(input_parameters, quadrants=(-1, -1, 1))
        hole4 = single_button_hole(input_parameters, quadrants=(1, -1, -1))

        vac1 = beampipe_vac.fuse(hole1)
        vac2 = vac1.fuse(hole2)
        vac3 = vac2.fuse(hole3)
        vac4 = vac3.fuse(hole4)

        button_block = block.cut(vac4)

        beampipe1 = beampipe.cut(block)
        beampipe2 = beampipe1.cut(beampipe_vac)

        button1, pin1, ceramic1, shell1 = single_button(input_parameters, quadrants=(1, 1, 1))
        button2, pin2, ceramic2, shell2 = single_button(input_parameters, quadrants=(-1, 1, -1))
        button3, pin3, ceramic3, shell3 = single_button(input_parameters, quadrants=(-1, -1, 1))
        button4, pin4, ceramic4, shell4 = single_button(input_parameters, quadrants=(1, -1, -1))

    except Exception as e:
        raise ModelException(e)
    # An entry in the parts dictionary corresponds to an STL file. This is useful for parts of differing materials.
    parts = {'vac': vac4, 'block': button_block, 'beampipe': beampipe2,
             'button1': button1, 'pin1': pin1, 'ceramic1': ceramic1, 'shell1': shell1,
             'button2': button2, 'pin2': pin2, 'ceramic2': ceramic2, 'shell2': shell2,
             'button3': button3, 'pin3': pin3, 'ceramic3': ceramic3, 'shell3': shell3,
             'button4': button4, 'pin4': pin4, 'ceramic4': ceramic4,  'shell4': shell4
             }
    # 'hole1': hole1, 'hole2': hole2, 'hole3': hole3, 'hole4': hole4
    return parts, os.path.splitext(os.path.basename(MODEL_NAME))[0]


def single_button_hole(input_parameters,  quadrants=(1, 1, 1)):
    """Generates the geometry for a single hole in the button block for the button to be placed
    
        Args:
            input_parameters (dict): Dictionary of input parameter names and values.
            quadrants (tuple): a set of 1 or -1 depending on whether the hole is in the positive volume quadrant 
                               or the negative volume quadrant. The order is (horizontal, vertical, beam direction).
    
    """
    beam_pipe_height = ellipse_track(input_parameters['pipe_height'], input_parameters['pipe_width'],
                                     quadrants[0] * input_parameters['button_horizontal_offset'])

    cylinder1 = Part.makeCylinder(input_parameters['button_hole_radius'], 100e-3,
                                  Base.Vector(quadrants[2] * input_parameters['button_s_offset'],
                                              # The -2 is to make sure that it is a clean hole
                                              quadrants[1] * (beam_pipe_height - 2e-3),
                                              quadrants[0] * input_parameters['button_horizontal_offset']),
                                  Base.Vector(0, quadrants[1], 0))

    cylinder2 = Part.makeCylinder(10.5e-3 / 2., 100e-3,
                                  Base.Vector(quadrants[2] * input_parameters['button_s_offset'],
                                              quadrants[1] * (beam_pipe_height + 5.e-3),
                                              quadrants[0] * input_parameters['button_horizontal_offset']),
                                  Base.Vector(0, quadrants[1], 0))

    cylinder3 = Part.makeCylinder(13e-3 / 2., 100e-3,
                                  Base.Vector(quadrants[2] * input_parameters['button_s_offset'],
                                              quadrants[1] * (beam_pipe_height + 5.e-3 + 3.5e-3),
                                              quadrants[0] * input_parameters['button_horizontal_offset']),
                                  Base.Vector(0, quadrants[1], 0))

    cylinder4 = Part.makeCylinder(17.4e-3 / 2., 100e-3,
                                  Base.Vector(quadrants[2] * input_parameters['button_s_offset'],
                                              quadrants[1] * (beam_pipe_height + 5.e-3 + 3.5e-3 + 9.5e-3),
                                              quadrants[0] * input_parameters['button_horizontal_offset']),
                                  Base.Vector(0, quadrants[1], 0))

    fin1 = cylinder1.fuse(cylinder2)
    fin2 = fin1.fuse(cylinder3)
    hole = fin2.fuse(cylinder4)

    hole = rotate_at(hole, loc=(quadrants[2] * input_parameters['button_s_offset'],
                                quadrants[1] * beam_pipe_height,
                                quadrants[0] * input_parameters['button_horizontal_offset'],
                                ),
                     rotation_angles=(quadrants[0] * quadrants[1] * input_parameters['button_angle'], 0, 0)
                     )
    return hole


def single_button(input_parameters, quadrants=(1, 1, 1)):
    """Generates the geometry for a single hole in the button block for the button to be placed

        Args:
            input_parameters (dict): Dictionary of input parameter names and values.
            quadrants (tuple): a set of 1 or -1 depending on whether the hole is in the positive volume quadrant 
                               or the negative volume quadrant. The order is (horizontal, vertical, beam direction).

    """
    beam_pipe_height = ellipse_track(input_parameters['pipe_height'], input_parameters['pipe_width'],
                                     quadrants[0] * input_parameters['button_horizontal_offset'])
    button_height = beam_pipe_height + input_parameters['button_offset']

    pin = Part.makeCylinder(input_parameters['pin_radius'], input_parameters['pin_height'],
                            Base.Vector(quadrants[2] * input_parameters['button_s_offset'],
                                        quadrants[1] * button_height,
                                        quadrants[0] * input_parameters['button_horizontal_offset']),
                            Base.Vector(0, quadrants[1], 0))

    button = Part.makeCylinder(input_parameters['button_radius'], input_parameters['button_thickness'],
                               Base.Vector(quadrants[2] * input_parameters['button_s_offset'],
                                           quadrants[1] * button_height,
                                           quadrants[0] * input_parameters['button_horizontal_offset']),
                               Base.Vector(0, quadrants[1], 0))

    # The button support ring thickness is determined by the gap between the top of the button,
    # and the bottom of the ceramic.
    button_ring_inner = Part.makeCylinder(input_parameters['button_ring_inner_radius'],
                                          input_parameters['ceramic_offset'] - input_parameters['button_thickness'],
                                          Base.Vector(quadrants[2] * input_parameters['button_s_offset'],
                                                      quadrants[1] * (button_height +
                                                                      input_parameters['button_thickness']),
                                                      quadrants[0] * input_parameters['button_horizontal_offset']),
                                          Base.Vector(0, quadrants[1], 0))

    button_ring_outer = Part.makeCylinder(input_parameters['button_ring_outer_radius'],
                                          input_parameters['ceramic_offset'] - input_parameters['button_thickness'],
                                          Base.Vector(quadrants[2] * input_parameters['button_s_offset'],
                                                      quadrants[1] * (button_height +
                                                                      input_parameters['button_thickness']),
                                                      quadrants[0] * input_parameters['button_horizontal_offset']),
                                          Base.Vector(0, quadrants[1], 0))

    ceramic = Part.makeCylinder(input_parameters['ceramic_radius'], input_parameters['ceramic_thickness'],
                                Base.Vector(quadrants[2] * input_parameters['button_s_offset'],
                                            quadrants[1] * (button_height + input_parameters['ceramic_offset']),
                                            quadrants[0] * input_parameters['button_horizontal_offset']),
                                Base.Vector(0, quadrants[1], 0))

    shell_upper1 = Part.makeCylinder(input_parameters['shell_upper_radius'], input_parameters['shell_upper_thickness'],
                                     Base.Vector(quadrants[2] * input_parameters['button_s_offset'],
                                                 quadrants[1] * (button_height + input_parameters['ceramic_offset']
                                                 + input_parameters['shell_lower_thickness']),
                                                 quadrants[0] * input_parameters['button_horizontal_offset']),
                                     Base.Vector(0, quadrants[1], 0))
    shell_upper2 = Part.makeCylinder(input_parameters['shell_upper_inner_radius'],
                                     input_parameters['shell_upper_thickness'],
                                     Base.Vector(quadrants[2] * input_parameters['button_s_offset'],
                                                 quadrants[1] * (button_height + input_parameters['ceramic_offset']
                                                 + input_parameters['shell_lower_thickness']),
                                                 quadrants[0] * input_parameters['button_horizontal_offset']),
                                     Base.Vector(0, quadrants[1], 0))
    shell_lower1 = Part.makeCylinder(input_parameters['shell_lower_radius'], input_parameters['shell_lower_thickness'],
                                     Base.Vector(quadrants[2] * input_parameters['button_s_offset'],
                                                 quadrants[1] * (button_height + input_parameters['ceramic_offset']),
                                                 quadrants[0] * input_parameters['button_horizontal_offset']),
                                     Base.Vector(0, quadrants[1], 0))
    shell_lower2 = Part.makeCylinder(input_parameters['shell_lower_inner_radius'],
                                     input_parameters['shell_lower_thickness'],
                                     Base.Vector(quadrants[2] * input_parameters['button_s_offset'],
                                                 quadrants[1] * (button_height + input_parameters['ceramic_offset']),
                                                 quadrants[0] * input_parameters['button_horizontal_offset']),
                                     Base.Vector(0, quadrants[1], 0))

    button_ring = button_ring_outer.cut(button_ring_inner)
    button = button.fuse(button_ring)
    shell_upper = shell_upper1.cut(shell_upper2)
    shell_lower = shell_lower1.cut(shell_lower2)
    shell = shell_upper.fuse(shell_lower)
    shell = shell.cut(ceramic)

    ceramic = ceramic.cut(pin)
    button = button.cut(pin)

    pin = rotate_at(pin, loc=(quadrants[2] * input_parameters['button_s_offset'],
                              quadrants[1] * beam_pipe_height,
                              quadrants[0] * input_parameters['button_horizontal_offset'],
                              ),
                    rotation_angles=(quadrants[0] * quadrants[1] * input_parameters['button_angle'], 0, 0)
                    )

    button = rotate_at(button, loc=(quadrants[2] * input_parameters['button_s_offset'],
                                    quadrants[1] * beam_pipe_height,
                                    quadrants[0] * input_parameters['button_horizontal_offset'],
                                    ),
                       rotation_angles=(quadrants[0] * quadrants[1] * input_parameters['button_angle'], 0, 0)
                       )

    ceramic = rotate_at(ceramic, loc=(quadrants[2] * input_parameters['button_s_offset'],
                                      quadrants[1] * beam_pipe_height,
                                      quadrants[0] * input_parameters['button_horizontal_offset'],
                                      ),
                        rotation_angles=(quadrants[0] * quadrants[1] * input_parameters['button_angle'], 0, 0)
                        )

    shell = rotate_at(shell, loc=(quadrants[2] * input_parameters['button_s_offset'],
                                  quadrants[1] * beam_pipe_height,
                                  quadrants[0] * input_parameters['button_horizontal_offset'],
                                  ),
                      rotation_angles=(quadrants[0] * quadrants[1] * input_parameters['button_angle'], 0, 0)
                      )

    return button, pin, ceramic, shell


def ellipse_track(e_height, e_width, x):
    a = e_width / 2.
    b = e_height / 2.
    y = (b**2. - ((b / a) * x)**2.)**0.5
    return y

base_model(simple_buttons_model, INPUT_PARAMETERS, OUTPUT_PATH, accuracy=10)
parameter_sweep(simple_buttons_model, INPUT_PARAMETERS, OUTPUT_PATH, 'button_radius', [2E-3, 2.5E-3])
