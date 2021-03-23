
import cv2
import numpy as np

import gcode_generator as gg

from parts import bearing_block, vert_bearing, shaft_support, pillow_block

# --- settings ---

# bit size
bit_size = gg.inch(0.25)
tnut_bit_size = gg.inch(3.0/8)
bearing_bit_size = gg.inch(5.0/16)

# compute screw rod distance to surface
screw_to_plate = shaft_support['hole_height'] + bearing_block['hole_height'] - pillow_block['hole_height']
print('screw_to_plate: ' + str(screw_to_plate))

# --- spindle plate ---

# spindle plate
spindle_plate = {
    "width": 100,
    "height": 120,
}

# spindle plate mounting holes
sp_mounting_holes = {
    'spacing_x': 80,
    'spacing_y': gg.inch(0.5),
    'offset_x': 10,
    'offset_y': 10,
    'nr_sets_x': 2,
    'nr_sets_y': 9,
}

# spindle plate clamp slots
spindle_slot = {
    "spacing_x": 60,
    "spacing_y": gg.inch(2.0),
    "offset_x": 20,
    "offset_y": gg.inch(0.75),
    "slot_length": 10,
}

# mark size
end_marks = [
    [spindle_plate['width'] + bit_size / 2.0, spindle_plate['height'] + bit_size / 2.0],
    [spindle_plate['width'] + bit_size / 2.0, 30],
    [30, spindle_plate['height'] + bit_size / 2.0],
]
end_marks = gg.holes_to_lines(end_marks)

# mounting holes
mounting_holes = gg.create_holes_sets(sp_mounting_holes)
mounting_holes = gg.holes_to_lines(mounting_holes)

# slots
slot_start = gg.create_rectangle(
    width = spindle_slot['spacing_x'],
    height = spindle_slot['spacing_y'],
    offset_x_y = [spindle_slot['offset_x'], spindle_slot['offset_y']]
)
slot_end = gg.create_rectangle(
    width = spindle_slot['spacing_x'],
    height = spindle_slot['spacing_y'],
    offset_x_y = [spindle_slot['offset_x'], spindle_slot['offset_y'] + spindle_slot['slot_length']]
)
clamp_lines = list(zip(slot_start, slot_end))

# lines list - reorder - preview - gcode
lines_list = [*end_marks, *mounting_holes, *clamp_lines]
lines_list = gg.order_closest_point(lines_list)
gg.preview(lines_list, bit_size)
gc = gg.cut_things(lines_list, gg.inch(0.65))

# write to file
filename_spindle_plate = './gcode/spindle_plate.nc'
with open(filename_spindle_plate, 'w') as file:
    file.write(gc)

# --- carve clamp indent ---

# lines list - reorder - preview - gcode
lines_list = [[slot_start[0], slot_start[2]], [slot_end[2], slot_end[0]],
    [slot_start[1], slot_start[3]], [slot_end[3], slot_end[1]],
]
# lines_list = gg.order_closest_point(lines_list)
gg.preview(lines_list, bit_size)
gc = gg.cut_things(lines_list, 2)

# write to file
filename_spindle_plate = './gcode/spindle_plate_clamp_indent.nc'
with open(filename_spindle_plate, 'w') as file:
    file.write(gc)

# --- create z plate ---

# z plate
z_plate = {
    "width": spindle_plate["width"],
    "height": 120
}

# z plate bearing (place in corners)
zp_bearings = {
    'spacing_x': z_plate['width'] - vert_bearing['width'],
    'spacing_y': z_plate['height'] - vert_bearing['height']
}

# z plate bracket
zp_bracket = {
    'spacing_x': 30,
    'spacing_y': 0,
    'offset_x': (z_plate['width'] - 30) / 2.0,
    'offset_y': z_plate['height'] / 2.0,
    'nr_sets_x': 2,
    'nr_sets_y': 1,
}

# z plate tnut holes (these need to be sunk, otherwise they conflict with bearing blocks)
zp_tnut_holes = {
    'spacing_x': sp_mounting_holes['spacing_x'],
    'spacing_y': gg.inch(1.5),
    'offset_x': sp_mounting_holes['offset_x'],
    'offset_y': (z_plate['height'] / 2.0) - (gg.inch(1.5) / 2.0),
    'nr_sets_x': 2,
    'nr_sets_y': 2,
}

