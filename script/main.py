import sys
import os
import time

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
import constants
from mathutils import Vector
from storyboard import Storyboard
from materials import create_materials
from frame import frame_triangles
from render import render_triangles
from variables import generate_variables

script_start = time.perf_counter()

materials = create_materials()

storyboard = Storyboard()
sprite = storyboard.sprite('b', Vector((0, 0)))
sprite.rotate(0, 999999, 0, 0)

frame = 0

scene = bpy.data.scenes[0]
camera = scene.camera

rendered = []
total_sprites = 0

while frame <= constants.FRAME_END:
    print("Frame", frame)
    scene.frame_set(frame)

    triangles = frame_triangles(scene, camera, materials)
    rendered = render_triangles(storyboard, triangles, rendered, frame * constants.FRAME_RATE)
    total_sprites += len(rendered)

    frame += constants.FRAME_STEP
    print()

variables = generate_variables(materials, storyboard) if constants.ENABLE_VARIABLES else []
storyboard.write(variables)

print('total_sprites', total_sprites)
print(f'elapsed {(time.perf_counter() - script_start) / 60:.2f}m')