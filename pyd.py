""" Packing your dropbox
    or the Minimal Bounding Box Problem
"""

import random
import sys
from cygon import CygonRectanglePacker
from itertools import chain

def flatten(listOfLists):
    "Flatten one level of nesting"
    return chain.from_iterable(listOfLists)


if __name__ == "__main__":

    rects = []
    lines = sys.stdin.readlines()
    for line in lines[1:]:
        x,y = line.split()
        x,y = int(x),int(y)
        if y > x:
            x,y = y,x
        rects.append((x,y))

    min_area            = sum([x*y for (x,y) in rects])
    largest_dimension   = max([ x for x,y in rects ])
    other_dimension     = min_area / largest_dimension

    packer = CygonRectanglePacker(largest_dimension,other_dimension)
    fits = True
    for x,y in rects:
        point = packer.tryFindBestPlacement(x,y)
        if point is None:
            fits = False
            break
        else:
            print "%d %d" % (point.x, point.y)

    if fits:
        print "%d" % (min_area)
    else:
        print "rectangles do not fit in minimum area"
