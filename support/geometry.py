import math
import numpy as np


def dist(start, end):
    return ((np.array(start) - np.array(end)) ** 2).sum()**0.5


def deg_to_rad(deg):
    return deg * math.pi / 180.0


def rad_to_deg(rad):
    return rad / math.pi * 180.0


def rotate(point, deg, reference=np.array([0,0])):
    rad = deg_to_rad(deg)
    R = np.array([[math.cos(rad), -math.sin(rad)],
                  [math.sin(rad), math.cos(rad)]])
    return np.matmul(R, (np.array(point) - reference)) + reference


def ellipse_points(height, width):

    # Get initial set of points
    points = []
    for deg in range(0, 90, 1):
        rad = deg_to_rad(deg)
        ratio = math.tan(rad) # y / x
        xp = ((height**2 * width**2) / (height**2 + ratio**2 * width**2))**0.5
        y  = ((1 - xp**2 / width**2) * height**2)**0.5
        assert np.round(xp**2 / width**2 + y**2 / height**2, 3) == 1
        points.append([xp, y, deg])
    points.append([0, height, 90])
    print(points)

    # Flips
    for p in points[-2::-1]:
        points.append([-p[0], p[1], p[2]])
    for p in points[-2:0:-1]:
        points.append([p[0], -p[1], p[2]])

    return points


def scale_min_max(x, in_range, out_range):
    n = (x - in_range[0])/(in_range[1] - in_range[0])
    return n * (out_range[1] - out_range[0]) + out_range[0]


def shift(point_list, delta):
    return [[pp + dd for pp, dd in zip(p, delta)] for p in point_list]
