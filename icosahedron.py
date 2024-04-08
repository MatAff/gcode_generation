
from support import gcode_generator as gg
from support import geometry as geo

bit_size = gg.inch(0.25)

# Icosahedron

filepath = './gcode/20230909_icosahedron.nc'

edge_length = 30
current_point = [1, edge_length * 2]

points = []
points.append(current_point)
current_point = geo.deg_to_shift(300, edge_length, current_point)
points.append(current_point)
for i in range(5):
    for deg in [300, 60, 180, 60, 180, 60, 300, 300]:
        current_point = geo.deg_to_shift(deg, edge_length, current_point)
        points.append(current_point)

# create cut list
rc = []
rc.append({'type': 'line', 'points': points, 'depth': 3.5})

# preview, generate, save
frame = gg.preview(rc, bit_size)
gc = gg.cut_things(rc, 0, cut_depth=5)
open(filepath, 'w').write(gc)

# Tetrahedron

filepath = './gcode/20230923_tetrahedron.nc'

edge_length = 30

current_point = [0, 0]

points = [current_point]
for deg in [0, 0, 120, 120, 240, 0, 240, 120, 240]:
    current_point = geo.deg_to_shift(deg, edge_length, current_point)
    points.append(current_point)

# create cut list
rc = []
rc.append({'type': 'line', 'points': points, 'depth': 3.5})

# preview, generate, save
frame = gg.preview(rc, bit_size)
gc = gg.cut_things(rc, 0, cut_depth=5)
open(filepath, 'w').write(gc)

# Octahedron

filepath = './gcode/20230923_octahedron.nc'

edge_length = 30

current_point = [0, 0]
current_point = geo.deg_to_shift(60, edge_length, current_point)

points = [current_point]
for deg in [0, 0, 0, 120, 240, 240, 120, 60, 300, 120, 120, 240, 0, 0, 180, 240, 120, 240, 120, 0]:
    current_point = geo.deg_to_shift(deg, edge_length, current_point)
    points.append(current_point)

# create cut list
rc = []
rc.append({'type': 'line', 'points': points, 'depth': 3.5})

# preview, generate, save
frame = gg.preview(rc, bit_size)
gc = gg.cut_things(rc, 0, cut_depth=5)
open(filepath, 'w').write(gc)

# Cube

filepath = './gcode/20230923_cube.nc'

edge_length = 30

current_point = [0, 0]
current_point = geo.deg_to_shift(0, edge_length, current_point)
current_point = geo.deg_to_shift(90, edge_length, current_point)

points = [current_point]
for deg in [180, 90, 0, 270, 0, 270, 0, 90, 180, 90, 0, 270, 0, 90, 180, 90, 180, 270, 180]:
    current_point = geo.deg_to_shift(deg, edge_length, current_point)
    points.append(current_point)

# create cut list
rc = []
rc.append({'type': 'line', 'points': points, 'depth': 3.5})

# preview, generate, save
frame = gg.preview(rc, bit_size)
gc = gg.cut_things(rc, 0, cut_depth=5)
open(filepath, 'w').write(gc)

# Dodecahedron

filepath = './gcode/20230923_dodecahedron.nc'

edge_length = 30

current_point = [100, 100]
points = [current_point]
deg = 0
for k in range(2):
    for i in range(5):
        for j in range(4):
            current_point = geo.deg_to_shift(deg, edge_length, current_point)
            points.append(current_point)
            deg = (deg + 72) % 360.0
        current_point = geo.deg_to_shift(deg, edge_length, current_point)
        points.append(current_point)
        deg = deg + 180
        current_point = geo.deg_to_shift(deg, edge_length, current_point)
        points.append(current_point)
        deg = (deg + 72 + 180 + 72) % 360.0
    current_point = geo.deg_to_shift(deg, edge_length, current_point)
    points.append(current_point)
    deg = deg + 72
    current_point = geo.deg_to_shift(deg, edge_length, current_point)
    points.append(current_point)
    deg = deg - 72
    current_point = geo.deg_to_shift(deg, edge_length, current_point)
    points.append(current_point)
    deg = deg + 180

# create cut list
rc = []
rc.append({'type': 'line', 'points': points, 'depth': 3.5})

# preview, generate, save
frame = gg.preview(rc, bit_size)
gc = gg.cut_things(rc, 0, cut_depth=5)
open(filepath, 'w').write(gc)

