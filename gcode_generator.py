
import cv2
from itertools import product
import math
import numpy as np

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
    return i * 25.4


def sets_sets(**kwargs):
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

    if kwargs['type'] == 'even_spaced':
        return even_spaced(**kwargs)
    elif kwargs['type'] == 'hole_sets':
        return hole_sets(**kwargs)
    elif kwargs['type']:
        return sets_sets(**kwargs)
    else:
        raise ValueError('invalid type, is not handled in create_elements function')


def preview(lines_list, bit_size, frame=None):

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
    return ((source[0] - target[0])**2 + (source[1] - target[1])**2)**0.5


def order_closest_point(list):
    
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


def lift_and_move(gc, point, track):
    gc += f"G1 Z{clear_height} F{plunge_feedrate} \n" # lift
    gc += f"G1 X{point[0]} Y{point[1]} F{rapid_feedrate} \n" # move
    track.track(*point)
    return gc


def get_sub_depths(depth, step):
    return [min ((i + 1) * step, depth)  for i in range(math.ceil(depth / step))]


def cut_things(cut_list, depth):

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
