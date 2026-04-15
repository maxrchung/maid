import sys
import os

# Add folder to path so modules can be found
script_dir = os.path.dirname(__file__)
if script_dir not in sys.path:
    sys.path.append(script_dir)

# Force modules to reload and bypass interpreter cache
import importlib
import constants
importlib.reload(constants)
import images
importlib.reload(images)
import storyboard
importlib.reload(storyboard)

from mathutils import *
from mathutils.geometry import *
from storyboard import Storyboard
from images import create_images

create_images()

sb = Storyboard()

sprite = sb.sprite('b', Vector((0, 0)))
sprite.rotate(0, 999999, 0, 0)

A = Vector((0, 0))
B = Vector((100, -50))
C = Vector((400, 100))

# Reorder A, B, C such that first point has the largest angle, or put in another
# way, the line away from this point is the longest. This addresses an issue with
# obtuse triangle projecting outside of the triangle.
def reorder_biggest_angle(A, B, C):
    ab = (B - A).length
    bc = (C - B).length
    ca = (A - C).length
    longest = max(ab, bc, ca)
    if longest == ab:
        return C, A, B
    elif longest == bc:
        return A, B, C
    else:
        return B, A, C
    
A, B, C = reorder_biggest_angle(A, B, C)

# Project point across from first point
D, _ = intersect_point_line(A, B, C)

# Ensure correct ordering while keeping first point as is
def reorder_clockwise(A, B, C):
    cross = (B - A).cross(C - A)
    # Swap points
    if cross > 0:
        return A, C, B
    return A, B, C

T1 = reorder_clockwise(D, A, B)
T2 = reorder_clockwise(D, A, C)

def create_sprite(storyboard, T):
    A, B, C = T
    unit_x = Vector((1, 0))
    AB = B - A
    AC = C - A
    rotate = unit_x.angle(AB)
    scale_x = AB.length / constants.SPRITE_SIZE
    scale_y = AC.length / constants.SPRITE_SIZE
    scale = Vector((scale_x, scale_y, 0))

    sprite = storyboard.sprite(1, A)
    sprite.rotate(0, 1000, rotate, rotate)
    sprite.scale(0, 0, scale, scale)

create_sprite(sb, T1)
create_sprite(sb, T2)

sb.write()

print('Done')