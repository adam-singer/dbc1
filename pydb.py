""" Packing your dropbox
    or the Minimal Bounding Box Problem
"""

import random
import sys
from cygon import CygonRectanglePacker

EPSILON = 0.001
Packer = CygonRectanglePacker

def is_bounding(width,height,rects):
    height = height + EPSILON
    width  = width + EPSILON
    packer = Packer(width,height)
    for x,y in rects:
        if not packer.TryPack(x,y):
            return False
    return True


def find_bounding(min_area,max_area,rects):
    min_dimension = max([ y for x,y in rects ]) 
    for area in range(min_area,max_area+1):
        x,y = min_dimension,(area/min_dimension)
        if y > x:
            x,y = y,x
        for w in xrange(x,y):
            h = area / w
            if is_bounding(w,h,rects):
                return (w,h)
    return (max_area/min_dimension,min_dimension)
    

def max_rectangle(rects):
    height = max([ y for x,y in rects ]) 
    length = sum([x for x,y in rects])
    packer = Packer(length+EPSILON,height+EPSILON)
    width  = 0
    for (x,y) in rects:
        point = packer.TryPack(x,y)
        if point.x + x >= width:
            width = point.x + x
            
    return width * height


def min_rectangle(rects):
    area = sum([x*y for (x,y) in rects])
    return area
    

def coord(w,h,comment=""):
    print "%s %d %d" % (comment,w,h)

if __name__ == "__main__":

    rects = []
    lines = sys.stdin.readlines()
    for line in lines[1:]:
        x,y = line.split()
        x,y = int(x),int(y)
        if x > y:
            x,y = y,x
        rects.append((x,y))

    min_area = min_rectangle(rects)
    max_area = max_rectangle(rects)
    width,height = find_bounding(min_area,max_area,rects)
    coord(width,height,"solution:")
    waste = 1 - (min_area / float(width * height))
    print "waste: %.4f" % (waste)
