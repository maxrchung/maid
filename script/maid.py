import sys
import os

# Add to path
script_dir = os.path.dirname(__file__)
if script_dir not in sys.path:
    sys.path.append(script_dir)

# Don't cache modules
sys.dont_write_bytecode = True

import bpy
from mathutils import *
from storyboard import Storyboard

D = bpy.data
C = bpy.context



sb = Storyboard()

sprite = sb.sprite('1', Vector((0,0)))
sprite.rotate(0, 1000, 0, 1)


sb.write()

print('Done')