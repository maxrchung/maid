import sys
import os
import importlib

# Add folder to path so modules can be found
script_dir = os.path.dirname(__file__)
if script_dir not in sys.path:
    sys.path.append(script_dir)

# Automatically reload any project module from disk
for name, module in list(sys.modules.items()):
    if getattr(module, "__file__", "") and module.__file__.startswith(script_dir):
        importlib.reload(module)

import bpy
from mathutils import Vector
from storyboard import Storyboard
from materials import create_materials
from frame import frame_triangles
from render import render_triangles

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
    scene.frame_set(frame)

    triangles = frame_triangles(scene, camera, materials)
    render_triangles(storyboard, triangles)

    frame += 1

storyboard.write()

print('Done')
