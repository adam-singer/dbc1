""" Packing your dropbox
    or the Minimal Bounding Box Problem
"""

import random
import sys
from cygon import CygonRectanglePacker

EPSILON = 0.001

def max_rectangle(rects):

    height = max([ y for x,y in rects ]) 
    
def is_bounding(width,height,rects, Packer=CygonRectanglePacker):
    height = height + EPSILON
    width  = width + EPSILON
    
    packer = Packer(width,height)
    for x,y in rects:
        if not packer.TryPack(x,y):
            return False

    return True


def find_bounding():
    pass

def max_rectangle(rects,Packer=CygonRectanglePacker):
    height = max([ y for x,y in rects ]) 
    width = sum([x for x,y in rects])
    packer = Packer(width+EPSILON,height+EPSILON)
    point = None
    for (x,y) in rects:
        point = packer.TryPack(x,y)
        print "%d, %d" % (point.x,point.y)
    return (point.x,height)

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
    print "minimum area: %d" % (min_width*min_height)
    print rects

    if is_bounding(min_width,min_height,rects):
        print "bounding"
    else:
        print "not bounding"

    print "%d %d" % (max_rectangle(rects))
