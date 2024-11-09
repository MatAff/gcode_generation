
"""Generate ribs for 3d objects

This code takes a filepath to an object file and produces a svg to cut ribs to 
create the shape

The package open3d only supports up to python3.10, might use trimesh instead

Install on Linux
! python3 -m pip install open3d
! python3 -m pip install drawsvg
Install on Windows
! py -m pip install open3d
! py -m pip install drawsvg
! py -m pip install trimesh

TODO: Have the rip teeth face each other to save space
TODO: Allow for missing panels in general
TODO: Don't add teeth if not facing another surface
TODO: Add padding such that corners are snug
TODO: Fix ends
"""

import sys; sys.path.append('..')

import drawsvg as svg
import numpy as np
# import open3d as o3d
import os
import trimesh

from support.geometry import (
    dist, rad_to_deg, deg_to_rad, points_to_line, compute_deg_between_lines
)

# Settings
filepath = './shapes/tower.obj'
out_path = './svg/' + os.path.basename(filepath).replace('.obj', '.svg')
material_thickness = 3  # mm
width = 10  # Edge width in mm

# Load from file
# mesh = o3d.io.read_triangle_mesh(filepath)
mesh = trimesh.load(filepath)
# mesh.compute_vertex_normals()

# Visualize it
mesh.show()

# vis = o3d.visualization.Visualizer()
# vis.create_window()
# vis.add_geometry(mesh)
# vis.run()
# vis.destroy_window()

def load_file(filepath):
  """Helper function to read text."""
  with open(filepath) as f:
    content = f.readlines()
  return content

def get_vertices(content):
  """Custom function to get vertices."""
  vertices = [[]]  # Include one bogus points as surface index starts at 1.
  for line in content:
    if line.startswith('v'):
      try:
        print(line.strip().split(' '))
        point = [int(p) for p in line.strip().split(' ')[1:] if p != '']
        assert len(point) == 3, f'Could not parse: {line}'
        vertices.append(point)
      except Exception as e:
        print(line)
        raise e
  return vertices

def get_surfaces(content):
  """Custom function to get surfaces."""
  surfaces = []
  for line in content:
    if line.startswith('f'):
      try:
        points = [int(p) for p in line.strip().split(' ')[1:] if p != '']
        assert len(points) >=3, f'Did not find at least 3 points in: {line}'
        surfaces.append(points)
      except Exception as e:
        print(line)
        raise e
  return surfaces



def compute_surface_normal(p0, p1, p2):
  # TODO: Move to support
  v01 = [p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]]
  v02 = [p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]]
  return [
      v01[1] * v02[2] - v01[2] * v02[1],
      v01[2] * v02[0] - v01[0] * v02[2],
      v01[0] * v02[1] - v01[1] * v02[0],
  ]

def compute_deg_between_lines(l0, l1):
  # TODO: Move to support
  rad = np.arccos(np.dot(l0, l1) / (np.linalg.norm(l0)*np.linalg.norm(l1)))
  return rad_to_deg(rad)

def compute_edge_deg(s, e, surfaces, vertices):
  normals = []
  for surface in surfaces:
    if s in surface and e in surface:
      normals.append(compute_surface_normal(*[vertices[v] for v in surface[0:3]]))
  assert len(normals) == 2
  return compute_deg_between_lines(
    normals[0],
    [normals[1][0] * -1, normals[1][1] * -1, normals[1][2] * -1,]
  )

# def compute_teeth_depth(edge_deg):
#   return material_thickness / (180 - np.tan(deg_to_rad(edge_deg)))

def compute_teeth_up_down(angle, thickness):
    if angle < 90.0:
        teeth_down = thickness / 2 / np.tan(deg_to_rad(angle / 2))
        teeth_up = np.tan(deg_to_rad(angle / 2)) * thickness / 2
    else:
        alt_angle = 180 - angle
        angle_to_midpoint = alt_angle / 2
        teeth_up = np.tan(deg_to_rad(angle_to_midpoint)) * thickness / 2
        diagonal_length = (thickness / 2**2 + teeth_up**2)**0.5
        back_angle = 90 - alt_angle - angle_to_midpoint
        teeth_down = diagonal_length * np.cos(deg_to_rad(back_angle))
    return {
       'teeth_up': teeth_up,
       'teeth_down': teeth_down,
    }

