

def swap_x_y(d):
    d = {k.replace('_x', '_temp').replace('_y', '_x').replace('_temp', '_y'): v for k, v in d.items()}
    d = {k.replace('width', 'temp').replace('height', 'width').replace('temp', 'height'): v for k, v in d.items()}
    return d


# bearing block
bearing_block = {
    "width": 34,
    "height": 30,
    "hole_spacing_x": 24,
    "hole_spacing_y": 18,
    "offset_x": (34 - 24) / 2.0,
    "offset_y": (30 - 18) / 2.0,
    "hole_height": 11
}

# shaft support
shaft_support = {
    "width": 42,
    "length": 14,
    "hole_spacing_x": 32,
    "hole_height": 20,
    "offset_x": (42 + 32) / 2.0,
    "offset_y": 14 / 2.0
}

# pillow block
pillow_block = {
    "width": 55,
    "length": 13,
    "hole_spacing_x": 42,
    "hole_height": 15,
    "offset_x": (55 + 42) / 2.0,
    "offset_y": 13 / 2.0
}

# vertical bearing block
vert_bearing = swap_x_y(bearing_block)