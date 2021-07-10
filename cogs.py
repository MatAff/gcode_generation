
import gcode_generator as gg

from cog_generation import (
    pendulum_cog, 
    inner_cuts, 
    plot_cog,
    interactive_plot,
    get_gear,
    cog_tool_path,
)

bit_size = gg.inch(0.25)

# --- PENDULUM COG ---

# create pendulum cog
pend_cog = pendulum_cog(51, 10, 25, bit_size)
pend_cog['inner'] = inner_cuts(10, 40, 10, 3)
pend_cog['inner_cut'] = inner_cuts(10 + bit_size/2.0, 40- bit_size/2.0, 10+ bit_size/2.0, 3)

# # interactive plot
# def plot_func():
#     return plot_cog(pend_cog)
# interactive_plot(plot_func)

# # cut list
# rc = []
# rc.append({'type': 'circle', 'depth': 5,  'center': [0, 0], 'radius':  0})
# for inner_set in pend_cog['inner_cut']:
#     rc.append({'type': 'line', 'points': inner_set, 'depth': 6})    
# rc.append({'type': 'line', 'points': pend_cog['all_cut_points'], 'depth': 6})
# rc.append({'type': 'line', 'points': pend_cog['all_cut_points'], 'depth': 6})

# # preview, generate and save
# frame = gg.preview(rc, bit_size)
# gc = gg.cut_things(rc, 0)
# open('./gcode/pend.nc', 'w').write(gc)

# --- FORK ---

from cog_generation import get_tangent_point, rotate
from cog_generation import rad_to_deg
from cog_generation import *

import math
import numpy as np

def shift_point(start, end, dist):
    delta = end - start
    delta_dist = (delta ** 2).sum() ** 0.5
    return start + delta * (dist / delta_dist)


# def fork():
circle = 51
teeth_depth = 10
nr_teeth = 25
rotation_dy = 30
pendulum_swing_deg = 10
deg_up, deg_down = 6, 4
inner_up, inner_down = 6, 5

rotation_point = [0, circle + teeth_depth + rotation_dy]
pend_attach_point = [0, circle + teeth_depth + rotation_dy + 10]

right, left = get_tangent_point(rotation_point, circle + teeth_depth)
angle = rad_to_deg(math.atan(right[0]/right[1])) * 2
teeth_diff = int((angle - (360 / nr_teeth * 0.5)) / (360 / nr_teeth)) + 0.5
print(teeth_diff)

right_point = rotate([0, circle + teeth_depth], (360 / nr_teeth) * (teeth_diff / -2.0))
left_point = rotate([0, circle + teeth_depth], (360 / nr_teeth) * (teeth_diff / 2.0))
right_inner_point = shift_point(right_point, rotation_point, 5)
left_inner_point = shift_point(left_point, rotation_point, -5)

right_stop_range = np.arange(deg_up + 10, -deg_down - 1, -1)
right_stop_face = [list(rotate(right_point, d, rotation_point)) for d in right_stop_range]

right_inner_range = np.arange(-inner_down, inner_up + 1)
right_inner_face = [list(rotate(right_inner_point, d, rotation_point)) for d in right_inner_range]

left_stop_range = np.arange(-deg_down, deg_up + 1)
left_stop_face = [list(rotate(left_point, d, rotation_point)) for d in left_stop_range]

left_inner_range = np.arange(inner_up, -inner_down - 10 - 1, -1)
left_inner_face = [list(rotate(left_inner_point, d, rotation_point)) for d in left_inner_range]

top = rotation_point + np.array([0, 20])
top_right = rotate(top, -15)
top_left = rotate(top, 15)
bottom = rotation_point + np.array([0, -20])
bottom_right = rotate(bottom, -20)
bottom_left = rotate(bottom, 20)

full = [top_left, top, top_right]
full.extend(right_stop_face)
full.extend(right_inner_face)
full.extend([bottom_right, bottom, bottom_left])
full.extend(left_stop_face)
full.extend(left_inner_face)
full.append(top_left)

fork = {}
fork['full'] = full
fork['right_stop_face'] = right_stop_face
fork['right_inner_face'] = right_inner_face
fork['left_stop_face'] = left_stop_face
fork['left_inner_face'] = left_inner_face

def plot_func():
    frame = plot_cog(pend_cog)
    frame = plot_dict(frame, fork)
    return frame 
interactive_plot(plot_func)

tool_path = get_tool_path(fork['full'], bit_size / 2.0)

fork['cut_points'] = tool_path

def plot_func():
    frame = plot_cog(pend_cog)
    frame = plot_dict(frame, fork)
    return frame 
interactive_plot(plot_func)

fork['rotation_point'] = rotation_point
fork['pend_attach_point'] = pend_attach_point

fork['cut_points'], dxy = gg.position_points(fork['cut_points'])
fork['rotation_point'] = fork['rotation_point'] - np.array(dxy)
fork['pend_attach_point'] = fork['pend_attach_point'] - np.array(dxy)

# cut list
rc = []
rc.append({'type': 'circle', 'depth': 6,  'center': fork['rotation_point'], 'radius':  0})
rc.append({'type': 'circle', 'depth': 6,  'center': fork['pend_attach_point'], 'radius':  0})
rc.append({'type': 'line', 'points': fork['cut_points'], 'depth': 6})

# preview, generate and save
frame = gg.preview(rc, bit_size)
gc = gg.cut_things(rc, 0)
open('./gcode/fork.nc', 'w').write(gc)








assert False








# --- ORIGINAL ---

# # settings
# nr_teeth = 15
# pitch_circle = 50
# pressure_angle_deg = 20 # degree
# center = [0, 0]
# bit_size = gg.inch(0.25)

# --- EIGHT TEETH ---

# settings
nr_teeth = 8
pitch_circle = 25
pressure_angle_deg = 20 # degree
center = [0, 0]
bit_size = gg.inch(0.25)

# generate gear and tool path
cog = get_gear(pitch_circle, nr_teeth, pressure_angle_deg, bit_size)
cog = cog_tool_path(cog, bit_size)

# interactive plot
def plot_func():
    return plot_cog(cog)
interactive_plot(plot_func)

# create cut list
rc = []
rc.append({'type': 'circle', 'depth': 5,  'center': [0, 0], 'radius':  0})
rc.append({'type': 'line', 'points': cog['all_cut_points'], 'depth': 6})

# preview, generate, save
frame = gg.preview(rc, bit_size)
gc = gg.cut_things(rc, 0)
open('./gcode/gear_8.nc', 'w').write(gc)

# --- FORTY TEETH ---


# settings
nr_teeth = 8 * 5
pitch_circle = 25 * 5
pressure_angle_deg = 20 # degree
center = [0, 0]
bit_size = gg.inch(0.25)

# generate gear and tool path
cog = get_gear(pitch_circle, nr_teeth, pressure_angle_deg, bit_size)
cog = cog_tool_path(cog, bit_size)

# interactive plot
def plot_func():
    return plot_cog(cog)
interactive_plot(plot_func)

# create cut list
rc = []
rc.append({'type': 'circle', 'depth': 5,  'center': [0, 0], 'radius':  0})
rc.append({'type': 'line', 'points': cog['all_cut_points'], 'depth': 6})

# preview, generate, save
frame = gg.preview(rc, bit_size)
gc = gg.cut_things(rc, 0)
open('./gcode/gear_8.nc', 'w').write(gc)



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

