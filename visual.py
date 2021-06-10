from __future__ import division, print_function
from vpython import *
from './mcu-lib/mcu' import MCUInterface
from movement import Movement

running = True
origin = vector(0,0,0)
vehicle = box(pos=origin,length=10, height=5, width=10)
t = 0
dt = 0.005
dt_real = dt*5
axes = [vector(1,0,0), vector(0,1,0), vector(0,0,1)]
X_INDEX = 0
Y_INDEX = 1
Z_INDEX = 2

visual = Movement(initial_angle=vector(0,0,0), initial_position=vector(0,0,0), initial_velocity=vector(0,0,0), vehicle=vehicle) 

#Change to exit condition
while running:
    rate(60)
    change = 0
    velocity_measurements = []
    while change<dt_real:
        new_angle = visual.change_angle()
        new_velocity = visual.change_velocity()
        velocity_measurements.append(new_velocity)
        change+=dt
    new_position = visual.change_position(velocity_measurements)
    for i in range(0, len(axes)):
        visual.vehicle.rotate(angle=new_angle[i], axis= axes[i], origin=visual.vehicle.pos)
    t+=dt_real

    

