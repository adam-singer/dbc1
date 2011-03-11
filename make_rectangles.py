import random

def rectanglesN(N=100):
    widths  = range(0,N)
    heights = range(0,N)
    
    random.shuffle(widths)
    random.shuffle(heights)
    print N
    for i in range(N):
        print "%d %d" % (widths[i],heights[i])


if __name__ == "__main__":
    rectanglesN(20)
