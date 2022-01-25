import json
import os

import cv2

import support.gcode_generator as gg
from support.geometry import dist, shift


class Clicker():
    """Intermediate class to capture clicks from events"""

    click_list = []

    def click_event(self, event, x, y, flags, params):

        if event == cv2.EVENT_LBUTTONDOWN:
            print(x, ' ', y)
            self.click_list.append(("L", x, y))
            cv2.circle(img, (x,y), radius=3, color=(0, 255, 0), thickness=3)
            cv2.imshow('image', img)

        if event == cv2.EVENT_RBUTTONDOWN:
            print(x, ' ', y)
            self.click_list.append(("R", x, y))
            cv2.circle(img, (x,y), radius=3, color=(0, 0, 255), thickness=3)

            # # Display the coordinate
            # font = cv2.FONT_HERSHEY_SIMPLEX
            # cv2.putText(img, str(x) + ',' + str(y), (x,y), font, 1, (255, 0, 0), 2)
            cv2.imshow('image', img)


def image_lines(path_image, scale):
    """Shows image and returns clicked points"""

    # Make global (for update within callback)
    global img

    assert os.path.exists(path_image)
    img = cv2.imread(path_image, 1)

    # Increase size
    size = [s * scale for s in img.shape[0:2]]
    img = cv2.resize(img, dsize=size)

    # Display the image
    cv2.imshow('image', img)

    # Setting mouse handler for the image
    clicker = Clicker()
    cv2.setMouseCallback('image', clicker.click_event)

    # Key to be pres to exit
    cv2.waitKey(0)

    # Close the window
    cv2.destroyAllWindows()

    return clicker.click_list


def separate_clicks(click_list):
    """Return list split by right clicks

    Potential for simplification
    """
    list_list = []

    current_list = []
    for s, x, y in click_list:
        print(s, x, y)
        if s == "R":
            if current_list != []:
                list_list.append(current_list)
            current_list = []
        else:
            current_list.append((x, y))

    if current_list != []:
        list_list.append(current_list)

    return list_list


def process_depth(point_list, square_ends=True):
    """Converts point pair to 3d points"""
    depth_list = []
    for s, e in zip(point_list[::2], point_list[1::2]):
        x = (s[0] + e[0]) / 2
        y = (s[1] + e[1]) / 2
        d = dist(s, e) / 2
        depth_list.append((x, y, d))

    if square_ends:
        depth_list = create_square_ends(depth_list, point_list)

    return depth_list


def create_square_ends(depth_list, point_list, do_other_end=True):
    """Add a square ends to lines"""
    last_point = depth_list[-1]
    second_point = depth_list[-2]
    width = dist(point_list[-1], point_list[-2]) / 2
    dist_between = dist(last_point[0:2], second_point[0:2])
    ratio = width / dist_between
    mid_point = [
        (second_point[0] - last_point[0]) * ratio + last_point[0],
        (second_point[1] - last_point[1]) * ratio + last_point[1],
        last_point[2],
    ]
    add_points = [mid_point, [*point_list[-2], 0], mid_point, [*point_list[-1], 0]]
    depth_list = [*depth_list[0:-1], *add_points]

    if do_other_end:
        depth_list = create_square_ends(depth_list[::-1], point_list[::-1], False)

    return depth_list


def get_current_size(depth_list):
    """Return x and y range used"""
    min_x, max_x, min_y, max_y = 10**5, 0, 10**5, 0
    for d_list in depth_list:
        for p in d_list:
            min_x = min(min_x, p[0] - p[2])
            max_x = max(max_x, p[0] + p[2])
            min_y = min(min_y, p[1] - p[2])
            max_y = max(max_y, p[1] + p[2])
    return min_x, max_x, min_y, max_y


def scale_list(depth_list, min_x, min_y, scale):
    """Returns scaled and shifted list

    Potential to use geometry support module
    """
    scaled_list = []
    for d_list in depth_list:
        s_list = []
        for p in d_list:
            s_list.append([
                (p[0] - min_x) * scale,
                (p[1] - min_y) * scale,
                p[2] * scale,
            ])
        scaled_list.append(s_list)
    return scaled_list


def click_letter(letter, load=True):
    """Shows image and processes and saves points"""

    img_scale = 4
    target_y = 30

    path_image = f"./font/{letter}.png"
    path_clicks = f"./font/{letter}_clicks.json"
    path_save = f"./font/{letter}.json"

    if load and os.path.exists(path_clicks):
        print("Loading previous clicks")
        click_list = json.load(open(path_clicks, 'r'))
    else:
        # Get list of clicks
        click_list = image_lines(path_image, img_scale)

    # Save original clicks
    json.dump({"clicks": click_list}, open(path_clicks, 'w'))

    # Flip
    click_list = [[p[0], -p[1], p[2]] for p in click_list]

    # Process
    separate_list = separate_clicks(click_list)

    # Convert to depth
    depth_list = [process_depth(l) for l in separate_list]

    # Scale
    min_x, max_x, min_y, max_y = get_current_size(depth_list)
    scale = target_y / (max_y - min_y)
    scaled_list = scale_list(depth_list, min_x, min_x, scale)

    # Save to file
    json.dump({"points": scaled_list}, open(path_save, 'w'))


if __name__=="__main__":

    letter = "C"

    # Click letter
    click_letter(letter)

    # Load json
    path_letter = f"./font/{letter}.json"
    scaled_list = json.load(open(path_letter, 'r'))["points"]

    # Convert to gcode
    x, y = 0, 0
    rc = []
    for s_list in scaled_list:
        rc.append({'type': 'line3', 'points': shift(s_list, [x, y, 0])})

    # Generatate gcode
    gc = gg.cut_things(rc, 0)
    print(gc)

    # Preview
    # TODO: ensure that preview uses x y consistent with machine
    def plot_func():
        return gg.preview_gcode(gc)
    gg.interactive_plot(plot_func)

    # Save to file
    open(f'./gcode/test_letters_{letter}.nc', 'w').write(gc)
