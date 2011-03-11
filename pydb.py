""" Packing your dropbox
    or the Minimal Bounding Box Problem
"""

import random
import sys
from cygon import CygonRectanglePacker

EPSILON = 1
Packer = CygonRectanglePacker

def is_bounding(width,height,rects):
    height = height + EPSILON
    width  = width + EPSILON
    packer = Packer(width,height)
    for x,y in rects:
        if not packer.TryPack(x,y):
            return False
    return True


def find_bounding(min_width,min_height,max_width,max_height,rects):
    for w in xrange(min_width,max_width+1):
        for h in xrange(min_height,max_height+1):
            if is_bounding(w,h,rects):
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
        else:
            print "%d %d" % (x,y)
            print "%d %d" % (length,height)
            
    return (width,height)

def min_rectangle(rects):
    area   = sum([x*y for (x,y) in rects])
    height = max([ y for x,y in rects ]) 
    width  = area / height
    return (width, height)
    
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
    (max_width,max_height) = max_rectangle(rects)
    width,height = find_bounding(min_width,min_height,max_width,max_height,rects)
    print "solution: %d %d" % (width,height)
