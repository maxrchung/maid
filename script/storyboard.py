import constants
import math

def is_vector_close(v1, v2):
  is_vector_close = (v1 - v2).length < constants.EPSILON
  return is_vector_close

def format_number(number, significant_digits):
  if math.isclose(number, 0):
    return 0
  
  format_number = f"{number:.{significant_digits}f}"
  
  if significant_digits > 0:
    format_number = format_number.rstrip('0').rstrip('.').lstrip('0')

  if format_number == "":
    return 0

  return format_number

class ScaleCommand:
  def __init__(self, start, end, start_scale, end_scale):
    self.start = start
    self.end = end
    self.start_scale = start_scale
    self.end_scale = end_scale

  def output(self):
    start = round(self.start)
    end = "" if math.isclose(self.start, self.end) else round(self.end)
    start_scale = f"{format_number(self.start_scale.x, 2)},{format_number(self.start_scale.y, 2)}"
    end_scale = "" if is_vector_close(self.start_scale, self.end_scale) else f",{format_number(self.end_scale.x, 2),format_number(self.end_scale.y, 2)}"
    output = f" V,0,{start},{end},{start_scale}{end_scale}\n"
    return output

class RotateCommand:
  def __init__(self, start, end, start_rotate, end_rotate):
    self.start = start
    self.end = end
    self.start_rotate = start_rotate
    self.end_rotate = end_rotate

  def output(self):
    start = round(self.start)
    end = "" if math.isclose(self.start, self.end) else round(self.end)
    start_rotate = format_number(self.start_rotate, 2)
    end_rotate = "" if math.isclose(self.start_rotate, self.end_rotate) else format_number(self.end_rotate, 2)
    output = f" R,0,{start},{end},{start_rotate}{end_rotate}\n"
    return output

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

  def write(self, file, variables):
    output = f"4,0,0,{self.file},{format_number(self.position.x, 0)},{format_number(self.position.y, 0)}\n"
    for key, value in variables:
      if value in output:
        output = output.replace(value, key)
        break
    file.write(output)

    for command in self.commands:
      output = command.output()
      for key, value in variables:
        if value in output:
          output = output.replace(value, key)
          break
      file.write(output)


class Storyboard:
  def __init__(self):
    self.sprites = []

  def sprite(self, file, position):
    sprite = Sprite(file, position)
    self.sprites.append(sprite)

    return sprite

  def add_sprite(self, sprite):
    self.sprites.append(sprite)

  def write(self, variables):
    with open(constants.STORYBOARD_PATH, "w") as file:
      if len(variables) > 0:
        file.write("[Variables]\n")
        for key, value in variables:
          file.write(f"{key}={value}\n")

      file.write("[Events]\n")
      file.write("//Background and Video events\n")
      file.write("//Storyboard Layer 0 (Background)\n")

      for sprite in self.sprites:
        sprite.write(file, variables)

      file.write("//Storyboard Layer 1 (Fail)\n")
      file.write("//Storyboard Layer 2 (Pass)")
      file.write("//Storyboard Layer 3 (Foreground)\n")
      file.write("//Storyboard Layer 4 (Overlay)\n")
      file.write("//Storyboard Sound Samples")
    