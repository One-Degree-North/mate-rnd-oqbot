from __future__ import division, print_function
from vpython import *
import numpy as np
from mcu import MCUInterface

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

class Movement:
    def __init__(self, initial_angle, initial_position, initial_velocity, vehicle):
        self.initial_angle = initial_angle
        self.initial_position = initial_position
        self.initial_velocity = initial_velocity
        self.vehicle = vehicle
    def get_gyro(self):
        return [random()*3.0, random()*3.0, random()*3.0]
    def get_accel(self):
        return [random()*3.0, random()*3.0, random()*3.0]
    def change_angle(self):
        self.initial_angle.x += self.get_gyro()[X_INDEX]*dt
        self.initial_angle.y += self.get_gyro()[Y_INDEX]*dt
        self.initial_angle.z += self.get_gyro()[Z_INDEX]*dt
        return [self.initial_angle.x, self.initial_angle.y, self.initial_angle.z]
    def change_velocity(self):
        self.initial_velocity.x += self.get_accel()[X_INDEX]*dt
        self.initial_velocity.y += self.get_accel()[Y_INDEX]*dt
        self.initial_velocity.z += self.get_accel()[Z_INDEX]*dt
        return [self.initial_velocity.x, self.initial_velocity.y, self.initial_velocity.z]
    def change_position(self, velocities):
        change = 0
        velocities = velocities[-1]
        while change<dt_real:
            self.vehicle.pos.x += velocities[X_INDEX]*dt
            self.vehicle.pos.y += velocities[Y_INDEX]*dt
            self.vehicle.pos.z += velocities[Z_INDEX]*dt
            change+=dt
        return [self.vehicle.pos.x, self.vehicle.pos.y, self.vehicle.pos.z]

visual = Movement(initial_angle=vector(0,0,0), initial_position=vector(0,0,0), initial_velocity=vector(0,0,0), vehicle=vehicle) 

#Change to exit condition
while True:
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
