import constants
import math

def is_vector_close(v1, v2):
  is_vector_close = (v1 - v2).length < constants.EPSILON
  return is_vector_close

def format_number(number, significant_digits):
  format_number = f"{number:.{significant_digits}f}".rstrip('0').rstrip('.')
  format_number.removeprefix("0.")
  return format_number

class ScaleCommand:
  def __init__(self, start, end, start_scale, end_scale):
    self.start = start
    self.end = end
    self.start_scale = start_scale
    self.end_scale = end_scale

  def write(self, file):
    start = round(self.start)
    end = "" if math.isclose(self.start, self.end) else round(self.end)
    start_scale = f"{format_number(self.start_scale.x, 1),format_number(self.start_scale.y, 1)}"
    end_scale = "" if is_vector_close(self.start_scale, self.end_scale) else f",{format_number(self.end_scale.x, 1),format_number(self.end_scale.y, 1)}"
    write = f" V,0,{start},{end},{start_scale}{end_scale}"
    file.write(write)

class RotateCommand:
  def __init__(self, start, end, start_rotate, end_rotate):
    self.start = start
    self.end = end
    self.start_rotate = start_rotate
    self.end_rotate = end_rotate

  def write(self, file):
    start = round(self.start)
    end = "" if math.isclose(self.start, self.end) else round(self.end)
    start_rotate = format_number(self.start_rotate, 2)
    end_rotate = "" if math.isclose(self.start_rotate, self.end_rotate) else format_number(self.end_scale, 2)
    write = f" R,0,{start},{end},{start_rotate}{end_rotate}"
    file.write(write)

class Sprite:
  def __init__(self, file, position):
    self.commands = []
    self.file = file
    self.position = position

  def scale(self, start, end, start_scale, end_scale):
    command = ScaleCommand(start, end, start_scale, end_scale)
    self.commands.append(command)

  def rotate(self, start, end, start_rotate, end_rotate):
    command = RotateCommand(start, end, start_rotate, end_rotate)
    self.commands.append(command)

  def write(self, file):
    write = f"4,0,0,{self.file},{format_number(self.position.x), 0},{format_number(self.position.y), 0}"
    file.write(write)

    for command in self.commands:
      command.write(file)

class Storyboard:
  def __init__(self):
    self.sprites = []

  def sprite(self):
    sprite = Sprite()
    self.sprites.append(sprite)

    return sprite

  def write(self):
    with open(constants.SB_PATH, "w") as file:
      file.write("[Events]")
      file.write("//Background and Video events")
      file.write("//Storyboard Layer 0 (Background)")

      for sprite in self.sprites:
        sprite.write(file)

      file.write("//Storyboard Layer 1 (Fail)")
      file.write("//Storyboard Layer 2 (Pass)")
      file.write("//Storyboard Layer 3 (Foreground)")
      file.write("//Storyboard Layer 4 (Overlay)")
      file.write("//Storyboard Sound Samples")
    