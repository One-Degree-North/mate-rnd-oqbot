from __future__ import division, print_function
from vpython import *
from mcu import MCUInterface

t = 0
dt = 0.05
dt_real = dt*5
X_INDEX = 0
Y_INDEX = 1
Z_INDEX = 2

class Movement:
    def __init__(self, initial_angle, initial_position, mcu, initial_velocity, vehicle, gui):
        self.initial_angle = initial_angle
        self.initial_position = initial_position
        self.mcu = mcu
        self.initial_velocity = initial_velocity
        self.vehicle = vehicle
        self.gui = gui
    def change_angle(self):
        self.initial_angle.x += self.mcu.latest_gyro[X_INDEX]*dt
        self.initial_angle.y += self.mcu.latest_gyro[Y_INDEX]*dt
        self.initial_angle.z += self.mcu.latest_gyro[Z_INDEX]*dt
        return [self.initial_angle.x, self.initial_angle.y, self.initial_angle.z]
    def change_velocity(self):
        self.initial_velocity.x += self.mcu.latest_accel[X_INDEX]*dt
        self.initial_velocity.y += self.mcu.latest_accel[Y_INDEX]*dt
        self.initial_velocity.z += self.mcu.latest_accel[Z_INDEX]*dt
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
