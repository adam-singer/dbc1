import copy
import random
import sys
import time
import logging
import math
log = logging.getLogger("Br")
logging.basicConfig(level=logging.INFO)

TL="TL"
TR="TR"
BL="BL"
BR="BR"

class R:
  corners = [TL, TR, BR, BL]

  def __init__(self, width, height):
    self.height = height
    self.width = width

    self.vert_map = {}
    self.rect_map = {}
    self.rotated = False
    self.anchor_point = None
    self.__colors = None

    self.__cluster = None
    self.__cluster_leader = None

  def __repr__(self):
    return "%sx%s#%s" % (self.width, self.height, self.anchor_point)

  # {{{ Corner Helpers & Calculations
  def corner_to_offset(self, c):
    ap = [0,0]
    if c[0] == "T":
      pass
    elif c[0] == "B":
      ap[1] = self.height
    else:
      raise Exception("Invalid Corner: %s" % (c))

    if c[1] == "L":
      pass
    elif c[1] == "R":
      ap[0] = self.width
    else:
      raise Exception("Invalid Corner: %s" % (c))

    return ap

  def corner_to_point(self, c):
    p = self.corner_to_offset
    return (p[0] + self.anchor_point[0], p[0] + self.anchor_point[0])

  def calculate_anchor_for_edge(self, c1, rect, c2):
    p1 = self.corner_to_offset(c1)
    p2 = rect.corner_to_offset(c2)
    traverse_point = [0,0]
    ap = self.anchor_point
    traverse_point[0] = ap[0] + p1[0] - p2[0]
    traverse_point[1] = ap[1] + p1[1] - p2[1]
    return traverse_point

  def calculate_anchor_for_rect(self, rect):
    # First figure out their connection points
    return self.calculate_anchor_for_edge(self.rect_map[rect], rect, rect.rect_map[self])

  # }}} Corner & Calculation Functions

  # {{{ Spatial Anchoring
  def anchor_to(self, point):
    point = tuple(point)
    log.debug( "Anchoring %s from %s to %s" % (self, self.anchor_point, point))
    if point == self.anchor_point:
      return

    if self.anchor_point and point != self.anchor_point:
      raise Exception("Already anchored! No pirating")

    self.anchor_point = point
    log.debug( "Coords are now: (%s, %s), (%s, %s)" % (self.x0, self.y0, self.x1, self.y1))
    for r in self.rect_map:
      r.anchor_to(self.calculate_anchor_for_rect(r))

  def unanchor(self, recurse=False):
    log.debug( "Pulling Anchor on %s" % self)
    if self.anchor_point:
      self.anchor_point = None

    if recurse:
      for r in self.rect_map:
        if r.anchor_point:
          r.unanchor(recurse)

  # Rotate this rectangle by swapping height and width
  def rotate(self):
    self.rotated = not self.rotated
    w,h = self.width, self.height
    self.width,self.height = h,w

  def rotate_corner(self, corner, amount=1):
    index = R.corners.index(corner)
    index += amount
    index %= len(R.corners)
    return R.corners[index]

  # Pivot this rectangle by moving each corner over by one and rotating the
  # rectangle. This Attempts to keep the attachment point during a rotation.
  # (It still requires the other connectec rectangle to pivot, too)
  def pivot(self):
    new_vert_map = {}
    new_rect_map = {}
    for corner in self.vert_map:
      new_corner = self.rotate_corner(corner, 1)
      new_vert_map[corner] = self.vert_map[corner]
      new_rect_map[self.vert_map[corner]] = new_corner

    self.vert_map = new_vert_map
    self.rect_map = new_rect_map
    self.rotate()


  # }}} Spatial Anchoring

  # {{{ Properties
  @property
  def name(self):
    return "%s,%s" % (self.width, self.height)

  @property
  def is_placed(self):
    return not not self.anchor_point

  @property
  def x0(self):
    return self.anchor_point[0]

  @property
  def y0(self):
    return self.anchor_point[1]

  @property
  def x1(self):
    return self.x0 + self.width

  @property
  def y1(self):
    return self.y0 + self.height

  @property
  def area(self):
    return self.height * self.width

  @property
  def neighbors(self):
    return self.rect_map.keys()

  @property
  def colors(self):
    if not self.__colors:
        r = random.random()
        g = random.random()
        b = random.random()
        self.__colors = (r,g,b,0.2)

    return self.__colors

  @property
  def cluster(self):
    return self.__cluster

  @property
  def cluster_leader(self):
    return self.__cluster_leader

  @property
  def is_cluster(self):
    return self.__cluster and len(self.__cluster) > 0
  # }}} Properties

  # Attach Functions {{{
  def attach_to(self, my_corner, rect, rect_corner):
    self.vert_map[my_corner] = rect
    self.rect_map[rect] = my_corner

  def attach(self, my_corner, rect, rect_corner):
    log.debug( "Attaching %s's %s corner to %s's %s corner" % (self, my_corner, rect, rect_corner))
    # Check if the attachment is valid.

    # For attachments, you don't want to have intersections (two rectangles go
    # into each other) or no overlap of edges
    if (my_corner[0] != rect_corner[0] and my_corner[1] != rect_corner[1]):
      raise Exception("Corner mismatch! Trying to connect %s to %s" % (my_corner, rect_corner))

    if (my_corner == rect_corner):
      raise Exception("Can't assign a connection in the same corner: %s" % my_corner)

    self.attach_to(my_corner, rect, rect_corner)
    rect.attach_to(rect_corner, self, my_corner)

    if self.anchor_point:
      rect.anchor_to(self.calculate_anchor_for_rect(rect))
    elif rect.anchor_point:
      self.anchor_to(rect.calculate_anchor_for_rect(self))


  def detach_from(self, rect):
    corner = self.rect_map[rect]
    if corner in self.vert_map:
      del self.vert_map[corner]

    del self.rect_map[rect]

  def detach(self, rect):
    if not rect:
      remove_rects = self.rect_map
      self.rect_map = {}
      self.vert_map = {}

      for rect in remove_rects:
        rect.detach_from(self)
    else:
      self.detach_from(rect)
      rect.detach_from(self)

  def set_cluster(self, cluster):
    self.__cluster = cluster
    self.__cluster_leader = cluster[0]

  # }}} Attach Functions

  # {{{ Geometry Functions

  # A rectangle overlaps another if any portion of one is inside the other
  # This is an exclusionary overlap, that doesn't count border pixels.
  def overlaps(self, other):
    if (self.x0 >= other.x1) or (self.x1 <= other.x0) or \
       (self.y0 >= other.y1) or (self.y1 <= other.y0):
          return False
    return True

  # }}}

