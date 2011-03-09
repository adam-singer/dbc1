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
        rects.append([int(x), int(y)])

    min_area = sum([x*y for (x,y) in rects])
    largest_dimension = max(flatten(rects))
    other_dimension = min_area / largest_dimension

    packer = CygonRectanglePacker(largest_dimension,other_dimension)
    fits = True
    for r in rects:
        point = packer.tryFindBestPlacement(r[0],r[1])
        if point is None:
            fits = False
            break

    if fits:
        print "%d" % (min_area)
    else:
        print "rectangles do not fit in minimum area"
