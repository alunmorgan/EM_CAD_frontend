import os
import sys
from sys import argv

from FreeCAD import Base
import Part
sys.path.insert(0, "V:\GitHub_Repositories\EM_CAD_frontend")
from FreeCAD_geometry_generation.freecad_apertures import \
    make_circular_aperture
from FreeCAD_geometry_generation.freecad_operations import (ModelException,
                                                            base_model,
                                                            make_beampipe,
                                                            parameter_sweep)


def simple_stripline_model(input_parameters):
    """Generates the geometry for a simplified stripline in FreeCAD. Also writes out the geometry as STL files
    and writes a "sidecar" text file containing the input parameters used.

      Args:
         input_parameters (dict): Dictionary of input parameter names and values.
    """

    try:
        # Make cavity
        wire1, face1 = make_circular_aperture(input_parameters["pipe_radius"])
        wire2, face2 = make_circular_aperture(input_parameters["cavity_radius"])
        beampipe1 = make_beampipe(
            face1,
            input_parameters["pipe_length"],
            (
                -input_parameters["pipe_length"] / 2.0
                - input_parameters["cavity_length"] / 2.0,
                0,
                0,
            ),
        )
        beampipe3 = make_beampipe(
            face1,
            input_parameters["pipe_length"],
            (
                input_parameters["pipe_length"] / 2.0
                + input_parameters["cavity_length"] / 2.0,
                0,
                0,
            ),
        )
        beampipe2 = make_beampipe(face2, input_parameters["cavity_length"])
        fin1 = beampipe1.fuse(beampipe2)
        outer = fin1.fuse(beampipe3)

        # Basic feedthrough
        cylinder1 = Part.makeCylinder(
            input_parameters["feedthrough_hole_radius"],
            100,
            Base.Vector(-input_parameters["port_offset"], -35, 0),
            Base.Vector(0, -1, 0),
        )
        cylinder2 = Part.makeCylinder(
            input_parameters["feedthrough_hole_radius"],
            100,
            Base.Vector(input_parameters["port_offset"], -35, 0),
            Base.Vector(0, -1, 0),
        )
        cylinder3 = Part.makeCylinder(
            input_parameters["feedthrough_hole_radius"],
            100,
            Base.Vector(-input_parameters["port_offset"], 35, 0),
            Base.Vector(0, 1, 0),
        )
        cylinder4 = Part.makeCylinder(
            input_parameters["feedthrough_hole_radius"],
            100,
            Base.Vector(input_parameters["port_offset"], 35, 0),
            Base.Vector(0, 1, 0),
        )
        # Pins
        pin1 = Part.makeCylinder(
            input_parameters["feedthrough_pin_radius"],
            input_parameters["cavity_radius"] - input_parameters["stripline_offset"],
            Base.Vector(-input_parameters["port_offset"], -30, 0),
            Base.Vector(0, -1, 0),
        )
        pin2 = Part.makeCylinder(
            input_parameters["feedthrough_pin_radius"],
            input_parameters["cavity_radius"] - input_parameters["stripline_offset"],
            Base.Vector(input_parameters["port_offset"], -30, 0),
            Base.Vector(0, -1, 0),
        )
        pin3 = Part.makeCylinder(
            input_parameters["feedthrough_pin_radius"],
            input_parameters["cavity_radius"] - input_parameters["stripline_offset"],
            Base.Vector(-input_parameters["port_offset"], 30, 0),
            Base.Vector(0, 1, 0),
        )
        pin4 = Part.makeCylinder(
            input_parameters["feedthrough_pin_radius"],
            input_parameters["cavity_radius"] - input_parameters["stripline_offset"],
            Base.Vector(input_parameters["port_offset"], 30, 0),
            Base.Vector(0, 1, 0),
        )

        # Basic striplines
        stripline1 = Part.makeBox(
            input_parameters["stripline_length"],
            2,
            input_parameters["stripline_width"],
            Base.Vector(
                -input_parameters["stripline_length"] / 2.0,
                30,
                -input_parameters["stripline_width"] / 2.0,
            ),
        )
        stripline2 = Part.makeBox(
            input_parameters["stripline_length"],
            2,
            input_parameters["stripline_width"],
            Base.Vector(
                -input_parameters["stripline_length"] / 2.0,
                -30,
                -input_parameters["stripline_width"] / 2.0,
            ),
        )

        diff3 = outer.cut(cylinder1)
        diff4 = diff3.cut(cylinder2)
        diff5 = diff4.cut(cylinder3)
        diff6 = diff5.cut(cylinder4)

        pins = pin1.fuse(pin2)
        pins = pins.fuse(pin3)
        pins = pins.fuse(pin4)

        striplines = stripline1.fuse(stripline2)

    except Exception as e:
        raise ModelException(e)
    # An entry in the parts dictionary corresponds to an STL file. This is useful for parts of differing materials.
    parts = {"cavity": diff6, "striplines": striplines, "pins": pins}
    return parts


# baseline model parameters
INPUT_PARAMETERS = {
    "cavity_radius": "80mm",
    "cavity_length": "180mm",
    "pipe_radius": "10mm",
    "pipe_length": "40mm",
    "port_offset": "30mm",
    "stripline_length": "150mm",
    "stripline_width": "10mm",
    "stripline_offset": "14mm",
    "feedthrough_hole_radius": "5mm",
    "feedthrough_pin_radius": "1mm",
}
MODEL_NAME = os.path.splitext(os.path.basename(os.path.basename(__file__)))[0]
OUTPUT_PATH = argv[1]

model_accuracy = 10
base_model(
    model_name = MODEL_NAME,
    model_function = simple_stripline_model,
    input_params = INPUT_PARAMETERS,
    output_path = OUTPUT_PATH,
    accuracy=model_accuracy,
    just_cad=0,
)
