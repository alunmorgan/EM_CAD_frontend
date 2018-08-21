from freecad_elements import make_beampipe, make_racetrack_aperture, make_octagonal_aperture,\
    make_taper, ModelException, parameter_sweep, base_model
from sys import argv
import os

# baseline model parameters
INPUT_PARAMETERS = {'racetrack_height': 10e-3, 'racetrack_width': 40e-3, 'racetrack_length': 80e-3,
                    'octagon_height': 20e-3, 'octagon_width': 60e-3, 'octagon_length': 20e-3,
                    'octagon_side_length': 8e-3, 'octagon_tb_length': 20e-3,
                    'taper_length': 30e-3, 'pipe_thickness': 2e-3}
MODEL_NAME, OUTPUT_PATH = argv


def racetrack_to_octagonal_cavity_model(input_parameters):
    """Generates the geometry for the elliptical taper in FreeCAD. Also writes out the geometry as STL files 
       and writes a "sidecar" text file containing the input parameters used.

         Args:
            input_parameters (dict): Dictionary of input parameter names and values.
        """
    try:
        wire1, face1 = make_octagonal_aperture(input_parameters['octagon_height'],
                                               input_parameters['octagon_width'],
                                               input_parameters['octagon_side_length'],
                                               input_parameters['octagon_tb_length'])
        wire2, face2 = make_racetrack_aperture(input_parameters['racetrack_height'],
                                               input_parameters['racetrack_width'])
        wire3, face3 = make_octagonal_aperture(input_parameters['octagon_height'] + input_parameters['pipe_thickness'],
                                               input_parameters['octagon_width'] + input_parameters['pipe_thickness'],
                                               input_parameters['octagon_side_length'],
                                               input_parameters['octagon_tb_length'])
        wire4, face4 = make_racetrack_aperture(input_parameters['racetrack_height'] + input_parameters['pipe_thickness'],
                                               input_parameters['racetrack_width'] + input_parameters['pipe_thickness'])

        vac1 = make_beampipe(face1, input_parameters['octagon_length'],
                             (-input_parameters['octagon_length'] / 2. -
                              input_parameters['taper_length'] -
                              input_parameters['racetrack_length'] / 2., 0, 0))
        vac2 = make_taper(wire2, wire1, input_parameters['taper_length'],
                          (-input_parameters['racetrack_length'] / 2., 0, 0), (0, 180, 0))
        vac3 = make_beampipe(face2, input_parameters['racetrack_length'])

        beampipe1 = make_beampipe(face3, input_parameters['octagon_length'],
                                  (-input_parameters['octagon_length'] / 2. -
                                   input_parameters['taper_length'] -
                                   input_parameters['racetrack_length'] / 2., 0, 0))
        taper1 = make_taper(wire4, wire3, input_parameters['taper_length'],
                            (-input_parameters['racetrack_length'] / 2., 0, 0), (0, 180, 0))
        beampipe2 = make_beampipe(face4, input_parameters['racetrack_length'])

        fin1 = beampipe1.fuse(taper1)
        fin2 = fin1.fuse(beampipe2)

        vac_vol = vac1.fuse(vac2)
        vac_vol1 = vac_vol.fuse(vac3)

        full_pipe = fin2.cut(vac_vol1)

    except Exception as e:
        raise ModelException(e)
    # An entry in the parts dictionary corresponds to an STL file. This is useful for parts of differing materials.
    parts = {'pipe': full_pipe, 'vac': vac_vol1}
    return parts, os.path.splitext(os.path.basename(MODEL_NAME))[0]


base_model(racetrack_to_octagonal_cavity_model, INPUT_PARAMETERS, OUTPUT_PATH, accuracy=10)
parameter_sweep(racetrack_to_octagonal_cavity_model, INPUT_PARAMETERS, OUTPUT_PATH, 'octagon_height', [5e-3, 10e-3, 15e-3, 25e-3, 30e-3])
parameter_sweep(racetrack_to_octagonal_cavity_model, INPUT_PARAMETERS, OUTPUT_PATH, 'octagon_width', [40e-3, 80e-3, 100e-3, 120e-3])
parameter_sweep(racetrack_to_octagonal_cavity_model, INPUT_PARAMETERS, OUTPUT_PATH, 'taper_length', [10e-3, 20e-3, 40e-3, 50e-3, 60e-3])
parameter_sweep(racetrack_to_octagonal_cavity_model, INPUT_PARAMETERS, OUTPUT_PATH, 'racetrack_height', [15e-3, 20e-3, 25e-3, 30e-3, 35e-3, 40e-3, 45e-3, 50e-3])
parameter_sweep(racetrack_to_octagonal_cavity_model, INPUT_PARAMETERS, OUTPUT_PATH, 'racetrack_width', [20e-3, 30e-3, 50e-3, 60e-3, 70e-3])
parameter_sweep(racetrack_to_octagonal_cavity_model, INPUT_PARAMETERS, OUTPUT_PATH, 'racetrack_length', [50e-3, 100e-3, 150e-3, 200e-3, 250e-3, 300e-3])
parameter_sweep(racetrack_to_octagonal_cavity_model, INPUT_PARAMETERS, OUTPUT_PATH, 'octagon_side_length', [4e-3, 6e-3, 10e-3, 12e-3])
parameter_sweep(racetrack_to_octagonal_cavity_model, INPUT_PARAMETERS, OUTPUT_PATH, 'octagon_tb_length', [10e-3, 30e-3])
