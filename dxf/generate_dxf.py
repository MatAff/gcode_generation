import cv2
import ezdxf
import numpy as np

import drawsvg as svg


def point_list_to_point_pair_list(points):
    return [[start, end] for start, end in zip(points[:-1], points[1:])]

def shift_point_pair_list(point_pair_list, shift):
    shifted = []
    for start, end in point_pair_list:
        shifted.append([
            [start[0] + shift[0], start[1] + shift[1]],
            [end[0] + shift[0], end[1] + shift[1]],
        ])
    return shifted


def preview(point_pair_list):
    cv2.namedWindow('Sim')
    running = True
    delay = 50
    size = 1
    while running:
        frame = np.zeros((480, 640, 3), np.uint8)
        for start, end in point_pair_list:
            cv2.line(frame, [int(p * size + 10) for p in start],
                            [int(p * size + 10) for p in end], (0, 255, 0), 2)
        cv2.imshow('Sim', frame)
        key =  cv2.waitKey(delay)
        if key != -1:
            print(key)
        if key == 27:
            running = False
        if key == 61:
            size = size * 1.5
        if key == 45:
            size = size / 1.5
    cv2.destroyAllWindows()


def create_dxf(point_pair_list, filename):
    preview(point_pair_list)
    if filename[-4:] != '.dxf':
        raise ValueError('Filename should end in .dxf')
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    for start, end in point_pair_list:
        msp.add_line(start, end)
    doc.saveas(filename)

def create_svg(point_pair_list, filename):
    preview(point_pair_list)
    if filename[-4:] != '.svg':
        raise ValueError('Filename should end in .svg')
    d = svg.Drawing(1500, 2000, origin='top-left')
    for start, end in point_pair_list:
        start = [p * 10 + 5 for p in start]
        end = [p * 10 + 5 for p in end]
        d.append(svg.Lines(*start, *end, stroke='red'))
    d.set_pixel_scale(1)
    d.save_svg(filename)


if __name__ == '__main__':

    # Example this can be previewed in InkScape
    point_pair_list = [
        [[0, 0], [0, 100]],
        [[0, 100], [100, 100]],
        [[100, 100], [100, 0]],
        [[100, 0], [0, 0]],
    ]
    create_dxf(point_pair_list, 'test.dxf')