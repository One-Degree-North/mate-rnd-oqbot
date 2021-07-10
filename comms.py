from PyQt5.QtCore import Qt

from threading import Thread
from typing import Iterable

from mcu_lib.mcu import *
from mcu_lib.command_constants import *
from controls_pyqt.key_signal import KeySignal

PWM_MIN = 1000
PWM_MID = 1500
PWM_MAX = 2000

CLAW_MIN = 1010
CLAW_MID = 1335
CLAW_MAX = 1660

CALIBRATION_VALUES = [1000, 1000, 1000, 1000]
SPEED_MODES = [10, 20, 40, 68]

UPDATE_MS = 25
SLEEP_TIME = 1 / 120

FRONT_DOWNWARDS_CALIBRATION = -27
BACK_DOWNWARDS_CALIBRATION = 32


class MotorState:
    def __init__(self):
        self.motors = [0, 0, 0, 0]
        self.claw = CLAW_MID

    def __str__(self):
        return f"Motors: {self.motors}, Servo: {self.claw}"


class Communications:
    def __init__(self, mcuVAR: MCUInterface, MULTIPLIER_PERCENT: int, initial_percent=100):
        self.mcuVAR = mcuVAR
        self.MULTIPLIER_PERCENT = MULTIPLIER_PERCENT
        self.initial_percent = initial_percent
        self.spacebar_count = 0
        self.mcu_thread: Thread = Thread(target=self.update_state)
        self.state: MotorState = MotorState()
        self.thread_running = False
        self.auto_downwards = False
        self.speed_mode = 0
        self.keys_pressed = []

    def start_thread(self):
        self.thread_running = True
        self.mcu_thread.start()

    def set_motor_state(self, motor, percent):
        self.state.motors[motor] = percent

    def set_servo_state(self, value):
        self.state.claw = value

    def halt(self):
        self.set_motor_state(0, 0)
        self.set_motor_state(1, 0)
        self.set_motor_state(2, 0)
        self.set_motor_state(3, 0)

    def force_esc_enable(self):
        self.halt()
        time.sleep(0.2)
        self.set_motor_state(0, 20)
        self.set_motor_state(1, 20)
        self.set_motor_state(2, 20)
        self.set_motor_state(3, 20)
        time.sleep(0.2)
        self.halt()
        time.sleep(0.4)

    def forward(self, percent: int):
        self.set_motor_state(MOTOR_LEFT, percent)
        self.set_motor_state(MOTOR_RIGHT, -percent)

    def backwards(self, percent: int):
        self.set_motor_state(MOTOR_LEFT, -percent)
        self.set_motor_state(MOTOR_RIGHT, percent)

    def turn_right(self, percent: int):
        self.set_motor_state(MOTOR_LEFT, percent)
        self.set_motor_state(MOTOR_RIGHT, percent)

    def turn_left(self, percent: int):
        self.set_motor_state(MOTOR_LEFT, -percent)
        self.set_motor_state(MOTOR_RIGHT, -percent)

    def up(self, percent: int):
        self.set_motor_state(MOTOR_FRONT, percent)
        self.set_motor_state(MOTOR_BACK, percent)

    def down(self, percent: int):
        self.set_motor_state(MOTOR_FRONT, -percent)
        self.set_motor_state(MOTOR_BACK, -percent)

    def tilt_up(self, percent: int):
        self.set_motor_state(MOTOR_FRONT, -percent)
        self.set_motor_state(MOTOR_BACK, percent)

    def tilt_down(self, percent: int):
        self.set_motor_state(MOTOR_FRONT, percent)
        self.set_motor_state(MOTOR_BACK, -percent)

    def __wait_for_next_send(self):
        time.sleep(SLEEP_TIME)

    def update_state(self):
        while self.thread_running:
            front_downwards = FRONT_DOWNWARDS_CALIBRATION if self.auto_downwards else 0
            back_downwards = BACK_DOWNWARDS_CALIBRATION if self.auto_downwards else 0
            self.mcuVAR.cmd_setMotorCalibrated(MOTOR_LEFT, self.state.motors[MOTOR_LEFT])
            self.__wait_for_next_send()
            self.mcuVAR.cmd_setMotorCalibrated(MOTOR_RIGHT, self.state.motors[MOTOR_RIGHT])
            self.__wait_for_next_send()
            self.mcuVAR.cmd_setMotorCalibrated(MOTOR_FRONT, self.state.motors[MOTOR_FRONT] - front_downwards)
            self.__wait_for_next_send()
            self.mcuVAR.cmd_setMotorCalibrated(MOTOR_BACK, self.state.motors[MOTOR_BACK] + back_downwards)
            self.__wait_for_next_send()
            self.mcuVAR.cmd_setMotorMicroseconds(MOTOR_CLAW, self.state.claw)
            self.__wait_for_next_send()

    def read_send(self, key_pressed: KeySignal):
        key = key_pressed.key

        # handle '1'-'4'
        if Qt.Key_1 <= key <= Qt.Key_4:
            self.speed_mode = int(key) - Qt.Key_1
            return

        # handle toggle downwards base motion
        if key == Qt.Key_7 and key_pressed.pressed:
            self.auto_downwards = not self.auto_downwards
            print(f"Toggling automatic downwards motion: {self.auto_downwards}")

        # handle other cases (instructions)
        if key_pressed.pressed:  # if pressed
            self.keys_pressed.append(key)
            self.__parse_keys()
        else:  # if released
            if self.keys_pressed:
                if key in self.keys_pressed:
                    self.keys_pressed.remove(key)
                if not self.keys_pressed:
                    self.halt()
                    return
                self.__parse_keys()
            else:
                self.keys_pressed.remove(key)
