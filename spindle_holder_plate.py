
import numpy as np

from gcode_generator import drill_holes, cut_things, inch, create_rectangle

# --- mounting holes - 1/4 inch drill ---

# settings
filename = './gcode/spindle_holder_plate_mounting_holes.nc'

offset_x = 15 # mm
offset_y = 40 # mm
width = 70 # mm apart
height = 40 # mm apart

# create hole grid
holes = create_rectangle(width, height)
print(holes)

# add offset
holes = holes + np.array([offset_x, offset_y])

# swap x and y
holes[:, [1, 0]] = holes[:, [0, 1]]
print(holes)

# generate and preview
gc = drill_holes(holes, inch(0.5))
print(gc)

# write to file
with open(filename, 'w') as file:
    file.write(gc)

# --- clamp slots and outline - 1/4 router bit ---

# settings
filename = './gcode/spindle_holder_plate_clamp_outline.nc'

# clamp slot settings
clamp_width = 65
clamp_height = 30
clamp_offset_x = 20
clamp_offset_y = 50
clamp_slot_length = 15

# outline settings
overall_width = offset_x + width + offset_x + inch(0.25 / 2)
overall_height = offset_y + height + offset_y + inch(0.25 / 2)

# create clamp slot lines
clamp_offset_start = np.array([clamp_offset_x, clamp_offset_y])
clamp_offset_end = np.array([clamp_offset_x, clamp_offset_y + clamp_slot_length])
slot_start = create_rectangle(clamp_width, clamp_height) + clamp_offset_start
slot_end = create_rectangle(clamp_width, clamp_height) + clamp_offset_end
clamp_lines = list(zip(slot_start, slot_end))

# create outline
outline = [
    [overall_width, 0], 
    [overall_width, overall_height],
    [0, overall_height],
]

# create lines list
lines_list = [*clamp_lines, outline]
print(lines_list)

# generate gcode 
gc = cut_things(lines_list, inch(0.5))
print(gc)

# write to file
with open(filename, 'w') as file:
    file.write(gc)
