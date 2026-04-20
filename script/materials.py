from PIL import Image, ImageDraw
from pathlib import Path
import constants
import bpy
import os
import glob

def delete_images():
   pngs = glob.glob(os.path.join(constants.SB_FOLDER, "*.png"))
   for png in pngs:
      os.remove(png)

def create_background():
    background = Image.new("RGB", (1, 1), (0, 0, 0))
    path = Path(constants.SB_FOLDER) / "b.png"
    background.save(path, "PNG", optimize=True)

def create_triangle(file, color):
  image = Image.new("RGBA", (constants.SPRITE_SIZE, constants.SPRITE_SIZE), (0, 0, 0, 0))
  draw = ImageDraw.Draw(image)
  # Not sure, but 1 to account for drawing over
  triangle = [(0, 0), (0, constants.SPRITE_SIZE - 1), (constants.SPRITE_SIZE - 1, 0)]
  draw.polygon(triangle, fill=(
     int(color[0] * 255),
     int(color[1] * 255),
     int(color[2] * 255)
  ))
  path = Path(constants.SB_FOLDER) / f"{file}.png"
  image.save(path, "PNG", optimize=True)

def create_materials():
  delete_images()
  
  create_background()

  materials = {}
  counter = 0

  for material in bpy.data.materials:
      name = material.name
      # Making some assumptions about the material structure
      color = material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value

      create_triangle(counter, color)
      materials[name] = counter
      counter = counter + 1

  return materials

