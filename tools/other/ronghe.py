#!/usr/bin/env python
# coding=utf-8

import cv2 as cv, numpy as np

# Load two images
img1 = cv.imread('/home/ww/桌面/tools_test/pic/AIFIT-diban.jpg')  # 背景
rectangle = cv.imread('/home/ww/桌面/tools_test/rectangle.png')  # logo

# I want to put logo on top-left corner, So I create a ROI
rows, cols, channels = rectangle.shape
roi = img1[0:rows, 0:cols]

# Now create a mask of logo and create its inverse mask also
img2gray = cv.cvtColor(rectangle, cv.COLOR_BGR2GRAY)
ret, mask = cv.threshold(img2gray, 254, 255, cv.THRESH_BINARY)  # 这个254很重要
mask_inv = cv.bitwise_not(mask)

# cv.imshow('mask',mask_inv)
# Now black-out the area of logo in ROI
img1_bg = cv.bitwise_and(roi, roi, mask=mask)  # 这里是mask,我参考的博文写反了,我改正了,费了不小劲

# Take only region of logo from logo image.
img2_fg = cv.bitwise_and(rectangle, rectangle, mask=mask_inv)  # 这里才是mask_inv

# Put logo in ROI and modify the main image
dst = cv.add(img1_bg, img2_fg)
img1[0:rows, 0:cols] = dst

cv.imshow('res', img1)
cv.waitKey(0)
cv.destroyAllWindows()
