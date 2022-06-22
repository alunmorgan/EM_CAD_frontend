import os
from sys import argv

from FreeCAD_geometry_generation.visualise_individual_apertures import (
   visualise_arc_aperture_with_notched_flat, visualise_cylinder_with_inserts
)
from FreeCAD_geometry_generation.freecad_operations import base_model

INPUT_PARAMETERS = {
    "flat_fraction": "0.7",
    "stripline_width": "90 deg",
    "stripline_thickness": "1.75 mm",
    "stripline_offset": "7mm",
    "stripline_blend_radius": "0.75mm",
    "shadowing_cutout_height": "1mm",
    "shadowing_cutout_depth": "1mm",
    "shadowing_cutout_blend_radius": "0.25mm",
}
#INPUT_PARAMETERS = {
 #   "cavity_radius": "25 mm",
  #  "pipe_radius": "10 mm",
   # "cavity_insert_angle": "20 deg",
    #"insert_blend_radius": "2mm",
#}
MODEL_NAME = os.path.splitext(os.path.basename(os.path.basename(__file__)))[0]
OUTPUT_PATH = argv[1]

model_accuracy = 25
base_model(
    MODEL_NAME,
    visualise_arc_aperture_with_notched_flat,
    INPUT_PARAMETERS,
    OUTPUT_PATH,
    accuracy=model_accuracy,
    just_cad=1,
)
