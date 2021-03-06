

def swap_x_y(d):
    d = {k.replace('_x', '_temp').replace('_y', '_x').replace('_temp', '_y'): v for k, v in d.items()}
    d = {k.replace('width', 'temp').replace('height', 'width').replace('temp', 'height'): v for k, v in d.items()}
    return d


# bearing block
vert_bearing = {
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
    "offset_x": (42 - 32) / 2.0,
    "offset_y": 14 / 2.0
}

# pillow block
pillow_block = {
    "width": 55,
    "length": 13,
    "hole_spacing_x": 42,
    "hole_height": 15,
    "offset_x": (55 - 42) / 2.0,
    "offset_y": 13 / 2.0
}

# vertical bearing block
horz_bearing = swap_x_y(vert_bearing)

# servo
nema17 = {
    'outer': 42, 
    'hole_spacing': 31,
    'offset': (42 - 31) / 2.0,
    'big_circle': 22,
}

sbr16uu_vert = {
    "width": 45,
    "height": 45,
    "hole_spacing_x": 32,
    "hole_spacing_y": 30,
    "offset_x": (45 - 32) / 2.0,
    "offset_y": (45 - 30) / 2.0,
    "hole_height": 20,
}

sbr16uu_horz = swap_x_y(sbr16uu_vert)

sbr_rail = {
    "width": 40,
    "height": 25,
}