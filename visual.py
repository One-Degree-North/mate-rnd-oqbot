from __future__ import division, print_function
from vpython import *
import numpy as np
from mcu import MCUInterface
from movement import Movement

t = 0
dt = 0.005
dt_real = dt*5
axes = [vector(1,0,0), vector(0,1,0), vector(0,0,1)]
X_INDEX = 0
Y_INDEX = 1
Z_INDEX = 2

class Visualizer:
    def __init__(self, visual: Movement):
        self.visual = visual
    def visualize():
        #Change to exit condition
        while visual.running:
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
