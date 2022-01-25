import sys; sys.path.append("..")

import cv2
import math
import numpy as np

from support.cog_generation import rotate
from support.geometry import dist

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

RED = (0, 0, 255)
BLUE = (255, 0, 0)
GREEN = (0, 255, 0)

# G21 - Millimeters
# G90 - Absolute distance mode
# G91 - Incremental distance mode
# M30 - Stop program

FILE_START = """
G21
G90
"""

FILE_END = "M30"

plunge_feedrate = 250
rapid_feedrate = 8000
cut_feedrate = 900
drill_depth = 3.3
cut_depth = 2.2
clear_height = 5.0


def inch(i):
    """Returns size in mm"""
    return i * 25.4


def sets_sets(**kwargs):
    """Return sets of points"""
    ox = kwargs.get('outer_offset_x', 0.0)
    oy = kwargs.get('outer_offset_y', 0.0)
    sx = kwargs.get('outer_spacing_x', 0.0)
    sy = kwargs.get('outer_spacing_y', 0.0)

    outer_elements = []
    for xx in range(kwargs.get('nr_outer_sets_x', 2)):
        for yy in range(kwargs.get('nr_outer_sets_y', 2)):
            elements = hole_sets(**kwargs)
            dx = ox + (sx * xx)
            dy = oy + (sy * yy)
            elements = [[[e[0] + dx, e[1] + dy] for e in se] for se in elements]
            outer_elements.extend(elements)
    return outer_elements


def hole_sets(**kwargs):
    """Returns hole sets"""
    elements = []
    for x in range(kwargs.get('nr_sets_x', 2)):
        for y in range(kwargs.get('nr_sets_y', 2)):
            e = [
                kwargs.get('offset_x', 0) + x * kwargs.get('spacing_x', 0.0),
                kwargs.get('offset_y', 0) + y * kwargs.get('spacing_y', 0.0),
            ]

            # handle slots
            f = [
                e[0] + kwargs.get('slot_x', 0.0),
                e[1] + kwargs.get('slot_y', 0.0)
            ]

            if e == f:
                elements.append([e])
            else:
                elements.append([e, f])
    return elements


def even_spaced(**kwargs):
    """Return evenly spaced points"""
    elements = []
    for i in range(kwargs.get('start', 0), kwargs['nr']):
        dx = (kwargs['x_end'] - kwargs['x_start']) / (kwargs['nr'] - 1)
        dy = (kwargs['y_end'] - kwargs['y_start']) / (kwargs['nr'] - 1)
        e = [
            kwargs['x_start'] + (i * dx),
            kwargs['y_start'] + (i * dy),
        ]
        elements.append([e])
    return elements


def create_elements(**kwargs):
    """Master function to create different point configurations"""
    if kwargs['type'] == 'even_spaced':
        return even_spaced(**kwargs)
    elif kwargs['type'] == 'hole_sets':
        return hole_sets(**kwargs)
    elif kwargs['type']:
        return sets_sets(**kwargs)
    else:
        raise ValueError('invalid type, is not handled in create_elements function')


