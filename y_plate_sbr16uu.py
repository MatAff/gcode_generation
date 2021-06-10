
import gcode_generator as gg
from gcode_generator import create_elements

from parts import sbr16uu_horz, sbr_rail, vert_bearing, shaft_support

# --- settings ---

bit_5 = 5
bit_1_4 = gg.inch(0.25)
width = 100 - vert_bearing['width'] + shaft_support["width"] # distance between z rods + width of support
height = 230 # same as current
print(width, height)

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
    'depth': 12,
})

# preview
frame = gg.preview(rc, bit_1_4)

# generate gcode
gc = gg.cut_things(rc, 0)
print(gc)

# write to file
open('./gcode/y_plate_sbr16uu_1_4_inch.nc', 'w').write(gc)

# --- bearing holes ---

rail_center = sbr_rail['width'] / 2.0
current_back_panel = 180
updated_back_panel = 210
outer_spacing_y = current_back_panel - (rail_center * 2.0)
updated_outer_spacing_y = updated_back_panel - (rail_center * 2.0)
print(outer_spacing_y, updated_outer_spacing_y)

y_plate_rail_from_top = 50 # based on current 
outer_spacing_y + sbr16uu_horz['height'] + y_plate_rail_from_top - sbr16uu_horz['height'] / 2.0

# bearing holes
outer_offset_y = y_plate_rail_from_top - sbr16uu_horz['height'] / 2.0 + bit_1_4 / 2.0
bearing_holes = create_elements(
    type = 'sets_sets',
    spacing_x = sbr16uu_horz['hole_spacing_x'],
    spacing_y = sbr16uu_horz['hole_spacing_y'],
    offset_x = sbr16uu_horz['offset_x'],
    offset_y = sbr16uu_horz['offset_y'],
    outer_offset_x = bit_1_4 / 2.0,
    outer_offset_y = outer_offset_y,
    outer_spacing_x = width - sbr16uu_horz['width'],
    outer_spacing_y = outer_spacing_y, # TODO: update based on measurement
)

bearing_holes.extend(create_elements(
    type = 'hole_sets',
    spacing_y = 30,
    offset_x = (width + bit_1_4) / 2.0,
    offset_y = outer_offset_y + (outer_spacing_y + sbr16uu_horz['height'] - 30) / 2.0,
    nr_sets_x =  1,
))

outer_offset_y = height + bit_1_4 / 2.0 - updated_outer_spacing_y - sbr16uu_horz['height']

bearing_holes.extend(create_elements(
    type = 'sets_sets',
    spacing_x = sbr16uu_horz['hole_spacing_x'],
    spacing_y = sbr16uu_horz['hole_spacing_y'],
    offset_x = sbr16uu_horz['offset_x'],
    offset_y = sbr16uu_horz['offset_y'],
    outer_offset_x = bit_1_4 / 2.0,
    outer_offset_y = outer_offset_y,  
    outer_spacing_x = width - sbr16uu_horz['width'],
    outer_spacing_y = updated_outer_spacing_y,
))

bearing_holes.extend(create_elements(
    type = 'hole_sets',
    spacing_y = 30,
    offset_x = (width + bit_1_4) / 2.0,
    offset_y = outer_offset_y + (outer_spacing_y + sbr16uu_horz['height'] - 30) / 2.0,
    nr_sets_x =  1,
))


# reorder
bearing_holes = gg.order_closest_point(bearing_holes)

bearing_holes = [h[0] for h in bearing_holes]
bearing_holes = bearing_holes[33:] # fix to finish cut
rc = []

# outline
rc.append({
    'type': 'drill',
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
