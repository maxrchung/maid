from mathutils import *
from mathutils.geometry import *
from storyboard import Sprite
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

def create_sprite(T, file, time):
    A, B, C = T
    unit_x = Vector((1, 0))
    AB = B - A
    AC = C - A
    rotate = AB.angle_signed(unit_x)
    scale_x = AB.length / constants.SPRITE_SIZE
    scale_y = AC.length / constants.SPRITE_SIZE
    scale = Vector((scale_x, scale_y, 0))

    sprite = Sprite(file, A)
    sprite.rotate(time, time + constants.FRAME_TIME, rotate, rotate)
    sprite.scale(time, time, scale, scale)
    return sprite

def render_triangle(T, file, time):
    A, B, C = T

    # Reorder such that first point has the largest angle, or put in another
    # way, the line opposite of the point is the longest. This addresses an
    # issue with obtuse triangle projecting outside of the triangle.
    A, B, C = reorder_biggest_angle(A, B, C)

    # Project point across from first point
    D, _ = intersect_point_line(A, B, C)

    # Ensure correct ordering while keeping first point as is
    T1 = reorder_clockwise(D, A, B)
    T2 = reorder_clockwise(D, A, C)

    sprite1 = create_sprite(T1, file, time)
    sprite2 = create_sprite(T2, file, time)
    return sprite1, sprite2

def render_triangles(storyboard, triangles, previous, time):
    sprites = []

    for triangle, file in triangles:
        # Transform to osu! coordinates
        osu_triangle = [
            Vector((
                v.x * constants.STORYBOARD_SIZE.x + constants.STORYBOARD_OFFSET.x,
                (1 - v.y) * constants.STORYBOARD_SIZE.y + constants.STORYBOARD_OFFSET.y
            ))
            for v in triangle
        ]

        sprite1, sprite2 = render_triangle(osu_triangle, file, time)
        sprites.append(sprite1)
        sprites.append(sprite2)

    is_previous_match = len(previous) == len(sprites) and all(
        prev.file == curr.file and
        prev.position == curr.position and
        prev.commands[0].start_rotate == curr.commands[0].start_rotate and
        prev.commands[1].start_scale == curr.commands[1].start_scale
        for prev, curr in zip(previous, sprites)
    )

    print('is_previous_match', is_previous_match)

    if is_previous_match:
        for prev in previous:
            prev.commands[0].end = time + constants.FRAME_TIME
            prev.commands[1].end = time + constants.FRAME_TIME
        return previous
    else:
        for sprite in sprites:
            storyboard.add_sprite(sprite)
        return sprites