def preview(lines_list, bit_size, frame=None):
    """Legacy preview function

    Current methods involved generating preview from gcode"""

    margin = 10
    position = [0, 0]
    factor = 2

    def disp(l):
        return tuple([int(e) * factor + margin for e in l])

    def draw_lines(line, position, bit_size=bit_size):

        print(line)

        # loop through points
        for ind, point in enumerate(line):

            print(ind)

            # draw travel
            cv2.line(frame, disp(position), disp(point), (255, 255, 0), 1)
            position = point

            # draw point
            cv2.circle(frame, disp(point), int(bit_size / 2) * factor, (0, 0, 255), 1)

            # draw line
            if ind != 0:
                cv2.line(frame, disp(last_point), disp(point), (0, 255, 0), 1)

            last_point = point

        return point

    max_x, max_y = 300, 300 # default
    for lines in lines_list:
        if not isinstance(lines, dict):
            for point in lines:
                max_x, max_y = max(max_x, point[0]), max(max_y, point[1])

    # create display
    if frame is None:
        frame = np.zeros((int((max_y * factor) + (2 * margin)), int((max_x *factor) + (2 * margin)), 3), np.uint8)

    # draw origin
    cv2.line(frame,(0, 10), (20, 10), (255, 0, 0), 1)
    cv2.line(frame,(10, 0), (10, 20), (255, 0, 0), 1)

    # loop through lines
    for line in lines_list:

        if isinstance(line, dict):

            if line['type'] == 'drill':
                points = [[p] for p in line['points']]
                for p in points:
                    position = draw_lines(p, position)
            if line['type'] == 'line':
                print(line['points'])
                position = draw_lines(line['points'], position)
            if line['type'] == 'circle':
                position = draw_lines([line['center']], position, line['radius'] * 2)

        else:

            position = draw_lines(line, position)

    # display
    cv2.imshow('image',frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return frame


def calc_dist(source, target):
    """Returns distance based on first two values in points"""
    return ((source[0] - target[0])**2 + (source[1] - target[1])**2)**0.5


def order_closest_point(list):
    """Returns optimized point order"""

    position = [0, 0]
    olist = []

    for i in range(len(list)):
        dist_list = [calc_dist(position, l[0]) for l in list]
        minpos = dist_list.index(min(dist_list))
        closest_line = list.pop(minpos)
        olist.append(closest_line)
        position = closest_line[0]

    return olist


def position_points(points, where='zero'):
    """Returns positioned points"""
    min_x = min([p[0] for p in points])
    max_x = max([p[0] for p in points])
    min_y = min([p[1] for p in points])
    max_y = max([p[1] for p in points])

    print(f'x: {min_x} - {max_x}, y: {min_y}, {max_y}')
    print(f'size: {max_x - min_x}, {max_y - min_y}')

    if where == 'zero':
        dx, dy = min_x, min_y
    if where == 'center':
        dx, dy = (max_x - min_x) / 2.0, (max_y - min_y) / 2.0

    return [[p[0] - dx, p[1] - dy] for p in points], [dx, dy]


class Track(object):
    """Class to track mill travel distance"""

    def __init__(self):
        self.distance = 0
        self.x = 0
        self.y = 0

    def track(self, x, y):
        self.distance += ((self.x - x)**2 + (self.y - y)**2) ** 0.5
        self.x = x
        self.y = y

    def track_circle(self, r):
        self.distance += 2 * 3.14159 * r


def get_fonty_points(position, deg, depth):
    """Create serif on text"""
    width = 4 * depth
    points = [
        [*list(position + rotate(np.array([-width / 2, 0]), deg).round(4)), 0],
        [*list(position + rotate(np.array([0, depth]), deg).round(4)), depth],
        [*list(position + rotate(np.array([width / 2, 0]), deg).round(4)), 0],
    ]
    return points


def get_sub_depths(depth, step):
    """Returns a list of depths to cut at"""
    return [min ((i + 1) * step, depth)  for i in range(math.ceil(depth / step))]


def lift_and_move(gc, point, track):
    """Returns gcode to move to a new location"""
    gc += f"G1 Z{clear_height} F{plunge_feedrate} \n" # lift
    gc += f"G1 X{point[0]} Y{point[1]} F{rapid_feedrate} \n" # move
    track.track(*point)
    return gc


def cut_things(cut_list, depth):
    """Return gcode from cut list"""

    gc = FILE_START

    # checks
    assert depth >= 0, "depth should be given as a positive number"

    # track position and distance
    track = Track()

    # loop and cut or drill
    for cut in cut_list:

        if isinstance(cut, dict):

            if cut['type'] == 'raw':

                gc += '\n'.join(cut['content']) + '\n'

            elif cut['type'] == 'drill':

                for point in cut['points']:

                    gc = lift_and_move(gc, point, track)

                    sub_depths = get_sub_depths(cut['depth'], drill_depth)
                    for sub_depth in sub_depths:
                        gc += f"G1 Z-{sub_depth} F{plunge_feedrate} \n" # drill
                        gc += f"G1 Z1.0 F{plunge_feedrate} \n" # pull back

                    gc += f"G1 Z{clear_height} F{plunge_feedrate} \n"

            elif cut['type'] == 'line':

                gc = lift_and_move(gc, cut['points'][0], track)

                sub_depths = get_sub_depths(cut['depth'], cut_depth)
                for sub_depth in sub_depths:
                    for ind, point in enumerate(cut['points']):

                        # move to point
                        gc += f"G1 X{point[0]} Y{point[1]} F{cut_feedrate} \n"
                        track.track(point[0], point[1])

                        # on first point plunge
                        if ind == 0 : gc += f"G1 Z-{sub_depth} F{plunge_feedrate} \n"

                    # lift
                    gc += f"G1 Z{clear_height} F{plunge_feedrate} \n"

            elif cut['type'] == 'line3':

                gc = lift_and_move(gc, cut['points'][0][0:2], track)

                for ind, point in enumerate(cut['points']):

                    # move to point
                    gc += f"G1 X{point[0]} Y{point[1]} Z-{point[2]} F{cut_feedrate} \n"
                    track.track(point[0], point[1])

                # lift
                gc += f"G1 Z{clear_height} F{plunge_feedrate} \n"

            elif cut['type'] == 'circle':

                start_point = [cut['center'][0], cut['center'][1] - cut['radius']]
                gc = lift_and_move(gc, start_point, track)
                gc += f"G1 X{start_point[0]} Y{start_point[1]} Z0 F{cut_feedrate} \n"

                sub_depths = get_sub_depths(cut['depth'], drill_depth)
                for sub_depth in sub_depths:
                    gc += f"G2 X{start_point[0]} Y{start_point[1]} J{cut['radius']} Z-{sub_depth} F{plunge_feedrate} \n"
                    track.track_circle(cut['radius'])

                # lift
                gc += f"G1 Z{clear_height} F{plunge_feedrate} \n"

            elif cut["type"] == "fonty":
                # TODO: remove this condition, use line3 instead

                fonty_points = get_fonty_points(cut["position"], cut["deg"], cut["depth"])
                gc = lift_and_move(gc, fonty_points[0][0:2], track)
                for fp in fonty_points:
                    gc += f"G1 X{fp[0]} Y{fp[1]} Z-{fp[2]} F{cut_feedrate} \n"
                    track.track(fp[0], fp[1])

            else:

                raise ValueError(f"unknown cut type {cut['type']}")

        else:

            # --- ORIGINAL LIST BASED APPROACH ---

            # lift
            gc += f"G1 Z{clear_height} F{plunge_feedrate} \n"

            # move to point
            gc += f"G1 X{cut[0][0]} Y{cut[0][1]} F{rapid_feedrate} \n"
            track.track(cut[0][0], cut[0][1])

            if len(cut) == 1:

                # DRILL

                # cut - divide depth in incremental steps
                nr_cycles = math.ceil(depth / drill_depth)
                for i in range(nr_cycles):

                    # drill
                    sub_depth = min ((i + 1) * drill_depth, depth)
                    gc += f"G1 Z-{sub_depth} F{plunge_feedrate} \n"

                    # pull back
                    gc += f"G1 Z1.0 F{plunge_feedrate} \n"

                gc += f"G1 Z{clear_height} F{plunge_feedrate} \n"

            else:

                # cut - divide depth in incremental steps
                nr_cycles = math.ceil(depth / cut_depth)
                for i in range(nr_cycles):

                    for ind, point in enumerate(cut):

                        # move to point
                        gc += f"G1 X{point[0]} Y{point[1]} F{cut_feedrate} \n"
                        track.track(point[0], point[1])

                        # on first point plunge
                        if ind == 0:
                            sub_depth = min ((i + 1) * cut_depth, depth)
                            gc += f"G1 Z-{sub_depth} F{plunge_feedrate} \n"

                    # lift
                    gc += f"G1 Z{clear_height} F{plunge_feedrate} \n"

    # return to start
    gc += f"G1 Z{clear_height} F{plunge_feedrate} \n"
    gc += f"G0 X0.0 Y0.0 F{rapid_feedrate} \n"
    track.track(0, 0)

    # distance
    print(f'distance travelled: {track.distance}')

    # end file
    gc += FILE_END

    return gc


# --- GCODE PREVIEW ---

def point_to_plot(point):
    """Returns location in frame"""
    return (np.array([-PLOT_ORIGIN[0] + point[0], PLOT_ORIGIN[1] - point[1]]) * SCALE).astype(int)


def scale_r(r):
    """Scales size to frame"""
    return r * SCALE


def interactive_plot(plot_func):
    """Displays interactive plot based on plot function"""

    global PLOT_ORIGIN
    global SCALE

    running = True
    while running:

        frame = plot_func()
        cv2.imshow('image', frame)
        key = cv2.waitKey(0)
        # print(key)

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


def parse_g1(g1):
    """Returns coordinates from g1 line

    Tested
    """
    point_dict = {}
    for part in g1.split(" "):
        for coordinate in ("X", "Y", "Z"):
            if part.startswith(coordinate):
                point_dict[coordinate] = float(part.replace(coordinate, ""))
    return point_dict


def preview_gcode(gc):
    """Returns frame with gcode preview

    Tested
    """

    center = [0, 0]
    position = center
    z = 0

    # create frame and draw origin
    frame = np.zeros([*FRAME_SIZE, 3], np.uint8)
    cv2.circle(frame, point_to_plot(center), 5, RED, 1)

    for line in gc.split("\n"):
        if line.startswith("G1"):
            point_dict = parse_g1(line)
            xx = point_dict.get("X", position[0])
            yy = point_dict.get("Y", position[1])
            zz = point_dict.get("Z", z)

            z = zz
            new_position = [xx, yy]
            if position != new_position:
                color = BLUE if z > 0 else RED
                if z <= 0:
                    # cv2.circle(frame, point_to_plot(position), int(scale_r(abs(z))), color, 1)
                    preview_line(
                        frame,
                        [*point_to_plot(position), depth],
                        [*point_to_plot(new_position), z],
                    )
                cv2.line(frame, point_to_plot(position), point_to_plot(new_position), color)
            position = new_position
            depth = z

    return frame

def preview_line(frame, start, end):
    """Plots line using circle to indicate depth"""
    length = dist(start, end)
    for i in range(int(length)):
        x = int((end[0] - start[0]) * i / length + start[0])
        y = int((end[1] - start[1]) * i / length + start[1])
        z = int((end[2] - start[2]) * i / length + start[2])
        cv2.circle(frame, (x, y), int(scale_r(-z)), RED, 1)


# --- TESTS ---


def test_preview_gcode():

    gc = """
    G21
    G90
    G1 Z5.0 F250
    G1 X10.0 Y0.0 F8000
    G1 X10.0 Y0.0 Z-0.5 F900
    G1 X9.999619172640966 Y0.17454400191598118 Z-0.5166666666666667 F900
    G1 X9.998476023269195 Y0.3491544764772416 Z-0.5333333333333333 F900
    G1 X9.99656854787627 Y0.5238979580449435 Z-0.55 F900
    """

    frame = preview_gcode(gc)

    assert isinstance(frame, np.ndarray)


def test_parse_g1():
    point_dict = parse_g1("G1 X10.0 Y0.0 Z-0.5 F900")
    assert point_dict == {"X": 10.0, "Y": 0.0, "Z": -0.5}



def test_get_sub_depths():
    expected = [3, 6, 9, 10]
    res = get_sub_depths(10, 3)
    assert res == expected



def test_get_fonty_points():

    points = get_fonty_points([0, 0], 0, 2)
    assert points == [[-4.0, 0.0, 0], [0.0, 2.0, 2], [4.0, 0.0, 0]]

if __name__ == "__main__":
    test_parse_g1()
    test_preview_gcode()
    test_get_fonty_points()

