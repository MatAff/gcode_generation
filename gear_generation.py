
import math
import numpy as np

import cv2
from numpy.lib.arraysetops import isin

import gcode_generator as gg

# plot constants
FRAME_SIZE = [750,750]
PLOT_ORIGIN = [-100, 150] # (np.array(FRAME_SIZE) / -2 / SCALE).astype(int) 
SCALE = 4


def deg_to_rad(deg):
    return deg * math.pi / 180.0


def get_circular_pitch(pitch_circle):
    return pitch_circle * math.pi


def get_base_circle(pitch_circle, pressure_angle_deg):
    return pitch_circle * math.cos(deg_to_rad(pressure_angle_deg))


def get_module(pitch_circle, nr_teeth):
    return pitch_circle / nr_teeth


def get_addendum_circle(pitch_circle, module):
    return pitch_circle + 1.0 * module


def get_dedendum_circle(pitch_circle, module):
    return pitch_circle - 1.25 * module


def rotate(point, deg):
    rad = deg_to_rad(deg)
    R = np.array([[math.cos(rad), -math.sin(rad)],
                  [math.sin(rad), math.cos(rad)]])
    return np.matmul(R, np.array(point))


def point_to_plot(point):
    # return (PLOT_ORIGIN - (np.array(point)) * SCALE).astype(int)
    return (np.array([-PLOT_ORIGIN[0] + point[0], PLOT_ORIGIN[1] - point[1]]) * SCALE).astype(int)


def scale_r(r):
    return r * SCALE


def dist(start, end):
    return ((np.array(start) - np.array(end)) ** 2).sum()**0.5


def abc(a, b, c):
    d = (b**2 - 4*a*c)**0.5
    return (-b+d) / (2*a), (-b-d) / (2*a)


def get_tangent_point(point, r):
    a = (point[1]**2 + point[0]**2)
    b = -2 * r**2 * point[0]
    c = r**4 - point[1]**2 * r**2 
    x1, x2 = abc(a, b, c)
    y1 = (r**2 - point[0] * x1) / point[1]
    y2 = (r**2 - point[0] * x2) / point[1]
    return [x1, y1], [x2, y2]


def get_perpendicual_point(point, dist):
    rad = math.atan(point[1]/point[0])
    if rad < 0:
        rad = rad + math.pi
    x = dist * -math.sin(rad) + point[0]
    y = dist * math.cos(rad) + point[1]
    return [x, y]


def get_perpendicular_vec(start, end, offset):
    dx = end[0] - start[0]
    dy = end [1] - start[1]
    if dy == 0:
        return [0, 1], [0, -1]
    elif dx == 0:
        return [1, 0], [-1,  0]
    else:
        ddx = 1
        ddy = -dx / dy
        dd_dist = dist([0, 0], [ddx, ddy])
        ddx = ddx / dd_dist * offset
        ddy = ddy / dd_dist * offset
        return [ddx, ddy], [-ddx, -ddy]


def get_offset_lines(s, e, offset):
    perp_list = get_perpendicular_vec(s, e, offset)
    if isinstance(perp_list,tuple):
        perp_list = np.array(perp_list)
    return (
        [(s + perp_list[0]).tolist(), (e + perp_list[0]).tolist()], 
        [(s + perp_list[1]).tolist(), (e + perp_list[1]).tolist()]
    ) 


def to_matrix(*args):
    res = ()
    for a in args:
        res = (*res, np.matrix(a))
    return res

def intersect(A, B, C, D):
    A, B, C, D = to_matrix(A, B, C, D)
    CA = A - C
    AB = B - A
    CD = D - C
    s = np.cross(CA,AB) / np.cross(CD, AB)
    return(C + s * CD)


# settings
nr_teeth = 15
pitch_circle = 50
pressure_angle_deg = 20 # degree
center = [0, 0]

red = (0, 0, 255)
blue = (255, 0, 0)
green = (0, 255, 0)

bit_size = gg.inch(0.25)


# TODO
# - avoid weird back and forth at the bottom
#   - due to perpendicular crossing y axis? 
# - convert to gcode

# def get_gear(pitch_circle, nr_teeth, pressure_angle_deg):

module = get_module(pitch_circle, nr_teeth)
addendum = get_addendum_circle(pitch_circle, module)
dedendum = get_dedendum_circle(pitch_circle, module)
base_circle = get_base_circle(pitch_circle, pressure_angle_deg)

# create frame and draw origin
frame = np.zeros([*FRAME_SIZE, 3], np.uint8)	
cv2.circle(frame, point_to_plot(center), 5, red, 1)

# draw circles
cv2.circle(frame, point_to_plot(center), int(scale_r(pitch_circle)), red, 1)
cv2.circle(frame, point_to_plot(center), int(scale_r(addendum)), blue, 1)
cv2.circle(frame, point_to_plot(center), int(scale_r(dedendum)), blue, 1)
cv2.circle(frame, point_to_plot(center), int(scale_r(base_circle)), red, 1)

# get pitch point
first_rotate = 360 / nr_teeth * 0.25
pitch_point = rotate([0, pitch_circle], first_rotate)
cv2.circle(frame, point_to_plot(pitch_point), 1, green, 3)

