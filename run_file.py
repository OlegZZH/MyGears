import bpy
import os
 
filename = os.path.join(r"C:\Users\Oleg\Dropbox\Gears", "bl_add_gear.py")
exec(compile(open(filename).read(), filename, 'exec'))