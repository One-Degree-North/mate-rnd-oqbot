from threading import Thread

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
SPEED_MODES = [20, 34, 48, 70]

UPDATE_MS = 25

BASE_DOWNWARDS_SPEED = 12


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
        self.set_motor_state(MOTOR_BACK, -percent)

    def down(self, percent: int):
        self.set_motor_state(MOTOR_FRONT, -percent)
        self.set_motor_state(MOTOR_BACK, percent)

    def tilt_up(self, percent: int):
        self.set_motor_state(MOTOR_FRONT, percent)
        self.set_motor_state(MOTOR_BACK, percent)

    def tilt_down(self, percent: int):
        self.set_motor_state(MOTOR_FRONT, -percent)
        self.set_motor_state(MOTOR_BACK, -percent)

    def update_state(self):
        while self.thread_running:
            downwards = BASE_DOWNWARDS_SPEED if self.auto_downwards else 0
            self.mcuVAR.cmd_setMotorCalibrated(MOTOR_LEFT, self.state.motors[MOTOR_LEFT])
            time.sleep(1 / 120)
            self.mcuVAR.cmd_setMotorCalibrated(MOTOR_RIGHT, self.state.motors[MOTOR_RIGHT])
            time.sleep(1 / 120)
            self.mcuVAR.cmd_setMotorCalibrated(MOTOR_FRONT, self.state.motors[MOTOR_FRONT] - downwards)
            time.sleep(1 / 120)
            self.mcuVAR.cmd_setMotorCalibrated(MOTOR_BACK, self.state.motors[MOTOR_BACK] + downwards)
            time.sleep(1 / 120)
            self.mcuVAR.cmd_setMotorMicroseconds(4, self.state.claw)
            time.sleep(1 / 120)

    def read_send(self, key_pressed: KeySignal):
        # debug
        multiplier_percent = SPEED_MODES[self.speed_mode] if key_pressed.pressed else 0
        multiplier_percent *= 2 if key_pressed.shift else 1
        print("comms received", key_pressed, "with percent", multiplier_percent)

        key = key_pressed.key

        # handle if it's just a speed change
        if key != "0" and key != "7" and key.isnumeric():
            self.speed_mode = int(key) - 1
            self.speed_mode %= 4  # safety
            return
        # handle toggle downwards base motion
        if key == "7" and key_pressed.pressed:
            self.auto_downwards = not self.auto_downwards
            print(f"Toggling automatic downwards motion: {self.auto_downwards}")

        # handle other cases (instructions)
        if key_pressed.pressed:  # if pressed
            self.keys_pressed.append(key)
            self.__parse_key(key)
        else:  # if released
            if self.keys_pressed and self.keys_pressed[-1] == key:
                self.keys_pressed.remove(key)
                if not self.keys_pressed:
                    self.halt()
                    return
                self.__parse_key(self.keys_pressed[-1])
            else:
                self.keys_pressed.remove(key)

        print("new key list:", self.keys_pressed)
        print("new state: ", self.state)

    def __parse_key(self, key: str):
        print("parsing key", key)
        multiplier_percent = SPEED_MODES[self.speed_mode]
        if key.isupper():
            multiplier_percent *= 2

        key_lower = key.lower()
        if key_lower == "w":
            self.forward(multiplier_percent)
        elif key_lower == "s":
            self.backwards(multiplier_percent)
        elif key_lower == "a":
            self.turn_left(multiplier_percent)
        elif key_lower == "d":
            self.turn_right(multiplier_percent)
        elif key_lower == "e":
            self.up(multiplier_percent)
        elif key_lower == "q":
            self.down(multiplier_percent)
        elif key_lower == "z":
            self.tilt_up(multiplier_percent)
        elif key_lower == "x":
            self.tilt_down(multiplier_percent)
        elif key_lower == "f":
            self.set_servo_state(CLAW_MIN)
        elif key_lower == "g":
            self.set_servo_state(CLAW_MID)
        elif key_lower == "h":
            self.set_servo_state(CLAW_MAX)
        elif key_lower == "0":
            self.halt()
            # self.mcuVAR.cmd_halt()
        elif key_lower == "i":
            self.set_motor_state(MOTOR_FRONT, multiplier_percent if key.islower() else -multiplier_percent)
        elif key_lower == "j":
            self.set_motor_state(MOTOR_LEFT, multiplier_percent if key.islower() else -multiplier_percent)
        elif key_lower == "k":
            self.set_motor_state(MOTOR_BACK, -multiplier_percent if key.islower() else multiplier_percent)
        elif key_lower == "l":
            self.set_motor_state(MOTOR_RIGHT, -multiplier_percent if key.islower() else multiplier_percent)

    def start_elec_ops(self):
        self.mcuVAR.open_serial()

        # calibrate
        self.mcuVAR.cmd_setMotorCalibration(MOTOR_LEFT, CALIBRATION_VALUES[MOTOR_LEFT])
        self.mcuVAR.cmd_setMotorCalibration(MOTOR_RIGHT, CALIBRATION_VALUES[MOTOR_RIGHT])
        self.mcuVAR.cmd_setMotorCalibration(MOTOR_FRONT, CALIBRATION_VALUES[MOTOR_FRONT])
        self.mcuVAR.cmd_setMotorCalibration(MOTOR_BACK, CALIBRATION_VALUES[MOTOR_BACK])

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
        self.thread_running = False
        self.mcu_thread.join()

        self.mcuVAR.cmd_halt()
        self.mcuVAR.cmd_setAutoReport(PARAM_ACCEL, False, 0)
        self.mcuVAR.cmd_setAutoReport(PARAM_GYRO, False, 0)
        self.mcuVAR.cmd_setAutoReport(PARAM_VOLT_TEMP, False, 0)
        self.mcuVAR.close_serial()
