
"""Generate ribs for 3d objects

This code takes a filepath to an object file and produces a svg to cut ribs to 
create the shape

This previously used open3d which was only supports up to python3.10.

Install on Linux
! python3 -m pip install drawsvg
Install on Windows
! py -m pip install drawsvg
! py -m pip install trimesh

TODO: Have the rip teeth face each other to save space
TODO: Allow for missing panels in general
TODO: Don't add teeth if not facing another surface
TODO: Add padding such that corners are snug
TODO: Fix ends
TODO: Add part markings
"""

import sys; sys.path.append('..')

import drawsvg as svg
import numpy as np
# import open3d as o3d
import os
import trimesh
from collections import Counter

from support.geometry import (
    dist,
    deg_to_rad,
    points_to_line,
    compute_deg_between_lines,
    compute_surface_normal,
    shift_list,
    flatten_pair_list,
    rotate_list,
    min_list,
)

# Settings
filepath = './shapes/blender_cube.obj'
out_path = './svg/' + os.path.basename(filepath).replace('.obj', '.svg')
material_thickness = 3  # mm
width = 10  # Edge width in mm

def visualize(filepath):
  mesh = trimesh.load(filepath)
  return mesh.show()

def compute_edge_deg(s, e, faces, vertices):
  """Finds both faces on the edge and computes the angle between them"""
  normals = []
  for face in faces:
    if s in face and e in face:
      normals.append(compute_surface_normal(*[vertices[v] for v in face[0:3]]))
  assert len(normals) == 2
  return compute_deg_between_lines(
    normals[0], [normals[1][0] * -1, normals[1][1] * -1, normals[1][2] * -1,]
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

def create_part_spec(s, e, face, faces, vertices):
  previous_vertex = face[face.index(s) - 1]
  next_vertex = face[(face.index(e) + 1) % len(face)]
  edge_deg = compute_edge_deg(s, e, faces, vertices)
  teeth_up_down = compute_teeth_up_down(edge_deg, material_thickness)
  return {
    'face': '-'.join([str(v) for v in face]),
    'edge': f'{str(s)}-{str(e)}',
    'edge_common': f'{str(min(s, e))}-{str(max(s, e))}',
    'length': dist(vertices[s], vertices[e]),
    'start_angle': compute_deg_between_lines(
      points_to_line(vertices[previous_vertex], vertices[s]),
      points_to_line(vertices[e], vertices[s])),
    'end_angle': compute_deg_between_lines(
      points_to_line(vertices[e], vertices[s]),
      points_to_line(vertices[e], vertices[next_vertex])),
    'edge_deg': edge_deg,
    'teeth_up': teeth_up_down['teeth_up'],
    'teeth_down': teeth_up_down['teeth_down'],
  }

def create_parts(filepath):
  """Create part specs for all edges."""
  mesh = trimesh.load(filepath)
  vertices = mesh.vertices.tolist()
  faces = mesh.faces.tolist()
  part_specs = []
  for face in faces:
    for s, e in zip(face, [*face[1:], face[0]]):
      part_specs.append(create_part_spec(s, e, face, faces, vertices))
  return part_specs

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
  all_point_pair_list = []
  y = 0
  last_edge_common = ""
  for part in parts_list:
    
    point_pair_list = []

    # Core points
    start_point = [0, 0]
    end_point = [start_point[0] + part['length'], start_point[1]]
    start_back = [
      start_point[0] + width / np.tan(deg_to_rad(part['start_angle'] / 2)),
      start_point[1] + width
    ]
    end_back = [
      start_point[0] + part['length'] - width / np.tan(deg_to_rad(part['end_angle'] / 2)),
      start_point[1] + width
    ]

    # Left corner
    points = get_squiggle_points(start_point, part['start_angle'] / 2)
    for s, e in zip(points[0:-1], points[1:]):
      point_pair_list.append([s, e])

    # Bottom line
    point_pair_list.append([start_back, end_back])

    # Right corner
    points = get_squiggle_points(end_point, 180 - part['end_angle'] / 2)
    for s, e in zip(points[0:-1], points[1:]):
      point_pair_list.append([s, e])

    # Top line
    teeth_points = get_teeth_points([start_point[0], start_point[1] + part['teeth_down']], part)
    for s, e in zip(teeth_points[0:-1], teeth_points[1:]):
      point_pair_list.append([s, e])

    # Rotate if same edge
    if part['edge_common'] != last_edge_common:
      point_pair_list = rotate_list(point_pair_list, 180, [50, 0])
      mins = min_list(flatten_pair_list(point_pair_list))
      point_pair_list = shift_list(point_pair_list, [-1 * e for e in mins])
      # point_pair_list = shift_list(point_pair_list, [13, 0])

    # Shift
    point_pair_list = shift_list(point_pair_list, [0, y])

    # Add points
    all_point_pair_list.extend(point_pair_list)

    # Update start pos
    if part['edge_common'] == last_edge_common:
      y = y + width
    else:
      y = y + width + part['teeth_up'] - part['teeth_down']
    last_edge_common = part['edge_common']

  # Write to file
  create_svg(all_point_pair_list, out_path)

def merge_triangles(filepath):
  """Reassemble n-sided shapes

  Restricting to 4 sides for now"""
  
  # Load mesh
  mesh = trimesh.load(filepath)

  # Detect combos
  vertices = mesh.vertices.tolist()
  faces = mesh.faces.tolist()
  normals = mesh.face_normals
  combos = []
  for i in range(0, len(faces) - 1):
    for j in range(i, len(faces)):
      if len(set([*faces[i], *faces[j]])) == 4:  # Matching edge
        if compute_deg_between_lines(normals[i], normals[j]) < 0.001:
          combos.append([i, j])

  print(combos)
  
  # Early exit in case not combos were detected
  if len(combos)==0:
    print('No split faces detected, not merging faces')
    return

  # Merge faces
  # The logic is not straightforward here
  # Basically the new faces should not contain the shared edge
  # Therefor we loop through the numbers in the first face until we are on the second
  # of share vertices. We include that vertex and the next vertex (which is unshare)
  # and the vertix after, which is again a shared vertex, but because their are not 
  # in succession they do not represent the shared edge. 
  # All that is left to do after is include remaining non-shared vertex from the
  # other shape.
  print('Split faces were detected, will attempt to merge them')
  print('If you have faces with more than 4 four sides, you might be in trouble, sorry')
  merged_faces = []
  for combo in combos:
    fi = faces[combo[0]]
    fj = faces[combo[1]]
    f_numbers =[*fi, *fj]
    fii = [*fi, *fi]
    f_counts = Counter(f_numbers)
    f_shared = [k for k, v in f_counts.items() if v == 2]
    merged_face = []
    for i in range(len(fii)):
      if (fii[i] in f_shared) & (fii[i+1] in f_shared):
        merged_face.extend(fii[i+1: i+4])
        merged_face.extend([jv for jv in fj if jv not in fi])
        break
    merged_faces.append(merged_face)

  # Create a new mesh and overwrite file.
  # TODO: This is messed up but this actually resplits this into triangles
  # and it even appears to do it on load. 
  merged_mesh = trimesh.Trimesh(vertices, merged_faces)
  merged_mesh.export(filepath)

# Main

# Create part specs
parts_list = create_parts(filepath)

# Merge trianges
merge_triangles(filepath)

# Sort by length and edge identifiers
sorted_parts_list = sorted(parts_list, key=lambda p: (p['length'], p['edge_common']))

# Draw parts
draw_parts(sorted_parts_list, out_path)

# Visualize
visualize(filepath)



