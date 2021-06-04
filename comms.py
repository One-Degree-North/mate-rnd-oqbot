from mcu import *
from controls import *
from command_constants import *
import pygame 
import thread from Thread

class Communications:
    def __init__(self, mcuVAR: MCUInterface, controller: controls):
        self.mcuVAR = mcuVAR
        self.controller = controls

        MOTOR_CLAW = 0 
        MOTOR_ONE = 1
        MOTOR_TWO = 2
        MOTOR_THREE = 3 

    def read_send(key_pressed):
        initial_calibration_percent = 100
        value_multiplier = 2 #2 percent
        self.mcuVAR.cmd_setMotorCalibration(MOTOR_ONE,1000)
        self.mcuVAR.cmd_setMotorCalibration(MOTOR_TWO, 1000)
        self.mcuVAR.cmd_setMotorCalibration(MOTOR_THREE, 1000)

        self.mcuVAR.cmd_setMotorMicroseconds(MOTOR_ONE,motors_move[i][1], 1500)
        self.mcuVAR.cmd_setMotorMicroseconds(MOTOR_TWO,motors_move[i][1], 1500)
        self.mcuVAR.cmd_setMotorMicroseconds(MOTOR_THREE,motors_move[i][1], 1500)

        while controls.running:
            #Different functionality/motor running process for 
            if key_pressed == "s":
                self.mcuVAR.cmd_setMotorCalibrated(MOTOR_ONE, -1*initial_calibration_percent)
            elif key_pressed == "a":
                self.mcuVAR.cmd_setMotorCalibrated(MOTOR_TWO, -1*initial_calibration_percent)
            elif key_pressed == "w":
                self.mcuVAR.cmd_setMotorCalibrated(MOTOR_ONE, initial_calibration_percent)
            elif key_pressed == "d":
                self.mcuVAR.cmd_setMotorCalibrated(MOTOR_TWO, initial_calibration_percent)
            elif key_pressed == "e":
                self.mcuVAR.cmd_setMotorCalibrated(MOTOR_CLAW, initial_calibration_percent)
            elif key_pressed == "ld":
                self.mcuVAR.cmd_setMotorCalibrated(MOTOR_TWO, -1*value_multiplier)
            elif key_pressed == "lw":
                self.mcuVAR.cmd_setMotorCalibrated(MOTOR_ONE, -1*value_multiplier)
            elif key_pressed == "ls":
                self.mcuVAR.cmd_setMotorCalibrated(MOTOR_ONE, -1*value_multiplier)
            elif key_pressed == "la":
                self.mcuVAR.cmd_setMotorCalibrated(MOTOR_TWO, -1*value_multiplier)
            elif key_pressed == "le":
                self.mcuVAR.cmd_setMotorCalibrated(MOTOR_CLAW, -1*value_multiplier)
            elif key_pressed == "sa":
                self.mcuVAR.cmd_setMotorCalibrated(MOTOR_TWO, value_multiplier)
            elif key_pressed == "sw":
                self.mcuVAR.cmd_setMotorCalibrated(MOTOR_ONE, value_multiplier)
            elif key_pressed == "sd":
                self.mcuVAR.cmd_setMotorCalibrated(MOTOR_TWO, value_multiplier)
            elif key_pressed == "ss":
                self.mcuVAR.cmd_setMotorCalibrated(MOTOR_ONE, value_multiplier)
            elif key_pressed == "se":
                self.mcuVAR.cmd_setMotorCalibrated(MOTOR_CLAW, value_multiplier)

        self.mcuVAR.__send_packet(COMMAND_HALT, any, None) 
    def kill_elec_ops():
        # ??


