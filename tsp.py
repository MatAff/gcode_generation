
import numpy as np

from gcode_generator import Track
from gcode_generator import holes_to_lines

def calc_dist(source, target):
    return ((source[0] - target[0])**2 + (source[1] - target[1])**2)**0.5

def order_closest_point(list):
    
    position = [0, 0]
    olist = []

    for i in range(len(list)):
        dist_list = [calc_dist(position, l[0]) for l in list]
        minpos = dist_list.index(min(dist_list)) 
        closest_line = list.pop(minpos)
        olist.append(closest_line)
        position = closest_line[0]
    
    return olist

# generate random list
list = np.round(np.random.randn(50, 2), 2)
list = list * 100 + 100
list = list.tolist()
list = holes_to_lines(list)
original_list = list.copy()
# print(list)

# order
olist = order_closest_point(list.copy())
# print(olist)

# ordered distance
track = Track()
for p in olist:
    track.track(p[0][0], p[0][1])
print(track.distance)

# unordered distance
track = Track()
for p in list:
    track.track(p[0][0], p[0][1])
print(track.distance)

# --- inline version ---

# order
position = [0, 0]
olist = []

for i in range(len(list)):
    dist_list = [calc_dist(position, l[0]) for l in list]
    minpos = dist_list.index(min(dist_list)) 
    closest_line = list.pop(minpos)
    olist.append(closest_line)

    # track
    track.track(closest_line[0][0], closest_line[0][1])
    position = closest_line[0]

# ordered distance
track = Track()
for p in olist:
    track.track(p[0][0], p[0][1])
print(track.distance)
