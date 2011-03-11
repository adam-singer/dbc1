import random
import sys

def rectanglesN(N=100):
    print N
    for i in range(N):
        w = random.randrange(1,N)
        h = random.randrange(1,N)
        print "%d %d" % (w,h)


if __name__ == "__main__":
    rectanglesN(int(sys.argv[1].strip()))
