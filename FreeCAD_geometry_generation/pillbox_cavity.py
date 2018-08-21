from freecad_elements import make_beampipe, make_circular_aperture, ModelException, parameter_sweep, base_model
from sys import argv
import os

# baseline model parameters
INPUT_PARAMETERS = {'cavity_radius': 20e-3, 'cavity_length': 20e-3, 'pipe_radius': 10e-3,
                    'pipe_length': 80e-3, 'wall_thickness': 2e-3}
MODEL_NAME, OUTPUT_PATH = argv


def pillbox_cavity_model(input_parameters):
    """ Generates the geometry for the pillbox cavity in FreeCAD. Also writes out the geometry as STL files 
       and writes a "sidecar" text file containing the input parameters used.

         Args:
            input_parameters (dict): Dictionary of input parameter names and values.
        """

    try:
        wire1, face1 = make_circular_aperture(input_parameters['pipe_radius'])
        wire2, face2 = make_circular_aperture(input_parameters['cavity_radius'])
        beampipe_vacuum1 = make_beampipe(face1, input_parameters['pipe_length'],
                                  (-input_parameters['pipe_length'] / 2. - input_parameters['cavity_length'] / 2., 0, 0)
                                  )
        cavity_vacuum = make_beampipe(face2, input_parameters['cavity_length'])
        beampipe_vacuum2 = make_beampipe(face1, input_parameters['pipe_length'],
                                  (input_parameters['pipe_length'] / 2. + input_parameters['cavity_length'] / 2., 0, 0)
                                  )

        vac1 = beampipe_vacuum1.fuse(cavity_vacuum)
        vac2 = vac1.fuse(beampipe_vacuum2)

        wire3, face3 = make_circular_aperture(input_parameters['pipe_radius'] + input_parameters['wall_thickness'])
        wire4, face4 = make_circular_aperture(input_parameters['cavity_radius'] + input_parameters['wall_thickness'])
        beampipe_shell1 = make_beampipe(face3, input_parameters['pipe_length'],
                                         (
                                         -input_parameters['pipe_length'] / 2. - input_parameters['cavity_length'] / 2.,
                                         0, 0)
                                         )
        cavity_shell = make_beampipe(face4, input_parameters['cavity_length'] + 2 * input_parameters['wall_thickness'])
        beampipe_shell2 = make_beampipe(face3, input_parameters['pipe_length'],
                                         (input_parameters['pipe_length'] / 2. + input_parameters['cavity_length'] / 2.,
                                          0, 0)
                                         )

        shell1 = beampipe_shell1.fuse(cavity_shell)
        shell2 = shell1.fuse(beampipe_shell2)
        shell3 = shell2.cut(vac2)
    except Exception as e:
        raise ModelException(e)
    # An entry in the parts dictionary corresponds to an STL file. This is useful for parts of differing materials.
    parts = {'vac': vac2, 'shell': shell3}
    return parts, os.path.splitext(os.path.basename(MODEL_NAME))[0]


base_model(pillbox_cavity_model, INPUT_PARAMETERS, OUTPUT_PATH, accuracy=10)
parameter_sweep(pillbox_cavity_model, INPUT_PARAMETERS, OUTPUT_PATH, 'cavity_radius', [10e-3, 30e-3, 40e-3, 50e-3])
parameter_sweep(pillbox_cavity_model, INPUT_PARAMETERS, OUTPUT_PATH, 'pipe_radius', [15e-3, 20e-3, 25e-3])
parameter_sweep(pillbox_cavity_model, INPUT_PARAMETERS, OUTPUT_PATH, 'cavity_length', [10e-3, 30e-3, 40e-3, 50e-3])
parameter_sweep(pillbox_cavity_model, INPUT_PARAMETERS, OUTPUT_PATH, 'cavity_radius', [10e-3, 30e-3, 40e-3, 50e-3])
parameter_sweep(pillbox_cavity_model, INPUT_PARAMETERS, OUTPUT_PATH, 'pipe_length', [40e-3, 60e-3, 100e-3])
