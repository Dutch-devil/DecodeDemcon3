# Consider the following problem on a tiny 3x3 field:
# 1 ? 2
# ? ? ?
# ? 4 ?
#
# Any naive implementation looking at one or a number of squares at a time would not be able to solve it, let alone similar problems at a larger scale.
# Therefore, it is important to look at all regions around a number and specifically the intersection on these regions.
# For example, lets consider the regions around 2 (region A) and 4 (region B) and their intersection (region C):
# 1 A 2     1 ? 2       1 D 2
# ? A A  n  B B B   =   E C C
# ? 4 ?     B 4 B       E 4 E
#
# From these last three regions we can deduct the following:
#  - Region C consists of 2 fields and can contain 1-2 mines (C: 1-2 / 2)
#  - Region D consists of 3 fields and can contain 1-3 mines (D: 1-3 / 3)
#  - Region E consists of 1 field  and can contain 0-1 mines (E: 0-1 / 1)
#
# Unfortunately, from this we know nothing, continuing by adding field 1 now does not result in a solution (thus, the order of intersecting matters!)
#
# Lets try again with fields 1 and 2:
# 1 A 2     1 B 2       1 C 2
# A A ?  n  ? B B   =   D C E
# ? 4 ?     ? 4 ?       ? 4 ?
#
# Deduction:
# C: 1-1 / 2
# D: 0-0 / 1
# E: 1-1 / 1
#
# Now we know for sure that B must be a mine and A must be safe! And we can continue trying this until the puzzle is solved....
#
#
#
# But instead, lets write some code to implement this strategy.
# Pseudocode:
#  For each numbered field:
#    Create a set of all adjacent unknown fields
#    If the set is empty, continue with the next field
#    Calculate the mines remaining as number-adjacent mines
#    If mines remaining is 0, then explore all adjacent unknown fields and restart
#    If mines remaining is equal to the amount of adjacent fields, mark all as mine and restart
#    Store region with mines remaining as mininum and maximum amount of mines, and the set of unknown fields
#
# If no regions stored, then we are finished!
#
#  For region A in all stored regions:
#    For region B in all subsequent stored regions:
#      Calculate intersection C of the sets of unknown fields of region A and B
#      Calculate D as the set difference A - B
#      Calculate E as the set difference B - A
#      Maximum amount of mines in C = min(maximum amount of mines in A, maximum amount of mines in B)
#      Minimum amount of mines in C = max(minimum amount of mines in A - size(D), minimum amount of mines in B - size(E)), but at least 0
#      Maximum amount of mines in D = maximum amount of mines in A - minimum amount of mines in C, but at least 0
#      Maximum amount of mines in E = maximum amount of mines in B - minimum amount of mines in C, but at least 0
#      Minimum amount of mines in D = minimum amount of mines in A - maximum amount of mines in C, but at least 0
#      Minimum amount of mines in E = minimum amount of mines in B - maximum amount of mines in C, but at least 0
#


from random import randint
from dataclasses import dataclass
from enum import IntEnum
from mineField import *

# For performance reasons, we are limited to a maximum recursion depth
# Note that this limits the amount of perfect solutions we can find...
MAX_RECURSION_DEPTH = 4

# Start with creating the minefield
width = EXPERT_FIELD['width']
height = EXPERT_FIELD['height']
mines_left = EXPERT_FIELD['number_of_mines']
minefield = MineField(width=width, height=height, number_of_mines=mines_left)

class FieldType(IntEnum):
    Numbered0 = 0
    Numbered1 = 1
    Numbered2 = 2
    Numbered3 = 3
    Numbered4 = 4
    Numbered5 = 5
    Numbered6 = 6
    Numbered7 = 7
    Numbered8 = 8
    Mine = 9
    Unknown = 10

@dataclass
class Region(object):
    mines_min: int
    mines_max: int
    fields: set

class Field(object):
    x = 0
    y = 0
    type = FieldType.Unknown
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Keep track of a local playarea for hints
playarea = []
for x in range(0, width):
    column = []
    for y in range(0, height):
        column.append(Field(x, y))
    playarea.append(column)

def sweep_field(field):
    adjacent_mines = minefield.sweep_cell(field.x, field.y)
    field.type = FieldType(adjacent_mines)

def find_adjacent_type(x: int, y: int, type: FieldType):
    adjacent = set()
    for scan_x in range(max(x - 1, 0), min(x + 2, width)):
        for scan_y in range(max(y - 1, 0), min(y + 2, height)):
            if (False == (scan_x == x and scan_y == y)) and (playarea[scan_x][scan_y].type == type):
                adjacent.add(playarea[scan_x][scan_y])
    return adjacent

def check_region(region):
    if (len(region.fields) == 0) or (region.mines_min != region.mines_max):
        # Don't know for sure...
        return False
    if region.mines_min == 0:
        # No mines, explore all
        for field in region.fields:
            sweep_field(field)
        return True
    if region.mines_min == len(region.fields):
        # All mines, mark
        for field in region.fields:
            field.type = FieldType.Mine
            global mines_left
            mines_left = mines_left - 1
        return True
    return False

