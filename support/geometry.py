import math
import numpy as np

def flip_x_and_y(points):
    return [[y, x] for x, y in points]


def round_points(points, digit=5):
    return [[np.round(x, digit), np.round(y, digit)] for x, y in points]


def deg_to_shift(deg, dist, start=None):
    if start is None:
        start = [0, 0]
    return [
        start[0] + np.cos(deg_to_rad(deg)) * dist,
        start[1] + np.sin(deg_to_rad(deg)) * dist,
    ]


def dist(start, end):
    return ((np.array(start) - np.array(end)) ** 2).sum()**0.5


def deg_to_rad(deg):
    return deg * math.pi / 180.0


def rad_to_deg(rad):
    return rad / math.pi * 180.0


def points_to_line(s, e):
  return [ee - ss for ss, ee in zip(s, e)]


def compute_deg_between_lines(s, e):
  rad = np.arccos(np.dot(s, e) / (np.linalg.norm(s)*np.linalg.norm(e)))
  return rad_to_deg(rad)


def rotate(point, deg, reference=np.array([0,0])):
    rad = deg_to_rad(deg)
    R = np.array([[math.cos(rad), -math.sin(rad)],
                  [math.sin(rad), math.cos(rad)]])
    return np.matmul(R, (np.array(point) - reference)) + reference


def rotate_list(point_list, deg, reference=np.array([0,0])):
   return [rotate(p, deg, reference) for p in point_list]


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


def shift_list(point_list, delta):
   return [shift(p, delta) for p in point_list]


def flatten_pair_list(pair_list):
  """Takes a list of point pairs and return a list of points"""
  flat_list = []
  for pair in pair_list:
    flat_list.extend(pair)
  return flat_list


def min_list(point_list):
  """Return the min values across a list of points"""
  return [min(e) for e in [list(x) for x in zip(*point_list)]]


def compute_surface_normal(p0, p1, p2):
  v01 = [p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]]
  v02 = [p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]]
  return [
      v01[1] * v02[2] - v01[2] * v02[1],
      v01[2] * v02[0] - v01[0] * v02[2],
      v01[0] * v02[1] - v01[1] * v02[0],
  ]


def load_file(filepath):
  """Helper function to read text."""
  with open(filepath) as f:
    content = f.readlines()
  return content