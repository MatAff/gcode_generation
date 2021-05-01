
import gcode_generator as gg
from gcode_generator import create_elements

from parts import sbr16uu_horz, vert_bearing, shaft_support

# --- settings ---

bit_5 = 5
bit_1_4 = gg.inch(0.25)
width = 100 - vert_bearing['width'] + shaft_support["width"] # distance between z rods + width of support
height = 220

# --- outline ---

# outer 
outer = create_elements(
    type='hole_sets',
    spacing_x = width + bit_1_4,
    spacing_y = height + bit_1_4
)
outer = [outer[0][0], outer[2][0], outer[3][0], outer[1][0], outer[0][0]]

rc = []

# outline
rc.append({
    'type': 'line',
    'points': outer[0:5],
    'depth': 4,
})

# preview
frame = gg.preview(rc, bit_1_4)

# generate gcode
gc = gg.cut_things(rc, 0)
print(gc)

# write to file
open('./gcode/y_plate_sbr16uu_1_4_inch.nc', 'w').write(gc)

# --- bearing holes ---

# bearing holes
bearing_holes = create_elements(
    type = 'sets_sets',
    spacing_x = sbr16uu_horz['hole_spacing_x'],
    spacing_y = sbr16uu_horz['hole_spacing_y'],
    offset_x = sbr16uu_horz['offset_x'] + bit_1_4 / 2.0,
    offset_y = sbr16uu_horz['offset_y'] + bit_1_4 / 2.0,
    outer_offset_y = (200 - 130 - sbr16uu_horz['height']) / 2.0,
    outer_spacing_x = width - sbr16uu_horz['width'],
    outer_spacing_y = 130, # TODO: update based on measurement
)

# reorder
bearing_holes = gg.order_closest_point(bearing_holes)

bearing_holes = [h[0] for h in bearing_holes]

rc = []

# outline
rc.append({
    'type': 'line',
    'points': bearing_holes,
    'depth': gg.inch(0.5),
})

# preview
frame = gg.preview(rc, bit_5, frame)

# generate gcode
gc = gg.cut_things(rc, 0)
print(gc)

# write to file
open('./gcode/y_plate_sbr16uu_5_mm.nc', 'w').write(gc)
