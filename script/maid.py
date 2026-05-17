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
from bpy_extras.object_utils import world_to_camera_view
from storyboard import Storyboard
from materials import create_materials
from render import render_triangle

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
        if object.scale.x == 0.0:
            continue
        
        objects.append(object)

    triangles = []

    for object in objects:
        mesh = object.data
        mesh.calc_loop_triangles()

        world_matrix = object.matrix_world

        for triangle in mesh.loop_triangles:
            # Cull if normal points away from camera
            world_normal = (world_matrix.to_3x3() @ triangle.normal).normalized()
            to_camera = (camera.location - world_matrix @ mesh.vertices[triangle.vertices[0]].co).normalized()
            if world_normal.dot(to_camera) <= 0:
                continue

            vertices = []
            for i in triangle.vertices:
                world_vertex = world_matrix @ mesh.vertices[i].co

                # Bottom left origin where x and y are 0 to 1
                camera_vertex = world_to_camera_view(scene, camera, world_vertex)
                vertices.append(camera_vertex)

            # Cull if all behind camera
            if all(vertex.z <= 0 for vertex in vertices):
                continue

            # Cull if all outside edge
            if (all(vertex.x >= 1 for vertex in vertices) or
                all(vertex.x <= 0 for vertex in vertices) or
                all(vertex.y >= 1 for vertex in vertices) or
                all(vertex.y <= 0 for vertex in vertices)):
                continue

            # Transform to osu! coordinates
            osu_triangle = []
            for vertex in vertices:
                x = vertex.x * constants.STORYBOARD_SIZE.x + constants.STORYBOARD_OFFSET.x
                y = (1 - vertex.y) * constants.STORYBOARD_SIZE.y + constants.STORYBOARD_OFFSET.y
                osu_triangle.append(Vector((x, y)))

            # Get material file
            material = object.material_slots[triangle.material_index].material
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