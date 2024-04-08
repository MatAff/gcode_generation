from support import gcode_generator as gg
from support import geometry as geo

bit_size = gg.inch(0.25)

# Note folding make make the inner dimensions smaller.
x = 60
y = 45
z = 45
outer_buffer = 3

filepath = f'./gcode/20230924_box_{x}_{y}_{z}.nc'

current_point = [x + outer_buffer, z + outer_buffer]

points = [current_point]
for deg, l in [
    (180, x), (90, y), (0, x), (270, y),  # Left box.
    (0, z),  # Connect.
    (270, z), (0, x), (90, z), (180, x),  # Top box.
    (90, y), (0, x),  # Connect.
    (270, y), (0, z), (90, y), (180, z),  # Right box.
    (90, z), (180, x), (270, z), # Bottom box
    (180, z), # Connect # End
    ]:
    current_point = geo.deg_to_shift(deg, l, current_point)
    points.append(current_point)

# create cut list
rc = []
points = geo.flip_x_and_y(points)
points = geo.round_points(points)
rc.append({'type': 'line', 'points': points, 'depth': 3})

# Outer cut
current_point = [current_point[0], current_point[1] + outer_buffer]
points = [current_point]
for deg, l in [
    (180, x + outer_buffer), (270, y + 2 * outer_buffer), (0, x), (0, z),
    (270, z), (0, x + 2 * outer_buffer), (90, z), (0, z),
    (90, y + 2 * outer_buffer), (180, z), (90, z),
    (180, x + 2 * outer_buffer), (270, z), (180, z),
]:
    current_point = geo.deg_to_shift(deg, l, current_point)
    points.append(current_point)

# Add to cut list
points = geo.flip_x_and_y(points)
points = geo.round_points(points)
rc.append({'type': 'line', 'points': points, 'depth': 6})

# preview, generate, save
frame = gg.preview(rc, bit_size)
gc = gg.cut_things(rc, 0, cut_depth=5)
open(filepath, 'w').write(gc)
