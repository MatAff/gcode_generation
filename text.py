import support.gcode_generator as gg
from support.geometry import ellipse_points, scale_min_max

# settings
bit_size = gg.inch(0.25)

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

# preview, generate, save
# frame = gg.preview(rc, bit_size)
gc = gg.cut_things(rc, 0)
print(gc)

# interactive plot
def plot_func():
    return gg.preview_gcode(gc)
gg.interactive_plot(plot_func)





open('./gcode/test_text_letter_o.nc', 'w').write(gc)



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

