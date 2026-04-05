from sprite import Sprite


class Storyboard:
  def __init__(self):
    self.sprites = []

  def sprite(self):
    sprite = Sprite()
    self.sprites.append(sprite)

  def write(self, path):
    with open(path, "w") as file:
      file.write("[Events]")
      file.write("//Background and Video events")
      file.write("//Storyboard Layer 0 (Background)")
      file.write("//Storyboard Layer 1 (Fail)")
      file.write("//Storyboard Layer 2 (Pass)")
      file.write("//Storyboard Layer 3 (Foreground)")
      file.write("//Storyboard Layer 4 (Overlay)")
      file.write("//Storyboard Sound Samples")
    