# mark size
end_marks = [
    [z_plate['width'] + bearing_bit_size / 2.0, z_plate['height'] + bearing_bit_size / 2.0],
    [z_plate['width'] + bearing_bit_size / 2.0, 30],
    [30, z_plate['height'] + bearing_bit_size / 2.0],
]
end_marks = gg.holes_to_lines(end_marks)

# bearing holes
bearing_template = gg.create_rectangle(
    width = vert_bearing['hole_spacing_x'],
    height = vert_bearing['hole_spacing_y'],
    offset_x_y = [vert_bearing['offset_x'], vert_bearing['offset_y']]
)
bearing_positions = gg.create_rectangle(
    width = zp_bearings['spacing_x'],
    height = zp_bearings['spacing_y']
)

bearing_holes = []
for bp in bearing_positions:
    for bt in bearing_template:
        bearing_holes.append(bp + np.array(bt))
bearing_holes = gg.holes_to_lines(bearing_holes)

# bracket holes
bracket_holes = gg.create_holes_sets(zp_bracket)
bracket_holes = gg.holes_to_lines(bracket_holes)

# tnut holes (manually drill to increase to required size)
tnut_holes = gg.create_holes_sets(zp_tnut_holes)
tnut_holes = gg.holes_to_lines(tnut_holes)

# lines list - reorder - preview - gcode
lines_list = [*end_marks, *bearing_holes, *bracket_holes, *tnut_holes]
lines_list = gg.order_closest_point(lines_list)
gg.preview(lines_list, bearing_bit_size)
gc = gg.cut_things(lines_list, gg.inch(0.55))

# write to file
filename_z_plate_bearing = './gcode/z_plate.nc'
with open(filename_z_plate_bearing, 'w') as file:
    file.write(gc)

# --- y plate ---

# y plate (needs to be wider to accomodate shaft supports)
y_plate = {
    "width": zp_bearings['spacing_y'] + shaft_support["width"], # distance between z rods + width of support
    "height": 200
}

# end marks
end_marks = [
    [y_plate['width'] + bearing_bit_size / 2.0, y_plate['height'] + bearing_bit_size / 2.0],
    [y_plate['width'] + bearing_bit_size / 2.0, 30],
    [30, y_plate['height'] + bearing_bit_size / 2.0],
]
end_marks = gg.holes_to_lines(end_marks)

# shaft supports
shaft_template = gg.create_rectangle(
    width = shaft_support['hole_spacing_x'],
    height = 0,
    offset_x_y = [shaft_support['offset_x'], shaft_support['offset_y']]
)[[0, 2]] # [[0, 2]] to get just the two points we need
shaft_positions = gg.create_rectangle(
    width = y_plate['width'] - shaft_support['width'],
    height = y_plate['height'] - shaft_support['length']
)

shaft_holes = []
for bp in shaft_positions:
    for bt in shaft_template:
        shaft_holes.append(bp + np.array(bt))
shaft_holes = gg.holes_to_lines(shaft_holes)

# pillow block

# bearing holes
# bearing_template = gg.create_rectangle(
#     bearing_block['hole_spacing_x'],
#     bearing_block['hole_spacing_y'],
#     [bearing_block['offset_x'], bearing_block['offset_y']]
# )
# bearing_positions = gg.create_rectangle(
#     yp_bearings['spacing_x'],
#     yp_bearings['spacing_y']
# )

# bearing_holes = []
# for bp in bearing_positions:
#     for bt in bearing_template:
#         bearing_holes.append(bp + np.array(bt))
# bearing_holes = gg.holes_to_lines(bearing_holes)

# # bracket holes
# bracket_holes = gg.create_holes_sets(yp_bracket)
# bracket_holes = gg.holes_to_lines(bracket_holes)

# lines list - reorder - preview - gcode
lines_list = [*end_marks, *shaft_holes]
lines_list = gg.order_closest_point(lines_list)
gg.preview(lines_list, bearing_bit_size)
gc = gg.cut_things(lines_list, gg.inch(0.55))

# write to file
filename_z_plate_bearing = './gcode/y_plate.nc'
with open(filename_z_plate_bearing, 'w') as file:
    file.write(gc)
