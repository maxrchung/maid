import sys
import os
import importlib

# Add folder to path so modules can be found
script_dir = os.path.dirname(__file__)
if script_dir not in sys.path:
    sys.path.append(script_dir)

# Automatically purge cached project modules from sys.modules so fresh imports load
script_dir_norm = os.path.normcase(os.path.abspath(script_dir))
for name, module in list(sys.modules.items()):
    if not name.startswith("<") and name != "__main__":
        mod_file = getattr(module, "__file__", "") or ""
        if mod_file and os.path.normcase(os.path.abspath(mod_file)).startswith(script_dir_norm):
            del sys.modules[name]

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

