""" Packing your dropbox
    or the Minimal Bounding Box Problem
"""

import random
import sys
from cygon import CygonRectanglePacker


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
    print "minimum area: %d" % (min_area)
    print rects
    min_height = max([ x for x,y in rects ]) 
    min_width  = min_area / min_height
    min_height = min_height + 0.1
    min_width = min_width + 0.1
    print "width: %d, height: %d" % (min_width,min_height)

    packer = CygonRectanglePacker(min_width,min_height)
    for x,y in rects:
        print "rectangle %d %d" % (x, y)
        point = packer.TryPack(x,y)
        if point is None:
            point = packer.TryPack(y,x)
            if point is None:
                print "Did not fit ...",
                print "%d %d" % (x, y)
            else:
                print "Fit ... ",
                print "%d %d" % (point.x, point.y)
        else:
            print "Fit ... ",
            print "%d %d" % (point.x, point.y)