def create_part(surface, surfaces, vertices):
  surface_parts = []
  for s, e in zip(surface, [*surface[1:], surface[0]]):
    part = {}
    part['surface'] = '-'.join([str(v) for v in surface])
    part['edge'] = f'{str(s)}-{str(e)}'
    print(s, e)
    part['length'] = dist(vertices[s], vertices[e])
    previous_vertex = surface[surface.index(s) - 1]
    part['start_angle'] = compute_deg_between_lines(
      points_to_line(vertices[previous_vertex], vertices[s]),
      points_to_line(vertices[e], vertices[s])
    )
    next_vertex = surface[(surface.index(e) + 1) % len(surface)]
    part['end_angle'] = compute_deg_between_lines(
      points_to_line(vertices[e], vertices[s]),
      points_to_line(vertices[e], vertices[next_vertex])
    )
    part['edge_deg'] = compute_edge_deg(s, e, surfaces, vertices)
    teeth_up_down = compute_teeth_up_down(part['edge_deg'], material_thickness)
    part['teeth_up'] = teeth_up_down['teeth_up']
    part['teeth_down'] = teeth_up_down['teeth_down']
    surface_parts.append(part)
  return surface_parts

def create_parts(filepath):
  content = load_file(filepath)
  vertices = get_vertices(content)
  surfaces = get_surfaces(content)
  print(surfaces)
  parts = []
  for surface in surfaces:
    parts.extend(create_part(surface, surfaces, vertices))
  return parts

def create_svg(point_pair_list, filename):
  if filename[-4:] != '.svg':
      raise ValueError('Filename should end in .svg')
  d = svg.Drawing(10000, 10000, origin='top-left')
  for start, end in point_pair_list:
      start = [p * 10 + 5 for p in start]
      end = [p * 10 + 5 for p in end]
      d.append(svg.Lines(*start, *end, stroke='red'))
  d.set_pixel_scale(1)
  d.save_svg(filename)

def get_squiggle_points(current, angle, lip_width = 1.5, lip_angle = 30.0):
  total_length = width / np.sin(deg_to_rad(angle))
  out_part_length_top = total_length * 0.5
  out_part_length_bottom = total_length * 0.2
  part_length = total_length * 0.15
  wedge_length = part_length + 2 * np.tan(deg_to_rad(lip_angle)) * lip_width
  wedge_side_length = lip_width / np.cos(deg_to_rad(lip_angle))

  sequence = [
    [0, out_part_length_top],
    [120, wedge_side_length],
    [0, wedge_length],
    [-120, wedge_side_length * 2],
    [0, wedge_length],
    [120, wedge_side_length],
    [0, out_part_length_bottom],
  ]

  points = [current]
  for add_angle, add_length in sequence:
    x = current[0] + np.cos(deg_to_rad(angle + add_angle)) * add_length
    y = current[1] + np.sin(deg_to_rad(angle + add_angle)) * add_length
    current = [x, y]
    points.append(current)

  return points

# part = parts_list[0]
def get_teeth_points(current, part, angle=0, target_teeth_width=20):
  teeth_count = int(round(part['length'] / target_teeth_width * 2, 0))
  teeth_width = part['length'] / teeth_count / 2

  sequence = [
    [0, teeth_width],  # Right
    [-90, part['teeth_down'] + part['teeth_up']],  # Up
    [0, teeth_width],  # Right
    [90, part['teeth_down'] + part['teeth_up']],  # down
  ]

  # current = [0, part['teeth_down'] * -1]
  points = [current]
  for i in range(teeth_count):
    for add_angle, add_length in sequence:
      x = current[0] + np.cos(deg_to_rad(angle + add_angle)) * add_length
      y = current[1] + np.sin(deg_to_rad(angle + add_angle)) * add_length
      current = [x, y]
      points.append(current)
  return points

def draw_parts(parts_list, out_path):
  point_pair_list = []

  for i, part in enumerate(parts_list):

    start_point = [0, i * (width + 2) + 2]

    # Core points
    end_point = [start_point[0] + part['length'], start_point[1]]
    start_angle = part['start_angle'] / 2
    start_back = [
      start_point[0] + width / np.tan(deg_to_rad(start_angle)),
      start_point[1] + width
    ]
    end_angle = part['end_angle'] / 2
    end_back = [
      start_point[0] + part['length'] - width / np.tan(deg_to_rad(end_angle)),
      start_point[1] + width
    ]

    points = get_squiggle_points(start_point, part['start_angle'] / 2)
    for s, e in zip(points[0:-1], points[1:]):
      point_pair_list.append([s, e])

    point_pair_list.append([start_back, end_back])

    points = get_squiggle_points(end_point, 180 - part['end_angle'] / 2)
    for s, e in zip(points[0:-1], points[1:]):
      point_pair_list.append([s, e])

    # point_pair_list.append([end_point, start_point])

    teeth_points = get_teeth_points([start_point[0], start_point[1] + part['teeth_down']], part)
    for s, e in zip(teeth_points[0:-1], teeth_points[1:]):
      point_pair_list.append([s, e])

    create_svg(point_pair_list, out_path)

# Create part definition
parts_list = create_parts(filepath)
# parts_list = parts_list[0:3]  # TODO: Remove
print(parts_list)

# Draw parts
draw_parts(parts_list, out_path)
