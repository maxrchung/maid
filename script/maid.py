import bpy
from mathutils import *
from storyboard import Storyboard

D = bpy.data
C = bpy.context



storyboard = Storyboard()

sprite = storyboard.sprite()
sprite.rotate(0, 1000, 0, 1)


storyboard.write()

print('Done')