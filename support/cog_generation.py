
import math
import numpy as np

import cv2
from numpy.core.fromnumeric import repeat
from numpy.lib.arraysetops import isin

# plot constants
FRAME_SIZE = [750,750]
PLOT_ORIGIN = [-100, 150] 
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
    # TODO: switch to using geometry.py
    return ((np.array(start) - np.array(end)) ** 2).sum()**0.5


def deg_to_rad(deg):
    # TODO: switch to using geometry.py
    return deg * math.pi / 180.0


def rad_to_deg(rad):
    # TODO: switch to using geometry.py
    return rad / math.pi * 180.0


def rotate(point, deg, reference=np.array([0,0])):
    # TODO: switch to using geometry.py
    rad = deg_to_rad(deg)
    R = np.array([[math.cos(rad), -math.sin(rad)],
                  [math.sin(rad), math.cos(rad)]])
    return np.matmul(R, (np.array(point) - reference)) + reference


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
        return [0, offset], [0, -offset]
    elif dx == 0:
        return [offset, 0], [-offset,  0]
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


def mirror(points):
    for p in points[::-1]:
        points.append([p[0] * -1, p[1]])
    return points


def repeat(points, nr_reps):
    repeat_points = []
    for r in range(nr_reps):
        rotate_deg = 360 / - nr_reps * r
        for p in points:
            repeat_points.append(rotate(p, rotate_deg))
    return repeat_points


def reverse_repeat_points(points, nr_reps):

    for p in points[::-1]:
        points.append([p[0] * -1, p[1]])
    repeat_points = []
    for r in range(nr_reps):
        rotate_deg = 360 / - nr_reps * r
        for p in points:
            repeat_points.append(rotate(p, rotate_deg))
    return repeat_points


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
    cog['teeth_points'] = reverse_repeat_points(points, nr_teeth)

    return cog


def plot_cog(cog):

    center = [0, 0]

    # create frame and draw origin
    frame = np.zeros([*FRAME_SIZE, 3], np.uint8)	
    cv2.circle(frame, point_to_plot(center), 5, red, 1)

    # draw circles
    cv2.circle(frame, point_to_plot(center), int(scale_r(cog.get('pitch_circle', 0))), red, 1)
    cv2.circle(frame, point_to_plot(center), int(scale_r(cog.get('addendum', 0))), blue, 1)
    cv2.circle(frame, point_to_plot(center), int(scale_r(cog.get('dedendum', 0))), blue, 1)
    cv2.circle(frame, point_to_plot(center), int(scale_r(cog.get('base_circle', 0))), red, 1)

    # display teeth
    for s, e in zip(cog['teeth_points'][0:-1], cog['teeth_points'][1:]):
        cv2.line(frame, point_to_plot(s), point_to_plot(e), green)    

    # display cut
    if cog.get('all_cut_points', None) is not None:
        all_cut_points = cog['all_cut_points']
        for s, e in zip(all_cut_points[0:-1], all_cut_points[1:]):
            cv2.line(frame, point_to_plot(s), point_to_plot(e), blue)    

    # display inner
    if cog.get('inner', None) is not None:
        for inner_set in cog['inner']:
            for s, e in zip(inner_set[0:-1], inner_set[1:]):
                cv2.line(frame, point_to_plot(s), point_to_plot(e), green)    

    # display inner cut
    if cog.get('inner_cut', None) is not None:
        for inner_set in cog['inner_cut']:
            for s, e in zip(inner_set[0:-1], inner_set[1:]):
                cv2.line(frame, point_to_plot(s), point_to_plot(e), blue)    


    return frame


def plot_dict(frame, d):
    for k, v in d.items():
        for s, e in zip(v[0:-1], v[1:]):
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
    for r in range(cog['nr_teeth']):
        rotate_deg = 360 / - cog['nr_teeth'] * r
        for p in cut_points:
            all_cut_points.append(rotate(p, rotate_deg))

    # append start
    all_cut_points.append(all_cut_points[0])
    cog['all_cut_points'] = all_cut_points

    return cog


def pendulum_cog(circle, teeth_depth, nr_teeth, bit_size):
    cog = {}
    points = []
    points.append(rotate([0, circle], 360/nr_teeth/2.0))
    points.append([0, circle])
    points.append([0, circle + teeth_depth])
    points.append(rotate([0, circle], 360/nr_teeth/-2.0))

    cog['nr_teeth'] = nr_teeth
    cog['single_points'] = points
    teeth_points = repeat(points, nr_teeth)
    teeth_points.append(teeth_points[0])
    cog['teeth_points'] = teeth_points

    # add tool path
    cut_points = []
    cut_points.append([bit_size / -2.0, circle])
    cut_points.append([bit_size / -2.0, circle + teeth_depth + bit_size / 2.0])
    cut_points.append([bit_size / 2.0, circle + teeth_depth + bit_size / 2.0])
    all_cut_points = repeat(cut_points, nr_teeth)
    all_cut_points.append(all_cut_points[0])
    cog['all_cut_points'] = all_cut_points
    
    return cog


def inner_cuts(min_y, max_y, width, nr=3):
    points = []
    points.append([-width, max_y])
    points.append([-width, min_y])
    points.append(rotate([width, min_y], 360.0/nr))
    points.append(rotate([width, max_y], 360.0/nr))
    for deg in range(10):
        new_point = rotate(rotate([width, max_y], 360.0/nr), deg*-10)
        if new_point[0] < -width:
            points.append(new_point)
        else:
            break
    points.append(points[0])
    points_list = []
    for i in range(nr):
        points_list.append([rotate(p, 360/nr * i) for p in points])
    return points_list


def arr(p):
    if isinstance(p, np.ndarray):
        return p
    return np.array(p)
    
def get_perpendicular_vec_new(s, e, offset=None):
    # TODO: deprecate the old version and consolidate
    delta = arr(e) - arr(s)
    delta_perp = np.array([-delta[1], delta[0]])
    if offset is not None:
        delta_perp = delta_perp / dist(s, e) * offset
    return delta_perp

def get_tool_path(points, offset):
    
    # get lines
    lines = []
    for s, e in zip(points[0:-1], points[1:]):
        lines.append([s, e])
    lines.append(lines[0])
    lines.append(lines[1])

    # get paralel lines: 
    para_lines = []
    for line in lines:
        perp_vec = get_perpendicular_vec_new(*line, offset)
        p_line = [line[0] + perp_vec, line[1] + perp_vec]
        para_lines.append(p_line)

    cut_points = [para_lines[0][0].tolist()]
    i = 0
    while i < len(para_lines):
        print(i)
        s = para_lines[i][0]
        e = para_lines[i][1]

        # compare to other lines
        j = i + 1
        closest_int = None
        closest_int_dist = 999
        closest_j = None
        while j < len(para_lines):
            if dist(e, para_lines[j][0]) < 10:
                int = intersect(*para_lines[i], *para_lines[j]).tolist()[0]

                # update int
                int_dist = dist(s, int)
                if int_dist < closest_int_dist:
                    closest_int_dist = int_dist
                    closest_int = int
                    closest_j = j
            else:
                break
            j = j + 1
        
        if closest_int is None:
            break
        cut_points.append(closest_int)
        i = closest_j

    return cut_points