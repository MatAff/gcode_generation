
import cv2
import numpy as np

import gcode_generator as gg
from gcode_generator import create_elements
from parts import horz_bearing, vert_bearing, shaft_support, pillow_block, nema17

# --- settings ---

# bit size
bit_size = gg.inch(0.25)
tnut_bit_size = gg.inch(3.0/8)
bearing_bit_size = 4.0

# compute screw rod distance to surface
screw_to_plate = shaft_support['hole_height'] + vert_bearing['hole_height'] - pillow_block['hole_height']
print('screw_to_plate: ' + str(screw_to_plate))

# --- spindle plate ---

# spindle plate
spindle_plate = {
    "width": 100,
    "height": 120,
}

# initialize spindle place list
sp = []

# vertical line
sp.extend(create_elements(
        type = 'even_spaced',
        start = 1, nr = 6,
        x_start = spindle_plate['width'] + bit_size / 2.0, y_start = 0,
        x_end = spindle_plate['width'] + bit_size / 2.0, y_end = (spindle_plate['height'] + bit_size / 2.0)
    ))

# horizontal line
sp.extend(create_elements(
        type = 'even_spaced',
        start = 1, nr = 6,
        x_start = 0, y_start = (spindle_plate['height'] + bit_size / 2.0),
        x_end = spindle_plate['width'] + bit_size / 2.0, y_end = (spindle_plate['height'] + bit_size / 2.0)
    ))

# mounting holes
sp.extend(create_elements(
    type = 'hole_sets',
    spacing_x = 80,
    spacing_y = gg.inch(0.5),
    offset_x = 10,
    offset_y = 10,
    nr_sets_x = 2,
    nr_sets_y = 9,
))

# clamp slots
sp.extend(create_elements(
    type = 'hole_sets',
    spacing_x = 60,
    spacing_y = gg.inch(2.0),
    offset_x = 20,
    offset_y = gg.inch(0.75),
    slot_x = 0,
    slot_y = 10,
))

# reorder - preview - gcode
sp = gg.order_closest_point(sp)
gg.preview(sp, bit_size)
gc = gg.cut_things(sp, gg.inch(0.65))

# write to file
filename_spindle_plate = './gcode/spindle_plate.nc'
with open(filename_spindle_plate, 'w') as file:
    file.write(gc)

# --- carve clamp indent ---

clamp = []

# clamp slots
clamp.extend(create_elements(
    type = 'sets_sets',
    spacing_y = 5,
    offset_x = 20,
    offset_y = gg.inch(0.75),
    nr_sets_x = 1,
    nr_sets_y = 3,
    slot_x = 60,
    slot_y = 0,
    outer_spacing_y = gg.inch(2.0),
    nr_outer_sets_x = 1,
))

# reorder - preview - gcode
clamp = gg.order_closest_point(clamp)
gg.preview(clamp, bit_size)
gc = gg.cut_things(clamp, 2.5)

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

# initialize spindle place list
zp = []

# vertical line
zp.extend(create_elements(
        type = 'even_spaced',
        start = 1, nr = 6,
        x_start = z_plate['width'] + bearing_bit_size / 2.0, y_start = 0,
        x_end = z_plate['width'] + bearing_bit_size / 2.0, y_end = (z_plate['height'] + bearing_bit_size / 2.0)
    ))

# horizontal line
zp.extend(create_elements(
        type = 'even_spaced',
        start = 1, nr = 6,
        x_start = 0, y_start = (z_plate['height'] + bearing_bit_size / 2.0),
        x_end = z_plate['width'] + bearing_bit_size / 2.0, y_end = (z_plate['height'] + bearing_bit_size / 2.0)
    ))

# bearings
zp.extend(create_elements(
    type = 'sets_sets',
    spacing_x = vert_bearing['hole_spacing_x'],
    spacing_y = vert_bearing['hole_spacing_y'],
    offset_x = vert_bearing['offset_x'],
    offset_y = vert_bearing['offset_y'],
    outer_spacing_x = z_plate['width'] - vert_bearing['width'],
    outer_spacing_y = z_plate['height'] - vert_bearing['height'],
))

# bracket
zp.extend(create_elements(
    type = 'hole_sets',
    spacing_x = 30,
    offset_x = (z_plate['width'] - 30) / 2.0,
    offset_y = z_plate['height'] / 2.0,
    nr_sets_y =  1,
))

# tnut holes
zp.extend(create_elements(
    type = 'hole_sets',
    spacing_x = 80, # mounting holes
    spacing_y = gg.inch(1.5),
    offset_x = 10, # mounting holes
    offset_y = (z_plate['height'] / 2.0) - (gg.inch(1.5) / 2.0)
))

# reorder - preview - gcode
zp = gg.order_closest_point(zp)
gg.preview(zp, bearing_bit_size)
gc = gg.cut_things(zp, gg.inch(0.5))

# write to file
filename_z_plate_bearing = './gcode/z_plate.nc'
with open(filename_z_plate_bearing, 'w') as file:
    file.write(gc)

# --- y plate ---

narrow_bit = 2.0

# y plate (needs to be wider to accomodate shaft supports)
y_plate = {
    "width": z_plate['width'] - vert_bearing['width'] + shaft_support["width"], # distance between z rods + width of support
    "height": 200
}

yp = []

# vertical line
yp.extend(create_elements(
    type = 'even_spaced',
    start = 1, nr = 4,
    x_start = y_plate['width'] + narrow_bit / 2.0, y_start = 0,
    x_end = y_plate['width'] + narrow_bit / 2.0, y_end = (y_plate['height'] + narrow_bit / 2.0)
))

