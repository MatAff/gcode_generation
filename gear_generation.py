
import math
import numpy as np

import cv2

# settings
nr_teeth = 20
pitch_circle = 150
pressure_angle_deg = 20 # degree


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


def scale_point(point, frame_size, scale=2):
    center = (np.array(frame_size) / 2).astype(int)
    return center - (np.array(point) * 2).astype(int)


def scale_r(r, scale=2):
    return r * scale


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


# def get_gear(pitch_circle, nr_teeth, pressure_angle):

frame_size = [750,750]

module = get_module(pitch_circle, nr_teeth)
addendum = get_addendum_circle(pitch_circle, module)
dedendum = get_dedendum_circle(pitch_circle, module)
base_circle = get_base_circle(pitch_circle, pressure_angle_deg)

# create frame and draw origin
frame = np.zeros(frame_size, np.uint8)	
center = list((np.array(frame_size) / 2).astype(int))
cv2.circle(frame, center, 5, (255, 255, 0), 1)

# draw circles
cv2.circle(frame, center, int(scale_r(pitch_circle)), (255, 255, 0), 1)
cv2.circle(frame, center, int(scale_r(addendum)), (255, 255, 0), 1)
cv2.circle(frame, center, int(scale_r(dedendum)), (255, 255, 0), 1)
cv2.circle(frame, center, int(scale_r(base_circle)), (255, 255, 0), 1)

# get first  point
first_rotate = 360 / nr_teeth * 0
base_point = rotate([0, base_circle], first_rotate)
print(base_point)
cv2.circle(frame, scale_point(base_point, frame_size), 1, (255, 255, 255), 1)

for d in range(35):
    alt_base = rotate(base_point, d)
    print(alt_base)
    print(d/360 * base_circle * math.pi)
    alt_point = get_perpendicual_point(alt_base, d/180 * base_circle * math.pi)
    print(alt_point)
    cv2.circle(frame, scale_point(alt_point, frame_size), 4, (d * 10, d * 10, d * 10), 1)

cv2.imshow('image',frame)
cv2.waitKey(0)    
cv2.destroyAllWindows()  




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