
import cv2
import numpy as np

import gcode_generator as gg

def swap_x_y(d):
    d = {k.replace('_x', '_temp').replace('_y', '_x').replace('_temp', '_y'): v for k, v in d.items()}
    d = {k.replace('width', 'temp').replace('height', 'width').replace('temp', 'height'): v for k, v in d.items()}
    return d

# --- settings ---

# bit size
bit_size = gg.inch(0.25)
tnut_bit_size = gg.inch(3.0/8)
bearing_bit_size = gg.inch(2.0/16)

# bearing block
bearing_block = {
    "width": 34,
    "height": 30,
    "hole_spacing_x": 24,
    "hole_spacing_y": 18,
    "offset_x": (34 - 24) / 2.0,
    "offset_y": (30 - 18) / 2.0,
    "hole_height": 11
}

vert_bearing = swap_x_y(bearing_block)

# shaft support
shaft_support = {
    "width": 42,
    "length": 14,
    "hole_spacing_x": 32,
    "hole_height": 20, 
    "offset_x": (42 + 32) / 2.0,
    "offset_y": 14 / 2.0
}

# pillow block
pillow_block = {
    "width": 55, 
    "length": 13,
    "hole_spacing_x": 42,
    "hole_height": 15,
    "offset_x": (55 + 42) / 2.0,
    "offset_y": 13 / 2.0
}

# compute screw rod distance to surface
screw_to_plate = shaft_support['hole_height'] + bearing_block['hole_height'] - pillow_block['hole_height']
print('screw_to_plate: ' + str(screw_to_plate))

# --- spindle plate ---

# spindle plate clamp slots
spindle_slot = {
    "spacing_x": 60,
    "spacing_y": gg.inch(2.0), # TODO: update this,
    "offset_x": 20,
    "offset_y": gg.inch(0.75),
    "slot_length": 10,
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

# spindle plate
spindle_plate = {
    "width": 100,
    "height": 120,
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
    spindle_slot['spacing_x'], 
    spindle_slot['spacing_y'],
    [spindle_slot['offset_x'], spindle_slot['offset_y']]
)
slot_end = gg.create_rectangle(
    spindle_slot['spacing_x'], 
    spindle_slot['spacing_y'],
    [spindle_slot['offset_x'], spindle_slot['offset_y'] + spindle_slot['slot_length']]
)
clamp_lines = list(zip(slot_start, slot_end))

# join lines list
lines_list = [
    *end_marks, 
    *mounting_holes, 
    *clamp_lines
]

# reorder
lines_list = gg.order_closest_point(lines_list)

# preview
gg.preview(lines_list, bit_size)

# path
filename_spindle_plate = './gcode/spindle_plate.nc'

# generate gcode 
gc = gg.cut_things(lines_list, gg.inch(0.65))
# print(gc)

# write to file
with open(filename_spindle_plate, 'w') as file:
    file.write(gc)

# --- carve clamp indent

lines_list = [
    [slot_start[0], slot_start[2]],
    [slot_end[2], slot_end[0]],
    [slot_start[1], slot_start[3]],
    [slot_end[3], slot_end[1]],
]

# reorder
# lines_list = gg.order_closest_point(lines_list)

# preview
gg.preview(lines_list, bit_size)

# path
filename_spindle_plate = './gcode/spindle_plate_clamp_indent.nc'

# generate gcode 
gc = gg.cut_things(lines_list, 2)
# print(gc)

# write to file
with open(filename_spindle_plate, 'w') as file:
    file.write(gc)

assert False, 'hold execution here'





# z plate tnut holes
zp_tnut_holes = {
    'spacing_x': spindle_slot['spacing_x'],
    'spacing_y': gg.inch(2),
    'offset_x': 10,
    'offset_y': 10,
    'nr_sets_x': 2,
    'nr_sets_y': 2, 
}

# z plate
z_movement = 75
z_plate = {
    "width": spindle_plate["width"],
    "height": 200 - (2 * pillow_block["length"]) - z_movement
}

# z plate bearing
zp_bearings = {
    'spacing_x': z_plate['width'] - vert_bearing['width'],
    'spacing_y': z_plate['height'] - vert_bearing['height']
}

# z plate bracket
zp_bracket = {
    'spacing_x': 30,
    'spacing_y': 0,
    'offset_x': 15,
    'offset_y': 0,
    'nr_sets_x': 2,
    'nr_sets_y': 1, 
}

# y plate
y_plate = {
    "width": z_plate["width"],
    "height": 200
}


# --- create z plate - tnut ---

# mark size
end_marks = [
    [z_plate['width'] + bit_size / 2.0, z_plate['height'] + bit_size / 2.0],
    [z_plate['width'] + bit_size / 2.0, 30],
    [30, z_plate['height'] + bit_size / 2.0],
]
end_marks = gg.holes_to_lines(end_marks)

# tnut holes
tnut_holes = gg.create_holes_sets(zp_tnut_holes)
tnut_holes = gg.holes_to_lines(tnut_holes)

# join list line
lines_list = [
    *end_marks,
    *tnut_holes,
]

# preview
gg.preview(lines_list, tnut_bit_size)

# path
filename_z_plate_tnut = './gcode/z_plate_tnut.nc'

# generate gcode 
gc = gg.cut_things(lines_list, gg.inch(0.55))
print(gc)

# write to file
with open(filename_z_plate_tnut, 'w') as file:
    file.write(gc)

# --- create z plate - bearing ---

# bearing holes
bearing_template = gg.create_rectangle(
    vert_bearing['width'], 
    vert_bearing['height'],
    [vert_bearing['offset_x'], vert_bearing['offset_y']]
)
bearing_positions = gg.create_rectangle(
    zp_bearings['spacing_x'],
    zp_bearings['spacing_y']
)
[bp for bp in bearing_positions]

bearing_holes = []
for bp in bearing_positions:
    for bt in bearing_template:
        bearing_holes.append(bp + np.array(bt))
bearing_holes = gg.holes_to_lines(bearing_holes)

# bracket holes
bracket_holes = gg.create_holes_sets(zp_bracket)
bracket_holes = gg.holes_to_lines(bracket_holes)

# join list line
lines_list = [
    *bearing_holes,
    *bracket_holes,
]

# preview
gg.preview(lines_list, bearing_bit_size)

# generate gcode 
gc = gg.cut_things(lines_list, gg.inch(0.55))
print(gc)

# write to file
filename_z_plate_bearing = './gcode/z_plate_bearing.nc'
with open(filename_z_plate_bearing, 'w') as file:
    file.write(gc)

# --- create y plate ---

# 