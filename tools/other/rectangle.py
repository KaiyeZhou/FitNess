#!/usr/bin/env python
# coding=utf-8

import numpy as np
import cv2
import PIL.Image as Image

H = 305
W = 480
x1 = int(W / 3)
y1 = 1
x2 = int(W * 2 / 3)
y2 = H - 1
#create a black use numpy,size is:512*512
img = np.zeros((H,W,3), np.uint8)
#fill the image with white
img.fill(255)

cv2.rectangle(img, (x1,y1), (x2, y2), (255,0,0), 3)
font = cv2.FONT_HERSHEY_SIMPLEX

cv2.imwrite('round1.png',img)
img = Image.open('round1.png')
img = img.convert('RGBA')

color_0 = img.getpixel((0, 0))
for h in range(H):
    for l in range(W):
        dot = (l,h)
        color_1 = img.getpixel(dot)
        if color_1 == color_0:
            color_1 = color_1[:-1] + (0,)
            img.putpixel(dot,color_1)
img.save('round1.png')
print "hello"