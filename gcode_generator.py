
from itertools import product
import math
import numpy as np

# G21 - Millimeters
# G90 - Absolute distance mode
# G91 - Incremental distance mode
# M30 - Stop program

FILE_START = """
G21
G90
"""

FILE_END = "M30"

plunge_feedrate = 250
rapid_feedrate = 6000
cut_feedrate = 900
cut_depth = 1.0
clear_height = 5.0


def inch(i):
    return i * 25.4


def create_rectangle(width, height):
    corners = product(np.array([0, 1]), np.array([0, 1]))
    return [c * np.array([width, height]) for c in corners]


def transpose(lines_list):
    return [[[p[1], p[0]] for p in line] for line in lines_list]


def cut_things(cut_list, depth):

    gc = FILE_START

    # checks
    assert depth > 0, "depth should be given as a positive number"

    # loop and cut or drill
    for cut in cut_list:

        # lift
        gc += f"G1 Z{clear_height} F{plunge_feedrate} \n"

        # cut - divide depth in incremental steps
        nr_cycles = math.ceil(depth / cut_depth)
        for i in range(nr_cycles):

            for ind, point in enumerate(cut):
                
                # move to point
                gc += f"G1 X{point[0]} Y{point[1]} F{cut_feedrate} \n"

                # on first point plunge
                if ind == 0: 
                    sub_depth = min ((i + 1) * cut_depth, depth)
                    gc += f"G1 Z-{sub_depth} F{plunge_feedrate} \n"

            # lift
            gc += f"G1 Z{clear_height} F{plunge_feedrate} \n"

    # return to start
    gc += f"G1 Z{clear_height} F{plunge_feedrate} \n"
    gc += f"G0 X0.0 Y0.0 F{rapid_feedrate} \n"

    # end file
    gc += FILE_END

    return gc
