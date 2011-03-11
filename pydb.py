""" Packing your dropbox
    or the Minimal Bounding Box Problem
"""

import random
import sys
from cygon import CygonRectanglePacker as Packer

EPSILON = 0.001

def is_bounding(width,height,rects):
    height = height + EPSILON
    width  = width + EPSILON
    packer = Packer(width,height)
    for x,y in rects:
        if not packer.TryPack(x,y) and not packer.TryPack(y,x):
            coord(width,height,"rejected:")
            return False
            
    return True


def find_bounding(min_area,max_area,rects):
    min_dimension = max([ y for x,y in rects ]) 
    for area in xrange(min_area,max_area+1):
        x,y = min_dimension,(area/min_dimension)
        if x > y:
            x,y = y,x
        for w in xrange(x,y):
            h = area / w
            if is_bounding(w,h,rects) or is_bounding(h,w,rects):
                return (w,h)
    return (max_area/min_dimension,min_dimension)
    

def max_rectangle(rects):
    H = max([ y for x,y in rects ]) 
    L = sum([x for x,y in rects])
    for w in xrange(L,1,-1):
        coord(w,H,"rough cut:")
        packer = Packer(w+EPSILON,H+EPSILON)
        for (x,y) in rects:
            point = packer.TryPack(x,y) or packer.TryPack(y,x)
            if point is None:
                return w * H
            coord(point.x,point.y,"co-ord:")

    return L * H
            

def coord(w,h,comment="rectangle:"):
    print "%s %.2f %2.f" % (comment,w,h)


if __name__ == "__main__":

    rects = []
    lines = sys.stdin.readlines()
    for line in lines[1:]:
        x,y = line.split()
        x,y = int(x),int(y)
        if x > y:
            x,y = y,x
        rects.append((x,y))

    min_area   = sum([x*y for (x,y) in rects])
    min_height = max([y for x,y in rects])
    coord(float(min_area/min_height),min_height,"min rectangle:")
    max_area = max_rectangle(rects)
    coord(float(max_area/min_height),min_height,"max rectangle:")
    width,height = find_bounding(min_area,max_area,rects)
    coord(width,height,"solution:")
    waste = 1 - (min_area / float(width * height))
    print "waste: %.4f" % (waste)