base_corner_combinations = [ (TR, TL), (BR, BL), (TR, BR), (TL, BL) ]
#full_corner_combinations = [ (TL, TR), (BL, BR), (BR, TR), (BL, TL) ]
#corner_combinations = base_corner_combinations + full_corner_combinations
corner_combinations = base_corner_combinations

# Calculates the bounding box bb + p
def incremental_bounding_box(bb, r):
  return ((min(bb[0][0], r.x0), min(bb[0][1], r.y0)),
          (max(bb[1][0], r.x1), max(bb[1][1], r.y1)))

# Calculates the area for a bounding box 2x2
def bounding_area(bb):
  return abs(bb[1][0] - bb[0][0]) * abs(bb[1][1] - bb[0][1])

# Calculates the bounding box for all rectangles by taking maxima in x & y
def bounding_box(rectangles):
  max_x, max_y = 0, 0
  min_x, min_y = 1000, 1000

  for r in rectangles:
    min_x = min(min_x, r.x0)
    min_y = min(min_y, r.y0)
    max_x = max(max_x, r.x1)
    max_y = max(max_y, r.y1)

  return ((min_x, min_y), (max_x, max_y))

# Rectangle Placement Helper
def is_placed(r):
  return r.is_placed

def is_overlapping(rectangles, r):
  for ss in rectangles:
    if ss == r:
      continue

    if not ss.is_placed:
      continue

    if ss.overlaps(r):
      return True
  return False

