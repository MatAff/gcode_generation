
# Want to use point bit and use depth to change width
# Could be used for text or turning imaging into cuts

# InkScape might have the option to do this
# Can get InkScape extension working though
# Only getting path to gcode working, which does not take into account the width of the bit

# Related: http://www.linuxcnc.org/docs/2.4/html/gui_image-to-gcode.html

# Write myself
# Given an area defined by a series of point
# For each point
#   Find the deepest cut you can make without
# For not ignore the fact that space in between might have to be filled in

import os
import cv2
import numpy as np


os.listdir('/home/ma/laser')

filepath = '/home/ma/laser/hao.svg'

# # Open as text file (turns out this is XML)
# with open(filepath) as f:
#     content = f.readlines()
# content


# ! python3 -m pip install svglib
from svglib.svglib import svg2rlg

drawing = svg2rlg(filepath)

contents = drawing.getContents()

element = contents[0]
a = element.getContents()[0]
b = a.getContents()[0]
c = b.getContents()[0]

points = c.points

points_2d = []
for i in range(0, len(points), 2):
    points_2d.append([points[i],points[i+1]])

frame = np.zeros((1000, 1000), np.uint8)

for p in points_2d:
    cv2.circle(frame, [int(e*10) for e in p], 1, (255, 0, 0), 1)

# display
cv2.imshow('image',frame)
cv2.waitKey(0)
cv2.destroyAllWindows()




# # ATTEMPT XML READ
# # ! python3 -m pip install lxml

# import xml.etree.ElementTree as ET

# tree = ET.parse(filepath)
# root = tree.getroot()

# root['svg']

# root[0].attrib

# root[2]

# list(tree.iterfind('path'))

# type(root)
# dir(root)
# root.text

# len(root)
# root[1].text

# root[0]

# layer = root[0].get('{http://www.inkscape.org/namespaces/inkscape}current-layer')

# type(layer)


# layer = root[0].attrib['{http://www.inkscape.org/namespaces/inkscape}current-layer']
# layer.title()
# layer.path()

# type(layer)
# dir(layer)
# print(layer)


# # printing the text contained within
# # first subtag of the 5th tag from
# # the parent
# print(root[5][0].text)