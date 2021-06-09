from mcu_lib.command_constants import *
from mcu_lib.mcu import *

PWM_MIN = 1000
PWM_MID = 1500
PWM_MAX = 2000

MOTOR_CLAW = 4
MOTOR_FRONT = 1
MOTOR_RIGHT = 2
MOTOR_LEFT = 3
MOTOR_BACK = 0

CLAW_MIN = 1010
CLAW_MID = 1400
CLAW_MAX = 1650

CALIBRATION_VALUES = [1000, 1000, 1000, 1000]

UPDATE_MS = 25

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

    def forward(self, percent: int):
        self.mcuVAR.cmd_setMotorCalibrated(MOTOR_LEFT, percent)
        self.mcuVAR.cmd_setMotorCalibrated(MOTOR_RIGHT, percent)

    def backwards(self, percent: int):
        self.mcuVAR.cmd_setMotorCalibrated(MOTOR_LEFT, -percent)
        self.mcuVAR.cmd_setMotorCalibrated(MOTOR_RIGHT, -percent)

    def turn_right(self, percent: int):
        self.mcuVAR.cmd_setMotorCalibrated(MOTOR_LEFT, percent)
        self.mcuVAR.cmd_setMotorCalibrated(MOTOR_RIGHT, -percent)

    def turn_left(self, percent: int):
        self.mcuVAR.cmd_setMotorCalibrated(MOTOR_LEFT, -percent)
        self.mcuVAR.cmd_setMotorCalibrated(MOTOR_RIGHT, percent)

    def up(self, percent: int):
        self.mcuVAR.cmd_setMotorCalibrated(MOTOR_FRONT, percent)
        self.mcuVAR.cmd_setMotorCalibrated(MOTOR_BACK, percent)

    def down(self, percent: int):
        self.mcuVAR.cmd_setMotorCalibrated(MOTOR_FRONT, -percent)
        self.mcuVAR.cmd_setMotorCalibrated(MOTOR_BACK, -percent)

    def tilt_up(self, percent: int):
        self.mcuVAR.cmd_setMotorCalibrated(MOTOR_FRONT, percent)
        self.mcuVAR.cmd_setMotorCalibrated(MOTOR_BACK, -percent)

    def tilt_down(self, percent: int):
        self.mcuVAR.cmd_setMotorCalibrated(MOTOR_FRONT, -percent)
        self.mcuVAR.cmd_setMotorCalibrated(MOTOR_BACK, percent)

    def read_send(self, key_pressed):
        # get multiplier
        multiplier_percent = self.initial_percent if len(key_pressed) == 1 else \
                                          (0 if key_pressed[0] == "s" else self.MULTIPLIER_PERCENT)
        # debug
        print("sending", key_pressed, "with percent", multiplier_percent)
        # parse last letter of key_pressed by command, sending in multiplier
        if key_pressed[-1] == "w":
            self.forward(multiplier_percent)
        elif key_pressed[-1] == "s":
            self.backwards(multiplier_percent)
        elif key_pressed[-1] == "a":
            self.turn_left(multiplier_percent)
        elif key_pressed[-1] == "d":
            self.turn_right(multiplier_percent)
        elif key_pressed[-1] == "e":
            self.up(multiplier_percent)
        elif key_pressed[-1] == "q":
            self.down(multiplier_percent)
        elif key_pressed[-1] == "i":
            self.tilt_up(multiplier_percent)
        elif key_pressed[-1] == "k":
            self.tilt_down(multiplier_percent)
        elif key_pressed[-1] == "f":
            self.mcuVAR.cmd_setMotorMicroseconds(MOTOR_CLAW, CLAW_MID)
        elif key_pressed == "spacebar":
            self.spacebar_count += 1
            self.spacebar_count %= 2
            if self.spacebar_count == 0:
                self.mcuVAR.cmd_setMotorMicroseconds(MOTOR_CLAW, CLAW_MAX)
            elif self.spacebar_count == 1:
                self.mcuVAR.cmd_setMotorMicroseconds(MOTOR_CLAW, CLAW_MIN)

    def start_elec_ops(self):
        self.mcuVAR.open_serial()

        # calibrate
        self.mcuVAR.cmd_setMotorCalibration(MOTOR_LEFT, CALIBRATION_VALUES[0])
        self.mcuVAR.cmd_setMotorCalibration(MOTOR_RIGHT, CALIBRATION_VALUES[1])
        self.mcuVAR.cmd_setMotorCalibration(MOTOR_FRONT, CALIBRATION_VALUES[2])
        self.mcuVAR.cmd_setMotorCalibration(MOTOR_BACK, CALIBRATION_VALUES[3])

        # write mid
        self.mcuVAR.cmd_setMotorMicroseconds(MOTOR_CLAW, PWM_MID)
        self.mcuVAR.cmd_setMotorMicroseconds(MOTOR_FRONT, PWM_MID)
        self.mcuVAR.cmd_setMotorMicroseconds(MOTOR_LEFT, PWM_MID)
        self.mcuVAR.cmd_setMotorMicroseconds(MOTOR_RIGHT, PWM_MID)
        self.mcuVAR.cmd_setMotorMicroseconds(MOTOR_BACK, PWM_MID)

        # enable autoreport
        self.mcuVAR.cmd_setAutoReport(PARAM_ACCEL, True, UPDATE_MS)
        self.mcuVAR.cmd_setAutoReport(PARAM_GYRO, True, UPDATE_MS)
        self.mcuVAR.cmd_setAutoReport(PARAM_VOLT_TEMP, True, UPDATE_MS)

    def kill_elec_ops(self):
        self.mcuVAR.cmd_halt()
        self.mcuVAR.cmd_setAutoReport(PARAM_ACCEL, False, 0)
        self.mcuVAR.cmd_setAutoReport(PARAM_GYRO, False, 0)
        self.mcuVAR.cmd_setAutoReport(PARAM_VOLT_TEMP, False, 0)
        self.mcuVAR.close_serial()