class BruteSolver:
  BRANCHES={}
  NULL_DATA=(sys.maxint,None)
  def __init__(self, rectangles):
    self.rectangles = rectangles
    self.prev_maxima_time = 0
    self.sum_area = sum([x.area for x in self.rectangles])


  # }}} Representation Helpers
  def to_connection_str(self):
    rect_strs = []
    for r in self.rectangles:
      # rect1 (n1 connections) connect through c1 to rect2(n2 connections) on c2

      # c1 c2 | r1 r2 | n1 n2
      # c2 c1 | r2 r1 | n2 n1
      for n in r.neighbors:
        if n.name > r.name:
          c1 = n.rect_map[r]
          c2 = r.rect_map[n]
          s = "%s %s %s %s %s %s" % (c1, c2, n.name, r.name, len(n.vert_map), len(r.vert_map))
        else:
          c1 = r.rect_map[n]
          c2 = n.rect_map[r]
          s = "%s %s %s %s %s %s" % (c2, c1, r.name, n.name, len(r.vert_map), len(n.vert_map))

        rect_strs.append(s)

      rect_strs.sort()
      return " ".join(rect_strs)
  # }}} Representation Helpers

  def reset_recursor(self):
    self.cur_best = sys.maxint
    BruteSolver.BRANCHES.clear()


  def r_c_p(self, this_bbox, greedy=True, level=0):
    this_area = bounding_area(this_bbox)
    rect_str = self.to_connection_str()

    if rect_str and rect_str in BruteSolver.BRANCHES:
      log.debug('Hit a previous branch!')
      return  BruteSolver.BRANCHES[rect_str]


    if this_area >= self.cur_best:
      log.debug( 'Pruning, due to %s(cur_best) <= %s(this_area)' % (self.cur_best, this_area))
      return BruteSolver.NULL_DATA

    placed_area = this_area
    unplaced_area = self.sum_area - placed_area
    open_area = this_area - self.sum_area

    any_rects = any([not x.is_placed for x in self.rectangles])

    if not any_rects:
      found_time = time.time()
      time_diff = found_time - self.prev_maxima_time
      self.prev_maxima_time = found_time

      # Grow the time to spend in this branch based on the difference in previous
      # and how long it took to find.

      log.debug("***Hit a local maximum***")
      log.debug("Time between maxima: %s" % (time_diff))
      log.debug( "This area: %s" % this_area)
      log.debug( "Prev best: %s" % self.cur_best)
      log.debug( "Difference: %s" % (this_area / float(self.cur_best)))
      log.debug( "Efficiency: %s" % (self.sum_area / float(this_area)))

      self.cur_best = this_area
      self.cur_bbox = this_bbox
      cur_efficiency = self.sum_area / float(this_area)


      cr = copy.deepcopy(self.rectangles)
      return this_area, cr

    # This is only a subset of corner combinations, for now
    best_area = sys.maxint
    best_rects = None
    for i, a in enumerate(self.rectangles):
      possible_placements = []
      for b in self.rectangles[i:]:
        if a.is_placed == b.is_placed:
          continue

        if a.is_placed:
          s = a
          r = b
        else:
          s = b
          r = a


        for c1, c2 in corner_combinations:
          if not c1 in s.vert_map and not c2 in r.vert_map:
            for rotate in [True, False]:
              if rotate and (r.width == r.height):
                continue

              if rotate:
                r.rotate()


              s.attach(c1, r, c2) # Attach will try and set your anchor
              if is_overlapping(self.rectangles, r):
                r.detach(s)
                r.unanchor()
                continue

              bb = incremental_bounding_box(this_bbox, r)
              next_area, fully_placed_rects = self.r_c_p(bb, greedy=greedy, level=level+1)
              if next_area < best_area and fully_placed_rects:
                best_area = next_area
                best_rects = fully_placed_rects

              r.detach(s)
              r.unanchor()

              if rotate:
                r.rotate()


    BruteSolver.BRANCHES[rect_str] = best_area, best_rects
    return BruteSolver.BRANCHES[rect_str]

