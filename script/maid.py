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
import images
importlib.reload(images)
import storyboard
importlib.reload(storyboard)
import triangles
importlib.reload(triangles)

from mathutils import *
from storyboard import Storyboard
from images import create_images
from triangles import create_triangles

create_images()

storyboard = Storyboard()

sprite = storyboard.sprite('b', Vector((0, 0)))
sprite.rotate(0, 999999, 0, 0)

create_triangles(storyboard, (Vector((0, 0)), Vector((100, -50)), Vector((400, 100))))
create_triangles(storyboard, (Vector((400, 400)), Vector((0, 200)), Vector((600, 600))))
create_triangles(storyboard, (Vector((80, 300)), Vector((55, 200)), Vector((50, 300))))

storyboard.write()

print('Done')