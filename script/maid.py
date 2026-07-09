import sys
import os

# Add folder to path so modules can be found. This is pretty stupid and maybe
# reason enough to look into add-on development instead.
script_dir = os.path.dirname(__file__)
if script_dir not in sys.path:
    sys.path.append(script_dir)

# Force modules to reload and bypass interpreter cache. This is pretty stupid
# and maybe reason enough to look into add-on development instead.
import importlib
import constants
importlib.reload(constants)
import materials
importlib.reload(materials)
import storyboard
importlib.reload(storyboard)
import render
importlib.reload(render)

import bpy
from mathutils import *
from mathutils.geometry import intersect_point_tri, intersect_tri_tri_2d
from bpy_extras.object_utils import world_to_camera_view
from storyboard import Storyboard
from materials import create_materials
from render import render_triangle

def is_a_behind_b(a, b):
    for v in a:
        p = intersect_point_tri(v, b[0], b[1], b[2])

        if p:
            return v.z <= p.z
    
    for v in b:
        p = intersect_point_tri(v, a[0], a[1], a[2])

        if p:
            return v.z >= p.z

def order_triangles(triangles):
    # Order in world coordinates using topo sort
    graph = {i: [] for i in range(len(triangles))}
    indegree = {i: 0 for i in range(len(triangles))}

    for i in range(len(triangles)):
        for j in range(i + 1, len(triangles)):
            a, b = triangles[i][0], triangles[j][0]

            if not intersect_tri_tri_2d(a[0].xy, a[1].xy, a[2].xy, b[0].xy, b[1].xy, b[2].xy):
                continue

            if is_a_behind_b(a, b):
                graph[j].append(i)
                indegree[i] += 1
            else:
                graph[i].append(j)
                indegree[j] += 1

    ordered = []
        
    while indegree:
        smallest_indegree = min(indegree.values())
            
        for key in list(indegree.keys()):
            if indegree[key] > smallest_indegree:
                continue
                
            ordered.append(triangles[key])
            del indegree[key]

            for dep in graph[key]:
                if dep not in indegree:
                    print("3-way cycle")
                    continue

                indegree[dep] -= 1

            if smallest_indegree > 0:
                print("smallest_indegree > 0")
                break

    return ordered

materials = create_materials()

storyboard = Storyboard()

sprite = storyboard.sprite('b', Vector((0, 0)))
sprite.rotate(0, 999999, 0, 0)

frame = 0
frame_end = 0

scene = bpy.data.scenes[0]
camera = scene.camera

while frame <= frame_end:
    print("Processing", frame)
    
    """
    {
        points: [Vector, Vector, Vector],
        material: string
    }
    """
    scene.frame_set(frame)
    camera_location = camera.matrix_world.translation

    objects = []
    for object in scene.objects:
        if not object.visible_get():
            continue
        
        # Ignore things like camera and rigs
        if object.type != "MESH":
            continue
        
        # Only consider objects that have some scale value
        if object.scale.x == 0.0 or object.scale.y == 0.0 or object.scale.z == 0.0:
            continue
        
        objects.append(object)

    triangles = []
    for object in objects:
        mesh = object.data
        mesh.calc_loop_triangles()

        world_matrix = object.matrix_world
        world_matrix_3x3 = world_matrix.to_3x3()
        view_matrix = camera.matrix_world.inverted()

        for loop_triangle in mesh.loop_triangles:
            # Cull if normal points away from camera
            world_normal = (world_matrix_3x3 @ loop_triangle.normal).normalized()
            to_camera = (camera.location - world_matrix @ mesh.vertices[loop_triangle.vertices[0]].co).normalized()
            if world_normal.dot(to_camera) <= 0:
                continue

            world_triangle = [world_matrix @ mesh.vertices[i].co for i in loop_triangle.vertices]

            # Bottom left origin where x and y are 0 to 1
            camera_triangle = [world_to_camera_view(scene, camera, v) for v in world_triangle]

            # Cull if all behind camera
            if all(v.z <= 0 for v in camera_triangle):
                continue

            # Cull if all outside edge
            if (all(v.x >= 1 for v in camera_triangle) or
                all(v.x <= 0 for v in camera_triangle) or
                all(v.y >= 1 for v in camera_triangle) or
                all(v.y <= 0 for v in camera_triangle)):
                continue

            # Get material file
            material = object.material_slots[loop_triangle.material_index].material
            if not material:
                continue
            file = materials[material.name]

            triangles.append((camera_triangle, file))

    # Order back to front
    ordered = order_triangles(triangles)
        
    for triangle, file in ordered:
        # Transform to osu! coordinates
        osu_triangle = [
            Vector((
                v.x * constants.STORYBOARD_SIZE.x + constants.STORYBOARD_OFFSET.x,
                (1 - v.y) * constants.STORYBOARD_SIZE.y + constants.STORYBOARD_OFFSET.y
            ))
            for v in triangle
        ]

        render_triangle(storyboard, osu_triangle, file)

    frame += 1


# render_triangle(storyboard, (Vector((0, 0)), Vector((100, -50)), Vector((400, 100))))
# render_triangle(storyboard, (Vector((400, 400)), Vector((0, 200)), Vector((600, 600))))
# render_triangle(storyboard, (Vector((80, 300)), Vector((55, 200)), Vector((50, 300))))

storyboard.write()

print('Done')