# }}} Recursive Place

  def place(self, origin_anchor=True, greedy=True):
    self.reset_recursor()
    best_area = 0
    best_rects = None
    for r in self.rectangles:
      # Anchoring r at top level
      if origin_anchor:
        r.anchor_to((0, 0))

      self.prev_maxima_time = time.time()
      best_area, best_rects = self.r_c_p(bounding_box([r]), greedy)
      r.unanchor()
      break

    return best_area, best_rects

def to_html(rectangles, filename):
  f = open("%s.html" % (filename), "w")

  min_x, min_y = 1000, 1000
  for r in rectangles:
    min_x = min(r.x0, min_x)
    min_y = min(r.y0, min_y)

  f.write( "<div>")
  for i in xrange(len(rectangles)):
    r = rectangles[i]
    f.write( "<div style='")
    f.write("width: %s; height: %s;" % (r.width-1, r.height-1))
    f.write("position: absolute; left: %s; top: %s;" %\
            (r.x0-min_x, r.y0-min_y))
    f.write("border: 1px solid #888;")
    intcolors = map(lambda x: int(x*256), r.colors)
    colors256 = map(lambda x: "%02x"%x, intcolors)
    hexcolors = map(lambda x: x.replace('0x', ''), colors256)
    f.write("background-color: #%s%s%s;" % tuple(hexcolors[:-1]))
    f.write("' >")
    f.write("\n")
    f.write( "</div>")
    f.write("\n")

  f.write( "</div>")

  f.close()

# {{{ Cluster Place
# {{{ Lambda type functions
# {{{ Comparator keys
def area_key(x):
  return x.area

def width_key(x):
  return x.width

def height_key(x):
  return x.height

# }}}
# Rectangle Placement Helper
def is_placed(r):
  return r.is_placed

def is_unplaced(r):
  return not r.is_unplaced
# }}}
#}}}

# {{{ Representation Helpers
# Unique representation of a cluster of rectangles based on sizes
# R1 R2 R3
def to_set_str(rectangles):
  rect_strs = []
  rectangles.sort(key=area_key)
  for r in rectangles:
    w,h = max(r.width, r.height), min(r.width, r.height)
    rect_strs.append("%s,%s"%(w,h))
  rect_strs.sort()
  return " ".join(rect_strs)
# }}} Representation Helpers

# {{{ Geometry Helpers

def box_width(bb):
  return bb[1][0] - bb[0][0]

def box_height(bb):
  return bb[1][1] - bb[0][1]


# Moves a box's offsets from any integer positioning to positive (starting from) (0,0) based.
def normalize_box(xy0, xy1):
  offset_x = 0 - xy0[0]
  offset_y = 0 - xy0[1]

  return ((0, 0), (xy1[0]+offset_x, xy1[1]+offset_y))

def normalize_rects(rects):
  min_x, min_y = sys.maxint, sys.maxint
  for rect in rects:
    min_x = min(rect.x0, min_x)
    min_y = min(rect.y0, min_y)

  for rect in rects:
    rect.anchor_point = (rect.x0-min_x, rect.y0-min_y)

def is_overlapping(rectangles, r):
  for ss in rectangles:
    if ss == r:
      continue

    if not ss.is_placed:
      continue

    if ss.overlaps(r):
      return True
  return False


# }}} Geometry Helpers

