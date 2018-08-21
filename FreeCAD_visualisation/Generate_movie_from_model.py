
from pivy import coin
from math import radians
import FreeCADGui as Gui
from sys import argv

_1, OUTPUT_PATH = argv


def spin_model(x_axis, y_axis, z_axis, output_location):
    """ Generates a series of images, with each one having the model turned further on a common axis.
        Args:
            x_axis (float): Represents the length of the axis vector in the x direction.
            y_axis (float): Represents the length of the axis vector in the y direction.
            z_axis (float): Represents the length of the axis vector in the z direction.
            output_location (str): File location that the output files will be put. 
    """
    Gui.ActiveDocument.ActiveView.viewBottom()
    Gui.SendMsgToActiveView("ViewFit")

    for ang in range(360):
        rotateview(x_axis, y_axis, z_axis, 1.0)
        new_f_name = ''.join([output_location, str(ang).zfill(3), '.png'])
        Gui.ActiveDocument.ActiveView.saveImage(new_f_name, 738, 676, 'Current')


def rotateview(axis_x=0.7071, axis_y=0.5, axis_z=0.5, angle=1.0):
    """ Changes the view of the model by the angle requested along the axis defined by axis_x, axis_y and axis_z.
    axis_x, axis_y and axis_z must vector sum to 1.
    
        Args:  
             axis_x (float): Represents the length of the axis vector in the x direction.
             axis_y (float): Represents the length of the axis vector in the y direction.
             axis_z (float): Represents the length of the axis vector in the z direction.
             angle (float): The angle to rotate the model by (degrees). 
    """

    # Based on code from the Freecad website,
    cam = Gui.ActiveDocument.ActiveView.getCameraNode()
    centre = coin.SbVec3f(find_centre())
    rot = coin.SbRotation()
    original_pos = coin.SbVec3f(cam.position.getValue())
    direction = coin.SbVec3f(axis_x, axis_y, axis_z)
    rot.setValue(direction, radians(angle))
    nrot = cam.orientation.getValue() * rot
    prot = rot.multVec(original_pos - centre) + centre
    cam.orientation = nrot
    cam.position = prot


def find_centre():
    """ Finds the centre of the model.
    Based on code from the Freecad website.
    """
    xmax = xmin = ymax = ymin = zmax = zmin = 0
    for obj in App.ActiveDocument.Objects:
        if obj.TypeId[:4] == "Mesh":
            box = obj.Mesh.BoundBox
        elif obj.TypeId[:6] == "Points":
            box = obj.Points.BoundBox
        elif obj.TypeId[:4] == "Part":
            box = obj.Shape.BoundBox
        else:
            continue
        xmax = max(xmax, box.XMax)
        xmin = min(xmin, box.XMin)
        ymax = max(ymax, box.YMax)
        ymin = min(ymin, box.YMin)
        zmax = max(zmax, box.ZMax)
        zmin = min(zmin, box.ZMin)

    centre = FreeCAD.Vector((xmax + xmin) / 2.0, (ymax + ymin) / 2.0, (zmax + zmin) / 2.0)
    return centre

# Call this script from the freeCad python command line
# exec(open("./path/to/script.py output_path").read(), globals())
spin_model(0.7071, 0.5, 0.5, OUTPUT_PATH)
# After images are generated use:
# ffmpeg - framerate 12 - test%03d.png output.png
# 'C:/Program files (x86)/ffmpeg-3.2.4-win64-static/bin/ffmpeg.exe - framerate 12 - test%03d.png output.png'
