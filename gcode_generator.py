
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
drill_depth = 3.5
cut_depth = 1.5
clear_height = 5.0


def inch(i):
    return i * 25.4


def create_rectangle(width, height, offset_x_y=None):
    corners = product(np.array([0, 1]), np.array([0, 1]))
    corners = [c * np.array([width, height]) for c in corners]
    if offset_x_y:
        corners = corners + np.array(offset_x_y)
    return corners


def create_holes_sets(d):
    holes = []
    for x in range(d['nr_sets_x']):
        for y in range(d['nr_sets_y']):
            h = [
                d['offset_x'] + x * d['spacing_x'],
                d['offset_y'] + y * d['spacing_y'], 
            ]
            holes.append(h)
    return holes


def transpose(lines_list):
    return [[[p[1], p[0]] for p in line] for line in lines_list]


def holes_to_lines(hole_list):
    return [[list(h)] for h in hole_list]    


def preview(lines_list, bit_size):

    margin = 10

    position = [0, 0]

    def disp(l):
        return tuple([int(e) + margin for e in l])

    max_x, max_y = 0, 0
    for lines in lines_list:
        for point in lines:
            max_x, max_y = max(max_x, point[0]), max(max_y, point[1])

    # create display
    frame = np.zeros((int(max_y + (2 * margin)), int(max_x + (2 * margin)), 3), np.uint8)	

    # draw origin
    cv2.line(frame,(0, 10), (20, 10), (255, 0, 0), 1)
    cv2.line(frame,(10, 0), (10, 20), (255, 0, 0), 1)

    # loop through lines
    for line in lines_list:

        # loop through points
        for ind, point in enumerate(line):

            # draw travel
            cv2.line(frame, disp(position), disp(point), (255, 255, 0), 1)
            position = point

            print(point)
            # draw point
            cv2.circle(frame, disp(point), int(bit_size / 2), (0, 0, 255), 1)

            # draw line
            if ind != 0:
                cv2.line(frame, disp(last_point), disp(point), (0, 255, 0), 1)

            last_point = point
    # display
    cv2.imshow('image',frame)
    cv2.waitKey(0)    
    cv2.destroyAllWindows()  


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


class Track(object):

    def __init__(self):
        self.distance = 0
        self.x = 0
        self.y = 0

    def track(self, x, y):
        self.distance += ((self.x - x)**2 + (self.y - y)**2) ** 0.5
        self.x = x
        self.y = y


def cut_things(cut_list, depth):

    gc = FILE_START

    # checks
    assert depth > 0, "depth should be given as a positive number"

    # track position and distance
    track = Track()

    # loop and cut or drill
    for cut in cut_list:

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
