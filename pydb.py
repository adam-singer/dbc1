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
            if not packer.TryPack(y,x):
                return False
    return True


def find_bounding(min_width,min_height,max_width,max_height,rects):
    for w in xrange(min_width,max_width+1):
        for h in xrange(min_height,max_height+1):
            if is_bounding(w,h,rects):
                print "found solution"
                return (w,h)
    return (max_width,max_height)
    

def max_rectangle(rects):
    height = max([ y for x,y in rects ]) 
    length = sum([x for x,y in rects])
    packer = Packer(length+EPSILON,height+EPSILON)
    width  = 0
    for (x,y) in rects:
        point = packer.TryPack(x,y)
        if point:
            if point.x >= width:
                width = point.x
            
    return (width,height)

def min_rectangle(rects):
    area   = sum([x*y for (x,y) in rects])
    height = max([ y for x,y in rects ]) 
    width  = area / height
    return (width, height)
    

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

    (min_width,min_height) = min_rectangle(rects)
    coord(min_width,min_height,"min rectangle:")
    (max_width,max_height) = max_rectangle(rects)
    coord(max_width,max_height,"max rectangle:")
    width,height = find_bounding(min_width,min_height,max_width,max_height,rects)
    coord(width,height,"solution:")
    waste = 1 - ((min_width * min_height) / float(width * height))
    print "waste: %.4f" % (waste)