# horizontal line
yp.extend(create_elements(
    type = 'even_spaced',
    start = 1, nr = 4,
    x_start = 0, y_start = (y_plate['height'] + narrow_bit / 2.0),
    x_end = y_plate['width'] + narrow_bit / 2.0, y_end = (y_plate['height'] + narrow_bit / 2.0)
))

# bracket
yp.extend(create_elements(
    type = 'hole_sets',
    spacing_y = 30,
    offset_x = (y_plate['width'] - 0) / 2.0,
    offset_y = (y_plate['height'] - 30) / 2.0,
    nr_sets_x =  1,
))

# shaft supports
yp.extend(create_elements(
    type = 'sets_sets',
    offset_x = shaft_support['offset_x'],
    offset_y = shaft_support['offset_y'],
    spacing_x = shaft_support['hole_spacing_x'],
    nr_sets_y = 1,
    outer_spacing_x = y_plate['width'] - shaft_support['width'], # this should align with z_plate['width'] - vert_bearing['width'],
    outer_spacing_y = y_plate['height'] - shaft_support['length'],
))

# pillow blocks
yp.extend(create_elements(
    type = 'sets_sets',
    offset_x = pillow_block['offset_x'],
    offset_y = pillow_block['offset_y'],
    spacing_x = pillow_block['hole_spacing_x'],
    nr_sets_y = 1,
    outer_offset_x = (y_plate['width'] - pillow_block['width']) / 2.0,
    outer_offset_y = shaft_support['length'],
    outer_spacing_y = y_plate['height'] - 2 * shaft_support['length'] - pillow_block['length'],
    nr_outer_sets_x = 1,
))

# reorder - preview - gcode
yp = gg.order_closest_point(yp)
gg.preview(yp, narrow_bit)
gc = gg.cut_things(yp, gg.inch(0.25))

# write to file
filename_z_plate_bearing = './gcode/y_plate.nc'
with open(filename_z_plate_bearing, 'w') as file:
    file.write(gc)

yp = []

# bearings
yp.extend(create_elements(
    type = 'sets_sets',
    spacing_x = horz_bearing['hole_spacing_x'],
    spacing_y = horz_bearing['hole_spacing_y'],
    offset_x = horz_bearing['offset_x'],
    offset_y = horz_bearing['offset_y'],
    outer_offset_y = (200 - 130 - horz_bearing['height']) / 2.0,
    outer_spacing_x = y_plate['width'] - horz_bearing['width'],
    outer_spacing_y = 130, # TODO: update based on measurement
))

# reorder - preview - gcode
yp = gg.order_closest_point(yp)
gg.preview(yp, bearing_bit_size)
gc = gg.cut_things(yp, gg.inch(0.25))

# write to file
filename_z_plate_bearing = './gcode/y_plate_bearing.nc'
with open(filename_z_plate_bearing, 'w') as file:
    file.write(gc)


# --- z plate finish after late fail ---

# z plate
z_plate = {
    "width": spindle_plate["width"],
    "height": 120
}

# initialize spindle place list
zp = []

# bracket
zp.extend(create_elements(
    type = 'hole_sets',
    spacing_x = 30,
    offset_x = (z_plate['width'] - 30) / 2.0,
    offset_y = z_plate['height'] / 2.0,
    nr_sets_y =  1,
))

# tnut holes
zp.extend(create_elements(
    type = 'hole_sets',
    spacing_x = 80, # mounting holes
    spacing_y = gg.inch(1.5),
    offset_x = 10, # mounting holes
    offset_y = (z_plate['height'] / 2.0) - (gg.inch(1.5) / 2.0)
))

# reorder - preview - gcode
zp = gg.order_closest_point(zp)
gg.preview(zp, bearing_bit_size)
gc = gg.cut_things(zp, gg.inch(0.5))

# write to file
filename_z_plate_bearing = './gcode/z_plate_finish.nc'
with open(filename_z_plate_bearing, 'w') as file:
    file.write(gc)


# --- nema17 mount ---

# dist to mountable surface
print(screw_to_plate)
dist_to_outer = screw_to_plate + gg.inch(0.5)
print(dist_to_outer)

bit_size = 3

# initialize list
p = [
    [[gg.inch(1.0)  - nema17['outer'] / 2 + 16, gg.inch(1.0)  - nema17['outer'] / 2 + 16]]
]

# mounting holes
p.extend(create_elements(
    type = 'hole_sets',
    spacing_x = nema17['hole_spacing'],
    spacing_y = nema17['hole_spacing'],
    offset_x = nema17['offset'] + gg.inch(1.0)  - nema17['outer'] / 2 + 16,
    offset_y = nema17['offset'] + gg.inch(1.0)  - nema17['outer'] / 2 + 16,
))

# mounting holes
p.extend(create_elements(
    type = 'hole_sets',
    spacing_x = dist_to_outer * 2,
    spacing_y = dist_to_outer * 2,
    offset_x = gg.inch(0.5),
    offset_y = gg.inch(0.5),
    nr_sets_y = 1
))


# reorder - preview - gcode
p = gg.order_closest_point(p)
gg.preview(p, bit_size)
gc = gg.cut_things(p, gg.inch(0.5))

# write to file
with open('./gcode/nema17_mounting.nc', 'w') as file:
    file.write(gc)
