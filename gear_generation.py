
import math
import numpy as np

import cv2

# plot constants
FRAME_SIZE = [750,750]
PLOT_ORIGIN = [-100, 200] # (np.array(FRAME_SIZE) / -2 / SCALE).astype(int) 
SCALE = 3



def deg_to_rad(deg):
    return deg * math.pi / 180.0


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


def rotate(point, deg):
    rad = deg_to_rad(deg)
    R = np.array([[math.cos(rad), -math.sin(rad)],
                  [math.sin(rad), math.cos(rad)]])
    return np.matmul(R, np.array(point))


def point_to_plot(point):
    # return (PLOT_ORIGIN - (np.array(point)) * SCALE).astype(int)
    return (np.array([-PLOT_ORIGIN[0] + point[0], PLOT_ORIGIN[1] - point[1]]) * SCALE).astype(int)


def scale_r(r):
    return r * SCALE


def dist(start, end):
    return ((np.array(start) - np.array(end)) ** 2).sum()**0.5


def abc(a, b, c):
    d = (b**2 - 4*a*c)**0.5
    return (-b+d) / (2*a), (-b-d) / (2*a)


def get_tangent_point(point, r):
    a = (point[1]**2 + point[0]**2)
    b = -2 * r**2 * point[0]
    c = r**4 - point[1]**2 * r**2 
    x1, x2 = abc(a, b, c)
    y1 = (r**2 - point[0] * x1) / point[1]
    y2 = (r**2 - point[0] * x2) / point[1]
    return [x1, y1], [x2, y2]


def get_perpendicual_point(point, dist):
    rad = math.atan(point[1]/point[0])
    x = dist * -math.sin(rad) + point[0]
    y = dist * math.cos(rad) + point[1]
    return [x, y]


# settings
nr_teeth = 20
pitch_circle = 150
pressure_angle_deg = 20 # degree
center = [0, 0]
red = (0, 0, 255)
blue = (255, 0, 0)
green = (0, 255, 0)

# def get_gear(pitch_circle, nr_teeth, pressure_angle):

module = get_module(pitch_circle, nr_teeth)
addendum = get_addendum_circle(pitch_circle, module)
dedendum = get_dedendum_circle(pitch_circle, module)
base_circle = get_base_circle(pitch_circle, pressure_angle_deg)

# create frame and draw origin
frame = np.zeros([*FRAME_SIZE, 3], np.uint8)	
cv2.circle(frame, point_to_plot(center), 5, red, 1)

# draw circles
cv2.circle(frame, point_to_plot(center), int(scale_r(pitch_circle)), red, 1)
cv2.circle(frame, point_to_plot(center), int(scale_r(addendum)), blue, 1)
cv2.circle(frame, point_to_plot(center), int(scale_r(dedendum)), blue, 1)
cv2.circle(frame, point_to_plot(center), int(scale_r(base_circle)), red, 1)

# get pitch point
first_rotate = 360 / nr_teeth * 0.25 # this should be -0.25 
pitch_point = rotate([0, pitch_circle], first_rotate)
print(pitch_point)
cv2.circle(frame, point_to_plot(pitch_point), 1, green, 3)

# get base point
base_point = get_tangent_point(pitch_point, base_circle)[0]
print(base_point)
pitch_base_dist = dist(pitch_point, base_point)
cv2.circle(frame, point_to_plot(base_point), 1, green, 3)

# roll points
points = []
for d in range(-25, 25):
    alt_base = rotate(base_point, d)
    alt_dist = pitch_base_dist - d/180 * base_circle * math.pi
    alt_point = get_perpendicual_point(alt_base, alt_dist)
    points.append(alt_point)

# add reverse points
for p in points[::-1]:
    points.append([p[0] * -1, p[1]])

# repeat
teeth_points = []
for r in range(nr_teeth):
    print(r)
    rotate_deg = 360 / nr_teeth * r
    for p in points:
        teeth_points.append(rotate(p, rotate_deg))

# teeth_points = points

# display teeth
for s, e in zip(teeth_points[0:-1], teeth_points[1:]):
    cv2.line(frame, point_to_plot(s), point_to_plot(e), green)    

cv2.imshow('image',frame)
cv2.waitKey(0)    
cv2.destroyAllWindows()  


# --- TEST FUNCTIONS ---


def test_dist():
    start = [0, 0]
    end = [3, 4]
    exp = 5
    assert dist(start, end) == exp


def test_get_tangent_point():
    point = [5, 3]
    r = 2
    [x1, y1], [x2, y2] = get_tangent_point(point, r)

    assert all(np.array([x1, y1]).round(3) == np.array([1.5548045132, -1.2580075220]).round(3)), [x1, y1]
    assert all(np.array([x2, y2]).round(3) == np.array([-0.3783339250, 1.9638898750]).round(3)), [x2, y2]

# test_get_tangent_point()

#cv2.line(frame, [0,0], [100, 100], (255, 255, 0), 1)
# cv2.line(frame, disp(position), disp(point), (255, 255, 0), 1)
# cv2.circle(frame, disp(point), int(bit_size / 2) * factor, (0, 0, 255), 1)

# steps
# define dedendum circle as a list of line segments by number of teeth
# define addendum circle as a list of line segments by number of teeth
# define straight line between point on the pitch circle and dedeundum circle
# calculate the intersect between the addenbum and involute
# iteteratively cut calculate mid point on involute line, till required precision is reached
# mirror involute
# multiply and rotate

# def scale_point(point, FRAME_SIZE, scale=2):
#     center = (np.array(FRAME_SIZE) / 2).astype(int)
#     return center - (np.array(point) * 2).astype(int)


