from PIL import Image, ImageDraw
from pathlib import Path
import constants

def create_triangle(file, color):
  image = Image.new("RGB", (100, 100), (0, 0, 0, 0))
  draw = ImageDraw.Draw(image)
  triangle = [(0, 0), (0, 100), (100, 0)]
  draw.polygon(triangle, fill=color)
  path = Path(constants.SB_FOLDER) / f"{file}.png"
  image.save(path, "PNG", optimize=True)


def create_images():
  background = Image.new("RGB", (1,1), (0, 0, 0))
  path = Path(constants.SB_FOLDER) / "b.png"
  background.save(path, "PNG", optimize=True)

  create_triangle(1, (200, 0, 0))
  create_triangle(2, (0, 200, 0))
  create_triangle(3, (0, 0, 200))

