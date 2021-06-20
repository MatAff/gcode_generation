
import math
import numpy as np

import cv2
from numpy.lib.arraysetops import isin

import gcode_generator as gg

# plot constants
FRAME_SIZE = [750,750]
PLOT_ORIGIN = [-100, 150] # (np.array(FRAME_SIZE) / -2 / SCALE).astype(int) 
SCALE = 4

ESC = 27
LEFT = 81
UP = 82
RIGHT = 83
DOWN = 84
MIN = 45
PLUS = 61

red = (0, 0, 255)
blue = (255, 0, 0)
green = (0, 255, 0)


def point_to_plot(point):
    return (np.array([-PLOT_ORIGIN[0] + point[0], PLOT_ORIGIN[1] - point[1]]) * SCALE).astype(int)


def scale_r(r):
    return r * SCALE


def interactive_plot(plot_func):

    global PLOT_ORIGIN
    global SCALE

    running = True
    while running:
        
        frame = plot_func()
        cv2.imshow('image', frame)
        key = cv2.waitKey(0)    
        print(key)
    
        if key == ESC:
            running=False
        if key == LEFT:
            PLOT_ORIGIN = [PLOT_ORIGIN[0] + 10, PLOT_ORIGIN[1]]
        if key == RIGHT:
            PLOT_ORIGIN = [PLOT_ORIGIN[0] - 10, PLOT_ORIGIN[1]]
        if key == UP:
            PLOT_ORIGIN = [PLOT_ORIGIN[0], PLOT_ORIGIN[1] - 10]
        if key == DOWN:
            PLOT_ORIGIN = [PLOT_ORIGIN[0], PLOT_ORIGIN[1] + 10]
        if key == MIN:
            SCALE = SCALE / 1.1
        if key == PLUS:
            SCALE = SCALE * 1.1

    cv2.destroyAllWindows()  


def dist(start, end):
    return ((np.array(start) - np.array(end)) ** 2).sum()**0.5


def deg_to_rad(deg):
    return deg * math.pi / 180.0


def rotate(point, deg):
    rad = deg_to_rad(deg)
    R = np.array([[math.cos(rad), -math.sin(rad)],
                  [math.sin(rad), math.cos(rad)]])
    return np.matmul(R, np.array(point))


def get_tangent_point(point, r):
    a = (point[1]**2 + point[0]**2)
    b = -2 * r**2 * point[0]
    c = r**4 - point[1]**2 * r**2 
    x1, x2 = abc(a, b, c)
    y1 = (r**2 - point[0] * x1) / point[1]
    y2 = (r**2 - point[0] * x2) / point[1]
    return [x1, y1], [x2, y2]


def abc(a, b, c):
    d = (b**2 - 4*a*c)**0.5
    return (-b+d) / (2*a), (-b-d) / (2*a)


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


def get_gear(pitch_circle, nr_teeth, pressure_angle_deg, bit_size):

    cog = {}
    
    cog['pitch_circle'] = pitch_circle
    cog['nr_teeth'] = nr_teeth
    cog['pressure_angle_deg'] = pressure_angle_deg

    cog['module'] = get_module(cog['pitch_circle'], cog['nr_teeth'])
    cog['addendum'] = get_addendum_circle(cog['pitch_circle'], cog['module'])
    cog['dedendum'] = get_dedendum_circle(cog['pitch_circle'], cog['module'])
    cog['base_circle'] = get_base_circle(cog['pitch_circle'], cog['pressure_angle_deg'])

    # get pitch point
    first_rotate = 360 / nr_teeth * 0.25
    pitch_point = rotate([0, cog['pitch_circle']], first_rotate)

    # get base point
    base_point = get_tangent_point(pitch_point, cog['base_circle'])[0]
    pitch_base_dist = dist(pitch_point, base_point)

    # roll points
    points = []
    for d in np.arange(25, -25, -0.1):
        alt_base = rotate(base_point, d)
        alt_dist = pitch_base_dist - d/180 * cog['base_circle'] * math.pi
        if alt_dist > 0:
            alt_point = get_perpendicual_point(alt_base, alt_dist)
            dist_to_center = dist([0, 0], alt_point)
            if (dist_to_center > cog['dedendum']) & (dist_to_center < (cog['addendum'] + (bit_size / 2.0))):
                points.append(alt_point)

    # store single point for tool path generation
    cog['single_points'] = points.copy()

    # add reverse points and repeat
    # TODO: move this to separate function
    for p in points[::-1]:
        points.append([p[0] * -1, p[1]])
    teeth_points = []
    for r in range(nr_teeth):
        rotate_deg = 360 / - nr_teeth * r
        for p in points:
            teeth_points.append(rotate(p, rotate_deg))
    cog['teeth_points'] = teeth_points

    return cog


def plot_cog(cog):

    # create frame and draw origin
    frame = np.zeros([*FRAME_SIZE, 3], np.uint8)	
    cv2.circle(frame, point_to_plot(center), 5, red, 1)

    # draw circles
    cv2.circle(frame, point_to_plot(center), int(scale_r(cog['pitch_circle'])), red, 1)
    cv2.circle(frame, point_to_plot(center), int(scale_r(cog['addendum'])), blue, 1)
    cv2.circle(frame, point_to_plot(center), int(scale_r(cog['dedendum'])), blue, 1)
    cv2.circle(frame, point_to_plot(center), int(scale_r(cog['base_circle'])), red, 1)

    # display teeth
    for s, e in zip(cog['teeth_points'][0:-1], cog['teeth_points'][1:]):
        cv2.line(frame, point_to_plot(s), point_to_plot(e), green)    

    # display cut
    if cog.get('all_cut_points', None) is not None:
        all_cut_points = cog['all_cut_points']
        for s, e in zip(all_cut_points[0:-1], all_cut_points[1:]):
            cv2.line(frame, point_to_plot(s), point_to_plot(e), blue)    

    return frame


def cog_tool_path(cog, bit_size):

    points = cog['single_points']
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

    # add reverse points and repeat
    for p in cut_points[::-1]:
        cut_points.append([p[0] * -1, p[1]])
    all_cut_points = []
    for r in range(nr_teeth):
        rotate_deg = 360 / - nr_teeth * r
        for p in cut_points:
            all_cut_points.append(rotate(p, rotate_deg))

    # append start
    all_cut_points.append(all_cut_points[0])
    cog['all_cut_points'] = all_cut_points

    return cog


# settings
nr_teeth = 15
pitch_circle = 50
pressure_angle_deg = 20 # degree
center = [0, 0]
bit_size = gg.inch(0.25)

# generate gear
cog = get_gear(pitch_circle, nr_teeth, pressure_angle_deg, bit_size)

# add tool path
cog = cog_tool_path(cog, bit_size)

# plot function to pass to interactive plot
def plot_func():
    return plot_cog(cog)

# interactive plot
interactive_plot(plot_func)


# --- GENERATE GCODE ---


rc = []
rc.append({'type': 'circle', 'depth': 5,  'center': [0, 0], 'radius':  0})
rc.append({'type': 'line', 'points': cog['all_cut_points'], 'depth': 6})

# preview
frame = gg.preview(rc, bit_size)

# generate gcode
gc = gg.cut_things(rc, 0)

# write to file
open('./gcode/gear.nc', 'w').write(gc)


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

