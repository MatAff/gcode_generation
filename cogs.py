
import gcode_generator as gg

from cog_generation import (
    pendulum_cog, 
    inner_cuts, 
    plot_cog,
    interactive_plot,
    get_gear,
    cog_tool_path,
)

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