# get base point
base_point = get_tangent_point(pitch_point, base_circle)[0]
pitch_base_dist = dist(pitch_point, base_point)
cv2.circle(frame, point_to_plot(base_point), 1, green, 3)

# roll points
points = []
for d in np.arange(25, -25, -0.1):
    alt_base = rotate(base_point, d)
    alt_dist = pitch_base_dist - d/180 * base_circle * math.pi
    if alt_dist > 0:
        alt_point = get_perpendicual_point(alt_base, alt_dist)
        dist_to_center = dist([0, 0], alt_point)
        if (dist_to_center > dedendum) & (dist_to_center < (addendum + (bit_size / 2.0))):
            points.append(alt_point)

single_points = points.copy()

# add reverse points
for p in points[::-1]:
    points.append([p[0] * -1, p[1]])

# repeat
teeth_points = []
for r in range(nr_teeth):
    rotate_deg = 360 / - nr_teeth * r
    for p in points:
        teeth_points.append(rotate(p, rotate_deg))

# display teeth
for s, e in zip(teeth_points[0:-1], teeth_points[1:]):
    cv2.line(frame, point_to_plot(s), point_to_plot(e), green)    

points = single_points

# def points_to_path(points, bit_size):

offset = bit_size / 2.0

cut_points = []

last_line = None
for p_pos in range(len(points)-2):
    s = points[p_pos]
    m = points[p_pos + 1]
    e = points[p_pos + 2]

    current_offsets = get_offset_lines(s, m, offset)
    next_offsets = get_offset_lines(m, e, offset)

    # weak point
    if last_line is None:
        last_line = current_offsets[1]

    # compute intersects with next offsets
    A, B = last_line[0], last_line[1]
    C, D = next_offsets[1][0], next_offsets[1][1]
    intersect_point = intersect(A, B, C, D)
    cut_points.append(intersect_point.tolist()[0])
    last_line = [C, D]


# add reverse points
for p in cut_points[::-1]:
    cut_points.append([p[0] * -1, p[1]])

# repeat
all_cut_points = []
for r in range(nr_teeth):
    rotate_deg = 360 / - nr_teeth * r
    for p in cut_points:
        all_cut_points.append(rotate(p, rotate_deg))

# append start
all_cut_points.append(all_cut_points[0])

# display teeth
for s, e in zip(all_cut_points[0:-1], all_cut_points[1:]):
    cv2.line(frame, point_to_plot(s), point_to_plot(e), blue)    





# start pos
# get offset line
# computer intersect with offset line
# go to intersect

cv2.imshow('image',frame)
cv2.waitKey(0)    
cv2.destroyAllWindows()  

# --- GENERATE GCODE ---

rc = []

rc.append({
    'type': 'circle',
    'depth': 5,
    'center': [0, 0],
    'radius':  0
})

rc.append({
    'type': 'line',
    'points': all_cut_points,
    'depth': 6,
})

# preview
frame = gg.preview(rc, bit_size)

# generate gcode
gc = gg.cut_things(rc, 0)
print(gc)

# write to file
open('./gcode/first_gear.nc', 'w').write(gc)



# --- TEST FUNCTIONS ---


def test_dist():
    start = [0, 0]
    end = [3, 4]
    exp = 5
    assert dist(start, end) == exp

test_dist()

def test_get_tangent_point():
    point = [5, 3]
    r = 2
    [x1, y1], [x2, y2] = get_tangent_point(point, r)

    assert all(np.array([x1, y1]).round(3) == np.array([1.5548045132, -1.2580075220]).round(3)), [x1, y1]
    assert all(np.array([x2, y2]).round(3) == np.array([-0.3783339250, 1.9638898750]).round(3)), [x2, y2]

test_get_tangent_point()

def test_get_perpendicular_vec():
    tc_list = [
        ({'start': [0, 0], 'end': [1, 0], 'offset': 1}, ([0, 1], [0, -1])),
        ({'start': [1, 1], 'end': [4, 5], 'offset': 1}, ([0.8, -0.6], [-0.8, 0.6])),
        ({'start': [-1, 1], 'end': [0, 2], 'offset': 1}, ([-0.707, 0.707], [0.707, -0.707]))
    ]
    for tc in tc_list:
        res = get_perpendicular_vec(**tc[0])
        for e in res:
            assert np.array(e).round(3).tolist() in tc[1], (e, tc[1])

test_get_perpendicular_vec()

def test_get_offset_lines():
    tc_list = [
        {'in': {'s': [0, 0], 'e': [1, 0], 'offset': 1}, 'exp': ([[0, 1], [1, 1]], [[0, -1], [1, -1]])}
    ]
    for tc in tc_list:
        res = get_offset_lines(**tc['in'])
        for e in tc['exp']:
            assert e in res, (e, res) 

test_get_offset_lines()



# steps
# define dedendum circle as a list of line segments by number of teeth
# define addendum circle as a list of line segments by number of teeth
# define straight line between point on the pitch circle and dedeundum circle
# calculate the intersect between the addenbum and involute
# iteteratively cut calculate mid point on involute line, till required precision is reached
# mirror involute
# multiply and rotate

# def scale_point(point, FRAME_SIZE, scale=2):
#     center = (np.array(FRAME_SIZE) / 2).astype(int)
#     return center - (np.array(point) * 2).astype(int)


