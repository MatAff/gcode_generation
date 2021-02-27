
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
drill_depth = 3.2
cut_depth = 1.0
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



def reorder(l):

    # TODO: solve traverling sales person problem here
    
    return l


def cut_things(cut_list, depth):

    gc = FILE_START

    # checks
    assert depth > 0, "depth should be given as a positive number"

    # reorder
    cut_list = reorder(cut_lsit)

    # loop and cut or drill
    for cut in cut_list:

        # lift
        gc += f"G1 Z{clear_height} F{plunge_feedrate} \n"

        # move to point
        gc += f"G1 X{cut[0][0]} Y{cut[0][1]} F{rapid_feedrate} \n"

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

                    # on first point plunge
                    if ind == 0: 
                        sub_depth = min ((i + 1) * cut_depth, depth)
                        gc += f"G1 Z-{sub_depth} F{plunge_feedrate} \n"

                # lift
                gc += f"G1 Z{clear_height} F{plunge_feedrate} \n"

    # return to start
    gc += f"G1 Z{clear_height} F{plunge_feedrate} \n"
    gc += f"G0 X0.0 Y0.0 F{rapid_feedrate} \n"

    # end file
    gc += FILE_END

    return gc