def pin_rects(best_rects, level=1):
  pinned_rects = []

  for r in best_rects:
    log.debug("(Pin) Examining cluster %s: %s" % (r, r.cluster))
    if not r.is_cluster:
      pinned_rects.append(r)
      continue
    else:
      log.debug("Pinning cluster to %s,%s" % (r.x0, r.y0))
      if r.cluster_leader == r:
        pinned_rects.append(r)
        continue


      r.cluster_leader.unanchor(recurse=True)

      # Normalize cluster coords, rotate and pin it
      for rect in r.cluster:
        if rect == r:
          continue

        if r.rotated:
          rect.pivot()

      if level % 2 == 0:
        for rect in r.cluster:
          rect.colors = r.colors

      r.cluster_leader.anchor_to((0,0))
      normalize_rects(r.cluster)

      original_anchor = r.cluster_leader.anchor_point

      offset_x = r.x0
      offset_y = r.y0

      new_anchor = (original_anchor[0] + offset_x, original_anchor[1] + offset_y)


      log.debug("Re-Anchored %s from %s to %s" % (r.cluster_leader,
        original_anchor, new_anchor))
      r.cluster_leader.unanchor(recurse=True)
      r.cluster_leader.anchor_to(new_anchor)
      pinned_rects.extend(pin_rects(r.cluster, level=level))

  return pinned_rects

# Break one cluster down from level l and put it in to_cluster
def break_cluster(clusters, l):
  break_cluster = random.choice(clusters[l])

  clusters[l].remove(break_cluster)
  if break_cluster.cluster:
    split_cluster = break_cluster.cluster
  else:
    split_cluster = [break_cluster]

  log.info('Breaking cluster %s into %s' % (break_cluster, split_cluster))

  for r in split_cluster:
    r.detach(None)
    r.unanchor()

  return split_cluster

shatter_level = 2
# Break a whole level of clusters down and return them to their previous level
def shatter_cluster(clusters, l):
  log.info("SHATTERING CLUSTER: %s" % (clusters[l]))
  clusters[l] = []
  for rect in clusters[l]:
    rect.detach(None)

  clusters[l-2] = []
  for rect in clusters[l-1]:
    if rect.cluster:
      clusters[l-2].extend(rect.cluster)
    else:
      clusters[l-2].append(rect)

  for rect in clusters[l-2]:
    rect.detach(None)
    rect.unanchor()

  clusters[l-1] = []

  l -= shatter_level
  return l

# TODO: Can use a global dictionary for cluster_size combinations to prevent
# us from re-examining combinations we've seen.
def cluster_place(rs):
  from collections import defaultdict

  # Cluster initialization
  clusters = defaultdict(list)
  best_rects_list = defaultdict(list)
  clusters[0] = rs
  cluster_size = 4
  cluster_level = math.floor(math.log(len(rs), cluster_size))
  clustered_rects = {}

  l = 0

  if len(rs) <= cluster_size:
    best_area, best_rects = place(rs)
    pinned_rects = pin_rects(best_rects)
    return pinned_rects

  # Build a hierarchy of clusters at base cluster_size.
  # For each level, keep trying to find clusters better than EFFICIENCY at
  # packing. Every so often, if we can't find some, we'll break apart a
  # cluster we already formed to try and distribute some of the good pieces.
  log.info("Building cluster hierarchy: %i^%i level" % (cluster_size, cluster_level))

  cluster_cache = {}
  levels = defaultdict(int)
  shatter_threshold = 0.95
  default_efficiency = 0.93
  while l <= cluster_level:
    if len(clusters[l]) <= 1:
      break

    if not l in levels:
      levels[l] = default_efficiency

    best_rects_list[l] = []

    log.info('Clustering level: %s' % l)
    to_cluster = copy.copy(clusters[l])
    to_cluster.sort(key=height_key)
    to_cluster.reverse()

    split_index = cluster_size
    if l == cluster_level - 1:
      split_index = 0
    move_to_next_round = to_cluster[:split_index]

    for cluster in move_to_next_round:
      clusters[l+1].append(cluster)

    keep_for_this_round = to_cluster[split_index:]

    to_cluster = keep_for_this_round
    false_clusters = 0
    broken = 0
    while to_cluster:
      if len(to_cluster) < cluster_size:
        cluster = copy.copy(to_cluster)
      else:
        cluster = random.sample(to_cluster, cluster_size)
      log.debug("Trying to cluster: %s" % (cluster))

      cluster_str = to_set_str(cluster)

      if len(cluster) == 1:
        log.warn("%s skipping clustering" % cluster)
        r = cluster[0]
        clusters[l+1].append(r)
        to_cluster.remove(r)
        continue
      else:
        if not cluster_str in cluster_cache:
          s = BruteSolver(rectangles=cluster)
          best_area, best_rects = s.place()
          cluster_cache[cluster_str] = (best_area, best_rects)

        cached_area, cached_rects = copy.deepcopy(cluster_cache[cluster_str])
        best_rects = cached_rects

        sum_area = sum(map(lambda x: x.area, best_rects))
        CUR_EFFICIENCY = sum_area / float(cached_area)

