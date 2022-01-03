
import gcode_generator as gg

depths = [1.5, 3]
speeds = [400, 500, 600] #  , 700, 800]
xd = 7
yd = 40

x = 0
y = 0

gc = gg.FILE_START

for d in depths:
    gc += f"G1 Z-{d} F250 \n" 
    for s in speeds:
        if y == 0:
            y = yd            
        else:
            y = 0
        gc += f"G1 X{x} Y{y} F{s} \n" 
        x += xd
        gc += f"G1 X{x} Y{y} F{s} \n" 
    
gc += f"G1 Z5 F250 \n" 
gc += f"G1 X0 Y0 F{s} \n" 
gc += gg.FILE_END

# write to file
open('./gcode/speed_sample.nc', 'w').write(gc)
