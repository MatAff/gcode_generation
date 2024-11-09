
import math
import numpy as np

def rad_to_deg(rad):
  return rad * 180 / math.pi

def deg_to_rad(deg):
  return deg * math.pi / 180

thickness = 300
half_thickness = thickness / 2
print(half_thickness)
angle = 137.8 # inside corner
alt_angle = 180 - angle
print(alt_angle)
angle_to_midpoint = alt_angle / 2
print(angle_to_midpoint)

teeth_up = np.tan(deg_to_rad(angle_to_midpoint)) * half_thickness
print(teeth_up)

diagonal_length = (half_thickness**2 + teeth_up**2)**0.5
print(diagonal_length)

back_angle = 90 - alt_angle - angle_to_midpoint
print(back_angle)

teeth_down = diagonal_length * np.cos(deg_to_rad(back_angle))
print(teeth_down)

def compute_teeth_up_down(angle, thickness):
    half_thickness = thickness / 2
    alt_angle = 180 - angle
    angle_to_midpoint = alt_angle / 2
    teeth_up = np.tan(deg_to_rad(angle_to_midpoint)) * half_thickness
    diagonal_length = (half_thickness**2 + teeth_up**2)**0.5
    back_angle = 90 - alt_angle - angle_to_midpoint
    teeth_down = diagonal_length * np.cos(deg_to_rad(back_angle))
    return {
       'teeth_up': teeth_up,
       'teeth_down': teeth_down,
    }

# Single test case.
angle = 137.8
thickness = 300
compute_teeth_up_down(angle, thickness)
compute_teeth_up_down(45, 300)

# Sharp angle is different.

angle = 35
thickness = 300
def compute_teeth_up_down(angle, thickness):
    if angle < 90.0:
        teeth_down = thickness / 2 / np.tan(deg_to_rad(angle / 2))
        teeth_up = np.tan(deg_to_rad(angle / 2)) * thickness / 2
    else:
        alt_angle = 180 - angle
        angle_to_midpoint = alt_angle / 2
        teeth_up = np.tan(deg_to_rad(angle_to_midpoint)) * thickness / 2
        diagonal_length = (half_thickness**2 + teeth_up**2)**0.5
        back_angle = 90 - alt_angle - angle_to_midpoint
        teeth_down = diagonal_length * np.cos(deg_to_rad(back_angle))
    return {
       'teeth_up': teeth_up,
       'teeth_down': teeth_down,
    }


# Loop through test cases.

test_cases = [
    {
      'angle': 150,
      'thickness': 300,
      'teeth_up': 40,
      'teeth_down': 110,
    },
    {
      'angle': 135,
      'thickness': 300,
      'teeth_up': 62,
      'teeth_down': 150,
    },
    {
      'angle': 35,
      'thickness': 300,
      'teeth_up': 47,
      'teeth_down': 476,
    },
]

for test_case in test_cases:
   teeth_up_down = compute_teeth_up_down(
      test_case['angle'],
      test_case['thickness'])
   print(teeth_up_down)
   print(test_case)
   assert np.round(teeth_up_down['teeth_up'] - test_case['teeth_up'], 0) == 0.0
   assert np.round(teeth_up_down['teeth_down'] - test_case['teeth_down'], 0) == 0.0