#        log.info("Clustering %s at %.02f efficiency" % (repr(cluster), CUR_EFFICIENCY))

        if CUR_EFFICIENCY < levels[l] or not best_rects:
          false_clusters += 1
#          log.info("Couldn't cluster at a high enough efficiency")
#          for c in packed:
#            c.unanchor()
#            c.detach(None)

          if false_clusters == 5:
            false_clusters = 0
            if len(clusters[l+1]) > 0:
              to_cluster.extend(break_cluster(clusters, l+1))

            broken += 1
            if broken == 5:
              broken = 0
              levels[l] -= 0.01
              log.info("Dropping cluster[%s] efficiency to %s" % (l, levels[l]))
              l = shatter_cluster(clusters, l)
          continue
        else:
          log.info("Clustering %s at %.02f efficiency" % (repr(cluster), CUR_EFFICIENCY))
#          log.info("Accepting cluster")
          broken = 0




        best_rects_list[l].extend(best_rects)

        cur_bbox = bounding_box(best_rects)
        r = R(height=box_height(cur_bbox), width=box_width(cur_bbox))
        r.set_cluster(best_rects)

        for rect in cluster:
          rect.unanchor()
          if rect in to_cluster:
            to_cluster.remove(rect)

      false_clusters = 0
      clusters[l+1].append(r)

    l += 1

    if l == cluster_level:
      if clusters[l+1]:
        for r in clusters[l+1]:
          clusters[l].append(r)
        clusters[l+1] = []

      if clusters[l]:
        remaining = list(set(clusters[l]))
        s = BruteSolver(rectangles=remaining)
        best_area, best_rects = s.place()

        log.info("Placed remaining clusters: %s at %s" % (remaining, CUR_EFFICIENCY))
        if CUR_EFFICIENCY < shatter_threshold-0.01 or not best_rects:
          shatter_threshold -= 0.01
          log.info("Dropping shatter threshold to %s" % shatter_threshold)
          l = shatter_cluster(clusters, l)
          for r in best_rects:
            r.unanchor()
            r.detach(None)
        else:
          best_rects_list[l].extend(best_rects)
          break



  # What we have:
  # r1,r2,r3
  # r_1(0), r_2(0), r_3(0)...r_n(0)
  # r_1(1), r_2(1), r_3(1)...r_n/cluster_level(1)
  # r_1(2), r_2(2), r_3(2)...r_n/cluster_level^2(2)

  # Show the best placement of the top level cluster.
  sum_area = sum([x.area for x in rs])
  log.info("Overall Efficiency: %s" % (float(sum_area) / bounding_area(cur_bbox)))

  log.info("Pinning rects")
  pinned_rects = pin_rects(best_rects)

  if len(pinned_rects) < len(rs):
    log.critical("Pinned: %s Found: %s" % (len(pinned_rects), len(rs)))
    raise Exception("Somehow we missed some rectangles during our clustering analysis and/or pinning")

  log.info("Overall Efficiency: %s" % (float(sum_area) / bounding_area(bounding_box(pinned_rects))))


  return pinned_rects

# }}}

if __name__ == "__main__":
  rects = []
  lines = sys.stdin.readlines()
  for line in lines[1:]:
    x,y = line.split()
    rects.append(R(int(x), int(y)))

  best_rects = cluster_place(rects)
  print bounding_area(bounding_box(best_rects))


  to_html(best_rects, "cluster")
# vim: foldlevel=1 foldmethod=marker
