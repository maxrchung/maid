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
from mathutils.geometry import intersect_tri_tri_2d
from bpy_extras.object_utils import world_to_camera_view
from storyboard import Storyboard
from materials import create_materials
from render import render_triangle

def order_triangles(triangles):
    # Order in world coordinates using topo sort
    graph = {i: [] for i in range(len(triangles))}
    indegree = {i: 0 for i in range(len(triangles))}

    for i in range(len(triangles)):
        for j in range(i + 1, len(triangles)):
            t1, t2 = triangles[i], triangles[j]

            if not intersect_tri_tri_2d(t1[0], t1[1], t1[2], t2[0], t2[1], t2[2]):
                continue

            if t1 > t2
                graph[t1].append(t2)
                indegree[t2] = indegree[t2] + 1


    order = []
        
    while indegree
        smallest_indegree = min(indegree.values())
            
        if smallest_indegree > 0
            there's a loop btw       
    
        for key in list(indegree.keys())
            if indegree[key] > smallest_indegree
                continue
                
            order.append(key)

            for dep in graph[key]
                indegree[dep] = indegree[dep] - 1

            del indegree[key]

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

    for object in objects:
        mesh = object.data
        mesh.calc_loop_triangles()

        world_matrix = object.matrix_world
        world_matrix_3x3 = world_matrix.to_3x3()

        world_triangles = []
        for loop_triangle in mesh.loop_triangles:
            # Cull if normal points away from camera
            world_normal = (world_matrix_3x3 @ loop_triangle.normal).normalized()
            to_camera = (camera.location - world_matrix @ mesh.vertices[loop_triangle.vertices[0]].co).normalized()
            if world_normal.dot(to_camera) <= 0:
                continue

            world_triangle = [world_matrix @ mesh.vertices[i].co for i in loop_triangle.vertices]
            world_triangles.append(world_triangle)

        ordered_triangles = order_triangles(world_triangles)
        
        for world_triangle in ordered_triangles:
            # Bottom left origin where x and y are 0 to 1
            camera_triangle = [world_to_camera_view(scene, camera, v) for v in world_triangle]

            # Cull if all behind camera
            if all(vertex.z <= 0 for vertex in camera_triangle):
                continue

            # Cull if all outside edge
            if (all(vertex.x >= 1 for vertex in camera_triangle) or
                all(vertex.x <= 0 for vertex in camera_triangle) or
                all(vertex.y >= 1 for vertex in camera_triangle) or
                all(vertex.y <= 0 for vertex in camera_triangle)):
                continue

            # Transform to osu! coordinates
            osu_triangle = [
                Vector((
                    v.x * constants.STORYBOARD_SIZE.x + constants.STORYBOARD_OFFSET.x,
                    (1 - v.y) * constants.STORYBOARD_SIZE.y + constants.STORYBOARD_OFFSET.y
                ))
                for v in camera_triangle
            ]

            # Get material file
            material = object.material_slots[loop_triangle.material_index].material
            if not material:
                continue
            file = materials[material.name]

            render_triangle(storyboard, osu_triangle, file)

    frame += 1


# render_triangle(storyboard, (Vector((0, 0)), Vector((100, -50)), Vector((400, 100))))
# render_triangle(storyboard, (Vector((400, 400)), Vector((0, 200)), Vector((600, 600))))
# render_triangle(storyboard, (Vector((80, 300)), Vector((55, 200)), Vector((50, 300))))

storyboard.write()

print('Done')