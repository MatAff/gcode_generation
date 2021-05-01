
import gcode_generator as gg
from gcode_generator import create_elements

from parts import shaft_support, vert_bearing, pillow_block, nema17

# --- settings ---

screw_to_plate = shaft_support['hole_height'] + vert_bearing['hole_height'] - pillow_block['hole_height']
print('screw_to_plate: ' + str(screw_to_plate))

bit = gg.inch(0.25)
width = 80
height = 25

# outer 
outer = create_elements(
    type='hole_sets',
    spacing_x = width + bit,
    spacing_y = height + bit
)
outer = [outer[0][0], outer[2][0], outer[3][0], outer[1][0], outer[0][0]]

rc = []

rc.append({
    'type': 'circle',
    'depth': 11,
    'center': [width / 2.0 + bit / 2.0, screw_to_plate + bit / 2.0],
    'radius': 10 / 2.0 - bit / 2.0
})

rc.append({
    'type': 'circle',
    'depth': gg.inch(0.75),
    'center': [width / 2.0 + bit / 2.0, screw_to_plate + bit / 2.0],
    'radius': 8.2 / 2.0 - bit / 2.0
})

rc.append({
    'type': 'line',
    'points': outer[1:5],
    'depth': 5,
})

rc.append({
    'type': 'line',
    'points': outer[0:2],
    'depth': gg.inch(0.75),
})

# preview
frame = gg.preview(rc, bit)

# generate gcode
gc = gg.cut_things(rc, 0)
print(gc)

# write to file
open('./gcode/lead_screw_wide_1_4_inch.nc', 'w').write(gc)
