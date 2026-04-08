import sys
import os

# Add folder to path so modules can be found
script_dir = os.path.dirname(__file__)
if script_dir not in sys.path:
    sys.path.append(script_dir)

# Force modules to reload and bypass interpreter cache
import importlib
import constants
importlib.reload(constants)
import images
importlib.reload(images)
import storyboard
importlib.reload(storyboard)

from mathutils import *
from storyboard import Storyboard
from images import create_images

create_images()

sb = Storyboard()

sprite = sb.sprite('b', Vector((0,0)))
sprite.rotate(0, 999999, 0, 0)

sb.write()

print('Done')