def find_regions():
    regions = []
    playarea_modified = False
    for y in range(0, height):
        for x in range(0, width):
            # Skip non-numbered fields
            if (playarea[x][y].type == FieldType.Mine) or (playarea[x][y].type == FieldType.Unknown):
                continue
            
            num_mines = int(playarea[x][y].type)
            
            adjacent_unknown = find_adjacent_type(x, y, FieldType.Unknown)
            if len(adjacent_unknown) == 0:
                continue
            
            adjacent_mines = len(find_adjacent_type(x, y, FieldType.Mine))
            mines_remaining = num_mines - adjacent_mines
            region = Region(mines_remaining, mines_remaining, adjacent_unknown)
            
            # Don't check duplicate regions for performance reasons
            duplicate = False
            for other_region in regions:
                if region.fields == other_region.fields:
                    duplicate = True
                    break
            if duplicate:
                continue
            
            # Check for exploration or mines
            playarea_modified = playarea_modified | check_region(region)
            
            # Store region
            regions.append(region)
    return (playarea_modified, regions)

def split_regions(regions, depth):
    if depth >= MAX_RECURSION_DEPTH:
        return False

    for regionA_index in range(0, len(regions)):
        for regionB_index in range(regionA_index + 1, len(regions)):
            regionA = regions[regionA_index]
            regionB = regions[regionB_index]
            
            regionC_fields = regionA.fields.intersection(regionB.fields)
            if len(regionC_fields) == 0:
                # No overlap, don't split
                continue
            
            regionD_fields = regionA.fields.difference(regionB.fields)
            regionE_fields = regionB.fields.difference(regionA.fields)
            
            if (len(regionD_fields) == 0) and (len(regionE_fields) == 0):
                # Full overlap, don't split
                continue
            
            regionC_mines_max = min(regionA.mines_max, regionB.mines_max)
            regionC_mines_min = max(regionA.mines_min - len(regionD_fields), regionB.mines_min - len(regionE_fields), 0)
            regionD_mines_max = max(regionA.mines_max - regionC_mines_min, 0)
            regionD_mines_min = max(regionA.mines_min - regionC_mines_max, 0)
            regionE_mines_max = max(regionB.mines_max - regionC_mines_min, 0)
            regionE_mines_min = max(regionB.mines_min - regionC_mines_max, 0)
            
            regionC = Region(regionC_mines_min, regionC_mines_max, regionC_fields)
            regionD = Region(regionD_mines_min, regionD_mines_max, regionD_fields)
            regionE = Region(regionE_mines_min, regionE_mines_max, regionE_fields)
            
            playarea_modified = False
            
            # Check for exploration or mines
            playarea_modified = playarea_modified | check_region(regionC)
            playarea_modified = playarea_modified | check_region(regionD)
            playarea_modified = playarea_modified | check_region(regionE)
            
            # If playarea modified, we have to restart
            if playarea_modified:
                return True
            
            # Remove old regions and add new regions
            regions.append(regionC)
            regions[regionA_index] = regionD
            regions[regionB_index] = regionE
            
            # Recursively call
            playarea_modified = split_regions(regions, depth + 1)
            
            # Restore to original state so that we can continue without making a deep copy
            regions[regionB_index] = regionB
            regions[regionA_index] = regionA
            del regions[-1]
            
            # If playarea modified, we have to restart
            if playarea_modified:
                return True
    return False

def find_remaining():
    remaining = []
    for y in range(0, height):
        for x in range(0, width):
            if playarea[x][y].type == FieldType.Unknown:
                remaining.append(playarea[x][y])
    return remaining

def visualize():
    for y in range(0, height):
        line = ''
        for x in range(0, width):
            if playarea[x][y].type == FieldType.Unknown:
                line += '?'
            elif playarea[x][y].type == FieldType.Mine:
                line += 'x'
            else:
                line += str(int(playarea[x][y].type))
        print(line)
    print()

while True:
    visualize()
    # Rebuild all regions
    # As an optimization, it should be possible to keep a live list of regions, which is adapted with every sweep or mine
    playarea_modified, regions = find_regions()
    if playarea_modified:
        # Modified playarea, need to continue until no more modifications are made
        continue
    
    playarea_modified = split_regions(regions, 0)
    if playarea_modified:
        # As long as modifications happen we have to continue searching
        continue
    
    remaining = find_remaining()
    if mines_left == 0:
        # Sweep remaining cells to verify we are done
        for to_sweep in remaining:
            sweep_field(to_sweep)
        remaining = []
    if len(remaining) == 0:
        # Done searching!
        break
    
    # Some mines are left, but no more hits for certain
    # We could implement some smart guess here, but times up, so just do a random guess...
    guess = randint(0, len(remaining) - 1)
    sweep_field(remaining[guess])

print('Solution:')
visualize()

