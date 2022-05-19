import sys

sys.path.insert(0, "V:\GitHub_Repositories\EM_CAD_frontend")

from FreeCAD_geometry_generation.freecad_apertures import (
    make_arc_aperture_with_notched_flat )

def visualise_arc_aperture_with_notched_flat(input_parameters):

    wire, face = make_arc_aperture_with_notched_flat(
         arc_inner_radius=input_parameters["stripline_offset"],
         arc_outer_radius= input_parameters["stripline_offset"] + input_parameters["stripline_thickness"],
         arc_length=input_parameters["stripline_width"],
         flat_fraction=input_parameters["flat_fraction"],
         notch_height=input_parameters["shadowing_cutout_height"],
         notch_depth=input_parameters["shadowing_cutout_depth"],
         notch_blend_radius=input_parameters["shadowing_cutout_blend_radius"],
         blend_radius=input_parameters["stripline_blend_radius"],
    )
    parts = {
         "wire": wire,
         "face": face,
    }
    return parts