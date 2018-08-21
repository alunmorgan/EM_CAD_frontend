from freecad_elements import make_beampipe, make_circular_aperture, ModelException, parameter_sweep, base_model
from sys import argv
import os
from FreeCAD import Base
import Part

# baseline model parameters
INPUT_PARAMETERS = {'cavity_radius': 80, 'cavity_length': 100, 'pipe_radius': 10, 'pipe_length': 80,
                    'port_offset': 30, 'stripline_length': 70, 'stripline_width': 10,
                    'stripline_offset': 30,
                    'feedthrough_hole_radius': 5, 'feedthrough_pin_radius': 1}
MODEL_NAME, OUTPUT_PATH = argv


def simple_stripline_model(input_parameters):
    """ Generates the geometry for a simplified stripline in FreeCAD. Also writes out the geometry as STL files 
       and writes a "sidecar" text file containing the input parameters used.

         Args:
            input_parameters (dict): Dictionary of input parameter names and values.
        """

    try:
        # Make cavity
        wire1, face1 = make_circular_aperture(input_parameters['pipe_radius'])
        wire2, face2 = make_circular_aperture(input_parameters['cavity_radius'])
        beampipe1 = make_beampipe(face1, input_parameters['pipe_length'],
                                  (-input_parameters['pipe_length'] / 2. - input_parameters['cavity_length'] / 2., 0, 0)
                                  )
        beampipe3 = make_beampipe(face1, input_parameters['pipe_length'],
                                  (input_parameters['pipe_length'] / 2. + input_parameters['cavity_length'] / 2., 0, 0)
                                  )
        beampipe2 = make_beampipe(face2, input_parameters['cavity_length'])
        fin1 = beampipe1.fuse(beampipe2)
        outer = fin1.fuse(beampipe3)

        # Basic feedthrough
        cylinder1 = Part.makeCylinder(input_parameters['feedthrough_hole_radius'], 100,
                                      Base.Vector(-input_parameters['port_offset'], -35, 0), Base.Vector(0, -1, 0))
        cylinder2 = Part.makeCylinder(input_parameters['feedthrough_hole_radius'], 100,
                                      Base.Vector(input_parameters['port_offset'], -35, 0), Base.Vector(0, -1, 0))
        cylinder3 = Part.makeCylinder(input_parameters['feedthrough_hole_radius'], 100,
                                      Base.Vector(-input_parameters['port_offset'], 35, 0), Base.Vector(0, 1, 0))
        cylinder4 = Part.makeCylinder(input_parameters['feedthrough_hole_radius'], 100,
                                      Base.Vector(input_parameters['port_offset'], 35, 0), Base.Vector(0, 1, 0))
        # Pins
        pin1 = Part.makeCylinder(input_parameters['feedthrough_pin_radius'],
                                 input_parameters['cavity_radius'] - input_parameters['stripline_offset'],
                                      Base.Vector(-input_parameters['port_offset'], -30, 0), Base.Vector(0, -1, 0))
        pin2 = Part.makeCylinder(input_parameters['feedthrough_pin_radius'],
                                 input_parameters['cavity_radius'] - input_parameters['stripline_offset'],
                                      Base.Vector(input_parameters['port_offset'], -30, 0), Base.Vector(0, -1, 0))
        pin3 = Part.makeCylinder(input_parameters['feedthrough_pin_radius'],
                                 input_parameters['cavity_radius'] - input_parameters['stripline_offset'],
                                      Base.Vector(-input_parameters['port_offset'], 30, 0), Base.Vector(0, 1, 0))
        pin4 = Part.makeCylinder(input_parameters['feedthrough_pin_radius'],
                                 input_parameters['cavity_radius'] - input_parameters['stripline_offset'],
                                      Base.Vector(input_parameters['port_offset'], 30, 0), Base.Vector(0, 1, 0))

        # Basic striplines
        stripline1 = Part.makeBox(input_parameters['stripline_length'], 2, input_parameters['stripline_width'],
                                  Base.Vector(-input_parameters['stripline_length'] / 2., 30, -input_parameters['stripline_width'] / 2.))
        stripline2 = Part.makeBox(input_parameters['stripline_length'], 2, input_parameters['stripline_width'],
                                  Base.Vector(-input_parameters['stripline_length'] / 2., -30, -input_parameters['stripline_width'] / 2.))

        diff3 = outer.cut(cylinder1)
        diff4 = diff3.cut(cylinder2)
        diff5 = diff4.cut(cylinder3)
        diff6 = diff5.cut(cylinder4)

        pins = pin1.fuse(pin2)
        pins= pins.fuse(pin3)
        pins = pins.fuse(pin4)

        striplines = stripline1.fuse(stripline2)

    except Exception as e:
        raise ModelException(e)
    # An entry in the parts dictionary corresponds to an STL file. This is useful for parts of differing materials.
    parts = {'cavity': diff6, 'striplines': striplines, 'pins': pins}
    return parts, os.path.splitext(os.path.basename(MODEL_NAME))[0]


base_model(simple_stripline_model, INPUT_PARAMETERS, OUTPUT_PATH, accuracy=10)
