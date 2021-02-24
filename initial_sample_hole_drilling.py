
from gcode_generator import drill_holes, inch

# settings
filename = './gcode/initial_sample_hole_drilling.nc'

# generate and preview
gc = drill_holes([[10,10], [20,20]], inch(0.25))
print(gc)

# write to file
with open(filename, 'w') as file:
    file.write(gc)

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

