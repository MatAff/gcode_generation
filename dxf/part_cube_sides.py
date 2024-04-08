"""Generate the six parts to make a cube.

Units are in mm.
"""

import sys; sys.path.append('..')
import math
import generate_dxf as dxf
from support import geometry

thickness = 3
inner_size = 18

def zigzag(thickness, length):
    points = [[thickness, thickness]]
    TIGHTNESS = 0.1
    if (length / thickness) % 2 != 0:
        raise ValueError('Lenght should be double multiple of thickness')
    for i in range(int(length / thickness / 2)):
        points.append([points[-1][0] + thickness - TIGHTNESS, points[-1][1]])
        points.append([points[-1][0], points[-1][1] - thickness])
        points.append([points[-1][0] + thickness + TIGHTNESS, points[-1][1]])
        points.append([points[-1][0], points[-1][1] + thickness])
    return points[:-1]

def get_cube_side(thickness, inner_size, fill_degs, blank_degs):
    center = [thickness + inner_size / 2, thickness + inner_size / 2]
    point_list = zigzag(thickness, inner_size)
    point_pair_list = dxf.point_list_to_point_pair_list(point_list)

    # Fill end
    fill_end = [point_list[-1]]
    fill_end.append([fill_end[-1][0] + thickness, fill_end[-1][1]])
    fill_end.append([fill_end[-1][0], fill_end[-1][1] + thickness])
    fill_end.append([fill_end[-1][0] - thickness, fill_end[-1][1]])

    # Blank end
    blank_end = [point_list[-1]]
    blank_end.append([blank_end[-1][0], blank_end[-1][1] + thickness])

    for i in range(3):
        point_list = [geometry.rotate(p, 90, center) for p in point_list]
        point_pair_list.extend(dxf.point_list_to_point_pair_list(point_list))

    for deg in fill_degs:
        points = [geometry.rotate(p, deg, center) for p in fill_end]
        point_pair_list.extend(dxf.point_list_to_point_pair_list(points))

    for deg in blank_degs:
        points = [geometry.rotate(p, deg, center) for p in blank_end]
        point_pair_list.extend(dxf.point_list_to_point_pair_list(points))

    return point_pair_list

def create_cube(thickness, cube_inner_size):
    fill_side = get_cube_side(thickness, inner_size, [0, 180], [90, 270])
    blank_side = get_cube_side(thickness, inner_size, [], [0, 90, 180, 270])
    cube_point_pair_list = []
    for i in range(4):
        cube_point_pair_list.extend(dxf.shift_point_pair_list(fill_side, [i * (inner_size + thickness), 0]))
    for i in range(4, 6):
        cube_point_pair_list.extend(dxf.shift_point_pair_list(blank_side, [i * (inner_size + thickness), 0]))
    dxf.create_svg(cube_point_pair_list, 'cube.svg')


def get_dodecahedron_side(thickness, inner_size):
    point_list = zigzag(thickness, inner_size)
    point_list.append([point_list[-1][0], point_list[-1][1] + thickness])
    shift = [20, 0]
    point_list = [[x + shift[0], y + shift[1]] for x, y in point_list]
    center = [
        thickness + shift[0] + inner_size / 2,
        thickness + math.tan(54 / 360 * 2 * 3.14159) * inner_size / 2
    ]
    point_pair_list = []
    for i in range(5):
        rotate_list = [geometry.rotate(p, 360 / 5 * i, center) for p in point_list]
        point_pair_list.extend(dxf.point_list_to_point_pair_list(rotate_list))
    return point_pair_list


def create_dodecahedron(thickness, inner_size):
    blank_side = get_dodecahedron_side(thickness, inner_size)
    dode_point_pair_list = []
    for i in range(3):
        for j in range(1):
            shift = [i * (inner_size * 2 + thickness), j * (inner_size * 2 + thickness)]
            dode_point_pair_list.extend(dxf.shift_point_pair_list(blank_side, shift))
    dxf.create_svg(dode_point_pair_list, 'dodecahedron.svg')


if __name__ == '__main__':
    create_dodecahedron(thickness, inner_size)
