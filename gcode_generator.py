
import math

FILE_START = "G21\nG90\n"
# G21 - Millimeters
# G90 - Absolute distance mode
# G91 - Incremental distance mode

FILE_END = "M30"

rapid_feedrate = 6000
drill_feedrate = 250
pullback_depth = 3.0
pullback_height = 1.0
clear_height = 5.0


def inch(i):
    return i * 25.4


def drill_holes(hole_list, depth):

    gc = FILE_START

    # checks
    assert depth > 0, "depth should be given as a positive number"

    # determine hole order
    # TODO: implement hold ordering

    # loop and drill
    for hole in hole_list:

        # lift
        gc += f"G1 Z{clear_height} F{drill_feedrate} \n"

        # move
        gc += f"G0 X{hole[0]} Y{hole[1]} F{rapid_feedrate} \n"

        # zero
        gc += f"G1 Z{0.0} F{drill_feedrate} \n"

        # drill - divide depth in incremental steps
        nr_cycles = math.ceil(depth / pullback_depth)
        for i in range(nr_cycles):
            sub_depth = min ((i + 1) * pullback_depth, depth)

            # drill 
            gc += f"G1 Z-{sub_depth} F{drill_feedrate} \n"

            # wait
            gc += "G4 S0.5 \n"

            # pull 
            gc += f"G1 Z{0.0} F{drill_feedrate} \n"

        # lift
        gc += f"G1 Z{clear_height} F{drill_feedrate} \n"

    # return to start
    # gc += f"G1 Z{clear_height} F{drill_feedrate} \n"
    gc += f"G0 X0.0 Y0.0 F{rapid_feedrate} \n"

    # end file
    gc += FILE_END

    return gc

# generate and preview
gc = drill_holes([[10,10], [20,20]], inch(0.25))
print(gc)

filename = 'drill.nc'

# write to file
with open(filename, 'w') as file:
    file.write(gc)

import numpy as np
from itertools import product

v = np.array([0, 1])
corners = list(product(v, v))

width, height = 10, 20
np.array(corners[3]) * np.array([width, height])


# > G4 S0.5 (line=7)
# error:28 (Invalid gcode ID:28)
# error:28 (Invalid gcode ID:28)
# error:28 (Invalid gcode ID:28)
# client> ~
# > G1 Z0.0 F250 (line=18)
# error:28 (Invalid gcode ID:28)
# error:28 (Invalid gcode ID:28)
# error:28 (Invalid gcode ID:28)
# client> ~
# [MSG:Pgm End]
# >