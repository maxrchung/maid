import bpy
from mathutils import *

D = bpy.data
C = bpy.context

sb_path = r"C:\Users\Max\AppData\Local\osu!\Songs\beatmap-639109698540463924-a\a - a (S2VX) [a].osb"

with open(sb_path, "w") as file:
  file.write("[Events]")
  file.write("//Background and Video events")
  file.write("//Storyboard Layer 0 (Background)")
  file.write("//Storyboard Layer 1 (Fail)")
  file.write("//Storyboard Layer 2 (Pass)")
  file.write("//Storyboard Layer 3 (Foreground)")
  file.write("//Storyboard Layer 4 (Overlay)")
  file.write("//Storyboard Sound Samples")


print('Done')