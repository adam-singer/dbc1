""" Packing your dropbox
    or the Minimal Bounding Box Problem
"""

import random
import sys
from cygon import CygonRectanglePacker as Packer

EPSILON = 0.001

def is_bounding(width,height,rects):
    packer = Packer(width+EPSILON,height+EPSILON)
    for x,y in rects:
        if packer.TryPack(x,y) is None and packer.TryPack(y,x) is None:
            return False
    # if you reach here, all rectangles fit
    return True


def find_bounding(min_area,max_area,rects):
    min_dimension = max([ y for x,y in rects ]) 
    for area in range(min_area,max_area+1):
        print "area %d" % (area)
        x,y = min_dimension,(area/min_dimension)
        for w in xrange(x,y):
            h = area / w
            print "%.2f" % (h)
            if is_bounding(w,h,rects):
                return (w,h)
    return (max_area/min_dimension,min_dimension)
    

def max_rectangle(rects):
    H = max([ y for x,y in rects ]) 
    L = sum([x for x,y in rects])
    W = L
    for w in xrange(L,1,-1):
        if not is_bounding(w,H,rects):
            return W * H
        else:
            W = w
            

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
    coord(float(min_area/min_height),float(min_height),"min rectangle:")
    max_area = max_rectangle(rects)
    coord(float(max_area/min_height),min_height,"max rectangle:")
    width,height = find_bounding(min_area,max_area,rects)
    coord(width,height,"solution:")
    waste = 1 - (min_area / float(width * height))
    print "waste: %.4f" % (waste)
