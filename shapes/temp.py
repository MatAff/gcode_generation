

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

# Test and sample code
content = load_file(filepath)
vertices = get_vertices(content)
surfaces = get_surfaces(content)
surface = surfaces[0]
compute_length([0, 0, 0], [1, 1, 0])


parts = []

# Loop each surface
for surface, edges in shape['surfaces'].items():
  # print(surface, edges)

  # For each side
  for edge in edges:
    part = {
        'surface': surface,
        'edge': edge,
    }

    # Compute length
    edge_points = shape['edges'][edge]
    part['length'] = compute_length(shape['points'][edge_points[0]],
                                    shape['points'][edge_points[1]])

    # End angles
    base_line = points_to_line(shape['points'][edge_points[0]],
                               shape['points'][edge_points[1]])
    base_point = edge_points[0]
    other_edge = get_edge_containing_point(surface, base_point, edge)
    other_point = [p for p in edge if p != base_point][0]
    other_line = points_to_line(shape['points'][base_point],
                                shape['points'][other_point])
    # TODO: This should not be zero as currently.
    part['base_angle'] = compute_deg_between_lines(base_line, other_line)


    # Find touching surface
    touching_surface = get_surface_containing_edge(edge, surface)
    # print(f'Touching surface {touching_surface}')
    assert len(touching_surface) <= 1, "Too many touching surfaces."

    if touching_surface:

      # Compute angle with touching surface
      base_points = get_points_from_surface(surface)
      target_points = get_points_from_surface(touching_surface[0])
      # print(base_points)
      # print(target_points)
      part['angle'] = compute_deg_between_surface(base_points, target_points)

    # print('part')
    print(part)

    # Create marking

    # Add to parts








def get_surface_containing_edge(target_edge, exclude_surfaces=None):
  if not exclude_surfaces:
    exclude_surfaces = []
  surfaces = []
  for surface, edges in shape['surfaces'].items():
    if edge in edges:
      surfaces.append(surface)
  return [s for s in surfaces if s not in exclude_surfaces]


def get_edge_containing_point(surface, point, exclude_edges=None):
  if not exclude_edges:
    excluding_edges = []
  edges = []
  for edge in shape['surfaces'][surface]:
    if point in shape['edges'][edge]:
      edges.append(edge)
  return [e for e in edges if e not in exclude_edges]


def get_points_from_surface(surface):
  points = []
  edges = shape['surfaces'][surface]
  for edge in edges:

    for point in edge:
      if point not in points:
        points.append(point)
  return [shape['points'][p] for p in points]


def compute_surface_normal(p0, p1, p2):
  v01 = [p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]]
  v02 = [p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]]
  return [
      v01[1] * v02[2] - v01[2] * v02[1],
      v01[2] * v02[0] - v01[0] * v02[2],
      v01[0] * v02[1] - v01[1] * v02[0],
  ]




def compute_deg_between_lines(l0, l1):
  rad = np.arccos(np.dot(l0, l1) / (np.linalg.norm(l0)*np.linalg.norm(l1)))
  return rad_to_deg(rad)


def compute_deg_between_surface(base, target):
  base_normal = compute_surface_normal(base[0], base[1], base[2])
  target_normal = compute_surface_normal(target[0], target[1], target[2])
  return compute_deg_between_lines(base_normal, target_normal)


def compute_length(base, target):
  return (
      (base[0] - target[0])**2 +
      (base[1] - target[1])**2 +
      (base[2] - target[2])**2
  )**0.5


def points_to_line(base, target):
  return [
      base[0] - target[0],
      base[1] - target[1],
      base[2] - target[2],
  ]


# get_surface_containing_edge('AB')
get_edge_containing_point('ABC', 'A', 'AB')
# get_points_from_surface('ABC')
# compute_surface_normal((1, 0, 0), (0, 0, 1), (0, 1, 0))
# compute_deg_between_lines([0, 0, 1], [0, 1, 1])
# compute_length([1, 1, 1], [2, 2, 2])