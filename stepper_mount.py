
import gcode_generator as gg
from gcode_generator import create_elements

from parts import pillow_block, nema17

# --- settings ---

hole_to_plate = pillow_block['hole_height']
bit_size = 3
backing = gg.inch(0.5)

# calculate overlap and offset
overlap = (nema17['outer'] / 2) - hole_to_plate
offset_y = backing - overlap
offset_x = 12

# --- drill section ---

# initialize request
rc = []

holes = []
mounting_holes = create_elements(
    type = 'hole_sets',
    spacing_x = nema17['hole_spacing'],
    spacing_y = nema17['hole_spacing'],
    offset_x = nema17['offset'] + offset_x,
    offset_y = nema17['offset'] + offset_y,
)
holes.extend(mounting_holes)
holes.extend([
    [[offset_x / 2, backing / 2]],
    [[offset_x * 1.5 + nema17['outer'], backing / 2]],
])

holes = gg.order_closest_point(holes)
holes = [e[0] for e in holes]
mounting_holes = gg.order_closest_point(mounting_holes)
mounting_holes = [e[0] for e in mounting_holes]

rc.append({
    'type': 'drill',
    'points': holes,
    'depth': gg.inch(0.25),
})

# preview
frame = gg.preview(rc, bit_size)

# generate gcode
gc = gg.cut_things(rc, 9999)
print(gc)

# write to file
open('./gcode/nema17_mounting_drill_3_mm.nc', 'w').write(gc)

# --- router section ---

# settings
bit = gg.inch(0.25)

# initialize request
rc = []

# circe
rc.append({
    'type': 'circle',
    'depth': gg.inch(0.25),
    'center': [offset_x + nema17['outer'] / 2.0, offset_y + nema17['outer'] / 2.0],
    'radius': nema17['big_circle'] / 2.0 + 1 - bit / 2.0,
})

# indents
rc.append({
    'type': 'drill',
    'points': mounting_holes,
    'depth': gg.inch(0.125),
})

# outer
rc.append({
    'type': 'line',
    'points': [
        # [0 - bit / 2, 0],
        # [0 - bit / 2, backing],
        [offset_x - bit/ 2, offset_y + nema17['outer'] + bit /2],
        [offset_x + nema17['outer'] + bit / 2, offset_y + nema17['outer'] + bit /2],
        [offset_x * 2.0 + nema17['outer'] + bit / 2, backing],
        [offset_x * 2.0 + nema17['outer'] + bit / 2 , 0],
    ],
    'depth': gg.inch(0.25),
})

# preview
frame = gg.preview(rc, bit, frame)

# generate gcode
gc = gg.cut_things(rc, 0)
print(gc)

# write to file
open('./gcode/nema17_mounting_router_1_4_inch.nc', 'w').write(gc)
