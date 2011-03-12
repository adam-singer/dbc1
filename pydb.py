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


def find_bounding(rects):
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

    min_area = sum([x*y for (x,y) in rects])
    bounding = find_bounding(rects)
    print bounding
    waste = 1 - (min_area / float(bounding))
    print "waste: %.4f" % (waste)
