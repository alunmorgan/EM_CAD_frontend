from freecad_elements import make_beampipe, make_elliptical_aperture, make_taper, ModelException, parameter_sweep,\
    base_model
from sys import argv
import os

# baseline model parameters
INPUT_PARAMETERS = {'pipe_height': 10, 'pipe_width': 40, 'pipe_length': 80,
                    'cavity_height': 20, 'cavity_width': 60, 'cavity_length': 20,
                    'taper_length': 30}
MODEL_NAME, OUTPUT_PATH = argv


def elliptical_taper_model(input_parameters):
    """Generates the geometry for the elliptical taper in FreeCAD. Also writes out the geometry as STL files 
       and writes a "sidecar" text file containing the input parameters used.

         Args:
            input_parameters (dict): Dictionary of input parameter names and values.
        """
    try:
        wire1, face1 = make_elliptical_aperture(input_parameters['pipe_height'], input_parameters['pipe_width'])
        wire2, face2 = make_elliptical_aperture(input_parameters['cavity_height'], input_parameters['cavity_width'])
        beampipe1 = make_beampipe(face1, input_parameters['pipe_length'],
                                  (-input_parameters['pipe_length'] / 2. -
                                   input_parameters['taper_length'] -
                                   input_parameters['cavity_length'] / 2., 0, 0)
                                  )
        taper1 = make_taper(wire2, wire1, input_parameters['taper_length'],
                            (-input_parameters['cavity_length'] / 2., 0, 0),
                            (0, 180, 0)
                            )
        beampipe2 = make_beampipe(face2, input_parameters['cavity_length'])
        taper2 = make_taper(wire2, wire1, input_parameters['taper_length'],
                            (input_parameters['cavity_length'] / 2., 0, 0)
                            )
        beampipe3 = make_beampipe(face1, input_parameters['pipe_length'],
                                  (input_parameters['pipe_length'] / 2. +
                                   input_parameters['taper_length'] +
                                   input_parameters['cavity_length'] / 2., 0, 0)
                                  )
        fin1 = beampipe1.fuse(taper1)
        fin2 = fin1.fuse(beampipe2)
        fin3 = fin2.fuse(taper2)
        fin4 = fin3.fuse(beampipe3)
    except Exception as e:
        raise ModelException(e)
    # An entry in the parts dictionary corresponds to an STL file. This is useful for parts of differing materials.
    parts = {'all': fin4}
    return parts, os.path.splitext(os.path.basename(MODEL_NAME))[0]

base_model(elliptical_taper_model, INPUT_PARAMETERS, OUTPUT_PATH, accuracy=10)
parameter_sweep(elliptical_taper_model, INPUT_PARAMETERS, OUTPUT_PATH, 'cavity_height', [5, 10, 15, 25, 30])
parameter_sweep(elliptical_taper_model, INPUT_PARAMETERS, OUTPUT_PATH, 'cavity_width', [40, 80, 100, 120])
parameter_sweep(elliptical_taper_model, INPUT_PARAMETERS, OUTPUT_PATH, 'taper_length', [10, 20, 40, 50, 60])
parameter_sweep(elliptical_taper_model, INPUT_PARAMETERS, OUTPUT_PATH, 'cavity_length', [40, 60, 80])
parameter_sweep(elliptical_taper_model, INPUT_PARAMETERS, OUTPUT_PATH, 'pipe_height', [15, 20, 25, 30, 35, 40, 45, 50])
parameter_sweep(elliptical_taper_model, INPUT_PARAMETERS, OUTPUT_PATH, 'pipe_length', [50, 100, 150, 200, 250, 300])
parameter_sweep(elliptical_taper_model, INPUT_PARAMETERS, OUTPUT_PATH, 'pipe_width', [30, 50, 60, 70])

