import support.gcode_generator as gg
from support.geometry import ellipse_points, scale_min_max, shift

# settings
bit_size = gg.inch(0.25)
depth = 2
depth_range = (0.5, depth)


def shift_rc(rc, x, y):
    for element in rc:
        print(element)
        if element["type"] == 'line':
            element["points"] = shift(element["points"], [x, y])
        elif element["type"] == 'line3':
            element["points"] = shift(element["points"], [x, y, 0])
        else:
            raise ValueError("Unsupported line type")


def test_shift_rc():

    rc = [{"type": "line", "points": [[0, 0]]}]
    x, y = 10, 20
    expected = [{"type": "line", "points": [[10, 20]]}]
    shift_rc(rc, x, y)

    assert rc == expected


# --- a ---

def letter_a(x, y):
    lower = ellipse_points(10, 10)
    lower = [[p[0], p[1], scale_min_max(p[2], (0, 90), depth_range)] for p in lower]

    upper = ellipse_points(10, 10)
    upper = [[p[0], p[1], scale_min_max(p[2], (0, 90), depth_range)] for p in upper]
    upper = [p for p in upper if p[1] > 0]
    upper = shift(upper, [0, 20, 0])

    rc = []
    rc.append({'type': 'line3', 'points': shift(lower, [x, y, 0])})
    rc.append({'type': 'line3', 'points': shift(upper, [x, y, 0])})
    rc.append({'type': 'line', 'points': shift([[10, -10 + depth], [10, 20 - depth]], [x, y]), "depth": depth})
    rc.append({'type': 'line3', 'points': shift(gg.get_fonty_points([10, -10], 0, depth), [x, y, 0])})
    return rc


# --- b ---

def letter_b(x=0, y=0):

    lower = ellipse_points(10, 10)
    lower = [[p[0], p[1], scale_min_max(p[2], (0, 90), depth_range)] for p in lower]

    rc = []
    rc.append({'type': 'line3', 'points': lower})
    rc.append({'type': 'line', 'points': [[-10, -10 + depth], [-10, 30 - depth]], "depth": depth})
    rc.append({'type': 'line3', 'points': gg.get_fonty_points([-10, -10], 0, depth)})
    rc.append({'type': 'line3', 'points': gg.get_fonty_points([-10, 30], 180, depth)})

    if x != 0 or y != 0:
        shift_rc(rc, x, y)

    return rc


# --- preview ---

rc = []
rc.extend(letter_a(0, 0))
rc.extend(letter_b(30, 0))
rc.extend(letter_a(60, 0))

# preview, generate, save
gc = gg.cut_things(rc, 0)

def plot_func():
    return gg.preview_gcode(gc)
gg.interactive_plot(plot_func)

open('./gcode/test_text_letters_aba.nc', 'w').write(gc)



if __name__ == "__main__":

    test_shift_rc()



# --- LETTER I ---

# create cut list
depth = 2
rc = []
rc.append({'type': 'line3', 'points': gg.get_fonty_points([0, 0], 0, depth)})
rc.append({'type': 'line', 'points': [[0, depth], [0, 20 - depth]], "depth": depth})
rc.append({'type': 'line3', 'points': gg.get_fonty_points([0, 20], 180, depth)})
# rc.append({'type': 'fonty', 'position': [0, 0], "deg": 0, "depth": depth})
# rc.append({'type': 'line', 'points': [[0, depth], [0, 20 - depth]], "depth": depth})
# rc.append({'type': 'fonty', 'position': [0, 20], "deg": 180, "depth": depth})

# preview, generate, save
frame = gg.preview(rc, bit_size)
gc = gg.cut_things(rc, 0)
print(gc)
open('./gcode/test_text.nc', 'w').write(gc)

# --- LETTER O ---

# def letter_o():
points = ellipse_points(20, 10)
depth_range = (0.5, 2)
points = [[p[0], p[1], scale_min_max(p[2], (0, 90), depth_range)] for p in points]

rc = []
rc.append({'type': 'line3', 'points': points})


open('./gcode/test_text_letter_o.nc', 'w').write(gc)



# --- c ---








letters = {
    "a": [
        {'type': 'fonty', 'position': [0, 0], "deg": 0, "depth": 3}, # left botton fonty
        {'type': 'fonty', 'position': [letter_width, 0], "deg": 0, "depth": 3}, # right bottom fonty
        {'type': 'fonty', 'position': [letter_width, letter_height], "deg": 0, "depth": 3}, # top fonty
        {'type': 'line', 'points': [[0, 3], [letter_width / 2, letter_height - 3]], "depth": 3}, # left leg
        {'type': 'line', 'points': [[letter_width, 3], [letter_width / 2, letter_height - 3]], "depth": 3}, # right leg
        {'type': 'line', 'points': [[letter_width * 1/6, letter_height  * 1/3], [letter_width * 5/6, letter_height * 1/3]], "depth": 2}, # middle bar
    ],
    "t": [
        {'type': 'fonty', 'position': [0, 0], "deg": 90, "depth": 3},
        {'type': 'line', 'points': [[letter_width / 2, 3], [letter_width / 2, letter_height - 3]], "depth": 3},
        {'type': 'fonty', 'position': [letter_width, 20], "deg": -90, "depth": 3},
        {'type': 'fonty', 'position': [letter_width, 0], "deg": 0, "depth": 3},
        {'type': 'line', 'points': [[0 + 3, letter_height], [letter_width + 3, letter_height]], "depth": 3},
    ],
    "i": [
        {'type': 'fonty', 'position': [letter_width / 2, 0], "deg": 0, "depth": 3}, # bottom fonty
        {'type': 'line', 'points': [[letter_width / 2, 3], [letter_width / 2, letter_height - 3]], "depth": 3}, # middle line
        {'type': 'fonty', 'position': [letter_width / 2, 20], "deg": 180, "depth": 3}, # top fonty
    ]
}

