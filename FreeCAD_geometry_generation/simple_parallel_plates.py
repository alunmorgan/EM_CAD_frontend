import os
import sys
from sys import argv

from FreeCAD import Base
import Part
sys.path.insert(0, "V:\GitHub_Repositories\EM_CAD_frontend")
from FreeCAD_geometry_generation.freecad_operations import (ModelException,
                                                            base_model,

                                                            parameter_sweep)


def simple_parallel_plates_model(input_parameters):
    """Generates the geometry for a simplified set of parallel plates in FreeCAD. Also writes out the geometry as STL files
    and writes a "sidecar" text file containing the input parameters used.

      Args:
         input_parameters (dict): Dictionary of input parameter names and values.
    """

    try:
        plate1 = Part.makeBox(
            input_parameters["plate_length"],
            input_parameters["plate_thickness"],
            input_parameters["plate_width"],
            Base.Vector(
                -input_parameters["plate_length"] / 2.0,
                input_parameters["plate_offset"] + input_parameters["plate_thickness"] / 2.0, 
                -input_parameters["plate_width"] / 2.0,
            ),
        )
        plate2 = Part.makeBox(
            input_parameters["plate_length"],
            input_parameters["plate_thickness"],
            input_parameters["plate_width"],
            Base.Vector(
                -input_parameters["plate_length"] / 2.0,
                -input_parameters["plate_offset"] - input_parameters["plate_thickness"] / 2.0, 
                -input_parameters["plate_width"] / 2.0,
            ),
        )

       
        plates = plate1.fuse(plate2)

    except Exception as e:
        raise ModelException(e)
    # An entry in the parts dictionary corresponds to an STL file. This is useful for parts of differing materials.
    parts = {"plates": plates}
    return parts


# baseline model parameters
INPUT_PARAMETERS = {
    "plate_length": "150mm",
    "plate_width": "14mm",
    "plate_thickness": "1.75mm",
    "plate_offset": "7mm",
}
MODEL_NAME = os.path.splitext(os.path.basename(os.path.basename(__file__)))[0]
OUTPUT_PATH = argv[1]

model_accuracy = 10
base_model(
    model_name = MODEL_NAME,
    model_function = simple_parallel_plates_model,
    input_params = INPUT_PARAMETERS,
    output_path = OUTPUT_PATH,
    accuracy=model_accuracy,
    just_cad=0,
)
