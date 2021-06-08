import sys

sys.path.insert(0, './mcu-lib')
from mcu import *

PWM_MIN = 1000
PWM_MID = 1500
PWM_MAX = 2000

MOTOR_CLAW = 0
MOTOR_FRONT = 1
MOTOR_RIGHT = 2
MOTOR_LEFT = 3
MOTOR_BACK = 4

CALIBRATION_VALUE = 1000

# I can literally use random values here. It makes no difference!
SAME = 0x932f28
NEG_SAME = 0x12fa38
OPPOSITE = 0x783e2c


class Communications:
    def __init__(self, mcuVAR: MCUInterface, MULTIPLIER_PERCENT: int, initial_percent = 100):
        self.mcuVAR = mcuVAR
        self.MULTIPLIER_PERCENT = MULTIPLIER_PERCENT
        self.initial_percent = initial_percent
        self.spacebar_count = 0

    def read_send(self, key_pressed):

        self.mcuVAR.cmd_setMotorCalibration(MOTOR_CLAW, CALIBRATION_VALUE)
        self.mcuVAR.cmd_setMotorCalibration(MOTOR_FRONT, CALIBRATION_VALUE)
        self.mcuVAR.cmd_setMotorCalibration(MOTOR_LEFT, CALIBRATION_VALUE)
        self.mcuVAR.cmd_setMotorCalibration(MOTOR_RIGHT, CALIBRATION_VALUE)
        self.mcuVAR.cmd_setMotorCalibration(MOTOR_BACK, CALIBRATION_VALUE)

        self.mcuVAR.cmd_setMotorMicroseconds(MOTOR_CLAW, PWM_MID)
        self.mcuVAR.cmd_setMotorMicroseconds(MOTOR_FRONT, PWM_MID)
        self.mcuVAR.cmd_setMotorMicroseconds(MOTOR_LEFT, PWM_MID)
        self.mcuVAR.cmd_setMotorCalibration(MOTOR_RIGHT, PWM_MID)
        self.mcuVAR.cmd_setMotorCalibration(MOTOR_BACK, PWM_MID)

        dict_motors = {
            "e": [MOTOR_FRONT, MOTOR_BACK, SAME],
            "q": [MOTOR_BACK, MOTOR_FRONT, NEG_SAME],
            "d": [MOTOR_RIGHT, MOTOR_LEFT, OPPOSITE],
            "a": [MOTOR_LEFT, MOTOR_RIGHT, OPPOSITE],
            "w": [MOTOR_LEFT, MOTOR_RIGHT, SAME],
            "s": [MOTOR_RIGHT, MOTOR_LEFT, NEG_SAME]
        }

        if key_pressed[0] == "s" and len(key_pressed) == 2:
            for i in range(0, len(dict_motors[key_pressed[1]])-1):
                self.mcuVAR.cmd_setMotorCalibrated(dict_motors[key_pressed[1]][i], 0)
        elif key_pressed[0] == "l":
            for i in range(0, len(dict_motors[key_pressed[1]])-1):
                self.mcuVAR.cmd_setMotorCalibrated(dict_motors[key_pressed[1]][i], (2*i-1)*self.MULTIPLIER_PERCENT)
        elif len(key_pressed) == 1:
            for i in range(0, len(dict_motors[key_pressed[1]])-1):
                if dict_motors[key_pressed[1]][2] == OPPOSITE:
                    self.mcuVAR.cmd_setMotorCalibrated(dict_motors[key_pressed[1]][i], (2*i-1)*self.initial_percent)
                elif dict_motors[key_pressed[1]][2] == SAME:
                    self.mcuVAR.cmd_setMotorCalibrated(dict_motors[key_pressed[1]][i], self.initial_percent)
                elif dict_motors[key_pressed[1]][2] == NEG_SAME:
                    self.mcuVAR.cmd_setMotorCalibrated(dict_motors[key_pressed[1]][i], -1*self.initial_percent)
        elif key_pressed =="spacebar":
            self.spacebar_count += 1
            if self.spacebar_count % 4 == 1:
                self.mcuVAR.cmd_setMotorCalibrated(MOTOR_CLAW, self.initial_percent)
            elif self.spacebar_count % 4 == 2:
                self.mcuVAR.cmd_setMotorCalibrated(MOTOR_CLAW, 0)
            elif self.spacebar_count % 4 == 3:
                self.mcuVAR.cmd_setMotorCalibrated(MOTOR_CLAW, -1*self.initial_percent)
            elif self.spacebar_count % 4 == 0:
                self.mcuVAR.cmd_setMotorCalibrated(MOTOR_CLAW, 0)

    def kill_elec_ops(self):
        self.mcuVAR.cmd_halt()
        self.mcuVAR.setAutoReport(PARAM_ACCEL, False, 0)
        self.mcuVAR.setAutoReport(PARAM_GYRO, False, 0)
        self.mcuVAR.setAutoReport(PARAM_VOLT_TEMP, False, 0)
        self.mcuVAR.close_serial()


