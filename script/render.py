from mathutils import *
from mathutils.geometry import *
import constants

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

def reorder_clockwise(A, B, C):
    cross = (B - A).cross(C - A)
    # Swap points
    if cross < 0:
        return A, C, B
    return A, B, C

def create_sprite(storyboard, T, file):
    A, B, C = T
    unit_x = Vector((1, 0))
    AB = B - A
    AC = C - A
    rotate = AB.angle_signed(unit_x)
    scale_x = AB.length / constants.SPRITE_SIZE
    scale_y = AC.length / constants.SPRITE_SIZE
    scale = Vector((scale_x, scale_y, 0))

    sprite = storyboard.sprite(file, A)
    sprite.rotate(0, 1000, rotate, rotate)
    sprite.scale(0, 0, scale, scale)

def render_triangle(storyboard, T, file):
    A, B, C = T

    # Reorder such that first point has the largest angle, or put in another
    # way, the line away from the point is the longest. This addresses an issue
    # with obtuse triangle projecting outside of the triangle.
    A, B, C = reorder_biggest_angle(A, B, C)

    # Project point across from first point
    D, _ = intersect_point_line(A, B, C)

    # Ensure correct ordering while keeping first point as is
    T1 = reorder_clockwise(D, A, B)
    T2 = reorder_clockwise(D, A, C)

    create_sprite(storyboard, T1, file)
    create_sprite(storyboard, T2, file)