Ob
    def __parse_keys(self):
        print("parsing keys: ", self.keys_pressed)
        new_state = MotorState()
        new_state.claw = self.state.claw
        self.state = new_state
        for key in self.keys_pressed:
            self.__parse_key(key)
        print("new state: ", self.state)

    def __parse_key(self, key: int):
        # print("parsing key", key)
        multiplier_percent = SPEED_MODES[self.speed_mode]

        if key == Qt.Key_W:
            self.forward(multiplier_percent)
        elif key == Qt.Key_S:
            self.backwards(multiplier_percent)
        elif key == Qt.Key_A or key == Qt.Key_Left:
            self.turn_left(multiplier_percent)
        elif key == Qt.Key_D or key == Qt.Key_Right:
            self.turn_right(multiplier_percent)
        elif key == Qt.Key_Q:
            self.up(multiplier_percent)
        elif key == Qt.Key_E:
            self.down(multiplier_percent)
        elif key == Qt.Key_Z or key == Qt.Key_Up:
            self.tilt_up(multiplier_percent)
        elif key == Qt.Key_X or key == Qt.Key_Down:
            self.tilt_down(multiplier_percent)
        elif key == Qt.Key_F:
            self.set_servo_state(CLAW_MIN)
        elif key == Qt.Key_G:
            self.set_servo_state(CLAW_MID)
        elif key == Qt.Key_H:
            self.set_servo_state(CLAW_MAX)
        elif key == Qt.Key_C:
            self.set_servo_state(max(CLAW_MIN, self.state.claw - multiplier_percent))
        elif key == Qt.Key_V:
            self.set_servo_state(min(CLAW_MAX, self.state.claw + multiplier_percent))
        elif key == Qt.Key_Y:
            self.force_esc_enable()
        elif key == Qt.Key_0:
            print("Recalibrating!!")
            self.halt()
            self.__calibrate()
            # self.mcuVAR.cmd_halt()

    def __calibrate(self):
        # calibrate
        self.mcuVAR.cmd_setMotorCalibration(MOTOR_LEFT, CALIBRATION_VALUES[MOTOR_LEFT])
        self.mcuVAR.cmd_setMotorCalibration(MOTOR_RIGHT, CALIBRATION_VALUES[MOTOR_RIGHT])
        self.mcuVAR.cmd_setMotorCalibration(MOTOR_FRONT, CALIBRATION_VALUES[MOTOR_FRONT])
        self.mcuVAR.cmd_setMotorCalibration(MOTOR_BACK, CALIBRATION_VALUES[MOTOR_BACK])

        # self.mcuVAR.cmd_setVoltageCalibration(6.5)

        # write mid
        self.mcuVAR.cmd_setMotorMicroseconds(MOTOR_CLAW, PWM_MID)
        self.mcuVAR.cmd_setMotorMicroseconds(MOTOR_FRONT, PWM_MID)
        self.mcuVAR.cmd_setMotorMicroseconds(MOTOR_LEFT, PWM_MID)
        self.mcuVAR.cmd_setMotorMicroseconds(MOTOR_RIGHT, PWM_MID)
        self.mcuVAR.cmd_setMotorMicroseconds(MOTOR_BACK, PWM_MID)

        # enable autoreport
        self.mcuVAR.cmd_setAutoReport(PARAM_ACCEL, True, UPDATE_MS)
        self.mcuVAR.cmd_setAutoReport(PARAM_GYRO, True, UPDATE_MS)
        self.mcuVAR.cmd_setAutoReport(PARAM_LINEAR_ACCEL, True, UPDATE_MS)
        self.mcuVAR.cmd_setAutoReport(PARAM_ORIENTATION, True, UPDATE_MS)
        self.mcuVAR.cmd_setAutoReport(PARAM_VOLT_TEMP, True, UPDATE_MS)

    def start_elec_ops(self):
        self.mcuVAR.open_serial()
        self.__calibrate()

    def kill_elec_ops(self):
        self.thread_running = False
        self.mcu_thread.join()

        self.mcuVAR.cmd_halt()
        self.mcuVAR.cmd_setAutoReport(PARAM_ACCEL, False, 0)
        self.mcuVAR.cmd_setAutoReport(PARAM_GYRO, False, 0)
        self.mcuVAR.cmd_setAutoReport(PARAM_VOLT_TEMP, False, 0)
        self.mcuVAR.cmd_setAutoReport(PARAM_LINEAR_ACCEL, False, 0)
        self.mcuVAR.cmd_setAutoReport(PARAM_ORIENTATION, False, 0)
        self.mcuVAR.close_serial()
